from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import scripts.run_subjectivity_tension_grouping as grouping_runner
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

    payload, markdown = grouping_runner.build_report(db_path)

    assert payload["overall_ok"] is True
    assert payload["grouping"]["summary"]["unresolved_row_count"] == 0
    assert payload["grouping"]["summary"]["semantic_group_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]
    assert "soul db path did not exist before grouping run" in payload["warnings"][0]
    assert "Subjectivity Tension Groups Latest" in markdown


def test_build_report_summarizes_semantic_groups_and_recommendations(tmp_path: Path) -> None:
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

    payload, markdown = grouping_runner.build_report(db_path, source_name="custom")

    assert payload["overall_ok"] is True
    assert payload["inputs"]["source"] == "custom"
    assert payload["grouping"]["summary"]["unresolved_row_count"] == 2
    assert payload["grouping"]["summary"]["semantic_group_count"] == 1
    assert payload["grouping"]["summary"]["recommendation_counts"] == {
        "candidate_for_manual_review": 1
    }
    assert payload["grouping"]["handoff"] == {
        "queue_shape": "action_required",
        "requires_operator_action": True,
        "semantic_group_count": 1,
        "status_line_count": 1,
        "top_group_shape": "manual_review_candidate",
        "primary_status_line": payload["grouping"]["primary_status_line"],
    }
    assert payload["grouping"]["status_lines"] == [payload["grouping"]["primary_status_line"]]
    group = payload["grouping"]["semantic_groups"][0]
    assert group["triage_recommendation"] == "candidate_for_manual_review"
    assert group["group_shape"] == "manual_review_candidate"
    assert group["source_urls"] == ["https://a.example/deps", "https://b.example/deps"]
    assert "## Handoff" in markdown
    assert "- queue_shape: action_required" in markdown
    assert "- requires_operator_action: true" in markdown
    assert "## Status Lines" in markdown
    assert "candidate_for_manual_review" in markdown
    assert "source_urls: https://a.example/deps, https://b.example/deps" in markdown


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

    payload, markdown = grouping_runner.build_report(db_path, source_name="custom")

    assert payload["grouping"]["summary"]["duplicate_pressure_counts"] == {"high": 1}
    assert payload["grouping"]["summary"]["producer_followup_counts"] == {
        "upstream_dedup_candidate": 1
    }
    assert payload["grouping"]["handoff"] == {
        "queue_shape": "monitoring_queue",
        "requires_operator_action": False,
        "semantic_group_count": 1,
        "status_line_count": 1,
        "top_group_shape": "high_duplicate_same_source_loop",
        "primary_status_line": payload["grouping"]["primary_status_line"],
    }
    group = payload["grouping"]["semantic_groups"][0]
    assert group["duplicate_pressure"] == "high"
    assert group["producer_followup"] == "upstream_dedup_candidate"
    assert group["group_shape"] == "high_duplicate_same_source_loop"
    assert group["repeated_lineage_count"] == 3
    assert group["dense_lineage_count"] == 0
    assert group["singleton_lineage_count"] == 0
    assert group["max_lineage_record_count"] == 2
    assert group["lineage_record_histogram"] == {"2": 3}
    assert "## Duplicate Pressure Counts" in markdown
    assert "- high: 1" in markdown
    assert "## Producer Follow-Up Counts" in markdown
    assert "- upstream_dedup_candidate: 1" in markdown
    assert (
        "- high_duplicate_same_source_loop | OSV homepage | recommendation=defer_review | rows=6 lineages=3 cycles=6 | density=2r x3 | followup=upstream_dedup_candidate"
        in markdown
    )
    assert "duplicate_pressure: high" in markdown
    assert "producer_followup: upstream_dedup_candidate" in markdown
    assert "group_shape: high_duplicate_same_source_loop" in markdown
    assert (
        "lineage_density: repeated_lineages=3, dense_lineages=0, singleton_lineages=0, max_rows_per_lineage=2"
        in markdown
    )
    assert "lineage_record_histogram: 2=>3" in markdown


def test_build_report_warns_when_topics_span_multiple_directions(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
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

    payload, markdown = grouping_runner.build_report(db_path, source_name="custom")

    assert payload["grouping"]["summary"]["multi_direction_topic_count"] == 1
    assert (
        "some topics span multiple inferred directions; verify split boundaries before review"
        in payload["warnings"]
    )
    assert "Topics With Multiple Directions" in markdown
    assert (
        "Shared intake conflict (directions=boundary_discipline, provenance_discipline)" in markdown
    )


def test_main_writes_grouping_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
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
            "run_subjectivity_tension_grouping.py",
            "--db-path",
            str(db_path),
            "--out-dir",
            str(out_dir),
            "--source",
            "custom",
        ],
    )

    exit_code = grouping_runner.main()

    assert exit_code == 0
    json_path = out_dir / grouping_runner.JSON_FILENAME
    md_path = out_dir / grouping_runner.MARKDOWN_FILENAME
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["grouping"]["summary"]["unresolved_row_count"] == 1
    assert payload["grouping"]["summary"]["semantic_group_count"] == 1
    assert payload["grouping"]["summary"]["multi_direction_topic_count"] == 0


def test_script_executes_directly_via_python_path_bootstrap(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    _append_tension(
        db,
        summary="Recurring provenance tension.",
        topic="Dependency intake policy",
        friction_score=0.41,
        source_url="https://a.example/deps",
        stimulus_record_id="stim-a",
        dream_cycle_id="cycle-1",
        council_reason="provenance checks are needed before approval",
        timestamp="2026-03-10T03:00:00Z",
    )
    out_dir = tmp_path / "status"
    script_path = Path("scripts/run_subjectivity_tension_grouping.py").resolve()

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
    payload = json.loads((out_dir / grouping_runner.JSON_FILENAME).read_text(encoding="utf-8"))
    assert payload["grouping"]["summary"]["unresolved_row_count"] == 1
