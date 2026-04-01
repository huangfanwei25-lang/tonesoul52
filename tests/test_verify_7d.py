import json
from datetime import datetime, timedelta, timezone

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


def test_check_sdh_uses_stdout_tail_when_stderr_empty(monkeypatch):
    def fake_run(command: list[str], timeout: int = 1200):
        return False, "[FAIL] backend /api/health connection refused", "", 1

    monkeypatch.setattr(verify_7d, "_run", fake_run)
    result = verify_7d._check_sdh("http://127.0.0.1:3000", "http://127.0.0.1:5000", 40)

    assert result.status == "fail"
    assert "connection refused" in result.note.lower()


def test_check_tdd_uses_extended_pytest_timeout(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run(command: list[str], timeout: int = 1200):
        captured["command"] = command
        captured["timeout"] = timeout
        return True, "", "", 0

    monkeypatch.setattr(verify_7d, "_run", fake_run)
    result = verify_7d._check_tdd()

    assert result.status == "pass"
    assert captured["timeout"] == verify_7d.TDD_PYTEST_TIMEOUT
    assert captured["command"] == [
        verify_7d.sys.executable,
        "scripts/run_test_tier.py",
        "--tier",
        verify_7d.DEFAULT_TDD_TEST_TIER,
    ]


def test_check_ddd_freshness_passes_for_recent_discussion(tmp_path):
    discussion = tmp_path / "agent_discussion_curated.jsonl"
    recent = datetime.now(timezone.utc) - timedelta(days=1)
    discussion.write_text(
        json.dumps(
            {
                "timestamp": recent.isoformat().replace("+00:00", "Z"),
                "author": "codex",
                "topic": "phase-closeout",
                "status": "done",
                "message": "fresh discussion closeout",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = verify_7d._check_ddd_freshness(discussion, stale_days=7)

    assert result.status == "pass"
    assert "age_days=" in result.note
    assert "remediation" not in result.note


def test_check_ddd_freshness_reports_closeout_remediation_for_stale_discussion(tmp_path):
    discussion = tmp_path / "agent_discussion_curated.jsonl"
    stale = datetime.now(timezone.utc) - timedelta(days=9)
    discussion.write_text(
        json.dumps(
            {
                "timestamp": stale.isoformat().replace("+00:00", "Z"),
                "author": "codex",
                "topic": "phase-closeout",
                "status": "done",
                "message": "stale discussion closeout",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = verify_7d._check_ddd_freshness(discussion, stale_days=7)

    assert result.status == "fail"
    assert "stale data" in result.note
    assert verify_7d.DDD_FRESHNESS_REMEDIATION in result.note
