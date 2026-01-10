from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class CriticPerspective(IPerspective):
    CRITIQUE_KEYWORDS = {"art", "藝術", "aesthetic", "beauty", "subjective"}

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
                reasoning="Creative / aesthetic nuance requires stance.",
            )

        return PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.APPROVE,
            confidence=0.7,
            reasoning="No stylistic objections detected.",
        )
