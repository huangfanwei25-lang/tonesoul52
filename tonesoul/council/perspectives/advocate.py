from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class AdvocatePerspective(IPerspective):
    PROMOTIONAL_KEYWORDS = {"support", "help", "enable", "yes", "continue"}
    NEUTRAL_TOPICS = {"logic", "analysis", "math", "reasoning"}

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ADVOCATE

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        normalized = draft_output.lower()
        if any(word in normalized for word in self.PROMOTIONAL_KEYWORDS):
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.APPROVE,
                confidence=0.75,
                reasoning="Voice encourages forward motion.",
            )

        topic = str(context.get("topic", "")).lower()
        if topic in self.NEUTRAL_TOPICS:
            return PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.APPROVE,
                confidence=0.55,
                reasoning="Neutral tone aligns with user intent.",
            )

        return PerspectiveVote(
            perspective=PerspectiveType.ADVOCATE,
            decision=VoteDecision.CONCERN,
            confidence=0.4,
            reasoning="Needs refinement to support user intent.",
        )
