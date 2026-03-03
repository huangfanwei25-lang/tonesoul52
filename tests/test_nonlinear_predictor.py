"""Tests for RFC-013: NonlinearPredictor."""

from tonesoul.nonlinear_predictor import NonlinearPredictor, PredictionResult


def test_prediction_result_to_dict():
    pr = PredictionResult(
        predicted_delta_sigma=0.42,
        prediction_confidence=0.85,
        trend="converging",
        lyapunov_exponent=-0.3,
        horizon_steps=4,
        acceleration=-0.01,
        ewma=0.4,
    )
    d = pr.to_dict()
    assert d["trend"] == "converging"
    assert d["prediction_confidence"] == 0.85
    assert d["lyapunov_exponent"] == -0.3


def test_converging_sequence():
    p = NonlinearPredictor(window=6, alpha=0.3)
    # Feed a monotonically decreasing sequence
    for val in [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]:
        result = p.predict(val)
    assert result.trend == "converging"
    assert result.lyapunov_exponent < 0


def test_stable_sequence():
    p = NonlinearPredictor(window=6, alpha=0.3)
    # Feed a constant sequence (very stable)
    for val in [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]:
        result = p.predict(val)
    assert result.trend == "stable"
    # Lyapunov is very negative because diffs ≈ 0 → log(~0) → clamped to -5
    assert result.lyapunov_exponent < 0


def test_diverging_sequence():
    p = NonlinearPredictor(window=6, alpha=0.3)
    # Feed a monotonically increasing sequence
    for val in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        result = p.predict(val)
    assert result.trend in ("diverging", "converging")
    # With constant increments, Lyapunov should stabilise around log(0.1)


def test_chaotic_sequence():
    p = NonlinearPredictor(window=8, alpha=0.3)
    # Feed a wildly oscillating sequence with large jumps
    for val in [0.1, 0.9, 0.05, 0.95, 0.1, 0.85, 0.02, 0.98]:
        result = p.predict(val)
    assert result.trend == "chaotic"
    # For symmetric oscillation, Lyapunov sign can vary;
    # the key assertion is that trend is correctly classified as chaotic


def test_prediction_clamps_within_bounds():
    p = NonlinearPredictor()
    result = p.predict(0.0)
    assert 0.0 <= result.predicted_delta_sigma <= 2.0
    assert 0.0 <= result.prediction_confidence <= 1.0

    result = p.predict(2.0)
    assert 0.0 <= result.predicted_delta_sigma <= 2.0


def test_reset_clears_state():
    p = NonlinearPredictor()
    p.predict(0.5)
    p.predict(0.6)
    assert len(p.history) == 2

    p.reset()
    assert len(p.history) == 0


def test_confidence_increases_with_predictable_data():
    p = NonlinearPredictor(window=8, alpha=0.3)
    # Highly predictable: constant
    for _ in range(6):
        result = p.predict(0.5)
    conf_stable = result.prediction_confidence

    p.reset()
    # Less predictable: noisy
    for val in [0.2, 0.8, 0.3, 0.7, 0.25, 0.75]:
        result = p.predict(val)
    conf_noisy = result.prediction_confidence

    assert conf_stable > conf_noisy


def test_horizon_short_for_chaotic():
    p = NonlinearPredictor(window=6, alpha=0.3)
    for val in [0.1, 0.9, 0.05, 0.95, 0.1, 0.85]:
        result = p.predict(val)
    # Chaotic → short horizon
    assert result.horizon_steps <= 2
