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

TENSION_DECAY_ALPHA = 0.05        # per hour, ~14h half-life
TENSION_PRUNE_THRESHOLD = 0.01    # drop tensions below this
DRIFT_RATE = 0.001                # 0.1% per session
SCHEMA_VERSION = "0.1.0"

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
    baseline_drift: Dict[str, float] = field(default_factory=lambda: {
        "caution_bias": 0.5,
        "innovation_bias": 0.6,
        "autonomy_level": 0.35,
    })
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

    avg_severity = sum(float(t.get("severity", 0.0)) for t in session_tensions) / len(session_tensions)

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
) -> GovernancePosture:
    """Load governance state at session start.

    1. Read governance_state.json
    2. Decay old tensions
    3. Return the posture for the agent to use

    If the file doesn't exist, returns a fresh default posture.
    """
    path = state_path or _DEFAULT_STATE_PATH

    if not path.exists():
        return GovernancePosture(last_updated=_utc_now())

    raw = json.loads(path.read_text(encoding="utf-8"))
    posture = GovernancePosture.from_dict(raw)

    # Decay tensions since last session
    posture.tension_history = decay_tensions(posture.tension_history)

    return posture


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
    6. Write updated state
    7. Append session trace to JSONL log
    8. Return the new posture

    Returns the updated GovernancePosture.
    """
    s_path = state_path or _DEFAULT_STATE_PATH
    t_path = traces_path or _DEFAULT_TRACES_PATH

    # Load current state (or fresh)
    posture = load(s_path)

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
            posture.active_vows.append({
                "id": vow_id,
                "content": ve.get("detail", ""),
                "created": trace.timestamp[:10],
                "source": f"session:{trace.session_id}",
            })
        elif action == "retired":
            posture.active_vows = [
                v for v in posture.active_vows if v.get("id") != vow_id
            ]

    # Merge aegis vetoes
    for veto in trace.aegis_vetoes:
        entry = dict(veto)
        if "timestamp" not in entry:
            entry["timestamp"] = trace.timestamp
        posture.aegis_vetoes.append(entry)

    # Update metadata
    posture.session_count += 1
    posture.last_updated = _utc_now()

    # Write governance state
    s_path.parent.mkdir(parents=True, exist_ok=True)
    s_path.write_text(
        json.dumps(posture.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Append session trace
    t_path.parent.mkdir(parents=True, exist_ok=True)
    with t_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")

    # Auto-rebuild zone_registry so world map updates immediately
    try:
        from tonesoul.zone_registry import rebuild_and_save
        rebuild_and_save(
            traces_path=t_path,
            governance_path=s_path,
        )
    except Exception:
        pass  # Non-critical — world map still works on next launch

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

    return "\n".join(lines)
