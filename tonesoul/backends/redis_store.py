"""RedisStore — Redis backend for ToneSoul governance state.

Keys:
  ts:governance   STRING  JSON of GovernancePosture
  ts:zones        STRING  JSON of ZoneRegistry
  ts:traces       STREAM  append-only session traces (XADD / XRANGE)

Pub/sub:
  ts:events       CHANNEL  {"type": "governance:updated" | "zones:updated"}

World map subscribes to ts:events and gets zero-latency push instead of polling.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Iterator, List

from tonesoul.store_keys import (
    CHANNEL_EVENTS,
    CHECKPOINT_PREFIX,
    COMMIT_LOCK_KEY,
    KEY_COMPACTED,
    KEY_COUNCIL_VERDICTS,
    KEY_GOVERNANCE,
    KEY_ROUTING_EVENTS,
    KEY_SUBJECT_SNAPSHOTS,
    KEY_ZONES,
    LOCK_PREFIX,
    OBSERVER_CURSOR_PREFIX,
    PERSPECTIVE_PREFIX,
    STREAM_TRACES,
)


class RedisStore:
    """Redis-backed store. Pass a connected `redis.Redis` client."""

    def __init__(self, client) -> None:
        self._r = client

    # ── Governance state ────────────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        raw = self._r.get(KEY_GOVERNANCE)
        if raw is None:
            return {}
        return json.loads(raw)

    def set_state(self, data: Dict[str, Any]) -> None:
        self._r.set(KEY_GOVERNANCE, json.dumps(data, ensure_ascii=False))
        self.publish(CHANNEL_EVENTS, {"type": "governance:updated"})

    # ── Session traces (Redis Stream) ────────────────────────────────────────

    def append_trace(self, trace: Dict[str, Any]) -> None:
        """Append to Redis Stream — ordered, appendonly, queryable by time."""
        self._r.xadd(
            STREAM_TRACES,
            {"data": json.dumps(trace, ensure_ascii=False)},
        )

    def get_traces(self, n: int = 100) -> List[Dict[str, Any]]:
        """Read last n traces from stream."""
        entries = self._r.xrevrange(STREAM_TRACES, count=n)
        result = []
        for _msg_id, fields in reversed(entries):
            raw = fields.get(b"data") or fields.get("data", "")
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            try:
                result.append(json.loads(raw))
            except json.JSONDecodeError:
                pass
        return result

    # ── Zone registry ────────────────────────────────────────────────────────

    def get_zones(self) -> Dict[str, Any]:
        raw = self._r.get(KEY_ZONES)
        if raw is None:
            return {}
        return json.loads(raw)

    def set_zones(self, data: Dict[str, Any]) -> None:
        self._r.set(KEY_ZONES, json.dumps(data, ensure_ascii=False))
        self.publish(CHANNEL_EVENTS, {"type": "zones:updated"})

    # ── Task claims / locks ────────────────────────────────────────────────

    _CLAIM_LOCK_SCRIPT = """
local key = KEYS[1]
local new_payload = ARGV[1]
local new_agent = ARGV[2]
local ttl = tonumber(ARGV[3])
local existing = redis.call('GET', key)
if existing then
    local data = cjson.decode(existing)
    if data['agent'] ~= new_agent then
        return 0
    end
end
redis.call('SET', key, new_payload, 'EX', ttl)
return 1
"""

    def claim_lock(self, task_id: str, claim: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        key = f"{LOCK_PREFIX}{task_id}"
        entry = dict(claim)
        entry["task_id"] = task_id
        entry["ttl_seconds"] = int(ttl_seconds)
        payload = json.dumps(entry, ensure_ascii=False)
        agent = str(claim.get("agent", ""))
        try:
            result = self._r.eval(self._CLAIM_LOCK_SCRIPT, 1, key, payload, agent, int(ttl_seconds))
        except Exception:
            # Fallback for environments where EVAL is disabled
            existing_raw = self._r.get(key)
            if existing_raw is not None:
                existing = json.loads(existing_raw)
                if str(existing.get("agent", "")) != agent:
                    return False
            self._r.set(key, payload, ex=int(ttl_seconds))
            result = 1
        if result:
            self.publish(CHANNEL_EVENTS, {"type": "claims:updated", "task_id": task_id})
        return bool(result)

    def release_lock(self, task_id: str, agent_id: str | None = None) -> bool:
        key = f"{LOCK_PREFIX}{task_id}"
        existing_raw = self._r.get(key)
        if existing_raw is None:
            return False
        existing = json.loads(existing_raw)
        if agent_id and str(existing.get("agent", "")) != str(agent_id):
            return False
        deleted = self._r.delete(key)
        if deleted:
            self.publish(CHANNEL_EVENTS, {"type": "claims:updated", "task_id": task_id})
        return bool(deleted)

    def list_locks(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for key in self._r.scan_iter(f"{LOCK_PREFIX}*"):
            raw = self._r.get(key)
            if raw is None:
                continue
            try:
                result.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        result.sort(key=lambda item: str(item.get("task_id", "")))
        return result

    # Canonical commit mutex

    def acquire_commit_lock(self, owner: str, ttl_seconds: int = 30) -> str | None:
        token = f"{owner}:{uuid.uuid4()}"
        acquired = self._r.set(COMMIT_LOCK_KEY, token, ex=int(ttl_seconds), nx=True)
        return token if acquired else None

    def release_commit_lock(self, token: str) -> bool:
        script = """
local raw = redis.call('GET', KEYS[1])
if not raw then
  return 0
end
if raw == ARGV[1] then
  redis.call('DEL', KEYS[1])
  return 1
end
return 0
"""
        try:
            released = self._r.eval(script, 1, COMMIT_LOCK_KEY, token)
        except Exception:
            raw = self._r.get(COMMIT_LOCK_KEY)
            if raw is None:
                return False
            text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            if text != token:
                return False
            released = self._r.delete(COMMIT_LOCK_KEY)
        return bool(released)

    # Perspective and checkpoint lanes

    def set_perspective(
        self,
        agent_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 7200,
    ) -> None:
        key = f"{PERSPECTIVE_PREFIX}{agent_id}"
        self._r.set(key, json.dumps(data, ensure_ascii=False), ex=int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "perspectives:updated", "agent": agent_id})

    def list_perspectives(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for key in self._r.scan_iter(f"{PERSPECTIVE_PREFIX}*"):
            raw = self._r.get(key)
            if raw is None:
                continue
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        result.sort(key=lambda item: str(item.get("agent", "")))
        return result

    def set_checkpoint(
        self,
        checkpoint_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 86400,
    ) -> None:
        key = f"{CHECKPOINT_PREFIX}{checkpoint_id}"
        self._r.set(key, json.dumps(data, ensure_ascii=False), ex=int(ttl_seconds))
        self.publish(
            CHANNEL_EVENTS, {"type": "checkpoints:updated", "checkpoint_id": checkpoint_id}
        )

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for key in self._r.scan_iter(f"{CHECKPOINT_PREFIX}*"):
            raw = self._r.get(key)
            if raw is None:
                continue
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        result.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
        return result

    def append_compaction(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 20,
        ttl_seconds: int = 604800,
    ) -> None:
        self._r.lpush(KEY_COMPACTED, json.dumps(data, ensure_ascii=False))
        self._r.ltrim(KEY_COMPACTED, 0, max(0, int(limit) - 1))
        if ttl_seconds > 0:
            self._r.expire(KEY_COMPACTED, int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "compactions:updated"})

    def get_compactions(self, n: int = 5) -> List[Dict[str, Any]]:
        raw_list = self._r.lrange(KEY_COMPACTED, 0, max(0, int(n) - 1))
        result: List[Dict[str, Any]] = []
        for raw in raw_list:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        return result

    def append_subject_snapshot(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 12,
        ttl_seconds: int = 2592000,
    ) -> None:
        self._r.lpush(KEY_SUBJECT_SNAPSHOTS, json.dumps(data, ensure_ascii=False))
        self._r.ltrim(KEY_SUBJECT_SNAPSHOTS, 0, max(0, int(limit) - 1))
        if ttl_seconds > 0:
            self._r.expire(KEY_SUBJECT_SNAPSHOTS, int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "subject_snapshots:updated"})

    def get_subject_snapshots(self, n: int = 3) -> List[Dict[str, Any]]:
        raw_list = self._r.lrange(KEY_SUBJECT_SNAPSHOTS, 0, max(0, int(n) - 1))
        result: List[Dict[str, Any]] = []
        for raw in raw_list:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        return result

    def set_observer_cursor(
        self,
        agent_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 2592000,
    ) -> None:
        key = f"{OBSERVER_CURSOR_PREFIX}{agent_id}"
        self._r.set(key, json.dumps(data, ensure_ascii=False), ex=int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "observer_cursor:updated", "agent": agent_id})

    def get_observer_cursor(self, agent_id: str) -> Dict[str, Any]:
        key = f"{OBSERVER_CURSOR_PREFIX}{agent_id}"
        raw = self._r.get(key)
        if raw is None:
            return {}
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def append_routing_event(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 50,
        ttl_seconds: int = 1209600,
    ) -> None:
        self._r.lpush(KEY_ROUTING_EVENTS, json.dumps(data, ensure_ascii=False))
        self._r.ltrim(KEY_ROUTING_EVENTS, 0, max(0, int(limit) - 1))
        if ttl_seconds > 0:
            self._r.expire(KEY_ROUTING_EVENTS, int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "routing_events:updated"})

    def get_routing_events(self, n: int = 10) -> List[Dict[str, Any]]:
        raw_list = self._r.lrange(KEY_ROUTING_EVENTS, 0, max(0, int(n) - 1))
        result: List[Dict[str, Any]] = []
        for raw in raw_list:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        return result

    def append_council_verdict(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 1000,
        ttl_seconds: int = 7776000,
    ) -> None:
        self._r.lpush(KEY_COUNCIL_VERDICTS, json.dumps(data, ensure_ascii=False))
        self._r.ltrim(KEY_COUNCIL_VERDICTS, 0, max(0, int(limit) - 1))
        if ttl_seconds > 0:
            self._r.expire(KEY_COUNCIL_VERDICTS, int(ttl_seconds))
        self.publish(CHANNEL_EVENTS, {"type": "council_verdicts:updated"})

    def get_council_verdicts(self, n: int = 25) -> List[Dict[str, Any]]:
        raw_list = self._r.lrange(KEY_COUNCIL_VERDICTS, 0, max(0, int(n) - 1))
        result: List[Dict[str, Any]] = []
        for raw in raw_list:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            try:
                result.append(json.loads(text))
            except json.JSONDecodeError:
                continue
        return result

    # ── Pub/sub ──────────────────────────────────────────────────────────────

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        self._r.publish(channel, json.dumps(message, ensure_ascii=False))

    def subscribe(self, channel: str) -> Iterator[Dict[str, Any]]:
        """Blocking iterator — yields messages as dicts."""
        pubsub = self._r.pubsub()
        pubsub.subscribe(channel)
        for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    yield json.loads(msg["data"])
                except (json.JSONDecodeError, TypeError):
                    pass

    # ── Migrate from FileStore ───────────────────────────────────────────────

    def import_from_file_store(self, file_store) -> dict:
        """One-time migration: copy JSON files into Redis.

        Returns summary of what was imported.
        """
        imported = {}

        state = file_store.get_state()
        if state:
            self.set_state(state)
            imported["governance"] = True

        zones = file_store.get_zones()
        if zones:
            self.set_zones(zones)
            imported["zones"] = True

        traces = file_store.get_traces(n=10000)
        if traces:
            for t in traces:
                self.append_trace(t)
            imported["traces"] = len(traces)

        return imported

    # ── Backend info ─────────────────────────────────────────────────────────

    @property
    def backend_name(self) -> str:
        return "redis"

    @property
    def is_redis(self) -> bool:
        return True
