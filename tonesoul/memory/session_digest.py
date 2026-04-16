"""Session Digest — extract structured learnings from a session trace.

Reflexive extraction: no LLM, no generation. Merges existing structured
data (key_decisions, tension_events, topics) into a compressed journal entry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _tension_summary(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute a tension summary from raw tension events."""
    if not events:
        return {
            "count": 0,
            "max_severity": 0.0,
            "avg_severity": 0.0,
            "resolved_count": 0,
            "unresolved_topics": [],
        }

    severities = [float(e.get("severity", 0.0)) for e in events]
    resolved = [e for e in events if e.get("resolution")]
    unresolved = [e for e in events if not e.get("resolution")]

    return {
        "count": len(events),
        "max_severity": round(max(severities), 4),
        "avg_severity": round(sum(severities) / len(severities), 4),
        "resolved_count": len(resolved),
        "unresolved_topics": [str(e.get("topic", "unknown")) for e in unresolved],
    }


def _compute_coherence(tension_summary: Dict[str, Any]) -> float:
    """Coherence = 1.0 - (avg_severity x unresolved_ratio).

    High coherence = low tension with most issues resolved.
    """
    count = tension_summary.get("count", 0)
    if count == 0:
        return 1.0  # no tension = fully coherent session

    avg_sev = tension_summary.get("avg_severity", 0.0)
    resolved = tension_summary.get("resolved_count", 0)
    unresolved_ratio = 1.0 - (resolved / max(1, count))
    return round(max(0.0, min(1.0, 1.0 - avg_sev * unresolved_ratio)), 4)


def digest_session(
    trace: Dict[str, Any],
    compaction: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract a structured learning digest from a session trace.

    Returns the digest dict (also suitable for writing to self_journal).
    """
    topics = trace.get("topics") or []
    key_decisions = trace.get("key_decisions") or []
    tension_events = trace.get("tension_events") or []
    stance_shift = trace.get("stance_shift")

    # Merge carry_forward from compaction into learnings
    learnings: List[str] = list(key_decisions)
    if compaction:
        carry = compaction.get("carry_forward")
        if isinstance(carry, list):
            learnings.extend(str(c) for c in carry if c)

    ts = _tension_summary(tension_events)
    coherence = _compute_coherence(ts)

    return {
        "timestamp": _utcnow_iso(),
        "type": "session_digest",
        "session_id": trace.get("session_id", str(uuid4())),
        "agent": trace.get("agent", "unknown"),
        "topics": topics,
        "learnings": learnings,
        "tension_summary": ts,
        "stance_shift": stance_shift,
        "coherence_snapshot": coherence,
        "verdict": "digest",
        "genesis": "session_end_pipeline",
        "is_mine": True,
        "actor_type": "system",
    }
