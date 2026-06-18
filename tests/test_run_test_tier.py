from __future__ import annotations

import scripts.run_test_tier as run_test_tier


def test_build_pytest_command_uses_core_tier_targets() -> None:
    command = run_test_tier._build_pytest_command("python", "core", use_xdist=False)

    assert command[:3] == ["python", "-m", "pytest"]
    assert "tests/test_runtime_adapter.py" in command
    assert "tests/test_workflow_contracts.py" in command
    assert command[-3:] == ["-q", "-m", "not slow"]


def test_build_pytest_command_keeps_legacy_blocking_alias() -> None:
    command = run_test_tier._build_pytest_command("python", "blocking", use_xdist=False)

    assert command == run_test_tier._build_pytest_command("python", "core", use_xdist=False)


def test_build_pytest_command_smoke_uses_xdist_by_default() -> None:
    command = run_test_tier._build_pytest_command("python", "smoke")

    assert "tests/test_verify_7d.py" in command
    assert command[-4:] == ["-m", "not slow", "-n", "auto"]


def test_build_pytest_command_slow_tier_runs_only_slow_tests() -> None:
    command = run_test_tier._build_pytest_command("python", "slow")

    assert command == ["python", "-m", "pytest", "tests", "-q", "-m", "slow", "-n", "auto"]


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

    exit_code = run_test_tier.main(["--tier", "core", "--no-xdist"])

    assert exit_code == 0
    command = captured["command"]
    assert isinstance(command, list)
    assert command[:3] == [run_test_tier.sys.executable, "-m", "pytest"]
    assert "tests/test_unified_pipeline_dispatch.py" in command
    assert "-n" not in command
