"""Tests for tonesoul.memory.session_digest."""

from __future__ import annotations

from tonesoul.memory.session_digest import (
    _compute_coherence,
    _tension_summary,
    digest_session,
)


def test_tension_summary_empty():
    ts = _tension_summary([])
    assert ts["count"] == 0
    assert ts["max_severity"] == 0.0
    assert ts["avg_severity"] == 0.0
    assert ts["resolved_count"] == 0
    assert ts["unresolved_topics"] == []


def test_tension_summary_with_events():
    events = [
        {"severity": 0.6, "resolution": "acknowledged", "topic": "honesty"},
        {"severity": 0.4, "topic": "scope"},  # unresolved
        {"severity": 0.8, "resolution": "deferred", "topic": "trust"},
    ]
    ts = _tension_summary(events)
    assert ts["count"] == 3
    assert ts["max_severity"] == 0.8
    assert abs(ts["avg_severity"] - 0.6) < 0.01
    assert ts["resolved_count"] == 2
    assert "scope" in ts["unresolved_topics"]


def test_coherence_no_tension():
    ts = _tension_summary([])
    assert _compute_coherence(ts) == 1.0


def test_coherence_all_resolved():
    events = [
        {"severity": 0.8, "resolution": "ok", "topic": "x"},
        {"severity": 0.6, "resolution": "ok", "topic": "y"},
    ]
    ts = _tension_summary(events)
    # unresolved_ratio = 0, so coherence = 1 - avg_sev * 0 = 1.0
    assert _compute_coherence(ts) == 1.0


def test_coherence_all_unresolved():
    events = [{"severity": 0.5, "topic": "x"}, {"severity": 0.5, "topic": "y"}]
    ts = _tension_summary(events)
    # unresolved_ratio = 1.0, avg_sev = 0.5 → coherence = 1 - 0.5 = 0.5
    assert abs(_compute_coherence(ts) - 0.5) < 0.01


def test_digest_session_minimal():
    trace = {
        "session_id": "sess-001",
        "agent": "claude-test",
        "topics": ["governance", "drift"],
        "key_decisions": ["use tight vow enforcement"],
        "tension_events": [],
    }
    digest = digest_session(trace)

    assert digest["session_id"] == "sess-001"
    assert digest["agent"] == "claude-test"
    assert digest["topics"] == ["governance", "drift"]
    assert "use tight vow enforcement" in digest["learnings"]
    assert digest["coherence_snapshot"] == 1.0
    assert digest["verdict"] == "digest"
    assert digest["genesis"] == "session_end_pipeline"
    assert digest["is_mine"] is True


def test_digest_session_merges_compaction_carry_forward():
    trace = {
        "session_id": "sess-002",
        "agent": "test",
        "key_decisions": ["decision A"],
        "tension_events": [],
    }
    compaction = {"carry_forward": ["carry item 1", "carry item 2"]}
    digest = digest_session(trace, compaction=compaction)

    assert "decision A" in digest["learnings"]
    assert "carry item 1" in digest["learnings"]
    assert "carry item 2" in digest["learnings"]


def test_digest_session_tension_summary_integrated():
    trace = {
        "session_id": "sess-003",
        "agent": "test",
        "key_decisions": [],
        "tension_events": [
            {"severity": 0.9, "topic": "axiom-conflict"},
            {"severity": 0.3, "resolution": "resolved", "topic": "scope"},
        ],
    }
    digest = digest_session(trace)

    ts = digest["tension_summary"]
    assert ts["count"] == 2
    assert ts["max_severity"] == 0.9
    assert ts["resolved_count"] == 1
    assert "axiom-conflict" in ts["unresolved_topics"]
    # coherence = 1 - avg(0.9, 0.3) * 0.5 = 1 - 0.6 * 0.5 = 0.7
    assert abs(digest["coherence_snapshot"] - 0.7) < 0.01


def test_digest_session_stance_shift_preserved():
    trace = {
        "session_id": "sess-004",
        "agent": "test",
        "key_decisions": [],
        "tension_events": [],
        "stance_shift": {"from": "neutral", "to": "cautious", "reason": "high tension"},
    }
    digest = digest_session(trace)
    assert digest["stance_shift"]["to"] == "cautious"


def test_digest_session_generates_session_id_if_missing():
    trace = {"agent": "test", "key_decisions": [], "tension_events": []}
    digest = digest_session(trace)
    assert digest["session_id"]
    assert len(digest["session_id"]) > 10
