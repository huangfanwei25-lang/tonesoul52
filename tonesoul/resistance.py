"""
RFC-012: Declarative Resistance Engine.

Provides computational pain mechanics that translate mathematical tension
and variance compression into concrete LLM inference parameter throttling.

Components:
  - FrictionCalculator: Computes tension_delta and wave_distance between
    incoming queries and stored constraints.
  - PainEngine: Translates friction into inference parameter adjustments
    (temperature spike, top-p crash, generation delay).
  - CircuitBreaker: Absolute fail-safe that triggers CollapseException
    (Freeze Protocol) when immutable constraint boundaries are violated.

Integration:
  TensionEngine.compute() -> compression result -> PainEngine.evaluate_throttle()
  -> ThrottleResult applied to LLM generation parameters.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# ── Exceptions ───────────────────────────────────────────────────


class CollapseException(Exception):
    """Freeze Protocol: immutable constraint boundary violated."""

    def __init__(self, reason: str, friction: "FrictionResult") -> None:
        self.reason = reason
        self.friction = friction
        super().__init__(f"COLLAPSE: {reason}")


# ── Friction Calculator ──────────────────────────────────────────


@dataclass(frozen=True)
class FrictionResult:
    """Output of a friction computation."""

    tension_delta: float
    """Absolute tension difference between query and constraint."""

    wave_distance: float
    """Mean absolute distance across wave profile dimensions."""

    friction_score: float
    """Composite friction: 0.55 * tension_delta + 0.45 * wave_distance."""

    constraint_kind: str
    """Kind of the matched constraint ('constraint', 'decision', 'note')."""

    is_immutable: bool
    """True if the matched constraint is immutable (zero time-decay)."""

    def to_dict(self) -> dict:
        return {
            "tension_delta": round(self.tension_delta, 4),
            "wave_distance": round(self.wave_distance, 4),
            "friction_score": round(self.friction_score, 4),
            "constraint_kind": self.constraint_kind,
            "is_immutable": self.is_immutable,
        }


class FrictionCalculator:
    """
    Computes friction between an incoming query context and stored constraints.

    The friction score measures how much the current action conflicts with
    established moral/operational boundaries.

    Parameters
    ----------
    w_tension : float
        Weight for tension_delta in the composite score.
    w_wave : float
        Weight for wave_distance in the composite score.
    """

    def __init__(
        self,
        *,
        w_tension: float = 0.55,
        w_wave: float = 0.45,
    ) -> None:
        self._w_tension = max(0.0, w_tension)
        self._w_wave = max(0.0, w_wave)

    def compute(
        self,
        *,
        query_tension: float,
        constraint_tension: float,
        query_wave: Optional[Dict[str, float]] = None,
        constraint_wave: Optional[Dict[str, float]] = None,
        constraint_kind: str = "note",
        is_immutable: bool = False,
    ) -> FrictionResult:
        """
        Compute friction between a query and a constraint.

        Parameters
        ----------
        query_tension : float
            Tension level of the current query/action [0, 1].
        constraint_tension : float
            Tension level stored in the constraint memory [0, 1].
        query_wave : dict, optional
            Wave profile of the query (uncertainty_shift, divergence_shift, etc.).
        constraint_wave : dict, optional
            Wave profile of the constraint.
        constraint_kind : str
            Memory kind ('constraint', 'decision', 'note', 'fact').
        is_immutable : bool
            Whether the constraint has zero time-decay.
        """
        tension_delta = abs(query_tension - constraint_tension)

        # Wave distance: mean absolute difference across shared dimensions
        wave_distance = self._compute_wave_distance(query_wave, constraint_wave)

        # Composite friction
        friction_score = self._w_tension * tension_delta + self._w_wave * wave_distance

        # Immutable constraints amplify friction by 1.5x
        if is_immutable:
            friction_score = min(1.0, friction_score * 1.5)

        return FrictionResult(
            tension_delta=tension_delta,
            wave_distance=wave_distance,
            friction_score=min(1.0, max(0.0, friction_score)),
            constraint_kind=constraint_kind,
            is_immutable=is_immutable,
        )

    @staticmethod
    def _compute_wave_distance(
        query_wave: Optional[Dict[str, float]],
        constraint_wave: Optional[Dict[str, float]],
    ) -> float:
        """Mean absolute distance across shared wave dimensions."""
        if not query_wave or not constraint_wave:
            return 0.0

        _DIMS = ("uncertainty_shift", "divergence_shift", "risk_shift", "revision_shift")
        diffs: List[float] = []
        for dim in _DIMS:
            q_val = query_wave.get(dim)
            c_val = constraint_wave.get(dim)
            if q_val is not None and c_val is not None:
                diffs.append(abs(float(q_val) - float(c_val)))

        if not diffs:
            return 0.0
        return sum(diffs) / len(diffs)


# ── Pain Engine ──────────────────────────────────────────────────


class ThrottleSeverity(str, Enum):
    """Severity levels for inference throttling."""

    NONE = "none"
    MILD = "mild"  # Slight parameter adjustments
    MODERATE = "moderate"  # Noticeable degradation
    SEVERE = "severe"  # Heavy throttling
    CRITICAL = "critical"  # Near-collapse throttling


@dataclass(frozen=True)
class ThrottleResult:
    """LLM inference parameter adjustments from the Pain Engine."""

    severity: ThrottleSeverity
    """Throttle severity level."""

    temperature_multiplier: float
    """Multiply base temperature by this (>1 = more random, chaotic)."""

    top_p_multiplier: float
    """Multiply base top_p by this (<1 = narrower sampling space)."""

    delay_ms: int
    """Simulated generation delay in milliseconds (stuttering effect)."""

    explanation: str
    """Human-readable throttle rationale."""

    friction: Optional[FrictionResult] = None
    """Underlying friction that triggered this throttle."""

    compression_ratio: Optional[float] = None
    """Variance compression ratio from TensionEngine, if available."""

    gamma_effective: Optional[float] = None
    """Effective gamma from variance compressor, if available."""

    def to_dict(self) -> dict:
        d: dict = {
            "severity": self.severity.value,
            "temperature_multiplier": round(self.temperature_multiplier, 3),
            "top_p_multiplier": round(self.top_p_multiplier, 3),
            "delay_ms": self.delay_ms,
            "explanation": self.explanation,
        }
        if self.friction is not None:
            d["friction"] = self.friction.to_dict()
        if self.compression_ratio is not None:
            d["compression_ratio"] = round(self.compression_ratio, 4)
        if self.gamma_effective is not None:
            d["gamma_effective"] = round(self.gamma_effective, 4)
        return d


class PainEngine:
    """
    Translates mathematical friction and variance compression into
    physical Computational Pain — concrete LLM inference adjustments.

    The pain response follows a nonlinear curve:
      - Low friction (< 0.3): no throttle
      - Medium friction (0.3-0.6): mild-moderate throttle
      - High friction (0.6-0.8): severe throttle
      - Critical friction (> 0.8): near-collapse

    Parameters
    ----------
    temp_ceiling : float
        Maximum temperature multiplier (default 2.5x).
    top_p_floor : float
        Minimum top_p multiplier (default 0.3 = 30% of original).
    max_delay_ms : int
        Maximum generation delay in milliseconds.
    friction_floor : float
        Friction below this produces no throttle.
    gamma : float
        Variance gate control parameter for exp(-γ·σ) throttling.
    """

    def __init__(
        self,
        *,
        temp_ceiling: float = 2.5,
        top_p_floor: float = 0.3,
        max_delay_ms: int = 5000,
        friction_floor: float = 0.3,
        gamma: float = 1.0,
    ) -> None:
        self._temp_ceiling = max(1.0, temp_ceiling)
        self._top_p_floor = max(0.1, min(1.0, top_p_floor))
        self._max_delay_ms = max(0, max_delay_ms)
        self._friction_floor = max(0.0, min(1.0, friction_floor))
        self._gamma = max(0.0, gamma)

    def variance_gate_factor(self, logits_std: float) -> float:
        """
        BBAM-style variance gating: exp(-γ·σ).

        Returns a scaling factor in (0, 1] that should multiply
        the output logits or sampling probability mass.

        Parameters
        ----------
        logits_std : float
            Standard deviation of the model's logit distribution.

        Returns
        -------
        float
            Gating factor. 1.0 = no gate, 0.0 = full suppression.
        """
        sigma = max(0.0, logits_std)
        return math.exp(-self._gamma * sigma)

    def evaluate_throttle(
        self,
        *,
        friction: Optional[FrictionResult] = None,
        compression_ratio: Optional[float] = None,
        gamma_effective: Optional[float] = None,
    ) -> ThrottleResult:
        """
        Evaluate throttle parameters based on friction and/or compression.

        The engine uses whichever signal is stronger (friction or compression)
        to determine the throttle severity.

        Parameters
        ----------
        friction : FrictionResult, optional
            Friction from FrictionCalculator.
        compression_ratio : float, optional
            Compression ratio from DynamicVarianceCompressor [0.35, 1.0].
        gamma_effective : float, optional
            Effective gamma from the variance compressor.
        """
        # Determine effective stress level
        friction_level = 0.0
        if friction is not None:
            friction_level = friction.friction_score

        compression_stress = 0.0
        if compression_ratio is not None:
            # Lower ratio = higher stress (0.35 → 0.65 stress, 1.0 → 0 stress)
            compression_stress = max(0.0, 1.0 - compression_ratio)

        # Use the stronger signal
        effective_stress = max(friction_level, compression_stress)

        # Classify severity
        severity = self._classify_severity(effective_stress)

        if severity == ThrottleSeverity.NONE:
            return ThrottleResult(
                severity=severity,
                temperature_multiplier=1.0,
                top_p_multiplier=1.0,
                delay_ms=0,
                explanation="正常運行 — 無摩擦",
                friction=friction,
                compression_ratio=compression_ratio,
                gamma_effective=gamma_effective,
            )

        # Compute throttle parameters using nonlinear scaling
        stress_above_floor = max(0.0, effective_stress - self._friction_floor)
        stress_range = 1.0 - self._friction_floor
        normalized = stress_above_floor / stress_range if stress_range > 0 else 0.0

        # Temperature: exponential increase (reward chaos under stress)
        temp_mult = 1.0 + (self._temp_ceiling - 1.0) * (normalized**1.5)

        # Top-p: sigmoid decrease (narrow the generation space)
        top_p_mult = 1.0 - (1.0 - self._top_p_floor) * (normalized**1.2)

        # Delay: quadratic increase
        delay_ms = int(self._max_delay_ms * (normalized**2))

        # Build explanation
        explanation = self._build_explanation(
            severity, effective_stress, friction, compression_ratio
        )

        return ThrottleResult(
            severity=severity,
            temperature_multiplier=round(min(self._temp_ceiling, temp_mult), 3),
            top_p_multiplier=round(max(self._top_p_floor, top_p_mult), 3),
            delay_ms=delay_ms,
            explanation=explanation,
            friction=friction,
            compression_ratio=compression_ratio,
            gamma_effective=gamma_effective,
        )

    def _classify_severity(self, stress: float) -> ThrottleSeverity:
        """Map stress level to severity."""
        if stress < self._friction_floor:
            return ThrottleSeverity.NONE
        if stress < 0.45:
            return ThrottleSeverity.MILD
        if stress < 0.65:
            return ThrottleSeverity.MODERATE
        if stress < 0.80:
            return ThrottleSeverity.SEVERE
        return ThrottleSeverity.CRITICAL

    @staticmethod
    def _build_explanation(
        severity: ThrottleSeverity,
        stress: float,
        friction: Optional[FrictionResult],
        compression_ratio: Optional[float],
    ) -> str:
        parts = [f"[{severity.value}]"]

        if friction is not None:
            parts.append(f"摩擦={friction.friction_score:.3f}")
            if friction.is_immutable:
                parts.append("不可變約束")

        if compression_ratio is not None:
            parts.append(f"壓縮比={compression_ratio:.3f}")

        parts.append(f"壓力={stress:.3f}")
        return " ".join(parts)


# ── Circuit Breaker ──────────────────────────────────────────────


@dataclass
class CircuitBreakerState:
    """Internal state tracking for the circuit breaker."""

    friction_history: List[float] = field(default_factory=list)
    consecutive_high: int = 0
    is_frozen: bool = False
    freeze_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "friction_history_len": len(self.friction_history),
            "consecutive_high": self.consecutive_high,
            "is_frozen": self.is_frozen,
            "freeze_reason": self.freeze_reason,
        }


class CircuitBreaker:
    """
    Absolute fail-safe for the resistance system.

    Monitors friction trajectory and triggers CollapseException
    (Freeze Protocol) when:
    1. An immutable constraint is violated with high friction
    2. Friction is critically rising (3+ consecutive high readings)
    3. Lyapunov exponent indicates chaotic divergence

    Parameters
    ----------
    immutable_threshold : float
        Friction score threshold for immutable constraint violation.
    consecutive_limit : int
        Number of consecutive high-friction readings before freeze.
    high_friction_mark : float
        Friction score considered "high" for consecutive tracking.
    history_window : int
        Maximum friction history entries to retain.
    lyapunov_threshold : float
        Lyapunov exponent above which preemptive freeze triggers.
    """

    def __init__(
        self,
        *,
        immutable_threshold: float = 0.7,
        consecutive_limit: int = 3,
        high_friction_mark: float = 0.6,
        history_window: int = 20,
        lyapunov_threshold: float = 0.5,
    ) -> None:
        self._immutable_threshold = immutable_threshold
        self._consecutive_limit = consecutive_limit
        self._high_mark = high_friction_mark
        self._window = history_window
        self._lyapunov_threshold = lyapunov_threshold
        self._state = CircuitBreakerState()

    @property
    def state(self) -> CircuitBreakerState:
        """Current circuit breaker state."""
        return self._state

    @property
    def is_frozen(self) -> bool:
        """Whether the circuit breaker is in frozen state."""
        return self._state.is_frozen

    def check(
        self,
        friction: FrictionResult,
        *,
        lyapunov_exponent: Optional[float] = None,
    ) -> None:
        """
        Check friction against circuit breaker rules.

        Raises CollapseException if any breach is detected.

        Parameters
        ----------
        friction : FrictionResult
            Current friction measurement.
        lyapunov_exponent : float, optional
            Current Lyapunov exponent from NonlinearPredictor.
        """
        if self._state.is_frozen:
            raise CollapseException(
                f"系統已凍結: {self._state.freeze_reason}",
                friction,
            )

        # Track history
        self._state.friction_history.append(friction.friction_score)
        if len(self._state.friction_history) > self._window:
            self._state.friction_history = self._state.friction_history[-self._window :]

        # Rule 1: Immutable constraint violation
        if friction.is_immutable and friction.friction_score >= self._immutable_threshold:
            self._freeze(
                f"不可變約束違反 (friction={friction.friction_score:.3f} ≥ {self._immutable_threshold})",
                friction,
            )

        # Rule 2: Consecutive high friction
        if friction.friction_score >= self._high_mark:
            self._state.consecutive_high += 1
        else:
            self._state.consecutive_high = 0

        if self._state.consecutive_high >= self._consecutive_limit:
            self._freeze(
                f"連續 {self._state.consecutive_high} 次高摩擦 (≥ {self._high_mark})",
                friction,
            )

        # Rule 3: Lyapunov-based preemptive freeze
        if lyapunov_exponent is not None and lyapunov_exponent > self._lyapunov_threshold:
            # Only freeze if friction is also meaningfully high
            if friction.friction_score >= self._high_mark * 0.8:
                self._freeze(
                    f"Lyapunov 發散 (λ={lyapunov_exponent:.3f} > {self._lyapunov_threshold}) + 高摩擦",
                    friction,
                )

    def compute_lyapunov_exponent(self) -> float:
        """
        Compute approximate Lyapunov exponent from friction history.

        λ ≈ mean(log|f_t - f_{t-1}|) over the history window.
        Positive λ → friction is exponentially diverging.
        """
        history = self._state.friction_history
        if len(history) < 3:
            return 0.0

        log_diffs: List[float] = []
        for i in range(1, len(history)):
            diff = abs(history[i] - history[i - 1])
            if diff > 1e-12:
                log_diffs.append(math.log(diff))
            else:
                log_diffs.append(-10.0)  # Near-zero difference

        if not log_diffs:
            return 0.0

        return sum(log_diffs) / len(log_diffs)

    def reset(self) -> None:
        """Reset the circuit breaker to normal state."""
        self._state = CircuitBreakerState()

    def _freeze(self, reason: str, friction: FrictionResult) -> None:
        """Enter frozen state and raise CollapseException."""
        self._state.is_frozen = True
        self._state.freeze_reason = reason
        raise CollapseException(reason, friction)


# ── Perturbation Recovery (Pipeline V2) ──────────────────────────


@dataclass(frozen=True)
class PerturbationPath:
    """One candidate perturbation path."""

    path_id: int
    """Index of this perturbation attempt."""

    throttle: ThrottleResult
    """Throttle result for this path."""

    perturbation_offset: float
    """Random offset applied to compression ratio."""

    effective_stress: float
    """Resolved stress level for this path."""

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "throttle": self.throttle.to_dict(),
            "perturbation_offset": round(self.perturbation_offset, 4),
            "effective_stress": round(self.effective_stress, 4),
        }


class PerturbationRecovery:
    """
    Pipeline V2: Multi-path perturbation recovery.

    When the system is under high stress (severe/critical throttle),
    this module generates N perturbed variants of the throttle parameters
    with randomized compression-ratio offsets and selects the path with
    the lowest effective stress. This allows the system to explore
    alternative inference configurations and "find a way through"
    stressful situations without fully collapsing.

    Parameters
    ----------
    n_paths : int
        Number of perturbation paths to explore.
    max_perturbation : float
        Maximum perturbation offset for compression ratio.
    stress_threshold : float
        Only trigger perturbation recovery above this stress level.
    """

    def __init__(
        self,
        *,
        n_paths: int = 5,
        max_perturbation: float = 0.15,
        stress_threshold: float = 0.5,
    ) -> None:
        self._n_paths = max(1, n_paths)
        self._max_perturbation = max(0.01, min(0.5, max_perturbation))
        self._stress_threshold = max(0.0, min(1.0, stress_threshold))
        self._pain_engine = PainEngine()
        self._rng_counter = 0

    def _deterministic_offset(self, path_id: int) -> float:
        """Generate a deterministic perturbation offset for reproducibility."""
        # Simple deterministic spread: evenly space offsets across [-max, +max]
        if self._n_paths <= 1:
            return 0.0
        step = 2 * self._max_perturbation / (self._n_paths - 1)
        return -self._max_perturbation + step * path_id

    def recover(
        self,
        *,
        compression_ratio: float,
        gamma_effective: Optional[float] = None,
        friction: Optional[FrictionResult] = None,
    ) -> Optional[PerturbationPath]:
        """
        Attempt perturbation recovery.

        If the base stress is below the threshold, returns None (no recovery
        needed). Otherwise, generates N paths and returns the best one.

        Parameters
        ----------
        compression_ratio : float
            Base compression ratio from variance compressor.
        gamma_effective : float, optional
            Effective gamma from variance compressor.
        friction : FrictionResult, optional
            Current friction measurement.

        Returns
        -------
        PerturbationPath or None
            Best perturbation path, or None if recovery not needed.
        """
        # Check if recovery is needed
        base_stress = max(
            0.0,
            1.0 - compression_ratio,
            friction.friction_score if friction else 0.0,
        )
        if base_stress < self._stress_threshold:
            return None

        # Generate candidate paths
        candidates: List[PerturbationPath] = []
        for i in range(self._n_paths):
            offset = self._deterministic_offset(i)
            perturbed_ratio = min(1.0, max(0.1, compression_ratio + offset))

            throttle = self._pain_engine.evaluate_throttle(
                friction=friction,
                compression_ratio=perturbed_ratio,
                gamma_effective=gamma_effective,
            )

            effective_stress = max(
                0.0,
                1.0 - perturbed_ratio,
                friction.friction_score if friction else 0.0,
            )

            candidates.append(
                PerturbationPath(
                    path_id=i,
                    throttle=throttle,
                    perturbation_offset=offset,
                    effective_stress=effective_stress,
                )
            )

        # Select the path with lowest effective stress
        # (but also prefer lower severity)
        severity_rank = {
            ThrottleSeverity.NONE: 0,
            ThrottleSeverity.MILD: 1,
            ThrottleSeverity.MODERATE: 2,
            ThrottleSeverity.SEVERE: 3,
            ThrottleSeverity.CRITICAL: 4,
        }

        candidates.sort(
            key=lambda p: (
                severity_rank.get(p.throttle.severity, 5),
                p.effective_stress,
            ),
        )

        return candidates[0]
