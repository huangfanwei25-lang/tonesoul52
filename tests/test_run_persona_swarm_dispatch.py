from __future__ import annotations

import scripts.run_persona_swarm_dispatch as dispatch


def test_build_command_validates_input_path_exists(tmp_path) -> None:
    missing_path = tmp_path / "missing.json"
    config = dispatch.DispatchConfig(strict=True, input_path=str(missing_path))

    command, warnings, error = dispatch.build_command(config)
    assert command[:2] == ["python", "scripts/run_persona_swarm_framework.py"]
    assert warnings == []
    assert error is not None
    assert "input_path does not exist" in error


def test_build_command_includes_strict_and_input_when_present(tmp_path) -> None:
    payload_path = tmp_path / "swarm_input.json"
    payload_path.write_text("{}", encoding="utf-8")

    config = dispatch.DispatchConfig(strict=True, input_path=str(payload_path))
    command, warnings, error = dispatch.build_command(config)

    assert error is None
    assert warnings == []
    assert "--strict" in command
    assert "--input" in command
    assert str(payload_path) in command


def test_build_command_without_strict_excludes_flag(tmp_path) -> None:
    payload_path = tmp_path / "swarm_input.json"
    payload_path.write_text("{}", encoding="utf-8")

    config = dispatch.DispatchConfig(strict=False, input_path=str(payload_path))
    command, warnings, error = dispatch.build_command(config)

    assert error is None
    assert warnings == []
    assert "--strict" not in command


def test_build_command_warns_for_non_json_input_extension(tmp_path) -> None:
    payload_path = tmp_path / "swarm_input.txt"
    payload_path.write_text("{}", encoding="utf-8")

    config = dispatch.DispatchConfig(strict=True, input_path=str(payload_path))
    command, warnings, error = dispatch.build_command(config)

    assert error is None
    assert "--input" in command
    assert len(warnings) == 1
    assert "does not end with .json" in warnings[0]
