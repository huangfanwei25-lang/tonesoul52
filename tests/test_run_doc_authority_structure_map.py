from __future__ import annotations

import json
from pathlib import Path

import scripts.run_doc_authority_structure_map as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_uses_inventory_metadata_posture(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "status" / "doc_convergence_inventory_latest.json",
        json.dumps(
            {
                "missing_metadata": {
                    "purpose": ["docs/API_SPEC.md"],
                    "date_hint": ["docs/API_SPEC.md", "docs/COUNCIL_RUNTIME.md"],
                }
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    _write(tmp_path / "README.md", "# Repo\n> Purpose: root\n> Last Updated: 2026-03-23\n")
    _write(
        tmp_path / "README.zh-TW.md", "# Repo ZH\n> Purpose: root zh\n> Last Updated: 2026-03-23\n"
    )
    _write(
        tmp_path / "AI_ONBOARDING.md", "# AI\n> Purpose: onboarding\n> Last Updated: 2026-03-23\n"
    )
    _write(
        tmp_path / "docs" / "INDEX.md", "# Index\n> Purpose: index\n> Last Updated: 2026-03-23\n"
    )
    _write(tmp_path / "docs" / "README.md", "# Docs\n> Purpose: docs\n> Last Updated: 2026-03-23\n")
    _write(tmp_path / "docs" / "API_SPEC.md", "# API\n")
    _write(tmp_path / "docs" / "COUNCIL_RUNTIME.md", "# Council\n> Purpose: council\n")

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["group_count"] == len(runner.GROUPS)
    assert "docs/API_SPEC.md" in payload["missing_metadata_files"]
    assert "docs/COUNCIL_RUNTIME.md" in payload["missing_metadata_files"]
    entrypoints = next(group for group in payload["groups"] if group["id"] == "entrypoints")
    generated_status = next(
        group for group in payload["groups"] if group["id"] == "generated_status"
    )
    assert entrypoints["metadata_complete_count"] >= 5
    assert any(
        row["path"] == "docs/status/claim_authority_latest.json"
        for row in generated_status["files"]
    )


def test_main_writes_structure_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "status" / "doc_convergence_inventory_latest.json",
        json.dumps({"missing_metadata": {"purpose": [], "date_hint": []}}, indent=2),
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    payload = json.loads(
        (tmp_path / "docs" / "status" / runner.JSON_FILENAME).read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "docs" / "status" / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    mermaid = (tmp_path / "docs" / "status" / runner.MERMAID_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["group_count"] == len(runner.GROUPS)
    assert "# Documentation Authority Structure Latest" in markdown
    assert "graph TD" in mermaid
