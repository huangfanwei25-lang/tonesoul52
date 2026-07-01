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
Because it is security-adjacent, it wants a different-model review before being trusted on real
output. See docs/plans/output_redaction_2026-07-01.md.
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
    ("anthropic_openai_key", 85, re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{16,}\b"), 0),
    ("bearer", 70, re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}=*"), 0),
    # credential assignment: mask only the value (group 3), keep the key name (group 1).
    # The (?!\[REDACTED:) lookahead keeps this idempotent — it will not re-mask its own marker.
    (
        "assignment",
        50,
        re.compile(
            r"\b(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?token|client[_-]?secret)\b"
            r"(\s*[:=]\s*)[\"']?((?!\[REDACTED:)[^\s\"'&]{6,})[\"']?",
            re.IGNORECASE,
        ),
        3,
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
