"""Atomic claim extraction with source span citations.

A "claim" is the smallest unit of assertable meaning. Not a sentence —
sometimes a sentence makes three claims; sometimes three sentences make one.

Why sub-sentence granularity matters:
  The AnalystPerspective already tracks evidence_ids at document level.
  But "the paper supports this argument" conflates which part of the paper
  and which part of the argument. When a block verdict flags an ungrounded
  claim, the council currently can't say *which* claim — just that one exists.
  AtomicClaims fix that: each claim carries a source span so the governing
  body can point at exactly what needs evidence.

Claim types:
  FACTUAL      — states something that is or was true ("revenue grew 12%")
  CAUSAL       — asserts cause-effect ("X leads to Y")
  QUANTITATIVE — contains a measurable quantity ("4x faster", "99.9% uptime")
  DEFINITIONAL — defines a term ("governance means...")
  EVALUATIVE   — expresses a judgment ("the design is elegant")

Span format:
  "L{start}-L{end}" where start/end are 1-indexed line numbers.
  For inline spans within a line: "L{line}:{char_start}-{char_end}".
  Unknown span → "L?".

This module is pure extraction — no LLM. It applies heuristic patterns
to surface likely atomic assertions. Precision is intentionally conservative:
it is better to miss a borderline claim than to split a sentence into two
claims that depend on each other.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Atomic claim extraction: decompose text into the smallest assertable units "
    "with source span citations for evidence traceability."
)


class ClaimType(str, Enum):
    FACTUAL = "factual"
    CAUSAL = "causal"
    QUANTITATIVE = "quantitative"
    DEFINITIONAL = "definitional"
    EVALUATIVE = "evaluative"


@dataclass
class AtomicClaim:
    """A single assertable statement extracted from source text."""

    id: str
    text: str  # the claim, as a clean statement
    source_span: str  # e.g. "L3-5", "L7:14-42", "L?"
    claim_type: ClaimType
    confidence: float  # extractor confidence 0.0 → 1.0
    line_number: int = 0  # primary line (0 = unknown)
    evidence_ids: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "source_span": self.source_span,
            "claim_type": self.claim_type.value,
            "confidence": round(self.confidence, 4),
            "line_number": self.line_number,
            "evidence_ids": self.evidence_ids,
        }


# ── Pattern tables ────────────────────────────────────────────────────────────

_CAUSAL_PATTERNS = re.compile(
    r"\b(leads? to|causes?|results? in|produces?|triggers?|enables?|prevents?|"
    r"because|therefore|thus|hence|so that|in order to|due to)\b",
    re.IGNORECASE,
)

_QUANTITATIVE_PATTERNS = re.compile(
    r"""
    (?:
        \d+(?:\.\d+)?               # bare number
        \s*(?:%|x|×|times|percent|ms|kb|mb|gb|tb|fps|rpm|hz|khz|mhz)
    )
    |
    (?:\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)   # range: "3-5x"
    |
    (?:
        \b(?:double|triple|quadruple|halve|increase|decrease|reduce|grow)
        \b[^.]{0,30}
        \b(?:by|to|from)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_DEFINITIONAL_PATTERNS = re.compile(
    r"\b(?:is defined as|means?|refers? to|is called|is known as|"
    r"by definition|in the context of|is a|is an|are a|are an)\b",
    re.IGNORECASE,
)

_EVALUATIVE_PATTERNS = re.compile(
    r"\b(?:better|worse|best|worst|elegant|clean|complex|simple|"
    r"superior|inferior|efficient|inefficient|robust|fragile|"
    r"important|critical|significant|trivial|excellent|poor)\b",
    re.IGNORECASE,
)

# Sentence endings that split cleanly
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z一-鿿])")

# Minimum length for a claim (below this it's probably a fragment)
_MIN_CLAIM_CHARS = 15
# Maximum: longer than this → too compound, extract sub-clauses
_MAX_CLAIM_CHARS = 250


# ── Extraction logic ──────────────────────────────────────────────────────────


def _detect_claim_type(text: str) -> Tuple[ClaimType, float]:
    """Return the most likely claim type and a confidence score."""
    if _QUANTITATIVE_PATTERNS.search(text):
        return ClaimType.QUANTITATIVE, 0.85
    if _CAUSAL_PATTERNS.search(text):
        return ClaimType.CAUSAL, 0.80
    if _DEFINITIONAL_PATTERNS.search(text):
        return ClaimType.DEFINITIONAL, 0.78
    if _EVALUATIVE_PATTERNS.search(text):
        return ClaimType.EVALUATIVE, 0.72
    return ClaimType.FACTUAL, 0.65


def _split_compound_sentence(text: str) -> List[str]:
    """Split a long compound sentence into sub-clauses at conjunctions.

    Only splits if the resulting pieces each exceed _MIN_CLAIM_CHARS.
    """
    # Conjunctions that typically separate independent assertions
    compound_split = re.compile(
        r"\s+(?:and|but|however|while|whereas|although|though|yet|"
        r"nevertheless|furthermore|moreover|additionally),?\s+",
        re.IGNORECASE,
    )
    parts = compound_split.split(text)
    clean = [p.strip() for p in parts if len(p.strip()) >= _MIN_CLAIM_CHARS]
    return clean if len(clean) > 1 else [text]


def _make_id() -> str:
    return f"cl-{str(uuid.uuid4())[:8]}"


def _span(line: int, total_lines: Optional[int] = None) -> str:
    if line <= 0:
        return "L?"
    return f"L{line}"


def _is_assertion(sentence: str) -> bool:
    """Filter out questions, commands, and pure exclamations."""
    stripped = sentence.strip()
    if not stripped or stripped.endswith("?"):
        return False
    # Imperative starters (commands are not claims)
    if re.match(r"^(?:run|do|make|please|note that|see |refer to)\b", stripped, re.IGNORECASE):
        return False
    return len(stripped) >= _MIN_CLAIM_CHARS


def extract_atomic_claims(
    text: str,
    *,
    max_claims: int = 10,
    evidence_ids: Optional[List[str]] = None,
) -> List[AtomicClaim]:
    """Extract atomic claims from text with source span citations.

    Returns at most ``max_claims`` claims, sorted by confidence descending.
    Line numbers are 1-indexed from the start of ``text``.
    """
    if not text or not text.strip():
        return []

    lines = text.splitlines()
    ev = evidence_ids or []
    claims: List[AtomicClaim] = []

    for line_idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        # Split into sentences first
        sentences = _SENTENCE_SPLIT.split(line)
        for sentence in sentences:
            sentence = sentence.strip()
            if not _is_assertion(sentence):
                continue

            # Decide whether to split compound sentence
            candidates = (
                _split_compound_sentence(sentence)
                if len(sentence) > _MAX_CLAIM_CHARS
                else [sentence]
            )

            for candidate in candidates:
                candidate = candidate.strip().rstrip(".,;:")
                if not _is_assertion(candidate):
                    continue

                claim_type, confidence = _detect_claim_type(candidate)
                claims.append(
                    AtomicClaim(
                        id=_make_id(),
                        text=candidate,
                        source_span=_span(line_idx),
                        claim_type=claim_type,
                        confidence=confidence,
                        line_number=line_idx,
                        evidence_ids=list(ev),
                    )
                )

                if len(claims) >= max_claims:
                    break
            if len(claims) >= max_claims:
                break
        if len(claims) >= max_claims:
            break

    return sorted(claims, key=lambda c: c.confidence, reverse=True)


def claims_requiring_evidence(claims: List[AtomicClaim]) -> List[AtomicClaim]:
    """Return the subset of claims that most need external evidence.

    FACTUAL and QUANTITATIVE claims without evidence_ids are highest priority.
    CAUSAL claims are second priority. EVALUATIVE claims typically don't need
    external evidence (they're judgments, not assertions of fact).
    """
    priority_order = {
        ClaimType.FACTUAL: 0,
        ClaimType.QUANTITATIVE: 1,
        ClaimType.CAUSAL: 2,
        ClaimType.DEFINITIONAL: 3,
        ClaimType.EVALUATIVE: 4,
    }
    needs_evidence = [
        c
        for c in claims
        if c.claim_type in (ClaimType.FACTUAL, ClaimType.QUANTITATIVE, ClaimType.CAUSAL)
        and not c.evidence_ids
    ]
    return sorted(needs_evidence, key=lambda c: priority_order[c.claim_type])


def format_claim_report(claims: List[AtomicClaim]) -> str:
    """Render a compact claim report for logging and handoff blocks."""
    if not claims:
        return "(no claims extracted)"
    lines = []
    for c in claims:
        ev_note = f" [ev:{len(c.evidence_ids)}]" if c.evidence_ids else " [no evidence]"
        lines.append(
            f"{c.source_span} {c.claim_type.value:12s} ({c.confidence:.2f}){ev_note}: {c.text[:80]}"
        )
    return "\n".join(lines)
