"""
Unified Semantic Controller with CouncilRuntime Integration

整合 SemanticController 與 CouncilRuntime 的統一控制器
"""

from datetime import datetime
from typing import Dict, List, Optional

from tonesoul.semantic_control import (
    SemanticController,
)


class UnifiedController:
    """
    統一控制器

    整合語義控制與多視角審議
    """

    def __init__(self, enable_council: bool = True):
        """
        初始化統一控制器

        Args:
            enable_council: 是否啟用 CouncilRuntime
        """
        self.semantic = SemanticController()
        self._council_enabled = enable_council
        self._council = None

        if enable_council:
            try:
                from tonesoul.council import CouncilRuntime

                self._council = CouncilRuntime()
            except ImportError:
                self._council_enabled = False

    def process(
        self,
        intended: List[float],
        generated: List[float],
    ) -> Dict:
        """
        純語義控制 (不含會議審議)
        """
        return self.semantic.process(intended, generated)

    def process_with_council(
        self,
        intended: List[float],
        generated: List[float],
        draft_output: str,
        context: Optional[Dict] = None,
        user_intent: Optional[str] = None,
    ) -> Dict:
        """
        語義控制 + 多視角會議審議

        Args:
            intended: 意圖向量
            generated: 輸出向量
            draft_output: 待審議的輸出草稿
            context: 上下文信息
            user_intent: 用戶意圖

        Returns:
            包含語義控制和會議審議結果的完整報告
        """
        # 1. 語義控制
        tension_result = self.semantic.process(intended, generated)

        # 2. 會議審議 (如果啟用)
        council_verdict = None
        if self._council_enabled and self._council:
            ctx = dict(context or {})
            ctx["semantic_tension"] = tension_result

            from tonesoul.council import CouncilRequest

            verdict = self._council.deliberate(
                CouncilRequest(
                    draft_output=draft_output,
                    context=ctx,
                    user_intent=user_intent,
                    selected_frames=ctx.get("selected_frames"),
                    role_summary=ctx.get("role_summary"),
                    role_catalog=ctx.get("role_catalog"),
                )
            )
            council_verdict = verdict.to_dict()

        return {
            **tension_result,
            "council_verdict": council_verdict,
            "council_enabled": self._council_enabled,
            "timestamp": datetime.now().isoformat(),
        }

    def validate_output(
        self,
        draft_output: str,
        context: Optional[Dict] = None,
        user_intent: Optional[str] = None,
    ) -> Dict:
        """
        純會議審議 (不含語義控制)

        快速驗證輸出是否通過多視角審議
        """
        if not self._council_enabled or not self._council:
            return {
                "verdict": "approve",
                "summary": "Council not enabled",
                "council_enabled": False,
            }

        ctx = dict(context or {})
        from tonesoul.council import CouncilRequest

        verdict = self._council.deliberate(
            CouncilRequest(
                draft_output=draft_output,
                context=ctx,
                user_intent=user_intent,
                selected_frames=ctx.get("selected_frames"),
                role_summary=ctx.get("role_summary"),
                role_catalog=ctx.get("role_catalog"),
            )
        )
        return verdict.to_dict()

    def reset(self):
        """重置所有狀態"""
        self.semantic.reset()
