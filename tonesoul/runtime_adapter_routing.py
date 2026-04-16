from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, List, Optional

from tonesoul.runtime_adapter_normalization import clean_string_list


def slug_from_summary(summary: str, *, fallback: str, prefix: str = "") -> str:
    raw = str(summary or "").strip().lower()
    chars: List[str] = []
    previous_dash = False
    for char in raw:
        if char.isalnum():
            chars.append(char)
            previous_dash = False
            continue
        if previous_dash:
            continue
        chars.append("-")
        previous_dash = True
    text = "".join(chars).strip("-")
    if not text:
        text = fallback
    if prefix:
        return f"{prefix}-{text}"
    return text


def route_r_memory_signal(
    *,
    agent_id: str,
    summary: str = "",
    task_id: str = "",
    session_id: str = "",
    paths: Optional[List[str]] = None,
    pending_paths: Optional[List[str]] = None,
    next_action: str = "",
    stance: str = "",
    tensions: Optional[List[str]] = None,
    proposed_drift: Optional[Dict[str, float]] = None,
    proposed_vows: Optional[List[str]] = None,
    carry_forward: Optional[List[str]] = None,
    evidence_refs: Optional[List[str]] = None,
    stable_vows: Optional[List[str]] = None,
    durable_boundaries: Optional[List[str]] = None,
    decision_preferences: Optional[List[str]] = None,
    verified_routines: Optional[List[str]] = None,
    active_threads: Optional[List[str]] = None,
    refresh_signals: Optional[List[str]] = None,
    source: str = "direct",
    prefer_surface: str = "",
) -> Dict[str, Any]:
    """Route a bounded runtime signal toward the most plausible shared surface."""

    normalized_summary = str(summary or "").strip()
    normalized_task_id = str(task_id or "").strip()
    normalized_session_id = str(session_id or "").strip()
    normalized_paths = clean_string_list(paths)
    normalized_pending_paths = clean_string_list(pending_paths)
    normalized_tensions = clean_string_list(tensions)
    normalized_proposed_vows = clean_string_list(proposed_vows)
    normalized_carry_forward = clean_string_list(carry_forward)
    normalized_evidence_refs = clean_string_list(evidence_refs)
    normalized_stable_vows = clean_string_list(stable_vows)
    normalized_durable_boundaries = clean_string_list(durable_boundaries)
    normalized_decision_preferences = clean_string_list(decision_preferences)
    normalized_verified_routines = clean_string_list(verified_routines)
    normalized_active_threads = clean_string_list(active_threads)
    normalized_refresh_signals = clean_string_list(refresh_signals)
    normalized_next_action = str(next_action or "").strip()
    normalized_stance = str(stance or "").strip()
    normalized_source = str(source or "direct").strip() or "direct"
    normalized_prefer_surface = str(prefer_surface or "").strip()

    has_subject_shape = any(
        (
            normalized_stable_vows,
            normalized_durable_boundaries,
            normalized_decision_preferences,
            normalized_verified_routines,
            normalized_active_threads,
            normalized_refresh_signals,
        )
    )
    has_compaction_shape = bool(normalized_carry_forward or normalized_evidence_refs)
    has_perspective_shape = bool(
        normalized_stance
        or normalized_tensions
        or (proposed_drift or {})
        or normalized_proposed_vows
    )
    has_checkpoint_shape = bool(normalized_pending_paths or normalized_next_action)
    has_claim_shape = bool(normalized_task_id)

    valid_surfaces = {
        "claim",
        "perspective",
        "checkpoint",
        "compaction",
        "subject_snapshot",
    }
    if normalized_prefer_surface and normalized_prefer_surface not in valid_surfaces:
        raise ValueError(f"Unknown preferred surface: {normalized_prefer_surface}")

    if normalized_prefer_surface:
        surface = normalized_prefer_surface
        reason = "preferred surface was explicitly requested"
        confidence = "forced"
    elif has_subject_shape:
        surface = "subject_snapshot"
        reason = "stable vows/boundaries/preferences indicate durable working identity"
        confidence = "high"
    elif has_claim_shape and not (
        has_compaction_shape or has_perspective_shape or has_checkpoint_shape
    ):
        surface = "claim"
        reason = "task_id without richer handoff fields indicates task ownership intent"
        confidence = "high"
    elif has_compaction_shape:
        surface = "compaction"
        reason = "carry-forward or evidence refs indicate bounded cross-session handoff"
        confidence = "high"
    elif has_perspective_shape:
        surface = "perspective"
        reason = "stance/tension/proposed drift indicate provisional interpretation"
        confidence = "high"
    elif has_checkpoint_shape:
        surface = "checkpoint"
        reason = "pending paths or next action indicate resumability state"
        confidence = "high"
    elif has_claim_shape:
        surface = "claim"
        reason = "task_id is the strongest remaining ownership signal"
        confidence = "medium"
    else:
        surface = "checkpoint"
        reason = (
            "summary-only updates are safest as resumability checkpoints until a stronger "
            "shape appears"
        )
        confidence = "low"

    payload: Dict[str, Any] = {
        "agent": agent_id,
        "summary": normalized_summary,
        "session_id": normalized_session_id,
        "source": normalized_source,
    }

    if surface == "claim":
        payload.update(
            {
                "task_id": normalized_task_id
                or slug_from_summary(normalized_summary, fallback="task-signal"),
                "paths": normalized_paths or normalized_pending_paths,
            }
        )
    elif surface == "perspective":
        payload.update(
            {
                "stance": normalized_stance or "provisional",
                "tensions": normalized_tensions,
                "proposed_drift": dict(proposed_drift or {}),
                "proposed_vows": normalized_proposed_vows,
                "evidence_refs": normalized_evidence_refs,
            }
        )
    elif surface == "checkpoint":
        payload.update(
            {
                "checkpoint_id": slug_from_summary(
                    normalized_summary,
                    fallback="checkpoint-signal",
                    prefix="cp",
                ),
                "pending_paths": normalized_pending_paths or normalized_paths,
                "next_action": normalized_next_action,
            }
        )
    elif surface == "compaction":
        payload.update(
            {
                "pending_paths": normalized_pending_paths or normalized_paths,
                "carry_forward": normalized_carry_forward,
                "evidence_refs": normalized_evidence_refs,
                "next_action": normalized_next_action,
            }
        )
    elif surface == "subject_snapshot":
        payload.update(
            {
                "stable_vows": normalized_stable_vows,
                "durable_boundaries": normalized_durable_boundaries,
                "decision_preferences": normalized_decision_preferences,
                "verified_routines": normalized_verified_routines,
                "active_threads": normalized_active_threads,
                "evidence_refs": normalized_evidence_refs,
                "refresh_signals": normalized_refresh_signals,
            }
        )

    return {
        "surface": surface,
        "confidence": confidence,
        "reason": reason,
        "payload": payload,
        "secondary_signals": {
            "claim": has_claim_shape,
            "checkpoint": has_checkpoint_shape,
            "compaction": has_compaction_shape,
            "perspective": has_perspective_shape,
            "subject_snapshot": has_subject_shape,
        },
    }


def persist_routed_signal(
    route: Dict[str, Any],
    *,
    claim_writer: Callable[..., Dict[str, Any]],
    perspective_writer: Callable[..., Dict[str, Any]],
    checkpoint_writer: Callable[..., Dict[str, Any]],
    compaction_writer: Callable[..., Dict[str, Any]],
    subject_snapshot_writer: Callable[..., Dict[str, Any]],
    store=None,
    ttl_seconds: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Persist a routed signal via injected surface writers."""

    payload = dict(route.get("payload") or {})
    surface = str(route.get("surface", "")).strip()
    if not surface:
        raise ValueError("route.surface is required")

    if surface == "claim":
        task_id = str(payload.get("task_id", "")).strip()
        return claim_writer(
            task_id,
            agent_id=str(payload.get("agent", "unknown")),
            summary=str(payload.get("summary", "")),
            paths=list(payload.get("paths") or []),
            source=str(payload.get("source", "direct")),
            ttl_seconds=int(ttl_seconds) if ttl_seconds is not None else 1800,
            store=store,
        )

    if surface == "perspective":
        return perspective_writer(
            str(payload.get("agent", "unknown")),
            session_id=str(payload.get("session_id", "")),
            summary=str(payload.get("summary", "")),
            stance=str(payload.get("stance", "")),
            tensions=list(payload.get("tensions") or []),
            proposed_drift=dict(payload.get("proposed_drift") or {}),
            proposed_vows=list(payload.get("proposed_vows") or []),
            evidence_refs=list(payload.get("evidence_refs") or []),
            source=str(payload.get("source", "direct")),
            ttl_seconds=int(ttl_seconds) if ttl_seconds is not None else 7200,
            store=store,
        )

    if surface == "checkpoint":
        return checkpoint_writer(
            str(payload.get("checkpoint_id", "")),
            agent_id=str(payload.get("agent", "unknown")),
            session_id=str(payload.get("session_id", "")),
            summary=str(payload.get("summary", "")),
            pending_paths=list(payload.get("pending_paths") or []),
            next_action=str(payload.get("next_action", "")),
            source=str(payload.get("source", "direct")),
            ttl_seconds=int(ttl_seconds) if ttl_seconds is not None else 86400,
            store=store,
        )

    if surface == "compaction":
        return compaction_writer(
            agent_id=str(payload.get("agent", "unknown")),
            session_id=str(payload.get("session_id", "")),
            summary=str(payload.get("summary", "")),
            carry_forward=list(payload.get("carry_forward") or []),
            pending_paths=list(payload.get("pending_paths") or []),
            evidence_refs=list(payload.get("evidence_refs") or []),
            next_action=str(payload.get("next_action", "")),
            source=str(payload.get("source", "direct")),
            ttl_seconds=int(ttl_seconds) if ttl_seconds is not None else 604800,
            limit=int(limit) if limit is not None else 20,
            store=store,
        )

    if surface == "subject_snapshot":
        return subject_snapshot_writer(
            agent_id=str(payload.get("agent", "unknown")),
            session_id=str(payload.get("session_id", "")),
            summary=str(payload.get("summary", "")),
            stable_vows=list(payload.get("stable_vows") or []),
            durable_boundaries=list(payload.get("durable_boundaries") or []),
            decision_preferences=list(payload.get("decision_preferences") or []),
            verified_routines=list(payload.get("verified_routines") or []),
            active_threads=list(payload.get("active_threads") or []),
            evidence_refs=list(payload.get("evidence_refs") or []),
            refresh_signals=list(payload.get("refresh_signals") or []),
            source=str(payload.get("source", "direct")),
            ttl_seconds=int(ttl_seconds) if ttl_seconds is not None else 2592000,
            limit=int(limit) if limit is not None else 12,
            store=store,
        )

    raise ValueError(f"Unsupported routed surface: {surface}")


def build_routing_event(
    route: Dict[str, Any],
    *,
    action: str = "preview",
    written: bool = False,
    utc_now: Callable[[], str],
) -> Dict[str, Any]:
    normalized_action = str(action or "preview").strip() or "preview"
    if normalized_action not in {"preview", "write"}:
        raise ValueError("action must be preview or write")

    payload = dict(route.get("payload") or {})
    secondary_signals = {
        key: bool(value) for key, value in dict(route.get("secondary_signals") or {}).items()
    }
    secondary_signal_count = sum(1 for value in secondary_signals.values() if value)
    forced = str(route.get("confidence", "")).strip() == "forced"
    overlap = secondary_signal_count > 1
    return {
        "event_id": str(uuid.uuid4()),
        "agent": str(payload.get("agent", "unknown")).strip() or "unknown",
        "session_id": str(payload.get("session_id", "")).strip(),
        "summary": str(payload.get("summary", "")).strip(),
        "surface": str(route.get("surface", "")).strip(),
        "action": normalized_action,
        "written": bool(written),
        "confidence": str(route.get("confidence", "")).strip(),
        "reason": str(route.get("reason", "")).strip(),
        "forced": forced,
        "overlap": overlap,
        "misroute_signal": forced or overlap,
        "secondary_signal_count": int(secondary_signal_count),
        "secondary_signals": secondary_signals,
        "source": str(payload.get("source", "")).strip(),
        "updated_at": utc_now(),
    }


def safe_list_routing_events(
    *,
    get_events: Callable[..., List[Dict[str, Any]]],
    n: int = 10,
) -> List[Dict[str, Any]]:
    try:
        return list(get_events(n=n))
    except Exception:
        return []


def build_routing_summary(
    events: List[Dict[str, Any]],
    *,
    freshness_hours: Optional[Callable[[Any], Optional[float]]] = None,
) -> Dict[str, Any]:
    if not events:
        return {
            "total_events": 0,
            "preview_count": 0,
            "write_count": 0,
            "forced_count": 0,
            "overlap_count": 0,
            "misroute_signal_count": 0,
            "surface_counts": {},
            "recent_agents": [],
            "dominant_surface": "",
            "summary_text": "router=no recent adoption telemetry",
            "recent_events": [],
        }

    preview_count = 0
    write_count = 0
    forced_count = 0
    overlap_count = 0
    misroute_signal_count = 0
    surface_counts: Dict[str, int] = {}
    recent_agents: List[str] = []
    recent_events: List[Dict[str, Any]] = []

    for event in events:
        action = str(event.get("action", "")).strip()
        if action == "write":
            write_count += 1
        else:
            preview_count += 1

        surface = str(event.get("surface", "")).strip()
        if surface:
            surface_counts[surface] = int(surface_counts.get(surface, 0)) + 1

        if bool(event.get("forced", False)):
            forced_count += 1
        if bool(event.get("overlap", False)):
            overlap_count += 1
        if bool(event.get("misroute_signal", False)):
            misroute_signal_count += 1

        agent = str(event.get("agent", "")).strip()
        if agent and agent not in recent_agents:
            recent_agents.append(agent)

        recent_event = {
            "event_id": str(event.get("event_id", "")),
            "agent": agent,
            "surface": surface,
            "action": action,
            "forced": bool(event.get("forced", False)),
            "overlap": bool(event.get("overlap", False)),
            "misroute_signal": bool(event.get("misroute_signal", False)),
            "updated_at": str(event.get("updated_at", "")),
            "summary": str(event.get("summary", "")),
        }
        if freshness_hours is not None:
            freshness = freshness_hours(event.get("updated_at", ""))
            if freshness is not None:
                recent_event["freshness_hours"] = freshness
        recent_events.append(recent_event)

    dominant_surface = ""
    if surface_counts:
        dominant_surface = sorted(surface_counts.items(), key=lambda item: (-item[1], item[0]))[0][
            0
        ]

    summary_text = (
        "router="
        f"writes={write_count} previews={preview_count} "
        f"overrides={forced_count} overlap={overlap_count} "
        f"misroute_signals={misroute_signal_count}"
    )
    if dominant_surface:
        summary_text += f" top={dominant_surface}"

    return {
        "total_events": len(events),
        "preview_count": preview_count,
        "write_count": write_count,
        "forced_count": forced_count,
        "overlap_count": overlap_count,
        "misroute_signal_count": misroute_signal_count,
        "surface_counts": surface_counts,
        "recent_agents": recent_agents[:5],
        "dominant_surface": dominant_surface,
        "summary_text": summary_text,
        "recent_events": recent_events[:5],
    }
