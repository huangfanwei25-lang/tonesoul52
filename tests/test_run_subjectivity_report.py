from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_subjectivity_report as subjectivity_runner
from tonesoul.memory.reviewed_promotion import (
    apply_reviewed_promotion,
    build_reviewed_promotion_decision,
)
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


def test_build_report_warns_when_db_did_not_exist(tmp_path: Path) -> None:
    db_path = tmp_path / "missing.db"

    payload, markdown = subjectivity_runner.build_report(db_path)

    assert payload["overall_ok"] is True
    assert payload["metrics"]["total_records"] == 0
    assert payload["metrics"]["unresolved_tension_count"] == 0
    assert payload["metrics"]["deferred_tension_count"] == 0
    assert payload["metrics"]["settled_tension_count"] == 0
    assert payload["metrics"]["reviewed_vow_count"] == 0
    assert payload["handoff"] == {
        "queue_shape": "empty_report",
        "requires_operator_action": False,
        "top_unresolved_status": "",
        "primary_status_line": "empty_report | records=0 unresolved=0 deferred=0 settled=0 reviewed_vows=0",
    }
    assert payload["primary_status_line"] == payload["handoff"]["primary_status_line"]
    assert payload["status_lines"] == [payload["primary_status_line"]]
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
    assert payload["metrics"]["deferred_tension_count"] == 0
    assert payload["metrics"]["settled_tension_count"] == 0
    assert payload["metrics"]["reviewed_vow_count"] == 1
    assert payload["handoff"] == {
        "queue_shape": "action_required",
        "requires_operator_action": True,
        "top_unresolved_status": "candidate",
        "primary_status_line": "action_required | records=3 unresolved=1 deferred=0 settled=0 reviewed_vows=1 | top_unresolved_status=candidate",
    }
    assert payload["primary_status_line"] == payload["handoff"]["primary_status_line"]
    assert payload["status_lines"] == [payload["primary_status_line"]]
    assert payload["metrics"]["by_subjectivity_layer"]["vow"] == 1
    assert payload["metrics"]["unresolved_by_status"] == {"candidate": 1}
    assert payload["unresolved_tensions"][0]["summary"] == "Newer unresolved tension."
    assert (
        payload["reviewed_vows"][0]["summary"] == "Reviewed commitment to keep provenance explicit."
    )
    assert payload["issues"] == ["1 unresolved tension record(s) pending review"]
    assert "## Handoff" in markdown
    assert "- queue_shape: action_required" in markdown
    assert "- requires_operator_action: true" in markdown
    assert "## Status Lines" in markdown
    assert (
        "- action_required | records=3 unresolved=1 deferred=0 settled=0 reviewed_vows=1 | top_unresolved_status=candidate"
        in markdown
    )
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
    assert payload["metrics"]["deferred_tension_count"] == 0
    assert payload["overall_ok"] is False


def test_build_report_excludes_settled_tension_after_review(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    source = MemorySource.CUSTOM
    payload = {
        "summary": "Reviewed unresolved tension.",
        "layer": "experiential",
        "subjectivity_layer": "tension",
        "promotion_gate": {"status": "candidate"},
        "evidence": ["cycle-1", "cycle-2"],
        "provenance": {"source": "dream_engine"},
        "timestamp": "2026-03-10T06:00:00Z",
    }
    record_id = db.append(source, payload)
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor="operator",
        review_basis="Repeated unresolved tension across reviewed cycles.",
        reviewed_record_id=record_id,
        status="approved",
    )
    apply_reviewed_promotion(db, source=source, payload=payload, decision=decision)

    report, _ = subjectivity_runner.build_report(
        db_path,
        source_name="custom",
        unresolved_limit=5,
        reviewed_vow_limit=5,
    )

    assert report["overall_ok"] is True
    assert report["metrics"]["unresolved_tension_count"] == 0
    assert report["metrics"]["deferred_tension_count"] == 0
    assert report["metrics"]["settled_tension_count"] == 1
    assert report["metrics"]["reviewed_vow_count"] == 1
    assert report["handoff"] == {
        "queue_shape": "settled_or_reviewed",
        "requires_operator_action": False,
        "top_unresolved_status": "",
        "primary_status_line": "settled_or_reviewed | records=2 unresolved=0 deferred=0 settled=1 reviewed_vows=1",
    }
    assert report["issues"] == []


def test_build_report_surfaces_deferred_unresolved_tension_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Deferred unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {
                "status": "deferred",
                "reviewed_by": "operator",
                "review_basis": "Keep watching for broader context diversity.",
            },
            "timestamp": "2026-03-10T07:00:00Z",
        },
    )

    payload, markdown = subjectivity_runner.build_report(
        db_path,
        source_name="custom",
        unresolved_limit=5,
        reviewed_vow_limit=5,
    )

    assert payload["overall_ok"] is False
    assert payload["metrics"]["unresolved_tension_count"] == 1
    assert payload["metrics"]["deferred_tension_count"] == 1
    assert payload["metrics"]["unresolved_by_status"] == {"deferred": 1}
    assert payload["handoff"] == {
        "queue_shape": "deferred_monitoring",
        "requires_operator_action": False,
        "top_unresolved_status": "deferred",
        "primary_status_line": "deferred_monitoring | records=1 unresolved=1 deferred=1 settled=0 reviewed_vows=0 | top_unresolved_status=deferred",
    }
    assert "1 unresolved tension record(s) are explicitly deferred" in payload["warnings"]
    assert "## Unresolved Statuses" in markdown
    assert "- queue_shape: deferred_monitoring" in markdown
    assert "- Deferred unresolved tension. (`deferred`, `custom`" in markdown


def test_build_report_surfaces_deferred_review_context_from_action_log(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    source = MemorySource.CUSTOM
    payload = {
        "summary": "Deferred unresolved tension with explicit revisit condition.",
        "layer": "experiential",
        "subjectivity_layer": "tension",
        "promotion_gate": {"status": "candidate"},
        "evidence": ["cycle-1", "cycle-2"],
        "provenance": {"source": "dream_engine"},
        "source_record_ids": ["stim-010"],
        "timestamp": "2026-03-10T08:00:00Z",
    }
    record_id = db.append(source, payload)
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor="operator",
        review_basis="Keep observing until a second source context appears.",
        reviewed_record_id=record_id,
        status="deferred",
        notes="Wake this up only when the same direction appears outside the current source loop.",
    )
    apply_reviewed_promotion(db, source=source, payload=payload, decision=decision)

    report, markdown = subjectivity_runner.build_report(
        db_path,
        source_name="custom",
        unresolved_limit=5,
        reviewed_vow_limit=5,
    )

    assert report["unresolved_tensions"][0]["review_basis"] == (
        "Keep observing until a second source context appears."
    )
    assert report["unresolved_tensions"][0]["review_notes"] == (
        "Wake this up only when the same direction appears outside the current source loop."
    )
    assert "review_basis: Keep observing until a second source context appears." in markdown
    assert (
        "review_notes: Wake this up only when the same direction appears outside the current source loop."
        in markdown
    )
