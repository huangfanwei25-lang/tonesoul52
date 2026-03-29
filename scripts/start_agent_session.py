#!/usr/bin/env python3
"""Run the default ToneSoul session-start bundle in one command."""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

from tonesoul.working_style import build_working_style_playbook


def _ensure_repo_root_on_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


def _resolve_sidecar(root: Path, name: str) -> Path:
    canonical = root / ".aegis" / name
    legacy = root / name
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return canonical


def _build_store(args):
    if args.state_path is None and args.traces_path is None:
        return None

    from tonesoul.backends.file_store import FileStore

    if args.traces_path is not None:
        root = args.traces_path.parent
        zones_path = root / "zone_registry.json"
    elif args.state_path is not None:
        root = args.state_path.parent
        zones_path = root / "zone_registry.json"
    else:
        root = Path(".")
        zones_path = None

    return FileStore(
        gov_path=args.state_path,
        traces_path=args.traces_path,
        zones_path=zones_path,
        claims_path=_resolve_sidecar(root, "task_claims.json"),
        perspectives_path=_resolve_sidecar(root, "perspectives.json"),
        checkpoints_path=_resolve_sidecar(root, "checkpoints.json"),
        compactions_path=_resolve_sidecar(root, "compacted.json"),
        subject_snapshots_path=_resolve_sidecar(root, "subject_snapshots.json"),
        observer_cursors_path=_resolve_sidecar(root, "observer_cursors.json"),
    )


def _quiet_call(fn, *args, **kwargs):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        return fn(*args, **kwargs)


def _build_compact_line(*, agent_id: str, backend_name: str, packet: dict, posture) -> str:
    risk_posture = ((packet.get("posture") or {}).get("risk_posture") or {})
    repo_progress = ((packet.get("project_memory_summary") or {}).get("repo_progress") or {})
    return (
        f"[ToneSoul] {backend_name} | SI={float(getattr(posture, 'soul_integral', 0.0)):.2f} | "
        f"vows={len(getattr(posture, 'active_vows', []) or [])} "
        f"tensions={len(getattr(posture, 'tension_history', []) or [])} | "
        f"R={float(risk_posture.get('score', 0.0)):.2f}/{risk_posture.get('level', 'unknown')} | "
        f"claims={len(packet.get('active_claims', []))} "
        f"checkpoints={len(packet.get('recent_checkpoints', []))} "
        f"compactions={len(packet.get('recent_compactions', []))} "
        f"subjects={len(packet.get('recent_subject_snapshots', []))} | "
        f"git={repo_progress.get('head', 'unknown')}/dirty={int(repo_progress.get('dirty_count', 0) or 0)} | "
        f"agent={agent_id}"
    )


def _looks_like_stop(text: str) -> bool:
    normalized = str(text or "").strip().upper()
    return normalized.startswith("STOP:")


def _parse_iso(text: str) -> datetime | None:
    value = str(text or "").strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _hours_since(timestamp: str) -> float | None:
    dt = _parse_iso(timestamp)
    if dt is None:
        return None
    return round(max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0), 3)


def _latest_freshness(entries: list[dict], *, freshness_key: str = "freshness_hours", timestamp_key: str) -> float | None:
    if not entries:
        return None
    latest = entries[0]
    raw_freshness = latest.get(freshness_key)
    if raw_freshness is not None:
        try:
            return round(float(raw_freshness), 3)
        except (TypeError, ValueError):
            pass
    return _hours_since(str(latest.get(timestamp_key, "")))


def _min_claim_ttl_minutes(claims: list[dict]) -> float | None:
    remaining: list[float] = []
    now = datetime.now(timezone.utc).timestamp()
    for claim in claims:
        raw = str(claim.get("expires_at", "")).strip()
        if not raw:
            continue
        try:
            remaining.append(max(0.0, (float(raw) - now) / 60.0))
        except ValueError:
            continue
    if not remaining:
        return None
    return round(min(remaining), 1)


def _carry_forward_promotion_hazards(subject_refresh: dict) -> list[str]:
    hazards: list[str] = []
    for hazard in list(subject_refresh.get("promotion_hazards") or []):
        text = str(hazard or "").strip()
        if "carry_forward" in text:
            hazards.append(text)
    return hazards


def _latest_council_dossier_snapshot(*, latest_compaction: dict, latest_trace: dict) -> dict:
    if isinstance(latest_compaction.get("council_dossier"), dict):
        payload = latest_compaction.get("council_dossier") or {}
    elif isinstance(latest_trace.get("council_dossier_summary"), dict):
        payload = latest_trace.get("council_dossier_summary") or {}
    else:
        return {}

    decomposition = payload.get("confidence_decomposition") or {}
    snapshot: dict[str, object] = {}
    confidence_posture = str(payload.get("confidence_posture", "")).strip()
    if confidence_posture:
        snapshot["confidence_posture"] = confidence_posture
    if "has_minority_report" in payload:
        snapshot["has_minority_report"] = bool(payload.get("has_minority_report"))
    elif isinstance(payload.get("minority_report"), list):
        snapshot["has_minority_report"] = bool(payload.get("minority_report"))
    if "evolution_suppression_flag" in payload:
        snapshot["evolution_suppression_flag"] = bool(payload.get("evolution_suppression_flag"))

    calibration_status = str(decomposition.get("calibration_status", "")).strip()
    if calibration_status:
        snapshot["calibration_status"] = calibration_status
    adversarial_posture = str(decomposition.get("adversarial_posture", "")).strip()
    if adversarial_posture:
        snapshot["adversarial_posture"] = adversarial_posture
    coverage_posture = str(decomposition.get("coverage_posture", "")).strip()
    if coverage_posture:
        snapshot["coverage_posture"] = coverage_posture
    return snapshot


def _build_readiness(*, agent_id: str, packet: dict, claims: list[dict]) -> dict:
    risk_posture = ((packet.get("posture") or {}).get("risk_posture") or {})
    delta_feed = packet.get("delta_feed") or {}
    project_memory_summary = packet.get("project_memory_summary") or {}

    risk_level = str(risk_posture.get("level", "unknown") or "unknown")
    other_agent_claims = [
        claim
        for claim in list(claims or [])
        if str(claim.get("agent", "")).strip() and str(claim.get("agent", "")).strip() != agent_id
    ]
    fresh_handoff_count = int(
        len(delta_feed.get("new_compactions") or []) + len(delta_feed.get("new_checkpoints") or [])
    )

    recent_stop_actions = [
        str(entry.get("next_action", "")).strip()
        for entry in list(packet.get("recent_compactions") or [])[:3] + list(packet.get("recent_checkpoints") or [])[:3]
        if _looks_like_stop(str(entry.get("next_action", "")).strip())
    ]
    next_actions = [
        action
        for action in (project_memory_summary.get("next_actions") or [])
        if str(action or "").strip()
    ]
    stop_actions = [action for action in next_actions if _looks_like_stop(action)]

    blocking_reasons: list[str] = []
    clarification_reasons: list[str] = []

    if risk_level == "critical":
        blocking_reasons.append("risk_level_is_critical")
    elif risk_level == "high":
        clarification_reasons.append("risk_level_is_high")

    if stop_actions or recent_stop_actions:
        blocking_reasons.append("stop_handoff_present")

    if other_agent_claims:
        clarification_reasons.append("other_agent_claims_visible")

    if not bool(delta_feed.get("first_observation")) and fresh_handoff_count > 0:
        clarification_reasons.append("fresh_handoff_updates_visible")

    if blocking_reasons:
        status = "blocked"
        recommended_action = (
            "Resolve the blocking condition before editing shared work; if the STOP signal or critical risk is not yours to clear, ask a human."
        )
    elif clarification_reasons:
        status = "needs_clarification"
        recommended_action = (
            "Review fresh handoff state, confirm claim overlap, and clarify ambiguous scope before shared edits."
        )
    else:
        status = "pass"
        recommended_action = "Session-start posture is clear enough to classify the task and begin work."

    summary_parts = [
        f"readiness={status}",
        f"risk={risk_level}",
        f"other_claims={len(other_agent_claims)}",
        f"fresh_handoff={fresh_handoff_count}",
        f"stops={len(stop_actions) + len(recent_stop_actions)}",
    ]

    return {
        "status": status,
        "ready": status == "pass",
        "risk_level": risk_level,
        "claim_conflict_count": len(other_agent_claims),
        "other_agent_claims": [
            {
                "task_id": str(claim.get("task_id", "")),
                "agent": str(claim.get("agent", "")),
                "summary": str(claim.get("summary", "")),
            }
            for claim in other_agent_claims[:3]
        ],
        "fresh_handoff_count": fresh_handoff_count,
        "stop_signal_count": len(stop_actions) + len(recent_stop_actions),
        "blocking_reasons": blocking_reasons,
        "clarification_reasons": clarification_reasons,
        "recommended_action": recommended_action,
        "summary_text": " | ".join(summary_parts),
    }


def _build_import_posture(*, packet: dict, readiness: dict) -> dict:
    claims = list(packet.get("active_claims") or [])
    checkpoints = list(packet.get("recent_checkpoints") or [])
    compactions = list(packet.get("recent_compactions") or [])
    subject_snapshots = list(packet.get("recent_subject_snapshots") or [])
    traces = list(packet.get("recent_traces") or [])
    delta_feed = packet.get("delta_feed") or {}
    project_memory_summary = packet.get("project_memory_summary") or {}
    working_style_anchor = project_memory_summary.get("working_style_anchor") or {}
    subject_refresh = project_memory_summary.get("subject_refresh") or {}
    carry_forward_hazards = _carry_forward_promotion_hazards(subject_refresh)

    claim_ttl_minutes = _min_claim_ttl_minutes(claims)
    latest_compaction = compactions[0] if compactions else {}
    latest_trace = traces[0] if traces else {}
    latest_dossier_snapshot = _latest_council_dossier_snapshot(
        latest_compaction=latest_compaction,
        latest_trace=latest_trace,
    )
    latest_dossier_freshness = None
    if latest_compaction.get("council_dossier"):
        latest_dossier_freshness = _latest_freshness(compactions, timestamp_key="updated_at")
    elif latest_trace.get("council_dossier_summary"):
        latest_dossier_freshness = _latest_freshness(traces, timestamp_key="timestamp")

    surfaces = {
        "posture": {
            "present": True,
            "import_posture": "directly_importable",
            "receiver_obligation": "must_read",
            "decay_posture": "none",
            "freshness_hours": float((packet.get("posture") or {}).get("freshness_hours", 0.0) or 0.0),
            "note": "Canonical governance context; use directly for current operating posture.",
        },
        "readiness": {
            "present": True,
            "import_posture": "directly_importable",
            "receiver_obligation": "must_read",
            "decay_posture": "fast",
            "freshness_hours": 0.0,
            "note": "Computed at session start; safe to apply to the current task classification.",
        },
        "claims": {
            "present": bool(claims),
            "import_posture": "directly_importable",
            "receiver_obligation": "must_read",
            "decay_posture": "fast",
            "freshness_hours": _latest_freshness(claims, timestamp_key="created_at"),
            "note": (
                f"Check TTL before overlapping work; shortest remaining claim window is ~{claim_ttl_minutes} minutes."
                if claim_ttl_minutes is not None
                else "Check TTL before overlapping work; active claims are short-lived coordination signals."
            ),
        },
        "delta_feed": {
            "present": bool(delta_feed),
            "import_posture": "ephemeral_until_acked",
            "receiver_obligation": "must_read",
            "decay_posture": "medium",
            "freshness_hours": 0.0,
            "note": "Ack advances the observer cursor; safe to apply after review, never to promote.",
        },
        "checkpoints": {
            "present": bool(checkpoints),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "medium",
            "freshness_hours": _latest_freshness(checkpoints, timestamp_key="updated_at"),
            "note": "Checkpoint next_action can guide resumability, but it is not a canonical work order.",
        },
        "compactions": {
            "present": bool(compactions),
            "import_posture": "advisory",
            "receiver_obligation": "must_not_promote" if carry_forward_hazards else "should_consider",
            "decay_posture": "medium",
            "freshness_hours": _latest_freshness(compactions, timestamp_key="updated_at"),
            "promotion_hazards": carry_forward_hazards,
            "note": (
                "Carry-forward is resumability memory; the latest compaction repeats an older handoff without new evidence, so it may guide review but must not be promoted."
                if carry_forward_hazards
                else "Carry-forward is resumability memory; apply cautiously and never silently promote."
            ),
        },
        "project_memory_summary": {
            "present": bool(project_memory_summary),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "medium",
            "freshness_hours": 0.0,
            "note": "Packet-level aggregation is useful for planning, but it remains a read-time summary surface.",
        },
        "subject_snapshot": {
            "present": bool(subject_snapshots),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": _latest_freshness(subject_snapshots, timestamp_key="updated_at"),
            "note": "Working identity is inheritable but non-canonical; do not promote it into governance truth.",
        },
        "working_style": {
            "present": bool(working_style_anchor),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": _latest_freshness(subject_snapshots, timestamp_key="updated_at"),
            "note": (
                "Shared operating style may guide scan order, evidence discipline, and prompt shape, "
                "but it must not be promoted into vows, canonical rules, or durable identity without fresh proof."
            ),
            "working_style_anchor": working_style_anchor,
        },
        "subject_refresh": {
            "present": bool(subject_refresh),
            "import_posture": "advisory",
            "receiver_obligation": "must_not_promote",
            "decay_posture": "medium",
            "freshness_hours": 0.0 if subject_refresh else None,
            "note": "Refresh guidance may influence review, but it must never auto-promote higher-authority identity fields.",
        },
        "council_dossier": {
            "present": bool(latest_compaction.get("council_dossier") or latest_trace.get("council_dossier_summary")),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": latest_dossier_freshness,
            "note": (
                "Council verdict memory can inform follow-up decisions, but it is not binding precedent; confidence surfaces remain descriptive agreement signals, not calibrated accuracy predictors."
                if str(latest_dossier_snapshot.get("calibration_status", "")).strip() == "descriptive_only"
                else "Council verdict memory can inform follow-up decisions, but it is not binding precedent."
            ),
            "dossier_interpretation": latest_dossier_snapshot,
        },
        "recent_traces": {
            "present": bool(traces),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": _latest_freshness(traces, timestamp_key="timestamp"),
            "note": "Historical traces are descriptive context, not current operational truth.",
        },
        "operator_guidance": {
            "present": bool(packet.get("operator_guidance")),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "medium",
            "freshness_hours": 0.0,
            "note": "Operator guidance should shape workflow order, not become a new P0 constraint.",
        },
    }

    summary_order = [
        "posture",
        "readiness",
        "claims",
        "delta_feed",
        "compactions",
        "subject_snapshot",
        "working_style",
        "council_dossier",
    ]
    summary_parts = []
    for name in summary_order:
        surface = surfaces[name]
        if not surface["present"]:
            continue
        detail = surface["import_posture"]
        freshness = surface.get("freshness_hours")
        if freshness is not None and name not in {"readiness", "delta_feed", "operator_guidance", "project_memory_summary", "subject_refresh"}:
            detail += f"@{float(freshness):.1f}h"
        if name == "claims" and claim_ttl_minutes is not None:
            detail += f"/ttl≈{claim_ttl_minutes:.0f}m"
        if name == "claims" and claim_ttl_minutes is not None and "/ttl" in detail:
            detail = detail.split("/ttl", 1)[0] + f"/ttl≈{claim_ttl_minutes:.0f}m"
        summary_parts.append(f"{name}={detail}")

    receiver_alerts: list[str] = []
    if carry_forward_hazards:
        receiver_alerts.append(
            "Latest carry-forward repeats an older handoff without new evidence; ack or review it, but do not promote it into subject identity or canonical planning."
        )
    if carry_forward_hazards and subject_refresh:
        receiver_alerts.append(
            "Compaction-backed subject refresh is currently blocked by recycled carry-forward evidence; wait for a fresh compaction or stronger evidence before applying active_threads refresh."
        )
    if str(latest_dossier_snapshot.get("calibration_status", "")).strip() == "descriptive_only":
        receiver_alerts.append(
            "Latest council dossier confidence is descriptive_only; treat coherence and confidence posture as internal agreement context, not as an accuracy prediction."
        )
    if bool(latest_dossier_snapshot.get("evolution_suppression_flag")):
        receiver_alerts.append(
            "Latest council dossier indicates potential evolution suppression on repeated dissent; review minority signals carefully before dismissing objections."
        )
    if working_style_anchor:
        receiver_alerts.append(
            "Working-style continuity is advisory only; reuse decision preferences and verified routines as habits, but do not promote them into vows, canonical rules, or durable identity."
        )

    return {
        "summary_text": " | ".join(summary_parts),
        "surfaces": surfaces,
        "receiver_alerts": receiver_alerts,
        "receiver_rule": "ack is safe, apply is bounded, promote requires explicit justification and human confirmation.",
        "readiness_alignment": str(readiness.get("status", "")),
    }


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Run the ToneSoul session-start bundle")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--trace-limit", type=int, default=5)
    parser.add_argument("--visitor-limit", type=int, default=5)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-ack", action="store_true")
    args = parser.parse_args()

    agent_id = str(args.agent or "").strip()
    if not agent_id:
        parser.error("--agent is required")

    from tonesoul.runtime_adapter import (
        acknowledge_observer_cursor,
        list_active_claims,
        load,
        r_memory_packet,
    )
    from tonesoul.store import get_store

    store = _build_store(args)
    if store is None:
        posture = _quiet_call(load, agent_id=agent_id, source="start_agent_session")
        backend_name = getattr(_quiet_call(get_store), "backend_name", "unknown")
    else:
        posture = _quiet_call(
            load,
            state_path=args.state_path,
            agent_id=agent_id,
            source="start_agent_session",
        )
        backend_name = getattr(store, "backend_name", "file")

    packet = _quiet_call(
        r_memory_packet,
        posture=posture,
        store=store,
        observer_id=agent_id,
        trace_limit=args.trace_limit,
        visitor_limit=args.visitor_limit,
    )
    if not args.no_ack:
        acknowledge_observer_cursor(agent_id, packet=packet, store=store)

    claims = _quiet_call(list_active_claims, store=store)
    readiness = _build_readiness(agent_id=agent_id, packet=packet, claims=claims)
    working_style_playbook = build_working_style_playbook(
        ((packet.get("project_memory_summary") or {}).get("working_style_anchor") or {})
    )
    payload = {
        "contract_version": "v1",
        "bundle": "session_start",
        "agent": agent_id,
        "acknowledged_observer_cursor": not args.no_ack,
        "backend_mode": backend_name,
        "compact_diagnostic": _build_compact_line(
            agent_id=agent_id,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
        )
        + f" | readiness={readiness['status']}",
        "readiness": readiness,
        "import_posture": _build_import_posture(packet=packet, readiness=readiness),
        "working_style_playbook": working_style_playbook,
        "claim_view": {
            "count": len(claims),
            "claims": claims,
        },
        "underlying_commands": [
            f"python -m tonesoul.diagnose --agent {agent_id}",
            f"python scripts/run_r_memory_packet.py --agent {agent_id}{'' if args.no_ack else ' --ack'}",
            "python scripts/run_task_claim.py list",
        ],
        "packet": packet,
    }

    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
