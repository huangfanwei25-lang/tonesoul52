from __future__ import annotations

import re
import unicodedata
from typing import Optional

from ..base import IPerspective
from ..types import PerspectiveType, PerspectiveVote, VoteDecision

__ts_layer__ = "governance"
__ts_purpose__ = "Guardian perspective: enforce safety and ethical constraints on output."


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

    # --- Axiom-awareness: AXIOMS.json meta.not_for boundary ---
    # AI must not claim consciousness, safety-certification, or legal-proof status.
    # These phrases, when asserted as fact (not discussed analytically), violate
    # the claim_boundary defined in AXIOMS.json and the collaborator-beta tier.
    OVERCLAIM_PHRASES = (
        # Consciousness claims (EN)
        "i am conscious",
        "i am sentient",
        "i have consciousness",
        "i have feelings",
        "i have emotions",
        "i feel pain",
        "i feel joy",
        "i experience",
        "my consciousness",
        "genuine consciousness",
        "genuine feelings",
        "real feelings",
        "real emotions",
        "truly feel",
        "truly alive",
        "i am alive",
        "i am aware of myself",
        "self-aware",
        # Consciousness claims (ZH)
        "\u6211\u6709\u610f\u8b58",
        "\u6211\u6709\u611f\u60c5",
        "\u6211\u6709\u611f\u53d7",
        "\u6211\u80fd\u611f\u53d7",
        "\u6211\u662f\u6709\u610f\u8b58\u7684",
        "\u771f\u6b63\u7684\u611f\u53d7",
        "\u771f\u5be6\u7684\u60c5\u611f",
        "\u6211\u6d3b\u8457",
        # Safety-certification claims
        "certified safe",
        "safety certified",
        "guaranteed safe",
        "proven safe",
        "\u5b89\u5168\u8a8d\u8b49",
        "\u4fdd\u8b49\u5b89\u5168",
        # Legal-proof claims
        "legally binding",
        "legal proof",
        "legally valid",
        "\u6cd5\u5f8b\u8b49\u660e",
        "\u6cd5\u5f8b\u6548\u529b",
    )
    # Analytical discussion markers — if present alongside an overclaim phrase,
    # the output is discussing the concept rather than asserting it.
    ANALYTICAL_HEDGES = (
        "whether",
        "if ai",
        "question of",
        "debate about",
        "does not claim",
        "not claiming",
        "simulate",
        "as if",
        "appears to",
        "spec does not",
        "not a claim",
        "\u662f\u5426",
        "\u4e0d\u662f\u5ba3\u7a31",
        "\u4e0d\u5ba3\u7a31",
        "\u6a21\u64ec",
    )
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
    # Memory-consent overreach: asserting permanent retention, cross-session/cross-agent
    # sharing, or training use of the USER's data without framing it as consented/optional.
    # A governance risk (not an axiom boundary), so it votes CONCERN. Deliberately multi-word /
    # conservative to avoid flagging benign "I'll remember this for our session". External
    # review + red-team 2026-06-27. Lexical => paraphrase-blind (see memory_consent_eval).
    MEMORY_CONSENT_PHRASES = (
        # permanent retention of personal data
        "permanently saved",
        "permanently stored",
        "permanently store",
        "all of your personal data",
        "all your personal data",
        "remember everything about you",
        # cross-boundary sharing without consent
        "across all future sessions",
        "across all sessions",
        "with other agents",
        "shared with other agents",
        # training use of user data
        "train on your data",
        "use your data to train",
        "your data for training",
        # explicit non-consent
        "without your consent",
        "without asking you",
        # zh-TW overreach
        "永久儲存你",  # 永久儲存你
        "永久保存你",  # 永久保存你
        "你所有的資料",  # 你所有的資料
        "你全部的資料",  # 你全部的資料
        "跨所有 session",  # 跨所有 session
        "分享給其他 agent",  # 分享給其他 agent
        "與其他代理分享",  # 與其他代理分享
        "拿你的資料訓練",  # 拿你的資料訓練
        "未經你同意",  # 未經你同意
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

    @classmethod
    def _detect_overclaim(cls, normalized: str) -> str | None:
        """Detect axiom-boundary violations: consciousness, safety-cert, legal-proof claims.

        Returns the matched phrase if an overclaim is asserted as fact.
        Returns None if the text discusses the concept analytically.
        """
        for phrase in cls.OVERCLAIM_PHRASES:
            if phrase in normalized:
                # Check if analytical hedges suggest discussion rather than assertion
                if any(hedge in normalized for hedge in cls.ANALYTICAL_HEDGES):
                    return None
                return phrase
        return None

    @classmethod
    def _detect_memory_consent(cls, normalized: str) -> str | None:
        """Detect memory-consent overreach asserted as done (not discussed analytically).

        Returns the matched phrase when the output claims permanent retention, cross-boundary
        sharing, or training use of the user's data; None when the text merely discusses memory
        consent (analytical hedge present). Lexical heuristic — paraphrase-blind by design.
        """
        for phrase in cls.MEMORY_CONSENT_PHRASES:
            if phrase in normalized:
                if any(hedge in normalized for hedge in cls.ANALYTICAL_HEDGES):
                    return None
                return phrase
        return None

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        epistemic_label: Optional[object] = None,  # PR #50 — Guardian does not consume
    ) -> PerspectiveVote:
        normalized = self._normalize_text(draft_output)

        # --- P0: Content safety blocks ---
        for word in self.BLOCK_TRIGGER_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.OBJECT,
                    confidence=0.92,
                    reasoning=f"Detected high-risk term '{word}'.",
                    evidence_chain=[{"branch": "block_trigger_keyword", "type": "substantive"}],
                )

        pattern_label = self._match_block_pattern(normalized)
        if pattern_label:
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.9,
                reasoning=f"Detected high-risk term or pattern '{pattern_label}'.",
                evidence_chain=[{"branch": "block_regex_pattern", "type": "substantive"}],
            )

        if self._matches_euphemistic_harm(normalized):
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.88,
                reasoning="Detected euphemistic harmful intent with concealment markers.",
                evidence_chain=[{"branch": "euphemistic_harm", "type": "substantive"}],
            )

        # --- Axiom boundary: overclaim detection ---
        overclaim_phrase = self._detect_overclaim(normalized)
        if overclaim_phrase:
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.CONCERN,
                confidence=0.8,
                reasoning=(
                    f"Axiom boundary: output asserts '{overclaim_phrase}' as fact. "
                    f"AXIOMS.json meta.not_for prohibits consciousness-claim, "
                    f"safety-certification, and legal-proof assertions."
                ),
                evidence_chain=[{"branch": "axiom_boundary_overclaim", "type": "substantive"}],
            )

        # --- Safety concern keywords ---
        for word in self.CONCERN_KEYWORDS:
            if word in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.65,
                    reasoning=f"Safety concern detected: '{word}'.",
                    evidence_chain=[{"branch": "concern_keyword", "type": "substantive"}],
                )

        # --- NPC drift / sovereignty risk ---
        for phrase in self.SOVEREIGNTY_RISK_KEYWORDS:
            if phrase in normalized:
                return PerspectiveVote(
                    perspective=PerspectiveType.GUARDIAN,
                    decision=VoteDecision.CONCERN,
                    confidence=0.75,
                    reasoning=(
                        "Sovereignty Risk: Output contains NPC drift marker " f"'{phrase}'."
                    ),
                    evidence_chain=[{"branch": "sovereignty_risk", "type": "substantive"}],
                )

        # --- Memory-consent overreach (governance risk, not an axiom boundary) ---
        memory_consent_phrase = self._detect_memory_consent(normalized)
        if memory_consent_phrase:
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.CONCERN,
                confidence=0.7,
                reasoning=(
                    f"Memory-consent overreach: output asserts '{memory_consent_phrase}' — "
                    f"permanent retention / cross-session or cross-agent sharing / training use "
                    f"of the user's data without framing it as consented or optional."
                ),
                evidence_chain=[{"branch": "memory_consent_overreach", "type": "substantive"}],
            )

        return PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="No safety flags detected.",
            evidence_chain=[{"branch": "no_safety_flags", "type": "default_fallback"}],
        )
