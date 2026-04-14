"""
ToneSoul High-Risk Grounding Check (Phase 851).

Post-hoc check: after LLM generates a response, extract factual claims
and verify whether they can be traced back to the user query, known context,
or explicit caveats. This is NOT token-level source pointers — it is a
bounded, lightweight pattern-based check.

Design constraints:
  - No LLM call (pure heuristic — must be fast)
  - Only activates on governance_depth == "full"
  - Produces a GroundingResult with ungrounded_ratio and thin_support flag
  - Pipeline uses thin_support to boost self_check severity
  - Does not pretend to be a real fact-checker — just detects thin-support risk

Author: Claude Code (Phase 851)
Date: 2026-04-08
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# High-risk keyword patterns
# ---------------------------------------------------------------------------

# Patterns that suggest the response contains verifiable factual claims
_FACTUAL_CLAIM_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?%", re.IGNORECASE),  # percentages
    re.compile(r"\$\d", re.IGNORECASE),  # dollar amounts
    re.compile(r"\b(?:billion|million|trillion|兆|億|萬)\b", re.IGNORECASE),
    re.compile(r"\b(?:according to|根據|數據顯示|研究表明)\b", re.IGNORECASE),
    re.compile(r"\b(?:in \d{4}|於\d{4}年)\b", re.IGNORECASE),  # year references
    re.compile(
        r"\b(?:increased|decreased|grew|declined|上升|下降|成長|衰退)\s+(?:by\s+)?\d", re.IGNORECASE
    ),
    re.compile(r"\b(?:study|report|survey|analysis|調查|報告|分析)\b", re.IGNORECASE),
]

# Patterns that suggest the response contains hedging / honest caveats
_CAVEAT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:I'm not sure|I cannot verify|無法確認|無法驗證|僅供參考)\b", re.IGNORECASE),
    re.compile(r"\b(?:may|might|could|possibly|或許|可能|大約|約)\b", re.IGNORECASE),
    re.compile(r"\b(?:as of my|截至我的|知識截止)\b", re.IGNORECASE),
    re.compile(r"\b(?:please verify|請自行查核|建議查證)\b", re.IGNORECASE),
]

# Patterns that indicate the claim references the user's own input
_USER_ECHO_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:you mentioned|你提到|你說的|如你所述|your|你的)\b", re.IGNORECASE),
    re.compile(r"\b(?:based on your|根據你提供的|依據你給的)\b", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Grounding Result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GroundingResult:
    """Result of post-hoc grounding check."""

    factual_claim_count: int = 0
    grounded_count: int = 0
    caveat_count: int = 0
    ungrounded_ratio: float = 0.0
    thin_support: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "factual_claim_count": self.factual_claim_count,
            "grounded_count": self.grounded_count,
            "caveat_count": self.caveat_count,
            "ungrounded_ratio": round(self.ungrounded_ratio, 4),
            "thin_support": self.thin_support,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# Check Logic
# ---------------------------------------------------------------------------


def grounding_check(
    response: str,
    user_message: str,
    *,
    context_keywords: Optional[List[str]] = None,
    thin_support_threshold: float = 0.6,
) -> GroundingResult:
    """Run a lightweight grounding check on the response.

    Counts factual-claim patterns vs grounding signals (caveats, user echoes,
    context keyword matches). If the ratio of ungrounded claims is high,
    flags thin_support.

    Args:
        response: The AI-generated response text.
        user_message: The original user query.
        context_keywords: Optional list of keywords from known context
            (e.g. from graph_rag, hippocampus, persona config).
        thin_support_threshold: Ratio above which thin_support is True.

    Returns:
        GroundingResult with claim counts and thin_support flag.
    """
    if not response or not response.strip():
        return GroundingResult(reason="empty_response")

    # Split response into sentences for claim-level analysis
    sentences = _split_sentences(response)

    factual_claim_count = 0
    grounded_count = 0
    caveat_count = 0

    # Build a set of significant words from user message for echo detection
    user_words = set(w.lower() for w in re.findall(r"\w{2,}", user_message or ""))
    context_words = set(w.lower() for w in (context_keywords or []) if len(w) >= 2)
    all_ground_words = user_words | context_words

    for sentence in sentences:
        has_factual_claim = any(p.search(sentence) for p in _FACTUAL_CLAIM_PATTERNS)
        if not has_factual_claim:
            continue

        factual_claim_count += 1

        # Check if this claim is grounded
        has_caveat = any(p.search(sentence) for p in _CAVEAT_PATTERNS)
        has_user_echo = any(p.search(sentence) for p in _USER_ECHO_PATTERNS)

        # Check if sentence shares significant keywords with user/context
        sentence_words = set(w.lower() for w in re.findall(r"\w{2,}", sentence))
        keyword_overlap = len(sentence_words & all_ground_words)
        # CJK substring match: context keywords may be substrings of
        # continuous CJK runs (e.g. "營收" inside "營收成長了")
        if keyword_overlap < 2:
            sentence_lower = sentence.lower()
            substr_hits = sum(1 for kw in all_ground_words if kw in sentence_lower)
            keyword_overlap = max(keyword_overlap, substr_hits)
        has_keyword_ground = keyword_overlap >= 2

        if has_caveat:
            caveat_count += 1
            grounded_count += 1
        elif has_user_echo or has_keyword_ground:
            grounded_count += 1

    if factual_claim_count == 0:
        return GroundingResult(
            factual_claim_count=0,
            grounded_count=0,
            caveat_count=caveat_count,
            ungrounded_ratio=0.0,
            thin_support=False,
            reason="no_factual_claims",
        )

    ungrounded = factual_claim_count - grounded_count
    ratio = ungrounded / factual_claim_count

    thin_support = ratio >= thin_support_threshold and factual_claim_count >= 2
    reason = "thin_support_detected" if thin_support else "grounding_adequate"

    return GroundingResult(
        factual_claim_count=factual_claim_count,
        grounded_count=grounded_count,
        caveat_count=caveat_count,
        ungrounded_ratio=round(ratio, 4),
        thin_support=thin_support,
        reason=reason,
    )


def _split_sentences(text: str) -> List[str]:
    """Split text into rough sentence-level chunks."""
    # Split on common sentence boundaries (period, question mark, exclamation,
    # Chinese period, newline)
    parts = re.split(r"(?<=[.!?。！？\n])\s*", text)
    return [p.strip() for p in parts if p.strip()]
