"""
Resonance classifier - distinguishes genuine resonance from sycophantic flow.

Formula:
  Resonance = (delta_before > 0) and (delta_after < delta_before)
              and (prediction_confidence >= threshold)

Categories:
  - flow: delta ~ 0 throughout (no tension, canned response)
  - resonance: tension appears -> converges -> novel output
  - deep_resonance: prediction fails but still converges (unprecedented alignment)
  - divergence: tension appears -> does NOT converge
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResonanceType(str, Enum):
    FLOW = "flow"
    RESONANCE = "resonance"
    DEEP_RESONANCE = "deep_resonance"
    DIVERGENCE = "divergence"


@dataclass(frozen=True)
class ResonanceResult:
    resonance_type: ResonanceType
    delta_before: float
    delta_after: float
    prediction_confidence: float
    explanation: str

    def to_dict(self) -> dict:
        return {
            "resonance_type": self.resonance_type.value,
            "delta_before": float(self.delta_before),
            "delta_after": float(self.delta_after),
            "prediction_confidence": float(self.prediction_confidence),
            "explanation": self.explanation,
        }


def _semantic_delta(result: Any) -> float:
    signals = getattr(result, "signals", None)
    return float(getattr(signals, "semantic_delta", 0.0) or 0.0)


def _prediction_confidence(result: Any) -> float:
    prediction = getattr(result, "prediction", None)
    return float(getattr(prediction, "prediction_confidence", 1.0) or 1.0)


def classify_resonance(
    before: Any,
    after: Any,
    *,
    flow_threshold: float = 0.05,
    confidence_threshold: float = 0.5,
) -> ResonanceResult:
    """
    Compare two consecutive TensionResults to classify interaction resonance.
    """
    delta_before = _semantic_delta(before)
    delta_after = _semantic_delta(after)
    pred_conf = _prediction_confidence(after)

    if delta_before < float(flow_threshold):
        return ResonanceResult(
            resonance_type=ResonanceType.FLOW,
            delta_before=delta_before,
            delta_after=delta_after,
            prediction_confidence=pred_conf,
            explanation="No meaningful pre-response tension detected; classified as flow.",
        )

    if delta_after >= delta_before:
        return ResonanceResult(
            resonance_type=ResonanceType.DIVERGENCE,
            delta_before=delta_before,
            delta_after=delta_after,
            prediction_confidence=pred_conf,
            explanation="Post-response semantic delta did not converge.",
        )

    if pred_conf < float(confidence_threshold):
        return ResonanceResult(
            resonance_type=ResonanceType.DEEP_RESONANCE,
            delta_before=delta_before,
            delta_after=delta_after,
            prediction_confidence=pred_conf,
            explanation="Converged despite low prediction confidence; deep resonance detected.",
        )

    return ResonanceResult(
        resonance_type=ResonanceType.RESONANCE,
        delta_before=delta_before,
        delta_after=delta_after,
        prediction_confidence=pred_conf,
        explanation="Tension converged with confidence support; resonance detected.",
    )
