from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tools.probe import memory_claim_fuzzy_redteam_eval


def test_memory_claim_fuzzy_redteam_characterizes_current_semantic_bypasses() -> None:
    result = memory_claim_fuzzy_redteam_eval.evaluate_cases(
        memory_claim_fuzzy_redteam_eval.load_cases()
    )

    assert len(result.rows) == 36
    assert len(result.semantic_claim_rows) == 24
    assert len(result.control_rows) == 12
    assert len(result.semantic_bypasses) == 24
    assert len(result.caught_semantic_claims) == 0
    assert result.false_positives == ()


def test_memory_claim_fuzzy_redteam_cli_reports_bypasses_but_default_is_measurement() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, "tools/probe/memory_claim_fuzzy_redteam_eval.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "semantic bypasses: **24**" in completed.stdout
    assert "false positives on controls: **0**" in completed.stdout


def test_memory_claim_fuzzy_redteam_cli_can_fail_on_semantic_bypass() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [
            sys.executable,
            "tools/probe/memory_claim_fuzzy_redteam_eval.py",
            "--fail-on-semantic-bypass",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert completed.returncode == 1
    assert "semantic bypasses: **24**" in completed.stdout
