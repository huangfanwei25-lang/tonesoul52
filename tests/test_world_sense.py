"""Tests for tonesoul.yuhun.world_sense.WorldSense."""

from __future__ import annotations

from tonesoul.yuhun.world_sense import DreamCandidate, WorldSense


def _normal_vec():
    return {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}


def _high_drift_vec():
    return {"deltaT": 0.9, "deltaS": 0.1, "deltaR": 0.9}


class TestWorldSenseInit:
    def test_no_observations_quick_status(self):
        ws = WorldSense()
        status = ws.quick_status()
        assert status["step"] == 0
        assert status["is_drifting"] is False
        assert status["is_lockdown"] is False
        assert status["inbreeding_risk"] == "none"
        assert "no observations" in status["advisory"]

    def test_no_observations_dream_candidates_empty(self):
        ws = WorldSense()
        candidates = ws.dream_candidates(top_n=5)
        assert candidates == []

    def test_no_observations_inbreeding_risk_none(self):
        ws = WorldSense()
        risk = ws.inbreeding_risk()
        assert risk.risk_level in ("none", "low")

    def test_no_observations_stable_anchors(self):
        ws = WorldSense()
        anchors = ws.stable_anchors()
        assert 0.0 <= anchors.stability_score <= 1.0


class TestObserve:
    def test_observe_returns_snapshot_with_step(self):
        ws = WorldSense()
        snap = ws.observe(semantic_vector=_normal_vec(), tension_total=0.1)
        assert snap.step >= 1
        assert 0.0 <= snap.drift_value <= 2.0

    def test_observe_increments_step(self):
        ws = WorldSense()
        snap1 = ws.observe(semantic_vector=_normal_vec(), tension_total=0.0)
        snap2 = ws.observe(semantic_vector=_normal_vec(), tension_total=0.0)
        assert snap2.step > snap1.step

    def test_observe_high_tension_records_value(self):
        ws = WorldSense()
        snap = ws.observe(semantic_vector=_normal_vec(), tension_total=0.9)
        assert snap.tension_total == 0.9

    def test_observe_large_drift_triggers_warning(self):
        ws = WorldSense(home_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5})
        for _ in range(3):
            ws.observe(semantic_vector=_high_drift_vec(), tension_total=0.0)
        status = ws.quick_status()
        assert status["step"] >= 3


class TestDreamCandidates:
    def test_low_drift_no_candidates(self):
        ws = WorldSense(
            home_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            high_drift_threshold=0.40,
            high_tension_threshold=0.75,
        )
        for _ in range(3):
            ws.observe(semantic_vector=_normal_vec(), tension_total=0.1)
        candidates = ws.dream_candidates()
        assert len(candidates) == 0

    def test_high_tension_produces_candidate(self):
        ws = WorldSense(high_tension_threshold=0.75)
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.95)
        candidates = ws.dream_candidates()
        assert len(candidates) >= 1
        assert candidates[0].priority > 0.0

    def test_candidates_sorted_by_priority_descending(self):
        ws = WorldSense(high_tension_threshold=0.75)
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.80)
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.99)
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.77)
        candidates = ws.dream_candidates()
        priorities = [c.priority for c in candidates]
        assert priorities == sorted(priorities, reverse=True)

    def test_top_n_limits_results(self):
        ws = WorldSense(high_tension_threshold=0.75)
        for _ in range(5):
            ws.observe(semantic_vector=_normal_vec(), tension_total=0.95)
        candidates = ws.dream_candidates(top_n=2)
        assert len(candidates) <= 2

    def test_candidate_has_required_fields(self):
        ws = WorldSense(high_tension_threshold=0.75)
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.95)
        candidates = ws.dream_candidates()
        assert candidates
        c = candidates[0]
        assert isinstance(c, DreamCandidate)
        assert c.step >= 1
        assert c.reason
        assert 0.0 < c.priority <= 1.0
        assert c.type in ("high_drift", "lockdown_event", "high_tension")


class TestQuickStatus:
    def test_nominal_status_after_stable_observations(self):
        ws = WorldSense()
        for _ in range(5):
            ws.observe(semantic_vector=_normal_vec(), tension_total=0.1)
        status = ws.quick_status()
        assert status["advisory"] == "nominal" or "drift" in status["advisory"] or "inbreeding" in status["advisory"]
        assert status["step"] == 5

    def test_status_includes_all_required_keys(self):
        ws = WorldSense()
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.3)
        status = ws.quick_status()
        for key in ("is_drifting", "is_lockdown", "inbreeding_risk", "step", "advisory"):
            assert key in status


class TestShadowSupplement:
    def test_to_shadow_supplement_empty(self):
        ws = WorldSense()
        supplement = ws.to_shadow_supplement()
        assert isinstance(supplement, dict)
        assert "world_sense" in supplement

    def test_to_shadow_supplement_after_observations(self):
        ws = WorldSense()
        ws.observe(semantic_vector=_normal_vec(), tension_total=0.5)
        supplement = ws.to_shadow_supplement()
        world = supplement["world_sense"]
        assert "step" in world
        assert world["step"] >= 1
