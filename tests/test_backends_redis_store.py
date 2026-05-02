"""Tests for tonesoul.backends.redis_store using a mock Redis client."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List
from unittest.mock import MagicMock

from tonesoul.backends.redis_store import RedisStore

# ── In-memory fake Redis ──────────────────────────────────────────────────────


class FakeRedis:
    """Minimal in-memory Redis stand-in for unit testing RedisStore."""

    def __init__(self):
        self._kv: Dict[str, Any] = {}
        self._lists: Dict[str, list] = defaultdict(list)
        self._streams: Dict[str, list] = defaultdict(list)
        self._published: List[tuple] = []
        self._eval_results: Dict[str, Any] = {}

    # string ops
    def get(self, key):
        v = self._kv.get(key)
        return v.encode("utf-8") if isinstance(v, str) else v

    def set(self, key, value, ex=None, nx=False):
        if nx and key in self._kv:
            return None
        self._kv[key] = value
        return True

    def delete(self, key):
        existed = key in self._kv
        self._kv.pop(key, None)
        return 1 if existed else 0

    # list ops
    def lpush(self, key, *values):
        for v in values:
            self._lists[key].insert(0, v)
        return len(self._lists[key])

    def ltrim(self, key, start, end):
        lst = self._lists[key]
        self._lists[key] = lst[start : end + 1]

    def lrange(self, key, start, end):
        lst = self._lists[key]
        if end == -1:
            return lst[start:]
        return lst[start : end + 1]

    # stream ops
    def xadd(self, stream, fields):
        entry_id = f"{len(self._streams[stream])}-0"
        self._streams[stream].append((entry_id, fields))
        return entry_id

    def xrevrange(self, stream, count=None):
        entries = list(reversed(self._streams[stream]))
        if count is not None:
            entries = entries[:count]
        return [(eid, f) for eid, f in entries]

    # scan
    def scan_iter(self, pattern):
        prefix = pattern.rstrip("*")
        return [k for k in list(self._kv.keys()) if k.startswith(prefix)]

    # expire (no-op for testing)
    def expire(self, key, seconds):
        pass

    # pub/sub
    def publish(self, channel, message):
        self._published.append((channel, message))

    def pubsub(self):
        ps = MagicMock()
        ps.listen.return_value = []
        return ps

    # eval (used by claim_lock / release_commit_lock)
    def eval(self, script, numkeys, *args):
        raise Exception("eval disabled in fake")


def _store() -> tuple[RedisStore, FakeRedis]:
    fake = FakeRedis()
    return RedisStore(fake), fake


# ── Backend properties ────────────────────────────────────────────────────────


class TestRedisStoreBackendProperties:
    def test_backend_name_is_redis(self):
        store, _ = _store()
        assert store.backend_name == "redis"

    def test_is_redis_true(self):
        store, _ = _store()
        assert store.is_redis is True


# ── Governance state ──────────────────────────────────────────────────────────


class TestRedisStoreGovernanceState:
    def test_get_state_empty_returns_empty_dict(self):
        store, _ = _store()
        assert store.get_state() == {}

    def test_set_and_get_state_round_trip(self):
        store, _ = _store()
        state = {"readiness": "ready", "drift": 0.1}
        store.set_state(state)
        assert store.get_state() == state

    def test_set_state_publishes_event(self):
        store, fake = _store()
        store.set_state({"key": "value"})
        assert any("governance:updated" in str(m) for _, m in fake._published)

    def test_set_state_overwrites_previous(self):
        store, _ = _store()
        store.set_state({"v": 1})
        store.set_state({"v": 2})
        assert store.get_state()["v"] == 2


# ── Zones ─────────────────────────────────────────────────────────────────────


class TestRedisStoreZones:
    def test_get_zones_empty_returns_empty_dict(self):
        store, _ = _store()
        assert store.get_zones() == {}

    def test_set_and_get_zones(self):
        store, _ = _store()
        zones = {"zone_alpha": {"name": "Alpha"}, "zone_beta": {"name": "Beta"}}
        store.set_zones(zones)
        assert store.get_zones() == zones

    def test_set_zones_publishes_event(self):
        store, fake = _store()
        store.set_zones({"z": {}})
        assert any("zones:updated" in str(m) for _, m in fake._published)


# ── Traces (stream) ───────────────────────────────────────────────────────────


class TestRedisStoreTraces:
    def test_append_and_get_traces(self):
        store, _ = _store()
        store.append_trace({"session_id": "s1", "topic": "governance"})
        traces = store.get_traces()
        assert len(traces) == 1
        assert traces[0]["session_id"] == "s1"

    def test_traces_ordered_oldest_first(self):
        store, _ = _store()
        store.append_trace({"order": 1})
        store.append_trace({"order": 2})
        traces = store.get_traces()
        assert traces[0]["order"] == 1
        assert traces[1]["order"] == 2

    def test_get_traces_respects_n_limit(self):
        store, _ = _store()
        for i in range(10):
            store.append_trace({"i": i})
        traces = store.get_traces(n=3)
        assert len(traces) <= 3

    def test_malformed_trace_skipped(self):
        store, fake = _store()
        fake._streams["ts:traces"].append(("0-0", {"data": "not-json{{{"}))
        store.append_trace({"valid": True})
        traces = store.get_traces()
        # Only the valid entry should be returned
        assert all("valid" in t for t in traces)


# ── Compactions ───────────────────────────────────────────────────────────────


class TestRedisStoreCompactions:
    def test_append_and_get_compaction(self):
        store, _ = _store()
        store.append_compaction({"summary": "session closed"})
        result = store.get_compactions()
        assert len(result) == 1
        assert result[0]["summary"] == "session closed"

    def test_compaction_limit_enforced(self):
        store, _ = _store()
        for i in range(25):
            store.append_compaction({"i": i}, limit=5)
        result = store.get_compactions(n=100)
        assert len(result) <= 5

    def test_compaction_publishes_event(self):
        store, fake = _store()
        store.append_compaction({"x": 1})
        assert any("compactions:updated" in str(m) for _, m in fake._published)


# ── Subject snapshots ─────────────────────────────────────────────────────────


class TestRedisStoreSubjectSnapshots:
    def test_append_and_get_snapshot(self):
        store, _ = _store()
        store.append_subject_snapshot({"subject": "drift", "status": "stable"})
        result = store.get_subject_snapshots()
        assert len(result) == 1
        assert result[0]["subject"] == "drift"

    def test_snapshot_limit_enforced(self):
        store, _ = _store()
        for i in range(20):
            store.append_subject_snapshot({"i": i}, limit=3)
        result = store.get_subject_snapshots(n=100)
        assert len(result) <= 3


# ── Observer cursor ───────────────────────────────────────────────────────────


class TestRedisStoreObserverCursor:
    def test_set_and_get_cursor(self):
        store, _ = _store()
        store.set_observer_cursor("agent-1", {"last_id": "42-0"})
        cursor = store.get_observer_cursor("agent-1")
        assert cursor["last_id"] == "42-0"

    def test_get_missing_cursor_returns_empty(self):
        store, _ = _store()
        assert store.get_observer_cursor("nonexistent") == {}

    def test_cursor_publishes_event(self):
        store, fake = _store()
        store.set_observer_cursor("agent-x", {})
        assert any("observer_cursor:updated" in str(m) for _, m in fake._published)


# ── Routing events ────────────────────────────────────────────────────────────


class TestRedisStoreRoutingEvents:
    def test_append_and_get_routing_event(self):
        store, _ = _store()
        store.append_routing_event({"surface": "claim", "claim_id": "c1"})
        result = store.get_routing_events()
        assert len(result) == 1
        assert result[0]["surface"] == "claim"

    def test_routing_event_limit_enforced(self):
        store, _ = _store()
        for i in range(60):
            store.append_routing_event({"i": i}, limit=10)
        result = store.get_routing_events(n=100)
        assert len(result) <= 10


# ── Council verdicts ──────────────────────────────────────────────────────────


class TestRedisStoreCouncilVerdicts:
    def test_append_and_get_verdict(self):
        store, _ = _store()
        store.append_council_verdict({"verdict": "approve", "coherence": 0.85})
        result = store.get_council_verdicts()
        assert len(result) == 1
        assert result[0]["verdict"] == "approve"

    def test_verdict_limit_enforced(self):
        store, _ = _store()
        for i in range(10):
            store.append_council_verdict({"i": i}, limit=3)
        result = store.get_council_verdicts(n=100)
        assert len(result) <= 3


# ── Perspectives ──────────────────────────────────────────────────────────────


class TestRedisStorePerspectives:
    def test_set_and_list_perspective(self):
        store, _ = _store()
        store.set_perspective("agent-a", {"stance": "cautious"})
        perspectives = store.list_perspectives()
        assert len(perspectives) == 1
        assert perspectives[0]["stance"] == "cautious"

    def test_multiple_perspectives_sorted_by_agent(self):
        store, _ = _store()
        store.set_perspective("agent-z", {"agent": "z"})
        store.set_perspective("agent-a", {"agent": "a"})
        perspectives = store.list_perspectives()
        agents = [p["agent"] for p in perspectives]
        assert agents == sorted(agents)


# ── Checkpoints ───────────────────────────────────────────────────────────────


class TestRedisStoreCheckpoints:
    def test_set_and_list_checkpoint(self):
        store, _ = _store()
        store.set_checkpoint("cp-1", {"phase": "864", "updated_at": "2026-04-22T00:00:00Z"})
        checkpoints = store.list_checkpoints()
        assert len(checkpoints) == 1

    def test_checkpoint_publishes_event(self):
        store, fake = _store()
        store.set_checkpoint("cp-2", {"updated_at": "2026-04-22T00:00:00Z"})
        assert any("checkpoints:updated" in str(m) for _, m in fake._published)


# ── Locks ─────────────────────────────────────────────────────────────────────


class TestRedisStoreLocks:
    def test_claim_lock_succeeds_first_time(self):
        store, _ = _store()
        result = store.claim_lock("task-1", {"agent": "claude"})
        assert result is True

    def test_claim_lock_same_agent_succeeds(self):
        store, _ = _store()
        store.claim_lock("task-1", {"agent": "claude"})
        result = store.claim_lock("task-1", {"agent": "claude"})
        assert result is True

    def test_claim_lock_different_agent_fails(self):
        store, _ = _store()
        store.claim_lock("task-1", {"agent": "claude"})
        result = store.claim_lock("task-1", {"agent": "gpt"})
        assert result is False

    def test_release_lock_succeeds(self):
        store, _ = _store()
        store.claim_lock("task-1", {"agent": "claude"})
        released = store.release_lock("task-1", agent_id="claude")
        assert released is True

    def test_release_lock_wrong_agent_fails(self):
        store, _ = _store()
        store.claim_lock("task-1", {"agent": "claude"})
        released = store.release_lock("task-1", agent_id="gpt")
        assert released is False

    def test_release_nonexistent_lock_returns_false(self):
        store, _ = _store()
        assert store.release_lock("ghost-task") is False

    def test_list_locks_returns_claimed(self):
        store, _ = _store()
        store.claim_lock("t1", {"agent": "a1"})
        store.claim_lock("t2", {"agent": "a2"})
        locks = store.list_locks()
        task_ids = [lock["task_id"] for lock in locks]
        assert "t1" in task_ids
        assert "t2" in task_ids

    def test_list_locks_excludes_released(self):
        store, _ = _store()
        store.claim_lock("t1", {"agent": "a1"})
        store.release_lock("t1", agent_id="a1")
        locks = store.list_locks()
        assert not any(lock.get("task_id") == "t1" for lock in locks)


# ── Commit lock ───────────────────────────────────────────────────────────────


class TestRedisStoreCommitLock:
    def test_acquire_commit_lock_returns_token(self):
        store, _ = _store()
        token = store.acquire_commit_lock("claude")
        assert token is not None
        assert "claude" in token

    def test_second_acquire_fails(self):
        store, _ = _store()
        store.acquire_commit_lock("claude")
        token2 = store.acquire_commit_lock("other-agent")
        assert token2 is None

    def test_release_commit_lock_allows_reacquire(self):
        store, _ = _store()
        token = store.acquire_commit_lock("claude")
        store.release_commit_lock(token)
        token2 = store.acquire_commit_lock("claude")
        assert token2 is not None

    def test_release_wrong_token_fails(self):
        store, _ = _store()
        store.acquire_commit_lock("claude")
        released = store.release_commit_lock("wrong-token")
        assert released is False


# ── Pub/sub ───────────────────────────────────────────────────────────────────


class TestRedisStorePublish:
    def test_publish_sends_to_fake(self):
        store, fake = _store()
        store.publish("ts:events", {"type": "test"})
        assert len(fake._published) == 1
        assert fake._published[0][0] == "ts:events"


# ── Import from FileStore ─────────────────────────────────────────────────────


class TestRedisStoreImportFromFileStore:
    def test_imports_state_and_zones(self):
        store, _ = _store()
        fake_file_store = MagicMock()
        fake_file_store.get_state.return_value = {"readiness": "ready"}
        fake_file_store.get_zones.return_value = {"z1": {}}
        fake_file_store.get_traces.return_value = [{"trace": 1}, {"trace": 2}]

        result = store.import_from_file_store(fake_file_store)

        assert result.get("governance") is True
        assert result.get("zones") is True
        assert result.get("traces") == 2
        assert store.get_state()["readiness"] == "ready"

    def test_empty_file_store_skips_keys(self):
        store, _ = _store()
        fake_file_store = MagicMock()
        fake_file_store.get_state.return_value = {}
        fake_file_store.get_zones.return_value = {}
        fake_file_store.get_traces.return_value = []

        result = store.import_from_file_store(fake_file_store)

        assert "governance" not in result
        assert "zones" not in result
