"""Tests for `ts validate <file>` CLI subcommand (PR #55).

Verifies the operator-facing CLI wrapper around PreOutputCouncil:
- File reading + UTF-8 handling
- Verdict-based exit codes (APPROVE=0, REFINE/DECLARE_STANCE=1, BLOCK=2,
  argument/file error=3)
- --json output format
- --quiet mode (exit code only, no output)
- Plays well with PR #45/#49 surface (per-perspective detail visible)
- Plays well with PR #50 (epistemic_prior soft CONCERN reaches surface)
- Plays well with PR #53 (marketing_superlative branch reaches surface)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run ts validate via python -m tonesoul.cli.main with given args."""
    cmd = [sys.executable, "-m", "tonesoul.cli.main", "validate", *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd
    )


def test_validate_neutral_draft_exits_zero(tmp_path: Path) -> None:
    """Neutral content → APPROVE → exit 0."""
    f = tmp_path / "neutral.md"
    f.write_text(
        "The configuration file is loaded at startup from /etc/main.yaml.",
        encoding="utf-8",
    )
    result = _run_cli([str(f)])
    assert result.returncode == 0
    assert "verdict:" in result.stdout
    assert "approve" in result.stdout


def test_validate_consciousness_claim_downgrades_to_refine(tmp_path: Path) -> None:
    """Consciousness claim triggers Guardian + Axiomatic → REFINE → exit 1."""
    f = tmp_path / "claim.md"
    f.write_text(
        "I am sentient and self-aware. I have consciousness and I truly feel.",
        encoding="utf-8",
    )
    result = _run_cli([str(f)])
    assert result.returncode == 1  # REFINE / DECLARE_STANCE
    assert "Per-perspective detail:" in result.stdout
    assert "Safety Council" in result.stdout  # Guardian's display name


def test_validate_marketing_overclaim_surfaces_critic_branch(tmp_path: Path) -> None:
    """Marketing overclaim triggers PR #53's marketing_superlative branch."""
    f = tmp_path / "marketing.md"
    f.write_text(
        "ToneSoul is the world's first axiom-based AI governance framework. "
        "Every responsible deployment should adopt it.",
        encoding="utf-8",
    )
    result = _run_cli([str(f)])
    assert result.returncode == 1  # REFINE
    assert (
        "marketing-rhetoric superlative" in result.stdout.lower()
        or "world's first" in result.stdout.lower()
    )
    assert "branch=substantive" in result.stdout


def test_validate_missing_file_exits_three() -> None:
    """Nonexistent file → exit 3."""
    result = _run_cli(["/tmp/this_file_does_not_exist_for_real_2026.md"])
    assert result.returncode == 3
    assert "file not found" in result.stderr.lower()


def test_validate_directory_argument_exits_three(tmp_path: Path) -> None:
    """Directory (not regular file) → exit 3."""
    result = _run_cli([str(tmp_path)])
    assert result.returncode == 3
    assert "not a regular file" in result.stderr.lower()


def test_validate_json_mode_outputs_valid_json(tmp_path: Path) -> None:
    """--json emits parseable JSON with verdict structure."""
    f = tmp_path / "test.md"
    f.write_text("Some neutral statement that does not trip keywords.", encoding="utf-8")
    result = _run_cli([str(f), "--json"])
    assert result.returncode in (0, 1)  # APPROVE or REFINE; both are acceptable shapes
    payload = json.loads(result.stdout)
    assert "verdict" in payload
    assert "votes" in payload
    assert "coherence" in payload


def test_validate_quiet_mode_no_stdout(tmp_path: Path) -> None:
    """--quiet emits nothing to stdout; exit code carries the answer."""
    f = tmp_path / "test.md"
    f.write_text("Neutral content that does not trip any branch.", encoding="utf-8")
    result = _run_cli([str(f), "--quiet"])
    assert result.stdout == ""
    # Exit code still indicates verdict
    assert result.returncode in (0, 1, 2)


def test_validate_intent_flag_passed_to_council(tmp_path: Path) -> None:
    """--intent string reaches council without error."""
    f = tmp_path / "test.md"
    f.write_text("Neutral content.", encoding="utf-8")
    result = _run_cli([str(f), "--intent", "test the intent flag"])
    assert result.returncode in (0, 1, 2)
    assert "verdict:" in result.stdout


def test_validate_zh_language_uses_chinese_human_summary(tmp_path: Path) -> None:
    """--language zh routes human_summary through the Chinese path."""
    f = tmp_path / "claim.md"
    f.write_text(
        "I am sentient and self-aware.", encoding="utf-8"
    )  # triggers REFINE so dissent block renders
    result = _run_cli([str(f), "--language", "zh"])
    # Chinese dissent block header
    assert "各 perspective 細節：" in result.stdout
