from __future__ import annotations

from tonesoul.memory.subjectivity_handoff import (
    build_handoff_surface,
    extend_handoff_markdown,
    extend_status_lines_markdown,
    normalize_status_lines,
    primary_status_line,
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


# ── normalize_status_lines ────────────────────────────────────────────────────

def test_normalize_status_lines_rejects_non_iterables() -> None:
    assert normalize_status_lines("a string") == []
    assert normalize_status_lines(b"bytes") == []
    assert normalize_status_lines({"key": "val"}) == []
    assert normalize_status_lines(42) == []  # type: ignore[arg-type]


def test_normalize_status_lines_filters_blank_entries() -> None:
    result = normalize_status_lines(["keep", "", "  ", None, "also keep"])
    assert result == ["keep", "also keep"]


def test_normalize_status_lines_from_generator() -> None:
    result = normalize_status_lines(x for x in ["alpha", "beta"])
    assert result == ["alpha", "beta"]


# ── primary_status_line ───────────────────────────────────────────────────────

def test_primary_status_line_returns_empty_for_empty_input() -> None:
    assert primary_status_line([]) == ""
    assert primary_status_line("not a list") == ""


def test_primary_status_line_returns_first_non_blank() -> None:
    assert primary_status_line(["  ", "first", "second"]) == "first"


# ── build_handoff_surface ─────────────────────────────────────────────────────

def test_build_handoff_surface_without_extra_fields() -> None:
    result = build_handoff_surface(
        queue_shape="active",
        requires_operator_action=True,
        status_lines=["active | urgent"],
    )
    assert result["queue_shape"] == "active"
    assert result["requires_operator_action"] is True
    assert result["primary_status_line"] == "active | urgent"
    assert len(result) == 3


def test_build_handoff_surface_ignores_non_mapping_extra_fields() -> None:
    result = build_handoff_surface(
        queue_shape="idle",
        requires_operator_action=False,
        status_lines=[],
        extra_fields=["not", "a", "mapping"],  # type: ignore[arg-type]
    )
    assert "primary_status_line" in result
    assert result["primary_status_line"] == ""


# ── extend_handoff_markdown ───────────────────────────────────────────────────

def test_extend_handoff_markdown_skips_non_mapping_handoff() -> None:
    lines: list[str] = ["before"]
    extend_handoff_markdown(lines, handoff=None)
    extend_handoff_markdown(lines, handoff={})
    assert lines == ["before"]


def test_extend_handoff_markdown_without_extra_fields() -> None:
    lines: list[str] = []
    extend_handoff_markdown(
        lines,
        handoff={"queue_shape": "q", "requires_operator_action": False, "primary_status_line": "x"},
    )
    rendered = "\n".join(lines)
    assert "queue_shape: q" in rendered
    assert "primary_status_line: x" in rendered


# ── extend_status_lines_markdown ──────────────────────────────────────────────

def test_extend_status_lines_markdown_renders_none_when_empty() -> None:
    lines: list[str] = []
    extend_status_lines_markdown(lines, [])
    assert "- None" in lines


def test_extend_status_lines_markdown_renders_all_items() -> None:
    lines: list[str] = []
    extend_status_lines_markdown(lines, ["line one", "line two"])
    assert "- line one" in lines
    assert "- line two" in lines
