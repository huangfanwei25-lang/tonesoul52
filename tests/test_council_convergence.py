"""Tests for tonesoul.council.convergence."""

from __future__ import annotations

from tonesoul.council.convergence import (
    MAX_RECOMMENDED_ROUNDS,
    ConvergenceResult,
    check_convergence,
    convergence_score,
    should_continue_deliberating,
)
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


def _vote(perspective, decision=VoteDecision.APPROVE, confidence=0.8):
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning="test",
    )


# ── convergence_score ─────────────────────────────────────────────────────────


class TestConvergenceScore:
    def test_empty_votes_returns_one(self):
        assert convergence_score([]) == 1.0

    def test_single_vote_returns_its_confidence(self):
        vote = _vote(PerspectiveType.ANALYST, confidence=0.75)
        assert convergence_score([vote]) == 0.75

    def test_identical_confidences_returns_one(self):
        votes = [
            _vote(PerspectiveType.ANALYST, confidence=0.8),
            _vote(PerspectiveType.GUARDIAN, confidence=0.8),
            _vote(PerspectiveType.CRITIC, confidence=0.8),
        ]
        assert convergence_score(votes) == 1.0

    def test_maximally_spread_returns_low_score(self):
        # 0.0 and 1.0 → maximum variance
        votes = [
            _vote(PerspectiveType.ANALYST, confidence=0.0),
            _vote(PerspectiveType.GUARDIAN, confidence=1.0),
        ]
        score = convergence_score(votes)
        assert score < 0.5

    def test_score_in_unit_interval(self):
        votes = [
            _vote(PerspectiveType.ANALYST, confidence=0.6),
            _vote(PerspectiveType.GUARDIAN, confidence=0.9),
        ]
        score = convergence_score(votes)
        assert 0.0 <= score <= 1.0

    def test_tighter_spread_gives_higher_score(self):
        tight = [
            _vote(PerspectiveType.ANALYST, confidence=0.79),
            _vote(PerspectiveType.GUARDIAN, confidence=0.81),
        ]
        wide = [
            _vote(PerspectiveType.ANALYST, confidence=0.5),
            _vote(PerspectiveType.GUARDIAN, confidence=1.0),
        ]
        assert convergence_score(tight) > convergence_score(wide)


# ── check_convergence ─────────────────────────────────────────────────────────


class TestCheckConvergence:
    def _converged_votes(self):
        return [
            _vote(PerspectiveType.ANALYST, confidence=0.85),
            _vote(PerspectiveType.GUARDIAN, confidence=0.82),
            _vote(PerspectiveType.CRITIC, confidence=0.88),
        ]

    def _diverged_votes(self):
        # Spread: 0.95, 0.10, 0.60 → variance ~0.122 → score ~0.51 (below threshold)
        return [
            _vote(PerspectiveType.ANALYST, confidence=0.95),
            _vote(PerspectiveType.GUARDIAN, confidence=0.10),
            _vote(PerspectiveType.CRITIC, confidence=0.60),
        ]

    def test_returns_convergence_result(self):
        result = check_convergence(self._converged_votes())
        assert isinstance(result, ConvergenceResult)

    def test_tight_cluster_converged(self):
        result = check_convergence(self._converged_votes())
        assert result.converged is True

    def test_wide_spread_not_converged(self):
        result = check_convergence(self._diverged_votes())
        assert result.converged is False

    def test_empty_votes_converged(self):
        result = check_convergence([])
        assert result.converged is True

    def test_objecting_vote_prevents_convergence(self):
        votes = [
            _vote(PerspectiveType.GUARDIAN, decision=VoteDecision.OBJECT, confidence=0.9),
            _vote(PerspectiveType.ANALYST, confidence=0.85),
        ]
        result = check_convergence(votes)
        assert result.converged is False

    def test_objecting_perspective_in_suggested_focus(self):
        votes = [
            _vote(PerspectiveType.GUARDIAN, decision=VoteDecision.OBJECT, confidence=0.9),
            _vote(PerspectiveType.ANALYST, confidence=0.85),
        ]
        result = check_convergence(votes)
        assert "guardian" in result.suggested_focus

    def test_diverged_recommends_additional_rounds(self):
        result = check_convergence(self._diverged_votes())
        assert result.additional_rounds_recommended > 0

    def test_converged_recommends_zero_rounds(self):
        result = check_convergence(self._converged_votes())
        assert result.additional_rounds_recommended == 0

    def test_score_matches_convergence_score_function(self):
        votes = self._converged_votes()
        result = check_convergence(votes)
        assert abs(result.score - convergence_score(votes)) < 0.001

    def test_recommendation_is_non_empty_string(self):
        result = check_convergence(self._converged_votes())
        assert isinstance(result.recommendation, str)
        assert result.recommendation.strip()

    def test_to_dict_has_required_keys(self):
        result = check_convergence(self._converged_votes())
        d = result.to_dict()
        for key in (
            "converged",
            "score",
            "variance",
            "mean_confidence",
            "recommendation",
            "suggested_focus",
            "additional_rounds_recommended",
        ):
            assert key in d

    def test_custom_threshold_respected(self):
        votes = self._converged_votes()
        # With threshold=0.999 (impossible), even a tight cluster is not converged
        result = check_convergence(votes, threshold=0.999)
        assert result.converged is False

    def test_additional_rounds_capped_at_max(self):
        # Maximally diverged votes
        votes = [
            _vote(PerspectiveType.ANALYST, confidence=0.0),
            _vote(PerspectiveType.GUARDIAN, confidence=1.0),
        ]
        result = check_convergence(votes)
        assert result.additional_rounds_recommended <= MAX_RECOMMENDED_ROUNDS


# ── should_continue_deliberating ──────────────────────────────────────────────


class TestShouldContinueDeliberating:
    def _not_converged(self):
        return ConvergenceResult(
            converged=False,
            score=0.5,
            variance=0.1,
            mean_confidence=0.7,
            recommendation="not converged",
            additional_rounds_recommended=1,
        )

    def _converged(self):
        return ConvergenceResult(
            converged=True,
            score=0.9,
            variance=0.005,
            mean_confidence=0.85,
            recommendation="converged",
            additional_rounds_recommended=0,
        )

    def test_continue_when_not_converged_round_zero(self):
        assert should_continue_deliberating(self._not_converged(), current_round=0) is True

    def test_do_not_continue_when_converged(self):
        assert should_continue_deliberating(self._converged(), current_round=0) is False

    def test_do_not_continue_at_max_rounds(self):
        result = self._not_converged()
        assert should_continue_deliberating(result, current_round=MAX_RECOMMENDED_ROUNDS) is False

    def test_do_not_continue_beyond_max_rounds(self):
        result = self._not_converged()
        assert (
            should_continue_deliberating(result, current_round=MAX_RECOMMENDED_ROUNDS + 5) is False
        )

    def test_custom_max_rounds_respected(self):
        result = self._not_converged()
        assert should_continue_deliberating(result, current_round=0, max_rounds=0) is False

    def test_no_recommended_rounds_prevents_continuation(self):
        result = ConvergenceResult(
            converged=False,
            score=0.6,
            variance=0.05,
            mean_confidence=0.7,
            recommendation="low",
            additional_rounds_recommended=0,
        )
        assert should_continue_deliberating(result, current_round=0) is False
