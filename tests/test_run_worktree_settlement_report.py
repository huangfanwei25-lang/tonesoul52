from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_worktree_settlement_report as settlement_runner


def _dirty_plan() -> dict[str, object]:
    return {
        "recommendation": "defer_until_worktree_clean",
        "rationale": "worktree is dirty",
        "tree_equal": True,
        "current_missing_count": 5,
        "backfill_missing_count": 0,
        "cleanup_priority": [
            {"category": "generated_status", "count": 2, "reason": "refresh later"},
            {"category": "memory", "count": 1, "reason": "private review"},
            {"category": "tests", "count": 1, "reason": "pair with code"},
        ],
        "worktree": {
            "dirty": True,
            "entry_count": 4,
            "staged_count": 0,
            "unstaged_count": 2,
            "untracked_count": 2,
            "category_counts": {
                "generated_status": 2,
                "memory": 1,
                "tests": 1,
            },
        },
    }


def _dirty_entries() -> list[dict[str, object]]:
    return [
        {
            "status": " M",
            "path": "docs/status/repo_healthcheck_latest.json",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "reports/model_comparison_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "reports",
        },
        {
            "status": " M",
            "path": "memory/architecture_reflection_2026-03-07.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "memory",
        },
        {
            "status": "??",
            "path": "tests/test_run_worktree_settlement_report.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "tests",
        },
    ]


def test_build_report_groups_dirty_entries_into_lanes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: _dirty_plan()
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: _dirty_entries(),
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {
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
                ]
            },
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, markdown = settlement_runner.build_report(tmp_path, sample_limit=2)

    assert payload["overall_ok"] is False
    assert payload["planner"]["recommendation"] == "defer_until_worktree_clean"
    assert payload["worktree"]["entry_count"] == 4
    assert payload["summary"]["active_lane_count"] == 3

    refresh_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "refreshable_artifacts"
    )
    assert refresh_lane["active"] is True
    assert refresh_lane["entry_count"] == 2
    assert refresh_lane["categories"][0]["category"] == "generated_status"
    assert refresh_lane["handoff_preview_count"] == 2
    assert refresh_lane["admissibility_preview_count"] == 1
    assert payload["summary"]["refreshable_handoff_preview_count"] == 2
    assert payload["summary"]["refreshable_admissibility_preview_count"] == 1
    assert payload["subjectivity_focus_preview"] == {
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
    assert refresh_lane["handoff_previews"][0]["queue_shape"] == "deferred_monitoring"
    assert (
        refresh_lane["handoff_previews"][1]["admissibility_primary_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
    )
    assert refresh_lane["handoff_previews"][1]["requires_operator_action"] == "false"

    memory_lane = next(
        lane for lane in payload["settlement_lanes"] if lane["name"] == "private_memory_review"
    )
    assert memory_lane["active"] is True
    assert memory_lane["entry_count"] == 1
    assert "private" in memory_lane["recommended_actions"][0].lower()

    assert "Private memory paths remain governed by the dual-track boundary" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "Refreshable Artifacts" in markdown
    assert "Handoff previews: `2`" in markdown
    assert "requires_operator_action" in markdown
    assert "deferred_monitoring" in markdown
    assert "stable_history_only" in markdown
    assert "admissibility" in markdown


def test_build_report_returns_clean_status_when_worktree_is_clean(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clean_plan = {
        "recommendation": "no_switch_needed",
        "rationale": "clean",
        "tree_equal": True,
        "current_missing_count": 0,
        "backfill_missing_count": 0,
        "cleanup_priority": [],
        "worktree": {
            "dirty": False,
            "entry_count": 0,
            "staged_count": 0,
            "unstaged_count": 0,
            "untracked_count": 0,
            "category_counts": {},
        },
    }
    monkeypatch.setattr(
        settlement_runner.base_switch_planner, "build_plan", lambda config: clean_plan
    )
    monkeypatch.setattr(
        settlement_runner.base_switch_planner,
        "collect_worktree_entries",
        lambda repo_root: [],
    )
    monkeypatch.setattr(
        settlement_runner.refreshable_report,
        "build_report",
        lambda repo_root: (
            {"handoff_previews": [], "subjectivity_focus_preview": None},
            "# Refreshable Artifact Report Latest\n",
        ),
    )

    payload, _ = settlement_runner.build_report(tmp_path)

    assert payload["overall_ok"] is True
    assert payload["issues"] == []
    assert payload["summary"]["active_lane_count"] == 0
    assert payload["summary"]["refreshable_handoff_preview_count"] == 0
    assert payload["summary"]["refreshable_admissibility_preview_count"] == 0
    assert payload["subjectivity_focus_preview"] is None


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "planner": {"recommendation": "defer_until_worktree_clean"},
        "worktree": {"dirty": True},
        "settlement_lanes": [],
        "summary": {"active_lane_count": 1},
        "next_checkpoint": {
            "command": "python scripts/plan_commit_attribution_base_switch.py --strict"
        },
        "boundary_notes": {"public_scope": [], "private_scope": []},
        "issues": ["dirty_worktree_blocks_branch_movement"],
        "warnings": [],
    }
    monkeypatch.setattr(
        settlement_runner,
        "build_report",
        lambda repo_root, sample_limit=5, backfill_ref="": (
            payload,
            "# Worktree Settlement Latest\n",
        ),
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_worktree_settlement_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = settlement_runner.main()

    assert exit_code == 1
    json_path = out_dir / settlement_runner.JSON_FILENAME
    md_path = out_dir / settlement_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["planner"]["recommendation"] == "defer_until_worktree_clean"
