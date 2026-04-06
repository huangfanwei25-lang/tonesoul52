from __future__ import annotations

from tonesoul.self_improvement_trial_wave import build_self_improvement_trial_wave


def test_build_self_improvement_trial_wave_yields_promote_and_park() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    statuses = [item["analyzer_closeout"]["status"] for item in report["candidates"]]
    surface_statuses = [item["result_surface"]["surface_status"] for item in report["candidates"]]
    assert report["status"] == "completed"
    assert statuses == ["promote", "park", "promote", "promote", "promote", "promote", "promote", "promote", "promote", "promote"]
    assert surface_statuses == [
        "promoted_result",
        "parked_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
    ]
    assert report["outcome_counts"]["promote"] == 9
    assert report["outcome_counts"]["park"] == 1


def test_build_self_improvement_trial_wave_parks_consumer_candidate_on_drift() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "drift_detected", "summary_text": "consumer_drift drift_detected"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][0]
    assert candidate["candidate_record"]["candidate_id"] == "consumer_parity_packaging_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"
    assert candidate["result_surface"]["visibility"] == "status_surface_only"


def test_build_self_improvement_trial_wave_parks_deliberation_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={"present": False, "summary_text": "deliberation_hint_probe split=no"},
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][2]
    assert candidate["candidate_record"]["candidate_id"] == "deliberation_mode_hint_latency_v2"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_task_board_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={"present": False, "summary_text": "task_board_probe routing=no"},
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][3]
    assert candidate["candidate_record"]["candidate_id"] == "task_board_parking_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_shared_edit_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={"present": False, "summary_text": "shared_edit_probe pressures=no"},
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][4]
    assert candidate["candidate_record"]["candidate_id"] == "shared_edit_overlap_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_publish_push_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={"present": False, "summary_text": "publish_push_probe review=0 honesty=0"},
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][5]
    assert candidate["candidate_record"]["candidate_id"] == "publish_push_posture_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_mutation_followup_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={"present": False, "summary_text": "mutation_followup_probe missing"},
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][6]
    assert candidate["candidate_record"]["candidate_id"] == "mutation_followup_routing_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_surface_versioning_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={"present": False, "summary_text": "surface_versioning_probe missing"},
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][7]
    assert candidate["candidate_record"]["candidate_id"] == "surface_versioning_lineage_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_launch_health_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={"present": False, "summary_text": "launch_health_probe missing"},
        internal_state_probe={
            "present": True,
            "summary_text": "internal_state_probe signals=coordination_strain,continuity_drift,stop_reason_pressure,deliberation_conflict actions=4",
        },
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][8]
    assert candidate["candidate_record"]["candidate_id"] == "launch_health_trend_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"


def test_build_self_improvement_trial_wave_parks_internal_state_candidate_when_probe_missing() -> None:
    report = build_self_improvement_trial_wave(
        agent="trial-wave",
        consumer_drift_report={"status": "aligned", "summary_text": "consumer_drift aligned"},
        deliberation_hint_probe={
            "present": True,
            "summary_text": "deliberation_hint_probe mode=lightweight_review active=0 conditional=3 review=4 split=yes",
        },
        task_board_probe={
            "present": True,
            "summary_text": "task_board_probe classification=docs_plans_first write_task_md=no promotion=parking_only routing=yes",
        },
        shared_edit_probe={
            "present": True,
            "summary_text": "shared_edit_probe decision=coordinate basis=other_agent_overlap other=1 gaps=2 pressures=yes",
        },
        publish_push_probe={
            "present": True,
            "summary_text": "publish_push_probe classification=review_before_push basis=review_and_honesty_cues_present review=4 honesty=2 blocked=0",
        },
        mutation_followup_probe={
            "present": True,
            "summary_text": "mutation_followup_probe shared_target=shared_code_edit.path_overlap_preflight publish_target=publish_push.posture_preflight",
        },
        surface_versioning_probe={
            "present": True,
            "summary_text": "surface_versioning_probe consumers=codex_cli,dashboard_operator_shell,claude_style_shell compatibility=repo_native_entry,bounded_adapter,bounded_adapter fallback=session_start:tiered_v1>observer_window:anchor_window_v1>r_memory_packet:packet_v1",
        },
        launch_health_probe={
            "present": True,
            "summary_text": "launch_health_probe trend_watch=coordination_backend_alignment,collaborator_beta_validation_health forecast_blockers=continuity_effectiveness,council_decision_quality,public_launch_ready_flag actions=3",
        },
        internal_state_probe={"present": False, "summary_text": "internal_state_probe missing"},
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][9]
    assert candidate["candidate_record"]["candidate_id"] == "internal_state_observability_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"
