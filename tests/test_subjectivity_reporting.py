from __future__ import annotations

from tonesoul.memory.reviewed_promotion import (
    apply_reviewed_promotion,
    build_reviewed_promotion_decision,
)
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_reporting import (
    list_subjectivity_records,
    summarize_subjectivity_distribution,
)


def _build_db(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    return db, source


def test_summarize_subjectivity_distribution_counts_layers_and_statuses(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "summary": "Observed a stable preference during the session.",
            "layer": "factual",
            "subjectivity_layer": "event",
            "timestamp": "2026-03-10T01:00:00Z",
        },
    )
    db.append(
        source,
        {
            "summary": "Unresolved friction between safety and curiosity.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate", "source": "sleep_consolidate"},
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )
    db.append(
        source,
        {
            "summary": "Reviewed commitment to keep provenance explicit.",
            "layer": "factual",
            "subjectivity_layer": "vow",
            "promotion_gate": {
                "status": "reviewed",
                "reviewed_by": "operator",
                "review_basis": "Repeated conflict across reviewed cycles.",
            },
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )

    report = summarize_subjectivity_distribution(db, source=source)

    assert report["total_records"] == 3
    assert report["by_subjectivity_layer"]["event"] == 1
    assert report["by_subjectivity_layer"]["tension"] == 1
    assert report["by_subjectivity_layer"]["vow"] == 1
    assert report["by_subjectivity_layer"]["unclassified"] == 0
    assert report["by_memory_layer"] == {"factual": 2, "experiential": 1}
    assert report["by_promotion_status"] == {"none": 1, "candidate": 1, "reviewed": 1}
    assert report["unresolved_by_status"] == {"candidate": 1}
    assert report["by_source"] == {"self_journal": 3}
    assert report["event_only_count"] == 1
    assert report["unresolved_tension_count"] == 1
    assert report["deferred_tension_count"] == 0


def test_list_subjectivity_records_filters_unresolved_tension_and_sorts_latest_first(
    tmp_path,
) -> None:
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "summary": "Older unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "timestamp": "2026-03-10T01:00:00Z",
        },
    )
    db.append(
        source,
        {
            "summary": "Reviewed tension trace.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {
                "status": "reviewed",
                "reviewed_by": "operator",
                "review_basis": "Already reviewed.",
            },
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )
    db.append(
        source,
        {
            "summary": "Newer unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "source_record_ids": ["stim-002"],
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )

    rows = list_subjectivity_records(db, source=source, unresolved_only=True)

    assert [row["summary"] for row in rows] == [
        "Newer unresolved tension.",
        "Older unresolved tension.",
    ]
    assert all(row["unresolved_tension"] for row in rows)
    assert rows[0]["promotion_status"] == "candidate"
    assert rows[0]["pending_status"] == "candidate"
    assert rows[0]["source_record_ids"] == ["stim-002"]


def test_settled_reviewed_tension_is_removed_from_unresolved_queue(tmp_path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    source = MemorySource.CUSTOM
    payload = {
        "summary": "Operator-reviewed unresolved tension.",
        "layer": "experiential",
        "subjectivity_layer": "tension",
        "promotion_gate": {"status": "candidate"},
        "evidence": ["cycle-1", "cycle-2"],
        "provenance": {"source": "dream_engine"},
        "source_record_ids": ["stim-003"],
        "timestamp": "2026-03-10T04:00:00Z",
    }
    tension_record_id = db.append(source, payload)
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor="operator",
        review_basis="Repeated unresolved tension across reviewed cycles.",
        reviewed_record_id=tension_record_id,
        status="approved",
    )

    apply_reviewed_promotion(db, source=source, payload=payload, decision=decision)

    report = summarize_subjectivity_distribution(db, source=source)
    rows = list_subjectivity_records(db, source=source, subjectivity_layer="tension", limit=None)

    assert report["unresolved_tension_count"] == 0
    assert report["deferred_tension_count"] == 0
    assert report["settled_tension_count"] == 1
    assert rows[0]["record_id"] == tension_record_id
    assert rows[0]["unresolved_tension"] is False
    assert rows[0]["settled_by_review"] is True
    assert rows[0]["review_status"] == "approved"


def test_deferred_tension_is_counted_as_explicitly_deferred_but_still_unresolved(tmp_path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    source = MemorySource.CUSTOM
    db.append(
        source,
        {
            "summary": "Deferred unresolved tension.",
            "layer": "experiential",
            "subjectivity_layer": "tension",
            "promotion_gate": {
                "status": "deferred",
                "reviewed_by": "operator",
                "review_basis": "Keep watching for broader context diversity.",
            },
            "timestamp": "2026-03-10T05:00:00Z",
        },
    )

    report = summarize_subjectivity_distribution(db, source=source)

    assert report["unresolved_tension_count"] == 1
    assert report["deferred_tension_count"] == 1
    assert report["unresolved_by_status"] == {"deferred": 1}


def test_list_subjectivity_records_surfaces_deferred_review_context_from_action_log(
    tmp_path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    source = MemorySource.CUSTOM
    payload = {
        "summary": "Deferred unresolved tension with explicit revisit condition.",
        "layer": "experiential",
        "subjectivity_layer": "tension",
        "promotion_gate": {"status": "candidate"},
        "evidence": ["cycle-1", "cycle-2"],
        "provenance": {"source": "dream_engine"},
        "source_record_ids": ["stim-004"],
        "timestamp": "2026-03-10T06:00:00Z",
    }
    record_id = db.append(source, payload)
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor={"actor_id": "operator", "actor_type": "operator"},
        review_basis="Keep observing until a second source context appears.",
        reviewed_record_id=record_id,
        status="deferred",
        notes="Wake this up only when the same direction appears outside the current source loop.",
    )
    apply_reviewed_promotion(db, source=source, payload=payload, decision=decision)

    rows = list_subjectivity_records(
        db,
        source=source,
        subjectivity_layer="tension",
        unresolved_only=True,
        limit=None,
    )

    assert len(rows) == 1
    assert rows[0]["pending_status"] == "deferred"
    assert rows[0]["review_basis"] == "Keep observing until a second source context appears."
    assert (
        rows[0]["review_notes"]
        == "Wake this up only when the same direction appears outside the current source loop."
    )
    assert rows[0]["review_actor_id"] == "operator"
    assert rows[0]["review_actor_type"] == "operator"
