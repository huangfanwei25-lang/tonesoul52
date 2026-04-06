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
        registry_recommendation="promotion_ready_result" if consumer_aligned else "distilled_lesson",
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
            failure_pressure="low" if (deliberation_hint_ready and consumer_aligned) else "meaningful",
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
            "promotion_ready_result" if (task_board_ready and consumer_aligned) else "distilled_lesson"
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
            "promotion_ready_result" if (shared_edit_ready and consumer_aligned) else "distilled_lesson"
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

    candidates = [
        consumer_candidate,
        retrieval_candidate,
        deliberation_candidate,
        task_board_candidate,
        shared_edit_candidate,
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
        ],
        "outcome_counts": outcome_counts,
        "candidates": candidates,
        "next_short_board": "Phase 808: Fifth Trial Candidate Admission",
    }
