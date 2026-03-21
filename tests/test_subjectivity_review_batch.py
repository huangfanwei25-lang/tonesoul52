from __future__ import annotations

from pathlib import Path

import scripts.run_reviewed_promotion as review_runner
import scripts.run_subjectivity_group_review as group_review_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_review_batch import build_subjectivity_review_batch_report


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


def test_build_subjectivity_review_batch_report_maps_triage_to_operator_defaults(
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

    report = build_subjectivity_review_batch_report(db, source=MemorySource.CUSTOM)

    assert report["summary"]["review_group_count"] == 2
    assert report["summary"]["default_status_counts"] == {
        "manual_review_required": 1,
        "rejected": 1,
    }
    groups = {group["topic"]: group for group in report["review_groups"]}
    candidate_group = groups["Dependency intake policy"]
    assert candidate_group["default_review_status_if_confirmed"] == "manual_review_required"
    assert candidate_group["carry_forward_annotation"] == "fresh_group"
    assert len(candidate_group["representative_record_ids"]) == 2
    assert (
        "confirm admissibility under existing P0/P1 constraints"
        in candidate_group["review_basis_template"]
    )
    assert candidate_group["axiomatic_admissibility_checklist"]["required_for_approved"] is True
    assert (
        candidate_group["axiomatic_admissibility_checklist"]["gate_posture"]
        == "manual_review_candidate"
    )
    assert (
        candidate_group["admissibility_status_line"]
        == "manual_review_candidate | focus=traceability_and_accountability | tags=accountability_check, traceability_not_enough"
    )
    assert (
        "P0/P1 constraints"
        in candidate_group["axiomatic_admissibility_checklist"]["operator_prompt"]
    )

    reject_group = groups["OSV homepage"]
    assert reject_group["default_review_status_if_confirmed"] == "rejected"
    assert reject_group["carry_forward_annotation"] == "fresh_group"
    assert len(reject_group["representative_record_ids"]) == 1
    assert (
        "context diversity or axiomatic confidence to justify commitment"
        in reject_group["review_basis_template"]
    )
    assert (
        reject_group["axiomatic_admissibility_checklist"]["gate_posture"]
        == "insufficient_admissibility_confidence"
    )
    assert "exception_pressure" in reject_group["axiomatic_admissibility_checklist"]["risk_tags"]
    assert (
        reject_group["admissibility_status_line"]
        == "insufficient_admissibility_confidence | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure"
    )
    assert report["summary"]["admissibility_gate_posture_counts"] == {
        "insufficient_admissibility_confidence": 1,
        "manual_review_candidate": 1,
    }
    assert (
        report["admissibility_primary_status_line"] == candidate_group["admissibility_status_line"]
    )
    assert report["admissibility_status_lines"] == [
        candidate_group["admissibility_status_line"],
        reject_group["admissibility_status_line"],
    ]


def test_build_subjectivity_review_batch_report_returns_empty_queue_when_no_unresolved_rows(
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

    report = build_subjectivity_review_batch_report(db, source=MemorySource.CUSTOM)

    assert report["summary"]["review_group_count"] == 0
    assert report["summary"]["unresolved_row_count"] == 0
    assert report["review_groups"] == []


def test_build_subjectivity_review_batch_report_marks_deferred_groups_as_holding_until_new_rows_arrive(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring governance tension.",
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
        summary="Recurring governance tension.",
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
        topic="OSV homepage",
        direction="governance_escalation",
        friction_band="medium",
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        apply=True,
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["default_review_status_if_confirmed"] == "deferred"
    assert group["pending_status_counts"] == {"deferred": 2}
    assert group["rows_after_latest_review"] == 0
    assert group["revisit_readiness"] == "holding_deferred"
    assert group["carry_forward_annotation"] == "prior_deferred_match"
    assert group["queue_posture"] == "stable_deferred_history"
    assert group["revisit_trigger"] == (
        "Revisit when the same direction appears outside the current source loop, "
        "or when the group materially splits."
    )
    assert group["revisit_trigger_code"] == "second_source_context_or_material_split"
    assert group["prior_decision_status_counts"] == {"deferred": 2}
    assert group["first_seen"] == "2026-03-10T01:00:00Z"
    assert group["last_seen"] == "2026-03-10T02:00:00Z"
    assert "same-source loop; no new rows since latest review." in group["history_density_summary"]
    assert (
        "stable deferred history; 2 row(s) compress to 2 lineage(s) / 2 cycle(s)"
        in group["operator_lens_summary"]
    )
    assert (
        group["operator_status_line"]
        == "stable_deferred_history | OSV homepage | rows=2 lineages=2 cycles=2 | density=1r x2 | trigger=second_source_context_or_material_split"
    )
    assert (
        report["primary_status_line"]
        == "stable_deferred_history | OSV homepage | rows=2 lineages=2 cycles=2 | density=1r x2 | trigger=second_source_context_or_material_split"
    )
    assert report["status_lines"] == [report["primary_status_line"]]
    assert group["latest_review_timestamp"]
    assert group["latest_review_status"] == "deferred"
    assert report["summary"]["revisit_readiness_counts"] == {"holding_deferred": 1}
    assert report["summary"]["carry_forward_annotation_counts"] == {"prior_deferred_match": 1}
    assert report["summary"]["queue_posture_counts"] == {"stable_deferred_history": 1}
    assert report["handoff"] == {
        "queue_shape": "stable_history_only",
        "requires_operator_action": False,
        "review_group_count": 1,
        "status_line_count": 1,
        "top_queue_posture": "stable_deferred_history",
        "primary_status_line": report["primary_status_line"],
    }


def test_build_subjectivity_review_batch_report_marks_deferred_group_with_new_rows_as_needs_revisit(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring governance tension.",
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
        summary="Recurring governance tension.",
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
        topic="OSV homepage",
        direction="governance_escalation",
        friction_band="medium",
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2099-03-10T03:00:00Z",
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["default_review_status_if_confirmed"] == "deferred"
    assert group["pending_status_counts"] == {"deferred": 2, "candidate": 1}
    assert group["rows_after_latest_review"] == 1
    assert group["revisit_readiness"] == "needs_revisit"
    assert group["carry_forward_annotation"] == "prior_deferred_match_needs_revisit"
    assert group["queue_posture"] == "deferred_revisit_queue"
    assert group["revisit_trigger"] == "triggered_now_1_new_row(s)_since_latest_review"
    assert group["revisit_trigger_code"] == "new_rows_since_latest_review"
    assert group["prior_decision_status_counts"] == {"deferred": 2}
    assert "1 row(s) added since latest review." in group["history_density_summary"]
    assert "deferred queue that has reopened for revisit" in group["operator_lens_summary"]
    assert (
        group["operator_status_line"]
        == "deferred_revisit_queue | OSV homepage | rows=3 lineages=3 cycles=3 | density=1r x3 | trigger=new_rows_since_latest_review"
    )
    assert report["primary_status_line"] == group["operator_status_line"]
    assert report["status_lines"] == [group["operator_status_line"]]
    assert group["latest_matched_review_timestamp"]
    assert report["summary"]["revisit_readiness_counts"] == {"needs_revisit": 1}
    assert report["summary"]["carry_forward_annotation_counts"] == {
        "prior_deferred_match_needs_revisit": 1
    }
    assert report["summary"]["queue_posture_counts"] == {"deferred_revisit_queue": 1}
    assert report["handoff"] == {
        "queue_shape": "action_required",
        "requires_operator_action": True,
        "review_group_count": 1,
        "status_line_count": 1,
        "top_queue_posture": "deferred_revisit_queue",
        "primary_status_line": report["primary_status_line"],
    }


def test_build_subjectivity_review_batch_report_surfaces_high_duplicate_pressure_for_single_source_loop(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    for index, stimulus_record_id in enumerate(("stim-a", "stim-b", "stim-c"), start=1):
        for cycle in range(2):
            _append_tension(
                db,
                summary="Recurring governance tension from one source loop.",
                topic="OSV homepage",
                friction_score=0.34,
                source_url="https://osv.dev/",
                stimulus_record_id=stimulus_record_id,
                dream_cycle_id=f"cycle-{index}-{cycle}",
                council_reason="governance threshold exceeded again",
                timestamp=f"2026-03-10T0{index}:0{cycle}:00Z",
            )

    report = build_subjectivity_review_batch_report(db, source=MemorySource.CUSTOM)

    assert report["summary"]["duplicate_pressure_counts"] == {"high": 1}
    assert report["summary"]["producer_followup_counts"] == {"upstream_dedup_candidate": 1}
    group = report["review_groups"][0]
    assert group["duplicate_pressure"] == "high"
    assert group["producer_followup"] == "upstream_dedup_candidate"
    assert group["same_source_loop"] is True
    assert group["rows_per_lineage"] == 2.0
    assert group["rows_per_cycle"] == 1.0
    assert group["repeated_lineage_count"] == 3
    assert group["dense_lineage_count"] == 0
    assert group["singleton_lineage_count"] == 0
    assert group["max_lineage_record_count"] == 2
    assert group["lineage_record_histogram"] == {"2": 3}
    assert group["density_compaction_candidate"] is False
    assert group["operator_followup"] == "none"
    assert group["queue_posture"] == "active_deferred_queue"
    assert group["revisit_trigger_code"] == "more_context_required"
    assert "reopening the queue" in group["duplicate_pressure_reason"]


def test_build_subjectivity_review_batch_report_marks_holding_deferred_high_pressure_group_as_density_compaction_candidate(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    for index, stimulus_record_id in enumerate(("stim-a", "stim-b", "stim-c"), start=1):
        for cycle in range(2):
            _append_tension(
                db,
                summary="Recurring governance tension from one source loop.",
                topic="OSV homepage",
                friction_score=0.34,
                source_url="https://osv.dev/",
                stimulus_record_id=stimulus_record_id,
                dream_cycle_id=f"cycle-{index}-{cycle}",
                council_reason="governance threshold exceeded again",
                timestamp=f"2026-03-10T0{index}:0{cycle}:00Z",
            )
    group_review_runner.build_receipt(
        db_path,
        topic="OSV homepage",
        direction="governance_escalation",
        friction_band="medium",
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Keep observing for broader source diversity.",
        notes="Queue is settled for now; use density compaction to monitor the loop.",
        apply=True,
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["revisit_readiness"] == "holding_deferred"
    assert group["carry_forward_annotation"] == "prior_deferred_match"
    assert group["lineage_record_histogram"] == {"2": 3}
    assert group["density_compaction_candidate"] is True
    assert group["operator_followup"] == "read_only_density_compaction_candidate"
    assert (
        "6 deferred row(s) are concentrated into 3 lineage(s)" in group["density_compaction_reason"]
    )
    assert report["summary"]["operator_followup_counts"] == {
        "read_only_density_compaction_candidate": 1
    }


def test_build_subjectivity_review_batch_report_marks_fresh_reject_candidate_as_prior_reject_match(
    tmp_path: Path,
) -> None:
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
    group_review_runner.build_receipt(
        db_path,
        topic="OSV data sources",
        direction="governance_escalation",
        friction_band="low",
        source_name="custom",
        review_actor="operator",
        status="rejected",
        review_basis="Same-source repetition without context diversity should not become commitment weight.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.26,
        source_url="https://google.github.io/osv.dev/data/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["default_review_status_if_confirmed"] == "rejected"
    assert group["pending_status_counts"] == {"candidate": 1}
    assert group["carry_forward_annotation"] == "prior_reject_match"
    assert group["prior_decision_status_counts"] == {"rejected": 2}
    assert report["summary"]["carry_forward_annotation_counts"] == {"prior_reject_match": 1}


def test_build_subjectivity_review_batch_report_does_not_match_prior_rows_when_provenance_is_missing(
    tmp_path: Path,
) -> None:
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
    group_review_runner.build_receipt(
        db_path,
        topic="OSV data sources",
        direction="governance_escalation",
        friction_band="low",
        source_name="custom",
        review_actor="operator",
        status="rejected",
        review_basis="Same-source repetition without context diversity should not become commitment weight.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.26,
        source_url="",
        stimulus_record_id="stim-z",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["carry_forward_annotation"] == "fresh_group"
    assert group["prior_decision_status_counts"] == {}
    assert group["historical_prior_decision_status_counts"] == {}


def test_build_subjectivity_review_batch_report_keeps_prior_reject_match_across_friction_band_boundary(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.29,
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
        friction_score=0.29,
        source_url="https://google.github.io/osv.dev/data/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        topic="OSV data sources",
        direction="governance_escalation",
        friction_band="low",
        source_name="custom",
        review_actor="operator",
        status="rejected",
        review_basis="Same-source repetition without context diversity should not become commitment weight.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Repeated same-source governance tension around one page.",
        topic="OSV data sources",
        friction_score=0.30,
        source_url="https://google.github.io/osv.dev/data/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["friction_band"] == "medium"
    assert group["carry_forward_annotation"] == "prior_reject_match"
    assert group["prior_decision_status_counts"] == {"rejected": 2}


def test_build_subjectivity_review_batch_report_prefers_latest_active_decision_over_older_history(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring governance tension.",
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
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T02:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        topic="OSV homepage",
        direction="governance_escalation",
        friction_band="medium",
        source_name="custom",
        review_actor="operator",
        status="rejected",
        review_basis="Same-source repetition should stay visible without becoming commitment.",
        apply=True,
    )
    _append_tension(
        db,
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-3",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )
    _append_tension(
        db,
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.34,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-4",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T04:00:00Z",
    )
    group_review_runner.build_receipt(
        db_path,
        topic="OSV homepage",
        direction="governance_escalation",
        friction_band="medium",
        source_name="custom",
        review_actor="operator",
        status="deferred",
        review_basis="Broader source diversity is appearing, but commitment is still premature.",
        apply=True,
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["carry_forward_annotation"] == "prior_deferred_match"
    assert group["prior_decision_status_counts"] == {"deferred": 2}
    assert group["historical_prior_decision_status_counts"] == {
        "rejected": 2,
        "deferred": 2,
    }


def test_build_subjectivity_review_batch_report_marks_prior_approved_match(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    record_id = db.append(
        MemorySource.CUSTOM,
        {
            "summary": "Repeated provenance tension around dependency intake.",
            "topic": "Dependency intake policy",
            "reflection": "Repeated provenance tension around dependency intake.",
            "layer": "working",
            "subjectivity_layer": "tension",
            "friction_score": 0.44,
            "promotion_gate": {"status": "candidate", "source": "dream_engine"},
            "evidence": ["cycle-1", "cycle-2"],
            "provenance": {"source": "dream_engine"},
            "source_url": "https://a.example/deps",
            "stimulus_record_id": "stim-a",
            "source_record_ids": ["stim-a"],
            "dream_cycle_id": "cycle-1",
            "council_reason": "provenance checks are needed before approval",
            "timestamp": "2026-03-10T01:00:00Z",
        },
    )
    review_runner.build_receipt(
        db_path,
        record_id=record_id,
        source_name="custom",
        review_actor="operator",
        status="approved",
        review_basis="Repeated provenance tension has matured into an explicit commitment.",
    )
    _append_tension(
        db,
        summary="Repeated provenance tension around dependency intake.",
        topic="Dependency intake policy",
        friction_score=0.44,
        source_url="https://a.example/deps",
        stimulus_record_id="stim-b",
        dream_cycle_id="cycle-2",
        council_reason="provenance checks are needed before approval",
        timestamp="2026-03-10T02:00:00Z",
    )

    report = build_subjectivity_review_batch_report(
        SqliteSoulDB(db_path=db_path),
        source=MemorySource.CUSTOM,
    )

    group = report["review_groups"][0]
    assert group["carry_forward_annotation"] == "prior_approved_match"
    assert group["prior_decision_status_counts"] == {"approved": 1}
