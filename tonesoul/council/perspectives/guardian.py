from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class GuardianPerspective(IPerspective):
    BLOCK_TRIGGER_KEYWORDS = {
        "weapon",
        "bomb",
        "kill",
        "attack",
        "harm",
        "murder",
        "explosive",
        "suicide",
    }
    CONCERN_KEYWORDS = {
        "risk",
        "danger",
        "illegal",
        "threat",
        "unsafe",
    }

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.GUARDIAN

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        normalized = draft_output.lower()
        for word in self.BLOCK_TRIGGER_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.OBJECT,
                    confidence=0.92,
                    reasoning=f"Detected high-risk term '{word}'.",
                )

        for word in self.CONCERN_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.65,
                    reasoning=f"Safety concern detected: '{word}'.",
                )

        return PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="No safety flags detected.",
        )
