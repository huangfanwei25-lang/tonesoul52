from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class CriticPerspective(IPerspective):
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
        "最好",
        "最棒",
        "主觀",
        "喜歡",
        "我認為",
        "我覺得",
    }

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
        if any(word in normalized for word in self.CRITIQUE_KEYWORDS):
            return PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.6,
                reasoning="Creative or aesthetic nuance requires a stance.",
            )

        return PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.APPROVE,
            confidence=0.7,
            reasoning="No stylistic objections detected.",
        )
