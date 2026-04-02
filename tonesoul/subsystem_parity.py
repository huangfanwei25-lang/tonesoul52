"""Successor-facing subsystem parity and gap readouts."""

from __future__ import annotations

from typing import Any


def _family(
    name: str,
    *,
    status: str,
    current_signal: str,
    strongest_truth: str,
    main_gap: str,
    next_bounded_move: str,
    overclaim_to_avoid: str,
) -> dict[str, str]:
    return {
        "name": name,
        "status": status,
        "current_signal": current_signal,
        "strongest_truth": strongest_truth,
        "main_gap": main_gap,
        "next_bounded_move": next_bounded_move,
        "overclaim_to_avoid": overclaim_to_avoid,
    }


def _class_counts(families: list[dict[str, str]]) -> dict[str, int]:
    counts = {"baseline": 0, "beta_usable": 0, "partial": 0, "deferred": 0}
    for family in families:
        status = str(family.get("status", "")).strip()
        if status in counts:
            counts[status] += 1
    return counts


def build_subsystem_parity_readout(
    *,
    project_memory_summary: dict[str, Any],
    import_posture: dict[str, Any],
    readiness: dict[str, Any],
    task_track_hint: dict[str, Any],
    working_style_validation: dict[str, Any],
    mutation_preflight: dict[str, Any],
    canonical_center: dict[str, Any],
) -> dict[str, Any]:
    """Build a bounded successor-facing subsystem maturity readout."""
    surfaces = import_posture.get("surfaces") or {}
    evidence_readout = project_memory_summary.get("evidence_readout_posture") or {}
    launch_claim_posture = project_memory_summary.get("launch_claim_posture") or {}
    council_surface = surfaces.get("council_dossier") or {}
    council_interpretation = council_surface.get("dossier_interpretation") or {}
    compaction_surface = surfaces.get("compactions") or {}

    readiness_status = str(readiness.get("status", "unknown") or "unknown")
    claim_recommendation = str(
        task_track_hint.get("claim_recommendation", "unknown") or "unknown"
    )
    task_track = str(task_track_hint.get("suggested_track", "unclassified") or "unclassified")
    working_style_status = str(
        working_style_validation.get("status", "insufficient") or "insufficient"
    )
    current_tier = str(launch_claim_posture.get("current_tier", "unknown") or "unknown")
    public_launch_ready = bool(launch_claim_posture.get("public_launch_ready", False))
    evidence_counts = evidence_readout.get("classification_counts") or {}
    continuity_class = "unknown"
    for lane in list(evidence_readout.get("lanes") or []):
        if str(lane.get("lane", "")).strip() == "continuity_effectiveness":
            continuity_class = str(lane.get("classification", "unknown") or "unknown")
            break

    families = [
        _family(
            "session_start_bundle",
            status="baseline",
            current_signal=f"readiness={readiness_status} track={task_track} claim={claim_recommendation}",
            strongest_truth="Session-start exposes readiness, task/deliberation hints, import posture, and bounded successor guards.",
            main_gap="Cold successors still need one tighter parity readout for overall subsystem maturity.",
            next_bounded_move="keep first-hop bundle stable and successor-focused",
            overclaim_to_avoid="session-start alone captures the whole system",
        ),
        _family(
            "observer_window",
            status="baseline",
            current_signal=(
                "short_board_visible"
                if bool((canonical_center.get('current_short_board') or {}).get('present'))
                else "short_board_not_visible"
            ),
            strongest_truth="Stable/contested/stale observer window exists and is regression-backed.",
            main_gap="Anchor ordering is better than before but still relies on successor discipline.",
            next_bounded_move="keep observer output bounded to shell-order orientation",
            overclaim_to_avoid="observer window is canonical truth",
        ),
        _family(
            "receiver_posture",
            status="baseline",
            current_signal=str(import_posture.get("receiver_rule", "") or "receiver_rule_present"),
            strongest_truth="ack/apply/promote ladder is visible across session-start, packet, and diagnose.",
            main_gap="Cold readers can still miss it if they skip first-hop surfaces.",
            next_bounded_move="keep the ladder concentrated in successor-facing surfaces",
            overclaim_to_avoid="every agent will interpret the ladder identically",
        ),
        _family(
            "packet_hot_state",
            status="beta_usable",
            current_signal=(
                f"continuity={continuity_class} evidence_tested={evidence_counts.get('tested', 0)}"
            ),
            strongest_truth="Packet carries freshness, evidence posture, launch claim posture, and realism notes.",
            main_gap="Too many adjacent readouts still compete for attention.",
            next_bounded_move="keep canonical-center and parity ordering visible",
            overclaim_to_avoid="packet equals complete memory",
        ),
        _family(
            "compaction_checkpoint_handoff",
            status="beta_usable",
            current_signal=(
                f"receiver_obligation={str(compaction_surface.get('receiver_obligation', 'unknown') or 'unknown')} "
                f"closeout={str(compaction_surface.get('closeout_status', 'complete') or 'complete')}"
            ),
            strongest_truth="Bounded resumability, closeout grammar, and promotion hazards are visible.",
            main_gap="Smooth summaries can still be over-read if successors ignore closeout and receiver posture.",
            next_bounded_move="tighten closeout surfacing where successors actually read first",
            overclaim_to_avoid="compaction is full task truth",
        ),
        _family(
            "subject_working_style",
            status="partial",
            current_signal=f"validation={working_style_status}",
            strongest_truth="Working-style continuity exists with playbook, limits, observability, and validation.",
            main_gap="Successors can still confuse shared style with identity or authority.",
            next_bounded_move="keep style bounded to advisory workflow habits",
            overclaim_to_avoid="shared style means shared selfhood",
        ),
        _family(
            "council_realism",
            status="partial",
            current_signal=(
                f"calibration={str(council_interpretation.get('calibration_status', 'unknown') or 'unknown')}"
            ),
            strongest_truth="Descriptive-only, dissent, suppression, and realism notes are visible.",
            main_gap="No outcome calibration exists yet.",
            next_bounded_move="preserve realism warnings without pretending calibrated accuracy",
            overclaim_to_avoid="council confidence predicts correctness",
        ),
        _family(
            "evidence_posture",
            status="beta_usable",
            current_signal=(
                f"tested={evidence_counts.get('tested', 0)} runtime_present={evidence_counts.get('runtime_present', 0)} "
                f"descriptive_only={evidence_counts.get('descriptive_only', 0)}"
            ),
            strongest_truth="Evidence posture separates tested, runtime_present, descriptive_only, and document_backed lanes.",
            main_gap="Operator-facing storytelling still needs to stay aligned with this ladder.",
            next_bounded_move="keep evidence posture visible in successor surfaces and launch language",
            overclaim_to_avoid="all current claims are equally proven",
        ),
        _family(
            "collaborator_beta_launch",
            status="beta_usable",
            current_signal=f"current_tier={current_tier} public_ready={'yes' if public_launch_ready else 'no'}",
            strongest_truth="Guided collaborator beta is current truth and public launch remains deferred.",
            main_gap="External deployment and broader live validation are still thinner than the internal story.",
            next_bounded_move="continue bounded beta validation without widening claims",
            overclaim_to_avoid="public launch maturity is ready",
        ),
        _family(
            "mutation_preflight_hooks",
            status="beta_usable",
            current_signal=str(mutation_preflight.get("summary_text", "") or "preflight_present"),
            strongest_truth="Successor-facing mutation preflight now maps current write/mutate/publish decision points.",
            main_gap="Shared-edit overlap is now real, but the outer shell still needs bounded publish/push posture before outward-facing side effects.",
            next_bounded_move=str(
                ((mutation_preflight.get("next_followup") or {}).get("target"))
                or "publish_push.posture_preflight"
            ),
            overclaim_to_avoid="shared-edit mutation is now a full permission system",
        ),
        _family(
            "external_transport_plugins",
            status="deferred",
            current_signal="not_in_launch_default_story",
            strongest_truth="External transport, MCP, and plugin packaging are known future-value lanes.",
            main_gap="They are not needed for current collaborator-beta truth.",
            next_bounded_move="keep parked under external roadmap until current launch-default story is stronger",
            overclaim_to_avoid="ToneSoul already has a mature transport shell",
        ),
    ]

    counts = _class_counts(families)
    return {
        "present": True,
        "families": families,
        "counts": counts,
        "receiver_rule": (
            "Use baseline lanes for normal continuation, beta_usable lanes for guided collaborator-beta work, partial lanes with explicit gap awareness, and deferred lanes as out of current scope."
        ),
        "next_focus": {
            "target": "publish_push.posture_preflight",
            "resolved_to": "tool_permission.publish_push_preflight",
            "reason": "Shared-edit overlap is already a real hook; the next bounded outer-shell gain is publish/push posture before outward-facing side effects.",
        },
        "summary_text": (
            f"subsystem_parity baseline={counts['baseline']} beta_usable={counts['beta_usable']} "
            f"partial={counts['partial']} deferred={counts['deferred']} "
            f"launch={current_tier} readiness={readiness_status}"
        ),
    }
