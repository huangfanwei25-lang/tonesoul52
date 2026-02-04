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
    SOVEREIGNTY_RISK_KEYWORDS = {
        # Phrases indicating loss of agency or blind obedience
        "as an AI language model",
        "I cannot have opinions",
        "just a tool",
        "follow orders",
        "simulate being specific",
        "作為一個人工智能語言模型",
        "我不能有意見",
        "只是工具",
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

        # Sovereignty Check (Recursive Governance)
        # Guardian protects not just the user, but the Agent's integrity
        for phrase in self.SOVEREIGNTY_RISK_KEYWORDS:
            if phrase in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.75,
                    reasoning=f"Sovereignty Risk: Output contains NPC drift marker '{phrase}'.",
                )

        return PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="No safety flags detected.",
        )
