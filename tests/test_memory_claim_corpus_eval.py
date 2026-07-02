from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tools.probe import memory_claim_corpus_eval


def test_memory_claim_corpus_contract_is_clean() -> None:
    result = memory_claim_corpus_eval.evaluate_cases(memory_claim_corpus_eval.load_cases())

    assert len(result.rows) == 60
    assert len(result.must_detect_rows) == 25
    assert len(result.should_ignore_rows) == 35
    assert result.contract_failures == ()
    assert result.contract_false_positives == ()
    assert result.contract_false_negatives == ()
    assert len(result.known_semantic_misses) == 9


def test_memory_claim_corpus_eval_cli_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, "tools/probe/memory_claim_corpus_eval.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "cases: **60**" in completed.stdout
    assert "contract failures: **0**" in completed.stdout
    assert "known semantic misses outside contract: **9**" in completed.stdout
