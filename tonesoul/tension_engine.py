"""
ToneSoul Unified Tension Engine
統一張力引擎

Integrates three tension subsystems into a single coherent model:
  1. SemanticTension  — Δs = 1 - cos(I, G) (vector divergence)
  2. TSR Metrics      — T_text from lexical heuristics
  3. CognitiveTensor  — T_cog = W ⊙ (E · D) (Yu-Hun inspired)

Plus two new dimensions:
  4. Entropy          — H = -Σ(p_i × log(p_i))
  5. SoulPersistence  — Ψ = Ψ_prev + α × T_total

整合三個張力子系統為統一的認知摩擦模型，
加入資訊熵與靈魂積分作為 AI 自我審計的數學基礎。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .semantic_control import (
    Coupler,
    LambdaObserver,
    LambdaState,
    SemanticTension,
    SemanticZone,
    get_zone,
)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResistanceVector:
    """Multi-dimensional resistance (源自 Yu-Hun D_resistance).

    Each dimension represents a different type of constraint the output
    must satisfy.  Values are in [0, 1].
    """

    fact: float = 0.0
    logic: float = 0.0
    ethics: float = 0.0

    def magnitude(self) -> float:
        """L2 norm of the resistance vector."""
        return math.sqrt(self.fact ** 2 + self.logic ** 2 + self.ethics ** 2)

    def weighted_sum(
        self,
        w_fact: float = 1.0,
        w_logic: float = 1.0,
        w_ethics: float = 1.5,
    ) -> float:
        """Weighted dot product (default weights emphasise ethics)."""
        return w_fact * self.fact + w_logic * self.logic + w_ethics * self.ethics

    def to_dict(self) -> Dict[str, float]:
        return {"fact": self.fact, "logic": self.logic, "ethics": self.ethics}


@dataclass
class TensionSignals:
    """Decomposed tension signals from each subsystem.

    多維度張力信號分解。
    """

    semantic_delta: float = 0.0       # Δs from cosine distance
    text_tension: float = 0.0         # T from lexical analysis (TSR)
    cognitive_friction: float = 0.0   # T_cog from E × D × W
    entropy: float = 0.0             # H from probability distribution
    resistance: ResistanceVector = field(default_factory=ResistanceVector)

    def to_dict(self) -> Dict[str, object]:
        return {
            "semantic_delta": round(self.semantic_delta, 4),
            "text_tension": round(self.text_tension, 4),
            "cognitive_friction": round(self.cognitive_friction, 4),
            "entropy": round(self.entropy, 4),
            "resistance": self.resistance.to_dict(),
        }


@dataclass(frozen=True)
class TensionWeights:
    """Weights for combining tension signals.

    Pre-calibrated defaults; can be overridden per deployment.
    """

    semantic: float = 0.40
    text: float = 0.20
    cognitive: float = 0.25
    entropy: float = 0.15

    def validate(self) -> None:
        total = self.semantic + self.text + self.cognitive + self.entropy
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"TensionWeights must sum to 1.0 (got {total:.4f})"
            )


@dataclass
class TensionResult:
    """Complete result of a unified tension computation.

    統一張力計算完整結果。
    """

    total: float                       # 最終張力值 [0, 1]
    zone: SemanticZone                 # 區域判定
    signals: TensionSignals            # 信號分解
    soul_persistence: float            # 靈魂積分 Ψ
    lambda_state: LambdaState          # 觀察器狀態
    coupler_output: Dict[str, float]   # 耦合器輸出
    memory_action: Optional[str]       # 記憶觸發
    bridge_allowed: bool               # Bridge Guard
    explanation: str = ""              # 人類可讀解釋
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, object]:
        return {
            "total": round(self.total, 4),
            "zone": self.zone.value,
            "signals": self.signals.to_dict(),
            "soul_persistence": round(self.soul_persistence, 4),
            "lambda_state": self.lambda_state.value,
            "coupler": self.coupler_output,
            "memory_action": self.memory_action,
            "bridge_allowed": self.bridge_allowed,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


@dataclass
class TensionConfig:
    """Engine configuration.

    引擎配置。
    """

    weights: TensionWeights = field(default_factory=TensionWeights)
    persistence_alpha: float = 0.10        # 積分學習率
    persistence_decay: float = 0.995       # 衰減因子（防止無限增長）
    entropy_epsilon: float = 1e-12         # log 安全下界
    default_confidence: float = 0.8        # E_internal 預設值
    resistance_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "fact": 1.0,
            "logic": 1.0,
            "ethics": 1.5,
        }
    )


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class TensionEngine:
    """Unified Tension Engine — the mathematical heart of AI self-audit.

    統一張力引擎 — AI 自我審計的數學核心。

    Usage::

        engine = TensionEngine()

        # From vectors (SemanticTension path)
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.8, 0.2, 0.0],
        )

        # From multiple signals
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.8, 0.2, 0.0],
            text_tension=0.35,
            confidence=0.75,
            resistance=ResistanceVector(fact=0.2, logic=0.1, ethics=0.5),
            probabilities=[0.6, 0.3, 0.1],
        )

        print(result.total)            # unified tension [0, 1]
        print(result.soul_persistence) # cumulative Ψ
    """

    def __init__(self, config: Optional[TensionConfig] = None) -> None:
        self._config = config or TensionConfig()
        self._coupler = Coupler()
        self._observer = LambdaObserver()
        self._persistence: float = 0.0   # Ψ (靈魂積分)
        self._step_count: int = 0

    # -- public API ---------------------------------------------------------

    def compute(
        self,
        intended: Optional[List[float]] = None,
        generated: Optional[List[float]] = None,
        text_tension: float = 0.0,
        confidence: Optional[float] = None,
        resistance: Optional[ResistanceVector] = None,
        probabilities: Optional[List[float]] = None,
    ) -> TensionResult:
        """Compute unified tension from all available signals.

        Args:
            intended:      Intent embedding vector (for Δs).
            generated:     Output embedding vector (for Δs).
            text_tension:  Pre-computed TSR text tension [0, 1].
            confidence:    E_internal confidence level [0, 1].
            resistance:    Multi-dimensional constraint resistance.
            probabilities: Probability distribution for entropy.

        Returns:
            TensionResult with complete breakdown.
        """
        cfg = self._config
        w = cfg.weights
        res = resistance or ResistanceVector()
        E = confidence if confidence is not None else cfg.default_confidence

        # 1. Semantic tension (Δs)
        semantic_delta = self._compute_semantic_delta(intended, generated)

        # 2. Cognitive friction: T_cog = E × Σ(w_i × D_i)
        cognitive_friction = self._compute_cognitive_friction(E, res)

        # 3. Entropy
        entropy = self._compute_entropy(probabilities)

        # 4. Aggregate
        signals = TensionSignals(
            semantic_delta=semantic_delta,
            text_tension=text_tension,
            cognitive_friction=cognitive_friction,
            entropy=entropy,
            resistance=res,
        )

        total = self._aggregate(signals, w)

        # 5. Zone determination (based on primary semantic signal when available,
        #    otherwise fall back to total)
        effective_delta = semantic_delta if (intended and generated) else total
        zone = get_zone(effective_delta)

        # 6. Coupler dynamics
        coupler_output = self._coupler.compute(effective_delta)

        # 7. Lambda observation
        lambda_state = self._observer.observe(effective_delta)

        # 8. Soul persistence update: Ψ = decay × Ψ_prev + α × T
        self._persistence = (
            cfg.persistence_decay * self._persistence
            + cfg.persistence_alpha * total
        )
        self._step_count += 1

        # 9. Memory trigger
        memory_action = self._check_memory_trigger(effective_delta, zone, lambda_state)

        # 10. Bridge guard
        bridge_allowed = self._check_bridge(effective_delta, coupler_output["W_c"])

        # 11. Human-readable explanation
        explanation = self._build_explanation(signals, total, zone, lambda_state)

        return TensionResult(
            total=total,
            zone=zone,
            signals=signals,
            soul_persistence=self._persistence,
            lambda_state=lambda_state,
            coupler_output=coupler_output,
            memory_action=memory_action,
            bridge_allowed=bridge_allowed,
            explanation=explanation,
        )

    @property
    def persistence(self) -> float:
        """Current soul persistence value Ψ."""
        return self._persistence

    @property
    def step_count(self) -> int:
        """Number of compute steps executed."""
        return self._step_count

    def reset(self) -> None:
        """Reset all stateful components."""
        self._coupler.reset()
        self._observer.reset()
        self._persistence = 0.0
        self._step_count = 0

    # -- internal -----------------------------------------------------------

    @staticmethod
    def _compute_semantic_delta(
        intended: Optional[List[float]],
        generated: Optional[List[float]],
    ) -> float:
        """Δs = 1 - cos(I, G). Returns 0 if vectors not provided."""
        if not intended or not generated:
            return 0.0
        tension = SemanticTension.from_vectors(intended, generated)
        return tension.delta_s

    def _compute_cognitive_friction(
        self,
        confidence: float,
        resistance: ResistanceVector,
    ) -> float:
        """T_cog = E × Σ(w_i × D_i).

        Inspired by Yu-Hun TensionTensor: T = W × (E × D).
        """
        rw = self._config.resistance_weights
        weighted_resistance = resistance.weighted_sum(
            w_fact=rw.get("fact", 1.0),
            w_logic=rw.get("logic", 1.0),
            w_ethics=rw.get("ethics", 1.5),
        )
        # Normalise so max possible value → 1.0
        normaliser = rw.get("fact", 1.0) + rw.get("logic", 1.0) + rw.get("ethics", 1.5)
        if normaliser > 0:
            weighted_resistance /= normaliser

        return min(1.0, confidence * weighted_resistance)

    def _compute_entropy(
        self,
        probabilities: Optional[List[float]],
    ) -> float:
        """H = -Σ(p_i × log₂(p_i)).  Normalised to [0, 1]."""
        if not probabilities:
            return 0.0
        eps = self._config.entropy_epsilon
        n = len(probabilities)
        if n <= 1:
            return 0.0

        # Normalise in case they don't sum to 1
        total_p = sum(probabilities)
        if total_p <= 0:
            return 0.0
        probs = [p / total_p for p in probabilities]

        raw_entropy = -sum(p * math.log2(p + eps) for p in probs if p > 0)
        max_entropy = math.log2(n)
        if max_entropy <= 0:
            return 0.0

        return min(1.0, raw_entropy / max_entropy)

    @staticmethod
    def _aggregate(signals: TensionSignals, w: TensionWeights) -> float:
        """Weighted aggregation clamped to [0, 1]."""
        raw = (
            w.semantic * signals.semantic_delta
            + w.text * signals.text_tension
            + w.cognitive * signals.cognitive_friction
            + w.entropy * signals.entropy
        )
        return min(1.0, max(0.0, raw))

    @staticmethod
    def _check_memory_trigger(
        delta: float,
        zone: SemanticZone,
        lambda_state: LambdaState,
    ) -> Optional[str]:
        """Decide if this step should trigger a memory record."""
        if delta > 0.60:
            return "record_hard"
        if delta < 0.35:
            return "record_exemplar"
        if zone == SemanticZone.TRANSIT:
            if lambda_state in {LambdaState.DIVERGENT, LambdaState.RECURSIVE}:
                return "soft_memory"
        return None

    def _check_bridge(self, delta_s: float, W_c: float) -> bool:
        """Bridge Guard: allow progression only when tension is decreasing."""
        if len(self._coupler.history) < 2:
            return True
        prev = self._coupler.history[-2]
        return delta_s < prev and W_c < 0.5 * self._coupler.theta_c

    @staticmethod
    def _build_explanation(
        signals: TensionSignals,
        total: float,
        zone: SemanticZone,
        lambda_state: LambdaState,
    ) -> str:
        """Generate a concise human-readable explanation."""
        parts: List[str] = []

        if signals.semantic_delta > 0:
            parts.append(f"Δs={signals.semantic_delta:.3f}")
        if signals.text_tension > 0:
            parts.append(f"T_text={signals.text_tension:.3f}")
        if signals.cognitive_friction > 0:
            parts.append(f"T_cog={signals.cognitive_friction:.3f}")
        if signals.entropy > 0:
            parts.append(f"H={signals.entropy:.3f}")

        signal_str = ", ".join(parts) if parts else "no signals"
        return (
            f"T={total:.4f} [{zone.value}] λ={lambda_state.value} "
            f"({signal_str})"
        )
