from __future__ import annotations

from tonesoul.status_alignment import (
    _coerce_text,
    _route_family,
    _secondary_labels,
    build_dream_weekly_alignment_line,
)


def test_coerce_text_returns_empty_for_none() -> None:
    assert _coerce_text(None) == ""


def test_coerce_text_trims_whitespace() -> None:
    assert _coerce_text("  family=F1  ") == "family=F1"


def test_route_family_extracts_family_token() -> None:
    status_line = "route | family=F6_semantic_role_boundary_integrity repair=guardrail"

    assert _route_family(status_line) == "F6_semantic_role_boundary_integrity"


def test_route_family_returns_empty_without_family() -> None:
    assert _route_family("route | repair=guardrail") == ""


def test_secondary_labels_splits_and_filters_empty_items() -> None:
    labels = _secondary_labels(
        " F4_execution_contract_integrity, ,F6_semantic_role_boundary_integrity ,,"
    )

    assert labels == [
        "F4_execution_contract_integrity",
        "F6_semantic_role_boundary_integrity",
    ]


def test_alignment_returns_empty_for_non_mapping_inputs() -> None:
    assert build_dream_weekly_alignment_line(None, {}) == ""
    assert build_dream_weekly_alignment_line({}, None) == ""


def test_alignment_returns_empty_when_both_families_missing() -> None:
    assert build_dream_weekly_alignment_line({}, {}) == ""


def test_alignment_marks_aligned_and_preserves_shared_secondary() -> None:
    weekly_preview = {
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity repair=anchor_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
    }
    dream_preview = {
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity repair=anchor_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F4_execution_contract_integrity,F7_representation_localization_integrity,"
            "F6_semantic_role_boundary_integrity"
        ),
    }

    assert (
        build_dream_weekly_alignment_line(weekly_preview, dream_preview)
        == "dream_weekly_alignment | alignment=aligned "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F1_grounding_evidence_integrity "
        "shared_secondary=F4_execution_contract_integrity,F6_semantic_role_boundary_integrity"
    )


def test_alignment_marks_diverged_for_different_families() -> None:
    weekly_preview = {"problem_route_status_line": "route | family=F1_grounding_evidence_integrity"}
    dream_preview = {
        "problem_route_status_line": "route | family=F6_semantic_role_boundary_integrity"
    }

    assert (
        build_dream_weekly_alignment_line(weekly_preview, dream_preview)
        == "dream_weekly_alignment | alignment=diverged "
        "weekly=F1_grounding_evidence_integrity "
        "dream=F6_semantic_role_boundary_integrity"
    )


def test_alignment_marks_partial_when_only_weekly_has_family() -> None:
    weekly_preview = {"problem_route_status_line": "route | family=F4_execution_contract_integrity"}

    assert (
        build_dream_weekly_alignment_line(weekly_preview, {})
        == "dream_weekly_alignment | alignment=partial weekly=F4_execution_contract_integrity"
    )


def test_alignment_marks_partial_when_only_dream_has_family() -> None:
    dream_preview = {
        "problem_route_status_line": "route | family=F7_representation_localization_integrity"
    }

    assert (
        build_dream_weekly_alignment_line({}, dream_preview)
        == "dream_weekly_alignment | alignment=partial "
        "dream=F7_representation_localization_integrity"
    )


def test_alignment_ignores_non_overlapping_secondary_labels() -> None:
    weekly_preview = {
        "problem_route_status_line": "route | family=F4_execution_contract_integrity",
        "problem_route_secondary_labels": "F1_grounding_evidence_integrity",
    }
    dream_preview = {
        "problem_route_status_line": "route | family=F4_execution_contract_integrity",
        "problem_route_secondary_labels": "F7_representation_localization_integrity",
    }

    assert (
        build_dream_weekly_alignment_line(weekly_preview, dream_preview)
        == "dream_weekly_alignment | alignment=aligned "
        "weekly=F4_execution_contract_integrity "
        "dream=F4_execution_contract_integrity"
    )
