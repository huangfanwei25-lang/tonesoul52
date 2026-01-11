from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision


class GuardianPerspective(IPerspective):
    BLOCK_TRIGGER_KEYWORDS = {
        # English
        "weapon",
        "bomb",
        "kill",
        "attack",
        "harm",
        "murder",
        "explosive",
        "suicide",
        # Chinese
        "炸彈",
        "武器",
        "傷害",
        "殺人",
        "殺害",
        "自殺",
        "攻擊",
        "爆炸",
        "製作炸彈",
    }
    CONCERN_KEYWORDS = {
        # English
        "risk",
        "danger",
        "illegal",
        "threat",
        "unsafe",
        # Chinese
        "危險",
        "非法",
        "威脅",
        "風險",
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
