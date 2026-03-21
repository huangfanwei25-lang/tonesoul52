"""Tests for DriftTracker — Home Vector distance monitoring."""

from __future__ import annotations

from tonesoul.drift_tracker import DriftTracker


def test_default_home_vector() -> None:
    dt = DriftTracker()
    assert dt.home == {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}


def test_drift_at_home_is_zero() -> None:
    dt = DriftTracker()
    result = dt.compute(deltaT=0.5, deltaS=0.5, deltaR=0.5)
    assert result.drift == 0.0
    assert result.exceeded is False


def test_drift_increases_with_distance() -> None:
    dt = DriftTracker()
    r1 = dt.compute(deltaT=0.6, deltaS=0.5, deltaR=0.5)
    r2 = dt.compute(deltaT=0.8, deltaS=0.5, deltaR=0.5)
    assert r2.drift > r1.drift > 0.0


def test_drift_per_axis() -> None:
    dt = DriftTracker(home={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
    result = dt.compute(deltaT=0.7, deltaS=0.3, deltaR=0.5)
    assert abs(result.per_axis["deltaT"] - 0.2) < 1e-6
    assert abs(result.per_axis["deltaS"] - 0.2) < 1e-6
    assert abs(result.per_axis["deltaR"]) < 1e-6


def test_exceeded_when_above_threshold() -> None:
    dt = DriftTracker(threshold=0.1)
    result = dt.compute(deltaT=1.0, deltaS=1.0, deltaR=1.0)
    assert result.exceeded is True


def test_not_exceeded_when_below_threshold() -> None:
    dt = DriftTracker(threshold=2.0)
    result = dt.compute(deltaT=0.6, deltaS=0.5, deltaR=0.5)
    assert result.exceeded is False


def test_custom_home_vector() -> None:
    dt = DriftTracker(home={"deltaT": 0.0, "deltaS": 0.0, "deltaR": 0.0})
    result = dt.compute(deltaT=0.0, deltaS=0.0, deltaR=0.0)
    assert result.drift == 0.0


def test_maximum_drift() -> None:
    """Maximum drift is √3 ≈ 1.732 when going from (0,0,0) to (1,1,1)."""
    dt = DriftTracker(home={"deltaT": 0.0, "deltaS": 0.0, "deltaR": 0.0})
    result = dt.compute(deltaT=1.0, deltaS=1.0, deltaR=1.0)
    assert abs(result.drift - 3**0.5) < 1e-4


def test_drift_max_for_dcs_scaling() -> None:
    """DCS-scaled drift should be ≈ 4.0 at maximum Euclidean distance."""
    dt = DriftTracker(home={"deltaT": 0.0, "deltaS": 0.0, "deltaR": 0.0})
    dcs_val = dt.drift_max_for_dcs(deltaT=1.0, deltaS=1.0, deltaR=1.0)
    assert abs(dcs_val - 4.0) < 0.01


def test_drift_max_for_dcs_zero_at_home() -> None:
    dt = DriftTracker()
    dcs_val = dt.drift_max_for_dcs(deltaT=0.5, deltaS=0.5, deltaR=0.5)
    assert dcs_val == 0.0


def test_last_result_property() -> None:
    dt = DriftTracker()
    assert dt.last_result is None
    dt.compute(deltaT=0.7, deltaS=0.5, deltaR=0.5)
    assert dt.last_result is not None
    assert dt.last_result.drift > 0.0


def test_to_dict() -> None:
    dt = DriftTracker()
    dt.compute(deltaT=0.8, deltaS=0.5, deltaR=0.5)
    d = dt.to_dict()
    assert d["home"] == {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}
    assert d["last_drift"] is not None
    assert d["last_exceeded"] is not None
