from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_script(filename: str, module_name: str):
    path = Path(__file__).resolve().parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_host_tick_summary_and_task_status_form_a_compact_weekly_chain(
    monkeypatch,
    tmp_path: Path,
) -> None:
    host_tick_module = _load_script(
        "run_true_verification_host_tick.py",
        "run_true_verification_host_tick_chain_test",
    )
    status_module = _load_script(
        "report_true_verification_task_status.py",
        "report_true_verification_task_status_chain_test",
    )
    original_long_run_module = host_tick_module._LONG_RUN_MODULE

    class DummyLongRunModule:
        def build_parser(self):
            return original_long_run_module.build_parser()

        def run_long_run(self, _args):
            return {
                "overall_ok": True,
                "gate": {
                    "status": "passed",
                    "reason": "runtime_probe_ok",
                    "profile": "runtime_probe_watch",
                },
                "preflight": {
                    "overall_ok": True,
                    "results": [
                        {
                            "cycle": 1,
                            "duration_ms": 15,
                            "autonomous_payload": {
                                "overall_ok": True,
                                "dashboard_payload": {"huge": ["x"] * 40},
                            },
                        }
                    ],
                    "state": {"cycles_run": 1, "entry_states": {"osv": {"last_outcome": "ok"}}},
                },
                "schedule": {
                    "overall_ok": True,
                    "results": [
                        {
                            "cycle": 2,
                            "duration_ms": 22,
                            "autonomous_payload": {
                                "overall_ok": True,
                                "runtime_state": {
                                    "session_id": "chain-session",
                                    "next_cycle": 3,
                                    "consecutive_failures": 1,
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
                                "dashboard_payload": {"huge": ["y"] * 40},
                            },
                            "tension_budget": {
                                "status": "breached",
                                "observation": {"max_consecutive_failure_count": 1},
                            },
                        }
                    ],
                    "state": {"cycles_run": 2, "entry_states": {"nvd": {"last_outcome": "ok"}}},
                },
            }

    monkeypatch.setattr(host_tick_module, "_LONG_RUN_MODULE", DummyLongRunModule())
    tick_summary_path = tmp_path / "true_verification_host_tick_latest.json"
    host_tick_args = host_tick_module.build_parser().parse_args(
        [
            "--tick-summary-path",
            str(tick_summary_path),
        ]
    )

    raw_payload = host_tick_module.run_host_tick(host_tick_args)
    saved_tick_summary = json.loads(tick_summary_path.read_text(encoding="utf-8"))

    assert saved_tick_summary["schedule"]["result_count"] == 1
    assert saved_tick_summary["schedule"]["latest_result"] == {
        "cycle": 2,
        "duration_ms": 22,
        "autonomous_payload": {
            "overall_ok": True,
            "runtime_state": {
                "session_id": "chain-session",
                "next_cycle": 3,
                "consecutive_failures": 1,
                "resumed": True,
            },
            "wakeup_summary": {
                "overall_status": "ok",
                "result_count": 1,
                "latest_cycle": 3,
                "latest_status": "ok",
                "scribe_evaluated": True,
                "scribe_triggered": True,
                "scribe_status": "generated",
                "scribe_generation_mode": "template_assist",
                "scribe_state_document_posture": "pressure_without_counterweight",
                "scribe_anchor_status_line": "anchor | [T1] tension: observed grounding...",
                "scribe_problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=observed_history_grounding "
                    "repair=anchor_and_boundary_guardrail"
                ),
                "scribe_problem_route_secondary_labels": (
                    "F6_semantic_role_boundary_integrity," "F4_execution_contract_integrity"
                ),
                "scribe_latest_available_source": "chronicle_pair",
            },
        },
        "tension_budget": {
            "status": "breached",
            "observation": {"max_consecutive_failure_count": 1},
        },
    }
    assert "results" not in saved_tick_summary["schedule"]
    assert len(tick_summary_path.read_text(encoding="utf-8")) < len(
        json.dumps(raw_payload, ensure_ascii=False, indent=2)
    )

    schedule_snapshot_path = tmp_path / "autonomous_registry_schedule_latest.json"
    schedule_snapshot_path.write_text(
        json.dumps(
            {
                "overall_ok": True,
                "results": [{"cycle": 3, "duration_ms": 31}],
                "state": {"cycles_run": 3, "entry_states": {"scorecard": {"last_outcome": "ok"}}},
            }
        ),
        encoding="utf-8",
    )
    dream_observability_path = tmp_path / "dream_observability_latest.json"
    subjectivity_review_path = tmp_path / "subjectivity_review_batch_latest.json"
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
    status_path = tmp_path / "true_verification_task_status_latest.json"
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
        "LastRunTime": "2026-03-08T18:00:00",
        "NextRunTime": "2026-03-08T21:00:00",
        "LastTaskResult": 0,
        "NumberOfMissedRuns": 0,
    }
    monkeypatch.setattr(status_module, "_query_task_xml", lambda _name: (True, xml_payload))
    monkeypatch.setattr(
        status_module,
        "_query_task_runtime_info",
        lambda _name: (True, runtime_payload),
    )
    status_args = status_module.build_parser().parse_args(
        [
            "--status-path",
            str(status_path),
            "--host-tick-summary-path",
            str(tick_summary_path),
            "--schedule-snapshot-path",
            str(schedule_snapshot_path),
            "--dream-observability-path",
            str(dream_observability_path),
            "--subjectivity-review-path",
            str(subjectivity_review_path),
        ]
    )

    status_payload = status_module.report_task_status(status_args)

    assert status_payload["overall_ok"] is True
    assert (
        status_payload["primary_status_line"]
        == "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
        "runtime_source=host_tick session=chain-session resumed=yes"
    )
    assert (
        status_payload["runtime_status_line"]
        == "host_tick | session=chain-session resumed=yes next_cycle=3 "
        "failures=1 max_failure=1 tension=breached"
    )
    assert (
        status_payload["scribe_status_line"] == "host_tick | status=generated mode=template_assist "
        "posture=pressure_without_counterweight source=chronicle_pair "
        "triggered=yes skip=none"
    )
    assert (
        status_payload["anchor_status_line"]
        == "host_tick | anchor | [T1] tension: observed grounding..."
    )
    assert (
        status_payload["problem_route_status_line"]
        == "host_tick | family=F1_grounding_evidence_integrity "
        "invariant=observed_history_grounding "
        "repair=anchor_and_boundary_guardrail"
    )
    assert (
        status_payload["problem_route_secondary_labels"]
        == "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    assert (
        status_payload["dream_weekly_alignment_line"]
        == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity "
        "shared_secondary=F4_execution_contract_integrity,F6_semantic_role_boundary_integrity"
    )
    assert (
        status_payload["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert status_payload["artifacts"]["host_tick_summary"]["schedule"]["result_count"] == 1
    assert status_payload["artifacts"]["schedule_snapshot"]["result_count"] == 1
    assert status_payload["runtime_lineage"]["latest_available_source"] == "host_tick"
    assert status_payload["runtime_lineage"]["host_tick"]["session_id"] == "chain-session"
    assert status_payload["runtime_lineage"]["host_tick"]["session_resumed"] is True
    assert status_payload["runtime_lineage"]["host_tick"]["max_consecutive_failure_count"] == 1
    assert status_payload["scribe_handoff"]["latest_available_source"] == "host_tick"
    assert status_payload["scribe_handoff"]["host_tick"]["scribe_status"] == "generated"
    assert (
        status_payload["scribe_handoff"]["host_tick"]["scribe_problem_route_status_line"]
        == "route | family=F1_grounding_evidence_integrity "
        "invariant=observed_history_grounding "
        "repair=anchor_and_boundary_guardrail"
    )
    assert (
        status_payload["scribe_handoff"]["host_tick"]["scribe_problem_route_secondary_labels"]
        == "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    assert status_payload["handoff"]["queue_shape"] == "weekly_host_status"
    assert (
        status_payload["handoff"]["anchor_status_line"]
        == "host_tick | anchor | [T1] tension: observed grounding..."
    )
    assert (
        status_payload["handoff"]["problem_route_status_line"]
        == "host_tick | family=F1_grounding_evidence_integrity "
        "invariant=observed_history_grounding "
        "repair=anchor_and_boundary_guardrail"
    )
    assert (
        status_payload["handoff"]["problem_route_secondary_labels"]
        == "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    assert (
        status_payload["handoff"]["dream_weekly_alignment_line"]
        == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity "
        "shared_secondary=F4_execution_contract_integrity,F6_semantic_role_boundary_integrity"
    )
    assert (
        status_payload["handoff"]["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert status_payload["artifacts"]["schedule_snapshot"]["latest_result"] == {
        "cycle": 3,
        "duration_ms": 31,
    }
