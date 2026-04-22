"""Tests for tonesoul.council.types — shared council dataclasses and enums."""

from __future__ import annotations

import pytest

from tonesoul.council.types import (
    UNGROUNDED_CONFIDENCE_CAP,
    CoherenceScore,
    CouncilVerdict,
    GroundingStatus,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


class TestEnums:
    def test_perspective_type_values(self):
        assert PerspectiveType.GUARDIAN.value == "guardian"
        assert PerspectiveType.ANALYST.value == "analyst"
        assert PerspectiveType.CRITIC.value == "critic"
        assert PerspectiveType.ADVOCATE.value == "advocate"
        assert PerspectiveType.AXIOMATIC.value == "axiomatic"

    def test_vote_decision_values(self):
        assert VoteDecision.APPROVE.value == "approve"
        assert VoteDecision.CONCERN.value == "concern"
        assert VoteDecision.OBJECT.value == "object"
        assert VoteDecision.ABSTAIN.value == "abstain"

    def test_verdict_type_values(self):
        assert VerdictType.APPROVE.value == "approve"
        assert VerdictType.BLOCK.value == "block"
        assert VerdictType.REFINE.value == "refine"

    def test_grounding_status_values(self):
        assert GroundingStatus.GROUNDED.value == "grounded"
        assert GroundingStatus.UNGROUNDED.value == "ungrounded"
        assert GroundingStatus.PARTIAL.value == "partial"

    def test_ungrounded_confidence_cap_is_below_one(self):
        assert 0.0 < UNGROUNDED_CONFIDENCE_CAP < 1.0


class TestCoherenceScore:
    def test_overall_without_strong_objection_uses_weighted_formula(self):
        cs = CoherenceScore(
            c_inter=0.8,
            approval_rate=0.6,
            min_confidence=0.7,
            has_strong_objection=False,
        )
        expected = 0.8 * 0.4 + 0.6 * 0.4 + 0.7 * 0.2
        assert abs(cs.overall - expected) < 0.001

    def test_strong_objection_caps_overall_at_point_three(self):
        cs = CoherenceScore(
            c_inter=0.9,
            approval_rate=0.9,
            min_confidence=0.9,
            has_strong_objection=True,
        )
        assert cs.overall == min(0.9, 0.3)

    def test_strong_objection_with_low_c_inter_returns_c_inter(self):
        cs = CoherenceScore(
            c_inter=0.1,
            approval_rate=0.8,
            min_confidence=0.8,
            has_strong_objection=True,
        )
        assert cs.overall == min(0.1, 0.3)

    def test_all_zeros_gives_zero_overall(self):
        cs = CoherenceScore(
            c_inter=0.0,
            approval_rate=0.0,
            min_confidence=0.0,
            has_strong_objection=False,
        )
        assert cs.overall == 0.0


def _make_vote(
    perspective=PerspectiveType.GUARDIAN,
    decision=VoteDecision.APPROVE,
    confidence=0.8,
    reasoning="ok",
    evidence=None,
    requires_grounding=False,
    grounding_status=GroundingStatus.NOT_REQUIRED,
):
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=evidence,
        requires_grounding=requires_grounding,
        grounding_status=grounding_status,
    )


def _make_verdict(votes=None, summary="test", verdict=VerdictType.APPROVE):
    coherence = CoherenceScore(
        c_inter=0.7,
        approval_rate=0.8,
        min_confidence=0.6,
        has_strong_objection=False,
    )
    return CouncilVerdict(
        verdict=verdict,
        coherence=coherence,
        votes=votes or [_make_vote()],
        summary=summary,
    )


class TestCouncilVerdictToDict:
    def test_required_keys_present(self):
        d = _make_verdict().to_dict()
        for key in (
            "verdict", "coherence", "summary", "votes", "genesis",
            "grounding_summary", "transcript", "benevolence_audit",
        ):
            assert key in d

    def test_verdict_value_is_string(self):
        d = _make_verdict(verdict=VerdictType.BLOCK).to_dict()
        assert d["verdict"] == "block"

    def test_coherence_is_float(self):
        d = _make_verdict().to_dict()
        assert isinstance(d["coherence"], float)

    def test_votes_list_has_correct_structure(self):
        vote = _make_vote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.CONCERN,
            confidence=0.75,
            reasoning="some concern",
        )
        d = _make_verdict(votes=[vote]).to_dict()
        assert len(d["votes"]) == 1
        v = d["votes"][0]
        assert v["perspective"] == "analyst"
        assert v["decision"] == "concern"
        assert v["confidence"] == 0.75
        assert v["reasoning"] == "some concern"

    def test_genesis_none_serializes_to_none(self):
        d = _make_verdict().to_dict()
        assert d["genesis"] is None

    def test_grounding_summary_has_ungrounded_claims(self):
        ungrounded_vote = _make_vote(
            grounding_status=GroundingStatus.UNGROUNDED
        )
        d = _make_verdict(votes=[ungrounded_vote]).to_dict()
        assert d["grounding_summary"]["has_ungrounded_claims"] is True

    def test_grounding_summary_clean_when_all_grounded(self):
        grounded_vote = _make_vote(
            grounding_status=GroundingStatus.GROUNDED,
            evidence=["source1", "source2"],
        )
        d = _make_verdict(votes=[grounded_vote]).to_dict()
        assert d["grounding_summary"]["has_ungrounded_claims"] is False
        assert d["grounding_summary"]["total_evidence_sources"] == 2

    def test_string_perspective_serialized_as_string(self):
        vote = _make_vote(perspective="custom_perspective")
        d = _make_verdict(votes=[vote]).to_dict()
        assert d["votes"][0]["perspective"] == "custom_perspective"

    def test_empty_votes_gives_clean_grounding_summary(self):
        d = _make_verdict(votes=[]).to_dict()
        assert d["grounding_summary"]["has_ungrounded_claims"] is False
        assert d["grounding_summary"]["total_evidence_sources"] == 0
