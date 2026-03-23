from __future__ import annotations

import json
from pathlib import Path

import scripts.run_basename_divergence_distillation_report as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_covers_inventory_manual_review(tmp_path: Path) -> None:
    registry = {
        "version": "v1",
        "entries": [
            {
                "basename": "manifesto.md",
                "status": "resolved_boundary",
                "strategy": "keep_dual_boundary",
                "paths": ["constitution/manifesto.md", "docs/philosophy/manifesto.md"],
                "roles": {},
                "authority_rule": "keep dual",
                "editing_rule": "do not merge",
                "rationale": "different surfaces",
            }
        ],
    }
    inventory = {
        "collisions": [
            {"basename": "manifesto.md", "family": "manual_review"},
        ]
    }
    _write(
        tmp_path / "spec" / "governance" / "basename_divergence_registry_v1.json",
        json.dumps(registry, ensure_ascii=False, indent=2),
    )
    _write(
        tmp_path / "docs" / "status" / "doc_convergence_inventory_latest.json",
        json.dumps(inventory, ensure_ascii=False, indent=2),
    )
    _write(tmp_path / "constitution" / "manifesto.md", "# A\n")
    _write(tmp_path / "docs" / "philosophy" / "manifesto.md", "# B\n")

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["entry_count"] == 1
    assert payload["metrics"]["covered_manual_review_count"] == 1
    assert payload["issues"] == []


def test_main_writes_artifacts(tmp_path: Path) -> None:
    registry = {
        "version": "v1",
        "entries": [
            {
                "basename": "manifesto.md",
                "status": "resolved_boundary",
                "strategy": "keep_dual_boundary",
                "paths": ["constitution/manifesto.md", "docs/philosophy/manifesto.md"],
                "roles": {},
                "authority_rule": "keep dual",
                "editing_rule": "do not merge",
                "rationale": "different surfaces",
            }
        ],
    }
    _write(
        tmp_path / "spec" / "governance" / "basename_divergence_registry_v1.json",
        json.dumps(registry, ensure_ascii=False, indent=2),
    )
    _write(tmp_path / "constitution" / "manifesto.md", "# A\n")
    _write(tmp_path / "docs" / "philosophy" / "manifesto.md", "# B\n")

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    out_dir = tmp_path / "docs" / "status"
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["entry_count"] == 1
    assert "# Basename Divergence Distillation Latest" in markdown
