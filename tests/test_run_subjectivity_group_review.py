from __future__ import annotations

from pathlib import Path

import scripts.run_subjectivity_group_review as group_review_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_reporting import list_subjectivity_records
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


def _group_key_for_topic(db: SqliteSoulDB, topic: str) -> str:
    report = build_subjectivity_tension_group_report(db, source=MemorySource.CUSTOM)
    for group in report["semantic_groups"]:
        if group["topic"] == topic:
            return str(group["group_key"])
    raise AssertionError(f"group not found for topic: {topic}")


def test_build_receipt_dry_run_selects_one_semantic_group(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
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

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "Dependency intake policy"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Cross-cycle recurrence exists, but the pattern should stay observational for now.",
        apply=False,
    )

    assert receipt["overall_ok"] is True
    assert receipt["selection"]["record_count"] == 2
    assert receipt["results"]["applied_count"] == 0
    assert receipt["results"]["receipt_count"] == 2
    assert receipt["metrics"]["unresolved_tension_count"] == 2
    assert receipt["receipts"] == [
        {"record_id": receipt["selection"]["record_ids"][0], "planned_status": "deferred"},
        {"record_id": receipt["selection"]["record_ids"][1], "planned_status": "deferred"},
    ]


def test_build_receipt_apply_rejected_settles_selected_group_only(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.26,
        source_url="https://google.github.io/osv.dev/data/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.27,
        source_url="https://google.github.io/osv.dev/data/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "OSV data sources"),
        source_name="custom",
        review_actor="operator",
        status="rejected",
        review_basis="Same-source repetition without context diversity should not become commitment weight.",
        notes="Revisit only if the same direction appears across additional source contexts.",
        apply=True,
    )

    assert receipt["overall_ok"] is True
    assert receipt["results"]["receipt_count"] == 2
    assert receipt["results"]["applied_count"] == 2
    assert receipt["results"]["promoted_count"] == 0
    assert receipt["results"]["settled_count"] == 2
    assert receipt["metrics"]["unresolved_tension_count"] == 1
    assert receipt["metrics"]["settled_tension_count"] == 2
    assert receipt["metrics"]["reviewed_vow_count"] == 0
    assert all(item["overall_ok"] for item in receipt["receipts"])
    assert all(item["post_review_unresolved"] is False for item in receipt["receipts"])


def test_build_receipt_rejects_batch_promotion_statuses(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
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

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "Dependency intake policy"),
        source_name="custom",
        review_actor="operator",
        status="approved",
        review_basis="This should be blocked at the group-review layer.",
        apply=False,
    )

    assert receipt["overall_ok"] is False
    assert receipt["results"]["receipt_count"] == 1
    assert (
        "group review only supports deferred/rejected settlement; use single-record review for vow promotion"
        in receipt["issues"]
    )


def test_build_receipt_can_filter_group_to_candidate_rows_only(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(SqliteSoulDB(db_path=db_path), "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Only the fresh candidate slice should be re-reviewed.",
        pending_status="candidate",
        apply=False,
    )

    assert receipt["overall_ok"] is True
    assert receipt["selection"]["group_record_count"] == 3
    assert receipt["selection"]["selected_record_count"] == 1
    assert receipt["selection"]["pending_status_filter"] == "candidate"
    assert receipt["selection"]["selected_pending_status_counts"] == {"candidate": 1}
    assert receipt["results"]["receipt_count"] == 1


def test_build_receipt_apply_can_defer_only_candidate_rows_inside_needs_revisit_group(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(SqliteSoulDB(db_path=db_path), "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Fresh same-source recurrence still lacks context diversity for commitment weight.",
        notes="Revisit when a second source cluster or a clearly different governance context appears.",
        pending_status="candidate",
        apply=True,
    )

    rows = list_subjectivity_records(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
        subjectivity_layer="tension",
        unresolved_only=True,
        limit=None,
    )
    homepage_rows = [row for row in rows if row["summary"].startswith("Broader governance tension")]

    assert receipt["overall_ok"] is True
    assert receipt["selection"]["group_record_count"] == 3
    assert receipt["selection"]["selected_record_count"] == 1
    assert receipt["results"]["applied_count"] == 1
    assert receipt["results"]["receipt_count"] == 1
    assert len(homepage_rows) == 3
    assert sum(1 for row in homepage_rows if row["pending_status"] == "deferred") == 3


def test_build_receipt_can_reuse_latest_matched_decision_for_candidate_only_slice(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T01:00:00Z",
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        notes="Revisit when the same direction appears outside the current source loop.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(SqliteSoulDB(db_path=db_path), "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        pending_status="candidate",
        reuse_latest_decision=True,
        apply=False,
    )

    assert receipt["overall_ok"] is True
    assert receipt["inputs"]["reuse_latest_decision"] is True
    assert receipt["resolved_decision"] == {
        "status": "deferred",
        "review_basis": "Keep observing for broader source diversity.",
        "notes": "Revisit when the same direction appears outside the current source loop.",
        "decision_source": "latest_matched_review",
    }
    assert receipt["selection"]["group_record_count"] == 3
    assert receipt["selection"]["selected_record_count"] == 1
    assert receipt["results"]["receipt_count"] == 1
    assert receipt["receipts"] == [
        {
            "record_id": receipt["selection"]["record_ids"][0],
            "planned_status": "deferred",
        }
    ]


def test_build_receipt_reuse_latest_decision_requires_prior_review_context(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Broader governance tension with multiple lineages.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T01:00:00Z",
    )

    receipt = group_review_runner.build_receipt(
        db_path,
        group_key=_group_key_for_topic(db, "OSV homepage"),
        source_name="custom",
        review_actor="operator",
        reuse_latest_decision=True,
        apply=False,
    )

    assert receipt["overall_ok"] is False
    assert (
        "reuse_latest_decision requested but the matched group had no latest review status"
        in receipt["issues"]
    )
    assert (
        "reuse_latest_decision requested but the matched group had no latest review basis"
        in receipt["issues"]
    )
