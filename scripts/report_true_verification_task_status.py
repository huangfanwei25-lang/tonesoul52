from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

import tonesoul.true_verification_summary as _tv_summary  # noqa: E402

summarize_long_run_payload = _tv_summary.summarize_long_run_payload
summarize_schedule_payload = _tv_summary.summarize_schedule_payload

DEFAULT_TASK_NAME = "ToneSoul True Verification Weekly"
DEFAULT_STATUS_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_status_latest.json"
)
DEFAULT_INSTALL_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_install_latest.json"
)
DEFAULT_TEMPLATE_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_latest.json"
)
DEFAULT_HOST_TICK_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_host_tick_latest.json"
)
DEFAULT_EXPERIMENT_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_experiment_latest.json"
)
DEFAULT_SCHEDULE_SNAPSHOT_PATH = (
    "docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json"
)
TASK_NS = {"task": "http://schemas.microsoft.com/windows/2004/02/mit/task"}


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report live Windows Task Scheduler status for the weekly True Verification task."
    )
    parser.add_argument(
        "--task-name",
        type=str,
        default=DEFAULT_TASK_NAME,
        help="Task Scheduler display name to query",
    )
    parser.add_argument(
        "--status-path",
        type=str,
        default=DEFAULT_STATUS_PATH,
        help="Where to write the task status snapshot JSON",
    )
    parser.add_argument(
        "--install-summary-path",
        type=str,
        default=DEFAULT_INSTALL_SUMMARY_PATH,
        help="Installer summary artifact to include when present",
    )
    parser.add_argument(
        "--template-summary-path",
        type=str,
        default=DEFAULT_TEMPLATE_SUMMARY_PATH,
        help="Task template summary artifact to include when present",
    )
    parser.add_argument(
        "--host-tick-summary-path",
        type=str,
        default=DEFAULT_HOST_TICK_SUMMARY_PATH,
        help="Latest host tick summary artifact to include when present",
    )
    parser.add_argument(
        "--experiment-summary-path",
        type=str,
        default=DEFAULT_EXPERIMENT_SUMMARY_PATH,
        help="Latest weekly experiment summary artifact to include when present",
    )
    parser.add_argument(
        "--schedule-snapshot-path",
        type=str,
        default=DEFAULT_SCHEDULE_SNAPSHOT_PATH,
        help="Latest weekly schedule snapshot artifact to include when present",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when the task cannot be queried successfully",
    )
    return parser


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_optional_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_summary(path: Path, *, kind: str) -> dict[str, object] | None:
    payload = _read_optional_json(path)
    if not isinstance(payload, dict):
        return payload
    if kind == "long_run":
        return summarize_long_run_payload(payload)
    if kind == "schedule":
        return summarize_schedule_payload(payload)
    return payload


def _host_trigger_mode(host_tick_summary: dict[str, object] | None) -> str | None:
    if not isinstance(host_tick_summary, dict):
        return None
    experiment = host_tick_summary.get("experiment")
    if not isinstance(experiment, dict):
        return None
    mode = experiment.get("host_trigger_mode")
    if isinstance(mode, str) and mode.strip():
        return mode
    return None


def _decode_output(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "cp950", sys.getdefaultencoding()):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _query_task_xml(task_name: str) -> tuple[bool, str]:
    completed = subprocess.run(
        ["schtasks", "/Query", "/TN", task_name, "/XML"],
        capture_output=True,
        check=False,
    )
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    if completed.returncode != 0:
        return False, stderr or stdout
    return True, stdout


def _powershell_task_runtime_command(task_name: str) -> str:
    escaped_name = task_name.replace("'", "''")
    return (
        "$ErrorActionPreference='Stop'; "
        f"$task=Get-ScheduledTask -TaskName '{escaped_name}'; "
        f"$info=Get-ScheduledTaskInfo -TaskName '{escaped_name}'; "
        "[pscustomobject]@{"
        "TaskName=$task.TaskName; "
        "TaskPath=$task.TaskPath; "
        "State=[string]$task.State; "
        "Enabled=[bool]$task.Settings.Enabled; "
        "LastRunTime=$info.LastRunTime.ToString('o'); "
        "NextRunTime=$info.NextRunTime.ToString('o'); "
        "LastTaskResult=$info.LastTaskResult; "
        "NumberOfMissedRuns=$info.NumberOfMissedRuns"
        "} | ConvertTo-Json -Compress"
    )


def _query_task_runtime_info(task_name: str) -> tuple[bool, dict[str, object] | str]:
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            _powershell_task_runtime_command(task_name),
        ],
        capture_output=True,
        check=False,
    )
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    if completed.returncode != 0:
        return False, stderr or stdout
    return True, json.loads(stdout)


def _xml_text(root: ET.Element, path: str) -> str | None:
    node = root.find(path, TASK_NS)
    if node is None or node.text is None:
        return None
    return node.text


def _parse_task_xml(xml_payload: str) -> dict[str, object]:
    root = ET.fromstring(xml_payload)
    return {
        "author": _xml_text(root, "task:RegistrationInfo/task:Author"),
        "description": _xml_text(root, "task:RegistrationInfo/task:Description"),
        "uri": _xml_text(root, "task:RegistrationInfo/task:URI"),
        "start_boundary": _xml_text(root, "task:Triggers/task:CalendarTrigger/task:StartBoundary"),
        "interval": _xml_text(
            root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Interval"
        ),
        "duration": _xml_text(
            root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Duration"
        ),
        "stop_at_duration_end": _xml_text(
            root,
            "task:Triggers/task:CalendarTrigger/task:Repetition/task:StopAtDurationEnd",
        ),
        "execution_time_limit": _xml_text(root, "task:Settings/task:ExecutionTimeLimit"),
        "multiple_instances_policy": _xml_text(root, "task:Settings/task:MultipleInstancesPolicy"),
        "command": _xml_text(root, "task:Actions/task:Exec/task:Command"),
        "arguments": _xml_text(root, "task:Actions/task:Exec/task:Arguments"),
        "working_directory": _xml_text(root, "task:Actions/task:Exec/task:WorkingDirectory"),
    }


def report_task_status(args: argparse.Namespace) -> dict[str, object]:
    xml_ok, xml_payload = _query_task_xml(str(args.task_name))
    runtime_ok, runtime_payload = _query_task_runtime_info(str(args.task_name))
    host_tick_summary = _read_optional_json(Path(args.host_tick_summary_path))
    host_trigger_mode = _host_trigger_mode(host_tick_summary)
    ignore_experiment_summary = host_trigger_mode == "single_tick"
    result: dict[str, object] = {
        "overall_ok": bool(xml_ok and runtime_ok),
        "task_name": str(args.task_name),
        "task_registered": bool(xml_ok and runtime_ok),
        "scheduler_runtime": runtime_payload if runtime_ok else None,
        "task_contract": _parse_task_xml(xml_payload) if xml_ok else None,
        "errors": {
            "xml": None if xml_ok else xml_payload,
            "runtime": None if runtime_ok else runtime_payload,
        },
        "artifact_policy": {
            "host_trigger_mode": host_trigger_mode,
            "experiment_summary": {
                "included": not ignore_experiment_summary,
                "ignored_reason": (
                    "host_tick_single_tick_mode" if ignore_experiment_summary else None
                ),
            },
        },
        "artifacts": {
            "install_summary": _read_optional_summary(Path(args.install_summary_path), kind="raw"),
            "template_summary": _read_optional_summary(
                Path(args.template_summary_path),
                kind="raw",
            ),
            "host_tick_summary": summarize_long_run_payload(host_tick_summary),
            "experiment_summary": (
                None
                if ignore_experiment_summary
                else _read_optional_summary(Path(args.experiment_summary_path), kind="long_run")
            ),
            "schedule_snapshot": _read_optional_summary(
                Path(args.schedule_snapshot_path),
                kind="schedule",
            ),
        },
    }
    _write_json(Path(args.status_path), result)
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = report_task_status(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
