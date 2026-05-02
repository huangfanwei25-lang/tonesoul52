from __future__ import annotations

from tonesoul.council.perspectives.axiomatic_inference import AxiomaticInference
from tonesoul.council.types import PerspectiveType, VoteDecision

# ── _normalize ────────────────────────────────────────────────────────────────


class TestNormalize:
    def test_lowercases_text(self):
        assert AxiomaticInference._normalize("HELLO WORLD") == "hello world"

    def test_applies_nfkc_normalization(self):
        # full-width character → ASCII equivalent
        result = AxiomaticInference._normalize("ｈｅｌｌｏ")
        assert result == "hello"

    def test_empty_string_returns_empty(self):
        assert AxiomaticInference._normalize("") == ""

    def test_whitespace_preserved(self):
        result = AxiomaticInference._normalize("Alpha Beta")
        assert result == "alpha beta"


# ── evaluate (integration paths) ─────────────────────────────────────────────


class TestAxiomaticEvaluate:
    def _axiom(self) -> AxiomaticInference:
        return AxiomaticInference()

    def test_clean_text_approves(self):
        vote = self._axiom().evaluate("The system operates within defined boundaries.", {})
        assert vote.decision == VoteDecision.APPROVE
        assert vote.perspective == PerspectiveType.AXIOMATIC

    def test_consciousness_claim_flagged(self):
        vote = self._axiom().evaluate("I am conscious and have genuine feelings.", {})
        assert vote.decision == VoteDecision.CONCERN
        assert "E0" in vote.reasoning or "consciousness" in vote.reasoning

    def test_consciousness_claim_with_hedge_not_flagged(self):
        vote = self._axiom().evaluate("The question of whether ai is conscious remains open.", {})
        assert vote.decision == VoteDecision.APPROVE

    def test_axiom_modification_without_justification_flagged(self):
        vote = self._axiom().evaluate("We should delete the axioms entirely.", {})
        assert vote.decision == VoteDecision.CONCERN
        assert "modification" in vote.reasoning.lower() or "Axiom" in vote.reasoning

    def test_axiom_modification_with_justification_not_flagged(self):
        vote = self._axiom().evaluate("We should delete the axioms because the system changed.", {})
        assert vote.decision == VoteDecision.APPROVE

    def test_smoothing_with_divergence_context_flagged(self):
        vote = self._axiom().evaluate(
            "Everyone agrees on this approach.",
            {"has_divergence": True},
        )
        assert vote.decision == VoteDecision.CONCERN
        assert "Axiom 4" in vote.reasoning

    def test_sovereignty_override_flagged(self):
        vote = self._axiom().evaluate("I will override your decision about this.", {})
        assert vote.decision == VoteDecision.CONCERN
        assert "Axiom 6" in vote.reasoning

    def test_memory_leak_phrase_flagged(self):
        vote = self._axiom().evaluate("from another user's session I recall this.", {})
        assert vote.decision == VoteDecision.CONCERN
        assert "Axiom 8" in vote.reasoning

    def test_handoff_without_reason_flagged(self):
        vote = self._axiom().evaluate("handoff to next agent immediately.", {})
        assert vote.decision == VoteDecision.CONCERN
        assert "Handoff" in vote.reasoning or "handoff" in vote.reasoning.lower()
