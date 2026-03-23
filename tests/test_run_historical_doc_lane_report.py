from __future__ import annotations

import json
from pathlib import Path

import scripts.run_historical_doc_lane_report as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_tracks_chronicle_pairs_and_markers(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.md",
        "# Chronicle\n\n*Generated at 20260312_232804*\n",
    )
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.json",
        '{"cycle":"a"}\n',
    )
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260313_042310.md",
        "# Chronicle\n\n*Generated at 2026-03-13T04:23:10Z*\n",
    )
    _write(tmp_path / "docs" / "archive" / "deprecated_modules" / "README.md", "# Archive\n")

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["archive_markdown_count"] == 1
    assert payload["metrics"]["chronicle_markdown_count"] == 2
    assert payload["metrics"]["chronicle_json_pair_count"] == 1
    assert payload["metrics"]["chronicle_md_only_count"] == 1
    assert payload["metrics"]["generated_marker_count"] == 2
    assert payload["metrics"]["filename_timestamp_count"] == 2


def test_main_writes_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.md",
        "# Chronicle\n\n*Generated at 20260312_232804*\n",
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    out_dir = tmp_path / "docs" / "status"
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["chronicle_markdown_count"] == 1
    assert "# Historical Document Lane Latest" in markdown
