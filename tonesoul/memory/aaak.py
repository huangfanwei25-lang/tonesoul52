"""AAAK Memory Compaction — structured session compression for agent handoff.

AAAK = Anchors · Arcs · Anomalies · Keys

A    Anchors   — What held. Vows that survived, axioms invoked, stable truths.
A    Arcs      — What shifted. Key decisions, drift events, stance changes.
A    Anomalies — What demands attention. Unresolved tension, raised concerns,
                 claims that failed grounding checks.
K    Keys      — What the next agent must know to pick up without losing context.

Design goals:
  - No LLM, no generation. Pure extraction from existing structured data.
  - Output stays under 800 characters when formatted, enabling injection into
    any tier-0 or tier-1 session context without blowing the token budget.
  - Each slot is bounded: max 4 items, each item truncated to 120 chars.
  - The format is self-describing — a reader who has never seen AAAK before
    can parse it cold from the formatted block alone.

Relationship to session_digest:
  session_digest       → detailed structured record for the soul_db
  AAAK                 → ultra-compact handoff artifact for the next agent

The two can coexist. Build the digest first, then compress it to AAAK.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__ts_layer__ = "memory"
__ts_purpose__ = (
    "AAAK compaction: extract the 4-quadrant structured summary from a session "
    "for compact agent handoff."
)

_MAX_ITEMS = 4
_MAX_ITEM_CHARS = 120
_LABEL_WIDTH = 12


# ── Data structure ────────────────────────────────────────────────────────────


@dataclass
class AAAKRecord:
    """A single AAAK-compressed session summary."""

    anchors: List[str]     # what held (vows, axioms, stable facts)
    arcs: List[str]        # what shifted (decisions, stance changes, drift events)
    anomalies: List[str]   # what demands attention (unresolved tension, concerns)
    keys: List[str]        # must-know for the next agent

    session_id: str = ""
    agent_id: str = ""
    compressed_at: str = field(default_factory=lambda: _utcnow())

    def is_empty(self) -> bool:
        return not any([self.anchors, self.arcs, self.anomalies, self.keys])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": "aaak_v1",
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "compressed_at": self.compressed_at,
            "anchors": self.anchors,
            "arcs": self.arcs,
            "anomalies": self.anomalies,
            "keys": self.keys,
        }


# ── Extraction helpers ────────────────────────────────────────────────────────


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clip(text: str, max_chars: int = _MAX_ITEM_CHARS) -> str:
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    return s[:max_chars].rstrip() + "…" if len(s) > max_chars else s


def _pick(items: List[str], limit: int = _MAX_ITEMS) -> List[str]:
    seen: List[str] = []
    for item in items:
        clipped = _clip(item)
        if clipped and clipped not in seen:
            seen.append(clipped)
        if len(seen) >= limit:
            break
    return seen


def _extract_anchors(data: Dict[str, Any]) -> List[str]:
    raw: List[str] = []

    # Vows that confirmed/held
    for vow in data.get("active_vows") or []:
        if isinstance(vow, dict):
            text = vow.get("text") or vow.get("vow") or ""
        else:
            text = str(vow)
        if text:
            raw.append(f"vow: {text}")

    # Axioms explicitly invoked
    for axiom in data.get("axioms_invoked") or []:
        raw.append(f"axiom: {axiom}")

    # Stable outcomes from council
    verdicts = data.get("council_verdicts") or []
    approved = [v for v in verdicts if isinstance(v, dict) and v.get("verdict") == "approve"]
    if approved:
        raw.append(f"council approved {len(approved)} item(s) without objection")

    # Explicit anchor list from compaction
    for item in data.get("anchors") or []:
        raw.append(str(item))

    return _pick(raw)


def _extract_arcs(data: Dict[str, Any]) -> List[str]:
    raw: List[str] = []

    # Key decisions
    for decision in data.get("key_decisions") or []:
        raw.append(str(decision))

    # Drift events (high-significance)
    for event in data.get("drift_events") or []:
        if isinstance(event, dict):
            step = event.get("step", "?")
            reason = event.get("reason") or event.get("description") or ""
            raw.append(f"step {step}: {reason}" if reason else f"drift at step {step}")
        else:
            raw.append(str(event))

    # Stance shifts
    shift = data.get("stance_shift")
    if shift:
        raw.append(f"stance shift: {shift}")

    # Carry-forward from previous compaction that got resolved
    for item in data.get("resolved_carry_forward") or []:
        raw.append(f"resolved: {item}")

    return _pick(raw)


def _extract_anomalies(data: Dict[str, Any]) -> List[str]:
    raw: List[str] = []

    # Tension events that are unresolved
    for event in data.get("tension_events") or []:
        if isinstance(event, dict) and not event.get("resolution"):
            topic = event.get("topic") or event.get("description") or "unknown"
            severity = event.get("severity")
            suffix = f" (sev={severity:.2f})" if isinstance(severity, float) else ""
            raw.append(f"tension: {topic}{suffix}")

    # Council blocks or refine verdicts
    for verdict in data.get("council_verdicts") or []:
        if not isinstance(verdict, dict):
            continue
        v = verdict.get("verdict")
        if v in ("block", "refine"):
            hint = verdict.get("summary") or verdict.get("collapse_warning") or ""
            raw.append(f"{v}: {hint}" if hint else v)

    # Explicit concern list
    for concern in data.get("concerns") or []:
        raw.append(str(concern))

    # Unresolved carry_forward
    for item in data.get("carry_forward") or []:
        raw.append(f"carry: {item}")

    return _pick(raw)


def _extract_keys(data: Dict[str, Any]) -> List[str]:
    raw: List[str] = []

    # Explicit keys
    for key in data.get("keys") or data.get("must_know") or []:
        raw.append(str(key))

    # Current task hint
    task = data.get("task_track_hint") or data.get("current_task") or ""
    if task:
        raw.append(f"task: {task}")

    # Path / working area
    path = data.get("path") or data.get("working_path") or ""
    if path:
        raw.append(f"path: {path}")

    # Summary from end_agent_session
    summary = data.get("summary") or ""
    if summary:
        raw.append(summary)

    # Deliberation mode
    mode = data.get("deliberation_mode_hint") or ""
    if mode:
        raw.append(f"mode: {mode}")

    return _pick(raw)


# ── Public API ────────────────────────────────────────────────────────────────


def compress_to_aaak(
    session_data: Dict[str, Any],
    *,
    session_id: str = "",
    agent_id: str = "",
) -> AAAKRecord:
    """Extract AAAK quadrants from a session data dict.

    ``session_data`` can be a raw session trace, a compaction payload,
    a handoff JSON, or any dict that contains a subset of the known keys.
    Missing keys are silently ignored — the result may have empty quadrants
    but will never raise.
    """
    return AAAKRecord(
        anchors=_extract_anchors(session_data),
        arcs=_extract_arcs(session_data),
        anomalies=_extract_anomalies(session_data),
        keys=_extract_keys(session_data),
        session_id=session_id or str(session_data.get("session_id", "")),
        agent_id=agent_id or str(session_data.get("agent", "")),
    )


def format_handoff_block(record: AAAKRecord, *, label_width: int = _LABEL_WIDTH) -> str:
    """Render a compact AAAK block suitable for injection into handoff notes.

    The output is intentionally terse — a dense 5-line block that a cold
    reader can parse without any prior context.
    """
    def _fmt(label: str, items: List[str]) -> str:
        pad = label.ljust(label_width)
        if not items:
            return f"{pad}—"
        joined = " · ".join(items)
        return f"{pad}{joined}"

    lines = [
        f"{'[AAAK]'.ljust(label_width)}{record.compressed_at}  agent={record.agent_id or '?'}",
        _fmt("Anchors", record.anchors),
        _fmt("Arcs", record.arcs),
        _fmt("Anomalies", record.anomalies),
        _fmt("Keys", record.keys),
    ]
    return "\n".join(lines)


def merge_records(older: AAAKRecord, newer: AAAKRecord) -> AAAKRecord:
    """Merge two AAAK records, keeping the newer session_id and deduplicated items.

    Useful when a session was interrupted and resumed — merge the two partial
    records into a single one before writing to handoff.
    """
    def _merge_lists(a: List[str], b: List[str]) -> List[str]:
        combined = list(a)
        for item in b:
            if item not in combined:
                combined.append(item)
        return combined[:_MAX_ITEMS]

    return AAAKRecord(
        anchors=_merge_lists(older.anchors, newer.anchors),
        arcs=_merge_lists(older.arcs, newer.arcs),
        anomalies=_merge_lists(older.anomalies, newer.anomalies),
        keys=_merge_lists(older.keys, newer.keys),
        session_id=newer.session_id or older.session_id,
        agent_id=newer.agent_id or older.agent_id,
    )
