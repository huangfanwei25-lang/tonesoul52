from __future__ import annotations

from typing import Any


def _build_result_surface(
    *,
    status: str,
    registry_recommendation: str,
    supersession_posture: str,
    replay_rule: str,
    residue_posture: str,
    visibility: str,
    carry_forward_rule: str,
) -> dict[str, Any]:
    surface_status_map = {
        "promote": "promoted_result",
        "park": "parked_result",
        "retire": "retired_result",
        "blocked": "blocked_result",
        "not_ready_for_trial": "not_ready_result",
    }
    return {
        "surface_status": surface_status_map.get(status, "unknown_result"),
        "registry_recommendation": registry_recommendation,
        "supersession_posture": supersession_posture,
        "replay_rule": replay_rule,
        "residue_posture": residue_posture,
        "visibility": visibility,
        "carry_forward_rule": carry_forward_rule,
    }


def _build_candidate_record(
    *,
    candidate_id: str,
    target_surface: str,
    target_consumer: str,
    baseline_story: str,
    candidate_story: str,
    success_metric: str,
    failure_mode_watch: str,
    rollback_path: str,
    overclaim_to_avoid: str,
    scope_limit: str,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "target_surface": target_surface,
        "target_consumer": target_consumer,
        "baseline_story": baseline_story,
        "candidate_story": candidate_story,
        "success_metric": success_metric,
        "failure_mode_watch": failure_mode_watch,
        "rollback_path": rollback_path,
        "overclaim_to_avoid": overclaim_to_avoid,
        "scope_limit": scope_limit,
    }


def _build_analyzer_closeout(
    *,
    status: str,
    result_story: str,
    evidence_bundle_summary: str,
    unresolved_items: list[str],
    failure_pressure: str,
    rollback_posture: str,
    promotion_limit: str,
    overclaim_warning: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "result_story": result_story,
        "evidence_bundle_summary": evidence_bundle_summary,
        "unresolved_items": unresolved_items,
        "failure_pressure": failure_pressure,
        "rollback_posture": rollback_posture,
        "promotion_limit": promotion_limit,
        "overclaim_warning": overclaim_warning,
        "next_action": next_action,
    }


def _count_outcomes(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"promote": 0, "park": 0, "retire": 0, "blocked": 0, "not_ready_for_trial": 0}
    for item in items:
        status = ((item.get("analyzer_closeout") or {}).get("status") or "").strip()
        if status in counts:
            counts[status] += 1
    return counts


def build_self_improvement_trial_wave(
    *,
    agent: str,
    consumer_drift_report: dict[str, Any],
    deliberation_hint_probe: dict[str, Any],
    task_board_probe: dict[str, Any],
    shared_edit_probe: dict[str, Any],
    publish_push_probe: dict[str, Any],
    mutation_followup_probe: dict[str, Any],
    surface_versioning_probe: dict[str, Any],
    launch_health_probe: dict[str, Any],
    internal_state_probe: dict[str, Any],
    hook_chain_probe: dict[str, Any] | None = None,
    consumer_misread_guard_probe: dict[str, Any] | None = None,
    subsystem_parity_focus_probe: dict[str, Any] | None = None,
    closeout_attention_probe: dict[str, Any] | None = None,
    claude_priority_correction_probe: dict[str, Any] | None = None,
    hot_memory_pull_boundary_probe: dict[str, Any] | None = None,
    memory_panel_probe: dict[str, Any] | None = None,
    status_panel_probe: dict[str, Any] | None = None,
    command_shelf_probe: dict[str, Any] | None = None,
    operator_retrieval_contract_present: bool,
    compiled_landing_zone_spec_present: bool,
    retrieval_runner_present: bool,
) -> dict[str, Any]:
    consumer_aligned = str(consumer_drift_report.get("status") or "") == "aligned"
    consumer_summary = str(consumer_drift_report.get("summary_text") or "").strip()
    deliberation_hint_ready = bool((deliberation_hint_probe or {}).get("present"))
    deliberation_hint_summary = str(
        (deliberation_hint_probe or {}).get("summary_text") or ""
    ).strip()
    task_board_ready = bool((task_board_probe or {}).get("present"))
    task_board_summary = str((task_board_probe or {}).get("summary_text") or "").strip()
    shared_edit_ready = bool((shared_edit_probe or {}).get("present"))
    shared_edit_summary = str((shared_edit_probe or {}).get("summary_text") or "").strip()
    publish_push_ready = bool((publish_push_probe or {}).get("present"))
    publish_push_summary = str((publish_push_probe or {}).get("summary_text") or "").strip()
    mutation_followup_ready = bool((mutation_followup_probe or {}).get("present"))
    mutation_followup_summary = str(
        (mutation_followup_probe or {}).get("summary_text") or ""
    ).strip()
    surface_versioning_ready = bool((surface_versioning_probe or {}).get("present"))
    surface_versioning_summary = str(
        (surface_versioning_probe or {}).get("summary_text") or ""
    ).strip()
    launch_health_ready = bool((launch_health_probe or {}).get("present"))
    launch_health_summary = str((launch_health_probe or {}).get("summary_text") or "").strip()
    internal_state_ready = bool((internal_state_probe or {}).get("present"))
    internal_state_summary = str((internal_state_probe or {}).get("summary_text") or "").strip()
    hook_chain_ready = bool((hook_chain_probe or {}).get("present"))
    hook_chain_summary = str((hook_chain_probe or {}).get("summary_text") or "").strip()
    consumer_misread_guard_ready = bool((consumer_misread_guard_probe or {}).get("present"))
    consumer_misread_guard_summary = str(
        (consumer_misread_guard_probe or {}).get("summary_text") or ""
    ).strip()
    subsystem_parity_focus_ready = bool((subsystem_parity_focus_probe or {}).get("present"))
    subsystem_parity_focus_summary = str(
        (subsystem_parity_focus_probe or {}).get("summary_text") or ""
    ).strip()
    closeout_attention_ready = bool((closeout_attention_probe or {}).get("present"))
    closeout_attention_summary = str(
        (closeout_attention_probe or {}).get("summary_text") or ""
    ).strip()
    claude_priority_correction_ready = bool((claude_priority_correction_probe or {}).get("present"))
    claude_priority_correction_summary = str(
        (claude_priority_correction_probe or {}).get("summary_text") or ""
    ).strip()
    hot_memory_pull_boundary_ready = bool((hot_memory_pull_boundary_probe or {}).get("present"))
    hot_memory_pull_boundary_summary = str(
        (hot_memory_pull_boundary_probe or {}).get("summary_text") or ""
    ).strip()
    memory_panel_ready = bool((memory_panel_probe or {}).get("present"))
    memory_panel_summary = str((memory_panel_probe or {}).get("summary_text") or "").strip()
    status_panel_ready = bool((status_panel_probe or {}).get("present"))
    status_panel_summary = str((status_panel_probe or {}).get("summary_text") or "").strip()
    command_shelf_ready = bool((command_shelf_probe or {}).get("present"))
    command_shelf_summary = str((command_shelf_probe or {}).get("summary_text") or "").strip()

    consumer_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="consumer_parity_packaging_v1",
            target_surface="consumer_contract.first_hop_order",
            target_consumer="codex_claude_dashboard_observer",
            baseline_story=(
                "Consumer shells historically risked drifting on short-board meaning, closeout reading, "
                "surface-versioning summaries, and fallback order."
            ),
            candidate_story=(
                "The bounded consumer contract, surface versioning, and drift-validation wave now keep the "
                "same first-hop story across Codex-style, Claude-style, dashboard, and observer consumers."
            ),
            success_metric="cross_consumer_drift_validation_wave.status == aligned",
            failure_mode_watch="shared interpretation fracture while one shell still looks cleaner locally",
            rollback_path="revert packaging/readout changes and fall back to Tier-1 session-start ordering",
            overclaim_to_avoid="aligned packaging is not improved reasoning or governance quality",
            scope_limit="packaging and shared interpretation only; no reasoning-runtime or identity change",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if consumer_aligned else "park",
            result_story=(
                "Consumer-parity packaging now reads as aligned across the bounded shells that matter most."
                if consumer_aligned
                else "Consumer-parity packaging still shows drift and should not be promoted yet."
            ),
            evidence_bundle_summary=consumer_summary or "consumer_drift_validation_wave executed",
            unresolved_items=(
                [
                    "alignment is packaging-level only, not proof of better reasoning",
                    "future consumer changes must keep running the same drift wave",
                ]
                if consumer_aligned
                else ["one or more consumers still disagree on closeout or first-hop meaning"]
            ),
            failure_pressure="low" if consumer_aligned else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize council, identity, or transport-semantics changes",
            overclaim_warning="cross-consumer alignment is not outcome calibration or self-improvement of cognition",
            next_action=(
                "reuse this drift-validation wave whenever shared consumer packaging changes"
                if consumer_aligned
                else "repair parity drift before reopening this candidate"
            ),
        ),
    }
    consumer_candidate["result_surface"] = _build_result_surface(
        status=consumer_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result" if consumer_aligned else "distilled_lesson"
        ),
        supersession_posture="active_until_superseded_by_newer_consumer_parity_trial",
        replay_rule="read_status_surface_first_open_raw_run_only_if_consumer_story_is_disputed",
        residue_posture=(
            "keep_visible_in_latest_status_surface"
            if consumer_aligned
            else "keep_in_status_surface_but_do_not_surface_as_current_improvement_win"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future consumer-packaging trials, but does not authorize runtime, governance, or identity promotion"
        ),
    )

    retrieval_ready = (
        operator_retrieval_contract_present
        and compiled_landing_zone_spec_present
        and retrieval_runner_present
    )
    retrieval_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="operator_retrieval_cueing_v1",
            target_surface="operator_retrieval.result_shape",
            target_consumer="operator_shells",
            baseline_story=(
                "Operator retrieval had boundaries and landing-zone ideas, but no final query contract and no "
                "safe carry-forward posture for later operator use."
            ),
            candidate_story=(
                "The operator-retrieval contract now defines query classes, provenance-first return shape, "
                "and non-promotion rules so retrieval can stay auxiliary."
            ),
            success_metric=(
                "operator_retrieval_contract_present and compiled_landing_zone_spec_present and live runner maturity"
            ),
            failure_mode_watch="retrieval reading as runtime truth before a real compiled corpus and safe runner exist",
            rollback_path="revert retrieval-facing packaging and keep retrieval in planning-only posture",
            overclaim_to_avoid="a query contract is not a live retrieval system or solved memory layer",
            scope_limit="operator-facing retrieval packaging only; no runtime truth or identity promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if retrieval_ready else "park",
            result_story=(
                "Operator retrieval is both contract-complete and runtime-ready."
                if retrieval_ready
                else "Operator retrieval packaging is now bounded and safer to reason about, but it is not live enough to promote as an active capability."
            ),
            evidence_bundle_summary=(
                "operator retrieval contract present, compiled landing-zone spec present, live retrieval runner present"
                if retrieval_ready
                else "operator retrieval contract present; compiled landing-zone spec present; no live retrieval runner"
            ),
            unresolved_items=(
                []
                if retrieval_ready
                else [
                    "no live operator-retrieval runner is in the mainline yet",
                    "no compiled corpus or collection health lane exists yet",
                    "no operator validation wave has tested retrieval against real use",
                ]
            ),
            failure_pressure="low" if retrieval_ready else "meaningful",
            rollback_posture="clean_revert",
            promotion_limit="does not authorize retrieval answers to outrank session-start, observer-window, packet, or identity surfaces",
            overclaim_warning="operator-retrieval packaging is not solved knowledge memory and not runtime authority",
            next_action=(
                "keep retrieval under bounded operator use"
                if retrieval_ready
                else "revisit only after a live bounded retrieval runner and compiled collections exist"
            ),
        ),
    }
    retrieval_candidate["result_surface"] = _build_result_surface(
        status=retrieval_candidate["analyzer_closeout"]["status"],
        registry_recommendation="promotion_ready_result" if retrieval_ready else "distilled_lesson",
        supersession_posture="active_until_live_operator_retrieval_trials_exist",
        replay_rule="prefer_status_surface_then_follow_contracts_then_open_raw_run_if_retrieval_posture_is_contested",
        residue_posture=(
            "keep_visible_as_active_auxiliary_result"
            if retrieval_ready
            else "park_in_status_surface_and_reopen_only_when_live_retrieval_lane_exists"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may guide future retrieval packaging, but does not authorize retrieval answers to outrank runtime truth"
        ),
    )

    deliberation_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="deliberation_mode_hint_latency_v2",
            target_surface="session_start.deliberation_mode_hint",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Deliberation-mode hinting already pushed bounded feature work toward lightweight review, "
                "but shells could still over-read escalation ladders as active current pressure."
            ),
            candidate_story=(
                "The deliberation-mode hint now separates `active_escalation_signals`, "
                "`conditional_escalation_triggers`, and `review_cues` so later agents can keep a "
                "lightweight path lightweight without hiding real escalation pressure."
            ),
            success_metric=(
                "deliberation_hint_probe.present and consumer_drift_report.status == aligned"
            ),
            failure_mode_watch=(
                "lightweight paths still look heavier than they are, or shells drift on escalation meaning"
            ),
            rollback_path="revert to the prior deliberation-hint packaging and keep the admitted candidate as history only",
            overclaim_to_avoid="better deliberation hinting is not better deliberation quality or better reasoning",
            scope_limit="session-start packaging only; no council-runtime, claim-truth, or identity change",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (deliberation_hint_ready and consumer_aligned) else "park",
            result_story=(
                "Deliberation-mode hint packaging now cleanly separates active escalation pressure from conditional escalation ladders."
                if (deliberation_hint_ready and consumer_aligned)
                else "Deliberation-mode hint packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                deliberation_hint_summary or "deliberation-hint probe unavailable"
            ),
            unresolved_items=(
                [
                    "packaging wins do not prove better reasoning quality",
                    "future shell consumers must preserve the active/conditional distinction",
                ]
                if (deliberation_hint_ready and consumer_aligned)
                else [
                    "active versus conditional escalation is not yet visible enough",
                    "consumer parity must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (deliberation_hint_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize council runtime depth changes, confidence math changes, or broader shell expansion",
            overclaim_warning="better escalation packaging is not better council independence, accuracy, or calibration",
            next_action=(
                "keep this split stable while evaluating one next admitted self-improvement candidate"
                if (deliberation_hint_ready and consumer_aligned)
                else "repair the deliberation hint split or parity drift before reopening this candidate"
            ),
        ),
    }
    deliberation_candidate["result_surface"] = _build_result_surface(
        status=deliberation_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (deliberation_hint_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_deliberation_hint_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_hint_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (deliberation_hint_ready and consumer_aligned)
            else "park_in_status_surface_until_hint_split_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future routing-packaging trials, but does not authorize deeper council by default"
        ),
    )

    task_board_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="task_board_parking_clarity_v1",
            target_surface="task_board_preflight + mutation_preflight.next_followup",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Task-board parking helpers existed, but later agents could still read parking guidance as soft prose rather than a routing outcome."
            ),
            candidate_story=(
                "Task-board parking now surfaces routing outcome, task.md write allowance, and promotion posture explicitly, while mutation preflight carries the same story forward."
            ),
            success_metric="task_board_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="parking clarity turns into a permission myth or makes ratified follow-through harder than necessary",
            rollback_path="restore the prior task-board parking packaging and keep the result as history only",
            overclaim_to_avoid="better parking clarity is not better planning quality or better governance",
            scope_limit="task-board routing packaging only; no task.md authority rewrite or auto-promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (task_board_ready and consumer_aligned) else "park",
            result_story=(
                "Task-board parking now reads as a bounded routing outcome instead of soft parking prose."
                if (task_board_ready and consumer_aligned)
                else "Task-board parking clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=task_board_summary or "task_board_probe unavailable",
            unresolved_items=(
                [
                    "parking clarity does not prove better planning quality",
                    "future shells must preserve docs_plans_first as routing, not ratification",
                ]
                if (task_board_ready and consumer_aligned)
                else [
                    "task-board routing is not yet visible enough across consumers",
                    "parking clarity still needs parity-safe packaging",
                ]
            ),
            failure_pressure="low" if (task_board_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize task.md auto-promotion, governance semantics changes, or new permission systems",
            overclaim_warning="better parking clarity is not better planning, authority, or human approval",
            next_action=(
                "keep the task-board routing story stable while selecting the next bounded candidate"
                if (task_board_ready and consumer_aligned)
                else "repair task-board packaging drift before reopening this candidate"
            ),
        ),
    }
    task_board_candidate["result_surface"] = _build_result_surface(
        status=task_board_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (task_board_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_task_board_parking_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_task_board_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (task_board_ready and consumer_aligned)
            else "park_in_status_surface_until_task_board_routing_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future task-board routing trials, but does not authorize task.md promotion by itself"
        ),
    )

    shared_edit_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="shared_edit_overlap_clarity_v1",
            target_surface="shared_edit_preflight.result_shape",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Shared-edit preflight already guarded blocked, coordinate, claim-first, and clear outcomes, "
                "but shells could still blur path collision with self-claim gaps into one generic caution."
            ),
            candidate_story=(
                "Shared-edit preflight now surfaces decision basis, explicit other-overlap paths, claim-gap paths, "
                "and bounded pressure flags so later agents can tell coordination friction from claim discipline at a glance."
            ),
            success_metric="shared_edit_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="clearer overlap packaging turns into a fake permission system or hides the need to coordinate first",
            rollback_path="restore the prior shared-edit preflight packaging and keep the result as history only",
            overclaim_to_avoid="better shared-edit overlap clarity is not better collaboration quality or broader mutation authority",
            scope_limit="shared-edit packaging only; no new permission layer, no transport change, no governance semantics rewrite",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (shared_edit_ready and consumer_aligned) else "park",
            result_story=(
                "Shared-edit preflight now shows overlap pressure and claim-gap pressure as separate bounded signals."
                if (shared_edit_ready and consumer_aligned)
                else "Shared-edit overlap packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=shared_edit_summary or "shared_edit_probe unavailable",
            unresolved_items=(
                [
                    "clearer shared-edit packaging does not prove better collaboration outcomes",
                    "future shells must preserve overlap-versus-claim-gap separation without inventing new authority",
                ]
                if (shared_edit_ready and consumer_aligned)
                else [
                    "shared-edit overlap and claim-gap signals are not yet packaged clearly enough",
                    "consumer parity must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (shared_edit_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize automatic claims, path locks, broader write permissions, or governance changes",
            overclaim_warning="better shared-edit packaging is not better planning, coordination quality, or human approval",
            next_action=(
                "keep shared-edit preflight packaging bounded while selecting the next admitted candidate"
                if (shared_edit_ready and consumer_aligned)
                else "repair shared-edit packaging drift before reopening this candidate"
            ),
        ),
    }
    shared_edit_candidate["result_surface"] = _build_result_surface(
        status=shared_edit_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (shared_edit_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_shared_edit_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_shared_edit_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (shared_edit_ready and consumer_aligned)
            else "park_in_status_surface_until_shared_edit_packaging_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future shared-edit packaging trials, but does not authorize new write permissions or claim promotion"
        ),
    )

    publish_push_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="publish_push_posture_clarity_v1",
            target_surface="publish_push_preflight.result_shape",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Publish/push preflight already separated blocked reasons from review posture, "
                "but review cues and launch-claim honesty cues still traveled as one blended list."
            ),
            candidate_story=(
                "Publish/push preflight now separates decision basis, review cues, and honesty cues so later agents can tell side-effect risk from launch-language limits at a glance."
            ),
            success_metric="publish_push_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="clearer publish packaging turns into release optimism or hides hard stop conditions",
            rollback_path="restore the prior publish/push preflight packaging and keep the result as history only",
            overclaim_to_avoid="better publish/push posture clarity is not better launch maturity or safer deployment authority",
            scope_limit="publish/push packaging only; no deployment automation, no launch-tier rewrite, no outward-permission expansion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (publish_push_ready and consumer_aligned) else "park",
            result_story=(
                "Publish/push preflight now separates review posture from launch-honesty posture as bounded signals."
                if (publish_push_ready and consumer_aligned)
                else "Publish/push posture packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=publish_push_summary or "publish_push_probe unavailable",
            unresolved_items=(
                [
                    "clearer publish/push packaging does not prove safer deployment outcomes",
                    "future shells must preserve review-versus-honesty separation without widening authority",
                ]
                if (publish_push_ready and consumer_aligned)
                else [
                    "publish/push review and honesty cues are not yet separated clearly enough",
                    "consumer parity must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (publish_push_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize automatic publish, deployment, or stronger launch claims",
            overclaim_warning="better publish/push packaging is not better release readiness, launch maturity, or human approval",
            next_action=(
                "keep publish/push preflight packaging bounded while selecting the next admitted candidate"
                if (publish_push_ready and consumer_aligned)
                else "repair publish/push packaging drift before reopening this candidate"
            ),
        ),
    }
    publish_push_candidate["result_surface"] = _build_result_surface(
        status=publish_push_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (publish_push_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_publish_push_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_publish_push_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (publish_push_ready and consumer_aligned)
            else "park_in_status_surface_until_publish_push_packaging_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future publish/push packaging trials, but does not authorize release automation or stronger public claims"
        ),
    )

    mutation_followup_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="mutation_followup_routing_v1",
            target_surface="mutation_preflight.next_followup",
            target_consumer="codex_claude_dashboard_observer_operator_shells",
            baseline_story=(
                "Mutation preflight already exposed decision points, but next_followup still pointed too statically and could lag behind the current bounded friction."
            ),
            candidate_story=(
                "Mutation preflight now routes next_followup to the current narrowest bounded hook so successors can move toward shared-edit, publish/push, or task-board review without stale defaults."
            ),
            success_metric="mutation_followup_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="dynamic follow-up routing behaves like a hidden planner or diverges across consumers",
            rollback_path="restore the prior static next_followup packaging and keep the result as history only",
            overclaim_to_avoid="better follow-up routing is not better governance or broader autonomy",
            scope_limit="mutation-followup packaging only; no new hook family, no planner, no permission-system expansion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (mutation_followup_ready and consumer_aligned) else "park",
            result_story=(
                "Mutation preflight now routes next_followup toward the current bounded hook instead of pointing at one stale default."
                if (mutation_followup_ready and consumer_aligned)
                else "Mutation follow-up routing is not yet stable enough to promote."
            ),
            evidence_bundle_summary=mutation_followup_summary
            or "mutation_followup_probe unavailable",
            unresolved_items=(
                [
                    "clearer mutation follow-up routing does not prove better planning quality",
                    "future shells must preserve bounded hook selection without turning it into a planner",
                ]
                if (mutation_followup_ready and consumer_aligned)
                else [
                    "mutation follow-up routing is not yet visible enough across scenarios",
                    "consumer parity must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (mutation_followup_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize new hooks, broader permissions, or governance changes",
            overclaim_warning="better mutation follow-up routing is not better governance, launch maturity, or safe autonomy",
            next_action=(
                "keep mutation follow-up routing bounded while selecting the next admitted candidate"
                if (mutation_followup_ready and consumer_aligned)
                else "repair mutation follow-up routing drift before reopening this candidate"
            ),
        ),
    }
    mutation_followup_candidate["result_surface"] = _build_result_surface(
        status=mutation_followup_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (mutation_followup_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_mutation_followup_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_mutation_followup_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (mutation_followup_ready and consumer_aligned)
            else "park_in_status_surface_until_mutation_followup_routing_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future mutation-preflight packaging trials, but does not authorize new hooks or stronger permissions"
        ),
    )

    surface_versioning_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="surface_versioning_lineage_clarity_v1",
            target_surface="surface_versioning.compatibility_posture",
            target_consumer="codex_claude_dashboard_observer_operator_shells",
            baseline_story=(
                "Surface versioning already exposed versions and parent lineage, but it still lacked one explicit compatibility posture showing which shells are repo-native entries, which are bounded adapters, and what fallback chain preserves parity."
            ),
            candidate_story=(
                "Surface versioning now exposes compatibility posture so later agents can recover consumer roles and shared fallback order without guessing."
            ),
            success_metric="surface_versioning_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="compatibility packaging starts sounding like stronger interop truth or reopens transport mythology",
            rollback_path="remove compatibility posture and keep the prior versioning readout plus drift-wave history only",
            overclaim_to_avoid="clearer lineage packaging is not stronger vendor interop, shared cognition, or transport promotion",
            scope_limit="surface-versioning and consumer-lineage packaging only; no transport, hook, or governance mutation",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (surface_versioning_ready and consumer_aligned) else "park",
            result_story=(
                "Surface versioning now exposes compatibility posture and fallback lineage clearly enough for later shells to recover parent truth without guessing."
                if (surface_versioning_ready and consumer_aligned)
                else "Surface-versioning lineage clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=surface_versioning_summary
            or "surface_versioning_probe unavailable",
            unresolved_items=(
                [
                    "compatibility posture improves lineage clarity, not actual cross-vendor transport",
                    "future shells must keep the fallback chain subordinate to parent runtime truth",
                ]
                if (surface_versioning_ready and consumer_aligned)
                else [
                    "compatibility posture is not yet visible enough across bounded consumers",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (surface_versioning_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize new transport semantics, shell promotion, or vendor-native interoperability claims",
            overclaim_warning="clearer versioning lineage is not stronger shared understanding or transport truth",
            next_action=(
                "keep compatibility posture bounded while admitting the next candidate"
                if (surface_versioning_ready and consumer_aligned)
                else "repair versioning lineage clarity before reopening this candidate"
            ),
        ),
    }
    surface_versioning_candidate["result_surface"] = _build_result_surface(
        status=surface_versioning_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (surface_versioning_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_versioning_lineage_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_surface_versioning_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (surface_versioning_ready and consumer_aligned)
            else "park_in_status_surface_until_surface_versioning_lineage_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future consumer-lineage packaging trials, but does not authorize transport promotion or stronger interoperability claims"
        ),
    )

    launch_health_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="launch_health_trend_clarity_v1",
            target_surface="launch_health_trend_posture",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Launch-health posture already separated descriptive, trendable, and forecast-later metrics, but operators still had to infer what to watch next and why forecast language remained blocked."
            ),
            candidate_story=(
                "Launch-health posture now exposes trend-watch cues, forecast blockers, and operator actions so current honesty and future trend watching are clearer without adding fake predictive math."
            ),
            success_metric="launch_health_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="launch-health packaging starts reading like predictive maturity or inflated launch readiness",
            rollback_path="remove the added launch-health packaging cues and keep the prior posture plus registry history only",
            overclaim_to_avoid="clearer launch-health packaging is not predictive launch scoring or broader public readiness",
            scope_limit="launch and validation readout packaging only; no forecast math, no launch-tier rewrite, no deployment authority change",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (launch_health_ready and consumer_aligned) else "park",
            result_story=(
                "Launch-health posture now says what to watch, what blocks forecasting, and what operators may safely do now without implying predictive math."
                if (launch_health_ready and consumer_aligned)
                else "Launch-health trend clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=launch_health_summary or "launch_health_probe unavailable",
            unresolved_items=(
                [
                    "clearer launch-health packaging does not create predictive launch numbers",
                    "future consumers must keep trend-watch cues subordinate to present-tense launch posture",
                ]
                if (launch_health_ready and consumer_aligned)
                else [
                    "launch-health trend cues are not yet visible enough across bounded consumers",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (launch_health_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize predictive launch math, stronger maturity claims, or deployment authority changes",
            overclaim_warning="clearer launch-health packaging is not public-launch readiness or predictive success scoring",
            next_action=(
                "keep launch-health cues bounded while admitting the next candidate"
                if (launch_health_ready and consumer_aligned)
                else "repair launch-health trend clarity before reopening this candidate"
            ),
        ),
    }
    launch_health_candidate["result_surface"] = _build_result_surface(
        status=launch_health_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (launch_health_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_launch_health_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_launch_health_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (launch_health_ready and consumer_aligned)
            else "park_in_status_surface_until_launch_health_trend_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future launch and validation readout trials, but does not authorize predictive launch math or stronger public claims"
        ),
    )

    internal_state_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="internal_state_observability_clarity_v1",
            target_surface="internal_state_observability.pressure_watch_cues",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Internal-state observability already surfaced functional pressures, but operators still had to infer what practical action each pressure implied."
            ),
            candidate_story=(
                "Internal-state observability now exposes pressure-watch cues and bounded operator actions so strain, drift, stop pressure, and deliberation conflict can guide handling without turning into selfhood or emotion claims."
            ),
            success_metric="internal_state_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="internal-state packaging starts sounding like emotion, hidden thought, or personhood",
            rollback_path="remove the added internal-state cues/actions and keep the prior observability posture plus registry history only",
            overclaim_to_avoid="clearer functional pressure cues are not self-awareness, emotion detection, or deeper consciousness",
            scope_limit="internal-state observability packaging only; no selfhood claims, no hidden-thought inference, no governance mutation",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (internal_state_ready and consumer_aligned) else "park",
            result_story=(
                "Internal-state observability now says what pressures are visible and what bounded operator response fits each pressure without crossing into selfhood language."
                if (internal_state_ready and consumer_aligned)
                else "Internal-state action clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=internal_state_summary or "internal_state_probe unavailable",
            unresolved_items=(
                [
                    "functional pressure cues do not prove subjective feeling or self-awareness",
                    "future consumers must keep action cues subordinate to the selfhood boundary",
                ]
                if (internal_state_ready and consumer_aligned)
                else [
                    "internal-state action cues are not yet visible enough across bounded consumers",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (internal_state_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize emotion claims, hidden-thought inference, or stronger agency claims",
            overclaim_warning="clearer internal-state packaging is not selfhood, emotion, or consciousness",
            next_action=(
                "keep internal-state cues bounded while admitting the next candidate"
                if (internal_state_ready and consumer_aligned)
                else "repair internal-state action clarity before reopening this candidate"
            ),
        ),
    }
    internal_state_candidate["result_surface"] = _build_result_surface(
        status=internal_state_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (internal_state_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_internal_state_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_internal_state_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (internal_state_ready and consumer_aligned)
            else "park_in_status_surface_until_internal_state_action_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future functional-pressure readout trials, but does not authorize selfhood, emotion, or hidden-thought claims"
        ),
    )

    hook_chain_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="hook_chain_trigger_clarity_v1",
            target_surface="hook_chain.current_recommendation",
            target_consumer="codex_dashboard_packet_operator_shells",
            baseline_story=(
                "Hook-chain stages were visible, but later agents still had to infer which hook mattered now "
                "from mutation_preflight.next_followup or raw stage order."
            ),
            candidate_story=(
                "Hook chain now exposes hooks, selection rule, and a current recommendation so the narrowest "
                "bounded preflight reads as part of the hook shell instead of a separate guess."
            ),
            success_metric="hook_chain_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="hook-chain packaging turns into a planner myth or implies new hook authority",
            rollback_path="remove current_recommendation packaging and keep the prior static stage list plus registry history only",
            overclaim_to_avoid="clearer hook-chain packaging is not stronger permissions, autonomy, or planning quality",
            scope_limit="hook-chain packaging only; no new hooks, no permission expansion, no governance mutation",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (hook_chain_ready and consumer_aligned) else "park",
            result_story=(
                "Hook chain now says which bounded preflight is currently relevant and why, without inventing a new hook family."
                if (hook_chain_ready and consumer_aligned)
                else "Hook-chain trigger clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=hook_chain_summary or "hook_chain_probe unavailable",
            unresolved_items=(
                [
                    "clearer hook-chain packaging does not prove better planning quality or stronger permissions",
                    "future shells must keep current_recommendation subordinate to mutation_preflight and bounded hook scope",
                ]
                if (hook_chain_ready and consumer_aligned)
                else [
                    "hook-chain recommendation is not yet visible enough in the live shell",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (hook_chain_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize new hooks, stronger permissions, or planner-style mutation authority",
            overclaim_warning="clearer hook-chain packaging is not a new permission system or autonomous planner",
            next_action=(
                "keep hook-chain recommendations bounded while admitting the next candidate"
                if (hook_chain_ready and consumer_aligned)
                else "repair hook-chain trigger clarity before reopening this candidate"
            ),
        ),
    }
    hook_chain_candidate["result_surface"] = _build_result_surface(
        status=hook_chain_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (hook_chain_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_hook_chain_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_hook_chain_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (hook_chain_ready and consumer_aligned)
            else "park_in_status_surface_until_hook_chain_trigger_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future hook-shell packaging trials, but does not authorize new hooks, permissions, or broader planning authority"
        ),
    )

    consumer_misread_guard_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="consumer_misread_guard_clarity_v1",
            target_surface="consumer_contract.priority_misread_guard",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Consumer misread guards already existed, but they still read like a static list of warnings. "
                "Later agents had to infer where a misread would show up and what concrete correction to apply."
            ),
            candidate_story=(
                "Consumer misread guards now expose trigger_surface, operator_action, and one bounded priority correction "
                "so Codex-style, Claude-style, and dashboard shells can recover the same first correction without inventing a planner."
            ),
            success_metric="consumer_misread_guard_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="misread corrections become a second planner story or drift across shells",
            rollback_path="remove priority misread packaging and fall back to the prior name-plus-rule guard list",
            overclaim_to_avoid="clearer misread correction is not stronger transport, deeper cognition, or safer mutation by itself",
            scope_limit="consumer-guard packaging only; no new permissions, no new transport semantics, no governance widening",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (consumer_misread_guard_ready and consumer_aligned) else "park",
            result_story=(
                "Consumer misread guards now say where the misread appears, what correction to apply, and which correction matters first."
                if (consumer_misread_guard_ready and consumer_aligned)
                else "Consumer misread-guard packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                consumer_misread_guard_summary or "consumer_misread_guard_probe unavailable"
            ),
            unresolved_items=(
                [
                    "priority misread correction improves shared interpretation, not transport or reasoning quality",
                    "future consumers must keep the same guard set and priority rule",
                ]
                if (consumer_misread_guard_ready and consumer_aligned)
                else [
                    "priority correction or trigger/action fields are not yet visible enough across consumers",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (consumer_misread_guard_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize new planners, stronger permissions, or stronger cross-vendor interoperability claims",
            overclaim_warning="clearer misread guards are not proof of shared cognition, safer mutation, or better reasoning",
            next_action=(
                "keep consumer misread correction bounded while admitting the next candidate"
                if (consumer_misread_guard_ready and consumer_aligned)
                else "repair consumer misread correction packaging before reopening this candidate"
            ),
        ),
    }
    consumer_misread_guard_candidate["result_surface"] = _build_result_surface(
        status=consumer_misread_guard_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (consumer_misread_guard_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_consumer_misread_guard_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_consumer_contract_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (consumer_misread_guard_ready and consumer_aligned)
            else "park_in_status_surface_until_consumer_misread_guard_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future consumer-shell packaging trials, but does not authorize transport promotion, new planners, or stronger permissions"
        ),
    )

    subsystem_parity_focus_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="subsystem_parity_focus_clarity_v1",
            target_surface="subsystem_parity.next_focus",
            target_consumer="codex_claude_dashboard_operator_shells",
            baseline_story=(
                "Subsystem parity already exposed family status and one next_focus target, but successors still had to infer which family produced that focus and why it mattered now."
            ),
            candidate_story=(
                "Subsystem parity now exposes source_family, focus_pressures, and operator_action so Codex-style, Claude-style, and dashboard shells recover the same next-focus rationale without widening authority."
            ),
            success_metric="subsystem_parity_focus_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="next_focus packaging turns into a planner story or drifts across shells",
            rollback_path="remove next_focus rationale packaging and fall back to target-plus-reason only",
            overclaim_to_avoid="clearer next_focus packaging is not better planning quality or stronger authority",
            scope_limit="subsystem-parity packaging only; no shell redesign, no planner, no governance widening",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (subsystem_parity_focus_ready and consumer_aligned) else "park",
            result_story=(
                "Subsystem parity now says which family produced the current focus, what pressures made it current, and what bounded operator action follows."
                if (subsystem_parity_focus_ready and consumer_aligned)
                else "Subsystem-parity focus clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                subsystem_parity_focus_summary or "subsystem_parity_focus_probe unavailable"
            ),
            unresolved_items=(
                [
                    "clearer next_focus rationale improves orientation, not planning quality or authority",
                    "future shells must keep next_focus subordinate to mutation_preflight and canonical_center",
                ]
                if (subsystem_parity_focus_ready and consumer_aligned)
                else [
                    "next_focus rationale is not yet visible enough across bounded consumers",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (subsystem_parity_focus_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize planner behavior, stronger permissions, or governance promotion",
            overclaim_warning="clearer next_focus packaging is not autonomous planning or stronger runtime truth",
            next_action=(
                "keep subsystem-parity focus bounded while admitting the next candidate"
                if (subsystem_parity_focus_ready and consumer_aligned)
                else "repair subsystem-parity focus clarity before reopening this candidate"
            ),
        ),
    }
    subsystem_parity_focus_candidate["result_surface"] = _build_result_surface(
        status=subsystem_parity_focus_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (subsystem_parity_focus_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_subsystem_parity_focus_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_subsystem_parity_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (subsystem_parity_focus_ready and consumer_aligned)
            else "park_in_status_surface_until_subsystem_parity_focus_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future orientation-shell packaging trials, but does not authorize planner behavior or stronger authority"
        ),
    )

    closeout_attention_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="closeout_attention_action_clarity_v1",
            target_surface="closeout_attention.operator_action",
            target_consumer="observer_claude_dashboard_operator_shells",
            baseline_story=(
                "Closeout attention already lifted incomplete handoffs, but successors still had to infer what practical action followed from partial or blocked closeout."
            ),
            candidate_story=(
                "Closeout attention now exposes source_family, attention_pressures, and operator_action so observer, Claude-style, and dashboard shells recover the same bounded handling story."
            ),
            success_metric="closeout_attention_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="closeout attention turns into a planner story or shells drift on anti-fake-completion handling",
            rollback_path="remove closeout rationale packaging and fall back to status-plus-summary only",
            overclaim_to_avoid="clearer closeout handling is not stronger authority, better planning, or solved mutation safety",
            scope_limit="closeout-attention packaging only; no planner, no new permissions, no governance widening",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (closeout_attention_ready and consumer_aligned) else "park",
            result_story=(
                "Closeout attention now says which bounded handoff family triggered attention, what pressures are active, and what operator action follows."
                if (closeout_attention_ready and consumer_aligned)
                else "Closeout-attention action clarity is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                closeout_attention_summary or "closeout_attention_probe unavailable"
            ),
            unresolved_items=(
                [
                    "clearer closeout handling improves anti-fake-completion, not planning quality or authority",
                    "future shells must keep closeout attention subordinate to consumer contract and bounded handoff truth",
                ]
                if (closeout_attention_ready and consumer_aligned)
                else [
                    "closeout action grammar is not yet preserved across bounded shells",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (closeout_attention_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize planner behavior, stronger permissions, or governance promotion",
            overclaim_warning="clearer closeout-attention packaging is not stronger runtime truth, stronger authority, or solved mutation safety",
            next_action=(
                "keep closeout-attention handling bounded while admitting the next candidate"
                if (closeout_attention_ready and consumer_aligned)
                else "repair closeout-attention action clarity before reopening this candidate"
            ),
        ),
    }
    closeout_attention_candidate["result_surface"] = _build_result_surface(
        status=closeout_attention_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (closeout_attention_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_closeout_attention_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_closeout_attention_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (closeout_attention_ready and consumer_aligned)
            else "park_in_status_surface_until_closeout_attention_action_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future anti-fake-completion packaging trials, but does not authorize planner behavior or stronger authority"
        ),
    )

    claude_priority_correction_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="claude_priority_correction_clarity_v1",
            target_surface="claude_entry_adapter.priority_correction",
            target_consumer="claude_style_shell",
            baseline_story=(
                "Claude-style entry shells already preserved first-hop order and one must-correct-first object, "
                "but the actual correction path still required inference."
            ),
            candidate_story=(
                "The Claude-compatible adapter now exposes one bounded priority_correction with blocked assumption, "
                "re-read order, and bounded next-step target so the shell can recover the same first correction without acting like a planner."
            ),
            success_metric="claude_priority_correction_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="adapter correction turns into planner behavior or drifts away from the same first-hop contract",
            rollback_path="remove priority_correction packaging and fall back to must_correct_first only",
            overclaim_to_avoid="clearer Claude correction packaging is not vendor-native interop, shared cognition, or stronger transport",
            scope_limit="Claude-style shell packaging only; no transport change, no permission widening, no governance promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (claude_priority_correction_ready and consumer_aligned) else "park",
            result_story=(
                "Claude-style entry now recovers one bounded priority correction with enough structure to re-read the same parent surfaces before acting."
                if (claude_priority_correction_ready and consumer_aligned)
                else "Claude priority-correction packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                claude_priority_correction_summary or "claude_priority_correction_probe unavailable"
            ),
            unresolved_items=(
                [
                    "clearer Claude correction packaging improves shell parity, not transport or reasoning quality",
                    "future shells must keep priority correction subordinate to the same consumer contract and first-hop order",
                ]
                if (claude_priority_correction_ready and consumer_aligned)
                else [
                    "adapter correction packaging is not yet preserved cleanly enough",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (claude_priority_correction_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize vendor-native interop claims, stronger permissions, or transport promotion",
            overclaim_warning="clearer Claude correction packaging is not shared cognition, better transport, or stronger authority",
            next_action=(
                "keep Claude priority correction bounded while admitting the next candidate"
                if (claude_priority_correction_ready and consumer_aligned)
                else "repair Claude priority-correction packaging before reopening this candidate"
            ),
        ),
    }
    claude_priority_correction_candidate["result_surface"] = _build_result_surface(
        status=claude_priority_correction_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (claude_priority_correction_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_claude_priority_correction_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_claude_entry_adapter_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (claude_priority_correction_ready and consumer_aligned)
            else "park_in_status_surface_until_claude_priority_correction_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future Claude-style shell packaging trials, but does not authorize transport promotion or stronger vendor interop claims"
        ),
    )

    hot_memory_pull_boundary_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="hot_memory_pull_boundary_clarity_v1",
            target_surface="hot_memory_ladder.current_pull_boundary",
            target_consumer="observer_dashboard_operator_shells",
            baseline_story=(
                "The hot-memory ladder already showed layer statuses, but successors still had to infer how deep they should pull before widening context."
            ),
            candidate_story=(
                "Hot-memory ladder now exposes one bounded current_pull_boundary so observer and dashboard shells can preserve the same stop layer, pull posture, and operator action."
            ),
            success_metric="hot_memory_pull_boundary_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="pull-boundary packaging turns into planner behavior or starts authorizing deeper pulls by default",
            rollback_path="remove current_pull_boundary packaging and fall back to layer statuses only",
            overclaim_to_avoid="clearer pull boundaries are not stronger memory, retrieval, or transport semantics",
            scope_limit="hot-memory packaging only; no retrieval runtime, no transport change, no governance promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (hot_memory_pull_boundary_ready and consumer_aligned) else "park",
            result_story=(
                "Hot-memory ladder now says where a bounded successor should stop pulling and why, without widening authority."
                if (hot_memory_pull_boundary_ready and consumer_aligned)
                else "Hot-memory pull-boundary packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(
                hot_memory_pull_boundary_summary or "hot_memory_pull_boundary_probe unavailable"
            ),
            unresolved_items=(
                [
                    "clearer pull boundaries improve latency discipline, not memory quality or transport strength",
                    "future shells must keep current_pull_boundary subordinate to canonical_center and live coordination truth",
                ]
                if (hot_memory_pull_boundary_ready and consumer_aligned)
                else [
                    "pull-boundary packaging is not yet preserved cleanly enough across bounded shells",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure=(
                "low" if (hot_memory_pull_boundary_ready and consumer_aligned) else "meaningful"
            ),
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize deeper default pulls, retrieval promotion, or transport claims",
            overclaim_warning="clearer hot-memory pull boundaries are not better memory, retrieval, or shared cognition",
            next_action=(
                "keep hot-memory pull boundaries bounded while admitting the next candidate"
                if (hot_memory_pull_boundary_ready and consumer_aligned)
                else "repair hot-memory pull-boundary packaging before reopening this candidate"
            ),
        ),
    }
    hot_memory_pull_boundary_candidate["result_surface"] = _build_result_surface(
        status=hot_memory_pull_boundary_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (hot_memory_pull_boundary_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_hot_memory_pull_boundary_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_hot_memory_ladder_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (hot_memory_pull_boundary_ready and consumer_aligned)
            else "park_in_status_surface_until_hot_memory_pull_boundary_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future hot-memory and latency-packaging trials, but does not authorize retrieval promotion or deeper default pulls"
        ),
    )

    memory_panel_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="memory_panel_tier_subordination_v1",
            target_surface="dashboard.memory_panel.reference_boundary",
            target_consumer="dashboard_operator_shell",
            baseline_story=(
                "The dashboard memory panel already behaved like a secondary reference selector, but its boundary language was weak and the display layer still had encoding noise."
            ),
            candidate_story=(
                "Memory panel now says clearly that reference selection is auxiliary-only, keeps closeout caution visible, and stays subordinate to Tier 0 / Tier 1 operator truth."
            ),
            success_metric="memory_panel_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="reference selection starts reading like operator truth, hot-memory truth, or a second control panel",
            rollback_path="restore the previous memory-panel wording and drop the extra boundary cues",
            overclaim_to_avoid="a cleaner memory panel is not better memory semantics, retrieval quality, or shared cognition",
            scope_limit="dashboard memory-panel packaging only; no retrieval runtime, no identity change, no governance promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (memory_panel_ready and consumer_aligned) else "park",
            result_story=(
                "Dashboard memory panel now presents reference selection as an explicitly auxiliary layer and keeps closeout caution visible."
                if (memory_panel_ready and consumer_aligned)
                else "Dashboard memory-panel tier subordination is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(memory_panel_summary or "memory_panel_probe unavailable"),
            unresolved_items=(
                [
                    "clearer memory-panel packaging improves operator discipline, not retrieval quality or memory semantics",
                    "future dashboard changes must keep reference selection subordinate to Tier 0 / Tier 1 / Tier 2 operator truth",
                ]
                if (memory_panel_ready and consumer_aligned)
                else [
                    "memory-panel boundary language is not yet preserved cleanly enough",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (memory_panel_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize retrieval promotion, hotter memory claims, or a second operator control plane",
            overclaim_warning="clearer memory-panel boundaries are not improved memory transport, retrieval quality, or shared selfhood",
            next_action=(
                "keep the memory panel subordinate while admitting the next candidate"
                if (memory_panel_ready and consumer_aligned)
                else "repair memory-panel boundary packaging before reopening this candidate"
            ),
        ),
    }
    memory_panel_candidate["result_surface"] = _build_result_surface(
        status=memory_panel_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (memory_panel_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_memory_panel_boundary_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_memory_panel_view_model_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (memory_panel_ready and consumer_aligned)
            else "park_in_status_surface_until_memory_panel_tier_subordination_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future dashboard reference-panel packaging, but does not authorize retrieval promotion or a second operator truth surface"
        ),
    )

    status_panel_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="status_panel_operator_copy_clarity_v1",
            target_surface="dashboard.status_panel.operator_posture",
            target_consumer="dashboard_operator_shell",
            baseline_story=(
                "The dashboard status panel was structurally tier-aligned, but some operator-facing copy and telemetry labels still carried display noise that weakened first-hop readability."
            ),
            candidate_story=(
                "Status panel now exposes a clean operator note, a primary-vs-secondary boundary, and readable telemetry labels without changing the tier model itself."
            ),
            success_metric="status_panel_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="status panel drifts into a second control plane or hides primary-vs-secondary boundaries behind smoother copy",
            rollback_path="restore the prior status-panel copy and drop the extra operator-boundary cues",
            overclaim_to_avoid="cleaner status-panel copy is not better runtime truth, planning quality, or shared cognition",
            scope_limit="dashboard status-panel packaging only; no runtime semantics change, no new authority, no shell expansion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (status_panel_ready and consumer_aligned) else "park",
            result_story=(
                "Dashboard status panel now states operator boundaries cleanly and renders telemetry in a readable form without changing tier authority."
                if (status_panel_ready and consumer_aligned)
                else "Dashboard status-panel operator-copy packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(status_panel_summary or "status_panel_probe unavailable"),
            unresolved_items=(
                [
                    "clearer status-panel copy improves operator readability, not runtime truth or planning quality",
                    "future dashboard changes must keep primary-versus-secondary boundaries explicit",
                ]
                if (status_panel_ready and consumer_aligned)
                else [
                    "status-panel boundary language is not yet preserved cleanly enough",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (status_panel_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize new control planes, stronger runtime claims, or shell expansion",
            overclaim_warning="cleaner status-panel copy is not better reasoning, stronger authority, or improved memory transport",
            next_action=(
                "keep the status panel readable and subordinate while admitting the next candidate"
                if (status_panel_ready and consumer_aligned)
                else "repair status-panel operator-copy packaging before reopening this candidate"
            ),
        ),
    }
    status_panel_candidate["result_surface"] = _build_result_surface(
        status=status_panel_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (status_panel_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_status_panel_copy_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_status_panel_view_model_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (status_panel_ready and consumer_aligned)
            else "park_in_status_surface_until_status_panel_operator_copy_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future dashboard status-panel packaging, but does not authorize new authority or a second operator control plane"
        ),
    )

    command_shelf_candidate = {
        "candidate_record": _build_candidate_record(
            candidate_id="dashboard_command_shelf_activation_clarity_v1",
            target_surface="dashboard.command_shelf.commands",
            target_consumer="dashboard_operator_shell",
            baseline_story=(
                "The dashboard command shelf already pointed back to CLI/runtime entry surfaces, but dynamic commands still read too much like one flat browser-side menu."
            ),
            candidate_story=(
                "Command shelf now exposes source, activation, and return cues so bounded moves and deep pulls stay visibly subordinate to the tier model."
            ),
            success_metric="command_shelf_probe.present and consumer_drift_report.status == aligned",
            failure_mode_watch="command metadata starts reading like permission authority or flattens Tier 0 and Tier 2 into one workflow menu",
            rollback_path="restore the prior command-shelf packaging and drop the extra activation metadata",
            overclaim_to_avoid="clearer command-shelf packaging is not stronger planning, automation, or runtime authority",
            scope_limit="dashboard command-shelf packaging only; no command execution layer, no permission system, no governance promotion",
        ),
        "analyzer_closeout": _build_analyzer_closeout(
            status="promote" if (command_shelf_ready and consumer_aligned) else "park",
            result_story=(
                "Dashboard command shelf now states where each command comes from, why it is visible, and when to fall back to a smaller tier."
                if (command_shelf_ready and consumer_aligned)
                else "Dashboard command-shelf activation packaging is not yet stable enough to promote."
            ),
            evidence_bundle_summary=(command_shelf_summary or "command_shelf_probe unavailable"),
            unresolved_items=(
                [
                    "clearer command-shelf activation packaging improves operator discipline, not planning quality or automation authority",
                    "future dashboard changes must keep bounded moves and deep pulls visibly subordinate to the tier model",
                ]
                if (command_shelf_ready and consumer_aligned)
                else [
                    "command-shelf source, activation, or return cues are not yet preserved cleanly enough",
                    "consumer drift must stay aligned before promotion",
                ]
            ),
            failure_pressure="low" if (command_shelf_ready and consumer_aligned) else "meaningful",
            rollback_posture="bounded_restore",
            promotion_limit="does not authorize browser-side command execution, stronger permissions, or a new operator control plane",
            overclaim_warning="clearer command-shelf activation cues are not better planning, stronger governance, or safer mutation authority",
            next_action=(
                "hold self-improvement v0 at the status surface and require explicit ratification before opening a new active bucket"
                if (command_shelf_ready and consumer_aligned)
                else "repair command-shelf activation packaging before reopening this candidate"
            ),
        ),
    }
    command_shelf_candidate["result_surface"] = _build_result_surface(
        status=command_shelf_candidate["analyzer_closeout"]["status"],
        registry_recommendation=(
            "promotion_ready_result"
            if (command_shelf_ready and consumer_aligned)
            else "distilled_lesson"
        ),
        supersession_posture="active_until_newer_command_shelf_activation_trials_exist",
        replay_rule="prefer_status_surface_then_probe_current_command_shelf_shape_before_reusing_the_story",
        residue_posture=(
            "keep_visible_as_current_packaging_result"
            if (command_shelf_ready and consumer_aligned)
            else "park_in_status_surface_until_command_shelf_activation_clarity_is_stable"
        ),
        visibility="status_surface_only",
        carry_forward_rule=(
            "may inform future dashboard command-shelf packaging, but does not authorize browser-side execution, stronger permissions, or a new authority lane"
        ),
    )

    candidates = [
        consumer_candidate,
        retrieval_candidate,
        deliberation_candidate,
        task_board_candidate,
        shared_edit_candidate,
        publish_push_candidate,
        mutation_followup_candidate,
        surface_versioning_candidate,
        launch_health_candidate,
        internal_state_candidate,
        hook_chain_candidate,
        consumer_misread_guard_candidate,
        subsystem_parity_focus_candidate,
        closeout_attention_candidate,
        claude_priority_correction_candidate,
        hot_memory_pull_boundary_candidate,
        memory_panel_candidate,
        status_panel_candidate,
        command_shelf_candidate,
    ]
    outcome_counts = _count_outcomes(candidates)
    status = "completed"
    summary_text = (
        "self_improvement_trial_wave "
        f"promote={outcome_counts['promote']} park={outcome_counts['park']} "
        f"retire={outcome_counts['retire']} blocked={outcome_counts['blocked']}"
    )
    return {
        "contract_version": "v1",
        "bundle": "self_improvement_trial_wave",
        "agent": agent,
        "status": status,
        "summary_text": summary_text,
        "receiver_rule": (
            "Trial-wave outcomes are bounded self-improvement results. They may inform future patches or "
            "parking decisions, but they do not become governance truth, identity truth, or hot-memory authority."
        ),
        "trial_families": [
            "cross_consumer_parity_packaging",
            "bounded_operator_retrieval_cueing",
            "deliberation_mode_hint_packaging",
            "task_board_parking_clarity",
            "shared_edit_overlap_clarity",
            "publish_push_posture_clarity",
            "mutation_followup_routing",
            "surface_versioning_lineage_clarity",
            "launch_health_trend_clarity",
            "internal_state_observability_clarity",
            "hook_chain_trigger_clarity",
            "consumer_misread_guard_clarity",
            "subsystem_parity_focus_clarity",
            "closeout_attention_action_clarity",
            "claude_priority_correction_clarity",
            "hot_memory_pull_boundary_clarity",
            "memory_panel_tier_subordination_clarity",
            "status_panel_operator_copy_clarity",
            "dashboard_command_shelf_activation_clarity",
        ],
        "outcome_counts": outcome_counts,
        "candidates": candidates,
        "next_short_board": (
            "Explicitly ratify the next active bucket; do not silently auto-open queued governance-depth work."
        ),
    }
