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
            "promotion_ready_result" if (publish_push_ready and consumer_aligned) else "distilled_lesson"
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
            evidence_bundle_summary=mutation_followup_summary or "mutation_followup_probe unavailable",
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
            failure_pressure="low" if (mutation_followup_ready and consumer_aligned) else "meaningful",
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
            evidence_bundle_summary=surface_versioning_summary or "surface_versioning_probe unavailable",
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
            failure_pressure="low" if (surface_versioning_ready and consumer_aligned) else "meaningful",
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
            "promotion_ready_result" if (launch_health_ready and consumer_aligned) else "distilled_lesson"
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
        ],
        "outcome_counts": outcome_counts,
        "candidates": candidates,
        "next_short_board": "Phase 820: Ninth Trial Candidate Admission",
    }
