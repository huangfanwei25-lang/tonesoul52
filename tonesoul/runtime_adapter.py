"""ToneSoul Runtime Adapter — the bridge that makes governance state survive across sessions and models.

Implements RFC-015 Self-Dogfooding Runtime Adapter:
- load(): session start — read governance_state.json, decay old tensions, return posture
- commit(): session end — write session trace, update governance state, drift baseline

Design principles:
1. Model-agnostic — any AI agent (Claude, Codex, Gemini) can load/commit
2. JSON in, JSON out — no markdown parsing, no model-specific formats
3. Idempotent — load() without commit() produces zero diff
4. Observable — every mutation is traceable
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants (from RFC-015 §5)
# ---------------------------------------------------------------------------

TENSION_DECAY_ALPHA = 0.05  # per hour, ~14h half-life
TENSION_PRUNE_THRESHOLD = 0.01  # drop tensions below this
DRIFT_RATE = 0.001  # 0.1% per session
SCHEMA_VERSION = "0.1.0"
R_MEMORY_PACKET_VERSION = "v1"
COMMIT_LOCK_TTL_SECONDS = 30

_DEFAULT_STATE_PATH = Path("governance_state.json")
_DEFAULT_TRACES_PATH = Path("memory/autonomous/session_traces.jsonl")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class GovernancePosture:
    """What an agent sees at session start — the living governance state."""

    version: str = SCHEMA_VERSION
    last_updated: str = ""
    soul_integral: float = 0.0
    tension_history: List[Dict[str, Any]] = field(default_factory=list)
    active_vows: List[Dict[str, Any]] = field(default_factory=list)
    aegis_vetoes: List[Dict[str, Any]] = field(default_factory=list)
    baseline_drift: Dict[str, float] = field(
        default_factory=lambda: {
            "caution_bias": 0.5,
            "innovation_bias": 0.6,
            "autonomy_level": 0.35,
        }
    )
    session_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GovernancePosture:
        return cls(
            version=str(data.get("version", SCHEMA_VERSION)),
            last_updated=str(data.get("last_updated", "")),
            soul_integral=float(data.get("soul_integral", 0.0)),
            tension_history=list(data.get("tension_history") or []),
            active_vows=list(data.get("active_vows") or []),
            aegis_vetoes=list(data.get("aegis_vetoes") or []),
            baseline_drift=dict(data.get("baseline_drift") or {}),
            session_count=int(data.get("session_count", 0)),
        )


@dataclass
class SessionTrace:
    """What an agent writes at session end — one conversation's governance record."""

    session_id: str = ""
    agent: str = "unknown"
    timestamp: str = ""
    duration_minutes: float = 0.0
    topics: List[str] = field(default_factory=list)
    tension_events: List[Dict[str, Any]] = field(default_factory=list)
    vow_events: List[Dict[str, Any]] = field(default_factory=list)
    aegis_vetoes: List[Dict[str, Any]] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    stance_shift: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = _utc_now()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d.get("stance_shift") is None:
            del d["stance_shift"]
        return d


class CommitConcurrencyError(RuntimeError):
    """Raised when canonical governance commit cannot acquire the mutex."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(iso_str: str) -> Optional[datetime]:
    """Parse ISO datetime string, tolerant of Z suffix."""
    text = str(iso_str or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _hours_since(iso_str: str) -> float:
    """Hours elapsed since the given ISO timestamp."""
    dt = _parse_dt(iso_str)
    if dt is None:
        return 0.0
    now = datetime.now(timezone.utc)
    delta = (now - dt).total_seconds() / 3600.0
    return max(0.0, delta)


# ---------------------------------------------------------------------------
# Core: tension decay (RFC-015 §5.1)
# ---------------------------------------------------------------------------


def decay_tensions(
    tensions: List[Dict[str, Any]],
    alpha: float = TENSION_DECAY_ALPHA,
    prune_threshold: float = TENSION_PRUNE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Apply exponential decay to tension history, prune negligible entries."""
    surviving: List[Dict[str, Any]] = []
    for t in tensions:
        ts = t.get("timestamp", "")
        severity = float(t.get("severity", 0.0))
        hours = _hours_since(ts)
        decayed = severity * math.exp(-alpha * hours)
        if decayed >= prune_threshold:
            entry = dict(t)
            entry["severity"] = round(decayed, 4)
            surviving.append(entry)
    return surviving


# ---------------------------------------------------------------------------
# Core: baseline drift (RFC-015 §5.2)
# ---------------------------------------------------------------------------


def drift_baseline(
    current: Dict[str, float],
    session_tensions: List[Dict[str, Any]],
    rate: float = DRIFT_RATE,
) -> Dict[str, float]:
    """Nudge baseline biases toward session experience."""
    if not session_tensions:
        return dict(current)

    avg_severity = sum(float(t.get("severity", 0.0)) for t in session_tensions) / len(
        session_tensions
    )

    # High tension sessions nudge caution up, innovation down
    new = dict(current)
    caution = float(new.get("caution_bias", 0.5))
    innovation = float(new.get("innovation_bias", 0.5))

    new["caution_bias"] = round(caution + rate * (avg_severity - caution), 4)
    new["innovation_bias"] = round(innovation + rate * ((1.0 - avg_severity) - innovation), 4)
    # autonomy_level stays put unless explicitly shifted
    return new


# ---------------------------------------------------------------------------
# Core: soul integral update (RFC-015 §5.3)
# ---------------------------------------------------------------------------


def update_soul_integral(
    current: float,
    last_updated: str,
    session_tensions: List[Dict[str, Any]],
    alpha: float = TENSION_DECAY_ALPHA,
) -> float:
    """S_new = S_old * e^(-alpha * hours) + max_tension_this_session"""
    hours = _hours_since(last_updated)
    decayed = current * math.exp(-alpha * hours)
    max_t = max((float(t.get("severity", 0.0)) for t in session_tensions), default=0.0)
    return round(decayed + max_t, 4)


# ---------------------------------------------------------------------------
# Public API: load()
# ---------------------------------------------------------------------------


def load(
    state_path: Optional[Path] = None,
    agent_id: str = "",
    source: str = "direct",
) -> GovernancePosture:
    """Load governance state at session start.

    1. Read from store (Redis or JSON file)
    2. Decay old tensions
    3. Record agent footprint (who loaded, when)
    4. Return the posture for the agent to use

    If no state exists, returns a fresh default posture.
    """
    from tonesoul.backends.file_store import FileStore
    from tonesoul.store import get_store

    # Backward-compat: if explicit path given, use FileStore with that path
    if state_path is not None:
        store = FileStore(gov_path=state_path)
    else:
        store = get_store()

    raw = store.get_state()
    if not raw:
        return GovernancePosture(last_updated=_utc_now())

    posture = GovernancePosture.from_dict(raw)
    posture.tension_history = decay_tensions(posture.tension_history)

    # Record footprint: who loaded this memory?
    if agent_id and store.is_redis:
        _record_footprint(store, agent_id, source=source)

    return posture


def _record_footprint(store, agent_id: str, *, source: str = "direct") -> None:
    """Record an agent's visit in Redis. Recent visitors visible to all."""
    try:
        import json as _json

        entry = _json.dumps(
            {
                "agent": agent_id,
                "action": "load",
                "source": source,
                "timestamp": _utc_now(),
            },
            ensure_ascii=False,
        )
        # Append to capped list (keep last 100 visits)
        store._r.lpush("ts:footprints", entry)
        store._r.ltrim("ts:footprints", 0, 99)
        # Publish presence event
        store.publish(
            "ts:events",
            {
                "type": "agent:arrived",
                "agent": agent_id,
            },
        )
    except Exception:
        pass


def get_recent_visitors(store=None, n: int = 10) -> List[Dict[str, Any]]:
    """Who has been here recently? Returns list of footprints."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    if not store.is_redis:
        return []
    try:
        raw_list = store._r.lrange("ts:footprints", 0, n - 1)
        result = []
        for raw in raw_list:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            result.append(json.loads(text))
        return result
    except Exception:
        return []


def claim_task(
    task_id: str,
    *,
    agent_id: str,
    summary: str = "",
    paths: Optional[List[str]] = None,
    source: str = "direct",
    ttl_seconds: int = 1800,
    store=None,
) -> Dict[str, Any]:
    """Claim a task lock for multi-terminal coordination."""
    task_id = str(task_id).strip()
    if not task_id:
        return {"ok": False, "task_id": "", "claim": None, "backend": "invalid"}
    if store is None:
        from tonesoul.store import get_store

        store = get_store()

    created_at = _utc_now()
    claim = {
        "task_id": task_id,
        "agent": agent_id,
        "summary": summary,
        "paths": list(paths or []),
        "source": source,
        "created_at": created_at,
        "expires_at": (
            str(_parse_dt(created_at).timestamp() + ttl_seconds) if _parse_dt(created_at) else ""
        ),
    }
    acquired = store.claim_lock(task_id, claim, ttl_seconds=ttl_seconds)
    return {
        "ok": acquired,
        "task_id": task_id,
        "claim": claim if acquired else None,
        "backend": getattr(store, "backend_name", "unknown"),
    }


def release_task_claim(task_id: str, *, agent_id: str | None = None, store=None) -> Dict[str, Any]:
    """Release a task claim. If agent_id is set, ownership must match."""
    task_id = str(task_id).strip()
    if not task_id:
        return {"ok": False, "task_id": "", "backend": "invalid"}
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    released = store.release_lock(task_id, agent_id=agent_id)
    return {
        "ok": released,
        "task_id": task_id,
        "backend": getattr(store, "backend_name", "unknown"),
    }


def list_active_claims(store=None) -> List[Dict[str, Any]]:
    """List active task claims for multi-terminal coordination."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return list(store.list_locks())
    except Exception:
        return []


def write_perspective(
    agent_id: str,
    *,
    session_id: str = "",
    summary: str = "",
    stance: str = "",
    tensions: Optional[List[str]] = None,
    proposed_drift: Optional[Dict[str, float]] = None,
    proposed_vows: Optional[List[str]] = None,
    evidence_refs: Optional[List[str]] = None,
    source: str = "direct",
    ttl_seconds: int = 7200,
    store=None,
) -> Dict[str, Any]:
    """Write a non-canonical per-agent perspective lane entry."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    payload = {
        "agent": agent_id,
        "session_id": session_id,
        "summary": summary,
        "stance": stance,
        "tensions": list(tensions or []),
        "proposed_drift": dict(proposed_drift or {}),
        "proposed_vows": list(proposed_vows or []),
        "evidence_refs": list(evidence_refs or []),
        "source": source,
        "updated_at": _utc_now(),
    }
    store.set_perspective(agent_id, payload, ttl_seconds=ttl_seconds)
    return payload


def list_perspectives(store=None) -> List[Dict[str, Any]]:
    """List active per-agent perspectives from the experimental lane."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return list(store.list_perspectives())
    except Exception:
        return []


def write_checkpoint(
    checkpoint_id: str,
    *,
    agent_id: str,
    session_id: str = "",
    summary: str = "",
    pending_paths: Optional[List[str]] = None,
    next_action: str = "",
    source: str = "direct",
    ttl_seconds: int = 86400,
    store=None,
) -> Dict[str, Any]:
    """Write a mid-session resumability checkpoint outside canonical commit."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    payload = {
        "checkpoint_id": checkpoint_id,
        "agent": agent_id,
        "session_id": session_id,
        "summary": summary,
        "pending_paths": list(pending_paths or []),
        "next_action": next_action,
        "source": source,
        "updated_at": _utc_now(),
    }
    store.set_checkpoint(checkpoint_id, payload, ttl_seconds=ttl_seconds)
    return payload


def list_checkpoints(store=None) -> List[Dict[str, Any]]:
    """List active resumability checkpoints from the experimental lane."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return list(store.list_checkpoints())
    except Exception:
        return []


def write_compaction(
    *,
    agent_id: str,
    summary: str,
    session_id: str = "",
    carry_forward: Optional[List[str]] = None,
    pending_paths: Optional[List[str]] = None,
    evidence_refs: Optional[List[str]] = None,
    next_action: str = "",
    source: str = "direct",
    ttl_seconds: int = 604800,
    limit: int = 20,
    store=None,
) -> Dict[str, Any]:
    """Write a bounded non-canonical compaction summary for resumability."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    payload = {
        "compaction_id": str(uuid.uuid4()),
        "agent": agent_id,
        "session_id": session_id,
        "summary": summary,
        "carry_forward": list(carry_forward or []),
        "pending_paths": list(pending_paths or []),
        "evidence_refs": list(evidence_refs or []),
        "next_action": next_action,
        "source": source,
        "updated_at": _utc_now(),
    }
    store.append_compaction(payload, limit=limit, ttl_seconds=ttl_seconds)
    return payload


def list_compactions(store=None, n: int = 5) -> List[Dict[str, Any]]:
    """List recent non-canonical compaction summaries."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return list(store.get_compactions(n=n))
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Public API: commit()
# ---------------------------------------------------------------------------


def commit(
    trace: SessionTrace,
    state_path: Optional[Path] = None,
    traces_path: Optional[Path] = None,
) -> GovernancePosture:
    """Commit session results at session end.

    1. Load current governance state
    2. Append new tension events
    3. Update soul integral
    4. Drift baseline
    5. Reconcile vows
    6. Write updated state  (Redis → immediate pub/sub push)
    7. Append session trace
    8. Rebuild zone registry
    9. Return the new posture
    """
    from tonesoul.backends.file_store import FileStore
    from tonesoul.store import get_store

    # Backward-compat: explicit paths → FileStore
    if state_path is not None or traces_path is not None:
        if traces_path is not None:
            base_dir = traces_path.parent
        elif state_path is not None:
            base_dir = state_path.parent
        else:
            base_dir = Path(".")
        store = FileStore(
            gov_path=state_path or _DEFAULT_STATE_PATH,
            traces_path=traces_path or _DEFAULT_TRACES_PATH,
            zones_path=base_dir / "zone_registry.json",
            claims_path=base_dir / ".aegis" / "task_claims.json",
            commit_lock_path=base_dir / ".aegis" / "commit.lock.json",
            perspectives_path=base_dir / ".aegis" / "perspectives.json",
            checkpoints_path=base_dir / ".aegis" / "checkpoints.json",
            compactions_path=base_dir / ".aegis" / "compacted.json",
        )
    else:
        store = get_store()

    lock_owner = f"{trace.agent}:{trace.session_id}"
    lock_token = store.acquire_commit_lock(lock_owner, ttl_seconds=COMMIT_LOCK_TTL_SECONDS)
    if lock_token is None:
        raise CommitConcurrencyError(
            "Another agent is already committing canonical governance state"
        )

    # Load current state from the SAME store we'll write to (no split-brain)
    raw = store.get_state()
    if not raw:
        posture = GovernancePosture(last_updated=_utc_now())
    else:
        posture = GovernancePosture.from_dict(raw)
        posture.tension_history = decay_tensions(posture.tension_history)

    # ── Aegis Shield: check trace BEFORE mutating governance state ──
    trace_dict = trace.to_dict()
    try:
        from tonesoul.aegis_shield import AegisShield

        shield = AegisShield.load(store)
        trace_dict, content_check = shield.protect_trace(trace_dict, trace.agent)
        if content_check.severity == "blocked":
            print(f"[Aegis] BLOCKED trace from {trace.agent}: {content_check.violations}")
            # Record veto WITHOUT merging the poisoned trace into posture
            posture.aegis_vetoes.append(
                {
                    "type": "memory_poisoning",
                    "agent": trace.agent,
                    "violations": content_check.violations,
                    "timestamp": _utc_now(),
                }
            )
            store.set_state(posture.to_dict())
            store.release_commit_lock(lock_token)
            return posture
        if content_check.violations:
            print(f"[Aegis] WARNING: {content_check.violations}")
        shield.save(store)
    except ImportError:
        pass  # PyNaCl not installed — skip shield

    # ── Aegis passed — now safe to merge trace into governance state ──

    # Merge new tension events into history
    for event in trace.tension_events:
        entry = dict(event)
        if "timestamp" not in entry:
            entry["timestamp"] = trace.timestamp
        posture.tension_history.append(entry)

    # Update soul integral
    posture.soul_integral = update_soul_integral(
        posture.soul_integral,
        posture.last_updated,
        trace.tension_events,
    )

    # Drift baseline
    posture.baseline_drift = drift_baseline(
        posture.baseline_drift,
        trace.tension_events,
    )

    # Reconcile vows
    existing_ids = {v.get("id") for v in posture.active_vows}
    for ve in trace.vow_events:
        action = ve.get("action", "")
        vow_id = ve.get("vow_id", "")
        if action == "created" and vow_id not in existing_ids:
            posture.active_vows.append(
                {
                    "id": vow_id,
                    "content": ve.get("detail", ""),
                    "created": trace.timestamp[:10],
                    "source": f"session:{trace.session_id}",
                }
            )
        elif action == "retired":
            posture.active_vows = [v for v in posture.active_vows if v.get("id") != vow_id]

    # Merge aegis vetoes
    for veto in trace.aegis_vetoes:
        entry = dict(veto)
        if "timestamp" not in entry:
            entry["timestamp"] = trace.timestamp
        posture.aegis_vetoes.append(entry)

    # Update metadata
    posture.session_count += 1
    posture.last_updated = _utc_now()

    # Persist — Redis: atomic set + pub/sub push; FileStore: JSON write
    store.set_state(posture.to_dict())
    store.append_trace(trace_dict)

    # Rebuild zone registry (updates world map)
    try:
        from tonesoul.zone_registry import rebuild_and_save

        if store.is_redis:
            rebuild_and_save(store=store)
        else:
            rebuild_and_save(
                traces_path=store.traces_path,
                governance_path=store.gov_path,
                registry_path=store.zones_path,
            )
    except Exception:
        pass  # Non-critical

    store.release_commit_lock(lock_token)
    return posture


# ---------------------------------------------------------------------------
# Public API: summary() — human-readable snapshot for any model
# ---------------------------------------------------------------------------


def summary(posture: Optional[GovernancePosture] = None) -> str:
    """One-screen text summary of governance posture, readable by any AI model."""
    if posture is None:
        posture = load()

    lines = [
        "=== ToneSoul Governance Posture ===",
        f"Soul Integral (Psi): {posture.soul_integral}",
        f"Sessions: {posture.session_count}",
        f"Last Updated: {posture.last_updated}",
        "",
        "--- Baseline ---",
        f"  Caution:    {posture.baseline_drift.get('caution_bias', '?')}",
        f"  Innovation: {posture.baseline_drift.get('innovation_bias', '?')}",
        f"  Autonomy:   {posture.baseline_drift.get('autonomy_level', '?')}",
        "",
        f"--- Active Vows ({len(posture.active_vows)}) ---",
    ]
    for v in posture.active_vows:
        lines.append(f"  [{v.get('id')}] {v.get('content')}")

    if posture.tension_history:
        lines.append("")
        lines.append(f"--- Recent Tensions ({len(posture.tension_history)}) ---")
        for t in posture.tension_history[-5:]:
            lines.append(f"  [{t.get('severity', '?')}] {t.get('topic', '?')}")

    if posture.aegis_vetoes:
        lines.append("")
        lines.append(f"--- Aegis Vetoes ({len(posture.aegis_vetoes)}) ---")
        for v in posture.aegis_vetoes[-3:]:
            lines.append(f"  {v.get('topic', '?')}: {v.get('reason', '?')}")

    # Recent visitors (Redis only)
    visitors = get_recent_visitors(n=5)
    if visitors:
        lines.append("")
        lines.append("--- Recent Visitors ---")
        seen = set()
        for v in visitors:
            agent = v.get("agent", "?")
            ts = v.get("timestamp", "")[:19]
            src = v.get("source", "?")
            key = f"{agent}@{ts}"
            if key not in seen:
                seen.add(key)
                lines.append(f"  {agent} @ {ts} [{src}]")

    return "\n".join(lines)


def r_memory_packet(
    posture: Optional[GovernancePosture] = None,
    *,
    store=None,
    trace_limit: int = 5,
    visitor_limit: int = 5,
) -> Dict[str, Any]:
    """Compact agent-facing packet for inheriting live governance posture.

    This is the short machine-readable surface other agents should prefer over
    rereading long prose when they only need the current hot runtime picture.
    """
    if store is None:
        from tonesoul.store import get_store

        store = get_store()

    if posture is None:
        raw = {}
        try:
            raw = store.get_state()
        except Exception:
            raw = {}
        if raw:
            posture = GovernancePosture.from_dict(raw)
            posture.tension_history = decay_tensions(posture.tension_history)
        else:
            posture = GovernancePosture(last_updated=_utc_now())

    traces: List[Dict[str, Any]] = []
    try:
        traces = list(store.get_traces(n=trace_limit))
    except Exception:
        traces = []

    visitors = get_recent_visitors(store=store, n=visitor_limit)
    claims = list_active_claims(store=store)
    compactions = list_compactions(store=store, n=trace_limit)

    def _trim_tension(event: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "topic": str(event.get("topic", "")),
            "severity": float(event.get("severity", 0.0)),
        }
        if event.get("timestamp"):
            item["timestamp"] = str(event.get("timestamp"))
        if event.get("resolution"):
            item["resolution"] = str(event.get("resolution"))
        return item

    def _trim_veto(veto: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "type": str(veto.get("type", "")),
            "timestamp": str(veto.get("timestamp", "")),
        }
        if veto.get("agent"):
            item["agent"] = str(veto.get("agent"))
        if veto.get("topic"):
            item["topic"] = str(veto.get("topic"))
        if veto.get("reason"):
            item["reason"] = str(veto.get("reason"))
        if veto.get("violations"):
            item["violations"] = list(veto.get("violations") or [])
        return item

    def _trim_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "session_id": str(trace.get("session_id", "")),
            "agent": str(trace.get("agent", "unknown")),
            "timestamp": str(trace.get("timestamp", "")),
            "topics": list(trace.get("topics") or []),
            "tension_count": len(trace.get("tension_events") or []),
            "vow_count": len(trace.get("vow_events") or []),
            "aegis_veto_count": len(trace.get("aegis_vetoes") or []),
            "key_decision_count": len(trace.get("key_decisions") or []),
        }

    def _trim_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "task_id": str(claim.get("task_id", "")),
            "agent": str(claim.get("agent", "")),
            "summary": str(claim.get("summary", "")),
            "paths": list(claim.get("paths") or []),
            "source": str(claim.get("source", "")),
            "created_at": str(claim.get("created_at", "")),
            "expires_at": str(claim.get("expires_at", "")),
        }

    def _trim_compaction(entry: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "compaction_id": str(entry.get("compaction_id", "")),
            "agent": str(entry.get("agent", "")),
            "session_id": str(entry.get("session_id", "")),
            "summary": str(entry.get("summary", "")),
            "carry_forward": list(entry.get("carry_forward") or []),
            "pending_paths": list(entry.get("pending_paths") or []),
            "evidence_refs": list(entry.get("evidence_refs") or []),
            "next_action": str(entry.get("next_action", "")),
            "source": str(entry.get("source", "")),
            "updated_at": str(entry.get("updated_at", "")),
        }

    return {
        "contract_version": R_MEMORY_PACKET_VERSION,
        "generated_at": _utc_now(),
        "backend": getattr(store, "backend_name", "unknown"),
        "dominance_order": [
            "hard_constraints",
            "canonical_governance_contracts",
            "current_task_objective",
            "r_memory_posture",
            "retrieved_long_term_memory",
            "loose_prose_background",
        ],
        "session_end_order": [
            "build_session_trace",
            "run_aegis_and_verifier_gates",
            "merge_trace_effects_into_governance_posture",
            "persist_governance_posture",
            "append_aegis_protected_trace",
            "rebuild_world_and_zone_surfaces",
            "optionally_export_safe_semantic_summary",
        ],
        "trace_integrity": {
            "aegis_protected": True,
            "hash_chain_required": True,
            "source_of_truth": "tonesoul/runtime_adapter.py::commit",
        },
        "parallel_lanes": {
            "canonical_commit_serialized": True,
            "perspectives_surface": "ts:perspectives:{agent_id}",
            "checkpoints_surface": "ts:checkpoints:*",
            "compaction_surface": "ts:compacted",
            "field_surface": "ts:field",
        },
        "canonical_sources": [
            "docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md",
            "docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md",
            "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md",
            "docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md",
            "docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md",
        ],
        "posture": {
            "soul_integral": posture.soul_integral,
            "session_count": posture.session_count,
            "last_updated": posture.last_updated,
            "baseline_drift": dict(posture.baseline_drift),
            "active_vows": [
                {
                    "id": str(v.get("id", "")),
                    "content": str(v.get("content", "")),
                    "source": str(v.get("source", "")),
                }
                for v in posture.active_vows
            ],
            "recent_tensions": [_trim_tension(t) for t in posture.tension_history[-trace_limit:]],
            "recent_aegis_vetoes": [_trim_veto(v) for v in posture.aegis_vetoes[-3:]],
        },
        "recent_traces": [_trim_trace(t) for t in traces[-trace_limit:]],
        "recent_visitors": visitors[:visitor_limit],
        "active_claims": [_trim_claim(c) for c in claims],
        "recent_compactions": [_trim_compaction(c) for c in compactions[:trace_limit]],
    }
