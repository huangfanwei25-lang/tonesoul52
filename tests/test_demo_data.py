"""Tests for demo_data — realistic sample governance data."""

from apps.dashboard.frontend.utils.demo_data import (
    generate_demo_governance,
    generate_demo_health,
    generate_demo_reflex,
    generate_demo_vows,
)


def test_demo_governance_structure():
    gov = generate_demo_governance()
    assert isinstance(gov, dict)
    assert "soul_integral" in gov
    assert "session_count" in gov
    assert "tension_history" in gov
    assert "baseline_drift" in gov
    assert isinstance(gov["soul_integral"], float)
    assert isinstance(gov["session_count"], int)
    assert isinstance(gov["tension_history"], list)
    assert len(gov["tension_history"]) > 0


def test_demo_governance_values_in_range():
    gov = generate_demo_governance()
    assert 0.0 <= gov["soul_integral"] <= 1.0
    assert gov["session_count"] >= 0
    drift = gov["baseline_drift"]
    for key in ("caution_bias", "innovation_bias", "autonomy_level"):
        assert key in drift
        assert 0.0 <= drift[key] <= 1.0


def test_demo_vows_structure():
    vows = generate_demo_vows()
    assert isinstance(vows, dict)
    assert "total" in vows
    assert "active" in vows
    assert "vow_names" in vows
    assert "raw_vows" in vows
    assert vows["active"] <= vows["total"]
    assert len(vows["raw_vows"]) == vows["active"]


def test_demo_vow_entries_valid():
    vows = generate_demo_vows()
    for vow in vows["raw_vows"]:
        assert "id" in vow
        assert "content" in vow
        assert len(vow["content"]) > 0


def test_demo_health_structure():
    health = generate_demo_health()
    assert isinstance(health, dict)
    assert "backend" in health
    assert "chain_status" in health
    assert "recent_visitors" in health
    assert isinstance(health["recent_visitors"], list)


def test_demo_reflex_structure():
    reflex = generate_demo_reflex()
    assert isinstance(reflex, dict)
    assert "soul_band" in reflex
    assert "gate_modifier" in reflex
    assert reflex["soul_band"] in ("serene", "alert", "strained", "critical")
    assert 0.0 < reflex["gate_modifier"] <= 1.0
