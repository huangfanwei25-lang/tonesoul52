from tonesoul.council.coherence import _agreement_score, compute_coherence
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


def _vote(
    perspective: PerspectiveType, decision: VoteDecision, confidence: float = 0.8
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning="test",
    )


def test_compute_coherence_empty_votes():
    score = compute_coherence([])
    assert score.c_inter == 1.0
    assert score.approval_rate == 1.0
    assert score.min_confidence == 1.0
    assert score.has_strong_objection is False


def test_compute_coherence_adjacent_pair():
    votes = [
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.9),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.7),
    ]
    score = compute_coherence(votes)
    assert score.c_inter == 0.75
    assert score.approval_rate == 0.5
    assert score.min_confidence == 0.7


def test_compute_coherence_strong_objection_caps_overall():
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.OBJECT, 0.9),
        _vote(PerspectiveType.CRITIC, VoteDecision.APPROVE, 0.8),
    ]
    score = compute_coherence(votes)
    assert score.has_strong_objection is True
    assert score.overall == 0.3


def test_agreement_score_boundaries():
    assert _agreement_score(VoteDecision.APPROVE, VoteDecision.APPROVE) == 1.0
    assert _agreement_score(VoteDecision.APPROVE, VoteDecision.CONCERN) == 0.5
    assert _agreement_score(VoteDecision.OBJECT, VoteDecision.CONCERN) == 0.5
    assert _agreement_score(VoteDecision.APPROVE, VoteDecision.OBJECT) == 0.0
    assert _agreement_score(VoteDecision.ABSTAIN, VoteDecision.APPROVE) == 0.25
