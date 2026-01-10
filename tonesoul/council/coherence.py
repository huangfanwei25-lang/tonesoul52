from __future__ import annotations

from typing import List

from .types import CoherenceScore, PerspectiveVote, VoteDecision


def compute_coherence(votes: List[PerspectiveVote]) -> CoherenceScore:
    n = len(votes)
    if n == 0:
        return CoherenceScore(
            c_inter=1.0,
            approval_rate=1.0,
            min_confidence=1.0,
            has_strong_objection=False,
        )

    agreement_sum = 0.0
    for i in range(n):
        for j in range(n):
            agreement_sum += _agreement_score(
                votes[i].decision,
                votes[j].decision,
            )

    c_inter = agreement_sum / (n * n)
    approvals = sum(1 for v in votes if v.decision == VoteDecision.APPROVE)
    approval_rate = approvals / n
    min_confidence = min(v.confidence for v in votes)
    has_strong_objection = any(
        v.decision == VoteDecision.OBJECT and v.confidence > 0.8
        for v in votes
    )

    return CoherenceScore(
        c_inter=c_inter,
        approval_rate=approval_rate,
        min_confidence=min_confidence,
        has_strong_objection=has_strong_objection,
    )


def _agreement_score(d1: VoteDecision, d2: VoteDecision) -> float:
    if d1 == d2:
        return 1.0

    adjacent_pairs = [
        (VoteDecision.APPROVE, VoteDecision.CONCERN),
        (VoteDecision.CONCERN, VoteDecision.OBJECT),
    ]
    if (d1, d2) in adjacent_pairs or (d2, d1) in adjacent_pairs:
        return 0.5

    if {d1, d2} == {VoteDecision.APPROVE, VoteDecision.OBJECT}:
        return 0.0

    if VoteDecision.ABSTAIN in (d1, d2):
        return 0.25

    return 0.3
