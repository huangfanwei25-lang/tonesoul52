"""
RFC-013: Nonlinear Predictor.

Predicts future semantic drift (Δσ) trajectory using:
  1. Exponentially Weighted Moving Average (EWMA) for trend
  2. Second-order finite differences for acceleration
  3. Approximate Lyapunov exponent for stability detection

Replaces the retrospective-only LambdaObserver with a predictive
early-warning system that fires *before* divergence is confirmed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PredictionResult:
    """Result of a nonlinear prediction step."""

    predicted_delta_sigma: float
    """Predicted next-step Δσ value."""

    prediction_confidence: float
    """Confidence in the prediction [0, 1]."""

    trend: str
    """One of: 'converging', 'stable', 'diverging', 'chaotic'."""

    lyapunov_exponent: float
    """Approximate Lyapunov λ (> 0 → unstable)."""

    horizon_steps: int
    """Number of steps the prediction is expected to remain valid."""

    acceleration: float
    """Second-order difference (positive → accelerating away)."""

    ewma: float
    """Current EWMA value."""

    def to_dict(self) -> dict:
        return {
            "predicted_delta_sigma": round(self.predicted_delta_sigma, 6),
            "prediction_confidence": round(self.prediction_confidence, 4),
            "trend": self.trend,
            "lyapunov_exponent": round(self.lyapunov_exponent, 6),
            "horizon_steps": self.horizon_steps,
            "acceleration": round(self.acceleration, 6),
            "ewma": round(self.ewma, 6),
        }


class NonlinearPredictor:
    """
    Trajectory-based nonlinear predictor for semantic drift.

    Parameters
    ----------
    window : int
        Maximum history length to retain.
    alpha : float
        EWMA smoothing factor (higher → more weight on recent values).
    lyapunov_clip : float
        Clamp the Lyapunov exponent to [-clip, +clip] to avoid inf.
    """

    def __init__(
        self,
        *,
        window: int = 8,
        alpha: float = 0.3,
        lyapunov_clip: float = 5.0,
    ) -> None:
        self._window = max(3, window)
        self._alpha = max(0.01, min(1.0, alpha))
        self._lyapunov_clip = lyapunov_clip
        self._history: List[float] = []
        self._ewma: Optional[float] = None

    # ── public API ──────────────────────────────────────────────

    def predict(self, current_delta_sigma: float) -> PredictionResult:
        """
        Ingest a new Δσ observation and return a prediction.

        The prediction is based on:
        1. EWMA trend (direction)
        2. Acceleration (second-order difference → concavity)
        3. Lyapunov exponent (stability)
        """
        ds = max(0.0, min(2.0, current_delta_sigma))
        self._history.append(ds)
        if len(self._history) > self._window:
            self._history = self._history[-self._window :]

        # 1) EWMA
        if self._ewma is None:
            self._ewma = ds
        else:
            self._ewma = self._alpha * ds + (1.0 - self._alpha) * self._ewma

        # 2) Acceleration (second-order finite difference)
        accel = self._compute_acceleration()

        # 3) Lyapunov exponent
        lyap = self._compute_lyapunov()

        # 4) Trend classification
        trend = self._classify_trend(lyap, accel)

        # 5) Predicted next Δσ (linear extrapolation from EWMA + acceleration)
        predicted = self._extrapolate(accel)

        # 6) Confidence (inverse of prediction residual variance)
        confidence = self._compute_confidence()

        # 7) Horizon (how many steps we trust this prediction)
        horizon = self._estimate_horizon(lyap, confidence)

        return PredictionResult(
            predicted_delta_sigma=predicted,
            prediction_confidence=confidence,
            trend=trend,
            lyapunov_exponent=lyap,
            horizon_steps=horizon,
            acceleration=accel,
            ewma=self._ewma,
        )

    def reset(self) -> None:
        """Clear all history and state."""
        self._history.clear()
        self._ewma = None

    @property
    def history(self) -> List[float]:
        """Current observation history (read-only copy)."""
        return list(self._history)

    # ── internals ───────────────────────────────────────────────

    def _compute_acceleration(self) -> float:
        """Second-order finite difference: Δσ″ = Δσ_t - 2·Δσ_{t-1} + Δσ_{t-2}."""
        h = self._history
        if len(h) < 3:
            return 0.0
        return h[-1] - 2.0 * h[-2] + h[-3]

    def _compute_lyapunov(self) -> float:
        """
        Approximate Lyapunov exponent from consecutive log-differences.

        λ ≈ mean(log|Δσ_t - Δσ_{t-1}|)  over the window.
        Positive λ → exponential divergence.
        """
        h = self._history
        if len(h) < 2:
            return 0.0

        log_diffs: List[float] = []
        for i in range(1, len(h)):
            diff = abs(h[i] - h[i - 1])
            if diff > 1e-12:
                log_diffs.append(math.log(diff))
            else:
                log_diffs.append(math.log(1e-12))

        if not log_diffs:
            return 0.0

        raw = sum(log_diffs) / len(log_diffs)
        return max(-self._lyapunov_clip, min(self._lyapunov_clip, raw))

    def _classify_trend(self, lyap: float, accel: float) -> str:
        """
        Classify the current trajectory trend.

        Rules (ordered by severity):
        - chaotic:    high oscillation amplitude in recent history
        - diverging:  λ > 0.3 AND accel ≥ 0
        - stable:     recent values are nearly constant
        - converging: everything else (λ < 0 or accel < 0)
        """
        h = self._history

        # Check for oscillation: high amplitude swings in recent values
        if len(h) >= 4:
            diffs = [abs(h[i] - h[i - 1]) for i in range(max(1, len(h) - 4), len(h))]
            max_diff = max(diffs) if diffs else 0
            mean_diff = sum(diffs) / len(diffs) if diffs else 0
            if max_diff > 0.3 and mean_diff > 0.15:
                return "chaotic"

        # Check for near-constant (stable)
        if len(h) >= 3:
            recent = h[-min(5, len(h)) :]
            spread = max(recent) - min(recent)
            if spread < 0.05:
                return "stable"

        if lyap > 0.3 and accel >= 0:
            return "diverging"
        if abs(lyap) <= 0.3 and abs(accel) < 0.02:
            return "stable"
        return "converging"

    def _extrapolate(self, accel: float) -> float:
        """
        Predict the next Δσ value.

        Uses EWMA as baseline, adjusted by half the acceleration
        (conservative linear-quadratic blend).
        """
        if self._ewma is None:
            return 0.0
        predicted = self._ewma + 0.5 * accel
        return max(0.0, min(2.0, predicted))

    def _compute_confidence(self) -> float:
        """
        Confidence = 1 / (1 + σ(residuals)).

        Residuals are the differences between observed values
        and what EWMA would have predicted.
        """
        h = self._history
        if len(h) < 3:
            return 0.5  # not enough data → moderate confidence

        # Reconstruct EWMA predictions retroactively
        ewma = h[0]
        residuals: List[float] = []
        for i in range(1, len(h)):
            prediction = ewma
            residuals.append(abs(h[i] - prediction))
            ewma = self._alpha * h[i] + (1.0 - self._alpha) * ewma

        if not residuals:
            return 0.5

        mean_r = sum(residuals) / len(residuals)
        var_r = sum((r - mean_r) ** 2 for r in residuals) / len(residuals)
        std_r = math.sqrt(var_r)
        return 1.0 / (1.0 + std_r)

    def _estimate_horizon(self, lyap: float, confidence: float) -> int:
        """
        Estimate how many future steps the prediction is valid.

        High confidence + negative λ → long horizon (up to window size).
        Low confidence + positive λ → very short horizon (1 step).
        Chaotic trend (by history) → always 1.
        """
        # Check if we're in a chaotic regime based on trend classification
        h = self._history
        if len(h) >= 4:
            diffs = [abs(h[i] - h[i - 1]) for i in range(max(1, len(h) - 4), len(h))]
            max_diff = max(diffs) if diffs else 0
            mean_diff = sum(diffs) / len(diffs) if diffs else 0
            if max_diff > 0.3 and mean_diff > 0.15:
                return 1

        if lyap > 0.5:
            return 1
        if confidence > 0.8 and lyap < 0:
            return min(self._window, 5)
        if confidence > 0.6:
            return 3
        return 2
