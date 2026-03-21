from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "install_true_verification_task_scheduler.py"
    )
    spec = importlib.util.spec_from_file_location(
        "install_true_verification_task_scheduler_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_sets_safe_installer_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.apply is False
    assert args.skip_render is False
    assert args.task_name == "ToneSoul True Verification Weekly"
    assert args.xml_path.endswith("true_verification_task_scheduler.xml")
    assert args.script_path.endswith("run_true_verification_host_tick_task.py")
    assert args.install_summary_path.endswith(
        "true_verification_task_scheduler_install_latest.json"
    )


def test_install_task_dry_run_renders_but_does_not_call_schtasks(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    xml_path = tmp_path / "task.xml"
    render_summary_path = tmp_path / "render.json"
    install_summary_path = tmp_path / "install.json"

    class DummyRenderModule:
        DEFAULT_TASK_NAME = "ToneSoul True Verification Weekly"
        DEFAULT_OUTPUT_PATH = "unused.xml"
        DEFAULT_SUMMARY_PATH = "unused.json"
        DEFAULT_INTERVAL_HOURS = 3
        DEFAULT_DURATION_DAYS = 7
        DEFAULT_EXECUTION_TIME_LIMIT_HOURS = 2

        def render_task_template(self, args):
            xml_path.write_text("<Task />", encoding="utf-16")
            render_summary_path.write_text('{"overall_ok": true}', encoding="utf-8")
            return {"overall_ok": True, "output_path": str(xml_path)}

    def _unexpected_run(*_args, **_kwargs):
        raise AssertionError("schtasks should not run during dry-run install")

    monkeypatch.setattr(module, "_RENDER_MODULE", DummyRenderModule())
    monkeypatch.setattr(module.subprocess, "run", _unexpected_run)
    args = module.build_parser().parse_args(
        [
            "--xml-path",
            str(xml_path),
            "--render-summary-path",
            str(render_summary_path),
            "--install-summary-path",
            str(install_summary_path),
        ]
    )

    payload = module.install_task(args)

    assert payload["overall_ok"] is True
    assert payload["mode"] == "dry_run"
    assert payload["apply"] is False
    assert payload["rendered"] is True
    assert payload["command"][0] == "schtasks"
    summary = json.loads(install_summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "dry_run"


def test_install_task_apply_invokes_schtasks(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    xml_path = tmp_path / "task.xml"
    xml_path.write_text("<Task />", encoding="utf-16")
    install_summary_path = tmp_path / "install.json"

    class Completed:
        def __init__(self) -> None:
            self.returncode = 0
            self.stdout = "SUCCESS"
            self.stderr = ""

    captured: dict[str, object] = {}

    def _fake_run(command, capture_output, text, check):
        captured["command"] = command
        captured["capture_output"] = capture_output
        captured["text"] = text
        captured["check"] = check
        return Completed()

    monkeypatch.setattr(module.subprocess, "run", _fake_run)
    args = module.build_parser().parse_args(
        [
            "--skip-render",
            "--apply",
            "--xml-path",
            str(xml_path),
            "--install-summary-path",
            str(install_summary_path),
        ]
    )

    payload = module.install_task(args)

    assert payload["overall_ok"] is True
    assert payload["mode"] == "applied"
    assert captured["command"][0] == "schtasks"
    assert captured["command"][2] == "/TN"
    summary = json.loads(install_summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "applied"


def test_install_task_fails_when_xml_missing_and_render_skipped(tmp_path: Path) -> None:
    module = _load_module()
    missing_xml = tmp_path / "missing.xml"
    install_summary_path = tmp_path / "install.json"
    args = module.build_parser().parse_args(
        [
            "--skip-render",
            "--xml-path",
            str(missing_xml),
            "--install-summary-path",
            str(install_summary_path),
        ]
    )

    payload = module.install_task(args)

    assert payload["overall_ok"] is False
    assert payload["mode"] == "missing_xml"
    assert "not found" in payload["stderr"]
    summary = json.loads(install_summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "missing_xml"


def test_main_strict_returns_non_zero_when_install_fails(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "install_task",
        lambda _args: {"overall_ok": False, "mode": "missing_xml"},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
