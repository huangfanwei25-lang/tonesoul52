from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_subjectivity_report as subjectivity_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


def test_build_report_warns_when_db_did_not_exist(tmp_path: Path) -> None:
    db_path = tmp_path / "missing.db"

    payload, markdown = subjectivity_runner.build_report(db_path)

    assert payload["overall_ok"] is True
    assert payload["metrics"]["total_records"] == 0
    assert payload["metrics"]["unresolved_tension_count"] == 0
    assert payload["metrics"]["reviewed_vow_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]
    assert "soul db path did not exist" in payload["warnings"][0]
    assert "Subjectivity Report Latest" in markdown


def test_build_report_summarizes_unresolved_tensions_and_reviewed_vows(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Observed a stable preference during the session.",
            "layer": "factual",
            "subjectivity_layer": "event",
            "timestamp": "2026-03-10T01:00:00Z",
        },
    )
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Newer unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate", "source": "sleep_consolidate"},
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Reviewed commitment to keep provenance explicit.",
            "layer": "factual",
            "subjectivity_layer": "vow",
            "promotion_gate": {
                "status": "approved",
                "reviewed_by": "operator",
                "review_basis": "Repeated tension across reviewed cycles.",
            },
            "timestamp": "2026-03-10T04:00:00Z",
        },
    )

    payload, markdown = subjectivity_runner.build_report(
        db_path,
        source_name="custom",
        unresolved_limit=5,
        reviewed_vow_limit=5,
    )

    assert payload["overall_ok"] is False
    assert payload["metrics"]["total_records"] == 3
    assert payload["metrics"]["unresolved_tension_count"] == 1
    assert payload["metrics"]["reviewed_vow_count"] == 1
    assert payload["metrics"]["by_subjectivity_layer"]["vow"] == 1
    assert payload["unresolved_tensions"][0]["summary"] == "Newer unresolved tension."
    assert payload["reviewed_vows"][0]["summary"] == "Reviewed commitment to keep provenance explicit."
    assert payload["issues"] == ["1 unresolved tension record(s) pending review"]
    assert "Unresolved Tensions" in markdown
    assert "Reviewed Vows" in markdown


def test_main_strict_writes_artifacts_and_fails_when_unresolved_tensions_exist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Pending unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "timestamp": "2026-03-10T05:00:00Z",
        },
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_subjectivity_report.py",
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = subjectivity_runner.main()

    assert exit_code == 1
    json_path = out_dir / subjectivity_runner.JSON_FILENAME
    md_path = out_dir / subjectivity_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["unresolved_tension_count"] == 1
    assert payload["overall_ok"] is False
