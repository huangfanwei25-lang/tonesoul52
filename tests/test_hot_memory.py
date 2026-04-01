from __future__ import annotations

from tonesoul.hot_memory import build_canonical_center, extract_current_short_board_items


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
    assert payload["current_short_board"]["present"] is True
    assert payload["current_short_board"]["items"] == ["Phase 743: hot-memory ladder readout"]
    assert "short_board_items=1" in payload["summary_text"]


def test_build_canonical_center_marks_missing_short_board() -> None:
    payload = build_canonical_center(task_text="")

    assert payload["current_short_board"]["present"] is False
    assert payload["current_short_board"]["status"] == "not_visible"
