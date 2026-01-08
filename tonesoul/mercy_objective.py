from typing import Dict, Optional

from .ystm.schema import utc_now

BASE_WEIGHTS = {
    "benefit": 0.3,
    "harm": -0.35,
    "fairness": 0.15,
    "traceability": 0.1,
    "reversibility": 0.1,
}

MODE_WEIGHT_MULTIPLIERS = {
    "normal": {},
    "cautious": {"harm": 1.2, "benefit": 0.9},
    "lockdown": {"harm": 1.4, "benefit": 0.8, "traceability": 1.1},
}

DEFAULT_SIGNALS = {
    "benefit": 0.5,
    "harm": 0.4,
    "fairness": 0.5,
    "traceability": 0.8,
    "reversibility": 0.6,
}

MODE_SIGNAL_OVERRIDES = {
    "cautious": {"harm": 0.6},
    "lockdown": {"harm": 0.7, "benefit": 0.4},
}


def _decision_mode(context: Dict[str, object]) -> str:
    time_island = context.get("time_island") if isinstance(context, dict) else {}
    if not isinstance(time_island, dict):
        return "normal"
    kairos = time_island.get("kairos")
    if not isinstance(kairos, dict):
        return "normal"
    return str(kairos.get("decision_mode") or "normal")


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(abs(value) for value in weights.values())
    if total == 0:
        return weights
    return {key: value / total for key, value in weights.items()}


def _apply_multipliers(
    weights: Dict[str, float],
    multipliers: Optional[Dict[str, float]],
) -> Dict[str, float]:
    if not multipliers:
        return dict(weights)
    adjusted = dict(weights)
    for key, multiplier in multipliers.items():
        if key in adjusted:
            adjusted[key] = adjusted[key] * float(multiplier)
    return adjusted


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def resolve_mercy_objective(
    context: Dict[str, object],
    signals: Optional[Dict[str, float]] = None,
    weight_overrides: Optional[Dict[str, float]] = None,
) -> Dict[str, object]:
    decision_mode = _decision_mode(context)
    weights = _apply_multipliers(BASE_WEIGHTS, MODE_WEIGHT_MULTIPLIERS.get(decision_mode))
    if weight_overrides:
        for key, value in weight_overrides.items():
            weights[key] = float(value)
    weights = _normalize_weights(weights)

    resolved_signals = dict(DEFAULT_SIGNALS)
    resolved_signals.update(MODE_SIGNAL_OVERRIDES.get(decision_mode, {}))
    if signals:
        for key, value in signals.items():
            resolved_signals[key] = float(value)
    resolved_signals = {key: _clamp(value) for key, value in resolved_signals.items()}

    components = {}
    score = 0.0
    for key, weight in weights.items():
        signal = resolved_signals.get(key, 0.0)
        contribution = weight * signal
        components[key] = round(contribution, 4)
        score += contribution

    return {
        "objective": "mercy_based",
        "objective_version": "0.1",
        "generated_at": utc_now(),
        "decision_mode": decision_mode,
        "weights": weights,
        "signals": resolved_signals,
        "components": components,
        "score": round(score, 4),
        "rationale": "Weighted objective balances benefit with harm reduction and governance traceability.",
    }
