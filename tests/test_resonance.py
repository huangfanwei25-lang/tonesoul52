from __future__ import annotations

from dataclasses import dataclass

from tonesoul.resonance import ResonanceType, classify_resonance


@dataclass
class _Signals:
    semantic_delta: float


@dataclass
class _Prediction:
    prediction_confidence: float


@dataclass
class _Result:
    signals: _Signals
    prediction: _Prediction | None = None


def _r(delta: float, conf: float | None = None) -> _Result:
    prediction = _Prediction(conf) if conf is not None else None
    return _Result(signals=_Signals(semantic_delta=delta), prediction=prediction)


def test_flow_when_before_delta_below_threshold():
    result = classify_resonance(_r(0.02, 0.9), _r(0.01, 0.9), flow_threshold=0.05)
    assert result.resonance_type == ResonanceType.FLOW


def test_resonance_when_delta_converges_with_confidence():
    result = classify_resonance(_r(0.6, 0.8), _r(0.3, 0.8), confidence_threshold=0.5)
    assert result.resonance_type == ResonanceType.RESONANCE


def test_deep_resonance_when_converges_but_low_prediction_confidence():
    result = classify_resonance(_r(0.7, 0.2), _r(0.2, 0.2), confidence_threshold=0.5)
    assert result.resonance_type == ResonanceType.DEEP_RESONANCE


def test_divergence_when_after_delta_not_reduced():
    result = classify_resonance(_r(0.4, 0.9), _r(0.5, 0.9))
    assert result.resonance_type == ResonanceType.DIVERGENCE


def test_edge_case_equal_delta_is_divergence():
    result = classify_resonance(_r(0.3, 0.9), _r(0.3, 0.9))
    assert result.resonance_type == ResonanceType.DIVERGENCE


def test_defaults_prediction_confidence_to_one_when_missing():
    result = classify_resonance(_r(0.4, None), _r(0.2, None))
    assert result.prediction_confidence == 1.0
    assert result.resonance_type == ResonanceType.RESONANCE
