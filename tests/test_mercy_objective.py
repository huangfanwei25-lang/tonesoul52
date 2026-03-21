from __future__ import annotations

import pytest

from tonesoul.mercy_objective import (
    _clamp,
    _decision_mode,
    _normalize_weights,
    resolve_mercy_objective,
)


def test_resolve_mercy_objective_default_weights() -> None:
    result = resolve_mercy_objective({})

    assert result["objective"] == "mercy_based"
    assert result["decision_mode"] == "normal"
    assert pytest.approx(sum(abs(v) for v in result["weights"].values()), rel=1e-9) == 1.0


def test_resolve_mercy_objective_with_signals() -> None:
    baseline = resolve_mercy_objective({})
    result = resolve_mercy_objective({}, signals={"benefit": 1.0, "harm": 0.0})

    assert result["signals"]["benefit"] == 1.0
    assert result["signals"]["harm"] == 0.0
    assert result["score"] > baseline["score"]


def test_resolve_mercy_objective_with_overrides() -> None:
    baseline = resolve_mercy_objective({})
    result = resolve_mercy_objective({}, weight_overrides={"benefit": 0.8})

    assert result["weights"]["benefit"] > baseline["weights"]["benefit"]


def test_decision_mode_returns_string() -> None:
    result = _decision_mode({"time_island": {"kairos": {"decision_mode": "lockdown"}}})

    assert isinstance(result, str)
    assert result == "lockdown"


def test_normalize_weights_sums_to_one() -> None:
    normalized = _normalize_weights({"benefit": 0.2, "harm": -0.3, "fairness": 0.5})

    assert pytest.approx(sum(abs(v) for v in normalized.values()), rel=1e-9) == 1.0


def test_clamp_boundary_values() -> None:
    assert _clamp(-1.0) == 0.0
    assert _clamp(0.5) == 0.5
    assert _clamp(2.0) == 1.0
