from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.plan_commit_attribution_base_switch as planner


def test_build_plan_defers_when_worktree_is_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = planner.SwitchPlanConfig(
        repo_root=tmp_path,
        current_ref="HEAD",
        backfill_ref="feat/backfill",
        artifact_path=tmp_path / "plan.json",
        strict=True,
    )

    def fake_report(head_ref: str, equivalent_ref: str) -> dict[str, object]:
        if head_ref == "HEAD":
            return {
                "ok": False,
                "missing_count": 5,
                "missing": [{"rev": "abc", "summary": "missing trailers", "error": ""}],
                "mode": "local_incremental",
                "range_spec": "base..HEAD",
                "equivalence": {
                    "tree_equal": True,
                    "head_tree": "tree-1",
                    "compare_tree": "tree-1",
                },
            }
        return {
            "ok": True,
            "missing_count": 0,
            "missing": [],
            "mode": "local_incremental",
            "range_spec": "base..feat/backfill",
            "equivalence": {"tree_equal": True, "head_tree": "tree-1", "compare_tree": "tree-1"},
        }

    monkeypatch.setattr(planner, "_attribution_report", fake_report)
    monkeypatch.setattr(
        planner,
        "_worktree_snapshot",
        lambda repo_root: {
            "dirty": True,
            "entry_count": 2,
            "staged_count": 1,
            "unstaged_count": 1,
            "untracked_count": 0,
            "sample_entries": [{"status": "M ", "path": "task.md", "category": "repo_misc"}],
            "category_counts": {"generated_status": 1, "tonesoul": 1},
            "command_ok": True,
            "stderr_tail": "",
        },
    )

    payload = planner.build_plan(config)

    assert payload["recommendation"] == "defer_until_worktree_clean"
    assert payload["tree_equal"] is True
    assert payload["current_missing_count"] == 5
    assert payload["backfill_missing_count"] == 0
    assert payload["suggested_commands"][0] == "git worktree add <clean-path> feat/backfill"
    assert payload["cleanup_priority"] == [
        {
            "category": "generated_status",
            "count": 1,
            "reason": "generated snapshots can usually be refreshed later",
        },
        {
            "category": "tonesoul",
            "count": 1,
            "reason": "core library changes are high-signal branch content",
        },
    ]


def test_build_plan_recommends_backfill_branch_when_clean(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = planner.SwitchPlanConfig(
        repo_root=tmp_path,
        current_ref="HEAD",
        backfill_ref="feat/backfill",
        artifact_path=tmp_path / "plan.json",
        strict=False,
    )

    def fake_report(head_ref: str, equivalent_ref: str) -> dict[str, object]:
        if head_ref == "HEAD":
            return {
                "ok": False,
                "missing_count": 5,
                "missing": [{"rev": "abc", "summary": "missing trailers", "error": ""}],
                "mode": "local_incremental",
                "range_spec": "base..HEAD",
                "equivalence": {
                    "tree_equal": True,
                    "head_tree": "tree-1",
                    "compare_tree": "tree-1",
                },
            }
        return {
            "ok": True,
            "missing_count": 0,
            "missing": [],
            "mode": "local_incremental",
            "range_spec": "base..feat/backfill",
            "equivalence": {"tree_equal": True, "head_tree": "tree-1", "compare_tree": "tree-1"},
        }

    monkeypatch.setattr(planner, "_attribution_report", fake_report)
    monkeypatch.setattr(
        planner,
        "_worktree_snapshot",
        lambda repo_root: {
            "dirty": False,
            "entry_count": 0,
            "staged_count": 0,
            "unstaged_count": 0,
            "untracked_count": 0,
            "category_counts": {},
            "sample_entries": [],
            "command_ok": True,
            "stderr_tail": "",
        },
    )

    payload = planner.build_plan(config)

    assert payload["recommendation"] == "continue_from_backfill_branch"
    assert payload["suggested_commands"][0] == "git switch feat/backfill"


def test_build_plan_requires_manual_review_when_trees_differ(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = planner.SwitchPlanConfig(
        repo_root=tmp_path,
        current_ref="HEAD",
        backfill_ref="feat/backfill",
        artifact_path=tmp_path / "plan.json",
        strict=True,
    )

    def fake_report(head_ref: str, equivalent_ref: str) -> dict[str, object]:
        if head_ref == "HEAD":
            return {
                "ok": False,
                "missing_count": 5,
                "missing": [{"rev": "abc", "summary": "missing trailers", "error": ""}],
                "mode": "local_incremental",
                "range_spec": "base..HEAD",
                "equivalence": {
                    "tree_equal": False,
                    "head_tree": "tree-1",
                    "compare_tree": "tree-2",
                },
            }
        return {
            "ok": True,
            "missing_count": 0,
            "missing": [],
            "mode": "local_incremental",
            "range_spec": "base..feat/backfill",
            "equivalence": {"tree_equal": False, "head_tree": "tree-2", "compare_tree": "tree-1"},
        }

    monkeypatch.setattr(planner, "_attribution_report", fake_report)
    monkeypatch.setattr(
        planner,
        "_worktree_snapshot",
        lambda repo_root: {
            "dirty": False,
            "entry_count": 0,
            "staged_count": 0,
            "unstaged_count": 0,
            "untracked_count": 0,
            "category_counts": {},
            "sample_entries": [],
            "command_ok": True,
            "stderr_tail": "",
        },
    )

    payload = planner.build_plan(config)

    assert payload["recommendation"] == "manual_review_required"
    assert payload["suggested_commands"] == []


def test_parse_status_lines_tracks_categories() -> None:
    payload = planner._parse_status_lines(
        [
            " M docs/status/repo_healthcheck_latest.json",
            " M docs/status/README.md",
            "?? docs/status/tonesoul_system_manifesto.md",
            " M tonesoul/unified_pipeline.py",
            "?? reports/model_comparison_latest.json",
        ]
    )

    assert payload["category_counts"] == {
        "docs": 2,
        "generated_status": 1,
        "reports": 1,
        "tonesoul": 1,
    }
    assert payload["sample_entries"][0]["category"] == "generated_status"
    assert payload["sample_entries"][1]["category"] == "docs"
    assert payload["sample_entries"][2]["category"] == "docs"
    assert payload["sample_entries"][3]["category"] == "tonesoul"
    assert payload["sample_entries"][4]["category"] == "reports"


def test_main_writes_plan_artifact(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out_path = tmp_path / "docs" / "status" / "plan.json"

    monkeypatch.setattr(
        planner,
        "build_plan",
        lambda config: {
            "generated_at": "2026-03-08T00:00:00Z",
            "source": "scripts/plan_commit_attribution_base_switch.py",
            "current_ref": "HEAD",
            "backfill_ref": "feat/backfill",
            "current_missing_count": 5,
            "backfill_missing_count": 0,
            "tree_equal": True,
            "recommendation": "continue_from_backfill_branch",
            "rationale": "clean",
            "suggested_commands": ["git switch feat/backfill"],
            "worktree": {"dirty": False, "category_counts": {}},
            "cleanup_priority": [],
            "current_report": {"ok": False},
            "backfill_report": {"ok": True},
        },
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "plan_commit_attribution_base_switch.py",
            "--repo-root",
            str(tmp_path),
            "--artifact-path",
            str(out_path),
        ],
    )

    exit_code = planner.main()

    assert exit_code == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["recommendation"] == "continue_from_backfill_branch"
    assert payload["suggested_commands"] == ["git switch feat/backfill"]
