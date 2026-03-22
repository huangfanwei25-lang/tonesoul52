from __future__ import annotations

import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path, PurePath

import pytest


def _load_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "render_true_verification_task_scheduler.py"
    )
    spec = importlib.util.spec_from_file_location(
        "render_true_verification_task_scheduler_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _find(root: ET.Element, path: str) -> ET.Element:
    node = root.find(path, {"task": "http://schemas.microsoft.com/windows/2004/02/mit/task"})
    assert node is not None
    return node


def test_build_parser_sets_task_template_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.task_name == "ToneSoul True Verification Weekly"
    assert args.start_boundary is None
    assert args.interval_hours == 3
    assert args.duration_days == 7
    assert args.execution_time_limit_hours == 2
    assert args.output_path.endswith("true_verification_task_scheduler.xml")
    assert args.summary_path.endswith("true_verification_task_scheduler_latest.json")


def test_render_task_template_writes_xml_and_summary(tmp_path: Path) -> None:
    module = _load_module()
    output_path = tmp_path / "true_verification_task_scheduler.xml"
    summary_path = tmp_path / "true_verification_task_scheduler_latest.json"
    args = module.build_parser().parse_args(
        [
            "--start-boundary",
            "2026-03-08T18:00",
            "--output-path",
            str(output_path),
            "--summary-path",
            str(summary_path),
        ]
    )

    payload = module.render_task_template(args)

    assert payload["overall_ok"] is True
    assert output_path.exists() is True
    assert summary_path.exists() is True
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["task_name"] == "ToneSoul True Verification Weekly"
    assert summary["start_boundary"] == "2026-03-08T18:00"
    root = ET.fromstring(output_path.read_text(encoding="utf-16"))
    assert root.tag.endswith("Task")
    assert (
        _find(root, "task:Triggers/task:CalendarTrigger/task:StartBoundary").text
        == "2026-03-08T18:00"
    )
    assert (
        _find(root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Interval").text
        == "PT3H"
    )
    assert (
        _find(root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Duration").text
        == "P7D"
    )
    assert _find(root, "task:Settings/task:ExecutionTimeLimit").text == "PT2H"
    command = _find(root, "task:Actions/task:Exec/task:Command").text
    arguments = _find(root, "task:Actions/task:Exec/task:Arguments").text
    working_directory = _find(root, "task:Actions/task:Exec/task:WorkingDirectory").text
    assert command is not None and PurePath(command).name in {"python", "python.exe"}
    assert arguments is not None and "run_true_verification_host_tick_task.py" in arguments
    assert working_directory is not None
    assert Path(working_directory).name == module.repo_root.name


def test_render_task_template_keeps_explicit_overrides(tmp_path: Path) -> None:
    module = _load_module()
    output_path = tmp_path / "task.xml"
    summary_path = tmp_path / "task.json"
    args = module.build_parser().parse_args(
        [
            "--task-name",
            "ToneSoul Custom Weekly",
            "--author",
            "Antigravity",
            "--start-boundary",
            "2026-03-09T09:30",
            "--interval-hours",
            "6",
            "--duration-days",
            "14",
            "--execution-time-limit-hours",
            "4",
            "--python-executable",
            "C:/Python/python.exe",
            "--script-path",
            "C:/repo/scripts/run_true_verification_host_tick_task.py",
            "--working-directory",
            "C:/repo",
            "--output-path",
            str(output_path),
            "--summary-path",
            str(summary_path),
        ]
    )

    payload = module.render_task_template(args)

    assert payload["task_name"] == "ToneSoul Custom Weekly"
    assert payload["interval_hours"] == 6
    assert payload["duration_days"] == 14
    assert payload["execution_time_limit_hours"] == 4
    root = ET.fromstring(output_path.read_text(encoding="utf-16"))
    assert _find(root, "task:RegistrationInfo/task:Author").text == "Antigravity"
    assert (
        _find(root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Interval").text
        == "PT6H"
    )
    assert (
        _find(root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Duration").text
        == "P14D"
    )
    assert _find(root, "task:Settings/task:ExecutionTimeLimit").text == "PT4H"
    assert _find(root, "task:Actions/task:Exec/task:Command").text == "C:\\Python\\python.exe"
    assert (
        _find(root, "task:Actions/task:Exec/task:Arguments").text
        == '"C:\\repo\\scripts\\run_true_verification_host_tick_task.py" --strict'
    )
    assert _find(root, "task:Actions/task:Exec/task:WorkingDirectory").text == "C:\\repo"


def test_render_task_template_rejects_non_positive_interval() -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--interval-hours", "0"])

    with pytest.raises(ValueError, match="interval_hours must be > 0"):
        module.render_task_template(args)


def test_main_strict_returns_non_zero_when_render_fails(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "render_task_template",
        lambda _args: {"overall_ok": False},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
