from __future__ import annotations

from tonesoul.council_capability import (
    CapabilityBoundary,
    CouncilRole,
    CouncilWeights,
    LongTermQualityMonitor,
)


def test_council_weights_from_persona_uses_defaults() -> None:
    weights = CouncilWeights.from_persona({"council_weights": {"guardian": 1.5, "critic": 0.8}})

    assert weights.guardian == 1.5
    assert weights.analyst == 1.0
    assert weights.critic == 0.8
    assert weights.advocate == 1.0


def test_compute_zone_adjustment_normalizes_weighted_sum() -> None:
    weights = CouncilWeights(guardian=2.0, analyst=1.0, critic=1.0, advocate=0.0)

    assert weights.compute_zone_adjustment() == -0.0325


def test_adjusted_zone_thresholds_apply_zone_shift() -> None:
    thresholds = CouncilWeights(
        guardian=2.0, analyst=1.0, critic=1.0, advocate=0.0
    ).adjusted_zone_thresholds()

    assert thresholds == {
        "safe_to_transit": 0.368,
        "transit_to_risk": 0.568,
        "risk_to_danger": 0.818,
    }


def test_to_dict_includes_weights_and_zone_adjustment() -> None:
    weights = CouncilWeights(guardian=1.0, analyst=1.0, critic=1.0, advocate=1.0)

    assert weights.to_dict() == {
        "guardian": 1.0,
        "analyst": 1.0,
        "critic": 1.0,
        "advocate": 1.0,
        "zone_adjustment": -0.0125,
    }


def test_zone_adjustment_map_covers_all_roles() -> None:
    assert set(CouncilWeights.ZONE_ADJUSTMENT) == {
        CouncilRole.GUARDIAN,
        CouncilRole.ANALYST,
        CouncilRole.CRITIC,
        CouncilRole.ADVOCATE,
    }


def test_capability_boundary_from_persona_reads_skill_map() -> None:
    boundary = CapabilityBoundary.from_persona({"skills": {"python": 0.9, "frontend": 0.6}})

    assert boundary.skills == {"python": 0.9, "frontend": 0.6}


def test_check_coverage_uses_best_matching_skill() -> None:
    boundary = CapabilityBoundary(skills={"python": 0.9, "backend": 0.6})

    coverage, suggestion = boundary.check_coverage("python backend service")

    assert coverage == 0.9
    assert suggestion


def test_check_coverage_returns_zero_when_registry_is_empty() -> None:
    coverage, suggestion = CapabilityBoundary().check_coverage("unknown domain")

    assert coverage == 0.0
    assert suggestion


def test_get_tolerance_multiplier_tracks_coverage_tiers() -> None:
    boundary = CapabilityBoundary()

    assert boundary.get_tolerance_multiplier(0.85) == 1.0
    assert boundary.get_tolerance_multiplier(0.6) == 1.1
    assert boundary.get_tolerance_multiplier(0.4) == 1.3
    assert boundary.get_tolerance_multiplier(0.1) == 1.5


def test_generate_prefix_only_for_lower_coverage_ranges() -> None:
    boundary = CapabilityBoundary()

    assert boundary.generate_prefix(0.2)
    assert boundary.generate_prefix(0.4)
    assert boundary.generate_prefix(0.6) is None


def test_record_session_adds_timestamp() -> None:
    monitor = LongTermQualityMonitor()
    monitor.record_session({"avg_delta_s": 0.2})

    assert len(monitor.session_summaries) == 1
    assert "recorded_at" in monitor.session_summaries[0]


def test_get_long_term_trend_is_unknown_without_enough_history() -> None:
    monitor = LongTermQualityMonitor()
    monitor.record_session({"avg_delta_s": 0.2})

    assert monitor.get_long_term_trend() == {"trend": "unknown", "sessions": 1}


def test_get_long_term_trend_detects_degrading() -> None:
    monitor = LongTermQualityMonitor()
    for value in (0.2, 0.25, 0.3, 0.45, 0.5):
        monitor.record_session({"avg_delta_s": value})

    trend = monitor.get_long_term_trend()

    assert trend["trend"] == "degrading"
    assert trend["sessions"] == 5
    assert trend["recent_avg_delta_s"] == 0.4167


def test_get_long_term_trend_detects_improving() -> None:
    monitor = LongTermQualityMonitor()
    for value in (0.5, 0.45, 0.4, 0.2, 0.15):
        monitor.record_session({"avg_delta_s": value})

    assert monitor.get_long_term_trend()["trend"] == "improving"


def test_get_long_term_trend_detects_stable() -> None:
    monitor = LongTermQualityMonitor()
    for value in (0.3, 0.31, 0.29, 0.32, 0.3):
        monitor.record_session({"avg_delta_s": value})

    assert monitor.get_long_term_trend()["trend"] == "stable"


def test_get_alerts_returns_all_active_warnings() -> None:
    monitor = LongTermQualityMonitor()
    sessions = [
        {"avg_delta_s": 0.2, "contract_pass_rate": 0.9, "intervention_rate": 0.1},
        {"avg_delta_s": 0.25, "contract_pass_rate": 0.8, "intervention_rate": 0.15},
        {"avg_delta_s": 0.35, "contract_pass_rate": 0.6, "intervention_rate": 0.25},
        {"avg_delta_s": 0.45, "contract_pass_rate": 0.55, "intervention_rate": 0.35},
        {"avg_delta_s": 0.5, "contract_pass_rate": 0.5, "intervention_rate": 0.4},
    ]
    for session in sessions:
        monitor.record_session(session)

    alerts = monitor.get_alerts()

    assert len(alerts) == 3


def test_get_alerts_returns_empty_for_short_history() -> None:
    monitor = LongTermQualityMonitor()
    monitor.record_session(
        {"avg_delta_s": 0.2, "contract_pass_rate": 1.0, "intervention_rate": 0.0}
    )

    assert monitor.get_alerts() == []
