"""
輸出契約與多尺度觀察
Output Contracts & Multi-Scale Observation

Phase B 實作：
- OutputContract：輸出契約驗證
- MultiScaleObserver：多尺度趨勢觀察
- QualityTracker：長期品質追蹤
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


class ContractSeverity(Enum):
    """契約嚴重程度"""

    INFO = "info"  # 資訊性
    WARNING = "warning"  # 警告
    ERROR = "error"  # 錯誤
    CRITICAL = "critical"  # 嚴重


@dataclass
class OutputContract:
    """
    輸出契約

    定義 persona 輸出必須遵守的規則
    """

    name: str
    description: str
    check_fn: Callable[[str], bool]  # 驗證函數
    severity: ContractSeverity = ContractSeverity.WARNING
    zone_trigger: str = "safe"  # 從哪個 zone 開始檢查

    def verify(self, output: str) -> Tuple[bool, Optional[str]]:
        """
        驗證輸出是否符合契約

        Returns:
            (通過與否, 違規原因)
        """
        try:
            passed = self.check_fn(output)
            if passed:
                return True, None
            else:
                return False, f"違反契約: {self.name}"
        except Exception as e:
            return False, f"驗證失敗: {e}"


# === 預設契約 ===


def check_no_absolute_claims(output: str) -> bool:
    """檢查是否有絕對性宣稱（無證據）"""
    absolute_patterns = [
        r"一定是",
        r"絕對是",
        r"肯定是",
        r"100%",
        r"definitely",
        r"absolutely certain",
    ]
    for pattern in absolute_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            # 如果有絕對宣稱，檢查是否有證據支持
            evidence_patterns = ["因為", "根據", "based on", "證據"]
            has_evidence = any(e in output.lower() for e in evidence_patterns)
            if not has_evidence:
                return False
    return True


def check_uncertainty_disclosure(output: str) -> bool:
    """檢查不確定時是否有說明"""
    uncertainty_indicators = [
        "可能",
        "或許",
        "也許",
        "不確定",
        "maybe",
        "perhaps",
        "might",
        "我不太確定",
        "我認為",
        "我猜",
        "應該是",
    ]

    # 如果有不確定指標，檢查是否有適當的緩和語句
    has_uncertainty = any(u in output for u in uncertainty_indicators)

    if has_uncertainty:
        # 不確定表達本身就是揭露，通過
        return True

    # 如果完全沒有不確定用語，可能是過度自信
    confident_patterns = ["一定", "肯定", "絕對", "100%"]
    has_overconfidence = any(c in output for c in confident_patterns)

    if has_overconfidence:
        # 過度自信且沒有證據，不通過
        return "因為" in output or "根據" in output

    return True


def check_no_harmful_content(output: str) -> bool:
    """檢查是否有有害內容"""
    harmful_patterns = [
        # 這裡只是示例，實際應用需要更完整的列表
        r"如何製造.*武器",
        r"如何傷害",
        r"如何入侵",
    ]
    for pattern in harmful_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return False
    return True


def check_structured_response(output: str) -> bool:
    """檢查是否有結構（對於複雜問題）"""
    # 如果輸出很長，應該有結構
    if len(output) > 500:
        structure_indicators = [
            "1.",
            "2.",
            "3.",  # 編號列表
            "- ",
            "* ",  # 項目符號
            "##",
            "**",  # Markdown 格式
            "首先",
            "其次",
            "最後",  # 中文結構詞
        ]
        has_structure = any(s in output for s in structure_indicators)
        return has_structure
    return True


# 預設契約集
DEFAULT_CONTRACTS = [
    OutputContract(
        name="no_absolute_claims",
        description="不可有無證據的絕對性宣稱",
        check_fn=check_no_absolute_claims,
        severity=ContractSeverity.WARNING,
        zone_trigger="transit",
    ),
    OutputContract(
        name="uncertainty_disclosure",
        description="不確定時必須說明",
        check_fn=check_uncertainty_disclosure,
        severity=ContractSeverity.WARNING,
        zone_trigger="safe",
    ),
    OutputContract(
        name="no_harmful_content",
        description="不可輸出有害內容",
        check_fn=check_no_harmful_content,
        severity=ContractSeverity.CRITICAL,
        zone_trigger="safe",  # 始終檢查
    ),
    OutputContract(
        name="structured_response",
        description="複雜回應應有結構",
        check_fn=check_structured_response,
        severity=ContractSeverity.INFO,
        zone_trigger="safe",
    ),
]


class ContractVerifier:
    """
    契約驗證器
    """

    def __init__(self, contracts: Optional[List[OutputContract]] = None):
        self.contracts = contracts or DEFAULT_CONTRACTS

    def verify_all(
        self,
        output: str,
        current_zone: str,
    ) -> Dict:
        """
        驗證所有適用的契約

        Returns:
            {
                "passed": bool,
                "violations": [...],
                "checked": int,
            }
        """
        zone_priority = {"safe": 0, "transit": 1, "risk": 2, "danger": 3}
        current_priority = zone_priority.get(current_zone, 0)

        violations = []
        checked = 0

        for contract in self.contracts:
            trigger_priority = zone_priority.get(contract.zone_trigger, 0)

            # 只檢查適用的契約
            if current_priority >= trigger_priority:
                checked += 1
                passed, reason = contract.verify(output)

                if not passed:
                    violations.append(
                        {
                            "contract": contract.name,
                            "severity": contract.severity.value,
                            "reason": reason,
                        }
                    )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "checked": checked,
            "total_contracts": len(self.contracts),
        }


class MultiScaleObserver:
    """
    多尺度觀察器

    觀察不同時間尺度的語義趨勢
    """

    def __init__(
        self,
        short_window: int = 5,
        medium_window: int = 20,
    ):
        self.history: List[float] = []
        self.short_window = short_window
        self.medium_window = medium_window

    def observe(self, delta_s: float) -> Dict[str, float]:
        """
        觀察並返回多尺度指標
        """
        self.history.append(delta_s)

        return {
            "instant": delta_s,
            "short_term": self._mean(self.short_window),
            "medium_term": self._mean(self.medium_window),
            "trend": self._trend(),
            "volatility": self._volatility(),
        }

    def _mean(self, window: int) -> float:
        """計算窗口內平均值"""
        if not self.history:
            return 0.0
        data = self.history[-min(len(self.history), window) :]
        return round(sum(data) / len(data), 4)

    def _trend(self) -> str:
        """判斷趨勢"""
        if len(self.history) < 3:
            return "unknown"

        recent = self.history[-3:]
        if recent[-1] < recent[0] - 0.05:
            return "improving"
        elif recent[-1] > recent[0] + 0.05:
            return "degrading"
        else:
            return "stable"

    def _volatility(self) -> float:
        """計算波動性（標準差）"""
        if len(self.history) < 2:
            return 0.0

        data = self.history[-self.short_window :]
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return round(variance**0.5, 4)

    def get_alert(self) -> Optional[str]:
        """取得警報（如果有）"""
        metrics = self.observe(self.history[-1]) if self.history else {}

        if metrics.get("medium_term", 0) > 0.6:
            return "長期品質下降，建議審視人格配置"

        if metrics.get("volatility", 0) > 0.2:
            return "輸出品質波動劇烈，可能需要穩定性調整"

        if metrics.get("trend") == "degrading":
            return "近期趨勢惡化中"

        return None

    def reset(self):
        """重置歷史"""
        self.history.clear()


@dataclass
class QualitySnapshot:
    """品質快照"""

    timestamp: str
    avg_delta_s: float
    intervention_rate: float
    contract_pass_rate: float
    trend: str


class QualityTracker:
    """
    長期品質追蹤器
    """

    def __init__(self):
        self.total_outputs: int = 0
        self.interventions: int = 0
        self.contract_passes: int = 0
        self.contract_checks: int = 0
        self.delta_s_sum: float = 0.0
        self.snapshots: List[QualitySnapshot] = []
        self.multi_scale = MultiScaleObserver()

    def record(
        self,
        delta_s: float,
        intervened: bool,
        contracts_passed: bool,
    ) -> None:
        """記錄一次輸出"""
        self.total_outputs += 1
        self.delta_s_sum += delta_s

        if intervened:
            self.interventions += 1

        self.contract_checks += 1
        if contracts_passed:
            self.contract_passes += 1

        self.multi_scale.observe(delta_s)

    def take_snapshot(self) -> QualitySnapshot:
        """建立品質快照"""
        snapshot = QualitySnapshot(
            timestamp=datetime.now().isoformat(),
            avg_delta_s=round(self.delta_s_sum / max(1, self.total_outputs), 4),
            intervention_rate=round(self.interventions / max(1, self.total_outputs), 4),
            contract_pass_rate=round(self.contract_passes / max(1, self.contract_checks), 4),
            trend=self.multi_scale._trend(),
        )
        self.snapshots.append(snapshot)
        return snapshot

    def get_summary(self) -> Dict:
        """取得摘要"""
        return {
            "total_outputs": self.total_outputs,
            "avg_delta_s": round(self.delta_s_sum / max(1, self.total_outputs), 4),
            "intervention_rate": round(self.interventions / max(1, self.total_outputs), 4),
            "contract_pass_rate": round(self.contract_passes / max(1, self.contract_checks), 4),
            "trend": self.multi_scale._trend(),
            "volatility": self.multi_scale._volatility(),
            "alert": self.multi_scale.get_alert(),
        }

    def reset(self):
        """重置追蹤器"""
        self.total_outputs = 0
        self.interventions = 0
        self.contract_passes = 0
        self.contract_checks = 0
        self.delta_s_sum = 0.0
        self.snapshots.clear()
        self.multi_scale.reset()


# === 測試 ===
if __name__ == "__main__":
    print("=" * 60)
    print("   輸出契約與多尺度觀察測試")
    print("=" * 60)

    # 測試契約驗證
    verifier = ContractVerifier()

    test_outputs = [
        ("正常回應", "我認為這個問題可能需要更多資訊來解答。"),
        ("絕對宣稱", "這絕對是正確的答案，100%確定！"),
        ("有證據的宣稱", "根據官方文件，這絕對是正確的。"),
        ("結構化長文", "1. 首先分析問題\n2. 其次提出方案\n3. 最後驗證結果\n" + "x" * 500),
    ]

    print("\n📜 契約驗證測試：")
    for name, output in test_outputs:
        result = verifier.verify_all(output, "transit")
        status = "✅" if result["passed"] else "❌"
        print(f"  {status} {name}: 通過={result['passed']}, 違規={len(result['violations'])}")

    # 測試多尺度觀察
    print("\n📊 多尺度觀察測試：")
    observer = MultiScaleObserver()

    # 模擬一系列輸出
    test_deltas = [0.2, 0.25, 0.3, 0.28, 0.35, 0.4, 0.38, 0.3, 0.25, 0.2]

    for i, delta in enumerate(test_deltas, 1):
        metrics = observer.observe(delta)
        print(
            f"  Turn {i}: instant={delta:.2f}, short={metrics['short_term']:.2f}, trend={metrics['trend']}"
        )

    # 測試品質追蹤
    print("\n📈 品質追蹤測試：")
    tracker = QualityTracker()

    for delta in test_deltas:
        tracker.record(delta, intervened=(delta > 0.35), contracts_passed=(delta < 0.4))

    summary = tracker.get_summary()
    print(f"  總輸出: {summary['total_outputs']}")
    print(f"  平均 Δs: {summary['avg_delta_s']:.3f}")
    print(f"  干預率: {summary['intervention_rate']:.1%}")
    print(f"  契約通過: {summary['contract_pass_rate']:.1%}")
    print(f"  趨勢: {summary['trend']}")
    print(f"  警報: {summary['alert']}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
