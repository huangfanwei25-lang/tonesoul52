from __future__ import annotations

import json
from pathlib import Path

import scripts.run_l7_operational_packet as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_packet_defaults_to_latest_repo_state_without_change_context(tmp_path: Path) -> None:
    payload = runner.build_packet(repo_root=tmp_path)

    assert payload["status"] == "ready"
    assert payload["question_type"] == "latest_repo_state"
    assert payload["route_source"] == "default_no_change_context"
    assert payload["changed_surface_summary"]["changed_path_count"] == 0
    assert payload["open_sequence"][0]["value"] == "docs/status/repo_healthcheck_latest.json"
    assert payload["protected_path_summary"]["violation_count"] == 0


def test_build_packet_uses_change_validation_route_and_plans_checks(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py",
        "def test_smoke():\n    assert True\n",
    )

    payload = runner.build_packet(
        repo_root=tmp_path,
        changed_files=["scripts/run_changed_surface_checks.py"],
    )

    assert payload["question_type"] == "change_validation"
    assert payload["route_source"] == "inferred_from_change_surface"
    assert payload["changed_surface_summary"]["changed_path_count"] == 1
    assert "python_runtime" in payload["changed_surface_summary"]["surface_ids"]
    assert any(check["name"] == "protected_paths" for check in payload["recommended_checks"])
    assert any(check["name"] == "python_lint_changed" for check in payload["recommended_checks"])
    assert any(check["name"] == "targeted_pytest" for check in payload["recommended_checks"])


def test_main_writes_operational_packet_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    exit_code = runner.main(
        [
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--question-type",
            "architecture_meaning",
        ]
    )

    assert exit_code == 0
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["question_type"] == "architecture_meaning"
    assert payload["open_sequence"][0]["value"] == (
        "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md"
    )
    assert "# L7 Operational Packet Latest" in markdown
