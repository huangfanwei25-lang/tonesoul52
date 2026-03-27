"""Tests for Phase 544: DriftMonitor — Structure Layer semantic anchor."""

from tonesoul.drift_monitor import DriftAlert, DriftMonitor, DriftSnapshot


class TestDriftMonitorBasics:
    """Core DriftMonitor functionality."""

    def test_initial_state_is_zero(self):
        dm = DriftMonitor()
        assert dm.current_drift == 0.0
        assert dm.current_alert == DriftAlert.NONE
        assert dm.step_count == 0

    def test_first_observation_sets_center(self):
        dm = DriftMonitor()
        snap = dm.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        # Observation equals home → drift ≈ 0
        assert snap.drift < 0.001
        assert snap.alert == DriftAlert.NONE
        assert snap.step == 1

    def test_observation_at_home_stays_zero(self):
        dm = DriftMonitor(home_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        for _ in range(5):
            snap = dm.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        assert snap.drift < 0.001
        assert snap.alert == DriftAlert.NONE

    def test_drift_increases_with_divergent_observation(self):
        dm = DriftMonitor(home_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        # Extreme observation: all 1.0 when home is all 0.5
        snap = dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 1.0})
        assert snap.drift > 0.0

    def test_ema_smooths_observations(self):
        dm = DriftMonitor(ema_alpha=0.3)
        # First observation divergent from home (not proportional)
        snap1 = dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.5})
        # Second observation back at home
        snap2 = dm.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        # Center should be partially corrected but not fully
        assert snap2.drift < snap1.drift
        assert snap2.drift > 0.0  # EMA retains prior influence


class TestDriftAlertClassification:
    """Test graduated alert levels."""

    def test_no_alert_below_warning(self):
        dm = DriftMonitor(theta_warning=0.35, theta_crisis=0.60)
        snap = dm.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        assert snap.alert == DriftAlert.NONE

    def test_warning_alert(self):
        dm = DriftMonitor(theta_warning=0.05, theta_crisis=0.60)
        # Push drift above warning with divergent observation
        snap = dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.5})
        assert snap.alert == DriftAlert.WARNING

    def test_crisis_alert(self):
        dm = DriftMonitor(theta_warning=0.01, theta_crisis=0.05)
        snap = dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 1.0})
        assert snap.alert == DriftAlert.CRISIS

    def test_custom_thresholds_respected(self):
        dm = DriftMonitor(theta_warning=0.001, theta_crisis=0.002)
        # Use divergent observation to trigger low thresholds
        snap = dm.observe({"deltaT": 0.8, "deltaS": 0.2, "deltaR": 0.5})
        assert snap.alert in (DriftAlert.WARNING, DriftAlert.CRISIS)


class TestCosineDrift:
    """Test the cosine drift computation."""

    def test_identical_vectors_zero_drift(self):
        drift = DriftMonitor._cosine_drift(
            {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
        )
        assert drift < 1e-10

    def test_orthogonal_vectors_drift_one(self):
        # [1, 0, 0] vs [0, 1, 0] → cosine = 0 → drift = 1.0
        drift = DriftMonitor._cosine_drift(
            {"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.0},
            {"deltaT": 0.0, "deltaS": 1.0, "deltaR": 0.0},
        )
        assert abs(drift - 1.0) < 1e-10

    def test_zero_vector_returns_drift_one(self):
        drift = DriftMonitor._cosine_drift(
            {"deltaT": 0.0, "deltaS": 0.0, "deltaR": 0.0},
            {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
        )
        assert drift == 1.0

    def test_drift_is_bounded_zero_to_two(self):
        # Opposite direction → cosine = -1 → drift = 2.0 (theoretical max)
        drift = DriftMonitor._cosine_drift(
            {"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.0},
            {"deltaT": -1.0, "deltaS": 0.0, "deltaR": 0.0},
        )
        assert 0.0 <= drift <= 2.0


class TestDriftSummary:
    """Test summary output for governance surfaces."""

    def test_empty_summary(self):
        dm = DriftMonitor()
        s = dm.summary()
        assert s["drift"] == 0.0
        assert s["steps"] == 0
        assert s["alert"] == "none"

    def test_summary_after_observations(self):
        dm = DriftMonitor()
        dm.observe({"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        dm.observe({"deltaT": 0.7, "deltaS": 0.3, "deltaR": 0.5})
        s = dm.summary()
        assert s["steps"] == 2
        assert "max_drift" in s
        assert "mean_drift" in s
        assert s["max_drift"] >= s["mean_drift"]


class TestDriftRecommendations:
    """Alert classifications should surface bounded guidance."""

    def test_warning_recommendation_increases_caution(self):
        dm = DriftMonitor(theta_warning=0.05, theta_crisis=0.60)
        dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 0.5})

        recommendation = dm.last_recommendation
        assert recommendation is not None
        assert recommendation.action == "increase_caution"
        assert recommendation.increase_caution is True
        assert recommendation.session_pause_recommended is False

    def test_crisis_recommendation_propagates_to_summary(self):
        dm = DriftMonitor(theta_warning=0.01, theta_crisis=0.05)
        dm.observe({"deltaT": 1.0, "deltaS": 0.0, "deltaR": 1.0})

        summary = dm.summary()
        recommendation = summary["recommended_action"]
        assert recommendation["action"] == "recommend_session_pause"
        assert recommendation["session_pause_recommended"] is True
        assert recommendation["human_check_in_recommended"] is True


class TestDriftSnapshot:
    """Test snapshot serialization."""

    def test_to_dict(self):
        snap = DriftSnapshot(
            center={"deltaT": 0.6, "deltaS": 0.4, "deltaR": 0.5},
            home={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            drift=0.123456,
            alert=DriftAlert.WARNING,
            step=3,
        )
        d = snap.to_dict()
        assert d["drift"] == 0.123456
        assert d["alert"] == "warning"
        assert d["step"] == 3
        assert d["center"]["deltaT"] == 0.6


class TestTrajectoryAnalysisDriftField:
    """Test Phase 544 drift field on TrajectoryAnalysis."""

    def test_default_drift_is_none(self):
        from tonesoul.tonebridge.trajectory import TrajectoryAnalysis

        ta = TrajectoryAnalysis()
        assert ta.drift is None
        assert ta.drift_alert is None

    def test_drift_in_to_dict_when_set(self):
        from tonesoul.tonebridge.trajectory import TrajectoryAnalysis

        ta = TrajectoryAnalysis(drift=0.42, drift_alert="warning")
        d = ta.to_dict()
        assert d["drift"] == 0.42
        assert d["drift_alert"] == "warning"

    def test_drift_absent_from_to_dict_when_none(self):
        from tonesoul.tonebridge.trajectory import TrajectoryAnalysis

        ta = TrajectoryAnalysis()
        d = ta.to_dict()
        assert "drift" not in d
        assert "drift_alert" not in d
