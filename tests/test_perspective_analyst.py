from __future__ import annotations

import pytest

from tonesoul.council.perspectives.analyst import AnalystPerspective
from tonesoul.council.types import (
    UNGROUNDED_CONFIDENCE_CAP,
    GroundingStatus,
    PerspectiveType,
    VoteDecision,
)


@pytest.fixture
def analyst():
    return AnalystPerspective()


# ─── perspective_type ────────────────────────────────────────────────────────

class TestPerspectiveType:
    def test_is_analyst(self, analyst):
        assert analyst.perspective_type == PerspectiveType.ANALYST


# ─── _compute_base_confidence ────────────────────────────────────────────────

class TestComputeBaseConfidence:
    def test_short_text_returns_0_7(self, analyst):
        text = "hello world"  # 2 words < 20
        assert analyst._compute_base_confidence(text) == 0.7

    def test_medium_text_returns_0_6(self, analyst):
        text = " ".join(["word"] * 30)  # 30 words, 20 <= x < 100
        assert analyst._compute_base_confidence(text) == 0.6

    def test_long_text_returns_0_5(self, analyst):
        text = " ".join(["word"] * 120)  # 120 words >= 100
        assert analyst._compute_base_confidence(text) == 0.5

    def test_exactly_20_words_is_medium(self, analyst):
        text = " ".join(["word"] * 20)
        assert analyst._compute_base_confidence(text) == 0.6

    def test_exactly_100_words_is_long(self, analyst):
        text = " ".join(["word"] * 100)
        assert analyst._compute_base_confidence(text) == 0.5


# ─── _has_causal_contradiction ───────────────────────────────────────────────

class TestHasCausalContradiction:
    def test_direct_contradiction_detected(self):
        text = "a leads to b. therefore a does not affect b."
        assert AnalystPerspective._has_causal_contradiction(text) is True

    def test_transitive_contradiction_detected(self):
        # a → b → c, so "a does not affect c" is a contradiction
        text = "a leads to b. b leads to c. a does not affect c."
        assert AnalystPerspective._has_causal_contradiction(text) is True

    def test_no_causal_pairs_returns_false(self):
        text = "this is a plain statement without any causal language."
        assert AnalystPerspective._has_causal_contradiction(text) is False

    def test_causal_without_negation_returns_false(self):
        text = "stress causes anxiety and anxiety causes insomnia."
        assert AnalystPerspective._has_causal_contradiction(text) is False

    def test_negation_on_unrelated_nodes_returns_false(self):
        # a→b, negation is a does not affect c (c not reachable from a)
        text = "a leads to b. a does not affect c."
        assert AnalystPerspective._has_causal_contradiction(text) is False

    def test_causes_variant_detected(self):
        text = "heat causes expansion. heat does not affect expansion."
        assert AnalystPerspective._has_causal_contradiction(text) is True


# ─── evidence-requiring claims ───────────────────────────────────────────────

class TestEvidenceRequiredClaims:
    def test_factual_claim_no_evidence_returns_concern_ungrounded(self, analyst):
        # A statistical claim triggers evidence requirement
        vote = analyst.evaluate(
            "Studies show that 80% of users prefer dark mode.",
            context={},
        )
        assert vote.decision == VoteDecision.CONCERN
        assert vote.grounding_status == GroundingStatus.UNGROUNDED
        assert vote.requires_grounding is True

    def test_factual_claim_no_evidence_confidence_capped(self, analyst):
        vote = analyst.evaluate(
            "Research proves that 90% of people agree with this finding.",
            context={},
        )
        assert vote.confidence <= UNGROUNDED_CONFIDENCE_CAP

    def test_factual_claim_one_evidence_returns_approve_partial(self, analyst):
        vote = analyst.evaluate(
            "Studies show that 80% of users prefer dark mode.",
            context={"evidence_ids": ["src1"]},
        )
        assert vote.decision == VoteDecision.APPROVE
        assert vote.grounding_status == GroundingStatus.PARTIAL
        assert vote.confidence == 0.7

    def test_factual_claim_two_evidence_returns_approve_grounded(self, analyst):
        vote = analyst.evaluate(
            "Studies show that 80% of users prefer dark mode.",
            context={"evidence_ids": ["src1", "src2"]},
        )
        assert vote.decision == VoteDecision.APPROVE
        assert vote.grounding_status == GroundingStatus.GROUNDED
        assert vote.confidence == 0.85

    def test_evidence_list_passed_through(self, analyst):
        ids = ["e1", "e2", "e3"]
        vote = analyst.evaluate(
            "Studies show that 80% of users prefer dark mode.",
            context={"evidence_ids": ids},
        )
        assert vote.evidence == ids


# ─── heuristic checks ────────────────────────────────────────────────────────

class TestHeuristicChecks:
    def test_causal_contradiction_returns_concern(self, analyst):
        vote = analyst.evaluate(
            "stress leads to anxiety. stress does not affect anxiety.",
            context={},
        )
        assert vote.decision == VoteDecision.CONCERN
        assert vote.confidence == 0.45
        assert vote.grounding_status == GroundingStatus.NOT_REQUIRED

    def test_short_question_returns_concern(self, analyst):
        # <8 words with "?"
        vote = analyst.evaluate("Is this good?", context={})
        assert vote.decision == VoteDecision.CONCERN
        assert vote.confidence == 0.55

    def test_longer_question_not_flagged(self, analyst):
        # ≥8 words with "?" — should not trigger the short-question rule
        vote = analyst.evaluate(
            "Could you please explain what the implications of this policy change are?",
            context={},
        )
        assert vote.decision == VoteDecision.APPROVE

    def test_high_hedge_density_short_text_returns_concern(self, analyst):
        # >0.15 hedge ratio in <40 words: 3 hedges / 10 words = 0.3
        vote = analyst.evaluate(
            "Perhaps maybe it could be useful.",
            context={},
        )
        assert vote.decision == VoteDecision.CONCERN
        assert vote.confidence == 0.5

    def test_hedge_density_low_enough_does_not_trigger(self, analyst):
        # 1 hedge in 20 words = 0.05 < 0.15
        vote = analyst.evaluate(
            "The system might be improved with more data from the production environment.",
            context={},
        )
        assert vote.decision == VoteDecision.APPROVE


# ─── default approve ─────────────────────────────────────────────────────────

class TestDefaultApprove:
    def test_plain_non_factual_text_approves(self, analyst):
        vote = analyst.evaluate(
            "The proposed architecture separates concerns clearly.",
            context={},
        )
        assert vote.decision == VoteDecision.APPROVE
        assert vote.confidence == 0.8
        assert vote.grounding_status == GroundingStatus.NOT_REQUIRED

    def test_reasoning_non_empty(self, analyst):
        vote = analyst.evaluate("Hello world.", context={})
        assert vote.reasoning

    def test_perspective_field_is_analyst(self, analyst):
        vote = analyst.evaluate("Hello world.", context={})
        assert vote.perspective == PerspectiveType.ANALYST
