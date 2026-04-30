"""Tests for tonesoul.backends.file_store.FileStore."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from tonesoul.backends.file_store import FileStore

# ── Helpers ───────────────────────────────────────────────────────────────────


def _store(tmp_path: Path) -> FileStore:
    """Build a FileStore with all paths isolated to tmp_path."""
    aegis = tmp_path / ".aegis"
    return FileStore(
        gov_path=tmp_path / "gov.json",
        traces_path=tmp_path / "traces.jsonl",
        zones_path=tmp_path / "zones.json",
        claims_path=aegis / "claims.json",
        commit_lock_path=aegis / "commit.lock.json",
        perspectives_path=aegis / "perspectives.json",
        checkpoints_path=aegis / "checkpoints.json",
        compactions_path=aegis / "compacted.json",
        subject_snapshots_path=aegis / "subject_snapshots.json",
        observer_cursors_path=aegis / "observer_cursors.json",
        routing_events_path=aegis / "routing_events.json",
        council_verdicts_path=aegis / "council_verdicts.json",
    )


# ── backend_name / is_redis ───────────────────────────────────────────────────


class TestBackendInfo:
    def test_backend_name(self, tmp_path):
        assert _store(tmp_path).backend_name == "file"

    def test_is_redis_false(self, tmp_path):
        assert _store(tmp_path).is_redis is False


# ── get_state / set_state ─────────────────────────────────────────────────────


class TestGetSetState:
    def test_get_state_returns_empty_when_missing(self, tmp_path):
        s = _store(tmp_path)
        assert s.get_state() == {}

    def test_set_and_get_roundtrip(self, tmp_path):
        s = _store(tmp_path)
        data = {"version": "1.0", "soul_integral": 0.75}
        s.set_state(data)
        result = s.get_state()
        assert result["version"] == "1.0"
        assert result["soul_integral"] == pytest.approx(0.75)

    def test_set_state_overwrites(self, tmp_path):
        s = _store(tmp_path)
        s.set_state({"key": "v1"})
        s.set_state({"key": "v2"})
        assert s.get_state()["key"] == "v2"

    def test_get_state_ignores_corrupt_json(self, tmp_path, capsys):
        s = _store(tmp_path)
        s.gov_path.write_text("{not valid}", encoding="utf-8")
        result = s.get_state()
        assert result == {}
        err = capsys.readouterr().err
        assert "corrupt" in err.lower() or "Ignoring" in err

    def test_set_state_creates_parent_dirs(self, tmp_path):
        s = _store(tmp_path)
        nested = tmp_path / "a" / "b" / "gov.json"
        s.gov_path = nested
        s.set_state({"k": 1})
        assert nested.exists()

    def test_get_state_non_dict_json_gives_empty(self, tmp_path):
        s = _store(tmp_path)
        s.gov_path.write_text("[1, 2, 3]", encoding="utf-8")
        assert s.get_state() == {}


# ── append_trace / get_traces ─────────────────────────────────────────────────


class TestTraces:
    def test_get_traces_returns_empty_when_no_file(self, tmp_path):
        assert _store(tmp_path).get_traces() == []

    def test_append_and_get_trace(self, tmp_path):
        s = _store(tmp_path)
        s.append_trace({"session_id": "s1", "agent": "claude"})
        traces = s.get_traces()
        assert len(traces) == 1
        assert traces[0]["session_id"] == "s1"

    def test_multiple_traces_appended(self, tmp_path):
        s = _store(tmp_path)
        for i in range(5):
            s.append_trace({"index": i})
        traces = s.get_traces()
        assert len(traces) == 5

    def test_get_traces_respects_n_limit(self, tmp_path):
        s = _store(tmp_path)
        for i in range(10):
            s.append_trace({"i": i})
        traces = s.get_traces(n=3)
        assert len(traces) == 3

    def test_get_traces_skips_invalid_json_lines(self, tmp_path):
        s = _store(tmp_path)
        s.append_trace({"good": True})
        s.traces_path.open("a").write("not-json\n")
        traces = s.get_traces()
        assert len(traces) == 1
        assert traces[0]["good"] is True

    def test_append_creates_parent_dirs(self, tmp_path):
        s = _store(tmp_path)
        nested_traces = tmp_path / "nested" / "deeply" / "traces.jsonl"
        s.traces_path = nested_traces
        s.append_trace({"test": True})
        assert nested_traces.exists()


# ── get_zones / set_zones ─────────────────────────────────────────────────────


class TestZones:
    def test_get_zones_empty_when_no_file(self, tmp_path):
        assert _store(tmp_path).get_zones() == {}

    def test_set_and_get_zones(self, tmp_path):
        s = _store(tmp_path)
        s.set_zones({"zone_a": {"name": "Alpha"}})
        assert s.get_zones()["zone_a"]["name"] == "Alpha"


# ── publish / subscribe (no-op) ───────────────────────────────────────────────


class TestPubSub:
    def test_publish_returns_none(self, tmp_path):
        s = _store(tmp_path)
        result = s.publish("governance:updated", {"k": "v"})
        assert result is None

    def test_subscribe_returns_empty_iterator(self, tmp_path):
        s = _store(tmp_path)
        msgs = list(s.subscribe("any_channel"))
        assert msgs == []


# ── claim_lock / release_lock / list_locks ────────────────────────────────────


class TestClaimLock:
    def test_claim_lock_returns_true_for_new_claim(self, tmp_path):
        s = _store(tmp_path)
        result = s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        assert result is True

    def test_claim_appears_in_list_locks(self, tmp_path):
        s = _store(tmp_path)
        s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        locks = s.list_locks()
        assert len(locks) == 1
        assert locks[0]["task_id"] == "task-1"

    def test_same_agent_can_re_claim(self, tmp_path):
        s = _store(tmp_path)
        s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        result = s.claim_lock("task-1", {"agent": "agent-a", "summary": "updated"})
        assert result is True

    def test_different_agent_cannot_claim_existing(self, tmp_path):
        s = _store(tmp_path)
        s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        result = s.claim_lock("task-1", {"agent": "agent-b", "summary": "y"})
        assert result is False

    def test_release_lock_removes_claim(self, tmp_path):
        s = _store(tmp_path)
        s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        released = s.release_lock("task-1", agent_id="agent-a")
        assert released is True
        assert s.list_locks() == []

    def test_release_lock_wrong_agent_fails(self, tmp_path):
        s = _store(tmp_path)
        s.claim_lock("task-1", {"agent": "agent-a", "summary": "x"})
        released = s.release_lock("task-1", agent_id="agent-b")
        assert released is False

    def test_release_nonexistent_lock_returns_false(self, tmp_path):
        s = _store(tmp_path)
        assert s.release_lock("no-such-task") is False

    def test_expired_claims_purged_on_list(self, tmp_path):
        s = _store(tmp_path)
        past_time = str(time.time() - 10)
        claims = {
            "task-expired": {"agent": "a", "expires_at": past_time, "task_id": "task-expired"}
        }
        (tmp_path / ".aegis").mkdir(parents=True, exist_ok=True)
        s.claims_path.write_text(json.dumps(claims), encoding="utf-8")
        locks = s.list_locks()
        assert locks == []


# ── acquire_commit_lock / release_commit_lock ─────────────────────────────────


class TestCommitLock:
    def test_acquire_returns_token_string(self, tmp_path):
        s = _store(tmp_path)
        token = s.acquire_commit_lock("agent-a")
        assert token is not None
        assert isinstance(token, str)
        assert "agent-a" in token

    def test_acquire_second_time_returns_none(self, tmp_path):
        s = _store(tmp_path)
        s.acquire_commit_lock("agent-a")
        token2 = s.acquire_commit_lock("agent-b")
        assert token2 is None

    def test_release_with_valid_token_returns_true(self, tmp_path):
        s = _store(tmp_path)
        token = s.acquire_commit_lock("agent-a")
        assert s.release_commit_lock(token) is True

    def test_release_with_wrong_token_returns_false(self, tmp_path):
        s = _store(tmp_path)
        s.acquire_commit_lock("agent-a")
        assert s.release_commit_lock("wrong-token") is False

    def test_release_when_no_lock_returns_false(self, tmp_path):
        s = _store(tmp_path)
        assert s.release_commit_lock("any-token") is False

    def test_expired_lock_can_be_reacquired(self, tmp_path):
        s = _store(tmp_path)
        s.acquire_commit_lock("agent-a", ttl_seconds=0)
        # After TTL=0 it's immediately expired, second acquire should succeed
        token2 = s.acquire_commit_lock("agent-b")
        assert token2 is not None


# ── set_perspective / list_perspectives ──────────────────────────────────────


class TestPerspectives:
    def test_set_and_list_perspectives(self, tmp_path):
        s = _store(tmp_path)
        s.set_perspective("agent-a", {"plan": "review governance"})
        perspectives = s.list_perspectives()
        assert len(perspectives) == 1
        assert perspectives[0]["agent"] == "agent-a"

    def test_set_perspective_overwrites_same_agent(self, tmp_path):
        s = _store(tmp_path)
        s.set_perspective("agent-a", {"plan": "v1"})
        s.set_perspective("agent-a", {"plan": "v2"})
        perspectives = s.list_perspectives()
        assert len(perspectives) == 1
        assert perspectives[0]["plan"] == "v2"

    def test_multiple_agents_all_listed(self, tmp_path):
        s = _store(tmp_path)
        s.set_perspective("agent-a", {"plan": "a"})
        s.set_perspective("agent-b", {"plan": "b"})
        perspectives = s.list_perspectives()
        assert len(perspectives) == 2

    def test_expired_perspective_purged(self, tmp_path):
        s = _store(tmp_path)
        s.set_perspective("agent-a", {}, ttl_seconds=0)
        perspectives = s.list_perspectives()
        assert perspectives == []


# ── set_checkpoint / list_checkpoints ────────────────────────────────────────


class TestCheckpoints:
    def test_set_and_list_checkpoint(self, tmp_path):
        s = _store(tmp_path)
        s.set_checkpoint("cp-1", {"summary": "mid-session"})
        checkpoints = s.list_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0]["checkpoint_id"] == "cp-1"

    def test_multiple_checkpoints(self, tmp_path):
        s = _store(tmp_path)
        s.set_checkpoint("cp-1", {"s": "a"})
        s.set_checkpoint("cp-2", {"s": "b"})
        assert len(s.list_checkpoints()) == 2


# ── append_compaction / get_compactions ───────────────────────────────────────


class TestCompactions:
    def test_get_compactions_empty_when_no_file(self, tmp_path):
        assert _store(tmp_path).get_compactions() == []

    def test_append_and_get_compaction(self, tmp_path):
        s = _store(tmp_path)
        s.append_compaction({"summary": "compacted session"})
        result = s.get_compactions()
        assert len(result) == 1
        assert result[0]["summary"] == "compacted session"

    def test_latest_compaction_first(self, tmp_path):
        s = _store(tmp_path)
        s.append_compaction({"order": 1})
        s.append_compaction({"order": 2})
        result = s.get_compactions()
        assert result[0]["order"] == 2

    def test_compaction_limit_enforced(self, tmp_path):
        s = _store(tmp_path)
        for i in range(5):
            s.append_compaction({"i": i})
        result = s.get_compactions(n=3)
        assert len(result) == 3

    def test_compaction_count_capped_by_limit_param(self, tmp_path):
        s = _store(tmp_path)
        for i in range(25):
            s.append_compaction({"i": i}, limit=10)
        result = s.get_compactions(n=100)
        assert len(result) <= 10


# ── append_subject_snapshot / get_subject_snapshots ──────────────────────────


class TestSubjectSnapshots:
    def test_get_empty_when_no_file(self, tmp_path):
        assert _store(tmp_path).get_subject_snapshots() == []

    def test_append_and_retrieve(self, tmp_path):
        s = _store(tmp_path)
        s.append_subject_snapshot({"snapshot": "v1"})
        result = s.get_subject_snapshots()
        assert len(result) == 1
        assert result[0]["snapshot"] == "v1"

    def test_subject_snapshot_limit(self, tmp_path):
        s = _store(tmp_path)
        for i in range(5):
            s.append_subject_snapshot({"i": i}, limit=3)
        result = s.get_subject_snapshots(n=10)
        assert len(result) <= 3


# ── set_observer_cursor / get_observer_cursor ─────────────────────────────────


class TestObserverCursors:
    def test_get_cursor_empty_when_missing(self, tmp_path):
        s = _store(tmp_path)
        result = s.get_observer_cursor("agent-x")
        assert result == {}

    def test_set_and_get_cursor(self, tmp_path):
        s = _store(tmp_path)
        s.set_observer_cursor("agent-a", {"last_event_id": "ev-123"})
        cursor = s.get_observer_cursor("agent-a")
        assert cursor["last_event_id"] == "ev-123"

    def test_different_agents_independent_cursors(self, tmp_path):
        s = _store(tmp_path)
        s.set_observer_cursor("agent-a", {"pos": 1})
        s.set_observer_cursor("agent-b", {"pos": 2})
        assert s.get_observer_cursor("agent-a")["pos"] == 1
        assert s.get_observer_cursor("agent-b")["pos"] == 2


# ── append_routing_event / get_routing_events ─────────────────────────────────


class TestRoutingEvents:
    def test_get_empty_initially(self, tmp_path):
        assert _store(tmp_path).get_routing_events() == []

    def test_append_and_retrieve(self, tmp_path):
        s = _store(tmp_path)
        s.append_routing_event({"route": "council", "verdict": "approve"})
        events = s.get_routing_events()
        assert len(events) == 1
        assert events[0]["route"] == "council"

    def test_events_limited_by_n(self, tmp_path):
        s = _store(tmp_path)
        for i in range(5):
            s.append_routing_event({"i": i})
        assert len(s.get_routing_events(n=2)) == 2


# ── append_council_verdict / get_council_verdicts ─────────────────────────────


class TestCouncilVerdicts:
    def test_get_empty_initially(self, tmp_path):
        assert _store(tmp_path).get_council_verdicts() == []

    def test_append_and_retrieve(self, tmp_path):
        s = _store(tmp_path)
        s.append_council_verdict({"verdict": "approve", "agent": "guardian"})
        verdicts = s.get_council_verdicts()
        assert len(verdicts) == 1
        assert verdicts[0]["verdict"] == "approve"

    def test_latest_verdict_first(self, tmp_path):
        s = _store(tmp_path)
        s.append_council_verdict({"order": 1})
        s.append_council_verdict({"order": 2})
        verdicts = s.get_council_verdicts()
        assert verdicts[0]["order"] == 2

    def test_verdict_limit_n(self, tmp_path):
        s = _store(tmp_path)
        for i in range(10):
            s.append_council_verdict({"i": i})
        assert len(s.get_council_verdicts(n=3)) == 3


# ── _purge_expired_list_entries ───────────────────────────────────────────────


class TestPurgeExpiredListEntries:
    def test_expired_items_removed(self, tmp_path):
        s = _store(tmp_path)
        past = str(time.time() - 10)
        items = [
            {"data": "expired", "expires_at": past},
            {"data": "valid"},
        ]
        s._purge_expired_list_entries(items)
        assert len(items) == 1
        assert items[0]["data"] == "valid"

    def test_future_items_kept(self, tmp_path):
        s = _store(tmp_path)
        future = str(time.time() + 3600)
        items = [{"data": "future", "expires_at": future}]
        s._purge_expired_list_entries(items)
        assert len(items) == 1

    def test_items_without_expires_at_kept(self, tmp_path):
        s = _store(tmp_path)
        items = [{"data": "no_expiry"}]
        s._purge_expired_list_entries(items)
        assert len(items) == 1

    def test_invalid_expires_at_kept(self, tmp_path):
        s = _store(tmp_path)
        items = [{"data": "bad_expiry", "expires_at": "not-a-float"}]
        s._purge_expired_list_entries(items)
        assert len(items) == 1


# ── _read_list_registry edge cases ───────────────────────────────────────────


class TestReadListRegistry:
    def test_corrupt_json_returns_empty(self, tmp_path):
        s = _store(tmp_path)
        s.compactions_path.parent.mkdir(parents=True, exist_ok=True)
        s.compactions_path.write_text("{not-list}", encoding="utf-8")
        result = s._read_list_registry(s.compactions_path)
        assert result == []

    def test_non_list_json_returns_empty(self, tmp_path):
        s = _store(tmp_path)
        s.compactions_path.parent.mkdir(parents=True, exist_ok=True)
        s.compactions_path.write_text('{"key": "val"}', encoding="utf-8")
        result = s._read_list_registry(s.compactions_path)
        assert result == []

    def test_filters_non_dict_items(self, tmp_path):
        s = _store(tmp_path)
        s.compactions_path.parent.mkdir(parents=True, exist_ok=True)
        s.compactions_path.write_text('[{"ok": true}, "not-a-dict", 42]', encoding="utf-8")
        result = s._read_list_registry(s.compactions_path)
        assert len(result) == 1
        assert result[0]["ok"] is True
