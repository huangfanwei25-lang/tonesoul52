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
    _write_json(
        tmp_path / "worktree_settlement.json",
        {
            "planner": {"recommendation": "manual_review_required"},
            "worktree": {"dirty": True},
            "summary": {
                "refreshable_handoff_preview_count": 3,
                "refreshable_admissibility_preview_count": 1,
            },
            "subjectivity_focus_preview": {
                "path": "docs/status/subjectivity_review_batch_latest.json",
                "queue_shape": "stable_history_only",
                "requires_operator_action": "false",
                "primary_status_line": (
                    "stable_deferred_history | A distributed vulnerability database for "
                    "Open Source | rows=50 lineages=12 cycles=30"
                ),
                "admissibility_primary_status_line": (
                    "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                ),
            },
            "settlement_lanes": [
                {
                    "name": "refreshable_artifacts",
                    "handoff_previews": [
                        {
                            "path": "docs/status/subjectivity_report_latest.json",
                            "queue_shape": "deferred_monitoring",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "deferred_monitoring | records=195 unresolved=50 deferred=50 "
                                "settled=31 reviewed_vows=0 | top_unresolved_status=deferred"
                            ),
                            "admissibility_primary_status_line": "",
                        },
                        {
                            "path": "docs/status/subjectivity_review_batch_latest.json",
                            "queue_shape": "stable_history_only",
                            "requires_operator_action": "false",
                            "primary_status_line": (
                                "stable_deferred_history | A distributed vulnerability database for "
                                "Open Source | rows=50 lineages=12 cycles=30"
                            ),
                            "admissibility_primary_status_line": (
                                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                            ),
                        },
                    ],
                }
            ],
        },
    )

    payload, markdown = governance_report.build_report(
        tmp_path,
        healthcheck_path="healthcheck.json",
        attribution_path="attribution.json",
        runtime_groups_path="runtime_groups.json",
        worktree_settlement_path="worktree_settlement.json",
    )

    assert payload["overall_ok"] is False
    assert payload["settlement"]["status"] == "runtime_green_metadata_blocked"
    assert payload["settlement"]["metadata_only_blocker"] is True
    assert payload["settlement"]["runtime_green_except_metadata"] is True
    assert payload["healthcheck"]["failing_checks"] == ["commit_attribution"]
    assert payload["repo_governance_group"]["entry_count"] == 24
    assert payload["worktree_settlement"]["refreshable_handoff_preview_count"] == 3
    assert payload["worktree_settlement"]["refreshable_admissibility_preview_count"] == 1
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] == {
        "path": "docs/status/subjectivity_review_batch_latest.json",
        "queue_shape": "stable_history_only",
        "requires_operator_action": "false",
        "primary_status_line": (
            "stable_deferred_history | A distributed vulnerability database for "
            "Open Source | rows=50 lineages=12 cycles=30"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
    }
    assert payload["worktree_settlement"]["handoff_previews"][0]["queue_shape"] == (
        "deferred_monitoring"
    )
    assert (
        payload["worktree_settlement"]["handoff_previews"][1]["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert (
        payload["worktree_settlement"]["handoff_previews"][1]["requires_operator_action"] == "false"
    )
    assert payload["issues"] == ["metadata_only_commit_attribution_blocker"]
    assert "Metadata-only blocker: `true`" in markdown
    assert "Runtime green except attribution: `true`" in markdown
    assert "Refreshable subjectivity previews: `3`" in markdown
    assert "Refreshable admissibility previews: `1`" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "requires_operator_action" in markdown
    assert "deferred_monitoring" in markdown


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
    assert payload["worktree_settlement"]["refreshable_handoff_preview_count"] == 0
    assert payload["worktree_settlement"]["refreshable_admissibility_preview_count"] == 0
    assert payload["worktree_settlement"]["subjectivity_focus_preview"] is None
    assert payload["issues"] == [
        "blocking_check:python_tests",
        "blocking_check:commit_attribution",
    ]
    assert payload["warnings"] == [
        "missing_repo_governance_runtime_group",
        "missing_worktree_settlement_artifact",
    ]


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
        "worktree_settlement": {
            "dirty": True,
            "planner_recommendation": "manual_review_required",
            "refreshable_handoff_preview_count": 3,
            "refreshable_admissibility_preview_count": 1,
            "handoff_previews": [],
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
