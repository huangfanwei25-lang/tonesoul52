"""Tests for tonesoul.runtime_adapter — the session load/commit bridge."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from tonesoul.runtime_adapter import (
    GovernancePosture,
    SessionTrace,
    commit,
    decay_tensions,
    drift_baseline,
    load,
    summary,
    update_soul_integral,
)


@pytest.fixture()
def tmp_state(tmp_path: Path) -> Path:
    return tmp_path / "governance_state.json"


@pytest.fixture()
def tmp_traces(tmp_path: Path) -> Path:
    return tmp_path / "traces.jsonl"


# ── load() ──────────────────────────────────────────────────────


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    posture = load(state_path=tmp_path / "nonexistent.json")
    assert posture.session_count == 0
    assert posture.soul_integral == 0.0
    assert len(posture.active_vows) == 0


def test_load_existing_file(tmp_state: Path) -> None:
    state = {
        "version": "0.1.0",
        "last_updated": "2026-03-25T00:00:00+00:00",
        "soul_integral": 1.5,
        "tension_history": [],
        "active_vows": [{"id": "v1", "content": "test vow", "created": "2026-03-25"}],
        "aegis_vetoes": [],
        "baseline_drift": {"caution_bias": 0.6, "innovation_bias": 0.4, "autonomy_level": 0.3},
        "session_count": 5,
    }
    tmp_state.write_text(json.dumps(state), encoding="utf-8")
    posture = load(state_path=tmp_state)
    assert posture.session_count == 5
    assert posture.soul_integral == 1.5
    assert len(posture.active_vows) == 1


# ── commit() ────────────────────────────────────────────────────


def test_commit_increments_session_count(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(agent="test", key_decisions=["did a thing"])
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    assert posture.session_count == 1

    trace2 = SessionTrace(agent="test", key_decisions=["did another thing"])
    posture2 = commit(trace2, state_path=tmp_state, traces_path=tmp_traces)
    assert posture2.session_count == 2


def test_commit_writes_trace_jsonl(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(agent="claude", key_decisions=["test"])
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    lines = tmp_traces.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["agent"] == "claude"
    assert "test" in record["key_decisions"]


def test_commit_merges_tension_events(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(
        agent="test",
        tension_events=[{"topic": "scope creep", "severity": 0.6}],
        key_decisions=["kept it small"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    assert len(posture.tension_history) == 1
    assert posture.tension_history[0]["topic"] == "scope creep"


def test_commit_creates_vow(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(
        agent="test",
        vow_events=[{"vow_id": "v-new", "action": "created", "detail": "always test"}],
        key_decisions=["added vow"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    ids = [v["id"] for v in posture.active_vows]
    assert "v-new" in ids


def test_commit_retires_vow(tmp_state: Path, tmp_traces: Path) -> None:
    # Seed with a vow
    state = {
        "version": "0.1.0",
        "last_updated": "2026-03-25T00:00:00+00:00",
        "soul_integral": 0.0,
        "tension_history": [],
        "active_vows": [{"id": "v-old", "content": "obsolete", "created": "2026-01-01"}],
        "aegis_vetoes": [],
        "baseline_drift": {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5},
        "session_count": 0,
    }
    tmp_state.write_text(json.dumps(state), encoding="utf-8")

    trace = SessionTrace(
        agent="test",
        vow_events=[{"vow_id": "v-old", "action": "retired"}],
        key_decisions=["retired old vow"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    ids = [v["id"] for v in posture.active_vows]
    assert "v-old" not in ids


# ── decay_tensions() ────────────────────────────────────────────


def test_decay_prunes_old_tensions() -> None:
    old = [{"timestamp": "2020-01-01T00:00:00+00:00", "severity": 0.5, "topic": "ancient"}]
    result = decay_tensions(old)
    assert len(result) == 0  # years old, fully decayed


def test_decay_preserves_recent_tensions() -> None:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    recent = [{"timestamp": now, "severity": 0.8, "topic": "just happened"}]
    result = decay_tensions(recent)
    assert len(result) == 1
    assert result[0]["severity"] >= 0.79  # barely decayed


# ── drift_baseline() ────────────────────────────────────────────


def test_drift_no_tensions_returns_same() -> None:
    base = {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5}
    assert drift_baseline(base, []) == base


def test_drift_high_tension_nudges_caution_up() -> None:
    base = {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5}
    tensions = [{"severity": 0.9}]
    result = drift_baseline(base, tensions)
    assert result["caution_bias"] > 0.5


# ── update_soul_integral() ──────────────────────────────────────


def test_soul_integral_accumulates() -> None:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    result = update_soul_integral(0.0, now, [{"severity": 0.7}])
    assert result == pytest.approx(0.7, abs=0.01)


def test_soul_integral_decays_old() -> None:
    result = update_soul_integral(10.0, "2020-01-01T00:00:00+00:00", [])
    assert result < 0.01  # years of decay


# ── summary() ───────────────────────────────────────────────────


def test_summary_contains_key_sections() -> None:
    posture = GovernancePosture(
        soul_integral=1.23,
        session_count=5,
        active_vows=[{"id": "v1", "content": "be good"}],
    )
    text = summary(posture)
    assert "Soul Integral" in text
    assert "Sessions: 5" in text
    assert "be good" in text
    assert "Active Vows (1)" in text


# ── GovernancePosture round-trip ────────────────────────────────


def test_posture_round_trip() -> None:
    p = GovernancePosture(soul_integral=3.14, session_count=7)
    d = p.to_dict()
    p2 = GovernancePosture.from_dict(d)
    assert p2.soul_integral == 3.14
    assert p2.session_count == 7


# ── SessionTrace ────────────────────────────────────────────────


def test_session_trace_auto_id() -> None:
    t = SessionTrace(agent="test")
    assert len(t.session_id) > 0
    assert t.timestamp != ""
