from __future__ import annotations

import json
from pathlib import Path

import scripts.run_doc_convergence_inventory as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_detects_exact_and_divergent_collisions(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "engineering" / "OVERVIEW.md",
        "# Overview\n\n> Purpose: docs overview\n> Status: draft as of 2026-03-22\n",
    )
    _write(
        tmp_path / "law" / "engineering" / "OVERVIEW.md",
        "# Overview\n\n> Purpose: docs overview\n> Status: draft as of 2026-03-22\n",
    )
    _write(
        tmp_path / "docs" / "architecture" / "README.md",
        "# Architecture Readme\n\n> Purpose: architecture entry\n",
    )
    _write(
        tmp_path / "reports" / "README.md",
        "# Reports Readme\n\nThis report lane has different content.\n",
    )

    payload = runner.build_report(tmp_path)

    overview = next(item for item in payload["collisions"] if item["basename"] == "OVERVIEW.md")
    readme = next(item for item in payload["collisions"] if item["basename"] == "README.md")
    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert overview["family"] == "docs_law_engineering_mirror"
    assert overview["exact_match"] is True
    assert readme["exact_match"] is False
    assert "engineering_mirror_owner" in priority_ids
    assert payload["metrics"]["collision_count"] >= 2


def test_build_report_tracks_missing_metadata(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "# Repo\n")
    _write(
        tmp_path / "docs" / "architecture" / "A.md",
        "# A\n\n> Purpose: architecture note\n> Status: canonical as of 2026-03-22\n",
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert "README.md" in payload["missing_metadata"]["purpose"]
    assert "README.md" in payload["missing_metadata"]["date_hint"]
    assert payload["metrics"]["missing_purpose_count"] >= 1
    assert payload["metrics"]["missing_date_count"] >= 1
    assert payload["category_counts"]["root_entrypoint"] == 1
    assert "root_entrypoint_metadata_backfill" in priority_ids


def test_extract_purpose_accepts_bold_metadata_variants() -> None:
    text = "# A\n\n> **Document Purpose:** bold purpose line\n> **Last Updated**: 2026-03-23\n"

    assert runner._extract_purpose(text) == "bold purpose line"


def test_main_writes_inventory_artifacts(monkeypatch, tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "architecture" / "A.md",
        "# A\n\n> Purpose: architecture note\n> Status: canonical as of 2026-03-22\n",
    )
    out_dir = tmp_path / "docs" / "status"
    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    mermaid = (out_dir / runner.MERMAID_FILENAME).read_text(encoding="utf-8")
    assert payload["metrics"]["authored_file_count"] == 1
    assert "# Document Convergence Inventory Latest" in markdown
    assert "## Priority Actions" in markdown
    assert "## Top Missing Purpose Metadata" in markdown
    assert "graph TD" in mermaid


def test_build_report_uses_divergence_registry_when_present(tmp_path: Path) -> None:
    _write(tmp_path / "constitution" / "manifesto.md", "# A\n")
    _write(tmp_path / "docs" / "philosophy" / "manifesto.md", "# B\n")
    _write(
        tmp_path / "spec" / "governance" / "basename_divergence_registry_v1.json",
        json.dumps(
            {
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
            },
            ensure_ascii=False,
            indent=2,
        ),
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert "basename_divergence_registry_maintenance" in priority_ids


def test_build_report_uses_paradox_contract_when_present(tmp_path: Path) -> None:
    _write(tmp_path / "PARADOXES" / "paradox_003.json", '{"id":"P3","reasoning":"full"}\n')
    _write(tmp_path / "tests" / "fixtures" / "paradoxes" / "paradox_003.json", '{"id":"P3"}\n')
    _write(tmp_path / "docs" / "architecture" / "PARADOX_FIXTURE_OWNERSHIP_MAP.md", "# map\n")
    _write(
        tmp_path / "docs" / "status" / "paradox_fixture_ownership_latest.json",
        json.dumps({"metrics": {"needs_review_count": 0}}, ensure_ascii=False, indent=2),
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert "paradox_fixture_contract_maintenance" in priority_ids


def test_build_report_uses_private_shadow_contract_when_present(tmp_path: Path) -> None:
    _write(tmp_path / "memory" / ".hierarchical_index" / "vows_meta.json", '[{"statement":"a"}]\n')
    _write(
        tmp_path / "memory" / "memory" / ".hierarchical_index" / "vows_meta.json",
        '[{"statement":"b","agent_id":"ToneSoul"}]\n',
    )
    _write(
        tmp_path / "spec" / "governance" / "basename_divergence_registry_v1.json",
        json.dumps(
            {
                "version": "v1",
                "entries": [
                    {
                        "basename": "vows_meta.json",
                        "status": "unresolved_private_shadow",
                        "strategy": "defer_private_shadow_cleanup",
                        "paths": [
                            "memory/.hierarchical_index/vows_meta.json",
                            "memory/memory/.hierarchical_index/vows_meta.json",
                        ],
                        "roles": {},
                        "authority_rule": "defer",
                        "editing_rule": "do not mutate",
                        "rationale": "shadow",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    _write(
        tmp_path / "docs" / "architecture" / "PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md",
        "# map\n",
    )
    _write(
        tmp_path / "docs" / "status" / "private_memory_shadow_latest.json",
        json.dumps({"metrics": {"pair_count": 2}}, ensure_ascii=False, indent=2),
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert "private_memory_shadow_contract_maintenance" in priority_ids


def test_build_report_downgrades_historical_lane_when_contract_present(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.md",
        "# Chronicle\n\n*Generated at 20260312_232804*\n",
    )
    _write(
        tmp_path / "docs" / "chronicles" / "README.md",
        "# Chronicles\n\n> Purpose: lane readme\n> Last Updated: 2026-03-23\n",
    )
    _write(
        tmp_path / "docs" / "archive" / "deprecated_modules" / "README.md",
        "# Archive\n\n> Purpose: archive readme\n> Last Updated: 2026-03-23\n",
    )
    _write(
        tmp_path / "docs" / "architecture" / "HISTORICAL_DOC_LANE_POLICY.md",
        "# Policy\n",
    )
    _write(
        tmp_path / "docs" / "status" / "historical_doc_lane_latest.json",
        json.dumps({"metrics": {"chronicle_markdown_count": 1}}, ensure_ascii=False, indent=2),
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert (
        "docs/chronicles/scribe_chronicle_20260312_232804.md"
        not in payload["missing_metadata"]["purpose"]
    )
    assert "historical_doc_lane_contract_maintenance" in priority_ids


def test_build_report_keeps_historical_lane_in_backlog_without_contract(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.md",
        "# Chronicle\n\n*Generated at 20260312_232804*\n",
    )

    payload = runner.build_report(tmp_path)

    priority_ids = {item["id"] for item in payload["priority_actions"]}
    assert (
        "docs/chronicles/scribe_chronicle_20260312_232804.md"
        in payload["missing_metadata"]["purpose"]
    )
    assert "historical_doc_lane_contract" in priority_ids
