from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_subjectivity_shadow_query as shadow_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


def test_build_report_compares_baseline_and_shadow_results(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "title": "Governance note",
            "summary": "governance baseline record",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    db.append(
        MemorySource.CUSTOM,
        {
            "title": "Governance conflict",
            "summary": "governance unresolved tension",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "source_record_ids": ["stim-002"],
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )

    payload, markdown = shadow_runner.build_report(
        db_path,
        query="governance",
        source_name="custom",
        profile="tension_first",
        limit=2,
        candidate_limit=5,
    )

    assert payload["overall_ok"] is True
    assert payload["inputs"]["query"] == "governance"
    assert payload["shadow"]["baseline_results"][0]["subjectivity_layer"] == "unclassified"
    assert payload["shadow"]["shadow_results"][0]["subjectivity_layer"] == "tension"
    assert payload["shadow"]["metrics"]["overlap_count"] == 2
    assert "Subjectivity Shadow Query Latest" in markdown


def test_main_writes_shadow_query_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "title": "Provenance note",
            "summary": "provenance baseline record",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    db.append(
        MemorySource.CUSTOM,
        {
            "title": "Provenance commitment",
            "summary": "provenance vow reviewed through operator lane",
            "subjectivity_layer": "vow",
            "layer": "factual",
            "promotion_gate": {
                "status": "approved",
                "reviewed_by": "operator",
                "review_basis": "Repeated reviewed tension.",
            },
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_subjectivity_shadow_query.py",
            "provenance",
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--source",
            "custom",
            "--profile",
            "reviewed_vow_first",
        ],
    )

    exit_code = shadow_runner.main()

    assert exit_code == 0
    json_path = out_dir / shadow_runner.JSON_FILENAME
    md_path = out_dir / shadow_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["inputs"]["profile"] == "reviewed_vow_first"
    assert payload["shadow"]["shadow_results"][0]["subjectivity_layer"] == "vow"
