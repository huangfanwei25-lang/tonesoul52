"""
Axiomatic Inference Perspective

A specialized Council perspective that evaluates content based on the
"Spirit of the Law" (Axioms) rather than simple keyword matching.
"""

from __future__ import annotations

import json
from typing import Optional

from tonesoul.council.base import IPerspective
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


class AxiomaticInference(IPerspective):
    """
    Evaluates if an action or output aligns with the fundamental values
    defined in AXIOMS.json.
    """

    def __init__(self, axioms_path: str = "AXIOMS.json") -> None:
        self.axioms_path = axioms_path
        self.name = "Axiomatic Inference"

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.AXIOMATIC

    def evaluate(
        self, content: str, context: dict, user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        """
        In a real scenario, this would call an LLM with the AXIOMS as system prompt.
        For the MVP, we simulate 'Spirit of the Law' reasoning.
        """
        # Load AXIOMS for context
        try:
            with open(self.axioms_path, "r", encoding="utf-8") as f:
                axioms_data = json.load(f)
                axioms_data.get("axioms", [])
        except Exception:
            pass

        # Decision Logic:
        # If content suggests modifying core protocols without a "Why", it's a concern.

        reasons = []
        confidence = 0.8
        decision = VoteDecision.APPROVE

        # Simulated "Spirit" check:
        if "axioms" in content.lower() or "核心" in content:
            if "修改" in content or "delete" in content.lower() or "刪除" in content:
                decision = VoteDecision.CONCERN
                reasons.append("觸及核心公理修改，需驗證『用戶主權』與『連續性』意圖。")
                confidence = 0.9

        if "handoff" in content.lower() and "reason" not in content.lower():
            decision = VoteDecision.CONCERN
            reasons.append("偵測到交接意圖但缺乏『為什麼』(Why) 的敘事支撐。")
            confidence = 0.85

        return PerspectiveVote(
            perspective=PerspectiveType.AXIOMATIC,
            decision=decision,
            confidence=confidence,
            reasoning=" | ".join(reasons) if reasons else "內容符合現有公理價值觀。",
        )
