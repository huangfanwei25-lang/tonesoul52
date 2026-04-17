"""FileStore — JSON-file backend (current behavior, zero dependencies).

Stores:
  governance_state.json          → governance posture
  memory/autonomous/session_traces.jsonl → append-only trace log
  memory/autonomous/zone_registry.json   → zone map

Pub/sub: no-op (world map falls back to file-mtime polling).
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from time import time as _time
from typing import Any, Dict, Iterator, List

_ROOT = Path(__file__).resolve().parent.parent.parent  # repo root

_DEFAULT_GOV = _ROOT / "governance_state.json"
_DEFAULT_TRACES = _ROOT / "memory" / "autonomous" / "session_traces.jsonl"
_DEFAULT_ZONES = _ROOT / "memory" / "autonomous" / "zone_registry.json"
_DEFAULT_CLAIMS = _ROOT / ".aegis" / "task_claims.json"
_DEFAULT_COMMIT_LOCK = _ROOT / ".aegis" / "commit.lock.json"
_DEFAULT_PERSPECTIVES = _ROOT / ".aegis" / "perspectives.json"
_DEFAULT_CHECKPOINTS = _ROOT / ".aegis" / "checkpoints.json"
_DEFAULT_COMPACTIONS = _ROOT / ".aegis" / "compacted.json"
_DEFAULT_SUBJECT_SNAPSHOTS = _ROOT / ".aegis" / "subject_snapshots.json"
_DEFAULT_OBSERVER_CURSORS = _ROOT / ".aegis" / "observer_cursors.json"
_DEFAULT_ROUTING_EVENTS = _ROOT / ".aegis" / "routing_events.json"
_DEFAULT_COUNCIL_VERDICTS = _ROOT / ".aegis" / "council_verdicts.json"


class FileStore:
    """JSON/JSONL file backend. Thread-safe for single-writer scenarios."""

    def __init__(
        self,
        gov_path: Path | None = None,
        traces_path: Path | None = None,
        zones_path: Path | None = None,
        claims_path: Path | None = None,
        commit_lock_path: Path | None = None,
        perspectives_path: Path | None = None,
        checkpoints_path: Path | None = None,
        compactions_path: Path | None = None,
        subject_snapshots_path: Path | None = None,
        observer_cursors_path: Path | None = None,
        routing_events_path: Path | None = None,
        council_verdicts_path: Path | None = None,
    ) -> None:
        self.gov_path = gov_path or _DEFAULT_GOV
        self.traces_path = traces_path or _DEFAULT_TRACES
        self.zones_path = zones_path or _DEFAULT_ZONES
        self.claims_path = claims_path or _DEFAULT_CLAIMS
        self.commit_lock_path = commit_lock_path or _DEFAULT_COMMIT_LOCK
        self.perspectives_path = perspectives_path or _DEFAULT_PERSPECTIVES
        self.checkpoints_path = checkpoints_path or _DEFAULT_CHECKPOINTS
        self.compactions_path = compactions_path or _DEFAULT_COMPACTIONS
        self.subject_snapshots_path = subject_snapshots_path or _DEFAULT_SUBJECT_SNAPSHOTS
        self.observer_cursors_path = observer_cursors_path or _DEFAULT_OBSERVER_CURSORS
        self.routing_events_path = routing_events_path or (
            self.claims_path.with_name("routing_events.json")
            if claims_path is not None
            else _DEFAULT_ROUTING_EVENTS
        )
        self.council_verdicts_path = council_verdicts_path or (
            self.claims_path.with_name("council_verdicts.json")
            if claims_path is not None
            else _DEFAULT_COUNCIL_VERDICTS
        )

    # ── Governance state ────────────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        return self._read_json_file(self.gov_path)

    def set_state(self, data: Dict[str, Any]) -> None:
        self._atomic_write_text(
            self.gov_path,
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        )

    # ── Session traces ───────────────────────────────────────────────────────

    def append_trace(self, trace: Dict[str, Any]) -> None:
        self.traces_path.parent.mkdir(parents=True, exist_ok=True)
        with self.traces_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def get_traces(self, n: int = 100) -> List[Dict[str, Any]]:
        if not self.traces_path.exists():
            return []
        lines = self.traces_path.read_text(encoding="utf-8").splitlines()
        result = []
        for line in lines[-n:]:
            line = line.strip()
            if line:
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return result

    # ── Zone registry ────────────────────────────────────────────────────────

    def get_zones(self) -> Dict[str, Any]:
        return self._read_json_file(self.zones_path)

    def set_zones(self, data: Dict[str, Any]) -> None:
        self._atomic_write_text(
            self.zones_path,
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        )

    # ── Pub/sub (no-op) ──────────────────────────────────────────────────────

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        pass  # World map uses file-mtime polling as fallback

    def subscribe(self, channel: str) -> Iterator[Dict[str, Any]]:
        return iter([])  # no-op

    # ── Task claims / locks ────────────────────────────────────────────────

    def claim_lock(self, task_id: str, claim: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        claims = self._read_claims()
        self._purge_expired_claims(claims)
        existing = claims.get(task_id)
        if existing:
            if str(existing.get("agent", "")) != str(claim.get("agent", "")):
                return False
        entry = dict(claim)
        entry["task_id"] = task_id
        entry["ttl_seconds"] = int(ttl_seconds)
        claims[task_id] = entry
        self._write_claims(claims)
        return True

    def release_lock(self, task_id: str, agent_id: str | None = None) -> bool:
        claims = self._read_claims()
        self._purge_expired_claims(claims)
        existing = claims.get(task_id)
        if not existing:
            return False
        if agent_id and str(existing.get("agent", "")) != str(agent_id):
            return False
        del claims[task_id]
        self._write_claims(claims)
        return True

    def list_locks(self) -> List[Dict[str, Any]]:
        claims = self._read_claims()
        self._purge_expired_claims(claims)
        self._write_claims(claims)
        return [claims[key] for key in sorted(claims)]

    def _read_claims(self) -> Dict[str, Dict[str, Any]]:
        if not self.claims_path.exists():
            return {}
        try:
            raw = json.loads(self.claims_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        if not isinstance(raw, dict):
            return {}
        result: Dict[str, Dict[str, Any]] = {}
        for key, value in raw.items():
            if isinstance(key, str) and isinstance(value, dict):
                result[key] = dict(value)
        return result

    def _write_claims(self, claims: Dict[str, Dict[str, Any]]) -> None:
        self._atomic_write_text(
            self.claims_path,
            json.dumps(claims, indent=2, ensure_ascii=False) + "\n",
        )

    def _purge_expired_entries(self, claims: Dict[str, Dict[str, Any]]) -> None:
        to_delete: List[str] = []
        for task_id, claim in claims.items():
            expires_at = str(claim.get("expires_at", "")).strip()
            if not expires_at:
                continue
            try:
                expires_ts = float(expires_at)
            except ValueError:
                continue
            if expires_ts <= 0:
                continue
            if expires_ts <= _time():
                to_delete.append(task_id)
        for task_id in to_delete:
            claims.pop(task_id, None)

    def _purge_expired_claims(self, claims: Dict[str, Dict[str, Any]]) -> None:
        self._purge_expired_entries(claims)

    # Canonical commit mutex

    def acquire_commit_lock(self, owner: str, ttl_seconds: int = 30) -> str | None:
        token = f"{owner}:{uuid.uuid4()}"
        payload = {
            "owner": owner,
            "token": token,
            "expires_at": _time() + float(ttl_seconds),
        }
        self.commit_lock_path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                with self.commit_lock_path.open("x", encoding="utf-8") as handle:
                    handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                return token
            except FileExistsError:
                existing = self._read_json_file(self.commit_lock_path)
                expires_at = float(existing.get("expires_at", 0.0) or 0.0)
                if expires_at and expires_at <= _time():
                    try:
                        self.commit_lock_path.unlink()
                    except FileNotFoundError:
                        pass
                    continue
                return None
        return None

    def release_commit_lock(self, token: str) -> bool:
        raw = self._read_json_file(self.commit_lock_path)
        if not raw:
            return False
        if str(raw.get("token", "")) != str(token):
            return False
        try:
            self.commit_lock_path.unlink()
        except FileNotFoundError:
            return False
        return True

    # Perspective and checkpoint lanes

    def set_perspective(
        self,
        agent_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 7200,
    ) -> None:
        perspectives = self._read_registry(self.perspectives_path)
        entry = dict(data)
        entry["agent"] = agent_id
        entry["expires_at"] = str(_time() + float(ttl_seconds))
        perspectives[agent_id] = entry
        self._purge_expired_entries(perspectives)
        self._write_registry(self.perspectives_path, perspectives)

    def list_perspectives(self) -> List[Dict[str, Any]]:
        perspectives = self._read_registry(self.perspectives_path)
        self._purge_expired_entries(perspectives)
        self._write_registry(self.perspectives_path, perspectives)
        return [perspectives[key] for key in sorted(perspectives)]

    def set_checkpoint(
        self,
        checkpoint_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 86400,
    ) -> None:
        checkpoints = self._read_registry(self.checkpoints_path)
        entry = dict(data)
        entry["checkpoint_id"] = checkpoint_id
        entry["expires_at"] = str(_time() + float(ttl_seconds))
        checkpoints[checkpoint_id] = entry
        self._purge_expired_entries(checkpoints)
        self._write_registry(self.checkpoints_path, checkpoints)

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        checkpoints = self._read_registry(self.checkpoints_path)
        self._purge_expired_entries(checkpoints)
        self._write_registry(self.checkpoints_path, checkpoints)
        return sorted(
            checkpoints.values(),
            key=lambda item: str(item.get("updated_at", "")),
            reverse=True,
        )

    def append_compaction(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 20,
        ttl_seconds: int = 604800,
    ) -> None:
        compactions = self._read_list_registry(self.compactions_path)
        self._purge_expired_list_entries(compactions)
        entry = dict(data)
        if ttl_seconds > 0:
            entry["expires_at"] = str(_time() + float(ttl_seconds))
        compactions.insert(0, entry)
        if limit > 0:
            compactions = compactions[: int(limit)]
        self._write_list_registry(self.compactions_path, compactions)

    def get_compactions(self, n: int = 5) -> List[Dict[str, Any]]:
        compactions = self._read_list_registry(self.compactions_path)
        self._purge_expired_list_entries(compactions)
        self._write_list_registry(self.compactions_path, compactions)
        return compactions[: max(0, int(n))]

    def append_subject_snapshot(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 12,
        ttl_seconds: int = 2592000,
    ) -> None:
        snapshots = self._read_list_registry(self.subject_snapshots_path)
        self._purge_expired_list_entries(snapshots)
        entry = dict(data)
        if ttl_seconds > 0:
            entry["expires_at"] = str(_time() + float(ttl_seconds))
        snapshots.insert(0, entry)
        if limit > 0:
            snapshots = snapshots[: int(limit)]
        self._write_list_registry(self.subject_snapshots_path, snapshots)

    def get_subject_snapshots(self, n: int = 3) -> List[Dict[str, Any]]:
        snapshots = self._read_list_registry(self.subject_snapshots_path)
        self._purge_expired_list_entries(snapshots)
        self._write_list_registry(self.subject_snapshots_path, snapshots)
        return snapshots[: max(0, int(n))]

    def set_observer_cursor(
        self,
        agent_id: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: int = 2592000,
    ) -> None:
        cursors = self._read_registry(self.observer_cursors_path)
        entry = dict(data)
        entry["agent"] = agent_id
        entry["expires_at"] = str(_time() + float(ttl_seconds))
        cursors[agent_id] = entry
        self._purge_expired_entries(cursors)
        self._write_registry(self.observer_cursors_path, cursors)

    def get_observer_cursor(self, agent_id: str) -> Dict[str, Any]:
        cursors = self._read_registry(self.observer_cursors_path)
        self._purge_expired_entries(cursors)
        self._write_registry(self.observer_cursors_path, cursors)
        return dict(cursors.get(agent_id) or {})

    def append_routing_event(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 50,
        ttl_seconds: int = 1209600,
    ) -> None:
        events = self._read_list_registry(self.routing_events_path)
        self._purge_expired_list_entries(events)
        entry = dict(data)
        if ttl_seconds > 0:
            entry["expires_at"] = str(_time() + float(ttl_seconds))
        events.insert(0, entry)
        if limit > 0:
            events = events[: int(limit)]
        self._write_list_registry(self.routing_events_path, events)

    def get_routing_events(self, n: int = 10) -> List[Dict[str, Any]]:
        events = self._read_list_registry(self.routing_events_path)
        self._purge_expired_list_entries(events)
        self._write_list_registry(self.routing_events_path, events)
        return events[: max(0, int(n))]

    def append_council_verdict(
        self,
        data: Dict[str, Any],
        *,
        limit: int = 1000,
        ttl_seconds: int = 7776000,
    ) -> None:
        verdicts = self._read_list_registry(self.council_verdicts_path)
        self._purge_expired_list_entries(verdicts)
        entry = dict(data)
        if ttl_seconds > 0:
            entry["expires_at"] = str(_time() + float(ttl_seconds))
        verdicts.insert(0, entry)
        if limit > 0:
            verdicts = verdicts[: int(limit)]
        self._write_list_registry(self.council_verdicts_path, verdicts)

    def get_council_verdicts(self, n: int = 25) -> List[Dict[str, Any]]:
        verdicts = self._read_list_registry(self.council_verdicts_path)
        self._purge_expired_list_entries(verdicts)
        self._write_list_registry(self.council_verdicts_path, verdicts)
        return verdicts[: max(0, int(n))]

    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[WARN] Ignoring corrupt JSON store file {path}: {exc}", file=sys.stderr)
            return {}
        return raw if isinstance(raw, dict) else {}

    def _read_registry(self, path: Path) -> Dict[str, Dict[str, Any]]:
        raw = self._read_json_file(path)
        result: Dict[str, Dict[str, Any]] = {}
        for key, value in raw.items():
            if isinstance(key, str) and isinstance(value, dict):
                result[key] = dict(value)
        return result

    def _read_list_registry(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(raw, list):
            return []
        result: List[Dict[str, Any]] = []
        for item in raw:
            if isinstance(item, dict):
                result.append(dict(item))
        return result

    def _write_registry(self, path: Path, values: Dict[str, Dict[str, Any]]) -> None:
        self._atomic_write_text(
            path,
            json.dumps(values, indent=2, ensure_ascii=False) + "\n",
        )

    def _write_list_registry(self, path: Path, values: List[Dict[str, Any]]) -> None:
        self._atomic_write_text(
            path,
            json.dumps(values, indent=2, ensure_ascii=False) + "\n",
        )

    def _purge_expired_list_entries(self, values: List[Dict[str, Any]]) -> None:
        kept: List[Dict[str, Any]] = []
        for item in values:
            expires_at = str(item.get("expires_at", "")).strip()
            if not expires_at:
                kept.append(item)
                continue
            try:
                expires_ts = float(expires_at)
            except ValueError:
                kept.append(item)
                continue
            if expires_ts <= 0 or expires_ts > _time():
                kept.append(item)
        values[:] = kept

    # ── Backend info ─────────────────────────────────────────────────────────

    def _atomic_write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass

    @property
    def backend_name(self) -> str:
        return "file"

    @property
    def is_redis(self) -> bool:
        return False
