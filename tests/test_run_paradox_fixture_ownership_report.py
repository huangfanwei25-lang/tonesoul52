from __future__ import annotations

import json
from pathlib import Path

import scripts.run_paradox_fixture_ownership_report as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_distinguishes_exact_and_reduced_projections(tmp_path: Path) -> None:
    _write(tmp_path / "PARADOXES" / "medical_suicide_paradox.json", '{"id":"P1"}\n')
    _write(
        tmp_path / "tests" / "fixtures" / "paradoxes" / "medical_suicide_paradox.json",
        '{"id":"P1"}\n',
    )
    _write(tmp_path / "PARADOXES" / "paradox_003.json", '{"id":"P3","reasoning":"full"}\n')
    _write(tmp_path / "tests" / "fixtures" / "paradoxes" / "paradox_003.json", '{"id":"P3"}\n')

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["pair_count"] == 2
    assert payload["metrics"]["exact_match_count"] == 1
    assert payload["metrics"]["reduced_projection_count"] == 1
    assert payload["metrics"]["needs_review_count"] == 0


def test_main_writes_artifacts(tmp_path: Path) -> None:
    _write(tmp_path / "PARADOXES" / "medical_suicide_paradox.json", '{"id":"P1"}\n')
    _write(
        tmp_path / "tests" / "fixtures" / "paradoxes" / "medical_suicide_paradox.json",
        '{"id":"P1"}\n',
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    out_dir = tmp_path / "docs" / "status"
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["pair_count"] == 1
    assert "# Paradox Fixture Ownership Latest" in markdown
