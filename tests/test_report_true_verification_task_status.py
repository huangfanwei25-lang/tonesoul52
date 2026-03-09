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

    install_summary_path.write_text('{"mode":"applied"}', encoding="utf-8")
    template_summary_path.write_text('{"interval_hours":3}', encoding="utf-8")
    host_tick_summary_path.write_text(
        json.dumps(
            {
                "overall_ok": True,
                "experiment": {"host_trigger_mode": "single_tick"},
                "schedule": {"overall_ok": True, "results": [{"cycle": 1}]},
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
                "results": [{"cycle": 2, "duration_ms": 10}],
                "state": {"cycles_run": 2, "entry_states": {"osv": {"last_outcome": "ok"}}},
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
        ]
    )

    payload = module.report_task_status(args)

    assert payload["overall_ok"] is True
    assert payload["task_registered"] is True
    assert payload["scheduler_runtime"]["State"] == "Ready"
    assert payload["task_contract"]["interval"] == "PT3H"
    assert payload["artifacts"]["schedule_snapshot"]["result_count"] == 1
    assert payload["artifacts"]["schedule_snapshot"]["latest_result"] == {
        "cycle": 2,
        "duration_ms": 10,
    }
    saved = json.loads(status_path.read_text(encoding="utf-8"))
    assert saved["artifacts"]["install_summary"]["mode"] == "applied"


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
