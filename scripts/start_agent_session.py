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


def _ensure_repo_root_on_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


_REPO_ROOT = _ensure_repo_root_on_path()


def _build_working_style_playbook(anchor: dict) -> dict:
    from tonesoul.working_style import build_working_style_playbook

    return build_working_style_playbook(anchor)


def _build_working_style_validation(
    *,
    anchor: dict,
    playbook: dict,
    observability: dict,
    import_limits: dict,
) -> dict:
    from tonesoul.working_style import build_working_style_continuity_validation

    return build_working_style_continuity_validation(
        anchor=anchor,
        playbook=playbook,
        observability=observability,
        import_limits=import_limits,
    )


def _build_receiver_parity(*, council_snapshot: dict, project_memory_summary: dict) -> dict:
    from tonesoul.receiver_posture import build_receiver_parity_readout

    return build_receiver_parity_readout(
        council_snapshot=council_snapshot,
        project_memory_summary=project_memory_summary,
    )


def _build_canonical_center() -> dict:
    from tonesoul.hot_memory import build_canonical_center

    task_path = _REPO_ROOT / "task.md"
    try:
        task_text = task_path.read_text(encoding="utf-8")
    except OSError:
        task_text = ""
    return build_canonical_center(task_text=task_text)


def _build_repo_state_awareness(*, packet: dict) -> dict:
    from tonesoul.repo_state_awareness import build_repo_state_awareness

    return build_repo_state_awareness(
        project_memory_summary=packet.get("project_memory_summary") or {},
        delta_feed=packet.get("delta_feed") or {},
    )


def _build_publish_push_preflight(
    *,
    readiness: dict,
    import_posture: dict,
    repo_state_awareness: dict,
) -> dict:
    from tonesoul.publish_push_preflight import build_publish_push_preflight

    return build_publish_push_preflight(
        readiness=readiness,
        import_posture=import_posture,
        repo_state_awareness=repo_state_awareness,
    )


def _build_task_board_preflight(
    *,
    readiness: dict,
    canonical_center: dict,
    task_track_hint: dict,
) -> dict:
    from tonesoul.task_board_preflight import build_task_board_preflight

    return build_task_board_preflight(
        readiness=readiness,
        canonical_center=canonical_center,
        task_track_hint=task_track_hint,
        proposal_kind="external_idea",
        target_path="task.md",
    )


def _build_hook_chain(*, agent_id: str) -> dict:
    from tonesoul.hook_chain import build_hook_chain_readout

    return build_hook_chain_readout(agent_id=agent_id)


def _build_mutation_preflight(
    *,
    readiness: dict,
    task_track_hint: dict,
    deliberation_mode_hint: dict,
    import_posture: dict,
    canonical_center: dict,
    publish_push_preflight: dict,
    task_board_preflight: dict,
) -> dict:
    from tonesoul.mutation_preflight import build_mutation_preflight

    return build_mutation_preflight(
        readiness=readiness,
        task_track_hint=task_track_hint,
        deliberation_mode_hint=deliberation_mode_hint,
        import_posture=import_posture,
        canonical_center=canonical_center,
        publish_push_preflight=publish_push_preflight,
        task_board_preflight=task_board_preflight,
    )


def _build_subsystem_parity(
    *,
    packet: dict,
    import_posture: dict,
    readiness: dict,
    task_track_hint: dict,
    working_style_validation: dict,
    mutation_preflight: dict,
    canonical_center: dict,
) -> dict:
    from tonesoul.subsystem_parity import build_subsystem_parity_readout

    return build_subsystem_parity_readout(
        project_memory_summary=packet.get("project_memory_summary") or {},
        import_posture=import_posture,
        readiness=readiness,
        task_track_hint=task_track_hint,
        working_style_validation=working_style_validation,
        mutation_preflight=mutation_preflight,
        canonical_center=canonical_center,
    )


def _build_tier0_canonical_center(canonical_center: dict) -> dict:
    current_short_board = canonical_center.get("current_short_board") or {}
    successor_correction = canonical_center.get("successor_correction") or {}
    return {
        "present": bool(canonical_center.get("present")),
        "source_precedence_summary": str(
            canonical_center.get("source_precedence_summary", "")
        ).strip(),
        "current_short_board": {
            "present": bool(current_short_board.get("present")),
            "summary_text": str(current_short_board.get("summary_text", "")).strip(),
        },
        "successor_correction": {
            "summary_text": str(successor_correction.get("summary_text", "")).strip(),
        },
        "summary_text": (
            f"{str(current_short_board.get('summary_text', '')).strip()} | "
            f"{str(successor_correction.get('summary_text', '')).strip()}"
        ).strip(" |"),
    }


def _build_tier0_mutation_preflight(mutation_preflight: dict) -> dict:
    current_context = mutation_preflight.get("current_context") or {}
    next_followup = mutation_preflight.get("next_followup") or {}
    return {
        "present": bool(mutation_preflight.get("present")),
        "summary_text": str(mutation_preflight.get("summary_text", "")).strip(),
        "receiver_rule": str(mutation_preflight.get("receiver_rule", "")).strip(),
        "current_context": {
            "readiness_status": str(current_context.get("readiness_status", "")).strip(),
            "task_track": str(current_context.get("task_track", "")).strip(),
            "deliberation_mode": str(current_context.get("deliberation_mode", "")).strip(),
            "claim_conflict_count": int(current_context.get("claim_conflict_count", 0) or 0),
        },
        "next_followup": {
            "target": str(next_followup.get("target", "")).strip(),
            "classification": str(next_followup.get("classification", "")).strip(),
            "command": str(next_followup.get("command", "")).strip(),
            "reason": str(next_followup.get("reason", "")).strip(),
        },
    }


def _build_tier1_observer_shell(observer_window: dict) -> dict:
    repo_state_awareness = observer_window.get("repo_state_awareness") or {}
    hot_memory_ladder = observer_window.get("hot_memory_ladder") or {}
    return {
        "present": True,
        "summary_text": str(observer_window.get("summary_text", "")).strip(),
        "receiver_note": str(observer_window.get("receiver_note", "")).strip(),
        "counts": dict(observer_window.get("counts") or {}),
        "delta_summary": dict(observer_window.get("delta_summary") or {}),
        "closeout_attention": dict(observer_window.get("closeout_attention") or {}),
        "repo_state_awareness": {
            "classification": str(repo_state_awareness.get("classification", "")).strip(),
            "summary_text": str(repo_state_awareness.get("summary_text", "")).strip(),
            "misread_risk": bool(repo_state_awareness.get("misread_risk", False)),
            "receiver_note": str(repo_state_awareness.get("receiver_note", "")).strip(),
        },
        "hot_memory_ladder": {
            "summary_text": str(hot_memory_ladder.get("summary_text", "")).strip(),
            "layers": [
                {
                    "layer": str(layer.get("layer", "")).strip(),
                    "status": str(layer.get("status", "")).strip(),
                }
                for layer in list(hot_memory_ladder.get("layers") or [])
            ],
        },
        "stable_headlines": [
            str(item.get("claim", "")).strip()
            for item in list(observer_window.get("stable") or [])[:3]
            if str(item.get("claim", "")).strip()
        ],
        "contested_headlines": [
            str(item.get("claim", "")).strip()
            for item in list(observer_window.get("contested") or [])[:3]
            if str(item.get("claim", "")).strip()
        ],
        "stale_headlines": [
            str(item.get("claim", "")).strip()
            for item in list(observer_window.get("stale") or [])[:2]
            if str(item.get("claim", "")).strip()
        ],
    }


def _build_tier0_payload(
    *,
    agent_id: str,
    no_ack: bool,
    backend_name: str,
    packet: dict,
    posture,
    readiness: dict,
    task_track_hint: dict,
    deliberation_mode_hint: dict,
    canonical_center: dict,
    hook_chain: dict,
    mutation_preflight: dict,
) -> dict:
    return {
        "contract_version": "v1",
        "bundle": "session_start",
        "tier": 0,
        "bundle_posture": "fast_path",
        "agent": agent_id,
        "acknowledged_observer_cursor": not no_ack,
        "backend_mode": backend_name,
        "compact_diagnostic": _build_compact_line(
            agent_id=agent_id,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
        )
        + f" | readiness={readiness['status']}",
        "readiness": readiness,
        "task_track_hint": task_track_hint,
        "deliberation_mode_hint": deliberation_mode_hint,
        "canonical_center": _build_tier0_canonical_center(canonical_center),
        "hook_chain": hook_chain,
        "mutation_preflight": _build_tier0_mutation_preflight(mutation_preflight),
        "next_pull": {
            "receiver_rule": (
                "Tier 0 is a minimum safe start. Pull deeper surfaces only if the task is not local/clear, "
                "if claims collide, or if readiness is not pass."
            ),
            "recommended_commands": [
                f"python scripts/start_agent_session.py --agent {agent_id}",
                f"python -m tonesoul.diagnose --agent {agent_id}",
                f"python scripts/run_observer_window.py --agent {agent_id}",
            ],
        },
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent_id}",
            f"python -m tonesoul.diagnose --agent {agent_id}",
            f"python scripts/run_observer_window.py --agent {agent_id}",
        ],
    }


def _build_tier1_payload(
    *,
    agent_id: str,
    no_ack: bool,
    backend_name: str,
    packet: dict,
    posture,
    readiness: dict,
    task_track_hint: dict,
    deliberation_mode_hint: dict,
    canonical_center: dict,
    hook_chain: dict,
    mutation_preflight: dict,
    subsystem_parity: dict,
    observer_window: dict,
) -> dict:
    observer_shell = _build_tier1_observer_shell(observer_window)
    return {
        "contract_version": "v1",
        "bundle": "session_start",
        "tier": 1,
        "bundle_posture": "orientation_shell",
        "agent": agent_id,
        "acknowledged_observer_cursor": not no_ack,
        "backend_mode": backend_name,
        "compact_diagnostic": _build_compact_line(
            agent_id=agent_id,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
        )
        + f" | readiness={readiness['status']}",
        "readiness": readiness,
        "task_track_hint": task_track_hint,
        "deliberation_mode_hint": deliberation_mode_hint,
        "canonical_center": canonical_center,
        "hook_chain": hook_chain,
        "mutation_preflight": _build_tier0_mutation_preflight(mutation_preflight),
        "subsystem_parity": subsystem_parity,
        "observer_shell": observer_shell,
        "closeout_attention": dict(observer_window.get("closeout_attention") or {}),
        "next_pull": {
            "receiver_rule": (
                "Tier 1 is an orientation shell. Pull the full Tier-2 bundle when shared mutation, "
                "deep continuity, or contested governance details must be read directly."
            ),
            "recommended_commands": [
                f"python scripts/start_agent_session.py --agent {agent_id}",
                f"python scripts/run_observer_window.py --agent {agent_id}",
                f"python -m tonesoul.diagnose --agent {agent_id}",
            ],
        },
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent_id}",
            f"python scripts/run_observer_window.py --agent {agent_id}",
            f"python -m tonesoul.diagnose --agent {agent_id}",
        ],
    }


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
    risk_posture = (packet.get("posture") or {}).get("risk_posture") or {}
    repo_progress = (packet.get("project_memory_summary") or {}).get("repo_progress") or {}
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


def _latest_freshness(
    entries: list[dict], *, freshness_key: str = "freshness_hours", timestamp_key: str
) -> float | None:
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
    realism_note = str(payload.get("realism_note", "")).strip()
    if not realism_note:
        has_minority_report = bool(snapshot.get("has_minority_report"))
        suppression_flag = bool(snapshot.get("evolution_suppression_flag"))
        if calibration_status == "descriptive_only":
            if suppression_flag and has_minority_report:
                realism_note = (
                    "Descriptive agreement record only; dissent is visible and suppression risk is flagged, "
                    "so review minority signals before treating approval as settled."
                )
            elif has_minority_report or adversarial_posture == "survived_dissent":
                realism_note = (
                    "Descriptive agreement record only; visible dissent survived review, "
                    "so approval is not equivalent to proven correctness."
                )
            else:
                realism_note = "Descriptive agreement record only; coherence and confidence posture are not calibrated accuracy signals."
        elif suppression_flag and has_minority_report:
            realism_note = "Dissent and possible suppression are both visible; review minority signals before treating the verdict as settled."
        elif has_minority_report:
            realism_note = (
                "Minority dissent is visible; review it before treating approval as settled."
            )
    if realism_note:
        snapshot["realism_note"] = realism_note
    return snapshot


def _build_readiness(*, agent_id: str, packet: dict, claims: list[dict]) -> dict:
    risk_posture = (packet.get("posture") or {}).get("risk_posture") or {}
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
        for entry in list(packet.get("recent_compactions") or [])[:3]
        + list(packet.get("recent_checkpoints") or [])[:3]
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
        recommended_action = "Resolve the blocking condition before editing shared work; if the STOP signal or critical risk is not yours to clear, ask a human."
    elif clarification_reasons:
        status = "needs_clarification"
        recommended_action = "Review fresh handoff state, confirm claim overlap, and clarify ambiguous scope before shared edits."
    else:
        status = "pass"
        recommended_action = (
            "Session-start posture is clear enough to classify the task and begin work."
        )

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


def _clean_path_list(values: list[object] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        text = str(value or "").strip().replace("\\", "/")
        if text and text not in result:
            result.append(text)
    return result


def _is_system_track_path(path: str) -> bool:
    return (
        path == "task.md"
        or path == "AXIOMS.json"
        or path == "README.md"
        or path == "AI_ONBOARDING.md"
        or path == "docs/README.md"
        or path == "docs/INDEX.md"
        or path.startswith("docs/architecture/")
        or path.startswith("spec/")
    )


def _build_task_track_hint(*, packet: dict, readiness: dict) -> dict:
    project_memory_summary = packet.get("project_memory_summary") or {}
    pending_paths = _clean_path_list(project_memory_summary.get("pending_paths") or [])
    carry_forward = [
        str(item or "").strip()
        for item in (project_memory_summary.get("carry_forward") or [])
        if str(item or "").strip()
    ]
    next_actions = [
        str(item or "").strip()
        for item in (project_memory_summary.get("next_actions") or [])
        if str(item or "").strip()
    ]
    focus_topics = [
        str(item or "").strip()
        for item in (project_memory_summary.get("focus_topics") or [])
        if str(item or "").strip()
    ]
    risk_level = str((readiness or {}).get("risk_level", "unknown") or "unknown")

    if not pending_paths and not carry_forward and not next_actions:
        return {
            "present": False,
            "suggested_track": "unclassified",
            "confidence": "low",
            "exploration_depth_hint": "x0",
            "claim_recommendation": "unknown_until_objective_is_visible",
            "review_recommendation": "unknown_until_objective_is_visible",
            "reasons": ["no_visible_scope_surface"],
            "scope_basis": {"pending_paths": [], "focus_topics": [], "next_actions": []},
            "receiver_note": (
                "No resumability scope is visible yet. Read the explicit task objective before assigning a task track."
            ),
            "summary_text": "task_track=unclassified depth=x0 confidence=low scope=none",
        }

    root_families = sorted({path.split("/", 1)[0] for path in pending_paths if path})
    system_paths = [path for path in pending_paths if _is_system_track_path(path)]
    has_cross_family_scope = len(root_families) >= 3
    path_count = len(pending_paths)

    reasons: list[str] = []
    if system_paths:
        reasons.append("canonical_or_architecture_surface_visible")
    if path_count >= 5:
        reasons.append("pending_path_count_ge_5")
    if has_cross_family_scope:
        reasons.append("cross_family_scope_visible")
    if any(path.startswith("tests/") for path in pending_paths) and any(
        path.startswith("tonesoul/") or path.startswith("scripts/") for path in pending_paths
    ):
        reasons.append("implementation_plus_test_scope_visible")
    if risk_level in {"high", "critical"}:
        reasons.append(f"risk_level_{risk_level}")

    if system_paths or path_count >= 5 or has_cross_family_scope:
        suggested_track = "system_track"
        exploration_depth_hint = "x3"
        claim_recommendation = "required"
        review_recommendation = "required"
        confidence = "high" if (system_paths or path_count >= 5) else "medium"
    elif path_count >= 2 or any(
        path.startswith(("tonesoul/", "scripts/", "tests/")) for path in pending_paths
    ):
        suggested_track = "feature_track"
        exploration_depth_hint = "x2"
        claim_recommendation = "required"
        review_recommendation = "conditional"
        confidence = "medium"
    else:
        doc_only = all(path.startswith("docs/") for path in pending_paths)
        suggested_track = "quick_change"
        exploration_depth_hint = "x0" if doc_only and path_count <= 1 else "x1"
        claim_recommendation = "not_required"
        review_recommendation = "not_required"
        confidence = "medium"

    receiver_note = "This task-track hint is advisory and based only on visible session-start scope. The explicit task objective or work order may justify an override."
    if str((readiness or {}).get("status", "")) in {"blocked", "needs_clarification"}:
        receiver_note += " Resolve readiness first, then treat this track as the default starting classification."

    return {
        "present": True,
        "suggested_track": suggested_track,
        "confidence": confidence,
        "exploration_depth_hint": exploration_depth_hint,
        "claim_recommendation": claim_recommendation,
        "review_recommendation": review_recommendation,
        "reasons": reasons,
        "scope_basis": {
            "pending_paths": pending_paths[:8],
            "focus_topics": focus_topics[:3],
            "next_actions": next_actions[:3],
        },
        "receiver_note": receiver_note,
        "summary_text": (
            f"task_track={suggested_track} depth={exploration_depth_hint} "
            f"claim={claim_recommendation} review={review_recommendation} confidence={confidence}"
        ),
    }


def _normalize_risk_bucket(risk_level: str) -> str:
    normalized = str(risk_level or "").strip().lower()
    if normalized == "critical":
        return "critical"
    if normalized == "high":
        return "elevated"
    return "normal"


def _select_resume_deliberation_mode(
    *,
    task_track: str,
    risk_bucket: str,
    claim_collision: bool,
    readiness_state: str,
) -> tuple[str, bool, list[str]]:
    reasons: list[str] = [f"task_track_{task_track}", f"risk_bucket_{risk_bucket}"]
    if claim_collision:
        reasons.append("claim_collision_visible")
    if readiness_state == "needs_clarification":
        reasons.append("readiness_needs_clarification")

    if task_track == "quick_change":
        if claim_collision:
            return "standard_council", False, reasons
        if risk_bucket == "elevated":
            return "standard_council", False, reasons
        return "lightweight_review", False, reasons

    if task_track == "feature_track":
        if readiness_state == "needs_clarification":
            return "standard_council", False, reasons
        if risk_bucket in {"elevated", "critical"}:
            return "elevated_council", risk_bucket == "critical", reasons
        return "standard_council", False, reasons

    if task_track == "system_track":
        return "elevated_council", risk_bucket == "critical", reasons

    return "unclassified", False, reasons


def _build_deliberation_mode_hint(*, task_track_hint: dict, readiness: dict) -> dict:
    if not bool(task_track_hint.get("present")):
        return {
            "present": False,
            "suggested_mode": "unclassified",
            "resume_mode_after_unblock": None,
            "human_required": False,
            "confidence": "low",
            "risk_bucket": "unknown",
            "claim_state": "unknown",
            "readiness_state": str((readiness or {}).get("status", "unknown") or "unknown"),
            "reasons": ["task_track_unclassified"],
            "receiver_note": (
                "No visible task track is available yet. Read the explicit task objective before assigning deliberation depth."
            ),
            "summary_text": "deliberation_mode=unclassified confidence=low",
        }

    readiness_state = str((readiness or {}).get("status", "unknown") or "unknown")
    risk_bucket = _normalize_risk_bucket(
        str((readiness or {}).get("risk_level", "unknown") or "unknown")
    )
    claim_collision = int((readiness or {}).get("claim_conflict_count", 0) or 0) > 0
    claim_state = "active_collision" if claim_collision else "none"
    task_track = str(task_track_hint.get("suggested_track", "unclassified") or "unclassified")
    base_mode, base_human_required, reasons = _select_resume_deliberation_mode(
        task_track=task_track,
        risk_bucket=risk_bucket,
        claim_collision=claim_collision,
        readiness_state=readiness_state,
    )

    if readiness_state == "blocked":
        human_required = (
            bool(base_human_required)
            or int((readiness or {}).get("stop_signal_count", 0) or 0) > 0
            or risk_bucket == "critical"
        )
        reasons = reasons + ["readiness_blocked"]
        if int((readiness or {}).get("stop_signal_count", 0) or 0) > 0:
            reasons.append("stop_handoff_present")
        if human_required:
            reasons.append("human_clearance_required")
        return {
            "present": True,
            "suggested_mode": "do_not_deliberate",
            "resume_mode_after_unblock": base_mode if base_mode != "unclassified" else None,
            "human_required": human_required,
            "confidence": str(task_track_hint.get("confidence", "low") or "low"),
            "risk_bucket": risk_bucket,
            "claim_state": claim_state,
            "readiness_state": readiness_state,
            "reasons": reasons,
            "receiver_note": (
                "The task is blocked, so deliberation should not run yet. Clear the blocking condition first; if a STOP signal or critical risk is present, involve a human before resuming."
            ),
            "summary_text": (
                f"deliberation_mode=do_not_deliberate blocked resume={base_mode} "
                f"human_required={'yes' if human_required else 'no'}"
            ),
        }

    human_required = bool(base_human_required)
    if human_required:
        reasons.append("human_clearance_required")
    receiver_note = "This deliberation-mode hint is advisory and derived from task track, readiness, risk, and claim collision. It does not yet change council runtime depth automatically."
    if readiness_state == "needs_clarification":
        receiver_note += (
            " Clarify the task first, then treat this as the default deliberation depth."
        )

    return {
        "present": True,
        "suggested_mode": base_mode,
        "resume_mode_after_unblock": None,
        "human_required": human_required,
        "confidence": str(task_track_hint.get("confidence", "low") or "low"),
        "risk_bucket": risk_bucket,
        "claim_state": claim_state,
        "readiness_state": readiness_state,
        "reasons": reasons,
        "receiver_note": receiver_note,
        "summary_text": (
            f"deliberation_mode={base_mode} claim_state={claim_state} "
            f"risk_bucket={risk_bucket} human_required={'yes' if human_required else 'no'}"
        ),
    }


def _build_import_posture(*, packet: dict, readiness: dict) -> dict:
    from tonesoul.runtime_adapter import normalize_closeout_payload

    claims = list(packet.get("active_claims") or [])
    checkpoints = list(packet.get("recent_checkpoints") or [])
    compactions = list(packet.get("recent_compactions") or [])
    subject_snapshots = list(packet.get("recent_subject_snapshots") or [])
    traces = list(packet.get("recent_traces") or [])
    delta_feed = packet.get("delta_feed") or {}
    project_memory_summary = packet.get("project_memory_summary") or {}
    working_style_anchor = project_memory_summary.get("working_style_anchor") or {}
    working_style_observability = project_memory_summary.get("working_style_observability") or {}
    working_style_import_limits = project_memory_summary.get("working_style_import_limits") or {}
    evidence_readout_posture = project_memory_summary.get("evidence_readout_posture") or {}
    launch_claim_posture = project_memory_summary.get("launch_claim_posture") or {}
    subject_refresh = project_memory_summary.get("subject_refresh") or {}
    carry_forward_hazards = _carry_forward_promotion_hazards(subject_refresh)

    claim_ttl_minutes = _min_claim_ttl_minutes(claims)
    latest_compaction = compactions[0] if compactions else {}
    latest_compaction_closeout = normalize_closeout_payload(
        latest_compaction.get("closeout") if isinstance(latest_compaction.get("closeout"), dict) else None,
        pending_paths=list(latest_compaction.get("pending_paths") or []),
        next_action=str(latest_compaction.get("next_action", "")),
    )
    latest_compaction_closeout_status = str(latest_compaction_closeout.get("status", "")).strip()
    latest_compaction_stop_reason = str(latest_compaction_closeout.get("stop_reason", "")).strip()
    latest_compaction_unresolved_count = len(
        latest_compaction_closeout.get("unresolved_items") or []
    )
    latest_compaction_human_required = bool(
        latest_compaction_closeout.get("human_input_required", False)
    )
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
            "freshness_hours": float(
                (packet.get("posture") or {}).get("freshness_hours", 0.0) or 0.0
            ),
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
            "receiver_obligation": (
                "must_not_promote"
                if carry_forward_hazards
                else (
                    "must_review"
                    if latest_compaction_closeout_status in {"blocked", "underdetermined"}
                    or latest_compaction_human_required
                    else (
                        "review_before_apply"
                        if latest_compaction_closeout_status == "partial"
                        or latest_compaction_unresolved_count > 0
                        else "should_consider"
                    )
                )
            ),
            "decay_posture": "medium",
            "freshness_hours": _latest_freshness(compactions, timestamp_key="updated_at"),
            "promotion_hazards": carry_forward_hazards,
            "closeout_status": latest_compaction_closeout_status,
            "stop_reason": latest_compaction_stop_reason,
            "unresolved_count": latest_compaction_unresolved_count,
            "human_input_required": latest_compaction_human_required,
            "note": (
                "Carry-forward is resumability memory; the latest compaction repeats an older handoff without new evidence, so it may guide review but must not be promoted."
                if carry_forward_hazards
                else (
                    f"Carry-forward is resumability memory; latest closeout is {latest_compaction_closeout_status or 'complete'}, so review it before continuing."
                    if latest_compaction_closeout_status in {"partial", "blocked", "underdetermined"}
                    else "Carry-forward is resumability memory; apply cautiously and never silently promote."
                )
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
        "evidence_readout": {
            "present": bool(evidence_readout_posture),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": 0.0 if evidence_readout_posture else None,
            "note": (
                "Use this as a fast honesty shortcut: tested means regression-backed enough for workflow assumptions, "
                "runtime_present means mechanism presence, descriptive_only means context not proof, and document_backed means intent or boundary rather than runtime fact."
            ),
            "evidence_readout_posture": evidence_readout_posture,
        },
        "launch_claims": {
            "present": bool(launch_claim_posture),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": 0.0 if launch_claim_posture else None,
            "note": (
                "Use this to bound maturity and launch wording; it is a claim-language guard, not a runtime permission surface."
            ),
            "launch_claim_posture": launch_claim_posture,
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
                if str(working_style_observability.get("status", "")).strip() in {"", "reinforced"}
                else str(working_style_observability.get("receiver_note", "")).strip()
            ),
            "working_style_anchor": working_style_anchor,
            "working_style_observability": working_style_observability,
            "working_style_import_limits": working_style_import_limits,
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
            "present": bool(
                latest_compaction.get("council_dossier")
                or latest_trace.get("council_dossier_summary")
            ),
            "import_posture": "advisory",
            "receiver_obligation": "should_consider",
            "decay_posture": "slow",
            "freshness_hours": latest_dossier_freshness,
            "note": (
                "Council verdict memory can inform follow-up decisions, but it is not binding precedent; confidence surfaces remain descriptive agreement signals, not calibrated accuracy predictors."
                if str(latest_dossier_snapshot.get("calibration_status", "")).strip()
                == "descriptive_only"
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
        "evidence_readout",
        "launch_claims",
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
        if freshness is not None and name not in {
            "readiness",
            "delta_feed",
            "operator_guidance",
            "project_memory_summary",
            "subject_refresh",
        }:
            detail += f"@{float(freshness):.1f}h"
        if name == "claims" and claim_ttl_minutes is not None:
            detail += f"/ttl≈{claim_ttl_minutes:.0f}m"
        if name == "claims" and claim_ttl_minutes is not None and "/ttl" in detail:
            detail = detail.split("/ttl", 1)[0] + f"/ttl≈{claim_ttl_minutes:.0f}m"
        summary_parts.append(f"{name}={detail}")

    if claim_ttl_minutes is not None:
        summary_parts = [
            item.replace("/ttl?claim_ttl_minutes:.0f}m", f"/ttl={claim_ttl_minutes:.0f}m")
            for item in summary_parts
        ]

    if claim_ttl_minutes is not None:
        normalized_summary_parts: list[str] = []
        for item in summary_parts:
            if item.startswith("claims="):
                base = item.split("/ttl", 1)[0]
                item = f"{base}/ttl={claim_ttl_minutes:.0f}m"
            normalized_summary_parts.append(item)
        summary_parts = normalized_summary_parts

    claims_surface = surfaces["claims"]
    if claims_surface["present"] and claim_ttl_minutes is not None:
        claims_detail = str(claims_surface.get("import_posture", "")).strip()
        claims_freshness = claims_surface.get("freshness_hours")
        if claims_freshness is not None:
            claims_detail += f"@{float(claims_freshness):.1f}h"
        claims_detail += f"/ttl={claim_ttl_minutes:.0f}m"
        summary_parts = [
            f"claims={claims_detail}" if item.startswith("claims=") else item
            for item in summary_parts
        ]

    receiver_parity = _build_receiver_parity(
        council_snapshot=latest_dossier_snapshot,
        project_memory_summary=project_memory_summary,
    )
    receiver_alerts = list(
        receiver_parity.get("primary_alerts") or receiver_parity.get("alerts") or []
    )
    if latest_compaction_closeout_status in {"partial", "blocked", "underdetermined"}:
        receiver_alerts.append(
            f"Latest compaction closeout is {latest_compaction_closeout_status}; do not treat the handoff as completed work."
        )
    if latest_compaction_stop_reason:
        receiver_alerts.append(
            f"Latest compaction stop_reason={latest_compaction_stop_reason}; keep the next step bounded to current evidence."
        )
    if latest_compaction_human_required:
        receiver_alerts.append(
            "Latest compaction closeout still requires human input before the next mutation."
        )
    if latest_compaction_unresolved_count > 0:
        receiver_alerts.append(
            f"Latest compaction still carries {latest_compaction_unresolved_count} unresolved item(s); review them before applying the handoff."
        )
    deduped_alerts: list[str] = []
    for alert in receiver_alerts:
        if alert not in deduped_alerts:
            deduped_alerts.append(alert)

    return {
        "summary_text": " | ".join(summary_parts),
        "surfaces": surfaces,
        "receiver_parity": receiver_parity,
        "receiver_alerts": deduped_alerts,
        "receiver_rule": "ack is safe, apply is bounded, promote requires explicit justification and human confirmation.",
        "readiness_alignment": str(readiness.get("status", "")),
    }


def _build_store_from_paths(*, state_path: Path | None, traces_path: Path | None):
    """Build a FileStore from explicit paths, or return None for auto-discovery.

    This is the public-friendly version of _build_store that accepts keyword args
    instead of an argparse namespace.
    """
    if state_path is None and traces_path is None:
        return None

    from tonesoul.backends.file_store import FileStore

    if traces_path is not None:
        root = traces_path.parent
    elif state_path is not None:
        root = state_path.parent
    else:
        root = Path(".")

    zones_path = root / "zone_registry.json"
    return FileStore(
        gov_path=state_path,
        traces_path=traces_path,
        zones_path=zones_path,
        claims_path=_resolve_sidecar(root, "task_claims.json"),
        perspectives_path=_resolve_sidecar(root, "perspectives.json"),
        checkpoints_path=_resolve_sidecar(root, "checkpoints.json"),
        compactions_path=_resolve_sidecar(root, "compacted.json"),
        subject_snapshots_path=_resolve_sidecar(root, "subject_snapshots.json"),
        observer_cursors_path=_resolve_sidecar(root, "observer_cursors.json"),
    )


def run_session_start_bundle(
    *,
    agent_id: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
    trace_limit: int = 5,
    visitor_limit: int = 5,
    no_ack: bool = True,
    tier: int = 2,
) -> dict:
    """Run the full session-start bundle and return the payload dict.

    This is the direct-call equivalent of running ``start_agent_session.py``
    as a subprocess.  Using this function avoids subprocess nesting which
    can hang on Windows due to stdout pipe deadlocks.

    Returns the same JSON-serializable dict that ``main()`` prints to stdout.
    """
    _ensure_repo_root_on_path()

    from tonesoul.runtime_adapter import (
        acknowledge_observer_cursor,
        list_active_claims,
        load,
        r_memory_packet,
    )
    from tonesoul.store import get_store

    store = _build_store_from_paths(state_path=state_path, traces_path=traces_path)
    if store is None:
        posture = _quiet_call(load, agent_id=agent_id, source="start_agent_session")
        backend_name = getattr(_quiet_call(get_store), "backend_name", "unknown")
    else:
        posture = _quiet_call(
            load,
            state_path=state_path,
            agent_id=agent_id,
            source="start_agent_session",
        )
        backend_name = getattr(store, "backend_name", "file")

    packet = _quiet_call(
        r_memory_packet,
        posture=posture,
        store=store,
        observer_id=agent_id,
        trace_limit=trace_limit,
        visitor_limit=visitor_limit,
    )
    if not no_ack:
        acknowledge_observer_cursor(agent_id, packet=packet, store=store)

    claims = _quiet_call(list_active_claims, store=store)
    readiness = _build_readiness(agent_id=agent_id, packet=packet, claims=claims)
    working_style_anchor = (packet.get("project_memory_summary") or {}).get(
        "working_style_anchor"
    ) or {}
    working_style_observability = (packet.get("project_memory_summary") or {}).get(
        "working_style_observability"
    ) or {}
    working_style_import_limits = (packet.get("project_memory_summary") or {}).get(
        "working_style_import_limits"
    ) or {}
    working_style_playbook = _build_working_style_playbook(working_style_anchor)
    working_style_validation = _build_working_style_validation(
        anchor=working_style_anchor,
        playbook=working_style_playbook,
        observability=working_style_observability,
        import_limits=working_style_import_limits,
    )
    canonical_center = _build_canonical_center()
    repo_state_awareness = _build_repo_state_awareness(packet=packet)
    task_track_hint = _build_task_track_hint(packet=packet, readiness=readiness)
    deliberation_mode_hint = _build_deliberation_mode_hint(
        task_track_hint=task_track_hint,
        readiness=readiness,
    )
    import_posture = _build_import_posture(packet=packet, readiness=readiness)
    repo_state_alert = str(repo_state_awareness.get("alert_text", "")).strip()
    if repo_state_alert:
        receiver_alerts = list(import_posture.get("receiver_alerts") or [])
        if repo_state_alert not in receiver_alerts:
            receiver_alerts.append(repo_state_alert)
        import_posture["receiver_alerts"] = receiver_alerts
    publish_push_preflight = _build_publish_push_preflight(
        readiness=readiness,
        import_posture=import_posture,
        repo_state_awareness=repo_state_awareness,
    )
    hook_chain = _build_hook_chain(agent_id=agent_id)
    task_board_preflight = _build_task_board_preflight(
        readiness=readiness,
        canonical_center=canonical_center,
        task_track_hint=task_track_hint,
    )
    mutation_preflight = _build_mutation_preflight(
        readiness=readiness,
        task_track_hint=task_track_hint,
        deliberation_mode_hint=deliberation_mode_hint,
        import_posture=import_posture,
        canonical_center=canonical_center,
        publish_push_preflight=publish_push_preflight,
        task_board_preflight=task_board_preflight,
    )
    if int(tier) == 0:
        return _build_tier0_payload(
            agent_id=agent_id,
            no_ack=no_ack,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
            readiness=readiness,
            task_track_hint=task_track_hint,
            deliberation_mode_hint=deliberation_mode_hint,
            canonical_center=canonical_center,
            hook_chain=hook_chain,
            mutation_preflight=mutation_preflight,
        )
    subsystem_parity = _build_subsystem_parity(
        packet=packet,
        import_posture=import_posture,
        readiness=readiness,
        task_track_hint=task_track_hint,
        working_style_validation=working_style_validation,
        mutation_preflight=mutation_preflight,
        canonical_center=canonical_center,
    )
    if int(tier) == 1:
        from tonesoul.observer_window import build_low_drift_anchor

        observer_window = build_low_drift_anchor(
            packet=packet,
            import_posture=import_posture.get("surfaces") or {},
            readiness=readiness,
            canonical_center=canonical_center,
            subsystem_parity=subsystem_parity,
        )
        return _build_tier1_payload(
            agent_id=agent_id,
            no_ack=no_ack,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
            readiness=readiness,
            task_track_hint=task_track_hint,
            deliberation_mode_hint=deliberation_mode_hint,
            canonical_center=canonical_center,
            hook_chain=hook_chain,
            mutation_preflight=mutation_preflight,
            subsystem_parity=subsystem_parity,
            observer_window=observer_window,
        )
    return {
        "contract_version": "v1",
        "bundle": "session_start",
        "tier": 2,
        "bundle_posture": "full",
        "agent": agent_id,
        "acknowledged_observer_cursor": not no_ack,
        "backend_mode": backend_name,
        "compact_diagnostic": _build_compact_line(
            agent_id=agent_id,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
        )
        + f" | readiness={readiness['status']}",
        "readiness": readiness,
        "task_track_hint": task_track_hint,
        "deliberation_mode_hint": deliberation_mode_hint,
        "import_posture": import_posture,
        "receiver_parity": import_posture.get("receiver_parity", {}),
        "canonical_center": canonical_center,
        "repo_state_awareness": repo_state_awareness,
        "publish_push_preflight": publish_push_preflight,
        "hook_chain": hook_chain,
        "task_board_preflight": task_board_preflight,
        "mutation_preflight": mutation_preflight,
        "subsystem_parity": subsystem_parity,
        "working_style_playbook": working_style_playbook,
        "working_style_validation": working_style_validation,
        "claim_view": {
            "count": len(claims),
            "claims": claims,
        },
        "underlying_commands": [
            f"python -m tonesoul.diagnose --agent {agent_id}",
            f"python scripts/run_r_memory_packet.py --agent {agent_id}{'' if no_ack else ' --ack'}",
            "python scripts/run_task_claim.py list",
            f"python scripts/run_shared_edit_preflight.py --agent {agent_id} --path <repo-path>",
            f"python scripts/run_publish_push_preflight.py --agent {agent_id}",
            (
                f"python scripts/run_task_board_preflight.py --agent {agent_id} "
                "--proposal-kind external_idea --target-path task.md"
            ),
        ],
        "packet": packet,
    }


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Run the ToneSoul session-start bundle")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--trace-limit", type=int, default=5)
    parser.add_argument("--visitor-limit", type=int, default=5)
    parser.add_argument("--tier", type=int, choices=(0, 1, 2), default=2)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-ack", action="store_true")
    args = parser.parse_args()

    agent_id = str(args.agent or "").strip()
    if not agent_id:
        parser.error("--agent is required")

    payload = run_session_start_bundle(
        agent_id=agent_id,
        state_path=args.state_path,
        traces_path=args.traces_path,
        trace_limit=args.trace_limit,
        visitor_limit=args.visitor_limit,
        no_ack=args.no_ack,
        tier=args.tier,
    )

    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
