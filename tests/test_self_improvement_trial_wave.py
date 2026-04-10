from __future__ import annotations

import pytest

from tonesoul.self_improvement_trial_wave import build_self_improvement_trial_wave


def _build_report(**overrides):
    payload = {
        "agent": "trial-wave",
        "consumer_drift_report": {
            "status": "aligned",
            "summary_text": "consumer_drift aligned",
        },
        "deliberation_hint_probe": {
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        "task_board_probe": {
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        "shared_edit_probe": {
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        "publish_push_probe": {
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        "mutation_followup_probe": {
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        "surface_versioning_probe": {
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        "launch_health_probe": {
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        "internal_state_probe": {
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        "hook_chain_probe": {
            "present": True,
            "summary_text": "hook_chain_probe recommended=shared_edit_path_overlap target=shared_code_edit.path_overlap_preflight selection=yes hooks=3",
        },
        "consumer_misread_guard_probe": {
            "present": True,
            "summary_text": "consumer_misread_guard_probe guards=4 priority=observer_stable_not_verified surface=observer_window.stable claude_sync=yes",
        },
        "subsystem_parity_focus_probe": {
            "present": True,
            "summary_text": "subsystem_parity_focus_probe target=shared_code_edit.path_overlap_preflight source=mutation_preflight_hooks pressures=3 shell_sync=yes",
        },
        "closeout_attention_probe": {
            "present": True,
            "summary_text": "closeout_attention_probe status=partial source=bounded_handoff_closeout pressures=4 shell_sync=yes",
        },
        "claude_priority_correction_probe": {
            "present": True,
            "summary_text": "claude_priority_correction_probe name=compaction_not_completion reread=4 next=shared_code_edit.path_overlap_preflight rule=yes",
        },
        "hot_memory_pull_boundary_probe": {
            "present": True,
            "summary_text": "hot_memory_pull_boundary_probe posture=review_handoff_before_deeper_pull stop_at=bounded_handoff dashboard_sync=yes",
        },
        "memory_panel_probe": {
            "present": True,
            "summary_text": "memory_panel_probe boundary=auxiliary_only caution=yes selected=2",
        },
        "status_panel_probe": {
            "present": True,
            "summary_text": "status_panel_probe primary=yes secondary=yes telemetry=success",
        },
        "command_shelf_probe": {
            "present": True,
            "summary_text": "command_shelf_probe next_source=mutation_preflight.next_followup next_activation=yes deep_return=yes",
        },
        "operator_retrieval_contract_present": True,
        "compiled_landing_zone_spec_present": True,
        "retrieval_runner_present": False,
    }
    payload.update(overrides)
    return build_self_improvement_trial_wave(**payload)


def test_build_self_improvement_trial_wave_yields_expected_outcomes() -> None:
    report = _build_report()

    statuses = [item["analyzer_closeout"]["status"] for item in report["candidates"]]
    surface_statuses = [item["result_surface"]["surface_status"] for item in report["candidates"]]

    assert report["status"] == "completed"
    assert report["outcome_counts"]["promote"] == 18
    assert report["outcome_counts"]["park"] == 1
    assert report["next_short_board"] == (
        "Explicitly ratify the next active bucket; do not silently auto-open queued governance-depth work."
    )
    assert statuses == [
        "promote",
        "park",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
        "promote",
    ]
    assert surface_statuses[0] == "promoted_result"
    assert surface_statuses[1] == "parked_result"
    assert surface_statuses[-1] == "promoted_result"


def test_build_self_improvement_trial_wave_parks_consumer_candidate_on_drift() -> None:
    report = _build_report(
        consumer_drift_report={
            "status": "drift_detected",
            "summary_text": "consumer_drift drift_detected",
        }
    )

    candidate = report["candidates"][0]
    assert candidate["candidate_record"]["candidate_id"] == "consumer_parity_packaging_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


@pytest.mark.parametrize(
    ("probe_name", "candidate_index", "candidate_id"),
    [
        ("deliberation_hint_probe", 2, "deliberation_mode_hint_latency_v2"),
        ("task_board_probe", 3, "task_board_parking_clarity_v1"),
        ("shared_edit_probe", 4, "shared_edit_overlap_clarity_v1"),
        ("publish_push_probe", 5, "publish_push_posture_clarity_v1"),
        ("mutation_followup_probe", 6, "mutation_followup_routing_v1"),
        ("surface_versioning_probe", 7, "surface_versioning_lineage_clarity_v1"),
        ("launch_health_probe", 8, "launch_health_trend_clarity_v1"),
        ("internal_state_probe", 9, "internal_state_observability_clarity_v1"),
        ("hook_chain_probe", 10, "hook_chain_trigger_clarity_v1"),
        ("consumer_misread_guard_probe", 11, "consumer_misread_guard_clarity_v1"),
        ("subsystem_parity_focus_probe", 12, "subsystem_parity_focus_clarity_v1"),
        ("closeout_attention_probe", 13, "closeout_attention_action_clarity_v1"),
        ("claude_priority_correction_probe", 14, "claude_priority_correction_clarity_v1"),
        ("hot_memory_pull_boundary_probe", 15, "hot_memory_pull_boundary_clarity_v1"),
        ("memory_panel_probe", 16, "memory_panel_tier_subordination_v1"),
        ("status_panel_probe", 17, "status_panel_operator_copy_clarity_v1"),
        ("command_shelf_probe", 18, "dashboard_command_shelf_activation_clarity_v1"),
    ],
)
def test_build_self_improvement_trial_wave_parks_candidate_when_probe_missing(
    probe_name: str,
    candidate_index: int,
    candidate_id: str,
) -> None:
    report = _build_report(
        **{
            probe_name: {
                "present": False,
                "summary_text": f"{probe_name} missing",
            }
        }
    )

    candidate = report["candidates"][candidate_index]
    assert candidate["candidate_record"]["candidate_id"] == candidate_id
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"
