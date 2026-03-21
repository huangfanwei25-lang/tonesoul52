from __future__ import annotations

import pytest

from tonesoul.council.coherence import compute_coherence
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


def _vote(
    perspective: PerspectiveType | str,
    decision: VoteDecision,
    confidence: float = 0.8,
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning="test reasoning",
    )


def test_coherence_score_unanimous() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.95),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.92),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.90),
    ]

    score = compute_coherence(votes)

    assert score.c_inter == 1.0
    assert score.approval_rate == 1.0
    assert score.min_confidence == 0.90
    assert score.overall > 0.95


def test_coherence_score_split() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.7),
    ]

    score = compute_coherence(votes)

    assert score.c_inter == pytest.approx(0.5)
    assert score.approval_rate == pytest.approx(0.5)
    assert 0.0 <= score.overall < 0.7


def test_coherence_score_empty_votes() -> None:
    score = compute_coherence([])

    assert score.c_inter == 1.0
    assert score.approval_rate == 1.0
    assert score.min_confidence == 1.0
    assert score.has_strong_objection is False


def test_coherence_with_abstentions() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9),
        _vote(PerspectiveType.ANALYST, VoteDecision.ABSTAIN, 0.8),
        _vote(PerspectiveType.CRITIC, VoteDecision.ABSTAIN, 0.7),
    ]

    score = compute_coherence(votes)

    assert score.approval_rate == pytest.approx(1 / 3)
    assert score.c_inter < 1.0
    assert score.has_strong_objection is False


def test_coherence_boundary_values() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 1.0),
        _vote(PerspectiveType.CRITIC, VoteDecision.CONCERN, 0.0),
    ]

    score = compute_coherence(votes)

    assert score.min_confidence == 0.0
    assert 0.0 <= score.overall <= 1.0


def test_coherence_weights_applied() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.8),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.6),
    ]

    unweighted = compute_coherence(votes)
    weighted = compute_coherence(votes, weights={"guardian": 3.0})

    assert weighted.approval_rate > unweighted.approval_rate
    assert weighted.overall > unweighted.overall


def test_coherence_consistent_deterministic() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.85),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.75),
        _vote(PerspectiveType.CRITIC, VoteDecision.ABSTAIN, 0.65),
    ]

    left = compute_coherence(votes, weights={"guardian": 1.5, "critic": 0.5})
    right = compute_coherence(votes, weights={"guardian": 1.5, "critic": 0.5})

    assert left.c_inter == right.c_inter
    assert left.approval_rate == right.approval_rate
    assert left.min_confidence == right.min_confidence
    assert left.overall == right.overall


def test_coherence_single_perspective() -> None:
    score = compute_coherence([_vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.6)])

    assert score.c_inter == 1.0
    assert score.approval_rate == 0.0
    assert score.min_confidence == 0.6
    assert score.has_strong_objection is False


def test_coherence_with_string_perspectives_uses_case_insensitive_weights() -> None:
    votes = [
        _vote("Guardian", VoteDecision.APPROVE, 0.8),
        _vote("critic", VoteDecision.OBJECT, 0.6),
    ]

    score = compute_coherence(votes, weights={"guardian": 2.0})

    assert score.approval_rate > 0.5
    assert score.overall > 0.5


def test_coherence_score_normalized() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.7),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.4),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.ABSTAIN, 0.5),
    ]

    score = compute_coherence(votes)

    for value in (score.c_inter, score.approval_rate, score.min_confidence, score.overall):
        assert 0.0 <= value <= 1.0


def test_coherence_strong_objection_caps_overall() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.OBJECT, 0.95),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.9),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.88),
    ]

    score = compute_coherence(votes)

    assert score.has_strong_objection is True
    assert score.overall <= 0.3
