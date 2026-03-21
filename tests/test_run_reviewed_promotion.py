from __future__ import annotations

from pathlib import Path

import pytest

import scripts.run_reviewed_promotion as review_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


def _seed_tension(db: SqliteSoulDB) -> str:
    return db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Pending reviewed-promotion candidate.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate", "source": "sleep_consolidate"},
            "evidence": ["cycle-1", "cycle-2"],
            "provenance": {"source": "dream_engine"},
            "source_record_ids": ["stim-010"],
            "timestamp": "2026-03-10T07:00:00Z",
        },
    )


def test_build_receipt_approves_tension_and_settles_queue(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    record_id = _seed_tension(db)

    payload = review_runner.build_receipt(
        db_path,
        record_id=record_id,
        review_actor="operator",
        actor_type="human",
        status="approved",
        review_basis="Repeated unresolved tension across reviewed cycles.",
    )

    assert payload["overall_ok"] is True
    assert payload["result"]["review_log_id"]
    assert payload["result"]["promoted_record_id"]
    assert payload["result"]["pre_review_unresolved"] is True
    assert payload["result"]["post_review_unresolved"] is False
    assert payload["metrics"]["unresolved_tension_count"] == 0
    assert payload["metrics"]["settled_tension_count"] == 1
    assert payload["metrics"]["reviewed_vow_count"] == 1


def test_build_receipt_records_rejected_review_without_vow_write(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    record_id = _seed_tension(db)

    payload = review_runner.build_receipt(
        db_path,
        record_id=record_id,
        review_actor="operator",
        status="rejected",
        review_basis="Insufficient recurrence to justify commitment.",
    )

    assert payload["overall_ok"] is True
    assert payload["result"]["review_log_id"]
    assert payload["result"]["promoted_record_id"] is None
    assert payload["result"]["pre_review_unresolved"] is True
    assert payload["result"]["post_review_unresolved"] is False
    assert payload["metrics"]["unresolved_tension_count"] == 0
    assert payload["metrics"]["settled_tension_count"] == 1
    assert payload["metrics"]["reviewed_vow_count"] == 0


def test_main_fails_when_record_is_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_reviewed_promotion.py",
            "missing-record",
            "--db-path",
            str(db_path),
            "--review-actor",
            "operator",
            "--review-basis",
            "Missing target should fail.",
        ],
    )

    exit_code = review_runner.main()

    assert exit_code == 1
