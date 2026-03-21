from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_private_memory_review_report as private_report


def _entries() -> list[dict[str, object]]:
    return [
        {
            "status": " M",
            "path": "memory/antigravity_architecture_plan_2026-03-07.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "memory",
        },
        {
            "status": " M",
            "path": "memory/antigravity_journal.md",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "memory",
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
            "status": " M",
            "path": "memory/crystals.jsonl",
            "staged": False,
            "unstaged": True,
            "untracked": False,
            "category": "memory",
        },
        {
            "status": "??",
            "path": "memory/autonomous/",
            "staged": False,
            "unstaged": False,
            "untracked": True,
            "category": "memory",
        },
    ]


def test_build_report_classifies_private_memory_settlement_paths(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        private_report.planner, "collect_worktree_entries", lambda repo_root: _entries()
    )

    payload, markdown = private_report.build_report(tmp_path)

    assert payload["overall_ok"] is False
    assert payload["summary"]["entry_count"] == 5
    assert payload["summary"]["mirror_then_archive_count"] == 2
    assert payload["summary"]["archive_to_private_count"] == 3
    assert payload["summary"]["inspect_count"] == 0

    entries = {item["path"]: item for item in payload["entries"]}
    assert (
        entries["memory/architecture_reflection_2026-03-07.md"]["disposition"]
        == "mirror_then_archive"
    )
    assert entries["memory/crystals.jsonl"]["disposition"] == "mirror_then_archive"
    assert entries["memory/antigravity_journal.md"]["disposition"] == "archive_to_private"
    assert entries["memory/autonomous/"]["kind"] == "private_runtime_namespace"
    assert "mirror" in markdown.lower()
    assert "archive to private" in markdown.lower()


def test_build_report_is_clean_when_no_memory_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(private_report.planner, "collect_worktree_entries", lambda repo_root: [])

    payload, _ = private_report.build_report(tmp_path)

    assert payload["overall_ok"] is True
    assert payload["summary"]["entry_count"] == 0
    assert payload["issues"] == []


def test_main_strict_writes_artifacts_and_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = {
        "generated_at": "2026-03-08T00:00:00Z",
        "overall_ok": False,
        "source": "scripts/run_private_memory_review_report.py",
        "summary": {
            "entry_count": 2,
            "mirror_then_archive_count": 1,
            "archive_to_private_count": 1,
            "inspect_count": 0,
            "kind_counts": [],
            "disposition_counts": [],
        },
        "entries": [],
        "issues": ["private_memory_lane_still_dirty"],
        "warnings": [],
    }
    monkeypatch.setattr(private_report, "build_report", lambda repo_root: (payload, "# Private\n"))
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_private_memory_review_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = private_report.main()

    assert exit_code == 1
    json_path = out_dir / private_report.JSON_FILENAME
    md_path = out_dir / private_report.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["summary"]["entry_count"] == 2
