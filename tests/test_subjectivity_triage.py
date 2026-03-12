from __future__ import annotations

from pathlib import Path

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_triage import build_subjectivity_tension_group_report


def _append_tension(
    db: SqliteSoulDB,
    *,
    summary: str,
    topic: str,
    friction_score: float,
    source_url: str,
    stimulus_record_id: str,
    dream_cycle_id: str,
    council_reason: str,
    timestamp: str,
) -> None:
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": summary,
            "topic": topic,
            "reflection": summary,
            "layer": "working",
            "subjectivity_layer": "tension",
            "friction_score": friction_score,
            "promotion_gate": {"status": "candidate", "source": "dream_engine"},
            "source_url": source_url,
            "stimulus_record_id": stimulus_record_id,
            "source_record_ids": [stimulus_record_id],
            "dream_cycle_id": dream_cycle_id,
            "council_reason": council_reason,
            "timestamp": timestamp,
        },
    )


def test_build_subjectivity_tension_group_report_groups_by_semantics_not_single_source(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    _append_tension(
        db,
        summary="Repeated provenance tension around dependency intake.",
        topic="Dependency intake policy",
        friction_score=0.44,
        source_url="https://a.example/deps",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="provenance checks are needed before approval",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Repeated provenance tension around dependency intake.",
        topic="Dependency intake policy",
        friction_score=0.46,
        source_url="https://b.example/deps",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="provenance checks are needed before approval",
        timestamp="2026-03-10T02:00:00Z",
    )
    _append_tension(
        db,
        summary="Dream collision keeps escalating the same governance threshold.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    report = build_subjectivity_tension_group_report(db, source=MemorySource.CUSTOM)

    assert report["summary"]["unresolved_row_count"] == 3
    assert report["summary"]["semantic_group_count"] == 2
    assert report["summary"]["lineage_group_count"] == 3
    assert report["summary"]["recommendation_counts"] == {
        "candidate_for_manual_review": 1,
        "reject_review": 1,
    }
    assert report["handoff"] == {
        "queue_shape": "action_required",
        "requires_operator_action": True,
        "semantic_group_count": 2,
        "status_line_count": 2,
        "top_group_shape": "manual_review_candidate",
        "primary_status_line": report["primary_status_line"],
    }
    assert report["status_lines"] == [
        "manual_review_candidate | Dependency intake policy | recommendation=candidate_for_manual_review | rows=2 lineages=2 cycles=2 | density=1r x2",
        "same_source_loop_monitor | OSV homepage | recommendation=reject_review | rows=1 lineages=1 cycles=1 | density=1r x1",
    ]

    groups = {group["topic"]: group for group in report["semantic_groups"]}
    candidate_group = groups["Dependency intake policy"]
    assert candidate_group["direction"] == "provenance_discipline"
    assert candidate_group["source_url_count"] == 2
    assert candidate_group["lineage_count"] == 2
    assert candidate_group["cycle_count"] == 2
    assert candidate_group["triage_recommendation"] == "candidate_for_manual_review"
    assert candidate_group["group_shape"] == "manual_review_candidate"
    assert candidate_group["source_urls"] == ["https://a.example/deps", "https://b.example/deps"]

    reject_group = groups["OSV homepage"]
    assert reject_group["direction"] == "governance_escalation"
    assert reject_group["source_url_count"] == 1
    assert reject_group["lineage_count"] == 1
    assert reject_group["triage_recommendation"] == "reject_review"
    assert reject_group["group_shape"] == "same_source_loop_monitor"


def test_build_subjectivity_tension_group_report_returns_empty_summary_without_unresolved_rows(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Reviewed vow already settled.",
            "layer": "factual",
            "subjectivity_layer": "vow",
            "promotion_gate": {"status": "approved"},
            "timestamp": "2026-03-10T04:00:00Z",
        },
    )

    report = build_subjectivity_tension_group_report(db, source=MemorySource.CUSTOM)

    assert report == {
        "summary": {
            "unresolved_row_count": 0,
            "semantic_group_count": 0,
            "lineage_group_count": 0,
            "multi_direction_topic_count": 0,
        },
        "handoff": {
            "queue_shape": "empty_queue",
            "requires_operator_action": False,
            "semantic_group_count": 0,
            "status_line_count": 0,
            "top_group_shape": "",
            "primary_status_line": "",
        },
        "primary_status_line": "",
        "status_lines": [],
        "semantic_groups": [],
        "lineage_groups": [],
        "multi_direction_topics": [],
    }


def test_build_subjectivity_tension_group_report_surfaces_topics_with_multiple_directions(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    _append_tension(
        db,
        summary="Need stronger provenance audit before accepting this source.",
        topic="Shared intake conflict",
        friction_score=0.42,
        source_url="https://a.example/source",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="audit trail is incomplete",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Need a firmer boundary before accepting this source.",
        topic="Shared intake conflict",
        friction_score=0.43,
        source_url="https://b.example/source",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="boundary discipline is unclear",
        timestamp="2026-03-10T02:00:00Z",
    )

    report = build_subjectivity_tension_group_report(db, source=MemorySource.CUSTOM)

    assert report["summary"]["semantic_group_count"] == 2
    assert report["summary"]["multi_direction_topic_count"] == 1
    assert report["multi_direction_topics"] == [
        {
            "topic": "Shared intake conflict",
            "directions": ["boundary_discipline", "provenance_discipline"],
            "direction_count": 2,
        }
    ]
