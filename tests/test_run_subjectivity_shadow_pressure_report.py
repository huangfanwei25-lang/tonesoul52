from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_subjectivity_shadow_pressure_report as pressure_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


def test_build_report_aggregates_shadow_pressure_metrics(tmp_path: Path) -> None:
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
            "source_record_ids": ["stim-004"],
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )

    payload, markdown = pressure_runner.build_report(
        db_path,
        queries=["governance", "absent"],
        source_name="custom",
        profile="tension_first",
        limit=2,
        candidate_limit=5,
    )

    assert payload["overall_ok"] is True
    assert payload["pressure"]["metrics"]["query_count"] == 2
    assert payload["pressure"]["metrics"]["changed_query_count"] == 1
    assert payload["pressure"]["metrics"]["tension_top1_gain_count"] == 1
    assert payload["pressure"]["no_hit_queries"] == ["absent"]
    assert "Subjectivity Shadow Pressure Latest" in markdown


def test_main_writes_pressure_artifacts_and_uses_default_queries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "title": "Memory note",
            "summary": "memory baseline record",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_subjectivity_shadow_pressure_report.py",
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--source",
            "custom",
        ],
    )

    exit_code = pressure_runner.main()

    assert exit_code == 0
    json_path = out_dir / pressure_runner.JSON_FILENAME
    md_path = out_dir / pressure_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["inputs"]["queries"] == list(pressure_runner.DEFAULT_QUERIES)
    assert any(
        "used default subjectivity shadow query set" in warning for warning in payload["warnings"]
    )
