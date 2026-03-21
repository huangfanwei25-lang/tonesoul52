from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path, PureWindowsPath
from xml.sax.saxutils import escape

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

DEFAULT_TASK_NAME = "ToneSoul True Verification Weekly"
DEFAULT_OUTPUT_PATH = "docs/status/true_verification_weekly/true_verification_task_scheduler.xml"
DEFAULT_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_latest.json"
)
DEFAULT_INTERVAL_HOURS = 3
DEFAULT_DURATION_DAYS = 7
DEFAULT_EXECUTION_TIME_LIMIT_HOURS = 2
DEFAULT_ARGUMENTS = '"{script_path}" --strict'
DEFAULT_SCRIPT_PATH = str(repo_root / "scripts" / "run_true_verification_host_tick_task.py")
TASK_NAMESPACE = "http://schemas.microsoft.com/windows/2004/02/mit/task"


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _default_start_boundary() -> str:
    now = datetime.now().replace(second=0, microsecond=0)
    next_minute = now + timedelta(minutes=1)
    return next_minute.isoformat(timespec="minutes")


def _validate_positive(name: str, value: int) -> None:
    if int(value) <= 0:
        raise ValueError(f"{name} must be > 0")


def _looks_like_windows_path(value: str) -> bool:
    text = str(value).strip()
    return (len(text) >= 2 and text[1] == ":") or text.startswith("\\\\")


def _normalize_task_path(value: str) -> str:
    text = str(value).strip()
    if not text:
        return text
    if _looks_like_windows_path(text):
        return str(PureWindowsPath(text))
    return str(Path(text))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a Windows Task Scheduler XML template for the weekly True Verification host tick."
    )
    parser.add_argument(
        "--task-name",
        type=str,
        default=DEFAULT_TASK_NAME,
        help="Task Scheduler display name",
    )
    parser.add_argument(
        "--author",
        type=str,
        default=os.environ.get("USERNAME", "ToneSoul"),
        help="Registration author label written into the task definition",
    )
    parser.add_argument(
        "--start-boundary",
        type=str,
        default=None,
        help="Task start boundary in local ISO format, e.g. 2026-03-08T18:00",
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=DEFAULT_INTERVAL_HOURS,
        help="Task repetition interval in hours",
    )
    parser.add_argument(
        "--duration-days",
        type=int,
        default=DEFAULT_DURATION_DAYS,
        help="Task repetition duration in days",
    )
    parser.add_argument(
        "--execution-time-limit-hours",
        type=int,
        default=DEFAULT_EXECUTION_TIME_LIMIT_HOURS,
        help="Task execution time limit in hours",
    )
    parser.add_argument(
        "--python-executable",
        type=str,
        default=sys.executable,
        help="Python executable used by the scheduled task",
    )
    parser.add_argument(
        "--script-path",
        type=str,
        default=DEFAULT_SCRIPT_PATH,
        help="Host-task wrapper path invoked by the scheduled task",
    )
    parser.add_argument(
        "--working-directory",
        type=str,
        default=str(repo_root),
        help="Working directory for the scheduled task action",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help="Where to write the Task Scheduler XML definition",
    )
    parser.add_argument(
        "--summary-path",
        type=str,
        default=DEFAULT_SUMMARY_PATH,
        help="Where to write the task template metadata JSON summary",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if rendering fails validation",
    )
    return parser


def _build_config(args: argparse.Namespace) -> dict[str, object]:
    _validate_positive("interval_hours", args.interval_hours)
    _validate_positive("duration_days", args.duration_days)
    _validate_positive("execution_time_limit_hours", args.execution_time_limit_hours)
    return {
        "task_name": str(args.task_name).strip() or DEFAULT_TASK_NAME,
        "author": str(args.author).strip() or "ToneSoul",
        "start_boundary": (
            str(args.start_boundary).strip() if args.start_boundary else _default_start_boundary()
        ),
        "interval_hours": int(args.interval_hours),
        "duration_days": int(args.duration_days),
        "execution_time_limit_hours": int(args.execution_time_limit_hours),
        "python_executable": _normalize_task_path(args.python_executable),
        "script_path": _normalize_task_path(args.script_path),
        "working_directory": _normalize_task_path(args.working_directory),
    }


def build_task_xml(config: dict[str, object]) -> str:
    command = escape(str(config["python_executable"]))
    arguments = escape(DEFAULT_ARGUMENTS.format(script_path=str(config["script_path"])))
    working_directory = escape(str(config["working_directory"]))
    author = escape(str(config["author"]))
    description = escape(
        "ToneSoul weekly True Verification host tick. One invocation performs one runtime-gated cycle."
    )
    start_boundary = escape(str(config["start_boundary"]))
    interval = f'PT{int(config["interval_hours"])}H'
    duration = f'P{int(config["duration_days"])}D'
    execution_limit = f'PT{int(config["execution_time_limit_hours"])}H'
    return (
        '<?xml version="1.0" encoding="UTF-16"?>\n'
        f'<Task version="1.4" xmlns="{TASK_NAMESPACE}">\n'
        "  <RegistrationInfo>\n"
        f"    <Author>{author}</Author>\n"
        f"    <Description>{description}</Description>\n"
        "  </RegistrationInfo>\n"
        "  <Triggers>\n"
        "    <CalendarTrigger>\n"
        f"      <StartBoundary>{start_boundary}</StartBoundary>\n"
        "      <Enabled>true</Enabled>\n"
        "      <ScheduleByDay>\n"
        "        <DaysInterval>1</DaysInterval>\n"
        "      </ScheduleByDay>\n"
        "      <Repetition>\n"
        f"        <Interval>{interval}</Interval>\n"
        f"        <Duration>{duration}</Duration>\n"
        "        <StopAtDurationEnd>true</StopAtDurationEnd>\n"
        "      </Repetition>\n"
        "    </CalendarTrigger>\n"
        "  </Triggers>\n"
        "  <Settings>\n"
        "    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>\n"
        "    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>\n"
        "    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>\n"
        "    <AllowHardTerminate>true</AllowHardTerminate>\n"
        "    <StartWhenAvailable>true</StartWhenAvailable>\n"
        "    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>\n"
        "    <IdleSettings>\n"
        "      <StopOnIdleEnd>false</StopOnIdleEnd>\n"
        "      <RestartOnIdle>false</RestartOnIdle>\n"
        "    </IdleSettings>\n"
        "    <AllowStartOnDemand>true</AllowStartOnDemand>\n"
        "    <Enabled>true</Enabled>\n"
        "    <Hidden>false</Hidden>\n"
        "    <RunOnlyIfIdle>false</RunOnlyIfIdle>\n"
        "    <WakeToRun>false</WakeToRun>\n"
        f"    <ExecutionTimeLimit>{execution_limit}</ExecutionTimeLimit>\n"
        "    <Priority>7</Priority>\n"
        "  </Settings>\n"
        '  <Actions Context="Author">\n'
        "    <Exec>\n"
        f"      <Command>{command}</Command>\n"
        f"      <Arguments>{arguments}</Arguments>\n"
        f"      <WorkingDirectory>{working_directory}</WorkingDirectory>\n"
        "    </Exec>\n"
        "  </Actions>\n"
        "</Task>\n"
    )


def _write_text(path: Path, content: str, *, encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def render_task_template(args: argparse.Namespace) -> dict[str, object]:
    config = _build_config(args)
    xml_payload = build_task_xml(config)
    output_path = Path(args.output_path)
    summary_path = Path(args.summary_path)
    _write_text(output_path, xml_payload, encoding="utf-16")
    result = {
        "overall_ok": True,
        "task_name": config["task_name"],
        "author": config["author"],
        "start_boundary": config["start_boundary"],
        "interval_hours": config["interval_hours"],
        "duration_days": config["duration_days"],
        "execution_time_limit_hours": config["execution_time_limit_hours"],
        "python_executable": config["python_executable"],
        "script_path": config["script_path"],
        "working_directory": config["working_directory"],
        "output_path": str(output_path),
        "summary_path": str(summary_path),
        "register_hint": (f'schtasks /Create /TN "{config["task_name"]}" /XML "{output_path}" /F'),
    }
    _write_text(summary_path, json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = render_task_template(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
