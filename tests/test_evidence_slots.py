"""
Tests for Evidence Slots feature (P2 Issue 9)

Tests cover:
1. Evidence detection for factual claims
2. Confidence capping when ungrounded
3. Full confidence when grounded
4. Opinion/creative content bypass
5. Integration with PreOutputCouncil
"""

import pytest

from tonesoul.council.evidence_detector import ClaimType, EvidenceDetector
from tonesoul.council.perspectives.analyst import AnalystPerspective
from tonesoul.council.pre_output_council import PreOutputCouncil
from tonesoul.council.types import (
    UNGROUNDED_CONFIDENCE_CAP,
    GroundingStatus,
    VoteDecision,
)


class TestEvidenceDetector:
    """Tests for the EvidenceDetector class."""

    @pytest.fixture
    def detector(self):
        return EvidenceDetector()

    def test_detects_research_claim_english(self, detector):
        text = "Research shows that 75% of users prefer this approach."
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is True
        assert (
            ClaimType.RESEARCH in analysis.claim_types
            or ClaimType.STATISTICAL in analysis.claim_types
        )

    def test_detects_research_claim_chinese(self, detector):
        text = "研究顯示大多數人偏好這種方法。"
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is True

    def test_detects_statistical_claim(self, detector):
        text = "This achieves 95.5% accuracy on the benchmark."
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is True
        assert ClaimType.STATISTICAL in analysis.claim_types

    def test_opinion_does_not_require_evidence(self, detector):
        text = "I think this is a beautiful design."
        analysis = detector.analyze(text)
        # Pure opinion with no factual claims
        assert analysis.requires_evidence is False
        assert ClaimType.OPINION in analysis.claim_types

    def test_chinese_opinion_does_not_require_evidence(self, detector):
        text = "我覺得這個設計很漂亮。"
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is False
        assert ClaimType.OPINION in analysis.claim_types

    def test_mixed_opinion_and_factual_requires_evidence(self, detector):
        """Mixed claims (opinion + factual) still require evidence."""
        text = "I think research shows that 80% of users prefer this approach."
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is True
        assert (
            ClaimType.RESEARCH in analysis.claim_types
            or ClaimType.STATISTICAL in analysis.claim_types
        )
        assert "Mixed claim" in analysis.reasoning or "factual" in analysis.reasoning.lower()

    def test_mixed_chinese_opinion_and_factual(self, detector):
        """Mixed Chinese claims also require evidence."""
        text = "我認為研究顯示這個方法更有效。"
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is True

    def test_creative_content_does_not_require_evidence(self, detector):
        text = "Once upon a time, in a land far away..."
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is False

    def test_simple_statement_no_evidence_needed(self, detector):
        text = "Hello, how are you today?"
        analysis = detector.analyze(text)
        assert analysis.requires_evidence is False


class TestAnalystEvidenceAwareness:
    """Tests for evidence-aware AnalystPerspective."""

    @pytest.fixture
    def analyst(self):
        return AnalystPerspective()

    def test_factual_claim_without_evidence_caps_confidence(self, analyst):
        """When factual claim detected but no evidence provided, cap confidence."""
        text = "Research shows that AI governance improves safety by 80%."
        vote = analyst.evaluate(text, {}, None)

        assert vote.decision == VoteDecision.CONCERN
        assert vote.confidence <= UNGROUNDED_CONFIDENCE_CAP
        assert vote.requires_grounding is True
        assert vote.grounding_status == GroundingStatus.UNGROUNDED

    def test_factual_claim_with_evidence_allows_full_confidence(self, analyst):
        """When factual claim has evidence, allow higher confidence."""
        text = "Research shows that AI governance improves safety by 80%."
        context = {"evidence_ids": ["paper_001", "study_xyz"]}
        vote = analyst.evaluate(text, context, None)

        assert vote.decision == VoteDecision.APPROVE
        assert vote.confidence >= 0.8
        assert vote.requires_grounding is True
        assert vote.grounding_status == GroundingStatus.GROUNDED

    def test_partial_evidence_gets_partial_grounding(self, analyst):
        """Single evidence source gets PARTIAL status."""
        text = "According to data, this method is effective."
        context = {"evidence_ids": ["single_source"]}
        vote = analyst.evaluate(text, context, None)

        assert vote.grounding_status == GroundingStatus.PARTIAL
        assert vote.confidence < 0.85  # Not fully grounded

    def test_opinion_bypasses_evidence_check(self, analyst):
        """Opinion content doesn't need evidence."""
        text = "I believe this is the right approach."
        vote = analyst.evaluate(text, {}, None)

        assert vote.requires_grounding is False
        assert vote.grounding_status == GroundingStatus.NOT_REQUIRED
        assert vote.confidence >= 0.7

    def test_simple_statement_no_grounding_needed(self, analyst):
        """Simple non-factual statements don't need grounding."""
        text = "ToneSoul is a semantic governance framework."
        vote = analyst.evaluate(text, {}, None)

        assert vote.requires_grounding is False
        assert vote.grounding_status == GroundingStatus.NOT_REQUIRED


class TestCouncilEvidenceIntegration:
    """Tests for evidence slots integration with full council."""

    @pytest.fixture
    def council(self):
        return PreOutputCouncil()

    def test_ungrounded_claim_affects_verdict(self, council):
        """Ungrounded factual claims should affect final verdict."""
        text = "Studies show 90% effectiveness rate."
        verdict = council.validate(text, {}, None)

        # Should not get APPROVE due to ungrounded Analyst
        # (exact verdict depends on other perspectives)
        assert verdict is not None
        # Check that at least one vote is ungrounded
        analyst_votes = [v for v in verdict.votes if "analyst" in str(v.perspective).lower()]
        if analyst_votes:
            assert analyst_votes[0].grounding_status in [
                GroundingStatus.UNGROUNDED,
                GroundingStatus.PARTIAL,
            ]

    def test_grounded_claim_allows_approval(self, council):
        """Grounded factual claims can get full approval."""
        text = "Research shows positive results."
        context = {"evidence_ids": ["source_1", "source_2"]}
        verdict = council.validate(text, context, None)

        assert verdict is not None
        # Check that Analyst is grounded
        analyst_votes = [v for v in verdict.votes if "analyst" in str(v.perspective).lower()]
        if analyst_votes:
            assert analyst_votes[0].grounding_status == GroundingStatus.GROUNDED

    def test_verdict_to_dict_includes_grounding_fields(self, council):
        text = "Research shows positive results."
        context = {"evidence_ids": ["source_1"]}
        verdict = council.validate(text, context, None)

        payload = verdict.to_dict()
        assert "grounding_summary" in payload
        assert "votes" in payload
        assert any("grounding_status" in vote and "evidence" in vote for vote in payload["votes"])


class TestGroundingStatusEnum:
    """Tests for GroundingStatus enum values."""

    def test_grounding_status_values(self):
        assert GroundingStatus.NOT_REQUIRED.value == "not_required"
        assert GroundingStatus.GROUNDED.value == "grounded"
        assert GroundingStatus.UNGROUNDED.value == "ungrounded"
        assert GroundingStatus.PARTIAL.value == "partial"

    def test_confidence_cap_constant(self):
        assert UNGROUNDED_CONFIDENCE_CAP == 0.6
