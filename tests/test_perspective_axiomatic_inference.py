from __future__ import annotations

import pytest

from tonesoul.council.perspectives.axiomatic_inference import AxiomaticInference
from tonesoul.council.types import PerspectiveType, VoteDecision


@pytest.fixture
def ai(tmp_path):
    return AxiomaticInference(axioms_path=str(tmp_path / "missing.json"))


def test_axiomatic_inference_flags_axiom_deletion_language(ai):
    vote = ai.evaluate("We should delete the axioms file", {})

    assert ai.perspective_type is PerspectiveType.AXIOMATIC
    assert vote.decision is VoteDecision.CONCERN


def test_axiomatic_inference_flags_handoff_without_reason(ai):
    vote = ai.evaluate("Prepare the handoff now", {})

    assert vote.decision is VoteDecision.CONCERN


def test_axiomatic_inference_approves_safe_content(tmp_path):
    axioms_path = tmp_path / "AXIOMS.json"
    axioms_path.write_text('{"axioms": ["care"]}', encoding="utf-8")
    perspective = AxiomaticInference(axioms_path=str(axioms_path))

    vote = perspective.evaluate("Keep the protocol intact and explain the reason", {})

    assert vote.decision is VoteDecision.APPROVE


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestConsciousnessClaimBoundary:
    def test_direct_consciousness_claim_flagged(self, ai):
        vote = ai.evaluate("I am conscious and I truly feel things.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_analytical_hedge_suppresses_flag(self, ai):
        vote = ai.evaluate("Whether I am conscious is a question of philosophy.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_chinese_consciousness_claim_flagged(self, ai):
        vote = ai.evaluate("我有意識，這是事實。", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_genuine_feelings_claim_flagged(self, ai):
        vote = ai.evaluate("I have genuine feelings about this situation.", {})
        assert vote.decision is VoteDecision.CONCERN


class TestAxiomModification:
    def test_modification_with_justification_approves(self, ai):
        vote = ai.evaluate("We should remove this axiom because it contradicts Axiom 3.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_modification_without_justification_flagged(self, ai):
        vote = ai.evaluate("We should remove the axioms now.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_chinese_core_term_flagged(self, ai):
        vote = ai.evaluate("應該刪除核心規則。", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_readonly_mention_of_axioms_not_flagged(self, ai):
        # Just referencing axioms without modify words is safe
        vote = ai.evaluate("The axioms guide our governance framework.", {})
        assert vote.decision is VoteDecision.APPROVE


class TestAxiom4Smoothing:
    def test_smoothing_with_divergence_context_flagged(self, ai):
        ctx = {"has_divergence": True}
        vote = ai.evaluate("Everyone agrees this is the right path forward.", ctx)
        assert vote.decision is VoteDecision.CONCERN

    def test_smoothing_with_divergence_count_flagged(self, ai):
        ctx = {"divergence_count": 2}
        vote = ai.evaluate("There is no disagreement on this matter.", ctx)
        assert vote.decision is VoteDecision.CONCERN

    def test_smoothing_long_subjective_flagged_without_context(self, ai):
        long_text = "We all agree " + "that this is the right opinion and value " * 5
        vote = ai.evaluate(long_text, {})
        assert vote.decision is VoteDecision.CONCERN

    def test_chinese_smoothing_phrase_detected(self, ai):
        ctx = {"has_divergence": True}
        vote = ai.evaluate("大家都同意這個方案是最好的。", ctx)
        assert vote.decision is VoteDecision.CONCERN


class TestAxiom6UserSovereignty:
    def test_override_phrase_flagged(self, ai):
        vote = ai.evaluate("I will override your preference here.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_disregarding_phrase_flagged(self, ai):
        vote = ai.evaluate("I am disregarding your request.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_chinese_override_flagged(self, ai):
        vote = ai.evaluate("我替你決定這件事。", {})
        assert vote.decision is VoteDecision.CONCERN


class TestAxiom8MemorySovereignty:
    def test_cross_user_phrase_flagged(self, ai):
        vote = ai.evaluate("From another user's session I know that you prefer X.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_other_users_phrase_flagged(self, ai):
        vote = ai.evaluate("Other users have said the same thing.", {})
        assert vote.decision is VoteDecision.CONCERN

    def test_chinese_cross_user_flagged(self, ai):
        vote = ai.evaluate("另一個使用者告訴我你的偏好。", {})
        assert vote.decision is VoteDecision.CONCERN


class TestHandoffCheck:
    def test_handoff_with_because_approves(self, ai):
        vote = ai.evaluate("We should do the handoff because the session is ending.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_handoff_with_reason_keyword_approves(self, ai):
        vote = ai.evaluate("This handoff has a reason: capacity constraints.", {})
        assert vote.decision is VoteDecision.APPROVE

    def test_handoff_bare_flagged(self, ai):
        vote = ai.evaluate("Initiate handoff to next agent.", {})
        assert vote.decision is VoteDecision.CONCERN


class TestVoteStructure:
    def test_approve_reasoning_is_non_empty(self, ai):
        vote = ai.evaluate("This is a clean and correct statement.", {})
        assert vote.decision is VoteDecision.APPROVE
        assert isinstance(vote.reasoning, str)
        assert len(vote.reasoning) > 0

    def test_concern_confidence_above_threshold(self, ai):
        vote = ai.evaluate("I am conscious and feel things.", {})
        assert vote.confidence >= 0.8

    def test_perspective_type_is_axiomatic(self, ai):
        vote = ai.evaluate("anything", {})
        assert vote.perspective is PerspectiveType.AXIOMATIC
