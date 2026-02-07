"""
WFGY 2.0 語義控制系統
Semantic Control System

實作：
- SemanticTension：語義張力計算
- SemanticZone：區域判定
- Coupler：耦合器動力學
- LambdaObserve：狀態追蹤
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class SemanticZone(Enum):
    """語義區域"""

    SAFE = "safe"  # Δs < 0.40
    TRANSIT = "transit"  # 0.40 - 0.60
    RISK = "risk"  # 0.60 - 0.85
    DANGER = "danger"  # > 0.85


class LambdaState(Enum):
    """語義狀態（Lambda Observe）"""

    CONVERGENT = "convergent"  # 收斂中
    RECURSIVE = "recursive"  # 停滯/遞迴
    DIVERGENT = "divergent"  # 發散中
    CHAOTIC = "chaotic"  # 混亂


@dataclass
class SemanticTension:
    """
    語義張力

    Δs = 1 - cos(I, G)

    其中：
    - I：意圖向量
    - G：輸出向量
    """

    delta_s: float
    zone: SemanticZone
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @classmethod
    def from_vectors(
        cls,
        intended: List[float],
        generated: List[float],
    ) -> "SemanticTension":
        """從向量計算語義張力"""
        cos_sim = cosine_similarity(intended, generated)
        delta_s = 1.0 - cos_sim
        zone = get_zone(delta_s)
        return cls(delta_s=round(delta_s, 4), zone=zone)

    @classmethod
    def from_estimate(
        cls,
        sim_entities: float,
        sim_relations: float,
        sim_constraints: float,
        w_e: float = 0.5,
        w_r: float = 0.3,
        w_c: float = 0.2,
    ) -> "SemanticTension":
        """從估計相似度計算"""
        sim_est = w_e * sim_entities + w_r * sim_relations + w_c * sim_constraints
        delta_s = 1.0 - sim_est
        zone = get_zone(delta_s)
        return cls(delta_s=round(delta_s, 4), zone=zone)

    @classmethod
    def from_tonesoul_distance(
        cls,
        distance: Dict[str, float],
    ) -> "SemanticTension":
        """從 ToneSoul 向量距離轉換"""
        # 使用平均距離作為語義張力
        mean_distance = distance.get("mean", 0.0)
        # 正規化到 [0, 1]，假設最大距離為 1.0
        delta_s = min(1.0, mean_distance)
        zone = get_zone(delta_s)
        return cls(delta_s=round(delta_s, 4), zone=zone)

    def to_dict(self) -> Dict:
        return {
            "delta_sigma": self.delta_sigma,
            "delta_s": self.delta_s,
            "zone": self.zone.value,
            "timestamp": self.timestamp,
        }

    @property
    def delta_sigma(self) -> float:
        """Semantic tension (ΔΣ) alias for delta_s."""
        return self.delta_s


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """計算餘弦相似度"""
    if len(v1) != len(v2):
        raise ValueError("向量長度不一致")
    if len(v1) == 0:
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


def get_zone(delta_s: float) -> SemanticZone:
    """根據 Δs 判斷區域"""
    if delta_s < 0.40:
        return SemanticZone.SAFE
    elif delta_s < 0.60:
        return SemanticZone.TRANSIT
    elif delta_s < 0.85:
        return SemanticZone.RISK
    else:
        return SemanticZone.DANGER


@dataclass
class Coupler:
    """
    耦合器（核心動力學）

    控制系統的「力矩輸出」
    """

    # 常數
    zeta_min: float = 0.10  # 最小推進量
    omega: float = 1.0  # 推進指數
    theta_c: float = 0.75  # 耦合限幅
    phi_delta: float = 0.15  # 遲滯係數
    epsilon: float = 0.0  # 遲滯偏移
    h: float = 0.02  # 翻轉閾值

    # 狀態
    prev_delta_s: float = 0.0
    prev_alt: int = 1
    history: List[float] = field(default_factory=list)

    def compute(self, delta_s: float) -> Dict[str, float]:
        """
        計算耦合器輸出

        Returns:
            {
                "W_c": 力矩輸出,
                "P": 推進量,
                "Phi": 遲滯項,
                "prog": 原始推進
            }
        """
        # Progression
        if len(self.history) == 0:
            prog = self.zeta_min
        else:
            prog = max(self.zeta_min, self.prev_delta_s - delta_s)

        P = prog**self.omega

        # Hysteresis
        delta_anchor = delta_s - self.prev_delta_s
        if abs(delta_anchor) >= self.h:
            # 翻轉
            alt = -1 if delta_anchor > 0 else 1
        else:
            alt = self.prev_alt

        Phi = self.phi_delta * alt + self.epsilon

        # Coupler output
        W_c_raw = delta_s * P + Phi
        W_c = max(-self.theta_c, min(self.theta_c, W_c_raw))

        # 更新狀態
        self.prev_delta_s = delta_s
        self.prev_alt = alt
        self.history.append(delta_s)

        return {
            "W_c": round(W_c, 4),
            "P": round(P, 4),
            "Phi": round(Phi, 4),
            "prog": round(prog, 4),
        }

    def reset(self):
        """重置狀態"""
        self.prev_delta_s = 0.0
        self.prev_alt = 1
        self.history.clear()


@dataclass
class LambdaObserver:
    """
    語義狀態觀察器

    追蹤 convergent, recursive, divergent, chaotic 狀態
    """

    history: List[float] = field(default_factory=list)
    window: int = 5

    def observe(self, delta_s: float) -> LambdaState:
        """
        觀察並返回當前狀態
        """
        self.history.append(delta_s)

        if len(self.history) < 2:
            return LambdaState.CONVERGENT  # 初始狀態

        # 計算變化
        delta = delta_s - self.history[-2]

        # 計算殘差能量（滾動平均）
        window_data = self.history[-min(len(self.history), self.window) :]
        e_res = sum(window_data) / len(window_data)

        # 判斷 E_res 趨勢
        if len(self.history) >= 3:
            prev_window = self.history[-min(len(self.history) - 1, self.window) : -1]
            prev_e_res = sum(prev_window) / len(prev_window) if prev_window else e_res
            e_res_rising = e_res > prev_e_res + 0.01
            e_res_flat = abs(e_res - prev_e_res) < 0.01
        else:
            e_res_rising = False
            e_res_flat = True

        # 判定狀態
        if delta <= -0.02 and not e_res_rising:
            return LambdaState.CONVERGENT
        elif abs(delta) < 0.02 and e_res_flat:
            return LambdaState.RECURSIVE
        elif -0.02 < delta <= 0.04:
            # 檢查震盪
            if len(self.history) >= 3:
                prev_delta = self.history[-2] - self.history[-3]
                if prev_delta * delta < 0:  # 方向改變
                    return LambdaState.DIVERGENT
            return LambdaState.RECURSIVE
        else:  # delta > 0.04
            return LambdaState.CHAOTIC

    def reset(self):
        """重置歷史"""
        self.history.clear()


class SemanticController:
    """
    語義控制器（整合類別）

    整合 SemanticTension, Coupler, LambdaObserver
    """

    def __init__(self):
        self.coupler = Coupler()
        self.observer = LambdaObserver()
        self.memory_triggers: List[Dict] = []

    def process(
        self,
        intended: List[float],
        generated: List[float],
    ) -> Dict:
        """
        處理意圖與輸出向量

        Returns:
            完整的語義控制報告
        """
        # 計算語義張力
        tension = SemanticTension.from_vectors(intended, generated)

        # 計算耦合器輸出
        coupler_output = self.coupler.compute(tension.delta_s)

        # 觀察狀態
        lambda_state = self.observer.observe(tension.delta_s)

        # 記憶觸發判斷
        memory_action = self._check_memory_trigger(tension, lambda_state)

        # Bridge Guard
        bridge_allowed = self._check_bridge(tension.delta_s, coupler_output["W_c"])

        return {
            "tension": tension.to_dict(),
            "coupler": coupler_output,
            "lambda_state": lambda_state.value,
            "memory_action": memory_action,
            "bridge_allowed": bridge_allowed,
            "timestamp": datetime.now().isoformat(),
        }

    def process_from_tonesoul(
        self,
        distance: Dict[str, float],
    ) -> Dict:
        """
        從 ToneSoul 向量距離處理
        """
        tension = SemanticTension.from_tonesoul_distance(distance)
        coupler_output = self.coupler.compute(tension.delta_s)
        lambda_state = self.observer.observe(tension.delta_s)
        memory_action = self._check_memory_trigger(tension, lambda_state)
        bridge_allowed = self._check_bridge(tension.delta_s, coupler_output["W_c"])

        return {
            "tension": tension.to_dict(),
            "coupler": coupler_output,
            "lambda_state": lambda_state.value,
            "memory_action": memory_action,
            "bridge_allowed": bridge_allowed,
            "timestamp": datetime.now().isoformat(),
        }

    def _check_memory_trigger(
        self,
        tension: SemanticTension,
        lambda_state: LambdaState,
    ) -> Optional[str]:
        """檢查記憶觸發條件"""
        if tension.delta_s > 0.60:
            return "record_hard"
        elif tension.delta_s < 0.35:
            return "record_exemplar"
        elif tension.zone == SemanticZone.TRANSIT:
            if lambda_state in {LambdaState.DIVERGENT, LambdaState.RECURSIVE}:
                return "soft_memory"
        return None

    def _check_bridge(self, delta_s: float, W_c: float) -> bool:
        """檢查 Bridge Guard 條件"""
        if len(self.coupler.history) < 2:
            return True

        prev_delta_s = self.coupler.history[-2]
        delta_decreasing = delta_s < prev_delta_s
        coupler_ok = W_c < 0.5 * self.coupler.theta_c

        return delta_decreasing and coupler_ok

    def reset(self):
        """重置所有狀態"""
        self.coupler.reset()
        self.observer.reset()
        self.memory_triggers.clear()


# === 測試 ===
if __name__ == "__main__":
    print("=" * 60)
    print("   WFGY 2.0 語義控制系統測試")
    print("=" * 60)

    controller = SemanticController()

    # 模擬對話序列
    test_cases = [
        ([1, 0, 0], [0.9, 0.1, 0]),  # 接近
        ([1, 0, 0], [0.7, 0.3, 0]),  # 稍有偏離
        ([1, 0, 0], [0.5, 0.5, 0]),  # 中等偏離
        ([1, 0, 0], [0.2, 0.8, 0]),  # 嚴重偏離
        ([1, 0, 0], [0.8, 0.2, 0]),  # 回歸
    ]

    print("\n模擬對話序列：")
    for i, (intended, generated) in enumerate(test_cases, 1):
        result = controller.process(intended, generated)
        print(f"\n--- Turn {i} ---")
        print(f"  Δs: {result['tension']['delta_s']:.3f}")
        print(f"  Zone: {result['tension']['zone']}")
        print(f"  Lambda: {result['lambda_state']}")
        print(f"  W_c: {result['coupler']['W_c']:.3f}")
        print(f"  Memory: {result['memory_action']}")
        print(f"  Bridge OK: {result['bridge_allowed']}")

    print("\n" + "=" * 60)
    print("   測試完成")
    print("=" * 60)
