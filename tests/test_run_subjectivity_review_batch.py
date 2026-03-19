from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import scripts.run_subjectivity_group_review as group_review_runner
import scripts.run_subjectivity_review_batch as batch_runner
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


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


def test_build_report_warns_when_db_did_not_exist(tmp_path: Path) -> None:
    db_path = tmp_path / "missing.db"

    payload, markdown = batch_runner.build_report(db_path)

    assert payload["overall_ok"] is True
    assert payload["batch"]["summary"]["review_group_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]
    assert "soul db path did not exist before review-batch run" in payload["warnings"][0]
    assert "Subjectivity Review Batch Latest" in markdown


def test_build_report_emits_review_groups_and_default_status_counts(tmp_path: Path) -> None:
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
        summary="Dream collision keeps escalating the same governance threshold.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["overall_ok"] is True
    assert payload["inputs"]["source"] == "custom"
    assert payload["batch"]["summary"]["review_group_count"] == 2
    assert payload["batch"]["summary"]["default_status_counts"] == {
        "deferred": 1,
        "rejected": 1,
    }
    assert payload["batch"]["summary"]["revisit_readiness_counts"] == {
        "n/a": 1,
        "ready_for_first_deferred_write": 1,
    }
    assert payload["batch"]["summary"]["carry_forward_annotation_counts"] == {"fresh_group": 2}
    assert payload["batch"]["summary"]["admissibility_gate_posture_counts"] == {
        "admissibility_not_yet_clear": 1,
        "insufficient_admissibility_confidence": 1,
    }
    assert "Subjectivity Review Batch Latest" in markdown
    assert "default=rejected" in markdown
    assert "default=deferred" in markdown
    assert "## Admissibility Gate Counts" in markdown
    assert "## Admissibility Status Lines" in markdown
    assert (
        "admissibility_primary_status_line: insufficient_admissibility_confidence / "
        "authority_and_exception_pressure" in markdown
    )
    assert payload["batch"]["admissibility_primary_status_line"] == (
        "insufficient_admissibility_confidence | focus=authority_and_exception_pressure | "
        "tags=exception_pressure, externalized_harm_check, low_context_diversity, single_lineage_pressure"
    )


def test_main_writes_review_batch_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_subjectivity_review_batch.py",
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--source",
            "custom",
        ],
    )

    exit_code = batch_runner.main()

    assert exit_code == 0
    json_path = out_dir / batch_runner.JSON_FILENAME
    md_path = out_dir / batch_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["batch"]["summary"]["review_group_count"] == 1


def test_script_executes_directly_via_python_path_bootstrap(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring governance tension.",
        topic="OSV homepage",
        friction_score=0.33,
        source_url="https://osv.dev/",
        stimulus_record_id="stim-c",
        dream_cycle_id="cycle-2",
        council_reason="governance threshold exceeded again",
        timestamp="2026-03-10T03:00:00Z",
    )
    out_dir = tmp_path / "status"
    script_path = Path("scripts/run_subjectivity_review_batch.py").resolve()

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--source",
            "custom",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads((out_dir / batch_runner.JSON_FILENAME).read_text(encoding="utf-8"))
    assert payload["batch"]["summary"]["review_group_count"] == 1


def test_build_report_marks_deferred_group_as_holding_until_new_rows_arrive(tmp_path: Path) -> None:
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
        notes="Revisit when the same direction appears outside the current source loop.",
        apply=True,
    )

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["revisit_readiness_counts"] == {"holding_deferred": 1}
    assert payload["batch"]["summary"]["queue_posture_counts"] == {"stable_deferred_history": 1}
    assert payload["batch"]["handoff"] == {
        "queue_shape": "stable_history_only",
        "requires_operator_action": False,
        "review_group_count": 1,
        "status_line_count": 1,
        "top_queue_posture": "stable_deferred_history",
        "primary_status_line": payload["batch"]["primary_status_line"],
    }
    assert (
        payload["batch"]["primary_status_line"]
        == "stable_deferred_history | OSV homepage | rows=2 lineages=2 cycles=2 | density=1r x2 | trigger=second_source_context_or_material_split"
    )
    assert payload["batch"]["status_lines"] == [payload["batch"]["primary_status_line"]]
    group = payload["batch"]["review_groups"][0]
    assert group["pending_status_counts"] == {"deferred": 2}
    assert group["revisit_readiness"] == "holding_deferred"
    assert group["carry_forward_annotation"] == "prior_deferred_match"
    assert group["queue_posture"] == "stable_deferred_history"
    assert group["latest_review_status"] == "deferred"
    assert group["latest_review_basis"] == "Keep observing for broader source diversity."
    assert "same-source loop; no new rows since latest review." in group["history_density_summary"]
    assert group["revisit_trigger"] == (
        "Revisit when the same direction appears outside the current source loop."
    )
    assert group["revisit_trigger_code"] == "second_source_context_or_material_split"
    assert (
        group["latest_review_notes"]
        == "Revisit when the same direction appears outside the current source loop."
    )
    assert (
        "stable deferred history; 2 row(s) compress to 2 lineage(s) / 2 cycle(s)"
        in group["operator_lens_summary"]
    )
    assert group["axiomatic_admissibility_checklist"]["focus"] == "authority_and_exception_pressure"
    assert (
        group["axiomatic_admissibility_checklist"]["gate_posture"] == "admissibility_not_yet_clear"
    )
    assert (
        group["admissibility_status_line"]
        == "admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=exception_pressure, externalized_harm_check, low_context_diversity"
    )
    assert (
        payload["batch"]["admissibility_primary_status_line"] == group["admissibility_status_line"]
    )
    assert payload["batch"]["admissibility_status_lines"] == [group["admissibility_status_line"]]
    assert "## Admissibility Focus Counts" in markdown
    assert "## Admissibility Status Lines" in markdown
    assert "## Queue Postures" in markdown
    assert "- stable_deferred_history: 1" in markdown
    assert "## Handoff" in markdown
    assert "- queue_shape: stable_history_only" in markdown
    assert "- requires_operator_action: false" in markdown
    assert "## Status Lines" in markdown
    assert (
        "- stable_deferred_history | OSV homepage | rows=2 lineages=2 cycles=2 | density=1r x2 | trigger=second_source_context_or_material_split"
        in markdown
    )
    assert "## Operator Lens" in markdown
    assert "(`stable_deferred_history`)" in markdown
    assert "latest_review_status: deferred" in markdown
    assert "carry_forward_annotation: prior_deferred_match" in markdown
    assert "queue_posture: stable_deferred_history" in markdown
    assert "revisit_readiness: holding_deferred" in markdown
    assert "revisit_trigger_code: second_source_context_or_material_split" in markdown
    assert "history_density_summary: 2 row(s) across 2 cycle(s) / 2 lineage(s)" in markdown
    assert (
        "summary: stable deferred history; 2 row(s) compress to 2 lineage(s) / 2 cycle(s)"
        in markdown
    )
    assert (
        "operator_status_line: stable_deferred_history | OSV homepage | rows=2 lineages=2 cycles=2 | density=1r x2 | trigger=second_source_context_or_material_split"
        in markdown
    )
    assert "latest_review_basis: Keep observing for broader source diversity." in markdown
    assert (
        "latest_review_notes: Revisit when the same direction appears outside the current source loop."
        in markdown
    )


def test_build_report_marks_deferred_group_with_new_rows_as_needs_revisit(
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

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["revisit_readiness_counts"] == {"needs_revisit": 1}
    assert payload["batch"]["summary"]["carry_forward_annotation_counts"] == {
        "prior_deferred_match_needs_revisit": 1
    }
    assert payload["batch"]["summary"]["queue_posture_counts"] == {"deferred_revisit_queue": 1}
    assert payload["batch"]["handoff"] == {
        "queue_shape": "action_required",
        "requires_operator_action": True,
        "review_group_count": 1,
        "status_line_count": 1,
        "top_queue_posture": "deferred_revisit_queue",
        "primary_status_line": payload["batch"]["primary_status_line"],
    }
    assert payload["batch"]["primary_status_line"] == (
        "deferred_revisit_queue | OSV homepage | rows=3 lineages=3 cycles=3 | density=1r x3 | trigger=new_rows_since_latest_review"
    )
    assert payload["batch"]["status_lines"] == [payload["batch"]["primary_status_line"]]
    group = payload["batch"]["review_groups"][0]
    assert group["pending_status_counts"] == {"deferred": 2, "candidate": 1}
    assert group["revisit_readiness"] == "needs_revisit"
    assert group["carry_forward_annotation"] == "prior_deferred_match_needs_revisit"
    assert group["queue_posture"] == "deferred_revisit_queue"
    assert "1 row(s) added since latest review." in group["history_density_summary"]
    assert group["revisit_trigger"] == "triggered_now_1_new_row(s)_since_latest_review"
    assert group["revisit_trigger_code"] == "new_rows_since_latest_review"
    assert "carry_forward_annotation: prior_deferred_match_needs_revisit" in markdown
    assert "queue_posture: deferred_revisit_queue" in markdown
    assert "revisit_readiness: needs_revisit" in markdown
    assert "history_density_summary: 3 row(s) across 3 cycle(s) / 3 lineage(s)" in markdown
    assert "revisit_trigger: triggered_now_1_new_row(s)_since_latest_review" in markdown
    assert "revisit_trigger_code: new_rows_since_latest_review" in markdown
    assert (
        "operator_status_line: deferred_revisit_queue | OSV homepage | rows=3 lineages=3 cycles=3 | density=1r x3 | trigger=new_rows_since_latest_review"
        in markdown
    )


def test_build_report_surfaces_duplicate_pressure_and_producer_followup(tmp_path: Path) -> None:
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

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["duplicate_pressure_counts"] == {"high": 1}
    assert payload["batch"]["summary"]["producer_followup_counts"] == {
        "upstream_dedup_candidate": 1
    }
    group = payload["batch"]["review_groups"][0]
    assert group["duplicate_pressure"] == "high"
    assert group["producer_followup"] == "upstream_dedup_candidate"
    assert group["lineage_record_histogram"] == {"2": 3}
    assert group["operator_followup"] == "none"
    assert group["queue_posture"] == "active_deferred_queue"
    assert group["revisit_trigger_code"] == "more_context_required"
    assert "## Duplicate Pressure Counts" in markdown
    assert "- high: 1" in markdown
    assert "## Producer Follow-Up Counts" in markdown
    assert "- upstream_dedup_candidate: 1" in markdown
    assert "duplicate_pressure: high" in markdown
    assert "producer_followup: upstream_dedup_candidate" in markdown
    assert (
        "lineage_density: repeated_lineages=3, dense_lineages=0, singleton_lineages=0, max_rows_per_lineage=2"
        in markdown
    )
    assert "lineage_record_histogram: 2=>3" in markdown


def test_build_report_surfaces_density_compaction_followup_for_holding_deferred_group(
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

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["operator_followup_counts"] == {
        "read_only_density_compaction_candidate": 1
    }
    group = payload["batch"]["review_groups"][0]
    assert group["density_compaction_candidate"] is True
    assert group["operator_followup"] == "read_only_density_compaction_candidate"
    assert "## Operator Follow-Up Counts" in markdown
    assert "- read_only_density_compaction_candidate: 1" in markdown
    assert "operator_followup: read_only_density_compaction_candidate" in markdown
    assert (
        "density_compaction_reason: 6 deferred row(s) are concentrated into 3 lineage(s)"
        in markdown
    )


def test_build_report_marks_fresh_reject_candidate_as_prior_reject_match(tmp_path: Path) -> None:
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

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["carry_forward_annotation_counts"] == {
        "prior_reject_match": 1
    }
    group = payload["batch"]["review_groups"][0]
    assert group["carry_forward_annotation"] == "prior_reject_match"
    assert group["prior_decision_status_counts"] == {"rejected": 2}
    assert "carry_forward_annotation: prior_reject_match" in markdown


def test_build_report_surfaces_latest_active_decision_separately_from_historical_history(
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

    payload, markdown = batch_runner.build_report(db_path, source_name="custom")

    assert payload["batch"]["summary"]["carry_forward_annotation_counts"] == {
        "prior_deferred_match": 1
    }
    group = payload["batch"]["review_groups"][0]
    assert group["carry_forward_annotation"] == "prior_deferred_match"
    assert group["prior_decision_status_counts"] == {"deferred": 2}
    assert group["historical_prior_decision_status_counts"] == {
        "rejected": 2,
        "deferred": 2,
    }
    assert "carry_forward_annotation: prior_deferred_match" in markdown
    assert "historical_prior_decision_status_counts: deferred=2, rejected=2" in markdown
