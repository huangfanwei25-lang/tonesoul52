import scripts.verify_7d as verify_7d


def test_env_or_default_uses_default_for_missing_or_blank(monkeypatch):
    monkeypatch.delenv(verify_7d.AUDIT_WEB_BASE_ENV, raising=False)
    assert verify_7d._env_or_default(verify_7d.AUDIT_WEB_BASE_ENV, "fallback") == "fallback"

    monkeypatch.setenv(verify_7d.AUDIT_WEB_BASE_ENV, "   ")
    assert verify_7d._env_or_default(verify_7d.AUDIT_WEB_BASE_ENV, "fallback") == "fallback"


def test_build_parser_reads_env_defaults(monkeypatch):
    monkeypatch.setenv(verify_7d.AUDIT_WEB_BASE_ENV, "http://127.0.0.1:3002")
    monkeypatch.setenv(verify_7d.AUDIT_API_BASE_ENV, "http://127.0.0.1:5001")
    parser = verify_7d.build_parser()
    args = parser.parse_args([])

    assert args.web_base == "http://127.0.0.1:3002"
    assert args.api_base == "http://127.0.0.1:5001"
    assert args.check_council_modes is True


def test_cli_overrides_env_defaults(monkeypatch):
    monkeypatch.setenv(verify_7d.AUDIT_WEB_BASE_ENV, "http://127.0.0.1:3002")
    monkeypatch.setenv(verify_7d.AUDIT_API_BASE_ENV, "http://127.0.0.1:5001")
    parser = verify_7d.build_parser()
    args = parser.parse_args(
        [
            "--web-base",
            "http://127.0.0.1:3010",
            "--api-base",
            "http://127.0.0.1:5010",
        ]
    )

    assert args.web_base == "http://127.0.0.1:3010"
    assert args.api_base == "http://127.0.0.1:5010"


def test_cli_can_disable_council_mode_checks():
    parser = verify_7d.build_parser()
    args = parser.parse_args(["--no-check-council-modes"])
    assert args.check_council_modes is False


def test_display_command_normalizes_python_executable() -> None:
    command = [
        r"C:\\Users\\user\\Desktop\\repo\\.venv\\Scripts\\python.exe",
        "scripts/verify_7d.py",
        "--strict-soft-fail",
    ]
    assert verify_7d._display_command(command) == "python scripts/verify_7d.py --strict-soft-fail"


def test_check_sdh_includes_council_mode_switch_flag(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run(command: list[str], timeout: int = 1200):
        captured["command"] = command
        captured["timeout"] = timeout
        return True, "", "", 0

    monkeypatch.setattr(verify_7d, "_run", fake_run)
    result = verify_7d._check_sdh("http://127.0.0.1:3000", "http://127.0.0.1:5000", 40)

    command = captured["command"]
    assert isinstance(command, list)
    assert "--check-council-modes" in command
    assert "--check-council-modes" in result.command
    assert result.status == "pass"


def test_check_sdh_can_skip_council_mode_switch_flag(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run(command: list[str], timeout: int = 1200):
        captured["command"] = command
        captured["timeout"] = timeout
        return True, "", "", 0

    monkeypatch.setattr(verify_7d, "_run", fake_run)
    result = verify_7d._check_sdh(
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        40,
        check_council_modes=False,
    )

    command = captured["command"]
    assert isinstance(command, list)
    assert "--check-council-modes" not in command
    assert "--check-council-modes" not in result.command
    assert result.status == "pass"
