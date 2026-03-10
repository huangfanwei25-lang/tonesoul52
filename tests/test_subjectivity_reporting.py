from __future__ import annotations

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource
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
    assert report["by_source"] == {"self_journal": 3}
    assert report["event_only_count"] == 1
    assert report["unresolved_tension_count"] == 1


def test_list_subjectivity_records_filters_unresolved_tension_and_sorts_latest_first(tmp_path) -> None:
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
    assert rows[0]["source_record_ids"] == ["stim-002"]
