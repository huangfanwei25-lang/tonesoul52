from pathlib import Path

import scripts.run_repo_healthcheck as healthcheck


def test_display_command_normalizes_python_executable() -> None:
    command = [
        r"C:\\Users\\user\\Desktop\\repo\\.venv\\Scripts\\python.exe",
        "scripts/run_repo_healthcheck.py",
        "--strict",
    ]
    assert command[0] != "python"
    assert (
        healthcheck._display_command(command) == "python scripts/run_repo_healthcheck.py --strict"
    )


def test_display_command_normalizes_npm_executable() -> None:
    command = [
        r"C:\\Program Files\\nodejs\\npm.cmd",
        "--prefix",
        "apps/web",
        "run",
        "test",
    ]
    assert healthcheck._display_command(command) == "npm --prefix apps/web run test"


def test_build_check_specs_includes_verify_7d_flags(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=True,
        check_council_modes=True,
        strict_soft_fail=True,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    assert "--include-sdh" in audit_7d["command"]
    assert "--check-council-modes" in audit_7d["command"]
    assert "--strict-soft-fail" in audit_7d["command"]
    assert "skip_reason" not in audit_7d


def test_build_check_specs_skips_7d_if_discussion_missing_and_allowed(tmp_path: Path) -> None:
    discussion_path = tmp_path / "missing.jsonl"

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        allow_missing_discussion=True,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    assert audit_7d["command"] == [r"C:\\repo\\.venv\\Scripts\\python.exe", "scripts/verify_7d.py"]
    assert audit_7d["skip_reason"] == f"missing discussion file: {discussion_path}"


def test_build_check_specs_can_disable_council_mode_checks(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=True,
        check_council_modes=False,
        strict_soft_fail=False,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    assert "--include-sdh" in audit_7d["command"]
    assert "--no-check-council-modes" in audit_7d["command"]
    assert "--check-council-modes" not in audit_7d["command"]


def test_render_markdown_contains_summary_and_failures() -> None:
    payload = {
        "generated_at": "2026-02-09T00:00:00Z",
        "overall_ok": False,
        "checks": [
            {
                "name": "python_lint",
                "status": "pass",
                "exit_code": 0,
                "duration_seconds": 1.23,
                "command": "python -m ruff check tonesoul tests scripts",
            },
            {
                "name": "audit_7d",
                "status": "fail",
                "exit_code": 1,
                "duration_seconds": 2.34,
                "command": "python scripts/verify_7d.py",
                "stdout_tail": "",
                "stderr_tail": "blocking failure",
            },
            {
                "name": "audit_7d_ci",
                "status": "skip",
                "exit_code": None,
                "duration_seconds": 0.0,
                "command": "python scripts/verify_7d.py",
                "skip_reason": "missing discussion file: memory/agent_discussion_curated.jsonl",
            },
        ],
    }

    markdown = healthcheck._render_markdown(payload)
    assert "# Repo Healthcheck Latest" in markdown
    assert "- overall_ok: false" in markdown
    assert (
        "| python_lint | PASS | 0 | 1.23 | `python -m ruff check tonesoul tests scripts` |"
        in markdown
    )
    assert "## Failures" in markdown
    assert "`audit_7d`: blocking failure" in markdown
    assert "## Skipped" in markdown
    assert "missing discussion file: memory/agent_discussion_curated.jsonl" in markdown
