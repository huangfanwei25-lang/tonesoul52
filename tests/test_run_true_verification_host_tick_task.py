from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    path = (
        Path(__file__).resolve().parents[1] / "scripts" / "run_true_verification_host_tick_task.py"
    )
    spec = importlib.util.spec_from_file_location(
        "run_true_verification_host_tick_task_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_delegates_to_host_tick_module_and_suppresses_output(monkeypatch, capsys) -> None:
    module = _load_module()
    captured: dict[str, object] = {}

    class DummyHostTickModule:
        def main(self, argv):
            captured["argv"] = argv
            print("this should stay silent")
            return 0

    monkeypatch.setattr(module, "_load_host_tick_module", lambda: DummyHostTickModule())

    exit_code = module.main(["--strict"])

    assert exit_code == 0
    assert captured["argv"] == ["--strict"]
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""
