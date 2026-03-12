from __future__ import annotations

from tonesoul.memory.subjectivity_handoff import (
    build_handoff_surface,
    extend_handoff_markdown,
    extend_status_lines_markdown,
    normalize_status_lines,
)


def test_build_handoff_surface_normalizes_primary_status_line() -> None:
    status_lines = normalize_status_lines([" stable_history_only | topic ", "", None, "second"])

    assert status_lines == ["stable_history_only | topic", "second"]
    assert build_handoff_surface(
        queue_shape="stable_history_only",
        requires_operator_action=False,
        status_lines=status_lines,
        extra_fields={"top_queue_posture": "stable_deferred_history", "status_line_count": 2},
    ) == {
        "queue_shape": "stable_history_only",
        "requires_operator_action": False,
        "top_queue_posture": "stable_deferred_history",
        "status_line_count": 2,
        "primary_status_line": "stable_history_only | topic",
    }


def test_markdown_helpers_render_handoff_and_status_lines_sections() -> None:
    lines = ["# Example"]

    extend_handoff_markdown(
        lines,
        handoff={
            "queue_shape": "deferred_monitoring",
            "requires_operator_action": False,
            "top_unresolved_status": "deferred",
            "primary_status_line": "deferred_monitoring | records=1 unresolved=1",
        },
        extra_fields=["top_unresolved_status"],
    )
    extend_status_lines_markdown(
        lines,
        ["deferred_monitoring | records=1 unresolved=1", "", None],
    )

    assert lines == [
        "# Example",
        "",
        "## Handoff",
        "- queue_shape: deferred_monitoring",
        "- requires_operator_action: false",
        "- top_unresolved_status: deferred",
        "- primary_status_line: deferred_monitoring | records=1 unresolved=1",
        "",
        "## Status Lines",
        "- deferred_monitoring | records=1 unresolved=1",
    ]
