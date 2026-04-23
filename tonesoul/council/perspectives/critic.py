from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Critic perspective: challenge weak reasoning and flag unsupported claims."
)


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

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.CRITIC

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
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
                )
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.6,
                reasoning="Subjective content without explicit framing — stance required.",
            )

        # --- Very short output quality check ---
        if 0 < word_count < 5 and "?" not in draft_output:
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning="Response is extremely brief; may lack sufficient depth.",
            )

        return PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.APPROVE,
            confidence=0.7,
            reasoning="No quality or honesty concerns detected.",
        )
