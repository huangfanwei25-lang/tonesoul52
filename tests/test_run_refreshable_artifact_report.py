from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_refreshable_artifact_report as artifact_report


def _entries() -> list[dict[str, object]]:
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
            "status": " M",
            "path": "docs/status/probe_deadline/",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/runtime_probe_watch/",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/true_verification_weekly/",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/dream_observability_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/private_memory_review_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "generated_status",
        },
        {
            "status": "??",
            "path": "docs/status/runtime_source_change_groups_latest.json",
            "staged": False,
            "unstaged": False,
            "untracked": True,
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
            "status": "??",
            "path": "reports/analysis_gpt53.md",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "reports",
        },
        {
            "status": " M",
            "path": "docs/status/README.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "docs",
        },
    ]


def test_build_report_classifies_known_generated_and_manual_inputs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        artifact_report.planner, "collect_worktree_entries", lambda repo_root: _entries()
    )

    payload, markdown = artifact_report.build_report(tmp_path)

    assert payload["overall_ok"] is False
    assert payload["summary"]["entry_count"] == 9
    assert payload["summary"]["regenerate_count"] == 5
    assert payload["summary"]["namespace_regenerate_count"] == 2
    assert payload["summary"]["manual_review_count"] == 1
    assert payload["summary"]["archive_or_drop_count"] == 1
    assert payload["summary"]["inspect_count"] == 0

    entries = {item["path"]: item for item in payload["entries"]}
    assert entries["docs/status/repo_healthcheck_latest.json"]["disposition"] == "regenerate"
    assert (
        "run_repo_healthcheck.py"
        in entries["docs/status/repo_healthcheck_latest.json"]["producer_source"]
    )
    assert entries["docs/status/dream_observability_latest.json"]["disposition"] == "regenerate"
    assert entries["docs/status/private_memory_review_latest.json"]["disposition"] == "regenerate"
    assert (
        entries["docs/status/runtime_source_change_groups_latest.json"]["disposition"]
        == "regenerate"
    )
    assert entries["reports/model_comparison_latest.json"]["disposition"] == "regenerate"
    assert entries["reports/analysis_gpt53.md"]["disposition"] == "manual_review"
    assert entries["docs/status/probe_deadline/"]["disposition"] == "archive_or_drop"
    assert entries["docs/status/runtime_probe_watch/"]["disposition"] == "namespace_regenerate"
    assert (
        "python scripts/run_runtime_probe_watch.py --strict"
        in entries["docs/status/runtime_probe_watch/"]["namespace_commands"]
    )
    assert entries["docs/status/true_verification_weekly/"]["disposition"] == "namespace_regenerate"
    assert "docs/status/README.md" not in entries
    assert "reports/analysis_gpt53.md" in markdown
    assert "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion" in markdown
    assert "python scripts/run_runtime_probe_watch.py --strict" in markdown
    assert "Historical probe namespace" in markdown


def test_build_report_is_clean_when_no_refreshable_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(artifact_report.planner, "collect_worktree_entries", lambda repo_root: [])

    payload, _ = artifact_report.build_report(tmp_path)

    assert payload["overall_ok"] is True
    assert payload["summary"]["entry_count"] == 0
    assert payload["issues"] == []


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_refreshable_artifact_report.py",
        "summary": {
            "entry_count": 2,
            "regenerate_count": 1,
            "namespace_regenerate_count": 0,
            "manual_review_count": 1,
            "archive_or_drop_count": 0,
            "inspect_count": 0,
            "kind_counts": [],
            "category_counts": [],
            "disposition_counts": [],
        },
        "regenerate_groups": [],
        "namespace_groups": [],
        "archive_groups": [],
        "entries": [],
        "issues": ["refreshable_artifacts_lane_still_dirty"],
        "warnings": [],
    }
    monkeypatch.setattr(
        artifact_report, "build_report", lambda repo_root: (payload, "# Refreshable\n")
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_refreshable_artifact_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = artifact_report.main()

    assert exit_code == 1
    json_path = out_dir / artifact_report.JSON_FILENAME
    md_path = out_dir / artifact_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["summary"]["entry_count"] == 2
