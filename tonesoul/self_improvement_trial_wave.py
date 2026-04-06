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
    operator_retrieval_contract_present: bool,
    compiled_landing_zone_spec_present: bool,
    retrieval_runner_present: bool,
) -> dict[str, Any]:
    consumer_aligned = str(consumer_drift_report.get("status") or "") == "aligned"
    consumer_summary = str(consumer_drift_report.get("summary_text") or "").strip()

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

    candidates = [consumer_candidate, retrieval_candidate]
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
        ],
        "outcome_counts": outcome_counts,
        "candidates": candidates,
        "next_short_board": "Phase 796: Compact Self-Improvement Result Cue Design",
    }
