from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_runtime_source_change_report as runtime_report


def _entries() -> list[dict[str, object]]:
    return [
        {
            "status": " M",
            "path": "scripts/run_repo_healthcheck.py",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "scripts",
        },
        {
            "status": "??",
            "path": "tests/test_run_repo_healthcheck.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "tests",
        },
        {
            "status": "??",
            "path": "scripts/run_repo_governance_settlement_report.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "scripts",
        },
        {
            "status": " M",
            "path": "tonesoul/governance/kernel.py",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "tonesoul",
        },
        {
            "status": "??",
            "path": "tests/test_llm_router.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "tests",
        },
        {
            "status": " M",
            "path": "tonesoul/perception/web_ingest.py",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "tonesoul",
        },
        {
            "status": "??",
            "path": "scripts/run_true_verification_experiment.py",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "scripts",
        },
        {
            "status": " M",
            "path": "api/chat.py",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "runtime_apps",
        },
        {
            "status": " M",
            "path": "skills/registry.json",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "skills",
        },
        {
            "status": "??",
            "path": ".vscode/settings.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "tooling",
        },
    ]


def test_build_report_groups_runtime_source_changes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        runtime_report.planner, "collect_worktree_entries", lambda repo_root: _entries()
    )

    payload, markdown = runtime_report.build_report(tmp_path)

    assert payload["overall_ok"] is False
    assert payload["summary"]["entry_count"] == 10
    assert payload["summary"]["ungrouped_count"] == 0

    groups = {group["name"]: group for group in payload["change_groups"]}
    assert groups["repo_governance_and_settlement"]["entry_count"] == 3
    assert groups["repo_governance_and_settlement"]["status_surfaces"] == [
        "docs/status/repo_healthcheck_latest.json",
        "docs/status/repo_governance_settlement_latest.json",
        "docs/status/refreshable_artifact_report_latest.json",
    ]
    assert groups["governance_pipeline_and_llm"]["entry_count"] == 2
    assert groups["perception_and_memory_ingest"]["entry_count"] == 1
    assert groups["autonomous_verification_runtime"]["entry_count"] == 1
    assert groups["autonomous_verification_runtime"]["status_surfaces"] == [
        "docs/status/repo_healthcheck_latest.json",
        "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
        "docs/status/dream_observability_latest.json",
        "docs/status/autonomous_registry_schedule_latest.json",
    ]
    assert groups["api_contract_surface"]["entry_count"] == 1
    assert groups["skill_and_registry_contracts"]["entry_count"] == 1
    assert groups["tooling_and_editor_contract"]["entry_count"] == 1
    assert "Runtime Source Change Groups Latest" in markdown
    assert "Ungrouped entries: `0`" in markdown
    assert "Status surface: `docs/status/repo_healthcheck_latest.json`" in markdown
    assert (
        "Status surface: "
        "`docs/status/true_verification_weekly/true_verification_task_status_latest.json`"
        in markdown
    )


def test_build_report_surfaces_ungrouped_runtime_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        runtime_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": "??",
                "path": "scripts/unknown_runtime_script.py",
                "staged": False,
                "unstaged": False,
                "untracked": True,
                "category": "scripts",
            }
        ],
    )

    payload, _ = runtime_report.build_report(tmp_path)

    assert payload["summary"]["ungrouped_count"] == 1
    assert payload["change_groups"][-1]["name"] == "ungrouped_runtime_drift"
    assert payload["change_groups"][-1]["status_surfaces"] == []


def test_build_report_groups_scribe_runtime_lane(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        runtime_report.planner,
        "collect_worktree_entries",
        lambda repo_root: [
            {
                "status": " M",
                "path": "scripts/run_scribe_cycle.py",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "scripts",
            },
            {
                "status": " M",
                "path": "tonesoul/scribe/scribe_engine.py",
                "staged": False,
                "unstaged": True,
                "untracked": False,
                "category": "tonesoul",
            },
            {
                "status": "??",
                "path": "tests/test_scribe_engine.py",
                "staged": False,
                "unstaged": False,
                "untracked": True,
                "category": "tests",
            },
            {
                "status": "??",
                "path": "tests/test_run_scribe_cycle.py",
                "staged": False,
                "unstaged": False,
                "untracked": True,
                "category": "tests",
            },
        ],
    )

    payload, markdown = runtime_report.build_report(tmp_path)

    assert payload["summary"]["entry_count"] == 4
    assert payload["summary"]["ungrouped_count"] == 0
    groups = {group["name"]: group for group in payload["change_groups"]}
    assert groups["scribe_chronicle_runtime"]["entry_count"] == 4
    assert groups["scribe_chronicle_runtime"]["status_surfaces"] == [
        "docs/status/scribe_status_latest.json"
    ]
    assert groups["scribe_chronicle_runtime"]["paths"] == [
        "scripts/run_scribe_cycle.py",
        "tonesoul/scribe/scribe_engine.py",
        "tests/test_scribe_engine.py",
        "tests/test_run_scribe_cycle.py",
    ]
    assert "Scribe Chronicle Runtime" in markdown
    assert "docs/status/scribe_status_latest.json" in markdown


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_runtime_source_change_report.py",
        "summary": {
            "entry_count": 2,
            "group_count": 1,
            "ungrouped_count": 0,
            "category_counts": [],
        },
        "change_groups": [],
        "issues": ["runtime_source_lane_still_dirty"],
        "warnings": [],
    }
    monkeypatch.setattr(runtime_report, "build_report", lambda repo_root: (payload, "# Runtime\n"))
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_runtime_source_change_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = runtime_report.main()

    assert exit_code == 1
    json_path = out_dir / runtime_report.JSON_FILENAME
    md_path = out_dir / runtime_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["summary"]["entry_count"] == 2
