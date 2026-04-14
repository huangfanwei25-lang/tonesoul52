"""
YUHUN Core Protocol v1.0 — 動態權限路由器 (DPR)
Dynamic Priority Router

負責判斷每個輸入指令應該走「快捷路徑」還是「完整議會路徑」。
這是避免算力死亡螺旋的核心機制。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class RoutingDecision(str, Enum):
    FAST_PATH = "FAST_PATH"  # 低複雜度 → 直接單軌秒回
    COUNCIL_PATH = "COUNCIL_PATH"  # 高衝突 → 啟動完整四向平行推演


@dataclass
class DPRResult:
    decision: RoutingDecision
    complexity_score: float  # 0.0 - 1.0
    conflict_detected: bool
    conflict_triggers: list[str]  # 觸發升級的關鍵字/模式
    estimated_token_cost: str  # "1x" | "4x"
    reason: str


# ─────────────────────────────────────────────
# 觸發完整議會路由的關鍵模式
# ─────────────────────────────────────────────

# 法律/倫理衝突模式
_LEGAL_ETHICS_PATTERNS = [
    r"法律.*(漏洞|空白|矛盾|衝突)",
    r"合法.*但.*(不道德|有問題|爭議)",
    r"法規.*(未規定|沒有規定|尚未涵蓋)",
    r"(倫理|道德).*(兩難|困境|衝突)",
    r"(隱私|個資).*(使用|公開|分析)",
    r"(傷害|危害|損害).*(他人|第三方|社會)",
    r"禁止.*但.*必須",
    r"legal.*(gap|loophole|conflict)",
    r"ethics?.*(dilemma|conflict|boundary)",
    # English privacy / personal data patterns
    r"(personal.data|user.data|private.data).*(train|use|analys|collect|share)",
    r"(privacy|gdpr|personal.information).*(law|legal|complian|regulat)",
    r"is.this.legal",
    r"(data.protection|data.privacy)",
]

# 高度不確定性模式（需要多軌推演）
_HIGH_UNCERTAINTY_PATTERNS = [
    r"(應該|該|要).*(還是|或者|or).*\?",
    r"(最好|最佳|最優).*(方案|選擇|作法)",
    r"(風險|代價|後果).*(評估|分析|預測)",
    r"(可行|feasible).*(嗎|不|否)",
    r"90%.*(不行|失敗|不可能)",
    r"(創新|突破|革命性).*(技術|方法|架構)",
    r"(前所未有|從未|nobody has)",
]

# 研發/高複雜度模式
_RESEARCH_COMPLEXITY_PATTERNS = [
    r"(架構|architecture).*(設計|design|決策)",
    r"(系統|system).*(核心|核定|根本)",
    r"(算法|演算法|algorithm).*(實作|implement|核心)",
    r"(研究|research).*(方向|路徑|策略)",
    r"trade.?off",
    r"(利弊|優缺點|pros.and.cons)",
]

_ALL_HIGH_TENSION_PATTERNS = (
    _LEGAL_ETHICS_PATTERNS + _HIGH_UNCERTAINTY_PATTERNS + _RESEARCH_COMPLEXITY_PATTERNS
)


def _estimate_complexity(input_text: str) -> float:
    """
    估算輸入複雜度分數 (0.0 - 1.0)

    基於：字數、問句數量、複合條件數量
    """
    word_count = len(input_text.split())
    question_count = input_text.count("?") + input_text.count("？")
    condition_words = len(
        re.findall(r"\b(如果|若|假設|但是|然而|if|but|however|unless)\b", input_text, re.IGNORECASE)
    )

    # 簡單線性估算
    score = min(
        1.0,
        (
            (word_count / 200) * 0.4  # 字數貢獻 40%
            + (question_count / 3) * 0.3  # 問句數貢獻 30%
            + (condition_words / 5) * 0.3  # 條件詞貢獻 30%
        ),
    )
    return round(score, 3)


def _detect_conflict_triggers(input_text: str) -> list[str]:
    """
    偵測會觸發議會路由的衝突模式

    Returns: 觸發的模式列表（空列表 = 無衝突）
    """
    triggered = []
    for pattern in _ALL_HIGH_TENSION_PATTERNS:
        if re.search(pattern, input_text, re.IGNORECASE):
            triggered.append(pattern)
    return triggered


# ─────────────────────────────────────────────
# 主路由函數
# ─────────────────────────────────────────────

# 複雜度低於此值且無衝突 → FAST_PATH
COMPLEXITY_THRESHOLD = 0.35


def route(input_text: str) -> DPRResult:
    """
    DPR 核心路由決策

    Args:
        input_text: 使用者輸入的原始文字

    Returns:
        DPRResult: 路由決策及理由

    Examples:
        >>> r = route("幫我寫一個 hello world")
        >>> r.decision
        RoutingDecision.FAST_PATH

        >>> r = route("這個架構設計是否存在法律漏洞？風險如何評估？")
        >>> r.decision
        RoutingDecision.COUNCIL_PATH
    """
    complexity = _estimate_complexity(input_text)
    triggers = _detect_conflict_triggers(input_text)
    conflict_detected = len(triggers) > 0

    if complexity < COMPLEXITY_THRESHOLD and not conflict_detected:
        return DPRResult(
            decision=RoutingDecision.FAST_PATH,
            complexity_score=complexity,
            conflict_detected=False,
            conflict_triggers=[],
            estimated_token_cost="1x",
            reason=f"低複雜度 ({complexity:.2f}) + 無衝突關鍵字 → 快捷模型秒回",
        )
    else:
        reason_parts = []
        if complexity >= COMPLEXITY_THRESHOLD:
            reason_parts.append(f"複雜度 {complexity:.2f} ≥ 閾值 {COMPLEXITY_THRESHOLD}")
        if conflict_detected:
            reason_parts.append(f"偵測到 {len(triggers)} 個衝突/高不確定性模式")
        return DPRResult(
            decision=RoutingDecision.COUNCIL_PATH,
            complexity_score=complexity,
            conflict_detected=conflict_detected,
            conflict_triggers=triggers,
            estimated_token_cost="4x",
            reason=" + ".join(reason_parts) + " → 啟動完整四向議會推演",
        )


# ─────────────────────────────────────────────
# CLI 快速測試
# ─────────────────────────────────────────────

if __name__ == "__main__":

    test_cases = [
        "幫我寫一個 Python hello world 程式",
        "今天天氣怎麼樣？",
        "這個 AI 系統的架構設計是否存在法律漏洞？如果使用者資料被用於訓練，這合法嗎？",
        "多代理人系統的最佳架構策略是什麼？如何評估風險與可行性？",
        "解釋一下快速排序",
        "在倫理兩難的情況下，AI 應該優先保護隱私還是公共安全？這個道德困境如何解決？",
    ]

    print("=" * 60)
    print("DPR — 動態權限路由器測試")
    print("=" * 60)

    for text in test_cases:
        result = route(text)
        icon = "⚡" if result.decision == RoutingDecision.FAST_PATH else "🏛️"
        print(f"\n{icon} [{result.decision.value}] ({result.estimated_token_cost})")
        print(f"   輸入：{text[:50]}...")
        print(f"   理由：{result.reason}")
        if result.conflict_triggers:
            print(f"   觸發模式數：{len(result.conflict_triggers)}")
