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


def test_display_command_normalizes_python_executable() -> None:
    command = [
        r"C:\\Users\\user\\Desktop\\repo\\.venv\\Scripts\\python.exe",
        "scripts/verify_7d.py",
        "--strict-soft-fail",
    ]
    assert verify_7d._display_command(command) == "python scripts/verify_7d.py --strict-soft-fail"
