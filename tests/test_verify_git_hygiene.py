from pathlib import Path

import scripts.verify_git_hygiene as hygiene


def test_parse_count_objects_extracts_numeric_fields() -> None:
    parsed = hygiene._parse_count_objects(
        "\n".join(
            [
                "count: 12",
                "size: 4.00 MiB",
                "in-pack: 4508",
                "packs: 1",
                "size-pack: 3.53 GiB",
                "garbage: 0",
            ]
        )
    )

    assert parsed["loose_count"] == 12
    assert parsed["in_pack"] == 4508
    assert parsed["packs"] == 1
    assert parsed["garbage"] == 0
    assert parsed["size"] == "4.00 MiB"
    assert parsed["size_pack"] == "3.53 GiB"


def test_summarize_fsck_tracks_unexpected_lines() -> None:
    summary = hygiene._summarize_fsck(
        "\n".join(
            [
                "dangling blob a1",
                "dangling commit b2",
                "missing tree c3",
            ]
        )
    )

    assert summary["line_count"] == 3
    assert summary["dangling_count"] == 2
    assert summary["prefix_counts"]["dangling"] == 2
    assert summary["prefix_counts"]["missing"] == 1
    assert summary["unexpected_lines"] == ["missing tree c3"]


def test_build_report_passes_within_thresholds() -> None:
    def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:  # noqa: ARG001
        if command[:2] == ["git", "count-objects"]:
            return 0, "count: 7\nin-pack: 200\npacks: 1\nsize: 1.00 MiB\nsize-pack: 5.00 MiB\n", ""
        if command[:2] == ["git", "fsck"]:
            return 0, "dangling blob a1\ndangling commit b2\n", ""
        if command[:3] == ["git", "ls-files", "-ci"]:
            return 0, "", ""
        raise AssertionError(f"unexpected command: {command}")

    report = hygiene.build_report(
        repo_root=Path("."),
        max_dangling=10,
        max_loose_count=100,
        runner=fake_runner,
    )

    assert report["overall_ok"] is True
    assert report["issues"] == []
    assert report["metrics"]["loose_count"] == 7
    assert report["metrics"]["dangling_count"] == 2
    assert report["metrics"]["tracked_ignored_count"] == 0
    assert [check["status"] for check in report["checks"]] == ["pass", "pass", "pass"]


def test_build_report_flags_threshold_or_integrity_failures() -> None:
    def fake_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:  # noqa: ARG001
        if command[:2] == ["git", "count-objects"]:
            return 0, "count: 9000\nin-pack: 10\npacks: 1\n", ""
        if command[:2] == ["git", "fsck"]:
            return 0, "dangling blob a1\nmissing tree bad\n", ""
        if command[:3] == ["git", "ls-files", "-ci"]:
            return 0, "tmp/ignored.bin\n", ""
        raise AssertionError(f"unexpected command: {command}")

    report = hygiene.build_report(
        repo_root=Path("."),
        max_dangling=50,
        max_loose_count=100,
        runner=fake_runner,
    )

    assert report["overall_ok"] is False
    assert report["metrics"]["loose_count"] == 9000
    assert report["metrics"]["fsck_unexpected_count"] == 1
    assert report["metrics"]["tracked_ignored_count"] == 1
    assert any("loose object count" in issue for issue in report["issues"])
    assert any("non-dangling diagnostics" in issue for issue in report["issues"])
    assert any("tracked-ignored files" in issue for issue in report["issues"])
    assert [check["status"] for check in report["checks"]] == ["fail", "fail", "fail"]


def test_render_markdown_contains_metrics_and_issues() -> None:
    payload = {
        "generated_at": "2026-02-10T06:30:00Z",
        "overall_ok": False,
        "config": {"max_dangling": 50, "max_loose_count": 100, "max_tracked_ignored": 0},
        "metrics": {
            "loose_count": 9000,
            "in_pack": 10,
            "packs": 1,
            "size": "1 MiB",
            "size_pack": "2 MiB",
            "dangling_count": 1,
            "fsck_prefix_counts": {"dangling": 1, "missing": 1},
            "fsck_unexpected_count": 1,
            "tracked_ignored_count": 1,
        },
        "checks": [
            {
                "name": "count_objects",
                "status": "fail",
                "exit_code": 0,
                "duration_seconds": 0.12,
                "command": "git count-objects -vH",
            },
            {
                "name": "fsck",
                "status": "fail",
                "exit_code": 0,
                "duration_seconds": 0.34,
                "command": "git fsck --no-reflogs",
            },
            {
                "name": "tracked_ignored",
                "status": "fail",
                "exit_code": 0,
                "duration_seconds": 0.02,
                "command": "git ls-files -ci --exclude-standard",
            },
        ],
        "issues": ["loose object count 9000 exceeds threshold 100"],
        "fsck_unexpected_lines": ["missing tree bad"],
        "tracked_ignored_paths": ["tmp/ignored.bin"],
    }

    markdown = hygiene._render_markdown(payload)
    assert "# Git Hygiene Latest" in markdown
    assert "- overall_ok: false" in markdown
    assert "| count_objects | FAIL | 0 | 0.12 | `git count-objects -vH` |" in markdown
    assert "## Metrics" in markdown
    assert "- loose_count: 9000" in markdown
    assert "- tracked_ignored_count: 1" in markdown
    assert "## Issues" in markdown
    assert "- loose object count 9000 exceeds threshold 100" in markdown
    assert "## Unexpected Fsck Lines" in markdown
    assert "- `missing tree bad`" in markdown
    assert "## Tracked Ignored Files" in markdown
    assert "- `tmp/ignored.bin`" in markdown
