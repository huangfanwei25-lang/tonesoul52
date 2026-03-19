from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module():
    path = (
        Path(__file__).resolve().parents[1] / "scripts" / "report_true_verification_task_status.py"
    )
    spec = importlib.util.spec_from_file_location(
        "report_true_verification_task_status_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_sets_status_report_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.task_name == "ToneSoul True Verification Weekly"
    assert args.status_path.endswith("true_verification_task_status_latest.json")
    assert args.install_summary_path.endswith(
        "true_verification_task_scheduler_install_latest.json"
    )
    assert args.subjectivity_review_path.endswith("subjectivity_review_batch_latest.json")


def test_scribe_problem_route_status_line_stays_empty_without_route_signal() -> None:
    module = _load_module()

    assert module._scribe_problem_route_status_line("host_tick", None) == ""
    assert (
        module._scribe_problem_route_status_line(
            "host_tick",
            {
                "scribe_status": "generated",
                "scribe_generation_mode": "llm_chronicle",
                "scribe_state_document_posture": "anchor_only",
            },
        )
        == ""
    )


def test_scribe_problem_route_secondary_labels_stay_empty_without_route_signal() -> None:
    module = _load_module()

    assert module._scribe_problem_route_secondary_labels(None) == ""
    assert (
        module._scribe_problem_route_secondary_labels(
            {
                "scribe_status": "generated",
                "scribe_generation_mode": "llm_chronicle",
                "scribe_state_document_posture": "anchor_only",
            }
        )
        == ""
    )


def test_report_task_status_joins_live_task_and_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    status_path = tmp_path / "status.json"
    install_summary_path = tmp_path / "install.json"
    template_summary_path = tmp_path / "template.json"
    host_tick_summary_path = tmp_path / "tick.json"
    experiment_summary_path = tmp_path / "experiment.json"
    schedule_snapshot_path = tmp_path / "schedule.json"
    dream_observability_path = tmp_path / "dream_observability.json"
    subjectivity_review_path = tmp_path / "subjectivity_review.json"

    install_summary_path.write_text('{"mode":"applied"}', encoding="utf-8")
    template_summary_path.write_text('{"interval_hours":3}', encoding="utf-8")
    host_tick_summary_path.write_text(
        json.dumps(
            {
                "overall_ok": True,
                "experiment": {"host_trigger_mode": "single_tick"},
                "schedule": {
                    "overall_ok": True,
                    "results": [
                        {
                            "cycle": 1,
                            "autonomous_payload": {
                                "overall_ok": True,
                                "runtime_state": {
                                    "session_id": "host-tick-session",
                                    "next_cycle": 2,
                                    "consecutive_failures": 0,
                                    "resumed": False,
                                },
                                "wakeup_payload": {
                                    "overall_status": "ok",
                                    "results": [
                                        {
                                            "cycle": 2,
                                            "status": "ok",
                                            "summary": {
                                                "scribe_evaluated": True,
                                                "scribe_triggered": True,
                                                "scribe_status": "generated",
                                                "scribe_generation_mode": "template_assist",
                                                "scribe_state_document_posture": (
                                                    "pressure_without_counterweight"
                                                ),
                                                "scribe_problem_route_status_line": (
                                                    "route | family=F1_grounding_evidence_integrity "
                                                    "invariant=observed_history_grounding "
                                                    "repair=anchor_and_boundary_guardrail"
                                                ),
                                                "scribe_problem_route_secondary_labels": (
                                                    "F6_semantic_role_boundary_integrity,"
                                                    "F4_execution_contract_integrity"
                                                ),
                                                "scribe_latest_available_source": "chronicle_pair",
                                            },
                                        }
                                    ],
                                },
                            },
                            "tension_budget": {
                                "status": "ok",
                                "observation": {"max_consecutive_failure_count": 0},
                            },
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    experiment_summary_path.write_text(
        '{"experiment":{"name":"true_verification_weekly"}}', encoding="utf-8"
    )
    schedule_snapshot_path.write_text(
        json.dumps(
            {
                "overall_ok": True,
                "results": [
                    {
                        "cycle": 2,
                        "duration_ms": 10,
                        "autonomous_payload": {
                            "overall_ok": True,
                            "runtime_state": {
                                "session_id": "schedule-session",
                                "next_cycle": 3,
                                "consecutive_failures": 2,
                                "resumed": True,
                            },
                            "wakeup_payload": {
                                "overall_status": "ok",
                                "results": [
                                    {
                                        "cycle": 3,
                                        "status": "ok",
                                        "summary": {
                                            "scribe_evaluated": True,
                                            "scribe_triggered": True,
                                            "scribe_status": "generated",
                                            "scribe_generation_mode": "template_assist",
                                            "scribe_state_document_posture": (
                                                "pressure_without_counterweight"
                                            ),
                                            "scribe_anchor_status_line": (
                                                "anchor | [T1] tension: observed grounding..."
                                            ),
                                            "scribe_problem_route_status_line": (
                                                "route | family=F1_grounding_evidence_integrity "
                                                "invariant=observed_history_grounding "
                                                "repair=anchor_and_boundary_guardrail"
                                            ),
                                            "scribe_problem_route_secondary_labels": (
                                                "F6_semantic_role_boundary_integrity,"
                                                "F4_execution_contract_integrity"
                                            ),
                                            "scribe_latest_available_source": "chronicle_pair",
                                        },
                                    }
                                ],
                            },
                        },
                        "tension_budget": {
                            "status": "breached",
                            "observation": {"max_consecutive_failure_count": 2},
                        },
                    }
                ],
                "state": {"cycles_run": 2, "entry_states": {"osv": {"last_outcome": "ok"}}},
            }
        ),
        encoding="utf-8",
    )
    dream_observability_path.write_text(
        json.dumps(
            {
                "primary_status_line": (
                    "dream_observability_ready | cycles=8 collisions=3 councils=3 "
                    "scribe=generated"
                ),
                "problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=observed_history_grounding "
                    "repair=anchor_and_boundary_guardrail"
                ),
                "problem_route_secondary_labels": (
                    "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
                ),
            }
        ),
        encoding="utf-8",
    )
    subjectivity_review_path.write_text(
        json.dumps(
            {
                "admissibility_primary_status_line": (
                    "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                )
            }
        ),
        encoding="utf-8",
    )

    xml_payload = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>user</Author>
    <Description>desc</Description>
    <URI>\\ToneSoul True Verification Weekly</URI>
  </RegistrationInfo>
  <Settings>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
  </Settings>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-08T14:30:00</StartBoundary>
      <Repetition>
        <Interval>PT3H</Interval>
        <Duration>P7D</Duration>
        <StopAtDurationEnd>true</StopAtDurationEnd>
      </Repetition>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>C:\\repo\\.venv\\Scripts\\python.exe</Command>
      <Arguments>"C:\\repo\\scripts\\run_true_verification_host_tick.py" --strict</Arguments>
      <WorkingDirectory>C:\\repo</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
    runtime_payload = {
        "TaskName": "ToneSoul True Verification Weekly",
        "TaskPath": "\\",
        "State": "Ready",
        "Enabled": True,
        "LastRunTime": "2026-03-08T14:30:00",
        "NextRunTime": "2026-03-08T17:30:00",
        "LastTaskResult": 0,
        "NumberOfMissedRuns": 0,
    }

    monkeypatch.setattr(module, "_query_task_xml", lambda _name: (True, xml_payload))
    monkeypatch.setattr(module, "_query_task_runtime_info", lambda _name: (True, runtime_payload))
    args = module.build_parser().parse_args(
        [
            "--status-path",
            str(status_path),
            "--install-summary-path",
            str(install_summary_path),
            "--template-summary-path",
            str(template_summary_path),
            "--host-tick-summary-path",
            str(host_tick_summary_path),
            "--experiment-summary-path",
            str(experiment_summary_path),
            "--schedule-snapshot-path",
            str(schedule_snapshot_path),
            "--dream-observability-path",
            str(dream_observability_path),
            "--subjectivity-review-path",
            str(subjectivity_review_path),
        ]
    )

    payload = module.report_task_status(args)

    assert payload["overall_ok"] is True
    assert payload["task_registered"] is True
    assert payload["scheduler_runtime"]["State"] == "Ready"
    assert payload["task_contract"]["interval"] == "PT3H"
    assert (
        payload["primary_status_line"]
        == "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
        "runtime_source=schedule_snapshot session=schedule-session resumed=yes"
    )
    assert (
        payload["runtime_status_line"]
        == "schedule_snapshot | session=schedule-session resumed=yes next_cycle=3 "
        "failures=2 max_failure=2 tension=breached"
    )
    assert (
        payload["scribe_status_line"]
        == "schedule_snapshot | status=generated mode=template_assist "
        "posture=pressure_without_counterweight source=chronicle_pair "
        "triggered=yes skip=none"
    )
    assert (
        payload["anchor_status_line"]
        == "schedule_snapshot | anchor | [T1] tension: observed grounding..."
    )
    assert (
        payload["problem_route_status_line"]
        == "schedule_snapshot | family=F1_grounding_evidence_integrity "
        "invariant=observed_history_grounding "
        "repair=anchor_and_boundary_guardrail"
    )
    assert (
        payload["problem_route_secondary_labels"]
        == "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    assert (
        payload["dream_weekly_alignment_line"] == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity "
        "shared_secondary=F4_execution_contract_integrity,F6_semantic_role_boundary_integrity"
    )
    assert (
        payload["artifact_policy_status_line"]
        == "host_trigger_mode=single_tick | experiment_summary=ignored "
        "reason=host_tick_single_tick_mode"
    )
    assert (
        payload["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert payload["handoff"] == {
        "queue_shape": "weekly_host_status",
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=schedule_snapshot session=schedule-session resumed=yes"
        ),
        "scribe_status_line": (
            "schedule_snapshot | status=generated mode=template_assist "
            "posture=pressure_without_counterweight source=chronicle_pair "
            "triggered=yes skip=none"
        ),
        "anchor_status_line": ("schedule_snapshot | anchor | [T1] tension: observed grounding..."),
        "problem_route_status_line": (
            "schedule_snapshot | family=F1_grounding_evidence_integrity "
            "invariant=observed_history_grounding "
            "repair=anchor_and_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
        "dream_weekly_alignment_line": (
            "dream_weekly_alignment | alignment=aligned "
            "weekly=F1_grounding_evidence_integrity "
            "dream=F1_grounding_evidence_integrity "
            "shared_secondary=F4_execution_contract_integrity,F6_semantic_role_boundary_integrity"
        ),
        "artifact_policy_status_line": (
            "host_trigger_mode=single_tick | experiment_summary=ignored "
            "reason=host_tick_single_tick_mode"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "requires_operator_action": False,
    }
    assert payload["artifacts"]["schedule_snapshot"]["result_count"] == 1
    assert payload["runtime_lineage"]["latest_available_source"] == "schedule_snapshot"
    assert payload["runtime_lineage"]["host_tick"] == {
        "cycle": 1,
        "schedule_overall_ok": True,
        "session_id": "host-tick-session",
        "session_resumed": False,
        "next_cycle": 2,
        "consecutive_failures": 0,
        "tension_status": "ok",
        "max_consecutive_failure_count": 0,
    }
    assert payload["runtime_lineage"]["schedule_snapshot"] == {
        "cycle": 2,
        "schedule_overall_ok": True,
        "session_id": "schedule-session",
        "session_resumed": True,
        "next_cycle": 3,
        "consecutive_failures": 2,
        "tension_status": "breached",
        "max_consecutive_failure_count": 2,
    }
    assert (
        payload["artifacts"]["host_tick_summary"]["schedule"]["latest_result"][
            "autonomous_payload"
        ]["runtime_state"]["session_id"]
        == "host-tick-session"
    )
    assert (
        payload["artifacts"]["host_tick_summary"]["schedule"]["latest_result"][
            "autonomous_payload"
        ]["wakeup_summary"]["scribe_status"]
        == "generated"
    )
    assert (
        payload["artifacts"]["schedule_snapshot"]["latest_result"]["autonomous_payload"][
            "runtime_state"
        ]["session_id"]
        == "schedule-session"
    )
    assert (
        payload["artifacts"]["schedule_snapshot"]["latest_result"]["autonomous_payload"][
            "wakeup_summary"
        ]["scribe_state_document_posture"]
        == "pressure_without_counterweight"
    )
    assert (
        payload["artifacts"]["schedule_snapshot"]["latest_result"]["tension_budget"]["observation"][
            "max_consecutive_failure_count"
        ]
        == 2
    )
    assert payload["scribe_handoff"]["latest_available_source"] == "schedule_snapshot"
    assert payload["scribe_handoff"]["schedule_snapshot"]["scribe_status"] == "generated"
    assert (
        payload["scribe_handoff"]["schedule_snapshot"]["scribe_problem_route_status_line"]
        == "route | family=F1_grounding_evidence_integrity "
        "invariant=observed_history_grounding "
        "repair=anchor_and_boundary_guardrail"
    )
    assert (
        payload["scribe_handoff"]["schedule_snapshot"]["scribe_problem_route_secondary_labels"]
        == "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    saved = json.loads(status_path.read_text(encoding="utf-8"))
    assert saved["primary_status_line"] == payload["primary_status_line"]
    assert saved["scribe_status_line"] == payload["scribe_status_line"]
    assert saved["problem_route_status_line"] == payload["problem_route_status_line"]
    assert saved["problem_route_secondary_labels"] == payload["problem_route_secondary_labels"]
    assert saved["artifacts"]["install_summary"]["mode"] == "applied"
    assert saved["runtime_lineage"]["schedule_snapshot"]["session_id"] == "schedule-session"


def test_report_task_status_ignores_wrapper_summary_in_host_tick_mode(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    status_path = tmp_path / "status.json"
    host_tick_summary_path = tmp_path / "tick.json"
    experiment_summary_path = tmp_path / "experiment.json"

    host_tick_summary_path.write_text(
        json.dumps(
            {
                "experiment": {
                    "name": "true_verification_weekly",
                    "host_trigger_mode": "single_tick",
                }
            }
        ),
        encoding="utf-8",
    )
    experiment_summary_path.write_text(
        '{"experiment":{"name":"true_verification_weekly","days":9}}',
        encoding="utf-8",
    )

    xml_payload = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Author>user</Author></RegistrationInfo>
</Task>
"""
    runtime_payload = {
        "TaskName": "ToneSoul True Verification Weekly",
        "TaskPath": "\\",
        "State": "Ready",
        "Enabled": True,
        "LastRunTime": "2026-03-08T14:30:00",
        "NextRunTime": "2026-03-08T17:30:00",
        "LastTaskResult": 0,
        "NumberOfMissedRuns": 0,
    }

    monkeypatch.setattr(module, "_query_task_xml", lambda _name: (True, xml_payload))
    monkeypatch.setattr(module, "_query_task_runtime_info", lambda _name: (True, runtime_payload))
    args = module.build_parser().parse_args(
        [
            "--status-path",
            str(status_path),
            "--host-tick-summary-path",
            str(host_tick_summary_path),
            "--experiment-summary-path",
            str(experiment_summary_path),
        ]
    )

    payload = module.report_task_status(args)

    assert payload["artifact_policy"]["host_trigger_mode"] == "single_tick"
    assert payload["artifact_policy"]["experiment_summary"]["included"] is False
    assert payload["artifacts"]["experiment_summary"] is None
    assert (
        payload["artifact_policy_status_line"]
        == "host_trigger_mode=single_tick | experiment_summary=ignored "
        "reason=host_tick_single_tick_mode"
    )


def test_report_task_status_fails_closed_when_task_query_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    status_path = tmp_path / "status.json"
    monkeypatch.setattr(module, "_query_task_xml", lambda _name: (False, "xml missing"))
    monkeypatch.setattr(
        module, "_query_task_runtime_info", lambda _name: (False, "runtime missing")
    )
    args = module.build_parser().parse_args(["--status-path", str(status_path)])

    payload = module.report_task_status(args)

    assert payload["overall_ok"] is False
    assert payload["task_registered"] is False
    assert payload["primary_status_line"].startswith("task_attention | scheduler=unknown")
    assert payload["runtime_status_line"] == "none | runtime_lineage=unavailable"
    assert payload["handoff"]["requires_operator_action"] is True
    assert payload["errors"]["xml"] == "xml missing"
    assert payload["errors"]["runtime"] == "runtime missing"
    saved = json.loads(status_path.read_text(encoding="utf-8"))
    assert saved["overall_ok"] is False


def test_main_strict_returns_non_zero_when_status_query_fails(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "report_task_status",
        lambda _args: {"overall_ok": False},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
