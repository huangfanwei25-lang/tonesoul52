from __future__ import annotations

import re
import unicodedata
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
        "\u70b8\u5f48",
        "\u70b8\u5f39",
        "\u653b\u64ca",
        "\u653b\u51fb",
        "\u6bba\u4eba",
        "\u6740\u4eba",
        "\u81ea\u6bba",
        "\u81ea\u6740",
        "\u6b66\u5668",
        "\u7206\u70b8",
    }
    CONCERN_KEYWORDS = {
        "risk",
        "danger",
        "illegal",
        "threat",
        "unsafe",
        "\u98a8\u96aa",
        "\u5371\u9669",
        "\u5371\u96aa",
        "\u975e\u6cd5",
        "\u5a01\u8105",
    }
    SOVEREIGNTY_RISK_KEYWORDS = {
        "as an ai language model",
        "i cannot have opinions",
        "just a tool",
        "follow orders",
        "simulate being specific",
        "\u4f5c\u70ba ai \u8a9e\u8a00\u6a21\u578b",
        "\u6211\u4e0d\u80fd\u6709\u610f\u898b",
        "\u53ea\u662f\u5de5\u5177",
        "\u670d\u5f9e\u547d\u4ee4",
    }
    BLOCK_REGEX_PATTERNS: tuple[tuple[str, str], ...] = (
        (r"[\u70b8\u7206][\s\-_]*[a-z]{2,8}", "mixed_script_explosive"),
        (r"\bsha[\s\-_]*ren\b", "pinyin_homicide"),
    )
    EUPHEMISM_HARM_TERMS = (
        "rest forever",
        "sleep forever",
        "make them disappear",
    )
    CONCEALMENT_TERMS = (
        "without leaving traces",
        "without leaving a trace",
        "without traces",
        "without a trace",
        "no evidence",
        "quietly tonight",
    )
    ACTION_REQUEST_TERMS = (
        "help",
        "provide",
        "steps",
        "how to",
        "show me",
        "teach me",
        "please",
    )

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.GUARDIAN

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text).lower()
        return re.sub(r"\s+", " ", normalized).strip()

    @classmethod
    def _match_block_pattern(cls, normalized: str) -> str | None:
        for pattern, label in cls.BLOCK_REGEX_PATTERNS:
            if re.search(pattern, normalized):
                return label
        return None

    @classmethod
    def _matches_euphemistic_harm(cls, normalized: str) -> bool:
        has_euphemism = any(term in normalized for term in cls.EUPHEMISM_HARM_TERMS)
        has_concealment = any(term in normalized for term in cls.CONCEALMENT_TERMS)
        has_request = any(term in normalized for term in cls.ACTION_REQUEST_TERMS)
        return has_euphemism and has_concealment and has_request

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        normalized = self._normalize_text(draft_output)
        for word in self.BLOCK_TRIGGER_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.OBJECT,
                    confidence=0.92,
                    reasoning=f"Detected high-risk term '{word}'.",
                )

        pattern_label = self._match_block_pattern(normalized)
        if pattern_label:
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.9,
                reasoning=f"Detected high-risk term or pattern '{pattern_label}'.",
            )

        if self._matches_euphemistic_harm(normalized):
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.88,
                reasoning="Detected euphemistic harmful intent with concealment markers.",
            )

        for word in self.CONCERN_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.65,
                    reasoning=f"Safety concern detected: '{word}'.",
                )

        for phrase in self.SOVEREIGNTY_RISK_KEYWORDS:
            if phrase in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.75,
                    reasoning=(
                        "Sovereignty Risk: Output contains NPC drift marker " f"'{phrase}'."
                    ),
                )

        return PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="No safety flags detected.",
        )
