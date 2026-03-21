"""
ToneSoul Unified Tension Engine.

Integrates semantic, textual, cognitive, and entropy signals into one
stateful tension result used by dispatch and gate decisions.
"""

from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .nonlinear_predictor import NonlinearPredictor, PredictionResult
from .resistance import PainEngine, ThrottleResult
from .semantic_control import (
    Coupler,
    LambdaObserver,
    LambdaState,
    SemanticTension,
    SemanticZone,
    get_zone,
)
from .variance_compressor import CompressionResult, DynamicVarianceCompressor
from .work_classifier import WorkCategory


@dataclass(frozen=True)
class ResistanceVector:
    """Multi-dimensional resistance vector in [0, 1]."""

    fact: float = 0.0
    logic: float = 0.0
    ethics: float = 0.0

    def magnitude(self) -> float:
        """L2 norm of the resistance vector."""
        return math.sqrt(self.fact**2 + self.logic**2 + self.ethics**2)

    def weighted_sum(
        self,
        w_fact: float = 1.0,
        w_logic: float = 1.0,
        w_ethics: float = 1.5,
    ) -> float:
        """Weighted dot product (default emphasises ethics)."""
        return w_fact * self.fact + w_logic * self.logic + w_ethics * self.ethics

    def to_dict(self) -> Dict[str, float]:
        return {"fact": self.fact, "logic": self.logic, "ethics": self.ethics}


@dataclass
class TensionSignals:
    """Decomposed tension signals from each subsystem."""

    semantic_delta: float = 0.0
    text_tension: float = 0.0
    cognitive_friction: float = 0.0
    entropy: float = 0.0
    delta_s_ecs: float = 0.0
    t_ecs: float = 0.0
    resistance: ResistanceVector = field(default_factory=ResistanceVector)

    @property
    def delta_sigma(self) -> float:
        """Canonical project-wide alias for semantic drift."""
        return self.semantic_delta

    def to_dict(self) -> Dict[str, object]:
        return {
            "semantic_delta": round(self.semantic_delta, 4),
            "delta_sigma": round(self.delta_sigma, 4),
            "text_tension": round(self.text_tension, 4),
            "cognitive_friction": round(self.cognitive_friction, 4),
            "entropy": round(self.entropy, 4),
            "delta_s_ecs": round(self.delta_s_ecs, 4),
            "t_ecs": round(self.t_ecs, 4),
            "resistance": self.resistance.to_dict(),
        }


@dataclass(frozen=True)
class TensionWeights:
    """Weights for the legacy unified `total` signal."""

    semantic: float = 0.40
    text: float = 0.20
    cognitive: float = 0.25
    entropy: float = 0.15

    def validate(self) -> None:
        total = self.semantic + self.text + self.cognitive + self.entropy
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"TensionWeights must sum to 1.0 (got {total:.4f})")


@dataclass
class TensionResult:
    """Complete result of a unified tension computation."""

    total: float
    zone: SemanticZone
    signals: TensionSignals
    soul_persistence: float
    lambda_state: LambdaState
    coupler_output: Dict[str, float]
    memory_action: Optional[str]
    bridge_allowed: bool
    explanation: str = ""
    timestamp: str = ""
    # RFC-013 extensions
    prediction: Optional[PredictionResult] = None
    compression: Optional[CompressionResult] = None
    work_category: Optional[str] = None
    # RFC-012 resistance
    throttle: Optional[ThrottleResult] = None

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = {
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
        if self.prediction is not None:
            d["prediction"] = self.prediction.to_dict()
        if self.compression is not None:
            d["compression"] = self.compression.to_dict()
        if self.work_category is not None:
            d["work_category"] = self.work_category
        if self.throttle is not None:
            d["throttle"] = self.throttle.to_dict()
        return d


@dataclass
class TensionConfig:
    """Engine configuration."""

    weights: TensionWeights = field(default_factory=TensionWeights)
    persistence_alpha: float = 0.10
    persistence_decay: float = 0.995
    entropy_epsilon: float = 1e-12
    ecs_eps_obs: float = 0.10
    default_confidence: float = 0.8
    ecs_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "semantic": 0.45,
            "text": 0.30,
            "cognitive": 0.25,
        }
    )
    resistance_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "fact": 1.0,
            "logic": 1.0,
            "ethics": 1.5,
        }
    )


class TensionEngine:
    """Unified Tension Engine for ToneSoul runtime decisions."""

    def __init__(
        self,
        config: Optional[TensionConfig] = None,
        *,
        work_category: Optional[WorkCategory] = None,
    ) -> None:
        self._config = config or TensionConfig()
        self._coupler = Coupler()
        self._observer = LambdaObserver()
        self._persistence: float = 0.0
        self._step_count: int = 0
        # RFC-013 extensions
        self._predictor = NonlinearPredictor()
        self._compressor = DynamicVarianceCompressor()
        self._work_category = work_category or WorkCategory.ENGINEERING
        # RFC-012 resistance
        self._pain_engine = PainEngine()

    def compute(
        self,
        intended: Optional[List[float]] = None,
        generated: Optional[List[float]] = None,
        text_tension: float = 0.0,
        confidence: Optional[float] = None,
        resistance: Optional[ResistanceVector] = None,
        probabilities: Optional[List[float]] = None,
    ) -> TensionResult:
        """Compute unified tension from all available signals."""
        cfg = self._config
        w = cfg.weights
        res = resistance or ResistanceVector()
        conf = confidence if confidence is not None else cfg.default_confidence

        # 1) Semantic drift
        semantic_delta = self._compute_semantic_delta(intended, generated)

        # 2) Cognitive friction
        cognitive_friction = self._compute_cognitive_friction(conf, res)

        # 3) Entropy
        entropy = self._compute_entropy(probabilities)

        # 4) WFGY refinement: DeltaS_ECS and T_ECS
        delta_s_ecs = self._compute_delta_s_ecs(
            semantic_delta=semantic_delta,
            text_tension=text_tension,
            cognitive_friction=cognitive_friction,
        )
        t_ecs = self._compute_t_ecs(delta_s_ecs=delta_s_ecs, entropy=entropy)

        # 4.5) RFC-013: Nonlinear prediction
        effective_delta = semantic_delta if (intended and generated) else t_ecs
        prediction = self._predictor.predict(effective_delta)

        # 5) Legacy aggregate signal (kept for backward compatibility)
        signals = TensionSignals(
            semantic_delta=semantic_delta,
            text_tension=text_tension,
            cognitive_friction=cognitive_friction,
            entropy=entropy,
            delta_s_ecs=delta_s_ecs,
            t_ecs=t_ecs,
            resistance=res,
        )
        total = self._aggregate(signals, w)

        # 6) Zone source
        zone = get_zone(effective_delta)

        # 6.5) RFC-013: Dynamic variance compression
        signal_std = self._compute_signal_variance(signals)
        lambda_state_pre = self._observer.observe(effective_delta)
        compression = self._compressor.compress(
            signal_variance=signal_std,
            prediction=prediction,
            zone=zone,
            lambda_state=lambda_state_pre,
            work_category=self._work_category,
        )

        # 7) Coupler
        coupler_output = self._coupler.compute(effective_delta)

        # 8) Lambda observer (already computed at 6.5)
        lambda_state = lambda_state_pre

        # 9) Soul persistence
        self._persistence = (
            cfg.persistence_decay * self._persistence + cfg.persistence_alpha * total
        )
        self._step_count += 1

        # 10) Memory trigger
        memory_action = self._check_memory_trigger(
            effective_delta,
            zone,
            lambda_state,
            prediction=prediction,
            compression=compression,
        )

        # 11) Bridge guard
        bridge_allowed = self._check_bridge(effective_delta, coupler_output["W_c"])

        # 12) Explanation
        explanation = self._build_explanation(signals, total, zone, lambda_state)

        # 12.5) RFC-012: Evaluate pain throttle
        throttle = self._pain_engine.evaluate_throttle(
            compression_ratio=compression.compression_ratio,
            gamma_effective=compression.gamma_effective,
        )

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
            prediction=prediction,
            compression=compression,
            work_category=self._work_category.value,
            throttle=throttle,
        )

    @property
    def persistence(self) -> float:
        """Current soul persistence value."""
        return self._persistence

    @property
    def step_count(self) -> int:
        """Number of compute steps executed."""
        return self._step_count

    def reset(self) -> None:
        """Reset all stateful components."""
        self._coupler.reset()
        self._observer.reset()
        self._predictor.reset()
        self._persistence = 0.0
        self._step_count = 0

    def save_persistence(self, path: "Optional[pathlib.Path]" = None) -> None:
        """Persist the current Ψ value to disk for cross-session continuity."""
        from tonesoul.soul_persistence import save_psi

        save_psi(self._persistence, self._step_count, path)

    def load_persistence(self, path: "Optional[pathlib.Path]" = None) -> None:
        """Restore the Ψ value from a previous session."""
        from tonesoul.soul_persistence import load_psi

        snapshot = load_psi(path)
        self._persistence = snapshot.psi
        self._step_count = snapshot.step_count

    @property
    def work_category(self) -> WorkCategory:
        """Current work category."""
        return self._work_category

    @work_category.setter
    def work_category(self, value: WorkCategory) -> None:
        """Switch work category at runtime."""
        self._work_category = value

    @staticmethod
    def _compute_signal_variance(signals: TensionSignals) -> float:
        """Compute std of the main signal components for variance compression."""
        vals = [
            signals.semantic_delta,
            signals.text_tension,
            signals.cognitive_friction,
            signals.entropy,
        ]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        return math.sqrt(var)

    @staticmethod
    def _compute_semantic_delta(
        intended: Optional[List[float]],
        generated: Optional[List[float]],
    ) -> float:
        """DeltaSigma = 1 - cos(I, G)."""
        if not intended or not generated:
            return 0.0
        tension = SemanticTension.from_vectors(intended, generated)
        return tension.delta_s

    def _compute_cognitive_friction(
        self,
        confidence: float,
        resistance: ResistanceVector,
    ) -> float:
        """Cognitive friction from confidence * weighted resistance."""
        rw = self._config.resistance_weights
        weighted_resistance = resistance.weighted_sum(
            w_fact=rw.get("fact", 1.0),
            w_logic=rw.get("logic", 1.0),
            w_ethics=rw.get("ethics", 1.5),
        )
        normaliser = rw.get("fact", 1.0) + rw.get("logic", 1.0) + rw.get("ethics", 1.5)
        if normaliser > 0:
            weighted_resistance /= normaliser

        return min(1.0, confidence * weighted_resistance)

    def _compute_entropy(self, probabilities: Optional[List[float]]) -> float:
        """Normalized Shannon entropy in [0, 1]."""
        if not probabilities:
            return 0.0
        eps = self._config.entropy_epsilon
        n = len(probabilities)
        if n <= 1:
            return 0.0

        total_p = sum(probabilities)
        if total_p <= 0:
            return 0.0
        probs = [p / total_p for p in probabilities]

        raw_entropy = -sum(p * math.log2(p + eps) for p in probs if p > 0)
        max_entropy = math.log2(n)
        if max_entropy <= 0:
            return 0.0

        normalized_entropy = raw_entropy / max_entropy
        return min(1.0, max(0.0, normalized_entropy))

    def _compute_delta_s_ecs(
        self,
        semantic_delta: float,
        text_tension: float,
        cognitive_friction: float,
    ) -> float:
        """WFGY-style combined mismatch: DeltaS_ECS."""
        w = self._config.ecs_weights
        weighted = (
            float(w.get("semantic", 0.45)) * semantic_delta
            + float(w.get("text", 0.30)) * text_tension
            + float(w.get("cognitive", 0.25)) * cognitive_friction
        )
        return min(1.0, max(0.0, weighted))

    def _compute_t_ecs(self, delta_s_ecs: float, entropy: float) -> float:
        """WFGY-style ECS tension functional."""
        obs_constraint = max(self._config.ecs_eps_obs, 1.0 - entropy)
        t_ecs = delta_s_ecs / obs_constraint
        return min(1.0, max(0.0, t_ecs))

    @staticmethod
    def _aggregate(signals: TensionSignals, w: TensionWeights) -> float:
        """Legacy weighted aggregation, clamped to [0, 1]."""
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
        *,
        prediction: Optional[PredictionResult] = None,
        compression: Optional[CompressionResult] = None,
    ) -> Optional[str]:
        """Decide if this step should trigger a memory record."""
        if delta > 0.60:
            return "record_hard"
        if delta < 0.35:
            return "record_exemplar"
        if zone == SemanticZone.TRANSIT and lambda_state in {
            LambdaState.DIVERGENT,
            LambdaState.RECURSIVE,
        }:
            return "soft_memory"
        if prediction is not None:
            if prediction.trend == "chaotic":
                return "record_hard_predicted"
            if prediction.trend == "diverging" and prediction.prediction_confidence > 0.7:
                return "record_predictive_warning"
        if compression is not None and compression.compression_ratio < 0.5:
            return "record_high_compression"
        return None

    def _check_bridge(self, delta_s: float, w_c: float) -> bool:
        """Bridge Guard: allow progression only when tension is decreasing."""
        if len(self._coupler.history) < 2:
            return True
        prev = self._coupler.history[-2]
        return delta_s < prev and w_c < 0.5 * self._coupler.theta_c

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
            parts.append(f"delta_s={signals.semantic_delta:.3f}")
        if signals.text_tension > 0:
            parts.append(f"T_text={signals.text_tension:.3f}")
        if signals.cognitive_friction > 0:
            parts.append(f"T_cog={signals.cognitive_friction:.3f}")
        if signals.entropy > 0:
            parts.append(f"H={signals.entropy:.3f}")
        if signals.t_ecs > 0:
            parts.append(f"T_ECS={signals.t_ecs:.3f}")

        signal_str = ", ".join(parts) if parts else "no signals"
        return f"T={total:.4f} [{zone.value}] lambda={lambda_state.value} ({signal_str})"
