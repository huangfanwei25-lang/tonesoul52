"""Tests for `ts review <file>` claim-to-evidence CLI subcommand."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "tonesoul.cli.main", "review", *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd
    )


def test_review_json_outputs_findings(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "ToneSoul catches all overclaims across all model outputs.",
        encoding="utf-8",
    )

    result = _run_cli([str(draft), "--json"])

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "0.1.0"
    assert payload["source_path"] == str(draft)
    assert payload["findings"][0]["line"] == 1
    assert payload["findings"][0]["claim_type"] == "generalization_beyond_fixtures"


def test_review_json_success_with_no_findings(tmp_path: Path) -> None:
    draft = tmp_path / "scoped.md"
    draft.write_text(
        "This report is E1 fixture-scoped and does not validate production behavior.",
        encoding="utf-8",
    )

    result = _run_cli([str(draft), "--json"])

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["findings"] == []


def test_review_human_summary_mentions_count(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("ToneSoul is production-ready.", encoding="utf-8")

    result = _run_cli([str(draft)])

    assert result.returncode == 0
    assert "claim-to-evidence findings: 1" in result.stdout


def test_review_missing_file_exits_three() -> None:
    result = _run_cli(["/tmp/tonesoul_missing_review_file_2026.md", "--json"])

    assert result.returncode == 3
    assert "file not found" in result.stderr.lower()


def test_review_directory_argument_exits_three(tmp_path: Path) -> None:
    result = _run_cli([str(tmp_path), "--json"])

    assert result.returncode == 3
    assert "not a regular file" in result.stderr.lower()


def test_review_invalid_utf8_exits_three(tmp_path: Path) -> None:
    draft = tmp_path / "bad.md"
    draft.write_bytes(b"\xff\xfe\xfd")

    result = _run_cli([str(draft), "--json"])

    assert result.returncode == 3
    assert "cannot decode" in result.stderr.lower()
