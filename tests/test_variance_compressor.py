"""Tests for RFC-013: DynamicVarianceCompressor."""

from tonesoul.nonlinear_predictor import PredictionResult
from tonesoul.semantic_control import LambdaState, SemanticZone
from tonesoul.variance_compressor import DynamicVarianceCompressor
from tonesoul.work_classifier import WorkCategory


def _make_prediction(trend: str = "stable", lyap: float = 0.0) -> PredictionResult:
    return PredictionResult(
        predicted_delta_sigma=0.5,
        prediction_confidence=0.8,
        trend=trend,
        lyapunov_exponent=lyap,
        horizon_steps=3,
        acceleration=0.0,
        ewma=0.5,
    )


def test_compression_result_to_dict():
    c = DynamicVarianceCompressor()
    result = c.compress(signal_variance=0.5)
    d = result.to_dict()
    assert "compression_ratio" in d
    assert "gamma_effective" in d
    assert "gamma_breakdown" in d
    assert "explanation" in d


def test_debug_has_strongest_compression():
    c = DynamicVarianceCompressor()
    pred = _make_prediction("stable")

    debug = c.compress(
        signal_variance=0.5,
        prediction=pred,
        work_category=WorkCategory.DEBUG,
    )
    freeform = c.compress(
        signal_variance=0.5,
        prediction=pred,
        work_category=WorkCategory.FREEFORM,
    )
    assert debug.compression_ratio < freeform.compression_ratio
    assert debug.gamma_effective > freeform.gamma_effective


def test_freeform_has_weakest_compression():
    c = DynamicVarianceCompressor()
    result = c.compress(
        signal_variance=0.5,
        prediction=_make_prediction("stable"),
        work_category=WorkCategory.FREEFORM,
    )
    # freeform γ_base = 0.1 → should be close to 1.0
    assert result.compression_ratio > 0.9


def test_chaotic_trend_adds_compression():
    c = DynamicVarianceCompressor()

    stable = c.compress(
        signal_variance=0.5,
        prediction=_make_prediction("stable"),
        work_category=WorkCategory.ENGINEERING,
    )
    chaotic = c.compress(
        signal_variance=0.5,
        prediction=_make_prediction("chaotic"),
        work_category=WorkCategory.ENGINEERING,
    )
    assert chaotic.compression_ratio < stable.compression_ratio


def test_danger_zone_adds_compression():
    c = DynamicVarianceCompressor()

    safe = c.compress(
        signal_variance=0.5,
        zone=SemanticZone.SAFE,
        work_category=WorkCategory.ENGINEERING,
    )
    danger = c.compress(
        signal_variance=0.5,
        zone=SemanticZone.DANGER,
        work_category=WorkCategory.ENGINEERING,
    )
    assert danger.compression_ratio < safe.compression_ratio


def test_chaotic_lambda_adds_compression():
    c = DynamicVarianceCompressor()

    convergent = c.compress(
        signal_variance=0.5,
        lambda_state=LambdaState.CONVERGENT,
        work_category=WorkCategory.ENGINEERING,
    )
    chaotic = c.compress(
        signal_variance=0.5,
        lambda_state=LambdaState.CHAOTIC,
        work_category=WorkCategory.ENGINEERING,
    )
    assert chaotic.compression_ratio < convergent.compression_ratio


def test_minimum_compression_floor():
    c = DynamicVarianceCompressor(min_ratio=0.35)
    # Maximum γ scenario: debug + chaotic trend + danger zone + chaotic lambda
    result = c.compress(
        signal_variance=10.0,  # very high variance
        prediction=_make_prediction("chaotic"),
        zone=SemanticZone.DANGER,
        lambda_state=LambdaState.CHAOTIC,
        work_category=WorkCategory.DEBUG,
    )
    assert result.compression_ratio >= 0.35


def test_zero_variance_gives_no_compression():
    c = DynamicVarianceCompressor()
    result = c.compress(
        signal_variance=0.0,
        work_category=WorkCategory.DEBUG,
    )
    assert result.compression_ratio == 1.0


def test_zone_override_suggestion():
    c = DynamicVarianceCompressor()
    # Force a scenario where compression is very strong but zone is SAFE
    result = c.compress(
        signal_variance=5.0,
        prediction=_make_prediction("chaotic"),
        zone=SemanticZone.SAFE,
        lambda_state=LambdaState.CHAOTIC,
        work_category=WorkCategory.DEBUG,
    )
    # If ratio < 0.5 and zone is SAFE, should suggest override
    if result.compression_ratio < 0.5:
        assert result.zone_override == "risk"


def test_no_prediction_defaults_to_stable():
    c = DynamicVarianceCompressor()
    result = c.compress(
        signal_variance=0.5,
        prediction=None,  # explicit None
        work_category=WorkCategory.ENGINEERING,
    )
    # Should use "stable" as default trend → no trend penalty
    assert result.gamma_breakdown["trend"] == 0.0
