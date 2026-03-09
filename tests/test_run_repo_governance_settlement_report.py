from __future__ import annotations

import json
from pathlib import Path

import scripts.run_repo_governance_settlement_report as governance_report


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_report_identifies_metadata_only_blocker(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": False,
            "checks": [
                {"name": "python_lint", "ok": True},
                {"name": "python_tests", "ok": True},
                {"name": "commit_attribution", "ok": False},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
            "rationale": "dirty worktree",
            "suggested_commands": [
                "git worktree add <clean-path> feat/env-perception-attribution-backfill"
            ],
        },
    )
    _write_json(
        tmp_path / "runtime_groups.json",
        {
            "change_groups": [
                {
                    "name": "repo_governance_and_settlement",
                    "entry_count": 24,
                    "sample_paths": [
                        "scripts/run_repo_healthcheck.py",
                        "tests/test_run_repo_governance_settlement_report.py",
                    ],
                    "recommended_actions": ["keep gates and settlement scripts together"],
                }
            ]
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
    )

    assert payload["overall_ok"] is False
    assert payload["settlement"]["status"] == "runtime_green_metadata_blocked"
    assert payload["settlement"]["metadata_only_blocker"] is True
    assert payload["settlement"]["runtime_green_except_metadata"] is True
    assert payload["healthcheck"]["failing_checks"] == ["commit_attribution"]
    assert payload["repo_governance_group"]["entry_count"] == 24
    assert payload["issues"] == ["metadata_only_commit_attribution_blocker"]
    assert "Metadata-only blocker: `true`" in markdown
    assert "Runtime green except attribution: `true`" in markdown


def test_build_report_surfaces_non_metadata_runtime_blocker(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "healthcheck.json",
        {
            "generated_at": "2026-03-08T14:20:47Z",
            "overall_ok": False,
            "checks": [
                {"name": "python_tests", "ok": False},
                {"name": "commit_attribution", "ok": False},
            ],
        },
    )
    _write_json(
        tmp_path / "attribution.json",
        {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
        },
    )
    _write_json(tmp_path / "runtime_groups.json", {"change_groups": []})

    payload, _ = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
    )

    assert payload["settlement"]["status"] == "runtime_blocked"
    assert payload["settlement"]["metadata_only_blocker"] is False
    assert payload["issues"] == [
        "blocking_check:python_tests",
        "blocking_check:commit_attribution",
    ]
    assert payload["warnings"] == ["missing_repo_governance_runtime_group"]


def test_main_strict_writes_artifacts_and_fails_when_not_green(monkeypatch, tmp_path: Path) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_repo_governance_settlement_report.py",
        "healthcheck": {
            "generated_at": "2026-03-08T00:00:00Z",
            "overall_ok": False,
            "pass_count": 10,
            "fail_count": 1,
            "failing_checks": ["commit_attribution"],
        },
        "attribution": {
            "recommendation": "defer_until_worktree_clean",
            "tree_equal": True,
            "current_missing_count": 5,
            "backfill_missing_count": 0,
            "rationale": "dirty",
            "suggested_commands": [],
        },
        "repo_governance_group": {
            "entry_count": 24,
            "sample_paths": [],
            "recommended_actions": [],
        },
        "settlement": {
            "status": "runtime_green_metadata_blocked",
            "metadata_only_blocker": True,
            "runtime_green_except_metadata": True,
            "next_actions": [],
        },
        "issues": ["metadata_only_commit_attribution_blocker"],
        "warnings": [],
    }
    monkeypatch.setattr(
        governance_report,
        "build_report",
        lambda *args, **kwargs: (payload, "# Repo\n"),
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_governance_settlement_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = governance_report.main()

    assert exit_code == 1
    json_path = out_dir / governance_report.JSON_FILENAME
    md_path = out_dir / governance_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["settlement"]["status"] == "runtime_green_metadata_blocked"
