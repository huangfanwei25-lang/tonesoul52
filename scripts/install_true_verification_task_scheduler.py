from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


def _load_render_module():
    path = repo_root / "scripts" / "render_true_verification_task_scheduler.py"
    spec = importlib.util.spec_from_file_location(
        "render_true_verification_task_scheduler_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RENDER_MODULE = _load_render_module()
_DEFAULT_RENDER_AUTHOR = _RENDER_MODULE.build_parser().parse_args([]).author
_DEFAULT_SCRIPT_PATH = getattr(
    _RENDER_MODULE,
    "DEFAULT_SCRIPT_PATH",
    str(repo_root / "scripts" / "run_true_verification_host_tick_task.py"),
)
DEFAULT_INSTALL_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_install_latest.json"
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render and optionally install the weekly ToneSoul True Verification Task Scheduler definition."
    )
    parser.add_argument(
        "--task-name",
        type=str,
        default=_RENDER_MODULE.DEFAULT_TASK_NAME,
        help="Task Scheduler display name",
    )
    parser.add_argument(
        "--author",
        type=str,
        default=_DEFAULT_RENDER_AUTHOR,
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
        default=_RENDER_MODULE.DEFAULT_INTERVAL_HOURS,
        help="Task repetition interval in hours",
    )
    parser.add_argument(
        "--duration-days",
        type=int,
        default=_RENDER_MODULE.DEFAULT_DURATION_DAYS,
        help="Task repetition duration in days",
    )
    parser.add_argument(
        "--execution-time-limit-hours",
        type=int,
        default=_RENDER_MODULE.DEFAULT_EXECUTION_TIME_LIMIT_HOURS,
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
        default=_DEFAULT_SCRIPT_PATH,
        help="Host-task wrapper path invoked by the scheduled task",
    )
    parser.add_argument(
        "--working-directory",
        type=str,
        default=str(repo_root),
        help="Working directory for the scheduled task action",
    )
    parser.add_argument(
        "--xml-path",
        type=str,
        default=_RENDER_MODULE.DEFAULT_OUTPUT_PATH,
        help="Where to write or read the Task Scheduler XML definition",
    )
    parser.add_argument(
        "--render-summary-path",
        type=str,
        default=_RENDER_MODULE.DEFAULT_SUMMARY_PATH,
        help="Where to write the template-render metadata summary",
    )
    parser.add_argument(
        "--install-summary-path",
        type=str,
        default=DEFAULT_INSTALL_SUMMARY_PATH,
        help="Where to write the installer action summary JSON",
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="Use an existing XML template instead of re-rendering before install",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually register the task with schtasks instead of dry-run only",
    )
    parser.add_argument(
        "--schtasks-executable",
        type=str,
        default="schtasks",
        help="Task Scheduler CLI executable to invoke when --apply is set",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if rendering or installation fails validation",
    )
    return parser


def _build_render_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        task_name=args.task_name,
        author=args.author if args.author is not None else _DEFAULT_RENDER_AUTHOR,
        start_boundary=args.start_boundary,
        interval_hours=args.interval_hours,
        duration_days=args.duration_days,
        execution_time_limit_hours=args.execution_time_limit_hours,
        python_executable=args.python_executable,
        script_path=args.script_path,
        working_directory=args.working_directory,
        output_path=args.xml_path,
        summary_path=args.render_summary_path,
        strict=True,
    )


def install_task(args: argparse.Namespace) -> dict[str, object]:
    render_payload: dict[str, object] | None = None
    xml_path = Path(args.xml_path)
    if not bool(args.skip_render):
        render_payload = _RENDER_MODULE.render_task_template(_build_render_args(args))
    if not xml_path.exists():
        result = {
            "overall_ok": False,
            "mode": "missing_xml",
            "task_name": str(args.task_name),
            "apply": bool(args.apply),
            "rendered": render_payload is not None,
            "render": render_payload,
            "xml_path": str(xml_path),
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": f"Task Scheduler XML not found: {xml_path}",
        }
        _write_json(Path(args.install_summary_path), result)
        return result

    command = [
        str(args.schtasks_executable),
        "/Create",
        "/TN",
        str(args.task_name),
        "/XML",
        str(xml_path),
        "/F",
    ]
    stdout = ""
    stderr = ""
    returncode = 0
    mode = "dry_run"
    if bool(args.apply):
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = int(completed.returncode)
        mode = "applied" if returncode == 0 else "apply_failed"

    result = {
        "overall_ok": returncode == 0,
        "mode": mode,
        "task_name": str(args.task_name),
        "apply": bool(args.apply),
        "rendered": render_payload is not None,
        "render": render_payload,
        "xml_path": str(xml_path),
        "command": command,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
    _write_json(Path(args.install_summary_path), result)
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = install_task(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
