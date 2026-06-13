"""Lock every council perspective to a clean operator-facing label in stance text.

Bug (found 2026-06-13 while building examples/demo_declare_stance.py): a
DECLARE_STANCE verdict whose objections included the Axiomatic perspective
rendered the raw enum repr "PerspectiveType.AXIOMATIC" in the
operator-facing stance declaration — PERSPECTIVE_LABELS was missing the
"axiomatic" key and the fallback was str(value). Every OTHER perspective had
a friendly label, so the leak was easy to miss.

These tests pin the fix: no perspective may leak a "PerspectiveType." repr
into stance text, and all five carry an explicit friendly label.
"""

from __future__ import annotations

from tonesoul.council.summary_generator import (
    PERSPECTIVE_LABELS,
    _perspective_label,
    build_divergence_analysis,
    format_stance_declaration,
)
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


def _vote(perspective, decision, confidence, reasoning):
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=[],
        requires_grounding=False,
        grounding_status="n/a",
        evidence_chain=[],
    )


def test_all_perspectives_have_a_label():
    for p in PerspectiveType:
        assert p.value in PERSPECTIVE_LABELS, (
            f"PerspectiveType.{p.name} has no entry in PERSPECTIVE_LABELS — "
            "its stance text will leak the raw enum repr to operators."
        )


def test_label_never_leaks_raw_enum_repr():
    for p in PerspectiveType:
        label = _perspective_label(p)
        assert "PerspectiveType" not in label, f"{p.name} label leaked enum repr: {label!r}"


def test_axiomatic_renders_friendly_in_stance_declaration():
    # The exact split from the demo: a genuine divergence, no safety veto,
    # with the Axiomatic perspective objecting.
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.80, "No safety red line."),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.90, "Data favors A."),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.85, "Breaks continuity."),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.80, "Operator needs a hedge."),
        _vote(PerspectiveType.AXIOMATIC, VoteDecision.OBJECT, 0.80, "Violates L1 commitment."),
    ]
    stance = format_stance_declaration(build_divergence_analysis(votes))
    assert "PerspectiveType.AXIOMATIC" not in stance, f"raw enum leaked into stance:\n{stance}"
    assert "Axiomatic Guard" in stance, f"expected friendly Axiomatic label in stance:\n{stance}"
