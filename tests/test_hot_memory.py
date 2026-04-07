from __future__ import annotations

from tonesoul.hot_memory import (
    build_canonical_center,
    build_hot_memory_decay_map,
    build_hot_memory_ladder,
    extract_current_short_board_items,
)


def test_extract_current_short_board_items_returns_nested_bullets() -> None:
    task_text = """
# Task

## Water-Bucket Snapshot
- Current short board:
  - Phase 743: hot-memory ladder readout
  - Phase 744: observer-window misread correction
- After that:
  - rotate to next bucket
"""

    assert extract_current_short_board_items(task_text) == [
        "Phase 743: hot-memory ladder readout",
        "Phase 744: observer-window misread correction",
    ]


def test_extract_current_short_board_items_handles_missing_block() -> None:
    assert extract_current_short_board_items("# Task\n\n## Nothing here\n") == []


def test_build_canonical_center_marks_visible_short_board() -> None:
    payload = build_canonical_center(
        task_text=(
            "## Water-Bucket Snapshot\n"
            "- Current short board:\n"
            "  - Phase 743: hot-memory ladder readout\n"
            "- After that:\n"
            "  - rotate\n"
        )
    )

    assert payload["present"] is True
    assert payload["parent_surfaces"] == ["task.md", "DESIGN.md"]
    assert payload["canonical_anchor_references"] == [
        "AXIOMS.json",
        "DESIGN.md",
        "canonical architecture contracts",
        "task.md.current_short_board",
    ]
    assert payload["current_short_board"]["present"] is True
    assert payload["source_precedence_summary"].startswith("canonical_anchors >")
    assert payload["source_precedence"][0]["layer"] == "canonical_anchors"
    assert payload["current_short_board"]["items"] == ["Phase 743: hot-memory ladder readout"]
    assert "short_board_items=1" in payload["summary_text"]
    correction = payload["successor_correction"]
    assert correction["highest_risk_misread"] == "observer_stable_is_execution_permission"
    assert "confirm live_coordination first" in correction["summary_text"]
    assert "readiness.status" in correction["required_checks"]


def test_build_canonical_center_marks_missing_short_board() -> None:
    payload = build_canonical_center(task_text="")

    assert payload["current_short_board"]["present"] is False
    assert payload["current_short_board"]["status"] == "not_visible"


def test_build_hot_memory_decay_map_quarantines_contested_handoff() -> None:
    ladder = build_hot_memory_ladder(
        canonical_center=build_canonical_center(
            task_text=(
                "## Water-Bucket Snapshot\n"
                "- Current short board:\n"
                "  - Phase 745: hot-memory decay map\n"
            )
        ),
        import_posture={
            "posture": {"present": True},
            "readiness": {"present": True},
            "compactions": {
                "present": True,
                "receiver_obligation": "must_not_promote",
                "closeout_status": "partial",
            },
            "recent_traces": {"present": True},
            "subject_snapshot": {"present": True},
            "working_style": {
                "present": True,
                "working_style_observability": {"status": "reinforced"},
            },
            "council_dossier": {
                "present": True,
                "dossier_interpretation": {"calibration_status": "descriptive_only"},
            },
        },
        readiness={"status": "pass"},
        stable_count=5,
        contested_count=2,
        stale_count=0,
    )

    decay_map = build_hot_memory_decay_map(hot_memory_ladder=ladder)
    by_layer = {item["layer"]: item for item in decay_map["layers"]}

    assert by_layer["canonical_center"]["use_posture"] == "operational"
    assert by_layer["bounded_handoff"]["use_posture"] == "quarantine"
    assert by_layer["bounded_handoff"]["compression_posture"] == "compress_with_closeout_guards"
    assert by_layer["working_identity"]["use_posture"] == "review_only"
    assert "bounded_handoff" in decay_map["summary_text"]


def test_build_hot_memory_ladder_surfaces_current_pull_boundary() -> None:
    ladder = build_hot_memory_ladder(
        canonical_center=build_canonical_center(
            task_text=(
                "## Water-Bucket Snapshot\n"
                "- Current short board:\n"
                "  - Phase 789: operator retrieval contract\n"
            )
        ),
        import_posture={
            "posture": {"present": True},
            "readiness": {"present": True},
            "compactions": {
                "present": True,
                "receiver_obligation": "must_review",
                "closeout_status": "partial",
            },
            "recent_traces": {"present": True},
            "subject_snapshot": {"present": False},
            "working_style": {"present": False},
            "council_dossier": {"present": False},
        },
        readiness={"status": "pass"},
        stable_count=3,
        contested_count=1,
        stale_count=0,
    )

    boundary = ladder["current_pull_boundary"]
    assert boundary["pull_posture"] == "review_handoff_before_deeper_pull"
    assert boundary["preferred_stop_at"] == "bounded_handoff"
    assert "closeout" in boundary["operator_action"]
