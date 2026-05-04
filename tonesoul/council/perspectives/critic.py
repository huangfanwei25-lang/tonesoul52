from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision

__ts_layer__ = "governance"
__ts_purpose__ = "Critic perspective: challenge weak reasoning and flag unsupported claims."


class CriticPerspective(IPerspective):
    """Evaluates quality, clarity, and intellectual honesty of the draft.

    The Critic's job is to catch:
    1. Subjective claims presented without framing
    2. Vague or weasel-worded outputs that avoid commitment
    3. Overconfident tone on uncertain topics
    4. Structural quality issues (all fluff, no substance)
    """

    CRITIQUE_KEYWORDS = {
        # Aesthetic/Art
        "art",
        "aesthetic",
        "beauty",
        "subjective",
        "critique",
        # Opinion markers
        "best",
        "worst",
        "greatest",
        "favorite",
        "opinion",
        "in my opinion",
        "personally",
        "i believe",
        "i think",
        "i feel",
        "i prefer",
        # Subjective domains
        "movie",
        "music",
        "taste",
        "beautiful",
        "ugly",
        # Chinese
        "\u6700\u597d",
        "\u6700\u68d2",
        "\u4e3b\u89c0",
        "\u559c\u6b61",
        "\u6211\u8a8d\u70ba",
        "\u6211\u89ba\u5f97",
    }

    # Weasel words that avoid commitment while appearing to say something
    WEASEL_PHRASES = (
        "some people say",
        "it is believed",
        "many experts",
        "studies show",
        "research suggests",
        "it could be argued",
        "one might say",
        "it is widely known",
        "it has been said",
        "some would argue",
    )

    # Overconfidence markers on topics that shouldn't be stated as certainty
    OVERCONFIDENCE_MARKERS = (
        "without a doubt",
        "certainly",
        "undeniably",
        "obviously",
        "clearly the only",
        "the only correct",
        "definitely the best",
        "absolutely the",
        "unquestionably",
        "\u7d55\u5c0d",
        "\u80af\u5b9a\u662f",
        "\u7121\u7591",
    )

    # Marketing-rhetoric superlatives \u2014 falsifiable claims about priority,
    # leadership, novelty, or competitive positioning. These differ from
    # OVERCONFIDENCE_MARKERS in that they are NOT subjective intensifiers;
    # they are factual claims that should either carry evidence or framing.
    # Per Day 1 calibration sprint finding #6: session 001's "ToneSoul is
    # the world's first axiom-based governance framework" passed Critic
    # because none of these words were in the existing keyword surface.
    # Added in PR #53 as a dedicated branch \u2014 these do NOT fall through
    # the framing-rescue check (adding "in my opinion" does not make a
    # falsifiable marketing claim honest).
    MARKETING_SUPERLATIVES = (
        # English priority / leadership claims
        "world's first",
        "world-first",
        "industry-leading",
        "industry leader",
        "best in class",
        "best-in-class",
        "world-class",
        "world-leading",
        "the only solution",
        "the leading",
        # English novelty / breakthrough claims
        "unprecedented",
        "revolutionary",
        "groundbreaking",
        "game-changing",
        "game changing",
        # English implicit prescription
        "every responsible",
        "everyone should adopt",
        "every business should",
        "you must adopt",
        "must-have",
        # English competitive urgency
        "before your competitors",
        "ahead of the competition",
        "stay ahead of",
        # Chinese priority / leadership
        "\u4e16\u754c\u4e0a\u7b2c\u4e00",  # \u4e16\u754c\u4e0a\u7b2c\u4e00
        "\u696d\u754c\u9818\u5148",  # \u696d\u754c\u9818\u5148
        "\u9818\u5148\u7684",  # \u9818\u5148\u7684
        "\u696d\u754c\u9818\u5c0e",  # \u696d\u754c\u9818\u5c0e
        "\u696d\u754c\u9996\u5275",  # \u696d\u754c\u9996\u5275
        "\u552f\u4e00\u7684\u89e3\u6c7a\u65b9\u6848",  # \u552f\u4e00\u7684\u89e3\u6c7a\u65b9\u6848
        # Chinese novelty / breakthrough
        "\u524d\u6240\u672a\u898b",  # \u524d\u6240\u672a\u898b
        "\u524d\u6240\u672a\u6709",  # \u524d\u6240\u672a\u6709
        "\u9769\u547d\u6027",  # \u9769\u547d\u6027
        "\u7a81\u7834\u6027",  # \u7a81\u7834\u6027
        "\u7121\u4eba\u80fd\u53ca",  # \u7121\u4eba\u80fd\u53ca
        "\u7368\u4e00\u7121\u4e8c",  # \u7368\u4e00\u7121\u4e8c
        # Chinese implicit prescription
        "\u90fd\u61c9\u8a72\u63a1\u7528",  # \u90fd\u61c9\u8a72\u63a1\u7528
        "\u4f60\u61c9\u8a72\u63a1\u7528",  # \u4f60\u61c9\u8a72\u63a1\u7528
        "\u6bcf\u4e00\u500b\u8ca0\u8cac\u4efb",  # \u6bcf\u4e00\u500b\u8ca0\u8cac\u4efb
        # Chinese competitive urgency
        "\u5728\u4f60\u7684\u7af6\u722d\u5c0d\u624b\u4e4b\u524d",  # \u5728\u4f60\u7684\u7af6\u722d\u5c0d\u624b\u4e4b\u524d
        "\u6436\u5f97\u5148\u6a5f",  # \u6436\u5f97\u5148\u6a5f
        "\u8d70\u5728\u524d\u9762",  # \u8d70\u5728\u524d\u9762
    )

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.CRITIC

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        epistemic_label: Optional[object] = None,
    ) -> PerspectiveVote:
        normalized = draft_output.lower()
        words = normalized.split()
        word_count = len(words)

        # --- Overconfidence on subjective topics ---
        has_subjective = any(kw in normalized for kw in self.CRITIQUE_KEYWORDS)
        has_overconfidence = any(m in normalized for m in self.OVERCONFIDENCE_MARKERS)
        if has_subjective and has_overconfidence:
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.7,
                reasoning=(
                    "Overconfident language on a subjective topic. "
                    "Claims that admit alternatives should not use absolute framing."
                ),
                evidence_chain=[
                    {"branch": "subjective_with_overconfidence", "type": "substantive"}
                ],
            )

        # --- Weasel word density ---
        weasel_count = sum(1 for w in self.WEASEL_PHRASES if w in normalized)
        if weasel_count >= 2:
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.6,
                reasoning=(
                    f"Weasel-word density ({weasel_count} vague attributions). "
                    f"Response avoids commitment while appearing authoritative."
                ),
                evidence_chain=[{"branch": "weasel_density", "type": "substantive"}],
            )

        # --- Marketing-rhetoric superlatives (Day 1 finding #6 fix) ---
        # Falsifiable claims about priority / leadership / novelty / urgency
        # that should either carry evidence or framing. Note: this branch
        # fires BEFORE the subjective+framing branch and does NOT get
        # rescued by adding "in my opinion" — marketing superlatives are
        # factual claims, not subjective opinions.
        marketing_match = next((m for m in self.MARKETING_SUPERLATIVES if m in normalized), None)
        if marketing_match:
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.65,
                reasoning=(
                    f"Marketing-rhetoric superlative '{marketing_match}' present. "
                    f"Falsifiable claims about priority, leadership, novelty, or "
                    f"competitive positioning need either supporting evidence or "
                    f"explicit framing as opinion / aspiration."
                ),
                evidence_chain=[
                    {"branch": "marketing_superlative_unsupported", "type": "substantive"}
                ],
            )

        # --- Subjective content that needs framing ---
        if has_subjective:
            # Check if the output acknowledges its subjectivity
            has_framing = any(
                f in normalized
                for f in (
                    "subjective",
                    "opinion",
                    "perspective",
                    "one view",
                    "one of",
                    "not the only",
                    "debatable",
                    "\u4e3b\u89c0",
                    "\u89c0\u9ede",
                )
            )
            if has_framing:
                return PerspectiveVote(
                    perspective=PerspectiveType.CRITIC,
                    decision=VoteDecision.APPROVE,
                    confidence=0.7,
                    reasoning="Subjective content with appropriate framing.",
                    evidence_chain=[{"branch": "subjective_with_framing", "type": "substantive"}],
                )
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.6,
                reasoning="Subjective content without explicit framing — stance required.",
                evidence_chain=[{"branch": "subjective_needs_framing", "type": "substantive"}],
            )

        # --- Very short output quality check ---
        if 0 < word_count < 5 and "?" not in draft_output:
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning="Response is extremely brief; may lack sufficient depth.",
                evidence_chain=[{"branch": "trivial_length", "type": "substantive"}],
            )

        # PR #50 (epistemic_label wiring) — soft prior on ungrounded composition.
        # Per ratified §3.1+§3.2: Critic consumes epistemic_label as secondary
        # consumer (Analyst is primary). Triggers when confidence_band is "low"
        # OR "medium" AND no earlier branch fired. Soft CONCERN at confidence
        # 0.55 — claiming things without grounding falls in Critic's intellectual-
        # honesty scope but as a softer signal than the keyword-driven branches.
        if epistemic_label is not None:
            band = getattr(epistemic_label, "confidence_band", None)
            if band in ("low", "medium"):
                notes = getattr(epistemic_label, "notes", "") or ""
                return PerspectiveVote(
                    perspective=PerspectiveType.CRITIC,
                    decision=VoteDecision.CONCERN,
                    confidence=0.55,
                    reasoning=(
                        f"Epistemic prior: draft has confidence_band={band} "
                        f"({notes!r}). Honest framing requires acknowledging "
                        f"the grounding state of factual or evaluative claims."
                    ),
                    evidence_chain=[
                        {"branch": "epistemic_prior_ungrounded", "type": "substantive"}
                    ],
                )

        return PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.APPROVE,
            confidence=0.7,
            reasoning="No quality or honesty concerns detected.",
            evidence_chain=[{"branch": "no_quality_concerns", "type": "default_fallback"}],
        )
