"""ToneSoul Runtime Adapter ??the bridge that makes governance state survive across sessions and models.

Implements RFC-015 Self-Dogfooding Runtime Adapter:
- load(): session start ??read governance_state.json, decay old tensions, return posture
- commit(): session end ??write session trace, update governance state, drift baseline

Design principles:
1. Model-agnostic ??any AI agent (Claude, Codex, Gemini) can load/commit
2. JSON in, JSON out ??no markdown parsing, no model-specific formats
3. Idempotent ??load() without commit() produces zero diff
4. Observable ??every mutation is traceable
"""

from __future__ import annotations

__ts_layer__ = "pipeline"
__ts_purpose__ = (
    "Load/commit governance state across session boundaries; the model-agnostic runtime spine."
)

import json
import logging
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tonesoul.runtime_adapter_normalization import (
    build_council_dossier_summary as _build_council_dossier_summary,
)
from tonesoul.runtime_adapter_normalization import (
    clean_string_list as _clean_string_list,
)
from tonesoul.runtime_adapter_normalization import (
    derive_council_realism_note as _derive_council_realism_note,
)
from tonesoul.runtime_adapter_normalization import (
    normalize_closeout_payload,
)
from tonesoul.runtime_adapter_normalization import (
    normalize_council_dossier as _normalize_council_dossier,
)
from tonesoul.runtime_adapter_routing import (
    build_routing_event as _build_routing_event,
)
from tonesoul.runtime_adapter_routing import (
    build_routing_summary as _build_routing_summary_impl,
)
from tonesoul.runtime_adapter_routing import (
    persist_routed_signal as _persist_routed_signal,
)
from tonesoul.runtime_adapter_routing import (
    route_r_memory_signal as _route_r_memory_signal,
)
from tonesoul.runtime_adapter_routing import (
    safe_list_routing_events as _safe_list_routing_events,
)
from tonesoul.runtime_adapter_subject_refresh import (
    build_subject_refresh_summary as _build_subject_refresh_summary_impl,
)
from tonesoul.soul_config import SOUL

logger = logging.getLogger(__name__)
route_r_memory_signal = _route_r_memory_signal

# ---------------------------------------------------------------------------
# Constants (from RFC-015 禮5, canonical source: soul_config.py)
# ---------------------------------------------------------------------------

TENSION_DECAY_ALPHA = SOUL.tension.decay_alpha_per_hour
TENSION_PRUNE_THRESHOLD = SOUL.tension.prune_threshold
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
    """What an agent sees at session start ??the living governance state."""

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
    risk_posture: Dict[str, Any] = field(default_factory=dict)
    session_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Include runtime-attached reflex_decision if present
        reflex = getattr(self, "reflex_decision", None)
        if reflex is not None and hasattr(reflex, "to_dict"):
            d["reflex_decision"] = reflex.to_dict()
        return d

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
            risk_posture=dict(data.get("risk_posture") or {}),
            session_count=int(data.get("session_count", 0)),
        )


@dataclass
class SessionTrace:
    """What an agent writes at session end ??one conversation's governance record."""

    session_id: str = ""
    agent: str = "unknown"
    timestamp: str = ""
    duration_minutes: float = 0.0
    topics: List[str] = field(default_factory=list)
    tension_events: List[Dict[str, Any]] = field(default_factory=list)
    vow_events: List[Dict[str, Any]] = field(default_factory=list)
    aegis_vetoes: List[Dict[str, Any]] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    council_dossier: Optional[Dict[str, Any]] = None
    stance_shift: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = _utc_now()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d.get("council_dossier") is not None:
            d["council_dossier"] = _normalize_council_dossier(d.get("council_dossier"))
        if not d.get("council_dossier"):
            del d["council_dossier"]
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


def _offset_utc(iso_str: str, seconds: int) -> str:
    """Add seconds to an ISO datetime string. Returns ISO string."""
    from datetime import timedelta

    dt = _parse_dt(iso_str)
    if dt is None:
        dt = datetime.now(timezone.utc)
    return (dt + timedelta(seconds=seconds)).isoformat()


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


def _freshness_hours(raw_timestamp: Any) -> Optional[float]:
    """Return bounded freshness for a timestamp-like value."""
    text = str(raw_timestamp or "").strip()
    if not text:
        return None
    dt = _parse_dt(text)
    if dt is None:
        return None
    return round(_hours_since(text), 3)


# ---------------------------------------------------------------------------
# Core: tension decay (RFC-015 禮5.1)
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
# Core: baseline drift (RFC-015 禮5.2)
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
    # Autonomy drifts inversely with tension ??high-tension sessions reduce autonomy
    autonomy = float(new.get("autonomy_level", 0.35))
    target_autonomy = max(0.1, 1.0 - avg_severity)  # high severity ??low target
    new["autonomy_level"] = round(autonomy + rate * (target_autonomy - autonomy), 4)
    return new


# ---------------------------------------------------------------------------
# Core: soul integral update (RFC-015 禮5.3)
# ---------------------------------------------------------------------------


def update_soul_integral(
    current: float,
    last_updated: str,
    session_tensions: List[Dict[str, Any]],
    alpha: float = TENSION_DECAY_ALPHA,
    *,
    wisdom_delta: float = 0.0,
    wisdom_beta: float = 0.05,
) -> float:
    """Update soul integral as an exponentially-weighted moving integral.

    Formula: S_new = S_old * e^(-alpha * hours)
                    + tension_blend * max_tension
                    + wisdom_beta * wisdom_delta
    Clamped to [0.0, 1.0].

    The tension_blend (0.3) prevents a single high-tension session from
    spiking the integral to 1.0, while preserving the decay behavior
    that gradually relaxes stress back toward zero.

    The wisdom_delta (0.0-1.0) is an additive learning-accumulation
    signal computed from crystal density, session coherence, and
    rediscovery penalty.  Default 0.0 preserves backwards compatibility.

    When session_tensions is empty and wisdom_delta is 0, the integral
    purely decays ??it does NOT reset to zero.  The decay half-life
    (~14h) ensures historical stress fades naturally.
    """
    hours = _hours_since(last_updated)
    decayed = current * math.exp(-alpha * hours)
    max_t = max((float(t.get("severity", 0.0)) for t in session_tensions), default=0.0)
    tension_blend = 0.3  # how much of max_tension is absorbed per session
    result = decayed + tension_blend * max_t + wisdom_beta * max(0.0, min(1.0, wisdom_delta))
    return round(max(0.0, min(1.0, result)), 4)


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

    # Attach reflex arc evaluation (Phase 1: soft enforcement)
    _attach_reflex_state(posture)

    return posture


def _attach_reflex_state(posture: GovernancePosture) -> None:
    """Compute and attach reflex arc state to posture.

    Sets posture.reflex_decision (ReflexDecision) as a runtime attribute.
    Silently skips if reflex module is unavailable or config says disabled.
    """
    try:
        from tonesoul.governance.reflex import (
            GovernanceSnapshot,
            ReflexEvaluator,
        )
        from tonesoul.governance.reflex_config import load_reflex_config

        config = load_reflex_config()
        if not config.enabled:
            return

        snapshot = GovernanceSnapshot.from_posture(posture)
        evaluator = ReflexEvaluator(config=config)
        decision = evaluator.evaluate(snapshot)
        # Attach as runtime attribute (not part of dataclass schema)
        posture.reflex_decision = decision  # type: ignore[attr-defined]
    except Exception as exc:
        logger.debug("Reflex arc skipped: %s", exc)  # optional ??failure must not break load()


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
    except Exception as exc:
        logger.warning("Failed to record footprint for %s: %s", agent_id, exc)


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
    council_dossier: Optional[Dict[str, Any]] = None,
    closeout: Optional[Dict[str, Any]] = None,
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
    now = _utc_now()
    payload = {
        "compaction_id": str(uuid.uuid4()),
        "agent": agent_id,
        "session_id": session_id,
        "summary": summary,
        "carry_forward": list(carry_forward or []),
        "pending_paths": list(pending_paths or []),
        "evidence_refs": list(evidence_refs or []),
        "council_dossier": _normalize_council_dossier(council_dossier),
        "closeout": normalize_closeout_payload(
            closeout,
            pending_paths=list(pending_paths or []),
            next_action=next_action,
        ),
        "next_action": next_action,
        "source": source,
        "updated_at": now,
        # Temporal validity window ??when was this compaction's content true?
        # Inspired by MemPalace's temporal knowledge graph.
        # valid_from: when this snapshot of reality began (session start)
        # valid_until: when it should be considered stale (updated_at + TTL)
        "valid_from": now,
        "valid_until": _offset_utc(now, ttl_seconds),
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


def write_subject_snapshot(
    *,
    agent_id: str,
    summary: str,
    session_id: str = "",
    stable_vows: Optional[List[str]] = None,
    durable_boundaries: Optional[List[str]] = None,
    decision_preferences: Optional[List[str]] = None,
    verified_routines: Optional[List[str]] = None,
    active_threads: Optional[List[str]] = None,
    evidence_refs: Optional[List[str]] = None,
    refresh_signals: Optional[List[str]] = None,
    source: str = "direct",
    ttl_seconds: int = 2592000,
    limit: int = 12,
    store=None,
) -> Dict[str, Any]:
    """Write a more durable but still non-canonical subject snapshot."""
    if not str(summary or "").strip():
        raise ValueError("summary is required for subject snapshots")
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    now = _utc_now()
    payload = {
        "snapshot_id": str(uuid.uuid4()),
        "agent": agent_id,
        "session_id": session_id,
        "summary": summary,
        "stable_vows": list(stable_vows or []),
        "durable_boundaries": list(durable_boundaries or []),
        "decision_preferences": list(decision_preferences or []),
        "verified_routines": list(verified_routines or []),
        "active_threads": list(active_threads or []),
        "evidence_refs": list(evidence_refs or []),
        "refresh_signals": list(refresh_signals or []),
        "source": source,
        "updated_at": now,
        "valid_from": now,
        "valid_until": _offset_utc(now, ttl_seconds),
    }
    store.append_subject_snapshot(payload, limit=limit, ttl_seconds=ttl_seconds)
    return payload


def list_subject_snapshots(store=None, n: int = 3) -> List[Dict[str, Any]]:
    """List recent non-canonical subject snapshots."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return list(store.get_subject_snapshots(n=n))
    except Exception:
        return []


def apply_subject_refresh(
    *,
    agent_id: str,
    field: str = "active_threads",
    summary: str = "",
    session_id: str = "",
    source: str = "subject-refresh-cli",
    refresh_signals: Optional[List[str]] = None,
    store=None,
) -> Dict[str, Any]:
    """Apply one bounded subject-refresh heuristic to the latest snapshot lane.

    Current scope is intentionally narrow:

    - only `active_threads`
    - only when the field is `may_refresh_directly`
    - only when the evidence is `compaction-backed`
    - only when no promotion hazards are present

    This keeps the first runtime heuristic aligned with the documented boundary
    contract instead of silently auto-promoting broader identity fields.
    """
    refresh_field = str(field or "").strip() or "active_threads"
    if refresh_field != "active_threads":
        raise ValueError("only active_threads refresh is currently supported")
    if store is None:
        from tonesoul.store import get_store

        store = get_store()

    raw_posture = {}
    try:
        raw_posture = store.get_state()
    except Exception:
        raw_posture = {}
    if raw_posture:
        posture = GovernancePosture.from_dict(raw_posture)
        posture.tension_history = decay_tensions(posture.tension_history)
    else:
        posture = GovernancePosture(last_updated=_utc_now())

    traces: List[Dict[str, Any]] = []
    try:
        traces = list(store.get_traces(n=5))
    except Exception:
        traces = []

    subject_snapshots = list_subject_snapshots(store=store, n=5)
    checkpoints = list_checkpoints(store=store)[:5]
    compactions = list_compactions(store=store, n=5)
    claims = list_active_claims(store=store)
    routing_events = list_routing_events(store=store, n=5)

    from tonesoul.risk_calculator import build_project_memory_summary, compute_runtime_risk

    risk_posture = compute_runtime_risk(
        posture=posture,
        recent_traces=traces[-5:],
        claims=claims,
        compactions=compactions,
    )
    routing_summary = _build_routing_summary(routing_events)
    project_memory_summary = build_project_memory_summary(
        posture=posture,
        recent_traces=traces[-5:],
        claims=claims,
        compactions=compactions,
        subject_snapshots=subject_snapshots,
        routing_summary=routing_summary,
    )
    subject_refresh = _build_subject_refresh_summary(
        subject_snapshots=subject_snapshots,
        checkpoints=checkpoints,
        compactions=compactions,
        claims=claims,
        routing_summary=routing_summary,
        project_memory_summary=project_memory_summary,
        risk_posture=risk_posture,
    )
    guidance = next(
        (
            item
            for item in list(subject_refresh.get("field_guidance") or [])
            if str(item.get("field", "")).strip() == refresh_field
        ),
        {},
    )
    candidate_values = _clean_string_list(guidance.get("candidate_values") or [])
    action = str(guidance.get("action", "")).strip()
    evidence_level = str(guidance.get("evidence_level", "")).strip()
    hazards = list(subject_refresh.get("promotion_hazards") or [])

    if action != "may_refresh_directly":
        return {
            "ok": False,
            "field": refresh_field,
            "reason": "field_not_refreshable",
            "subject_refresh": subject_refresh,
            "applied_snapshot": None,
        }
    if evidence_level != "compaction-backed":
        return {
            "ok": False,
            "field": refresh_field,
            "reason": "evidence_not_compaction_backed",
            "subject_refresh": subject_refresh,
            "applied_snapshot": None,
        }
    if hazards:
        return {
            "ok": False,
            "field": refresh_field,
            "reason": "promotion_hazards_present",
            "subject_refresh": subject_refresh,
            "applied_snapshot": None,
        }
    if not candidate_values:
        return {
            "ok": False,
            "field": refresh_field,
            "reason": "no_candidate_values",
            "subject_refresh": subject_refresh,
            "applied_snapshot": None,
        }

    latest_snapshot = subject_snapshots[0] if subject_snapshots else {}
    merged_threads = _clean_string_list(
        list(latest_snapshot.get("active_threads") or []) + candidate_values
    )
    latest_compaction_ids = [
        f"compaction:{str(entry.get('compaction_id', '')).strip()}"
        for entry in list(compactions)[:2]
        if str(entry.get("compaction_id", "")).strip()
    ]
    merged_evidence_refs = _clean_string_list(
        list(latest_snapshot.get("evidence_refs") or []) + latest_compaction_ids
    )
    signal_list = _clean_string_list(
        list(latest_snapshot.get("refresh_signals") or [])
        + list(refresh_signals or [])
        + ["active_threads compaction-backed refresh applied"]
    )
    snapshot_summary = (
        str(summary or "").strip()
        or str(
            latest_snapshot.get("summary")
            or "Bounded subject refresh kept active_threads aligned with recent compaction-backed focus."
        ).strip()
    )

    applied_snapshot = write_subject_snapshot(
        agent_id=agent_id,
        session_id=session_id or str(latest_snapshot.get("session_id", "")),
        summary=snapshot_summary,
        stable_vows=list(latest_snapshot.get("stable_vows") or []),
        durable_boundaries=list(latest_snapshot.get("durable_boundaries") or []),
        decision_preferences=list(latest_snapshot.get("decision_preferences") or []),
        verified_routines=list(latest_snapshot.get("verified_routines") or []),
        active_threads=merged_threads,
        evidence_refs=merged_evidence_refs,
        refresh_signals=signal_list,
        source=source,
        store=store,
    )
    return {
        "ok": True,
        "field": refresh_field,
        "reason": "applied",
        "candidate_values": candidate_values,
        "subject_refresh": subject_refresh,
        "applied_snapshot": applied_snapshot,
    }


def write_routed_signal(
    route: Dict[str, Any],
    *,
    store=None,
    ttl_seconds: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Persist a routed signal into the selected shared surface."""
    return _persist_routed_signal(
        route,
        claim_writer=claim_task,
        perspective_writer=write_perspective,
        checkpoint_writer=write_checkpoint,
        compaction_writer=write_compaction,
        subject_snapshot_writer=write_subject_snapshot,
        store=store,
        ttl_seconds=ttl_seconds,
        limit=limit,
    )


def record_routing_event(
    route: Dict[str, Any],
    *,
    action: str = "preview",
    written: bool = False,
    store=None,
    ttl_seconds: int = 1209600,
    limit: int = 50,
) -> Dict[str, Any]:
    """Persist a bounded router adoption/ambiguity event."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    event = _build_routing_event(route, action=action, written=written, utc_now=_utc_now)
    store.append_routing_event(event, ttl_seconds=int(ttl_seconds), limit=int(limit))
    return event


def list_routing_events(store=None, n: int = 10) -> List[Dict[str, Any]]:
    """List recent router telemetry events."""
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    return _safe_list_routing_events(get_events=store.get_routing_events, n=n)


def _build_routing_summary(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _build_routing_summary_impl(events, freshness_hours=_freshness_hours)


def _build_subject_refresh_summary(
    *,
    subject_snapshots: List[Dict[str, Any]],
    checkpoints: List[Dict[str, Any]],
    compactions: List[Dict[str, Any]],
    claims: List[Dict[str, Any]],
    routing_summary: Dict[str, Any],
    project_memory_summary: Dict[str, Any],
    risk_posture: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_subject_refresh_summary_impl(
        subject_snapshots=subject_snapshots,
        checkpoints=checkpoints,
        compactions=compactions,
        claims=claims,
        routing_summary=routing_summary,
        project_memory_summary=project_memory_summary,
        risk_posture=risk_posture,
        parse_dt=_parse_dt,
    )


def get_observer_cursor(agent_id: str, store=None) -> Dict[str, Any]:
    """Read the current since-last-seen cursor for an observing agent."""
    observer_id = str(agent_id or "").strip()
    if not observer_id:
        return {}
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    try:
        return dict(store.get_observer_cursor(observer_id) or {})
    except Exception:
        return {}


def acknowledge_observer_cursor(
    agent_id: str,
    *,
    packet: Dict[str, Any],
    store=None,
    ttl_seconds: int = 2592000,
) -> Dict[str, Any]:
    """Advance an observer cursor after the packet has been read."""
    observer_id = str(agent_id or "").strip()
    if not observer_id:
        return {}
    if store is None:
        from tonesoul.store import get_store

        store = get_store()
    cursor = _build_observer_cursor(observer_id=observer_id, packet=packet)
    try:
        store.set_observer_cursor(observer_id, cursor, ttl_seconds=ttl_seconds)
    except Exception:
        return {}
    return cursor


def _build_observer_cursor(*, observer_id: str, packet: Dict[str, Any]) -> Dict[str, Any]:
    traces = list(packet.get("recent_traces") or [])
    compactions = list(packet.get("recent_compactions") or [])
    subject_snapshots = list(packet.get("recent_subject_snapshots") or [])
    checkpoints = list(packet.get("recent_checkpoints") or [])
    claims = list(packet.get("active_claims") or [])
    repo_progress = (packet.get("project_memory_summary") or {}).get("repo_progress") or {}

    latest_trace = traces[-1] if traces else {}
    latest_compaction = compactions[0] if compactions else {}
    latest_subject_snapshot = subject_snapshots[0] if subject_snapshots else {}
    latest_checkpoint = checkpoints[0] if checkpoints else {}

    return {
        "agent": observer_id,
        "last_seen_at": _utc_now(),
        "packet_generated_at": str(packet.get("generated_at", "")),
        "latest_trace_session_id": str(latest_trace.get("session_id", "")),
        "latest_compaction_id": str(latest_compaction.get("compaction_id", "")),
        "latest_subject_snapshot_id": str(latest_subject_snapshot.get("snapshot_id", "")),
        "latest_checkpoint_id": str(latest_checkpoint.get("checkpoint_id", "")),
        "active_claim_ids": [
            str(claim.get("task_id", ""))
            for claim in claims
            if str(claim.get("task_id", "")).strip()
        ],
        "repo_head": str(repo_progress.get("head", "")),
        "repo_dirty_count": int(repo_progress.get("dirty_count", 0) or 0),
    }


def _build_delta_feed(
    *,
    observer_id: str,
    cursor: Dict[str, Any],
    traces: List[Dict[str, Any]],
    claims: List[Dict[str, Any]],
    checkpoints: List[Dict[str, Any]],
    compactions: List[Dict[str, Any]],
    subject_snapshots: List[Dict[str, Any]],
    project_memory_summary: Dict[str, Any],
) -> Dict[str, Any]:
    first_observation = not bool(cursor)

    def _recent_since_marker(
        entries: List[Dict[str, Any]],
        *,
        key: str,
        fields: List[str],
        marker: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for entry in entries:
            entry_id = str(entry.get(key, ""))
            if marker and entry_id == marker:
                break
            trimmed = {field: entry.get(field) for field in fields if field in entry}
            result.append(trimmed)
            if len(result) >= limit:
                break
        return result

    new_compactions = _recent_since_marker(
        compactions,
        key="compaction_id",
        fields=["compaction_id", "agent", "summary", "updated_at"],
        marker=str(cursor.get("latest_compaction_id", "")),
    )
    new_subject_snapshots = _recent_since_marker(
        subject_snapshots,
        key="snapshot_id",
        fields=["snapshot_id", "agent", "summary", "updated_at"],
        marker=str(cursor.get("latest_subject_snapshot_id", "")),
    )
    new_checkpoints = _recent_since_marker(
        checkpoints,
        key="checkpoint_id",
        fields=["checkpoint_id", "agent", "summary", "next_action", "updated_at"],
        marker=str(cursor.get("latest_checkpoint_id", "")),
    )

    new_traces: List[Dict[str, Any]] = []
    latest_trace_marker = str(cursor.get("latest_trace_session_id", ""))
    for trace in reversed(traces):
        trace_id = str(trace.get("session_id", ""))
        if latest_trace_marker and trace_id == latest_trace_marker:
            break
        new_traces.append(
            {
                "session_id": trace_id,
                "agent": trace.get("agent"),
                "timestamp": trace.get("timestamp"),
                "topics": list(trace.get("topics") or [])[:3],
            }
        )
        if len(new_traces) >= 3:
            break

    previous_claim_ids = {
        str(task_id).strip()
        for task_id in (cursor.get("active_claim_ids") or [])
        if str(task_id).strip()
    }
    current_claim_ids = {
        str(claim.get("task_id", "")).strip()
        for claim in claims
        if str(claim.get("task_id", "")).strip()
    }
    new_claims = [
        {
            "task_id": str(claim.get("task_id", "")),
            "agent": str(claim.get("agent", "")),
            "summary": str(claim.get("summary", "")),
        }
        for claim in claims
        if str(claim.get("task_id", "")).strip()
        and str(claim.get("task_id", "")).strip() not in previous_claim_ids
    ][:3]
    released_claim_ids = sorted(previous_claim_ids - current_claim_ids)[:3]

    repo_progress = project_memory_summary.get("repo_progress") or {}
    previous_head = str(cursor.get("repo_head", ""))
    current_head = str(repo_progress.get("head", ""))
    previous_dirty = int(cursor.get("repo_dirty_count", 0) or 0)
    current_dirty = int(repo_progress.get("dirty_count", 0) or 0)
    repo_changed = (
        bool(previous_head and previous_head != current_head) or previous_dirty != current_dirty
    )

    update_count = (
        len(new_compactions)
        + len(new_subject_snapshots)
        + len(new_checkpoints)
        + len(new_traces)
        + len(new_claims)
        + len(released_claim_ids)
        + (1 if repo_changed else 0)
    )

    summary_parts: List[str] = []
    if first_observation:
        summary_parts.append(
            "No observer cursor yet; current packet becomes the baseline after ack."
        )
    else:
        if new_compactions:
            summary_parts.append(f"compactions={len(new_compactions)}")
        if new_subject_snapshots:
            summary_parts.append(f"subject_snapshots={len(new_subject_snapshots)}")
        if new_checkpoints:
            summary_parts.append(f"checkpoints={len(new_checkpoints)}")
        if new_traces:
            summary_parts.append(f"accepted_traces={len(new_traces)}")
        if new_claims or released_claim_ids:
            summary_parts.append(f"claims(+{len(new_claims)}/-{len(released_claim_ids)})")
        if repo_changed:
            summary_parts.append(
                f"repo={previous_head or 'unknown'}->{current_head or 'unknown'} dirty={previous_dirty}->{current_dirty}"
            )
        if not summary_parts:
            summary_parts.append("No changes since the last acknowledged observer baseline.")

    return {
        "observer_id": observer_id,
        "first_observation": first_observation,
        "has_updates": first_observation or update_count > 0,
        "update_count": int(update_count),
        "previous_seen_at": str(cursor.get("last_seen_at", "")),
        "summary_text": " | ".join(summary_parts),
        "new_compactions": new_compactions,
        "new_subject_snapshots": new_subject_snapshots,
        "new_checkpoints": new_checkpoints,
        "new_traces": new_traces,
        "new_claims": new_claims,
        "released_claim_ids": released_claim_ids,
        "repo_change": {
            "changed": repo_changed,
            "previous_head": previous_head,
            "current_head": current_head,
            "previous_dirty_count": previous_dirty,
            "current_dirty_count": current_dirty,
        },
        "ack_command": f"python scripts/run_r_memory_packet.py --agent {observer_id} --ack",
    }


def _build_operator_guidance(
    *,
    backend_name: str,
    is_redis: bool,
    observer_id: str,
    delta_feed: Dict[str, Any],
    claims: List[Dict[str, Any]],
    compactions: List[Dict[str, Any]],
    traces: List[Dict[str, Any]],
    subject_snapshots: List[Dict[str, Any]],
    project_memory_summary: Dict[str, Any],
    coordination_mode: Dict[str, Any],
) -> Dict[str, Any]:
    """Build packet-visible operator guidance for shared R-memory coordination."""
    from tonesoul.consumer_contract import build_memory_consumer_contract
    from tonesoul.hook_chain import build_hook_chain_readout
    from tonesoul.receiver_posture import build_receiver_parity_readout
    from tonesoul.surface_versioning import build_surface_versioning_readout

    reminders: List[str] = []
    latest_compaction = compactions[0] if compactions else {}
    latest_compaction_closeout = normalize_closeout_payload(
        (
            latest_compaction.get("closeout")
            if isinstance(latest_compaction.get("closeout"), dict)
            else None
        ),
        pending_paths=list(latest_compaction.get("pending_paths") or []),
        next_action=str(latest_compaction.get("next_action", "")),
    )
    if compactions:
        reminders.append(
            "Prefer recent_compactions and project_memory_summary before older recent_traces."
        )
    else:
        reminders.append(
            "No recent compaction is visible; write one before handoff if you finish a chunk."
        )

    if claims:
        reminders.append("Active claims are visible; coordinate before editing overlapping paths.")
    else:
        reminders.append("No active claims are visible; claim shared paths before editing them.")

    pending_paths = list(project_memory_summary.get("pending_paths") or [])
    if pending_paths:
        reminders.append(
            "Pending paths are already externalized; reuse them before widening the scan."
        )

    closeout_status = str(latest_compaction_closeout.get("status", "")).strip()
    if compactions and closeout_status in {"partial", "blocked", "underdetermined"}:
        reminders.append(
            f"Latest compaction closeout is {closeout_status}; do not read the handoff as completed work."
        )
    reminders.append(
        "Use --path and --next-action only for unresolved carry-forward; omit them when the session truly closes cleanly."
    )

    routing_summary = project_memory_summary.get("routing_summary") or {}
    if int(routing_summary.get("total_events", 0) or 0) <= 0:
        reminders.append(
            "No router telemetry is visible yet; use route_r_memory_signal.py when a note does not fit a surface cleanly."
        )
    elif int(routing_summary.get("misroute_signal_count", 0) or 0) > 0:
        reminders.append(
            "Router ambiguity signals are visible; review forced routes or multi-signal overlaps before assuming the chosen surface is obvious."
        )

    if subject_snapshots:
        reminders.append(
            "A recent subject snapshot is visible; treat it as durable working identity, but still non-canonical."
        )
    else:
        reminders.append(
            "No subject snapshot is visible; write one when stable boundaries, preferences, or verified routines change."
        )

    working_style_anchor = project_memory_summary.get("working_style_anchor") or {}
    if working_style_anchor:
        from tonesoul.working_style import build_working_style_playbook

        playbook = build_working_style_playbook(working_style_anchor)
        observability = project_memory_summary.get("working_style_observability") or {}
        import_limits = project_memory_summary.get("working_style_import_limits") or {}
        reminders.append(
            "A working-style playbook is visible; apply it as advisory workflow, not as durable identity or policy."
        )
        for item in list(playbook.get("checklist") or [])[:2]:
            reminders.append(f"Working-style: {item}")
        if import_limits:
            reminders.append(
                "Working-style import stays bounded to scan order, evidence handling, prompt shape, session cadence, and render interpretation."
            )
        status = str(observability.get("status", "")).strip()
        if status == "partial":
            reminders.append(
                "Only part of the shared working-style anchor is echoed by recent handoff surfaces; keep the playbook visible instead of assuming full continuity."
            )
        elif status == "unreinforced":
            reminders.append(
                "The shared working-style anchor is currently unreinforced by recent handoff surfaces; re-apply the playbook explicitly before defaulting to model-native habits."
            )

    subject_refresh = project_memory_summary.get("subject_refresh") or {}
    refresh_status = str(subject_refresh.get("status", "")).strip()
    if refresh_status in {"seed_snapshot", "refresh_candidate"}:
        reminders.append(
            "Subject-refresh heuristics found low-risk updates; review subject_refresh before writing the next snapshot."
        )
    elif refresh_status == "manual_review":
        reminders.append(
            "Subject-refresh heuristics found promotion hazards; keep higher-risk fields operator-reviewed instead of auto-promoting hot-state."
        )

    evidence_readout_posture = project_memory_summary.get("evidence_readout_posture") or {}
    evidence_summary = str(evidence_readout_posture.get("summary_text", "")).strip()
    if evidence_summary:
        reminders.append(f"Evidence posture: {evidence_summary}")

    launch_claim_posture = project_memory_summary.get("launch_claim_posture") or {}
    launch_claim_summary = str(launch_claim_posture.get("summary_text", "")).strip()
    if launch_claim_summary:
        reminders.append(f"Launch claim posture: {launch_claim_summary}")
    launch_health_trend_posture = project_memory_summary.get("launch_health_trend_posture") or {}
    launch_health_summary = str(launch_health_trend_posture.get("summary_text", "")).strip()
    if launch_health_summary:
        reminders.append(f"Launch health posture: {launch_health_summary}")
    internal_state_observability = project_memory_summary.get("internal_state_observability") or {}
    internal_state_summary = str(internal_state_observability.get("summary_text", "")).strip()
    if internal_state_summary:
        reminders.append(f"Internal state posture: {internal_state_summary}")

    latest_dossier_payload: Dict[str, Any] = {}
    for entry in compactions:
        candidate = entry.get("council_dossier")
        if isinstance(candidate, dict) and candidate:
            latest_dossier_payload = candidate
            break
    if not latest_dossier_payload:
        for entry in traces:
            candidate = entry.get("council_dossier")
            if isinstance(candidate, dict) and candidate:
                latest_dossier_payload = candidate
                break
    realism_note = _derive_council_realism_note(latest_dossier_payload)
    if realism_note:
        reminders.append(f"Council realism: {realism_note}")
    receiver_parity = build_receiver_parity_readout(
        council_snapshot=(
            _build_council_dossier_summary(latest_dossier_payload) if latest_dossier_payload else {}
        ),
        project_memory_summary=project_memory_summary,
    )
    receiver_summary = str(receiver_parity.get("summary_text", "")).strip()
    if receiver_summary:
        reminders.append(f"Receiver posture: {receiver_summary}")
    receiver_rule = str(receiver_parity.get("rule", "")).strip()
    if receiver_rule:
        reminders.append(f"Receiver ladder: {receiver_rule}")

    refresh_hint = str(coordination_mode.get("refresh_hint", "")).strip()
    if refresh_hint:
        reminders.append(refresh_hint)
    elif is_redis:
        reminders.append(
            "Redis live surfaces are available; perspectives and checkpoints may be visible immediately."
        )
    else:
        reminders.append(
            "Redis live surfaces are unavailable; coordination is currently file-backed."
        )

    launch_posture_note = str(coordination_mode.get("launch_posture_note", "")).strip()
    if launch_posture_note:
        reminders.append(f"Launch coordination default: {launch_posture_note}")

    if observer_id:
        if delta_feed.get("first_observation"):
            reminders.append(
                "No since-last-seen baseline exists yet; ack the packet after review to establish one."
            )
        else:
            reminders.append(
                "A delta feed is visible for this agent; ack after review to advance the observer baseline."
            )

    hook_chain = build_hook_chain_readout(agent_id=observer_id or "<your-id>")
    consumer_contract = build_memory_consumer_contract(
        readiness_status="unknown_until_session_start",
        canonical_center={},
        closeout_attention={
            "status": closeout_status or "complete",
            "summary_text": (
                "latest compaction closeout is complete"
                if not closeout_status or closeout_status == "complete"
                else f"latest compaction closeout is {closeout_status}"
            ),
        },
        mutation_preflight={},
        deep_surface_note=(
            "Packet is a deeper surface. Read session-start readiness and canonical center first, then pull packet detail if the task is ambiguous or shared-state heavy."
        ),
    )
    surface_versioning = build_surface_versioning_readout()
    reminders.append(f"Consumer contract: {consumer_contract.get('summary_text', '')}")
    reminders.append(f"Surface versioning: {surface_versioning.get('summary_text', '')}")

    return {
        "backend_mode": backend_name,
        "session_start": [
            "python scripts/start_agent_session.py --agent <your-id>",
            "python -m tonesoul.diagnose --agent <your-id>",
            "python scripts/run_r_memory_packet.py --agent <your-id> --ack",
            "python scripts/run_task_claim.py list",
        ],
        "session_end": [
            'python scripts/end_agent_session.py --agent <your-id> --summary "..." --closeout-status complete',
            'python scripts/end_agent_session.py --agent <your-id> --summary "..." --path "..." --next-action "..." --closeout-status partial',
            'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..." --next-action "..."',
            'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..." --next-action "..." --closeout-status partial',
            "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
        ],
        "preflight_chain": hook_chain,
        "consumer_contract": consumer_contract,
        "surface_versioning": surface_versioning,
        "coordination_commands": {
            "claim": 'python scripts/run_task_claim.py claim <task_id> --agent <your-id> --summary "..."',
            "perspective": 'python scripts/save_perspective.py --agent <your-id> --summary "..." --stance "..."',
            "checkpoint": 'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..." --next-action "..."',
            "compaction": 'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..." --next-action "..." --closeout-status partial',
            "signal_router": (
                'python scripts/route_r_memory_signal.py --agent <your-id> --summary "..." '
                '--path "..." --next-action "..." --write'
            ),
            "subject_snapshot": (
                'python scripts/save_subject_snapshot.py --agent <your-id> --summary "..." '
                '--boundary "..." --preference "..."'
            ),
            "apply_subject_refresh": (
                "python scripts/apply_subject_refresh.py --agent <your-id> "
                '--field active_threads --refresh-signal "subject-refresh heuristic reviewed"'
            ),
            "release": "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
        },
        "recommended_order": [
            "diagnose/load",
            "packet",
            "claim",
            "work",
            "perspective/checkpoint/compaction",
            "commit",
            "release",
        ],
        "current_reminders": reminders,
        "completion_rule": (
            "Before ending a session, externalize progress with checkpoint or compaction, "
            "mark closeout as complete/partial/blocked/underdetermined honestly, "
            "omit pending paths and next_action when the session truly ends cleanly, "
            "then release any shared claim."
        ),
    }


def _build_coordination_mode(
    *,
    is_redis: bool,
    observer_id: str,
    delta_feed: Dict[str, Any],
    claims: List[Dict[str, Any]],
    checkpoints: List[Dict[str, Any]],
    compactions: List[Dict[str, Any]],
    subject_snapshots: List[Dict[str, Any]],
    routing_events: List[Dict[str, Any]],
    visitors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    surface_modes = {
        "claims": "live" if is_redis else "file-backed",
        "perspectives": "live" if is_redis else "file-backed",
        "checkpoints": "live" if is_redis else "file-backed",
        "compactions": "live" if is_redis else "file-backed",
        "subject_snapshots": "live" if is_redis else "file-backed",
        "observer_cursors": "live" if is_redis else "file-backed",
        "routing_events": "live" if is_redis else "file-backed",
        "visitors": "live" if is_redis else "unavailable",
    }
    mode = "redis-live" if is_redis else "file-backed"
    observer_text = str(observer_id or "").strip()
    recheck_command = (
        f"python scripts/run_r_memory_packet.py --agent {observer_text}"
        if observer_text
        else "python scripts/run_r_memory_packet.py"
    )
    ack_command = str(delta_feed.get("ack_command", "")).strip() if observer_text else ""

    if is_redis:
        refresh_hint = "Redis live surfaces may change mid-session; re-read packet before shared edits after long work or when other agents arrive."
        launch_alignment = "runtime_override_not_launch_default"
        launch_posture_note = "Current runtime is redis-live, but the launch-default coordination story remains file-backed until Redis hardening is explicitly promoted."
    else:
        refresh_hint = "File-backed coordination is not push-driven; re-read packet before touching shared paths after longer work or after another agent reports progress."
        launch_alignment = "aligned_with_launch_default"
        launch_posture_note = "Current runtime matches the launch-default coordination story: file-backed continuity with receiver guards."

    summary_text = (
        "coordination="
        f"{mode} claims={surface_modes['claims']} checkpoints={surface_modes['checkpoints']} "
        f"subjects={surface_modes['subject_snapshots']} launch_default=file-backed "
        f"delta={'enabled' if observer_text else 'inactive'} "
        f"visitors={surface_modes['visitors']}"
    )
    if claims or checkpoints or compactions or subject_snapshots or routing_events or visitors:
        summary_text += (
            " active="
            f"claims:{len(claims)}/checkpoints:{len(checkpoints)}/compactions:{len(compactions)}/"
            f"subjects:{len(subject_snapshots)}/routing:{len(routing_events)}/visitors:{len(visitors)}"
        )

    return {
        "mode": mode,
        "live_surfaces_available": bool(is_redis),
        "delta_feed_enabled": bool(observer_text),
        "event_channel": "ts:events" if is_redis else "",
        "surface_modes": surface_modes,
        "recheck_command": recheck_command,
        "ack_command": ack_command,
        "refresh_hint": refresh_hint,
        "launch_default_mode": "file-backed",
        "launch_alignment": launch_alignment,
        "launch_posture_note": launch_posture_note,
        "summary_text": summary_text,
    }


def _build_launch_claim_posture(
    *,
    project_memory_summary: Dict[str, Any],
    coordination_mode: Dict[str, Any],
) -> Dict[str, Any]:
    evidence_readout = project_memory_summary.get("evidence_readout_posture") or {}
    lanes = list(evidence_readout.get("lanes") or [])
    lane_map = {
        str(item.get("lane", "")).strip(): str(item.get("classification", "")).strip()
        for item in lanes
        if str(item.get("lane", "")).strip()
    }

    continuity_classification = lane_map.get("continuity_effectiveness", "unknown")
    council_quality_classification = lane_map.get("council_decision_quality", "unknown")
    session_control_classification = lane_map.get("session_control_and_handoff", "unknown")
    council_mechanics_classification = lane_map.get("council_mechanics", "unknown")

    launch_default_mode = (
        str(coordination_mode.get("launch_default_mode", "unknown")).strip() or "unknown"
    )
    launch_alignment = (
        str(coordination_mode.get("launch_alignment", "unknown")).strip() or "unknown"
    )
    live_shared_memory_classification = (
        "not_launch_default" if launch_default_mode != "redis-live" else "launch_default"
    )

    tier_guidance = [
        {
            "tier": "internal_alpha",
            "posture": "safe_current_claims_only",
            "note": (
                "Safe to say trusted internal operators can use the current file-backed session-start/packet/diagnose "
                "workflow with tested receiver and council-mechanism readouts."
            ),
        },
        {
            "tier": "collaborator_beta",
            "posture": "guided_and_bounded",
            "note": (
                "Safe only as a guided beta target: repeated validation exists and the launch-default coordination story "
                "is explicit, but continuity effectiveness and council decision quality remain bounded rather than proven."
            ),
        },
        {
            "tier": "public_launch",
            "posture": "deferred",
            "note": (
                "Not yet honest to present ToneSoul as broadly launch-mature; public language must not overstate "
                "continuity effectiveness, council decision quality, or Redis/live shared memory."
            ),
        },
    ]

    safe_now = [
        (
            f"session_control_and_handoff={session_control_classification}: describe session-start, packet, delta, "
            "readiness, and receiver guards as the current tested coordination workflow."
        ),
        (
            f"coordination_backend={launch_default_mode}: describe file-backed coordination with receiver guards as "
            "the current launch-default story."
        ),
        (
            f"council_mechanics={council_mechanics_classification}: describe council structure, dossier extraction, "
            "and suppression visibility as mechanism-level support, not outcome proof."
        ),
    ]

    blocked_overclaims = [
        {
            "claim": "continuity_effectiveness",
            "current_classification": continuity_classification,
            "reason": (
                "Do not claim broadly proven cross-session continuity; current evidence supports bounded runtime "
                "presence and repeated validation, not public-grade proof."
            ),
        },
        {
            "claim": "council_decision_quality",
            "current_classification": council_quality_classification,
            "reason": (
                "Do not present council agreement or coherence as calibrated correctness; current confidence surfaces "
                "are descriptive, not accuracy-backed."
            ),
        },
        {
            "claim": "live_shared_memory",
            "current_classification": live_shared_memory_classification,
            "reason": (
                "Do not present Redis/live shared memory as the launch-default or hardened public story while "
                f"launch_default_mode remains {launch_default_mode} and launch_alignment is {launch_alignment}."
            ),
        },
    ]

    return {
        "current_tier": "collaborator_beta",
        "next_target_tier": "public_launch",
        "public_launch_ready": False,
        "tier_guidance": tier_guidance,
        "safe_now": safe_now,
        "blocked_overclaims": blocked_overclaims,
        "receiver_rule": (
            "Use collaborator-beta wording only for guided file-backed workflow and explicit evidence-bounded surfaces, "
            "and keep public-launch language deferred until "
            "evidence moves beyond runtime_present/descriptive_only on the known short boards."
        ),
        "summary_text": (
            "launch_claims=current:collaborator_beta public_launch:deferred "
            "blocked=continuity_effectiveness,council_decision_quality,live_shared_memory"
        ),
    }


def _build_launch_health_trend_posture(
    *,
    project_memory_summary: Dict[str, Any],
    coordination_mode: Dict[str, Any],
    launch_claim_posture: Dict[str, Any],
) -> Dict[str, Any]:
    evidence_readout = project_memory_summary.get("evidence_readout_posture") or {}
    lanes = list(evidence_readout.get("lanes") or [])
    lane_map = {
        str(item.get("lane", "")).strip(): str(item.get("classification", "")).strip()
        for item in lanes
        if str(item.get("lane", "")).strip()
    }

    continuity_classification = lane_map.get("continuity_effectiveness", "unknown")
    council_quality_classification = lane_map.get("council_decision_quality", "unknown")
    current_tier = str(launch_claim_posture.get("current_tier", "unknown") or "unknown")
    public_launch_ready = bool(launch_claim_posture.get("public_launch_ready", False))
    launch_default_mode = (
        str(coordination_mode.get("launch_default_mode", "unknown")).strip() or "unknown"
    )
    launch_alignment = (
        str(coordination_mode.get("launch_alignment", "unknown")).strip() or "unknown"
    )

    metric_classes = [
        {
            "metric": "current_launch_tier",
            "classification": "descriptive_only",
            "receiver_use": "current_posture_only",
            "note": "Current launch tier is a bounded operating posture, not a forecast of next-tier success.",
        },
        {
            "metric": "public_launch_ready_flag",
            "classification": "descriptive_only",
            "receiver_use": "current_boundary_only",
            "note": "The public_launch_ready flag is a present-tense boundary, not a probability of launch success.",
        },
        {
            "metric": "coordination_backend_alignment",
            "classification": "trendable",
            "receiver_use": "trend_watch_only",
            "note": "Backend mode and launch-default alignment can be trended later across validation waves without becoming predictive today.",
        },
        {
            "metric": "collaborator_beta_validation_health",
            "classification": "trendable",
            "receiver_use": "trend_watch_only",
            "note": "Repeated collaborator-beta validation can become a trend series later, but current packet/session-start still expose only bounded snapshots.",
        },
        {
            "metric": "public_launch_forecast",
            "classification": "forecast_later",
            "receiver_use": "deferred",
            "note": (
                "No calibrated forecast exists yet because continuity effectiveness remains "
                f"{continuity_classification} and council decision quality remains {council_quality_classification}."
            ),
        },
    ]
    trend_watch_cues = [
        {
            "metric": "coordination_backend_alignment",
            "current_value": launch_alignment,
            "watch_for": "alignment_stays_consistent_across_validation_waves",
            "note": "Track whether launch-default coordination stays aligned instead of inferring maturity from one snapshot.",
        },
        {
            "metric": "collaborator_beta_validation_health",
            "current_value": (
                "guided_beta_active" if current_tier == "collaborator_beta" else "not_in_beta_focus"
            ),
            "watch_for": "repeated_validation_without_new_overclaim_pressure",
            "note": "Track repeated collaborator-beta validation quality over time before promoting any broader launch story.",
        },
    ]
    forecast_blockers = [
        {
            "metric": "continuity_effectiveness",
            "classification": continuity_classification,
            "reason": "Continuity effectiveness is still not outcome-calibrated enough to support predictive launch language.",
        },
        {
            "metric": "council_decision_quality",
            "classification": council_quality_classification,
            "reason": "Council decision quality remains descriptive and cannot yet anchor a predictive launch story.",
        },
        {
            "metric": "public_launch_ready_flag",
            "classification": "descriptive_only",
            "reason": "Public launch remains a present-tense boundary rather than a probability estimate.",
        },
    ]
    operator_actions = [
        "Use current launch language as collaborator-beta-only unless a human explicitly narrows it further.",
        "Track trendable metrics across repeated validation waves before changing launch posture wording.",
        "Do not emit predictive launch numbers or success probabilities.",
    ]

    return {
        "summary_text": (
            f"launch_health current={current_tier} public_ready={str(public_launch_ready).lower()} "
            "descriptive=current_launch_tier,public_launch_ready_flag "
            "trendable=coordination_backend_alignment,collaborator_beta_validation_health "
            "forecast_later=public_launch_forecast"
        ),
        "current_state": {
            "current_tier": current_tier,
            "public_launch_ready": public_launch_ready,
            "launch_default_mode": launch_default_mode,
            "launch_alignment": launch_alignment,
            "continuity_effectiveness": continuity_classification,
            "council_decision_quality": council_quality_classification,
        },
        "metric_classes": metric_classes,
        "trend_watch_cues": trend_watch_cues,
        "forecast_blockers": forecast_blockers,
        "operator_actions": operator_actions,
        "forecast_boundary": (
            "Do not emit predictive launch numbers or success probabilities until trendable metrics are collected over time and calibrated separately from descriptive confidence."
        ),
        "receiver_rule": (
            "Treat launch health as a present-tense posture plus future trend lane. Descriptive metrics may orient current honesty, trendable metrics may justify later monitoring, and forecast_later metrics must remain non-numeric for now."
        ),
    }


def _build_internal_state_observability(
    *,
    project_memory_summary: Dict[str, Any],
    risk_posture: Dict[str, Any],
    compactions: list[Dict[str, Any]],
    recent_traces: list[Dict[str, Any]],
) -> Dict[str, Any]:
    risk_level = str(risk_posture.get("level", "unknown") or "unknown").strip()
    coordination_strain = {
        "stable": "low",
        "elevated": "medium",
        "critical": "high",
    }.get(risk_level, "unknown")

    working_style_observability = project_memory_summary.get("working_style_observability") or {}
    continuity_drift = str(working_style_observability.get("drift_risk", "")).strip() or "unknown"

    latest_closeout: Dict[str, Any] = {}
    for entry in compactions:
        normalized_closeout = normalize_closeout_payload(
            entry.get("closeout") if isinstance(entry.get("closeout"), dict) else None,
            pending_paths=list(entry.get("pending_paths") or []),
            next_action=str(entry.get("next_action", "")),
        )
        if normalized_closeout:
            latest_closeout = normalized_closeout
            break

    closeout_status = str(latest_closeout.get("status", "complete") or "complete").strip()
    stop_reason = str(latest_closeout.get("stop_reason", "")).strip()
    if closeout_status in {"blocked", "underdetermined"} or stop_reason in {
        "external_blocked",
        "internal_unstable",
        "divergence_risk",
        "underdetermined",
    }:
        stop_reason_pressure = "high"
    elif closeout_status == "partial" or stop_reason:
        stop_reason_pressure = "medium"
    else:
        stop_reason_pressure = "low"

    council_snapshot: Dict[str, Any] = {}
    for entry in compactions:
        normalized_dossier = _normalize_council_dossier(entry.get("council_dossier"))
        if normalized_dossier:
            council_snapshot = normalized_dossier
            break
    if not council_snapshot:
        for trace in recent_traces:
            summary = _build_council_dossier_summary(trace.get("council_dossier"))
            if summary:
                council_snapshot = summary
                break

    has_minority_report = bool(
        council_snapshot.get("has_minority_report") or council_snapshot.get("minority_report")
    )
    evolution_suppression_flag = bool(council_snapshot.get("evolution_suppression_flag", False))
    confidence_posture = str(council_snapshot.get("confidence_posture", "")).strip()
    deliberation_conflict = (
        "visible"
        if has_minority_report or evolution_suppression_flag or confidence_posture == "contested"
        else "clear"
    )

    evidence_sources = [
        f"risk_posture:{risk_level}",
        f"working_style_drift:{continuity_drift}",
        f"closeout:{closeout_status}",
        f"deliberation_conflict:{deliberation_conflict}",
    ]
    if stop_reason:
        evidence_sources.append(f"stop_reason:{stop_reason}")
    pressure_watch_cues = [
        {
            "signal": "coordination_strain",
            "current_value": coordination_strain,
            "operator_action": (
                "Slow shared side effects and re-read readiness/claims before broader edits."
                if coordination_strain in {"medium", "high"}
                else "Keep shared side effects bounded and keep readiness/claim checks ahead of broader edits."
            ),
        },
        {
            "signal": "continuity_drift",
            "current_value": continuity_drift,
            "operator_action": (
                "Re-read working-style and closeout surfaces before promoting continuity stories."
                if continuity_drift in {"medium", "high"}
                else "Keep continuity cues subordinate to current runtime truth."
            ),
        },
        {
            "signal": "stop_reason_pressure",
            "current_value": stop_reason_pressure,
            "operator_action": (
                "Keep closeout honest and request missing inputs before smooth continuation."
                if stop_reason_pressure in {"medium", "high"}
                else "Preserve explicit closeout even when continuation looks smooth."
            ),
        },
        {
            "signal": "deliberation_conflict",
            "current_value": deliberation_conflict,
            "operator_action": (
                "Treat visible disagreement as real and consider deeper review before forcing consensus."
                if deliberation_conflict != "clear"
                else "Keep disagreement checks available even when current deliberation looks clear."
            ),
        },
    ]
    operator_actions = [
        str(item.get("operator_action", "")).strip() for item in pressure_watch_cues
    ]

    return {
        "summary_text": (
            f"internal_state coordination={coordination_strain} "
            f"drift={continuity_drift} stop_pressure={stop_reason_pressure} "
            f"deliberation={deliberation_conflict}"
        ),
        "current_state": {
            "coordination_strain": coordination_strain,
            "continuity_drift": continuity_drift,
            "stop_reason_pressure": stop_reason_pressure,
            "deliberation_conflict": deliberation_conflict,
            "closeout_status": closeout_status,
            "has_stop_reason": bool(stop_reason),
            "has_minority_report": has_minority_report,
            "evolution_suppression_flag": evolution_suppression_flag,
        },
        "evidence_sources": evidence_sources,
        "pressure_watch_cues": pressure_watch_cues,
        "operator_actions": operator_actions,
        "selfhood_boundary": (
            "These are functional coordination pressures inferred from observable runtime surfaces, not proof of subjective feeling, emotion, or selfhood."
        ),
        "receiver_rule": (
            "Use this readout to notice strain, drift, stop pressure, and visible disagreement early. Do not restate it as hidden-thought access or emotional self-report."
        ),
    }


# ---------------------------------------------------------------------------
# Public API: commit()
# ---------------------------------------------------------------------------


def _commit_locked_posture(store: Any, trace: SessionTrace) -> GovernancePosture:
    # Load current state from the SAME store we'll write to (no split-brain)
    raw = store.get_state()
    if not raw:
        posture = GovernancePosture(last_updated=_utc_now())
    else:
        posture = GovernancePosture.from_dict(raw)
        posture.tension_history = decay_tensions(posture.tension_history)

    # Aegis Shield: check trace BEFORE mutating governance state
    trace_dict = trace.to_dict()
    try:
        from tonesoul.aegis_shield import AegisShield

        shield = AegisShield.load(store)
        trace_dict, content_check = shield.protect_trace(trace_dict, trace.agent)
        if content_check.severity == "blocked":
            print(f"[Aegis] BLOCKED trace from {trace.agent}: {content_check.violations}")
            posture.aegis_vetoes.append(
                {
                    "type": "memory_poisoning",
                    "agent": trace.agent,
                    "violations": content_check.violations,
                    "timestamp": _utc_now(),
                }
            )
            store.set_state(posture.to_dict())
            return posture
        if content_check.violations:
            print(f"[Aegis] WARNING: {content_check.violations}")
        shield.save(store)
    except ImportError:
        pass  # PyNaCl not installed -> skip shield

    for event in trace.tension_events:
        entry = dict(event)
        if "timestamp" not in entry:
            entry["timestamp"] = trace.timestamp
        posture.tension_history.append(entry)

    _pipeline_result = None
    try:
        from tonesoul.memory.pipeline import run_session_end_pipeline

        _pipeline_result = run_session_end_pipeline(
            trace_dict,
            posture.session_count + 1,
        )
    except Exception:
        pass

    _wisdom = _pipeline_result.wisdom_delta if _pipeline_result else 0.0
    posture.soul_integral = update_soul_integral(
        posture.soul_integral,
        posture.last_updated,
        trace.tension_events,
        wisdom_delta=_wisdom,
    )
    posture.baseline_drift = drift_baseline(
        posture.baseline_drift,
        trace.tension_events,
    )

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

    for veto in trace.aegis_vetoes:
        entry = dict(veto)
        if "timestamp" not in entry:
            entry["timestamp"] = trace.timestamp
        posture.aegis_vetoes.append(entry)

    recent_traces_for_risk = list(store.get_traces(n=4))
    recent_traces_for_risk.append(trace_dict)
    claims_for_risk = list_active_claims(store=store)
    compactions_for_risk = list_compactions(store=store, n=5)
    try:
        from tonesoul.risk_calculator import compute_runtime_risk

        posture.risk_posture = compute_runtime_risk(
            posture=posture,
            recent_traces=recent_traces_for_risk[-5:],
            claims=claims_for_risk,
            compactions=compactions_for_risk,
        )
    except Exception:
        posture.risk_posture = {}

    posture.session_count += 1
    posture.last_updated = _utc_now()

    store.set_state(posture.to_dict())
    store.append_trace(trace_dict)

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

    return posture


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
    6. Write updated state  (Redis -> immediate pub/sub push)
    7. Append session trace
    8. Rebuild zone registry
    9. Return the new posture
    """
    from tonesoul.backends.file_store import FileStore
    from tonesoul.store import get_store

    # Backward-compat: explicit paths -> FileStore
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
            subject_snapshots_path=base_dir / ".aegis" / "subject_snapshots.json",
        )
    else:
        store = get_store()

    lock_owner = f"{trace.agent}:{trace.session_id}"
    lock_token = store.acquire_commit_lock(
        lock_owner,
        ttl_seconds=COMMIT_LOCK_TTL_SECONDS,
    )
    if lock_token is None:
        raise CommitConcurrencyError(
            "Another agent is already committing canonical governance state"
        )

    try:
        return _commit_locked_posture(store=store, trace=trace)
    finally:
        try:
            store.release_commit_lock(lock_token)
        except Exception:
            logger.exception("Failed to release commit lock for %s", lock_owner)


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

    risk_posture = dict(posture.risk_posture or {})
    if risk_posture:
        lines.append("")
        lines.append("--- Risk Posture ---")
        lines.append(
            f"  R={float(risk_posture.get('score', 0.0)):.2f}"
            f" ({risk_posture.get('level', 'unknown')})"
        )
        lines.append(f"  Action: {risk_posture.get('recommended_action', 'unknown')}")
        factors = list(risk_posture.get("factors") or [])
        if factors:
            lines.append(f"  Factors: {', '.join(factors)}")

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
    observer_id: str = "",
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
    checkpoints = list_checkpoints(store=store)[:trace_limit]
    compactions = list_compactions(store=store, n=trace_limit)
    subject_snapshots = list_subject_snapshots(store=store, n=max(3, min(trace_limit, 5)))
    routing_events = list_routing_events(store=store, n=max(5, trace_limit))
    from tonesoul.risk_calculator import build_project_memory_summary, compute_runtime_risk

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
        item = {
            "session_id": str(trace.get("session_id", "")),
            "agent": str(trace.get("agent", "unknown")),
            "timestamp": str(trace.get("timestamp", "")),
            "topics": list(trace.get("topics") or []),
            "tension_count": len(trace.get("tension_events") or []),
            "vow_count": len(trace.get("vow_events") or []),
            "aegis_veto_count": len(trace.get("aegis_vetoes") or []),
            "key_decision_count": len(trace.get("key_decisions") or []),
        }
        freshness = _freshness_hours(item.get("timestamp", ""))
        if freshness is not None:
            item["freshness_hours"] = freshness
        council_dossier_summary = _build_council_dossier_summary(trace.get("council_dossier"))
        if council_dossier_summary:
            item["council_dossier_summary"] = council_dossier_summary
        return item

    def _trim_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "task_id": str(claim.get("task_id", "")),
            "agent": str(claim.get("agent", "")),
            "summary": str(claim.get("summary", "")),
            "paths": list(claim.get("paths") or []),
            "source": str(claim.get("source", "")),
            "created_at": str(claim.get("created_at", "")),
            "expires_at": str(claim.get("expires_at", "")),
        }
        freshness = _freshness_hours(item.get("created_at", ""))
        if freshness is not None:
            item["freshness_hours"] = freshness
        return item

    def _trim_compaction(entry: Dict[str, Any]) -> Dict[str, Any]:
        item = {
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
        freshness = _freshness_hours(item.get("updated_at", ""))
        if freshness is not None:
            item["freshness_hours"] = freshness
        council_dossier = _normalize_council_dossier(entry.get("council_dossier"))
        if council_dossier:
            item["council_dossier"] = council_dossier
        closeout = normalize_closeout_payload(
            entry.get("closeout") if isinstance(entry.get("closeout"), dict) else None,
            pending_paths=item.get("pending_paths"),
            next_action=item.get("next_action", ""),
        )
        if closeout:
            item["closeout"] = closeout
        return item

    def _trim_checkpoint(entry: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "checkpoint_id": str(entry.get("checkpoint_id", "")),
            "agent": str(entry.get("agent", "")),
            "session_id": str(entry.get("session_id", "")),
            "summary": str(entry.get("summary", "")),
            "pending_paths": list(entry.get("pending_paths") or []),
            "next_action": str(entry.get("next_action", "")),
            "source": str(entry.get("source", "")),
            "updated_at": str(entry.get("updated_at", "")),
        }
        freshness = _freshness_hours(item.get("updated_at", ""))
        if freshness is not None:
            item["freshness_hours"] = freshness
        return item

    def _trim_subject_snapshot(entry: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "snapshot_id": str(entry.get("snapshot_id", "")),
            "agent": str(entry.get("agent", "")),
            "session_id": str(entry.get("session_id", "")),
            "summary": str(entry.get("summary", "")),
            "stable_vows": list(entry.get("stable_vows") or []),
            "durable_boundaries": list(entry.get("durable_boundaries") or []),
            "decision_preferences": list(entry.get("decision_preferences") or []),
            "verified_routines": list(entry.get("verified_routines") or []),
            "active_threads": list(entry.get("active_threads") or []),
            "evidence_refs": list(entry.get("evidence_refs") or []),
            "refresh_signals": list(entry.get("refresh_signals") or []),
            "source": str(entry.get("source", "")),
            "updated_at": str(entry.get("updated_at", "")),
        }
        freshness = _freshness_hours(item.get("updated_at", ""))
        if freshness is not None:
            item["freshness_hours"] = freshness
        return item

    risk_posture = compute_runtime_risk(
        posture=posture,
        recent_traces=traces[-trace_limit:],
        claims=claims,
        compactions=compactions,
    )
    posture.risk_posture = dict(risk_posture)
    routing_summary = _build_routing_summary(routing_events)
    project_memory_summary = build_project_memory_summary(
        posture=posture,
        recent_traces=traces[-trace_limit:],
        claims=claims,
        compactions=compactions,
        subject_snapshots=subject_snapshots,
        routing_summary=routing_summary,
    )
    subject_refresh = _build_subject_refresh_summary(
        subject_snapshots=subject_snapshots,
        checkpoints=checkpoints,
        compactions=compactions,
        claims=claims,
        routing_summary=routing_summary,
        project_memory_summary=project_memory_summary,
        risk_posture=risk_posture,
    )
    if subject_refresh:
        project_memory_summary["subject_refresh"] = subject_refresh
        refresh_summary = str(subject_refresh.get("summary_text", "")).strip()
        if refresh_summary:
            base_summary = str(project_memory_summary.get("summary_text", "")).strip()
            project_memory_summary["summary_text"] = (
                f"{base_summary} | {refresh_summary}" if base_summary else refresh_summary
            )
    delta_feed = {}
    observer_text = str(observer_id or "").strip()
    if observer_text:
        delta_feed = _build_delta_feed(
            observer_id=observer_text,
            cursor=get_observer_cursor(observer_text, store=store),
            traces=[_trim_trace(t) for t in traces[-trace_limit:]],
            claims=[_trim_claim(c) for c in claims],
            checkpoints=[_trim_checkpoint(c) for c in checkpoints],
            compactions=[_trim_compaction(c) for c in compactions[:trace_limit]],
            subject_snapshots=[
                _trim_subject_snapshot(snapshot) for snapshot in subject_snapshots[:trace_limit]
            ],
            project_memory_summary=project_memory_summary,
        )
    coordination_mode = _build_coordination_mode(
        is_redis=bool(getattr(store, "is_redis", False)),
        observer_id=observer_text,
        delta_feed=delta_feed,
        claims=claims,
        checkpoints=checkpoints[:trace_limit],
        compactions=compactions[:trace_limit],
        subject_snapshots=subject_snapshots[:trace_limit],
        routing_events=routing_summary.get("recent_events", []),
        visitors=visitors[:visitor_limit],
    )
    launch_claim_posture = _build_launch_claim_posture(
        project_memory_summary=project_memory_summary,
        coordination_mode=coordination_mode,
    )
    if launch_claim_posture:
        project_memory_summary["launch_claim_posture"] = launch_claim_posture
        launch_summary = str(launch_claim_posture.get("summary_text", "")).strip()
        if launch_summary:
            base_summary = str(project_memory_summary.get("summary_text", "")).strip()
            project_memory_summary["summary_text"] = (
                f"{base_summary} | {launch_summary}" if base_summary else launch_summary
            )
    launch_health_trend_posture = _build_launch_health_trend_posture(
        project_memory_summary=project_memory_summary,
        coordination_mode=coordination_mode,
        launch_claim_posture=launch_claim_posture,
    )
    if launch_health_trend_posture:
        project_memory_summary["launch_health_trend_posture"] = launch_health_trend_posture
        launch_health_summary = str(launch_health_trend_posture.get("summary_text", "")).strip()
        if launch_health_summary:
            base_summary = str(project_memory_summary.get("summary_text", "")).strip()
            project_memory_summary["summary_text"] = (
                f"{base_summary} | {launch_health_summary}"
                if base_summary
                else launch_health_summary
            )
    internal_state_observability = _build_internal_state_observability(
        project_memory_summary=project_memory_summary,
        risk_posture=risk_posture,
        compactions=compactions,
        recent_traces=traces[-trace_limit:],
    )
    if internal_state_observability:
        project_memory_summary["internal_state_observability"] = internal_state_observability
        internal_state_summary = str(internal_state_observability.get("summary_text", "")).strip()
        if internal_state_summary:
            base_summary = str(project_memory_summary.get("summary_text", "")).strip()
            project_memory_summary["summary_text"] = (
                f"{base_summary} | {internal_state_summary}"
                if base_summary
                else internal_state_summary
            )
    operator_guidance = _build_operator_guidance(
        backend_name=getattr(store, "backend_name", "unknown"),
        is_redis=bool(getattr(store, "is_redis", False)),
        observer_id=observer_text,
        delta_feed=delta_feed,
        claims=claims,
        compactions=compactions,
        traces=traces,
        subject_snapshots=subject_snapshots,
        project_memory_summary=project_memory_summary,
        coordination_mode=coordination_mode,
    )
    consumer_contract = (
        (operator_guidance.get("consumer_contract") or {})
        if isinstance(operator_guidance, dict)
        else {}
    )
    surface_versioning = (
        (operator_guidance.get("surface_versioning") or {})
        if isinstance(operator_guidance, dict)
        else {}
    )

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
            "subject_snapshot_surface": "ts:subject_snapshots",
            "observer_cursor_surface": "ts:observer_cursors:{agent_id}",
            "routing_events_surface": "ts:routing_events",
            "field_surface": "ts:field",
        },
        "canonical_sources": [
            "docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md",
            "docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md",
            "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md",
            "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md",
            "docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md",
            "docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md",
        ],
        "posture": {
            "soul_integral": posture.soul_integral,
            "session_count": posture.session_count,
            "last_updated": posture.last_updated,
            **(
                {"freshness_hours": freshness}
                if (freshness := _freshness_hours(posture.last_updated)) is not None
                else {}
            ),
            "baseline_drift": dict(posture.baseline_drift),
            "risk_posture": dict(risk_posture),
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
        "recent_checkpoints": [_trim_checkpoint(c) for c in checkpoints[:trace_limit]],
        "recent_compactions": [_trim_compaction(c) for c in compactions[:trace_limit]],
        "recent_subject_snapshots": [
            _trim_subject_snapshot(snapshot) for snapshot in subject_snapshots[:trace_limit]
        ],
        "recent_routing_events": routing_summary.get("recent_events", []),
        "project_memory_summary": project_memory_summary,
        "coordination_mode": coordination_mode,
        "consumer_contract": consumer_contract,
        "surface_versioning": surface_versioning,
        "operator_guidance": operator_guidance,
        **({"delta_feed": delta_feed} if observer_text else {}),
    }
