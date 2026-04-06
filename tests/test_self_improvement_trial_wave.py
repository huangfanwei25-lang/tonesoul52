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
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    statuses = [item["analyzer_closeout"]["status"] for item in report["candidates"]]
    surface_statuses = [item["result_surface"]["surface_status"] for item in report["candidates"]]
    assert report["status"] == "completed"
    assert statuses == ["promote", "park", "promote", "promote", "promote"]
    assert surface_statuses == [
        "promoted_result",
        "parked_result",
        "promoted_result",
        "promoted_result",
        "promoted_result",
    ]
    assert report["outcome_counts"]["promote"] == 4
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
        operator_retrieval_contract_present=True,
        compiled_landing_zone_spec_present=True,
        retrieval_runner_present=False,
    )

    candidate = report["candidates"][4]
    assert candidate["candidate_record"]["candidate_id"] == "shared_edit_overlap_clarity_v1"
    assert candidate["analyzer_closeout"]["status"] == "park"
    assert candidate["result_surface"]["registry_recommendation"] == "distilled_lesson"
