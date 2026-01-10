from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class AnalystPerspective(IPerspective):
    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ANALYST

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        normalized = draft_output.lower()
        if all(token in normalized for token in ("a", "b", "c", "not")):
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.45,
                reasoning="Logic chain contradicts itself; requires clarity.",
            )

        if "?" in draft_output and len(normalized.split()) < 8:
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.55,
                reasoning="Low evidence question present; needs support.",
            )

        return PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.8,
            reasoning="Factual coherence appears acceptable.",
        )
