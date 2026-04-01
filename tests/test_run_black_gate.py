from __future__ import annotations

from pathlib import Path

import scripts.run_black_gate as black_gate


def test_resolve_black_mode_uses_advisory_full_for_schedule() -> None:
    assert black_gate.resolve_black_mode("schedule") == "advisory_full"
    assert black_gate.resolve_black_mode("pull_request") == "blocking_changed"


def test_collect_targets_for_pull_request_filters_python_roots(monkeypatch) -> None:
    monkeypatch.setattr(
        black_gate,
        "_collect_changed_files",
        lambda spec: [
            "tonesoul/runtime_adapter.py",
            "tests/test_runtime_adapter.py",
            "scripts/run_black_gate.py",
            "docs/README.md",
            "apps/web/src/index.ts",
        ],
    )

    payload = black_gate.collect_targets(
        event_name="pull_request",
        head_sha="merge-head",
        before_sha=None,
        pr_base_sha="base-sha",
        pr_head_sha="head-sha",
        local_base_candidates=["origin/master"],
        roots=["tonesoul", "tests", "scripts"],
    )

    assert payload["mode"] == "blocking_changed"
    assert payload["diff_spec"] == "base-sha...head-sha"
    assert payload["targets"] == [
        "scripts/run_black_gate.py",
        "tests/test_runtime_adapter.py",
        "tonesoul/runtime_adapter.py",
    ]


def test_collect_targets_for_schedule_uses_full_repo_walk(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "tonesoul").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    (root / "tonesoul" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (root / "tests" / "b.py").write_text("y = 2\n", encoding="utf-8")
    (root / "docs" / "skip.py").write_text("z = 3\n", encoding="utf-8")
    monkeypatch.chdir(root)

    payload = black_gate.collect_targets(
        event_name="schedule",
        head_sha="HEAD",
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
        roots=["tonesoul", "tests"],
    )

    assert payload["mode"] == "advisory_full"
    assert payload["targets"] == ["tests/b.py", "tonesoul/a.py"]


def test_main_returns_zero_when_advisory_full_detects_drift(monkeypatch, tmp_path: Path) -> None:
    artifact_path = tmp_path / "black_gate_report.json"
    monkeypatch.setattr(
        black_gate,
        "collect_targets",
        lambda **kwargs: {
            "event_name": "schedule",
            "mode": "advisory_full",
            "diff_spec": None,
            "base_ref": None,
            "targets": ["tonesoul/runtime_adapter.py"],
        },
    )

    class _Proc:
        returncode = 1
        stdout = "would reformat tonesoul/runtime_adapter.py"
        stderr = ""

    monkeypatch.setattr(black_gate, "_run_black", lambda targets, line_length: _Proc())

    exit_code = black_gate.main(
        [
            "--event-name",
            "schedule",
            "--strict",
            "--artifact-path",
            str(artifact_path),
        ]
    )

    assert exit_code == 0
    report_text = artifact_path.read_text(encoding="utf-8")
    assert '"mode": "advisory_full"' in report_text
    assert '"ok": false' in report_text


def test_main_returns_nonzero_when_blocking_changed_detects_drift(
    monkeypatch, tmp_path: Path
) -> None:
    artifact_path = tmp_path / "black_gate_report.json"
    monkeypatch.setattr(
        black_gate,
        "collect_targets",
        lambda **kwargs: {
            "event_name": "pull_request",
            "mode": "blocking_changed",
            "diff_spec": "base...head",
            "base_ref": "base",
            "targets": ["tests/test_runtime_adapter.py"],
        },
    )

    class _Proc:
        returncode = 1
        stdout = "would reformat tests/test_runtime_adapter.py"
        stderr = ""

    monkeypatch.setattr(black_gate, "_run_black", lambda targets, line_length: _Proc())

    exit_code = black_gate.main(
        [
            "--event-name",
            "pull_request",
            "--strict",
            "--artifact-path",
            str(artifact_path),
        ]
    )

    assert exit_code == 1
