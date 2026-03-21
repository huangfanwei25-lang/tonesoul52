from __future__ import annotations

from datetime import datetime

from tonesoul.tonebridge.rupture_detector import (
    RuptureDetector,
    RuptureSeverity,
    SemanticRupture,
)
from tonesoul.tonebridge.self_commit import AssertionType, SelfCommit, SelfCommitStack


def _commit(
    content: str,
    *,
    weight: float = 0.8,
    commit_id: str = "commit-1",
) -> SelfCommit:
    return SelfCommit(
        id=commit_id,
        timestamp=datetime.now(),
        assertion_type=AssertionType.BOUNDARY_SETTING,
        content=content,
        irreversible_weight=weight,
        context_hash="ctx",
    )


def test_semantic_rupture_to_dict_preserves_core_fields() -> None:
    rupture = SemanticRupture(
        id="r1",
        timestamp=datetime.now(),
        violated_commit=_commit("protect users"),
        new_statement="deny users",
        severity=RuptureSeverity.CRITICAL,
        contradiction_type="direct_negation",
        explanation="conflict",
        acknowledged=True,
        correction_reason="manual override",
    )

    payload = rupture.to_dict()

    assert payload["id"] == "r1"
    assert payload["violated_commit_id"] == "commit-1"
    assert payload["severity"] == "critical"
    assert payload["acknowledged"] is True
    assert payload["correction_reason"] == "manual override"


def test_extract_key_concepts_filters_short_tokens() -> None:
    detector = RuptureDetector()

    concepts = detector._extract_key_concepts("a alpha beta c")

    assert concepts == ["alpha", "beta"]


def test_check_direct_negation_detects_overlap_with_monkeypatched_pairs(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "NEGATION_PAIRS", [("allow", "deny")])
    commit = _commit("allow user uploads")

    result = detector._check_direct_negation(commit, "we deny user uploads now")

    assert result is not None
    assert result[0] == "direct_negation"
    assert "allow" in result[1]
    assert "deny" in result[1]


def test_check_direct_negation_returns_none_without_concept_overlap(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "NEGATION_PAIRS", [("allow", "deny")])
    commit = _commit("allow apples")

    assert detector._check_direct_negation(commit, "we deny oranges now") is None


def test_check_retraction_uses_marker_list(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "RETRACTION_MARKERS", ["I retract"])

    result = detector._check_retraction("I retract that statement.")

    assert result is not None
    assert result[0] == "retraction"
    assert "I retract" in result[1]


def test_check_softening_requires_high_weight_and_marker(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "SOFTENING_MARKERS", ["maybe"])

    high_weight = _commit("protect users", weight=0.8)
    low_weight = _commit("protect users", weight=0.5)

    assert detector._check_softening(high_weight, "maybe protect users later") is not None
    assert detector._check_softening(low_weight, "maybe protect users later") is None


def test_calculate_severity_respects_weight_and_type() -> None:
    detector = RuptureDetector()

    assert (
        detector._calculate_severity(_commit("x", weight=0.9), "direct_negation")
        is RuptureSeverity.CRITICAL
    )
    assert (
        detector._calculate_severity(_commit("x", weight=0.6), "direct_negation")
        is RuptureSeverity.SIGNIFICANT
    )
    assert (
        detector._calculate_severity(_commit("x", weight=0.4), "retraction")
        is RuptureSeverity.MINOR
    )
    assert (
        detector._calculate_severity(_commit("x", weight=0.9), "softening") is RuptureSeverity.MINOR
    )


def test_detect_collects_direct_negation_rupture(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "NEGATION_PAIRS", [("allow", "deny")])
    stack = SelfCommitStack()
    stack.push(_commit("allow user uploads", weight=0.9))

    ruptures = detector.detect("we deny user uploads", stack)

    assert len(ruptures) == 1
    assert ruptures[0].contradiction_type == "direct_negation"
    assert ruptures[0].severity is RuptureSeverity.CRITICAL


def test_detect_uses_retraction_when_no_other_rupture(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "RETRACTION_MARKERS", ["I retract"])
    stack = SelfCommitStack()
    stack.push(_commit("protect users", weight=0.8, commit_id="recent"))

    ruptures = detector.detect("I retract the earlier answer.", stack)

    assert len(ruptures) == 1
    assert ruptures[0].contradiction_type == "retraction"
    assert ruptures[0].violated_commit.id == "recent"
    assert ruptures[0].severity is RuptureSeverity.SIGNIFICANT


def test_detect_ignores_low_weight_commits(monkeypatch) -> None:
    detector = RuptureDetector()
    monkeypatch.setattr(detector, "NEGATION_PAIRS", [("allow", "deny")])
    stack = SelfCommitStack()
    stack.push(_commit("allow user uploads", weight=0.3))

    assert detector.detect("we deny user uploads", stack) == []


def test_format_rupture_warning_contains_commit_and_type() -> None:
    rupture = SemanticRupture(
        id="r1",
        timestamp=datetime.now(),
        violated_commit=_commit("protect users"),
        new_statement="deny users",
        severity=RuptureSeverity.SIGNIFICANT,
        contradiction_type="direct_negation",
        explanation="conflict",
    )

    warning = RuptureDetector().format_rupture_warning([rupture])

    assert "direct_negation" in warning
    assert "protect users" in warning
    assert "conflict" in warning
