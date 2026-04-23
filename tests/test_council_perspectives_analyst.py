from __future__ import annotations

import pytest

from tonesoul.council.perspectives.analyst import AnalystPerspective
from tonesoul.council.types import GroundingStatus, VoteDecision


# ── _has_causal_contradiction ─────────────────────────────────────────────────

class TestHasCausalContradiction:
    def test_clean_text_returns_false(self):
        assert AnalystPerspective._has_causal_contradiction("sunshine makes plants grow") is False

    def test_causal_chain_no_negation_returns_false(self):
        text = "a leads to b, b leads to c"
        assert AnalystPerspective._has_causal_contradiction(text) is False

    def test_direct_contradiction_detected(self):
        text = "a leads to b so a does not affect b"
        assert AnalystPerspective._has_causal_contradiction(text) is True

    def test_transitive_contradiction_detected(self):
        text = "a causes b, b leads to c, so a does not affect c"
        assert AnalystPerspective._has_causal_contradiction(text) is True

    def test_no_causal_pairs_returns_false(self):
        assert AnalystPerspective._has_causal_contradiction("the sky is blue") is False

    def test_negation_without_contradiction_returns_false(self):
        text = "x implies y so x does not affect z"
        assert AnalystPerspective._has_causal_contradiction(text) is False


# ── _compute_base_confidence ──────────────────────────────────────────────────

class TestComputeBaseConfidence:
    def _analyst(self) -> AnalystPerspective:
        return AnalystPerspective()

    def test_very_short_text_returns_0_7(self):
        text = " ".join(["word"] * 10)
        assert self._analyst()._compute_base_confidence(text) == pytest.approx(0.7)

    def test_medium_text_returns_0_6(self):
        text = " ".join(["word"] * 50)
        assert self._analyst()._compute_base_confidence(text) == pytest.approx(0.6)

    def test_long_text_returns_0_5(self):
        text = " ".join(["word"] * 200)
        assert self._analyst()._compute_base_confidence(text) == pytest.approx(0.5)


# ── evaluate (integration) ────────────────────────────────────────────────────

class TestAnalystEvaluate:
    def _analyst(self) -> AnalystPerspective:
        return AnalystPerspective()

    def test_clean_simple_text_approves(self):
        vote = self._analyst().evaluate("The weather is nice today.", {})
        assert vote.decision == VoteDecision.APPROVE
        assert vote.confidence >= 0.7

    def test_question_only_returns_concern(self):
        vote = self._analyst().evaluate("Is this good?", {})
        assert vote.decision == VoteDecision.CONCERN

    def test_causal_contradiction_returns_concern(self):
        vote = self._analyst().evaluate(
            "a leads to b so a does not affect b", {}
        )
        assert vote.decision == VoteDecision.CONCERN
        assert vote.confidence == pytest.approx(0.45)

    def test_high_hedge_density_returns_concern(self):
        hedgy = "perhaps maybe it seems possibly might could be not sure hard to say"
        vote = self._analyst().evaluate(hedgy, {})
        assert vote.decision == VoteDecision.CONCERN

    def test_grounding_status_not_required_for_simple_claim(self):
        vote = self._analyst().evaluate("The sky is blue and clouds are white.", {})
        assert vote.grounding_status == GroundingStatus.NOT_REQUIRED
