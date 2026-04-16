from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from tonesoul.runtime_adapter_normalization import (
    clean_string_list,
    find_recycled_carry_forward_hazard,
)


def _safe_parse_dt(
    raw_timestamp: Any,
    *,
    parse_dt: Callable[[str], Optional[datetime]],
) -> Optional[datetime]:
    try:
        return parse_dt(str(raw_timestamp or ""))
    except Exception:
        return None


def entries_newer_than(
    entries: List[Dict[str, Any]],
    *,
    marker_dt: Optional[datetime],
    parse_dt: Callable[[str], Optional[datetime]],
    timestamp_key: str = "updated_at",
) -> List[Dict[str, Any]]:
    if marker_dt is None:
        return list(entries)
    fresh: List[Dict[str, Any]] = []
    for entry in entries:
        entry_dt = _safe_parse_dt(entry.get(timestamp_key, ""), parse_dt=parse_dt)
        if entry_dt is not None and entry_dt > marker_dt:
            fresh.append(entry)
    return fresh


def build_subject_refresh_summary(
    *,
    subject_snapshots: List[Dict[str, Any]],
    checkpoints: List[Dict[str, Any]],
    compactions: List[Dict[str, Any]],
    claims: List[Dict[str, Any]],
    routing_summary: Dict[str, Any],
    project_memory_summary: Dict[str, Any],
    risk_posture: Dict[str, Any],
    parse_dt: Callable[[str], Optional[datetime]],
) -> Dict[str, Any]:
    latest_snapshot = subject_snapshots[0] if subject_snapshots else {}
    snapshot_dt = _safe_parse_dt(latest_snapshot.get("updated_at", ""), parse_dt=parse_dt)
    newer_checkpoints = entries_newer_than(
        checkpoints,
        marker_dt=snapshot_dt,
        parse_dt=parse_dt,
    )
    newer_compactions = entries_newer_than(
        compactions,
        marker_dt=snapshot_dt,
        parse_dt=parse_dt,
    )

    existing_threads = set(clean_string_list(latest_snapshot.get("active_threads") or []))
    focus_topics = clean_string_list(project_memory_summary.get("focus_topics") or [])
    candidate_threads = [topic for topic in focus_topics if topic not in existing_threads][:4]

    routing_total = int(routing_summary.get("total_events", 0) or 0)
    routing_misroute = int(routing_summary.get("misroute_signal_count", 0) or 0)
    dominant_surface = str(routing_summary.get("dominant_surface", "")).strip()
    risk_level = str(risk_posture.get("level", "")).strip() or "unknown"
    claim_count = len(claims)

    field_guidance: List[Dict[str, Any]] = [
        {
            "field": "stable_vows",
            "action": "must_not_auto_promote",
            "evidence_level": "human_confirmation",
            "candidate_values": [],
            "reason": "Stable vows are constitutional commitments and must never be inferred from hot-state coordination residue.",
        },
        {
            "field": "durable_boundaries",
            "action": "manual_operator_only",
            "evidence_level": "human_confirmation",
            "candidate_values": [],
            "reason": (
                "Durable boundaries may be refreshed only after deliberate review; "
                "transient risk or task pressure must not rewrite them."
            ),
        },
        {
            "field": "decision_preferences",
            "action": "may_influence_only" if routing_total > 0 else "manual_operator_only",
            "evidence_level": "repeat_pattern" if routing_total > 0 else "human_confirmation",
            "candidate_values": (
                [f"dominant routing surface: {dominant_surface}"]
                if dominant_surface and routing_total > 0
                else []
            ),
            "reason": (
                "Routing behavior can inform working preferences, but it should not "
                "auto-promote into durable preferences without operator review."
            ),
        },
        {
            "field": "verified_routines",
            "action": (
                "manual_operator_only"
                if newer_compactions and newer_checkpoints and routing_misroute <= 0
                else "may_influence_only"
            ),
            "evidence_level": (
                "repeat_pattern"
                if newer_compactions and newer_checkpoints and routing_misroute <= 0
                else "single_signal"
            ),
            "candidate_values": (
                ["checkpoint+compaction cadence remained visible across fresh shared surfaces"]
                if newer_compactions and newer_checkpoints and routing_misroute <= 0
                else []
            ),
            "reason": (
                "Repeated clean coordination can justify reviewing verified routines, "
                "but a routine should still be deliberately named before promotion."
            ),
        },
    ]

    if not latest_snapshot and (compactions or checkpoints) and candidate_threads:
        active_thread_action = "may_refresh_directly"
        active_thread_evidence = "compaction-backed" if compactions else "single_signal"
        active_thread_reason = (
            "No subject snapshot exists yet; current focus topics can seed the initial "
            "active_threads lane without promoting higher-risk identity fields."
        )
    elif candidate_threads and newer_compactions:
        active_thread_action = "may_refresh_directly"
        active_thread_evidence = "compaction-backed"
        active_thread_reason = (
            "Fresh compactions newer than the latest snapshot confirm that current focus "
            "topics are durable enough to refresh active_threads."
        )
    elif candidate_threads and len(newer_checkpoints) >= 2:
        active_thread_action = "may_refresh_directly"
        active_thread_evidence = "repeat_pattern"
        active_thread_reason = (
            "Repeated newer checkpoints suggest the current work focus is persistent "
            "enough to refresh active_threads."
        )
    else:
        active_thread_action = "may_influence_only"
        active_thread_evidence = "single_signal" if candidate_threads else "subject_snapshot_only"
        active_thread_reason = (
            "Active threads may track current heat, but weak or stale evidence should "
            "not rewrite them automatically."
        )

    field_guidance.append(
        {
            "field": "active_threads",
            "action": active_thread_action,
            "evidence_level": active_thread_evidence,
            "candidate_values": candidate_threads,
            "reason": active_thread_reason,
        }
    )

    promotion_hazards: List[str] = []
    if claim_count > 0:
        promotion_hazards.append(
            "Do not promote active claims into durable identity; claims are ownership signals, not selfhood."
        )
    if routing_misroute > 0:
        promotion_hazards.append(
            "Do not promote routing ambiguity or forced routes into durable preferences or routines."
        )
    if risk_level not in {"stable", "low", "normal_operation"}:
        promotion_hazards.append(
            "Elevated runtime risk should not auto-promote into stable vows or durable boundaries."
        )
    if newer_checkpoints and not newer_compactions:
        promotion_hazards.append(
            "Checkpoint-only evidence is too weak for durable identity promotion without compaction-backed confirmation."
        )
    recycled_carry_forward_hazard = find_recycled_carry_forward_hazard(
        newer_compactions=newer_compactions,
        all_compactions=compactions,
    )
    if recycled_carry_forward_hazard:
        promotion_hazards.append(recycled_carry_forward_hazard)
    if not latest_snapshot and not compactions:
        promotion_hazards.append(
            "Do not infer durable identity from traces alone when no subject snapshot or compaction-backed evidence exists yet."
        )

    direct_fields = [
        item["field"] for item in field_guidance if item["action"] == "may_refresh_directly"
    ]
    manual_fields = [
        item["field"]
        for item in field_guidance
        if item["action"] in {"manual_operator_only", "must_not_auto_promote"}
    ]

    if not latest_snapshot and not compactions and not checkpoints:
        status = "no_snapshot"
        refresh_recommended = False
    elif not latest_snapshot and (compactions or checkpoints):
        status = "seed_snapshot"
        refresh_recommended = True
    elif direct_fields:
        status = "refresh_candidate"
        refresh_recommended = True
    elif promotion_hazards or newer_checkpoints or newer_compactions:
        status = "manual_review"
        refresh_recommended = False
    elif latest_snapshot:
        status = "stable"
        refresh_recommended = False
    else:
        status = "no_snapshot"
        refresh_recommended = False

    recommended_command = ""
    if refresh_recommended:
        can_apply_active_threads = (
            active_thread_action == "may_refresh_directly"
            and active_thread_evidence == "compaction-backed"
            and not promotion_hazards
            and bool(candidate_threads)
        )
        if can_apply_active_threads:
            recommended_command = (
                "python scripts/apply_subject_refresh.py --agent <your-id> "
                '--field active_threads --refresh-signal "subject-refresh heuristic reviewed"'
            )
        else:
            command_parts = [
                'python scripts/save_subject_snapshot.py --agent <your-id> --summary "..."',
            ]
            for thread in candidate_threads[:2]:
                command_parts.append(f'--thread "{thread}"')
            if direct_fields:
                command_parts.append('--refresh-signal "subject-refresh heuristic reviewed"')
            recommended_command = " ".join(command_parts)

    summary_text = (
        "subject_refresh="
        f"{status} direct={len(direct_fields)} manual={len(manual_fields)} "
        f"hazards={len(promotion_hazards)} "
        f"evidence=c{len(newer_compactions)}/k{len(newer_checkpoints)}"
    )

    return {
        "status": status,
        "refresh_recommended": refresh_recommended,
        "snapshot_present": bool(latest_snapshot),
        "latest_snapshot_id": str(latest_snapshot.get("snapshot_id", "")),
        "snapshot_updated_at": str(latest_snapshot.get("updated_at", "")),
        "risk_level": risk_level,
        "newer_compaction_count": len(newer_compactions),
        "newer_checkpoint_count": len(newer_checkpoints),
        "active_claim_count": claim_count,
        "routing_misroute_signal_count": routing_misroute,
        "field_guidance": field_guidance,
        "promotion_hazards": promotion_hazards[:6],
        "recommended_command": recommended_command,
        "summary_text": summary_text,
    }
