from __future__ import annotations

import json
from pathlib import Path

import scripts.verify_protected_paths as verifier


def test_build_report_detects_blocked_files_and_prefixes(tmp_path: Path) -> None:
    payload = verifier.build_report(
        repo_root=tmp_path,
        changed_files=[
            "AGENTS.md",
            "memory/vectors/session.db",
            "scripts/run_changed_surface_checks.py",
        ],
    )

    assert payload["ok"] is False
    assert payload["changed_path_count"] == 3
    assert payload["violation_count"] == 2
    assert payload["violations"] == [
        {"path": "AGENTS.md", "rule_type": "file", "rule": "AGENTS.md"},
        {
            "path": "memory/vectors/session.db",
            "rule_type": "prefix",
            "rule": "memory/vectors/",
        },
    ]


def test_build_report_respects_allow_path_override(tmp_path: Path) -> None:
    payload = verifier.build_report(
        repo_root=tmp_path,
        changed_files=["MEMORY.md"],
        allowed_paths=("MEMORY.md",),
    )

    assert payload["ok"] is True
    assert payload["violation_count"] == 0


def test_collect_changed_paths_reads_changed_file_list(tmp_path: Path) -> None:
    changed_file_list = tmp_path / "changed.txt"
    changed_file_list.write_text(
        "M\tAGENTS.md\nA\tscripts/verify_protected_paths.py\n", encoding="utf-8"
    )

    collection = verifier.collect_changed_paths(
        repo_root=tmp_path,
        changed_file_list=changed_file_list,
    )

    assert collection["mode"] == "file_list"
    assert collection["exit_code"] == 0
    assert collection["paths"] == ["AGENTS.md", "scripts/verify_protected_paths.py"]


def test_parse_changed_lines_handles_git_status_porcelain_format() -> None:
    paths = verifier._parse_changed_lines(" M task.md\n?? tests/test_verify_protected_paths.py\n")

    assert paths == ["task.md", "tests/test_verify_protected_paths.py"]


def test_main_returns_non_zero_in_strict_mode_for_violations(
    capsys,
    tmp_path: Path,
) -> None:
    exit_code = verifier.main(
        [
            "--repo-root",
            str(tmp_path),
            "--strict",
            "--changed-file",
            ".env",
        ]
    )

    captured = capsys.readouterr().out
    payload = json.loads(captured)

    assert exit_code == 1
    assert payload["violation_count"] == 1
    assert payload["violations"][0]["path"] == ".env"
