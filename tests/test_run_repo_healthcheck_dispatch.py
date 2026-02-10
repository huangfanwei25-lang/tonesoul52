from __future__ import annotations

import scripts.run_repo_healthcheck_dispatch as dispatch


def test_build_command_rejects_non_positive_timeout() -> None:
    config = dispatch.DispatchConfig(
        include_sdh=True,
        web_base="http://127.0.0.1:3002",
        api_base="http://127.0.0.1:5001",
        sdh_timeout="0",
        check_council_modes=True,
    )

    command, warnings, error = dispatch.build_command(config)
    assert command[:2] == ["python", "scripts/run_repo_healthcheck.py"]
    assert warnings == []
    assert error is not None
    assert "positive integer" in error


def test_build_command_warns_when_sdh_inputs_set_but_include_disabled() -> None:
    config = dispatch.DispatchConfig(
        include_sdh=False,
        web_base="http://127.0.0.1:3002",
        api_base="",
        sdh_timeout="40",
        check_council_modes=True,
    )

    command, warnings, error = dispatch.build_command(config)
    assert error is None
    assert "--include-sdh" not in command
    assert warnings == [
        "SDH inputs were provided but include_sdh=false; web/api/timeout inputs will be ignored."
    ]


def test_build_command_includes_sdh_flags_and_overrides() -> None:
    config = dispatch.DispatchConfig(
        include_sdh=True,
        web_base="http://127.0.0.1:3002",
        api_base="http://127.0.0.1:5001",
        sdh_timeout="40",
        check_council_modes=False,
    )

    command, warnings, error = dispatch.build_command(config)
    assert error is None
    assert warnings == []
    assert "--include-sdh" in command
    assert "--no-check-council-modes" in command
    assert "--check-council-modes" not in command
    assert "--web-base" in command
    assert "http://127.0.0.1:3002" in command
    assert "--api-base" in command
    assert "http://127.0.0.1:5001" in command
    assert "--sdh-timeout" in command
    assert "40" in command


def test_build_command_warns_on_single_side_endpoint() -> None:
    config = dispatch.DispatchConfig(
        include_sdh=True,
        web_base="http://127.0.0.1:3002",
        api_base="",
        sdh_timeout="",
        check_council_modes=True,
    )

    _, warnings, error = dispatch.build_command(config)
    assert error is None
    assert len(warnings) == 1
    assert "api_base is empty" in warnings[0]
