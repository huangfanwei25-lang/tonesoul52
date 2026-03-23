from __future__ import annotations

import json
from pathlib import Path

import scripts.run_engineering_mirror_ownership_report as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_tracks_exact_sync_and_canonical_only(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "engineering" / "README.md", "# Canonical\n\n> Purpose: owner\n")
    _write(tmp_path / "law" / "engineering" / "README.md", "# Canonical\n\n> Purpose: mirror\n")
    _write(tmp_path / "docs" / "engineering" / "OVERVIEW.md", "# A\n\nnote\n")
    _write(tmp_path / "law" / "engineering" / "OVERVIEW.md", "# A\n")
    _write(tmp_path / "docs" / "engineering" / "prompt_hardening.md", "# Canonical only\n")

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["pair_count"] == 2
    assert payload["metrics"]["exact_match_count"] == 0
    assert payload["metrics"]["sync_needed_count"] == 1
    assert payload["metrics"]["canonical_only_count"] == 1
    assert "prompt_hardening.md" in payload["canonical_only"]
    assert "OVERVIEW.md" in payload["sync_needed"]
    readme = next(item for item in payload["pairs"] if item["relative_path"] == "README.md")
    assert readme["policy_mode"] == "role_scoped"
    assert readme["needs_sync"] is False


def test_main_writes_artifacts(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "engineering" / "README.md", "# Canonical\n")
    _write(tmp_path / "law" / "engineering" / "README.md", "# Canonical\n")

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    out_dir = tmp_path / "docs" / "status"
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["pair_count"] == 1
    assert "# Engineering Mirror Ownership Latest" in markdown
