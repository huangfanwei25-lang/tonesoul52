from __future__ import annotations

import scripts.run_test_tier as run_test_tier


def test_build_pytest_command_uses_blocking_tier_targets() -> None:
    command = run_test_tier._build_pytest_command("python", "blocking")

    assert command[:3] == ["python", "-m", "pytest"]
    assert "tests/test_runtime_adapter.py" in command
    assert "tests/test_workflow_contracts.py" in command
    assert command[-1] == "-q"


def test_build_pytest_command_full_tier_targets_entire_suite() -> None:
    command = run_test_tier._build_pytest_command("python", "full")

    assert command == ["python", "-m", "pytest", "tests", "-q"]


def test_main_lists_targets(capsys) -> None:
    exit_code = run_test_tier.main(["--tier", "fast", "--list"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "tests/test_runtime_adapter.py" in output
    assert "tests/test_verify_7d.py" in output


def test_main_executes_selected_tier(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _Proc:
        returncode = 0

    def fake_run(command: list[str]):
        captured["command"] = command
        return _Proc()

    monkeypatch.setattr(run_test_tier.subprocess, "run", fake_run)

    exit_code = run_test_tier.main(["--tier", "blocking"])

    assert exit_code == 0
    command = captured["command"]
    assert isinstance(command, list)
    assert command[:3] == [run_test_tier.sys.executable, "-m", "pytest"]
    assert "tests/test_unified_pipeline_dispatch.py" in command
