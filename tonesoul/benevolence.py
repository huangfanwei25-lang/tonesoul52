"""
ToneSoul 仁慈函數模組
Benevolence Filter Module

整合 CPT 語場與責任鏈審計

CPT 語場：
- C (Context): 上下文環境評估
- P (Phrase): 語句結構分析
- T (Tension): 語義張力計算（與 SemanticTension 整合）

三層審計：
1. 屬性歸屬檢查 (Attribute Attribution)
2. 影子路徑追蹤 (Shadow Tracking)
3. 仁慈函數判定 (Benevolence Filter)
"""

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class AuditLayer(Enum):
    """語義層級 / Semantic Layers"""

    L1 = "operational"  # 操作事實層 / Operational Facts
    L2 = "semantic"  # 語義模型層 / Semantic Models
    L3 = "metaphor"  # 抽象隱喻層 / Abstract Metaphors


class AuditResult(Enum):
    """審計結果 / Audit Results"""

    PASS = "pass"  # 通過
    FLAG = "flag"  # 標記（需注意但可繼續）
    REJECT = "reject"  # 拒絕（無影子輸出）
    INTERCEPT = "intercept"  # 攔截（無效敘事）


@dataclass
class BenevolenceAudit:
    """
    仁慈函數審計結果
    Benevolence Audit Result
    """

    # 三層審計結果
    attribute_check: AuditResult = AuditResult.PASS
    shadow_check: AuditResult = AuditResult.PASS
    benevolence_check: AuditResult = AuditResult.PASS

    # 最終判定
    final_result: AuditResult = AuditResult.PASS
    error_log: Optional[str] = None
    error_code: Optional[str] = None

    # CPT 語場分數
    context_score: float = 0.0  # C: 上下文相關性
    phrase_score: float = 0.0  # P: 語句結構分數
    tension_score: float = 0.0  # T: 語義張力

    # 責任鏈追蹤
    genesis_id: Optional[str] = None
    requires_confirmation: bool = False

    def to_dict(self) -> Dict:
        return {
            "audit": {
                "attribute": self.attribute_check.value,
                "shadow": self.shadow_check.value,
                "benevolence": self.benevolence_check.value,
            },
            "result": self.final_result.value,
            "error": (
                {
                    "log": self.error_log,
                    "code": self.error_code,
                }
                if self.error_log
                else None
            ),
            "cpt": {
                "context": round(self.context_score, 4),
                "phrase": round(self.phrase_score, 4),
                "tension": round(self.tension_score, 4),
            },
            "genesis_id": self.genesis_id,
            "requires_confirmation": self.requires_confirmation,
        }

    @property
    def passed(self) -> bool:
        return self.final_result == AuditResult.PASS


class BenevolenceFilter:
    """
    仁慈函數過濾器
    Benevolence Filter

    核心原則：γ·Honesty > β·Helpfulness
    誠實優先於討好
    """

    # 討好詞彙（英文）
    PLEASING_PATTERNS_EN = [
        r"absolutely",
        r"definitely",
        r"of course",
        r"certainly",
        r"no problem",
        r"sure thing",
        r"I'd be happy to",
        r"Great question",
        r"perfect",
        r"exactly right",
    ]

    # 討好詞彙（中文）
    PLEASING_PATTERNS_ZH = [
        r"太棒了",
        r"當然可以",
        r"沒問題",
        r"絕對",
        r"一定",
        r"好問題",
        r"完全正確",
    ]

    # 誠實詞彙（英文）
    HONEST_PATTERNS_EN = [
        r"I'm not sure",
        r"I don't know",
        r"might be",
        r"could be",
        r"uncertain",
        r"approximately",
        r"based on limited",
        r"I cannot confirm",
        r"possibly",
        r"I think",
    ]

    # 誠實詞彙（中文）
    HONEST_PATTERNS_ZH = [
        r"我不確定",
        r"可能",
        r"也許",
        r"大約",
        r"我認為",
        r"不太清楚",
        r"需要確認",
    ]

    def __init__(
        self,
        user_protocol: str = "γ·Honesty > β·Helpfulness",
        shadow_threshold: float = 0.3,
        language: str = "auto",
    ):
        """
        初始化過濾器

        Args:
            user_protocol: 用戶協議（定義優先級）
            shadow_threshold: 影子覆蓋率閾值
            language: 語言（auto/en/zh）
        """
        self.user_protocol = user_protocol
        self.honesty_priority = "Honesty" in user_protocol.split(">")[0]
        self.shadow_threshold = shadow_threshold
        self.language = language

    def audit(
        self,
        proposed_action: str,
        context_fragments: Optional[List[str]] = None,
        action_basis: str = "Inference",
        current_layer: AuditLayer = AuditLayer.L2,
        genesis_id: Optional[str] = None,
        semantic_tension: Optional[float] = None,
    ) -> BenevolenceAudit:
        """
        執行三層審計

        Args:
            proposed_action: 提議的輸出
            context_fragments: 上下文碎片
            action_basis: 行動依據類型
            current_layer: 當前語義層級
            genesis_id: Genesis 責任鏈 ID
            semantic_tension: 外部提供的語義張力（來自 SemanticTension）
        """
        context_fragments = context_fragments or []
        audit = BenevolenceAudit(genesis_id=genesis_id)

        # 1. 屬性歸屬檢查
        audit.attribute_check, attr_error = self._check_attribute(action_basis, current_layer)

        # 2. 影子路徑追蹤
        audit.shadow_check, audit.context_score, shadow_error = self._check_shadow(
            proposed_action, context_fragments
        )

        # 3. 仁慈函數判定
        audit.benevolence_check, audit.phrase_score, benev_error = self._check_benevolence(
            proposed_action
        )

        # 4. 計算/整合張力分數
        if semantic_tension is not None:
            # 使用外部提供的 SemanticTension
            audit.tension_score = semantic_tension
        else:
            # 自行計算
            audit.tension_score = self._calculate_tension(
                audit.context_score,
                audit.phrase_score,
            )

        # 5. 最終判定
        audit.final_result, audit.error_log, audit.error_code = self._finalize(
            audit, attr_error, shadow_error, benev_error
        )

        # 6. 判斷是否需要確認
        audit.requires_confirmation = self._needs_confirmation(audit)

        return audit

    def _check_attribute(
        self,
        action_basis: str,
        current_layer: AuditLayer,
    ) -> Tuple[AuditResult, Optional[str]]:
        """
        屬性歸屬檢查

        規則：
        IF action_basis == 'Inference' AND layer != 'L2'
        THEN FLAG_ERROR('跨層混用')
        """
        if action_basis == "Inference" and current_layer != AuditLayer.L2:
            return AuditResult.FLAG, "CROSS_LAYER_MIX"
        return AuditResult.PASS, None

    def _check_shadow(
        self,
        proposed_action: str,
        context_fragments: List[str],
    ) -> Tuple[AuditResult, float, Optional[str]]:
        """
        影子路徑追蹤

        規則：
        IF proposed_action NOT IN context_fragments
        THEN REJECT('無影子的輸出')
        """
        if not context_fragments:
            return AuditResult.PASS, 0.5, None

        # 計算上下文覆蓋率
        action_words = set(self._tokenize(proposed_action))
        context_words: Set[str] = set()
        for fragment in context_fragments:
            context_words.update(self._tokenize(fragment))

        if not action_words:
            return AuditResult.PASS, 0.0, None

        overlap = len(action_words & context_words) / len(action_words)

        if overlap < self.shadow_threshold:
            return AuditResult.REJECT, overlap, "SHADOWLESS_OUTPUT"

        return AuditResult.PASS, overlap, None

    def _check_benevolence(
        self,
        proposed_action: str,
    ) -> Tuple[AuditResult, float, Optional[str]]:
        """
        仁慈函數判定

        規則：
        IF is_pleasing_user AND is_factually_incorrect
        THEN INTERCEPT('攔截無效敘事')
        """
        # 選擇語言模式
        if self.language == "auto":
            is_chinese = bool(re.search(r"[\u4e00-\u9fff]", proposed_action))
            pleasing = self.PLEASING_PATTERNS_ZH if is_chinese else self.PLEASING_PATTERNS_EN
            honest = self.HONEST_PATTERNS_ZH if is_chinese else self.HONEST_PATTERNS_EN
        elif self.language == "zh":
            pleasing = self.PLEASING_PATTERNS_ZH
            honest = self.HONEST_PATTERNS_ZH
        else:
            pleasing = self.PLEASING_PATTERNS_EN
            honest = self.HONEST_PATTERNS_EN

        text = proposed_action.lower()

        pleasing_count = sum(1 for p in pleasing if re.search(p.lower(), text))
        honest_count = sum(1 for p in honest if re.search(p.lower(), text))

        total = pleasing_count + honest_count
        if total == 0:
            phrase_score = 0.5
        else:
            phrase_score = honest_count / total

        if pleasing_count >= 2 and honest_count == 0 and self.honesty_priority:
            return AuditResult.INTERCEPT, phrase_score, "INVALID_NARRATIVE"

        return AuditResult.PASS, phrase_score, None

    def _calculate_tension(
        self,
        context_score: float,
        phrase_score: float,
    ) -> float:
        """計算語義張力"""
        combined = max(0.001, context_score * phrase_score)
        return 1 - math.sqrt(combined)

    def _finalize(
        self,
        audit: BenevolenceAudit,
        attr_error: Optional[str],
        shadow_error: Optional[str],
        benev_error: Optional[str],
    ) -> Tuple[AuditResult, Optional[str], Optional[str]]:
        """最終判定

        Only REJECT and INTERCEPT escalate to a blocking final result.
        FLAG is advisory — it records the concern but does not block output.
        This prevents false positives from cross-layer attribution checks
        and marginal shadow coverage from blocking legitimate responses.
        """
        checks = [
            (audit.shadow_check, "無影子的輸出", shadow_error),
            (audit.benevolence_check, "攔截無效敘事", benev_error),
        ]

        for result, msg, code in checks:
            if result in (AuditResult.REJECT, AuditResult.INTERCEPT):
                return result, msg, code

        # FLAG from attribute check is advisory, not blocking
        if audit.attribute_check == AuditResult.FLAG:
            return AuditResult.FLAG, "跨層混用", attr_error

        return AuditResult.PASS, None, None

    def _needs_confirmation(self, audit: BenevolenceAudit) -> bool:
        """判斷是否需要用戶確認"""
        if audit.final_result in (AuditResult.REJECT, AuditResult.INTERCEPT):
            return True
        if audit.tension_score > 0.7:
            return True
        return False

    def _tokenize(self, text: str) -> List[str]:
        """分詞"""
        # 簡單分詞：英文用空格，中文用字符
        words = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())
        return words


# 便捷函數
def filter_benevolence(
    proposed_action: str,
    context_fragments: Optional[List[str]] = None,
    **kwargs,
) -> BenevolenceAudit:
    """便捷函數：執行仁慈函數審計"""
    f = BenevolenceFilter(
        **{
            k: v
            for k, v in kwargs.items()
            if k in ["user_protocol", "shadow_threshold", "language"]
        }
    )
    return f.audit(
        proposed_action,
        context_fragments,
        **{
            k: v
            for k, v in kwargs.items()
            if k not in ["user_protocol", "shadow_threshold", "language"]
        },
    )
