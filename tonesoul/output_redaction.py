"""Output secret redaction — mask credential-shaped substrings before external artifacts.

§0 Orientation
--------------
ToneSoul's thesis is accountability + restraint. This is restraint applied to EGRESS: before
ToneSoul emits an external artifact (report / handoff / log / posted comment), mask
credential-shaped substrings so a secret can't ride out. Three native design choices distinguish
it from the source it was inspired by (AI Team OS `guardrails.py`, whose redaction idea was
referenced but whose code was NOT lifted — its input gate is lexical and >16KB-bypassable and is
deliberately not reused):

- SECRETS by default; PII (email) OPT-IN. ToneSoul content legitimately contains emails (the
  creator's, cited authors'); blanket PII redaction destroys real content. Secrets are
  high-signal / low-false-positive shapes, safe to mask by default.
- AUDITABLE, never silent. `redact` returns WHAT it masked (kind + span + a non-leaking preview).
  Redaction without a record is the opposite of accountability.
- Masks the VALUE, preserves structure: `api_key=sk-...` -> `api_key=[REDACTED:assignment]`.

It is a PRIMITIVE: it masks + reports; it does NOT auto-wire into a live egress path (that is a
separate, owner-gated step). meta.not_for applies: this is a best-effort deterministic mask, NOT a
safety certification and NOT a claim that "secrets cannot leak".

§N Coda
-------
Lexical redaction is a FLOOR, not a proof: it catches known shapes, not novel encodings. Never
claim "secrets cannot leak"; claim "known credential shapes are masked, and here is the record of
what was". A missed shape is a bug to add a pattern + test for — not a reason to trust it blindly.

Coverage was widened over two different-model (codex) review rounds on 2026-07-01. Round 1: env-style
keys (OPENAI_API_KEY / AWS_SECRET_ACCESS_KEY), connection-string / URL userinfo, Basic auth, Stripe,
and a narrowed sk- to kill a "sk-learn" false positive. Round 2: audit-idempotent quoted redaction,
URI passwords containing ":", SECRET_KEY_BASE, colon-quoted values only at line start (so inline
prose `note: password: "…"` is safe), and Basic auth gated behind an Authorization header. KNOWN
REMAINING GAPS (deliberate, honest): an UNQUOTED value after ":" is not masked (lexically
indistinguishable from prose); a QUOTED colon value masks only at line start (a mid-line YAML flow
value is missed); raw high-entropy hex/base64 with no key context is not masked (would false-positive
on git SHAs); an unquoted value with spaces is masked only up to the first space. Candidates for a
future opt-in strict/entropy mode, not silent behaviour. Security-adjacent → re-confirm with a
different model after each pattern change. See docs/plans/output_redaction_2026-07-01.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Output secret redaction: mask known credential shapes before external artifacts, auditably."
)

USES_LLM = False
USES_NETWORK = False


@dataclass(frozen=True)
class RedactionFinding:
    """One masked span. `preview` carries the kind + length only — never the secret's characters."""

    kind: str
    start: int
    end: int
    preview: str


@dataclass(frozen=True)
class RedactionResult:
    text: str
    findings: tuple[RedactionFinding, ...]

    @property
    def redacted(self) -> bool:
        return bool(self.findings)


# Credential-assignment key matching. `_KEY_PREFIX` lets env-style names match
# (OPENAI_API_KEY / DB_PASSWORD / AWS_SECRET_ACCESS_KEY): the lookbehind anchors the whole name at a
# real boundary, the (?:[A-Za-z0-9]+_)* eats env prefixes, and the required \s*[:=] after the keyword
# is the effective right boundary (so TOKENIZER=... / AUTHOR=... do NOT match). Longer compounds are
# listed before bare secret/token so alternation prefers them.
_KEY_PREFIX = r"(?<![A-Za-z0-9_])(?:[A-Za-z0-9]+_)*"
_KEY_WORDS = (
    r"(?:api[_-]?key|secret[_-]?access[_-]?key|secret[_-]?key[_-]?base|secret[_-]?key|"
    r"access[_-]?key[_-]?id|access[_-]?token|client[_-]?secret|auth[_-]?token|private[_-]?key|"
    r"credential|password|passwd|pwd|secret|token)"
)

# (kind, priority, compiled regex, group_to_mask). Higher priority wins an overlap. group 0 = whole
# match; a positive int masks only that capture group (so an assignment keeps its key name).
# Ordered most-specific-first. Deliberately conservative: high-signal shapes, low false positives.
_SECRET_PATTERNS: list[tuple[str, int, re.Pattern[str], int]] = [
    (
        "private_key",
        100,
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        0,
    ),
    # credentials in a connection string / URL userinfo: scheme://user:PASSWORD@host. The password
    # group allows ":" and "/" (only whitespace/@ end it) so "s3c:r3t" is masked whole.
    (
        "uri_userinfo",
        95,
        re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:((?!\[REDACTED:)[^\s@]{3,})@"),
        1,
    ),
    # Basic auth — require an Authorization / Proxy-Authorization header so prose "Basic word" is safe.
    (
        "basic_auth",
        92,
        re.compile(
            r"(?:Proxy-)?Authorization\s*:\s*Basic\s+((?!\[REDACTED:)[A-Za-z0-9+/]{16,}={0,2})",
            re.IGNORECASE,
        ),
        1,
    ),
    (
        "jwt",
        90,
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
        0,
    ),
    ("aws_access_key_id", 85, re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), 0),
    ("github_token", 85, re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"), 0),
    ("google_api_key", 85, re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), 0),
    ("slack_token", 85, re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), 0),
    ("stripe_key", 85, re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{10,}\b"), 0),
    # sk- keys: require a known provider prefix (ant-/proj-) OR a long contiguous run, so hyphenated
    # prose like "sk-learn-compatible" does NOT match.
    (
        "anthropic_openai_key",
        84,
        re.compile(r"\bsk-(?:(?:ant|proj)-[A-Za-z0-9_-]{16,}|[A-Za-z0-9]{40,})\b"),
        0,
    ),
    ("bearer", 70, re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}=*"), 0),
    # credential assignment, "=" with a QUOTED value (any position). Full quoted content is masked
    # (spaces incl). (?!\[REDACTED:) keeps it audit-idempotent.
    (
        "assignment_quoted",
        55,
        re.compile(
            _KEY_PREFIX + _KEY_WORDS + r"""\s*=\s*["']((?!\[REDACTED:)[^"']{6,})["']""",
            re.IGNORECASE,
        ),
        1,
    ),
    # credential assignment, ":" with a QUOTED value but only at LINE START (YAML/config), so inline
    # prose like  note: password: "strong policy"  is NOT eaten (":" mid-line stays prose).
    (
        "assignment_quoted",
        54,
        re.compile(
            r"(?m)^[ \t]*"
            + _KEY_PREFIX
            + _KEY_WORDS
            + r"""\s*:\s*["']((?!\[REDACTED:)[^"']{6,})["']""",
            re.IGNORECASE,
        ),
        1,
    ),
    # credential assignment, UNQUOTED value. Only "=" (a ":" would eat prose like "password: strong").
    # (?!\[REDACTED:) keeps it idempotent — it will not re-mask its own marker.
    (
        "assignment",
        50,
        re.compile(
            _KEY_PREFIX + _KEY_WORDS + r"""\s*=\s*(?!["'])((?!\[REDACTED:)[^\s"'&]{6,})""",
            re.IGNORECASE,
        ),
        1,
    ),
]

_PII_PATTERNS: list[tuple[str, int, re.Pattern[str], int]] = [
    ("email", 40, re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), 0),
]


def _collect(
    text: str, patterns: list[tuple[str, int, re.Pattern[str], int]]
) -> list[tuple[int, int, int, str]]:
    """Return candidate spans as (start, end, priority, kind) over the ORIGINAL text."""
    spans: list[tuple[int, int, int, str]] = []
    for kind, priority, pattern, group in patterns:
        for m in pattern.finditer(text):
            start, end = m.span(group)
            if end > start:
                spans.append((start, end, priority, kind))
    return spans


def _resolve_overlaps(spans: list[tuple[int, int, int, str]]) -> list[tuple[int, int, str]]:
    """Keep highest-priority (then longest) span among overlaps; return sorted (start, end, kind)."""
    # sort so the winner of any overlap comes first: by priority desc, then length desc, then start
    ordered = sorted(spans, key=lambda s: (-s[2], -(s[1] - s[0]), s[0]))
    kept: list[tuple[int, int, str]] = []
    for start, end, _priority, kind in ordered:
        if any(start < k_end and end > k_start for k_start, k_end, _ in kept):
            continue
        kept.append((start, end, kind))
    kept.sort(key=lambda s: s[0])
    return kept


def redact(text: str, *, include_pii: bool = False) -> RedactionResult:
    """Mask credential shapes (and, if include_pii, emails). Auditable: reports every masked span.

    Masks the value with ``[REDACTED:<kind>]`` and preserves surrounding structure. Returns the
    redacted text plus a finding per masked span whose ``preview`` names the kind + length only
    (never the secret's characters). Idempotent on already-redacted text (the marker matches no
    pattern).
    """
    if not text:
        return RedactionResult(text=text, findings=())
    patterns = list(_SECRET_PATTERNS)
    if include_pii:
        patterns = patterns + _PII_PATTERNS

    kept = _resolve_overlaps(_collect(text, patterns))
    if not kept:
        return RedactionResult(text=text, findings=())

    out_parts: list[str] = []
    findings: list[RedactionFinding] = []
    cursor = 0
    for start, end, kind in kept:
        out_parts.append(text[cursor:start])
        out_parts.append(f"[REDACTED:{kind}]")
        findings.append(
            RedactionFinding(
                kind=kind, start=start, end=end, preview=f"{kind}({end - start} chars)"
            )
        )
        cursor = end
    out_parts.append(text[cursor:])
    return RedactionResult(text="".join(out_parts), findings=tuple(findings))


def has_secrets(text: str) -> bool:
    """True if any credential shape is present (secrets only; PII not counted)."""
    return bool(_resolve_overlaps(_collect(text, _SECRET_PATTERNS)))
