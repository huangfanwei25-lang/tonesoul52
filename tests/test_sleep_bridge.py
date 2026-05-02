"""Tests for tonesoul.yuhun.sleep_bridge.candidate_to_stimulus."""

from __future__ import annotations

from tonesoul.yuhun.sleep_bridge import candidate_to_stimulus
from tonesoul.yuhun.world_sense import DreamCandidate


def _make_candidate(
    step=3,
    type_="high_tension",
    drift=0.65,
    tension=0.85,
    priority=0.72,
    reason="high tension event",
    jump_signal=None,
):
    return DreamCandidate(
        step=step,
        reason=reason,
        drift_at_moment=drift,
        tension_at_moment=tension,
        jump_signal=jump_signal
        or {"triggered": False, "self_reference": 0.1, "chain_integrity": 0.95},
        priority=priority,
        type=type_,
    )


def test_stimulus_has_required_dream_engine_fields():
    payload = candidate_to_stimulus(_make_candidate())
    for field in ("topic", "summary", "relevance_score", "novelty_score", "tags", "source_url"):
        assert field in payload


def test_topic_includes_step_and_type_label():
    candidate = _make_candidate(step=7, type_="high_drift")
    payload = candidate_to_stimulus(candidate)
    assert "Step 7" in payload["topic"]
    assert "漂移" in payload["topic"] or "drift" in payload["topic"].lower()


def test_relevance_score_capped_at_one():
    candidate = _make_candidate(drift=2.0)
    payload = candidate_to_stimulus(candidate)
    assert payload["relevance_score"] == 1.0


def test_novelty_score_capped_at_one():
    candidate = _make_candidate(tension=1.5)
    payload = candidate_to_stimulus(candidate)
    assert payload["novelty_score"] == 1.0


def test_scores_reflect_drift_and_tension():
    candidate = _make_candidate(drift=0.3, tension=0.6)
    payload = candidate_to_stimulus(candidate)
    assert abs(payload["relevance_score"] - 0.3) < 0.01
    assert abs(payload["novelty_score"] - 0.6) < 0.01


def test_tags_include_yuhun_world_sense_and_type():
    candidate = _make_candidate(type_="lockdown_event")
    payload = candidate_to_stimulus(candidate)
    assert "yuhun" in payload["tags"]
    assert "world_sense" in payload["tags"]
    assert "lockdown_event" in payload["tags"]


def test_seabed_lockdown_tag_added_when_triggered():
    candidate = _make_candidate(
        jump_signal={"triggered": True, "self_reference": 0.2, "chain_integrity": 0.8}
    )
    payload = candidate_to_stimulus(candidate)
    assert "seabed_lockdown" in payload["tags"]


def test_inbreeding_risk_tag_added_when_self_reference_high():
    candidate = _make_candidate(
        jump_signal={"triggered": False, "self_reference": 0.8, "chain_integrity": 0.6}
    )
    payload = candidate_to_stimulus(candidate)
    assert "inbreeding_risk" in payload["tags"]


def test_source_url_includes_step():
    candidate = _make_candidate(step=12)
    payload = candidate_to_stimulus(candidate)
    assert "12" in payload["source_url"]


def test_session_id_propagated():
    candidate = _make_candidate()
    payload = candidate_to_stimulus(candidate, session_id="session-xyz")
    assert payload["yuhun_metadata"]["session_id"] == "session-xyz"
    assert payload["provenance"]["session_id"] == "session-xyz"


def test_yuhun_metadata_contains_key_fields():
    candidate = _make_candidate(step=5, type_="high_drift", drift=0.55, tension=0.80)
    payload = candidate_to_stimulus(candidate)
    meta = payload["yuhun_metadata"]
    assert meta["step"] == 5
    assert meta["candidate_type"] == "high_drift"
    assert abs(meta["drift_at_moment"] - 0.55) < 0.01
    assert abs(meta["tension_at_moment"] - 0.80) < 0.01


def test_unknown_type_gets_fallback_label():
    candidate = _make_candidate(type_="exotic_new_type")
    payload = candidate_to_stimulus(candidate)
    assert "YUHUN" in payload["topic"] or "exotic_new_type" in payload["topic"]
