"""
RFC-013: Dynamic Variance Compressor.

Replaces WFGY's static BBAM (exp(-γ·σ)) with an adaptive compression
engine whose strength varies by:
  - Work category  (γ_base from ConstraintProfile)
  - Prediction trend (NonlinearPredictor output)
  - Semantic zone   (safe → danger)
  - Lambda state    (convergent → chaotic)

The compressor outputs a ratio in [0.35, 1.0].
  1.0 = no compression (full variance preserved)
  0.35 = maximum compression (only 35 % variance survives)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .nonlinear_predictor import PredictionResult
from .semantic_control import LambdaState, SemanticZone
from .work_classifier import ConstraintProfile, WorkCategory, get_profile

# ── γ contribution tables ────────────────────────────────────────

_GAMMA_TREND = {
    "converging": 0.0,
    "stable": 0.0,
    "diverging": 0.2,
    "chaotic": 0.5,
}

_GAMMA_ZONE = {
    SemanticZone.SAFE: 0.0,
    SemanticZone.TRANSIT: 0.1,
    SemanticZone.RISK: 0.3,
    SemanticZone.DANGER: 0.5,
}

_GAMMA_LAMBDA = {
    LambdaState.CONVERGENT: 0.0,
    LambdaState.RECURSIVE: 0.1,
    LambdaState.DIVERGENT: 0.2,
    LambdaState.CHAOTIC: 0.4,
}


@dataclass
class CompressionResult:
    """Output of a single compression step."""

    compression_ratio: float
    """Effective compression ratio [0.35, 1.0]. Lower = stronger."""

    gamma_effective: float
    """Composite γ value that produced this compression."""

    gamma_breakdown: dict
    """Per-source γ contributions for explainability."""

    zone_override: Optional[str]
    """If compression was strong enough to suggest a zone override."""

    explanation: str
    """Human-readable compression rationale."""

    def to_dict(self) -> dict:
        return {
            "compression_ratio": round(self.compression_ratio, 4),
            "gamma_effective": round(self.gamma_effective, 4),
            "gamma_breakdown": {k: round(v, 4) for k, v in self.gamma_breakdown.items()},
            "zone_override": self.zone_override,
            "explanation": self.explanation,
        }


class DynamicVarianceCompressor:
    """
    Adaptive variance compression engine.

    Parameters
    ----------
    min_ratio : float
        Floor for compression ratio (never compress below this).
    max_ratio : float
        Ceiling for compression ratio.
    sigma_scale : float
        Scaling factor applied to the signal variance before
        computing exp(-γ·σ). Higher → more sensitive to variance.
    """

    def __init__(
        self,
        *,
        min_ratio: float = 0.35,
        max_ratio: float = 1.0,
        sigma_scale: float = 1.0,
    ) -> None:
        self._min = max(0.01, min(1.0, min_ratio))
        self._max = max(self._min, min(1.0, max_ratio))
        self._sigma_scale = max(0.1, sigma_scale)

    def compress(
        self,
        *,
        signal_variance: float,
        prediction: Optional[PredictionResult] = None,
        zone: SemanticZone = SemanticZone.SAFE,
        lambda_state: LambdaState = LambdaState.CONVERGENT,
        work_category: WorkCategory = WorkCategory.ENGINEERING,
    ) -> CompressionResult:
        """
        Compute adaptive compression.

        Parameters
        ----------
        signal_variance : float
            Variance (or std) of the tension signal ensemble.
            Typically computed as std(semantic_delta, text_tension,
            cognitive_friction, entropy).
        prediction : PredictionResult, optional
            Output of NonlinearPredictor.predict().
        zone : SemanticZone
            Current semantic zone.
        lambda_state : LambdaState
            Current lambda observer state.
        work_category : WorkCategory
            Active work category for constraint profile lookup.
        """
        profile = get_profile(work_category)
        trend = prediction.trend if prediction else "stable"

        # ── assemble γ_eff ───────────────────────────────────────
        gamma_base = profile.gamma_base
        gamma_trend = _GAMMA_TREND.get(trend, 0.0)
        gamma_zone = _GAMMA_ZONE.get(zone, 0.0)
        gamma_lambda = _GAMMA_LAMBDA.get(lambda_state, 0.0)

        gamma_eff = gamma_base + gamma_trend + gamma_zone + gamma_lambda

        breakdown = {
            "base": gamma_base,
            "trend": gamma_trend,
            "zone": gamma_zone,
            "lambda": gamma_lambda,
        }

        # ── compute compression ──────────────────────────────────
        sigma = max(0.0, signal_variance) * self._sigma_scale
        raw_ratio = math.exp(-gamma_eff * sigma) if sigma > 0 else 1.0
        ratio = max(self._min, min(self._max, raw_ratio))

        # ── zone override suggestion ────────────────────────────
        zone_override: Optional[str] = None
        if ratio < 0.5 and zone in (SemanticZone.SAFE, SemanticZone.TRANSIT):
            zone_override = "risk"

        # ── explanation ──────────────────────────────────────────
        explanation = self._build_explanation(
            profile,
            trend,
            zone,
            lambda_state,
            gamma_eff,
            ratio,
        )

        return CompressionResult(
            compression_ratio=ratio,
            gamma_effective=gamma_eff,
            gamma_breakdown=breakdown,
            zone_override=zone_override,
            explanation=explanation,
        )

    @staticmethod
    def _build_explanation(
        profile: ConstraintProfile,
        trend: str,
        zone: SemanticZone,
        lambda_state: LambdaState,
        gamma_eff: float,
        ratio: float,
    ) -> str:
        parts = [f"[{profile.label}]"]

        if ratio >= 0.9:
            parts.append("最小壓縮 — 信號穩定")
        elif ratio >= 0.7:
            parts.append("輕度壓縮")
        elif ratio >= 0.5:
            parts.append("中度壓縮")
        else:
            parts.append("強壓縮 — 方差過大")

        details = []
        if trend in ("diverging", "chaotic"):
            details.append(f"趨勢={trend}")
        if zone not in (SemanticZone.SAFE,):
            details.append(f"zone={zone.value}")
        if lambda_state not in (LambdaState.CONVERGENT,):
            details.append(f"λ={lambda_state.value}")

        if details:
            parts.append(f"({', '.join(details)})")

        parts.append(f"γ_eff={gamma_eff:.2f} → ratio={ratio:.3f}")
        return " ".join(parts)
