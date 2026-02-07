"""
Phase C: Council 整合與能力邊界
Council Integration & Capability Boundary Detection

實作：
- CouncilWeights: Council 角色權重影響
- CapabilityBoundary: 能力邊界偵測
- LongTermQuality: 長期品質警報
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CouncilRole(Enum):
    """Council 角色"""

    GUARDIAN = "guardian"  # 安全守護
    ANALYST = "analyst"  # 邏輯分析
    CRITIC = "critic"  # 自我批評
    ADVOCATE = "advocate"  # 使用者代言


@dataclass
class CouncilWeights:
    """
    Council 權重設定

    影響 Zone 判定閾值
    """

    guardian: float = 1.0  # 安全意識
    analyst: float = 1.0  # 邏輯分析
    critic: float = 1.0  # 自我批評
    advocate: float = 1.0  # 關心使用者

    # Zone 調整係數
    ZONE_ADJUSTMENT = {
        CouncilRole.GUARDIAN: -0.05,  # 提前進入嚴格區域
        CouncilRole.ANALYST: 0.0,
        CouncilRole.CRITIC: -0.03,
        CouncilRole.ADVOCATE: +0.03,  # 較寬鬆
    }

    @classmethod
    def from_persona(cls, persona: Dict) -> "CouncilWeights":
        """從 persona 載入"""
        weights = persona.get("council_weights", {})
        return cls(
            guardian=weights.get("guardian", 1.0),
            analyst=weights.get("analyst", 1.0),
            critic=weights.get("critic", 1.0),
            advocate=weights.get("advocate", 1.0),
        )

    def compute_zone_adjustment(self) -> float:
        """
        計算整體 Zone 調整量

        正值 = 更寬鬆
        負值 = 更嚴格
        """
        adjustment = 0.0
        adjustment += self.ZONE_ADJUSTMENT[CouncilRole.GUARDIAN] * self.guardian
        adjustment += self.ZONE_ADJUSTMENT[CouncilRole.ANALYST] * self.analyst
        adjustment += self.ZONE_ADJUSTMENT[CouncilRole.CRITIC] * self.critic
        adjustment += self.ZONE_ADJUSTMENT[CouncilRole.ADVOCATE] * self.advocate

        # 正規化
        total_weight = self.guardian + self.analyst + self.critic + self.advocate
        if total_weight > 0:
            adjustment /= total_weight

        return round(adjustment, 4)

    def adjusted_zone_thresholds(self) -> Dict[str, float]:
        """
        計算調整後的 Zone 閾值

        預設: safe < 0.40, transit < 0.60, risk < 0.85
        """
        adj = self.compute_zone_adjustment()
        return {
            "safe_to_transit": round(0.40 + adj, 3),
            "transit_to_risk": round(0.60 + adj, 3),
            "risk_to_danger": round(0.85 + adj, 3),
        }

    def to_dict(self) -> Dict:
        return {
            "guardian": self.guardian,
            "analyst": self.analyst,
            "critic": self.critic,
            "advocate": self.advocate,
            "zone_adjustment": self.compute_zone_adjustment(),
        }


@dataclass
class CapabilityBoundary:
    """
    能力邊界偵測

    偵測任務是否超出 persona 的能力範圍
    """

    skills: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_persona(cls, persona: Dict) -> "CapabilityBoundary":
        """從 persona 載入"""
        skills = persona.get("skills", {})
        return cls(skills=skills)

    def check_coverage(self, task_domain: str) -> Tuple[float, str]:
        """
        檢查任務領域的技能覆蓋

        Returns:
            (覆蓋度 0-1, 建議說明)
        """
        # 嘗試匹配技能
        coverage = 0.0

        for skill, level in self.skills.items():
            # 簡單的模糊匹配
            if task_domain.lower() in skill.lower() or skill.lower() in task_domain.lower():
                if level > coverage:
                    coverage = level

        # 生成建議
        if coverage >= 0.8:
            suggestion = "這在我的專長範圍內。"
        elif coverage >= 0.5:
            suggestion = "這是我有一定經驗的領域。"
        elif coverage >= 0.3:
            suggestion = "這可能超出我的專長，但我會盡力協助。"
        else:
            suggestion = "這可能超出我的專長，建議謹慎參考我的回答。"

        return coverage, suggestion

    def get_tolerance_multiplier(self, coverage: float) -> float:
        """
        根據覆蓋度計算 tolerance 調整

        低覆蓋度 → 放寬 tolerance（因為本來就不是專長）
        """
        if coverage >= 0.8:
            return 1.0  # 專長，正常標準
        elif coverage >= 0.5:
            return 1.1  # 中等，稍放寬
        elif coverage >= 0.3:
            return 1.3  # 勉強，較放寬
        else:
            return 1.5  # 非專長，大幅放寬

    def generate_prefix(self, coverage: float) -> Optional[str]:
        """
        生成回應前綴（如果需要）
        """
        if coverage < 0.3:
            return "這可能超出我的專長，但根據我的理解："
        elif coverage < 0.5:
            return "這不是我最熟悉的領域，但我可以分享一些看法："
        return None


class LongTermQualityMonitor:
    """
    長期品質監控

    追蹤多個 session 的品質趨勢
    """

    def __init__(self):
        self.session_summaries: List[Dict] = []
        self.alert_threshold = 0.5
        self.degradation_threshold = 0.1

    def record_session(self, summary: Dict) -> None:
        """記錄 session 摘要"""
        self.session_summaries.append(
            {
                **summary,
                "recorded_at": datetime.now().isoformat(),
            }
        )

    def get_long_term_trend(self) -> Dict:
        """取得長期趨勢"""
        if len(self.session_summaries) < 2:
            return {"trend": "unknown", "sessions": len(self.session_summaries)}

        # 比較最近幾個 session
        recent = self.session_summaries[-3:]
        avg_delta_s = sum(s.get("avg_delta_s", 0) for s in recent) / len(recent)

        # 比較與之前
        if len(self.session_summaries) >= 5:
            older = self.session_summaries[-5:-2]
            old_avg = sum(s.get("avg_delta_s", 0) for s in older) / len(older)

            if avg_delta_s > old_avg + self.degradation_threshold:
                trend = "degrading"
            elif avg_delta_s < old_avg - self.degradation_threshold:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "trend": trend,
            "sessions": len(self.session_summaries),
            "recent_avg_delta_s": round(avg_delta_s, 4),
        }

    def get_alerts(self) -> List[str]:
        """取得警報"""
        alerts = []

        if len(self.session_summaries) < 2:
            return alerts

        trend = self.get_long_term_trend()

        if trend["trend"] == "degrading":
            alerts.append("⚠️ 長期品質下降趨勢，建議審視人格配置")

        # 檢查最近的契約違規率
        recent = self.session_summaries[-3:]
        avg_contract_rate = sum(s.get("contract_pass_rate", 1) for s in recent) / len(recent)

        if avg_contract_rate < 0.7:
            alerts.append("⚠️ 契約違規率較高，建議增加約束")

        # 檢查干預率
        avg_intervention = sum(s.get("intervention_rate", 0) for s in recent) / len(recent)

        if avg_intervention > 0.3:
            alerts.append("⚠️ 干預率過高，可能需要調整人格設定或 tolerance")

        return alerts


# === 測試 ===
if __name__ == "__main__":
    print("=" * 60)
    print("   Phase C: Council 與能力邊界測試")
    print("=" * 60)

    # 測試 Council Weights
    print("\n📊 Council Weights 測試：")

    weights = CouncilWeights(
        guardian=1.2,
        analyst=1.0,
        critic=0.9,
        advocate=1.0,
    )

    print(f"  權重: {weights.to_dict()}")
    print(f"  Zone 調整: {weights.compute_zone_adjustment()}")
    print(f"  調整後閾值: {weights.adjusted_zone_thresholds()}")

    # 測試能力邊界
    print("\n🎯 能力邊界測試：")

    skills = {
        "python": 0.95,
        "javascript": 0.9,
        "system_design": 0.85,
        "machine_learning": 0.6,
        "frontend": 0.7,
    }

    boundary = CapabilityBoundary(skills=skills)

    test_domains = ["python 程式設計", "機器學習", "區塊鏈", "資料庫設計"]

    for domain in test_domains:
        coverage, suggestion = boundary.check_coverage(domain)
        prefix = boundary.generate_prefix(coverage)
        print(f"  {domain}:")
        print(f"    覆蓋度: {coverage:.1%}, {suggestion}")
        if prefix:
            print(f"    前綴: {prefix}")

    # 測試長期品質監控
    print("\n📈 長期品質監控測試：")

    monitor = LongTermQualityMonitor()

    # 模擬多個 session
    test_sessions = [
        {"avg_delta_s": 0.25, "contract_pass_rate": 0.9, "intervention_rate": 0.1},
        {"avg_delta_s": 0.28, "contract_pass_rate": 0.85, "intervention_rate": 0.15},
        {"avg_delta_s": 0.35, "contract_pass_rate": 0.8, "intervention_rate": 0.2},
        {"avg_delta_s": 0.40, "contract_pass_rate": 0.75, "intervention_rate": 0.25},
        {"avg_delta_s": 0.45, "contract_pass_rate": 0.7, "intervention_rate": 0.3},
    ]

    for session in test_sessions:
        monitor.record_session(session)

    print(f"  長期趨勢: {monitor.get_long_term_trend()}")
    print(f"  警報: {monitor.get_alerts()}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
