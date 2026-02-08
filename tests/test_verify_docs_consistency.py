from pathlib import Path

import scripts.verify_docs_consistency as docs_consistency


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_passes_when_thresholds_and_curated_refs_align(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is True
    assert report["issues"] == []
    assert report["monthly_consolidation"] == {
        "workflow_exists": True,
        "has_schedule": True,
        "has_runner": True,
        "has_allow_missing_discussion": True,
    }


def test_build_report_fails_on_threshold_mismatch(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "verify_7d.py", "RDD_MIN_CASES = 20\n")
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 10\n")
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 10 tests\n")
    _write(tmp_path / "docs" / "7D_EXECUTION_SPEC.md", "at least 10 cases\n")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("mismatch" in issue for issue in report["issues"])
    assert any(
        "missing .github/workflows/monthly_consolidation.yml" in issue for issue in report["issues"]
    )


def test_build_report_fails_when_monthly_workflow_missing_allow_missing_discussion_flag(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict\n",
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("--allow-missing-discussion" in issue for issue in report["issues"])
