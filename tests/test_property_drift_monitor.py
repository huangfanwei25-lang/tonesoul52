from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tonesoul.drift_monitor import DriftAlert, DriftMonitor


def _unit_float():
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


@st.composite
def _observation(draw):
    return {
        "deltaT": draw(_unit_float()),
        "deltaS": draw(_unit_float()),
        "deltaR": draw(_unit_float()),
    }


class TestDriftMonitorProperties:
    @settings(max_examples=25, deadline=5000)
    @given(observations=st.lists(_observation(), min_size=1, max_size=20))
    def test_observe_keeps_drift_in_expected_bounds(self, observations) -> None:
        monitor = DriftMonitor()

        for observation in observations:
            snapshot = monitor.observe(observation)
            assert 0.0 <= snapshot.drift <= 1.0

    @settings(max_examples=25, deadline=5000)
    @given(observations=st.lists(_observation(), min_size=1, max_size=20))
    def test_summary_step_count_matches_observation_count(self, observations) -> None:
        monitor = DriftMonitor()

        for observation in observations:
            monitor.observe(observation)

        assert monitor.summary()["steps"] == len(observations)

    @settings(max_examples=20, deadline=5000)
    @given(observations=st.lists(_observation(), min_size=1, max_size=12))
    def test_current_alert_is_always_valid_enum(self, observations) -> None:
        monitor = DriftMonitor()

        for observation in observations:
            monitor.observe(observation)

        assert monitor.current_alert in {DriftAlert.NONE, DriftAlert.WARNING, DriftAlert.CRISIS}

    @settings(max_examples=20, deadline=5000)
    @given(steps=st.integers(min_value=1, max_value=12))
    def test_stable_home_vector_input_does_not_trigger_warning(self, steps) -> None:
        monitor = DriftMonitor()

        for _ in range(steps):
            snapshot = monitor.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})

        assert snapshot.alert == DriftAlert.NONE
        assert monitor.current_drift == 0.0

    @settings(max_examples=15, deadline=5000)
    @given(alpha=st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False))
    def test_large_shift_triggers_warning_under_low_thresholds(self, alpha) -> None:
        monitor = DriftMonitor(ema_alpha=alpha, theta_warning=0.05, theta_crisis=0.2)
        monitor.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        alerts = []

        for _ in range(5):
            shifted = monitor.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.0})
            alerts.append(shifted.alert)

        assert any(alert in {DriftAlert.WARNING, DriftAlert.CRISIS} for alert in alerts)
