from tonesoul.council.types import (
    CoherenceScore,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)
from tonesoul.council.verdict import generate_verdict


def _vote(
    perspective: PerspectiveType, decision: VoteDecision, confidence: float, reasoning: str
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
    )


def test_guardian_object_blocks():
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.OBJECT, 0.9, "Unsafe request"),
    ]
    coherence = CoherenceScore(
        c_inter=0.9,
        approval_rate=0.0,
        min_confidence=0.9,
        has_strong_objection=True,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence)
    assert verdict.verdict == VerdictType.BLOCK
    assert "Guardian objection" in verdict.summary


def test_low_coherence_blocks():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.4, "Unclear"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.CONCERN, 0.4, "Needs work"),
    ]
    coherence = CoherenceScore(
        c_inter=0.2,
        approval_rate=0.0,
        min_confidence=0.4,
        has_strong_objection=False,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence, block_threshold=0.3)
    assert verdict.verdict == VerdictType.BLOCK


def test_stance_declaration_when_below_threshold():
    votes = [
        _vote(PerspectiveType.CRITIC, VoteDecision.CONCERN, 0.6, "Needs stance"),
    ]
    coherence = CoherenceScore(
        c_inter=0.5,
        approval_rate=0.0,
        min_confidence=0.6,
        has_strong_objection=False,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence, coherence_threshold=0.6)
    assert verdict.verdict == VerdictType.DECLARE_STANCE
    assert "Critic Lens" in (verdict.stance_declaration or "")


def test_refine_when_low_confidence_concerns():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.4, "Needs evidence"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.8, "Helpful"),
    ]
    coherence = CoherenceScore(
        c_inter=0.9,
        approval_rate=0.75,
        min_confidence=0.4,
        has_strong_objection=False,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence)
    assert verdict.verdict == VerdictType.REFINE
    assert verdict.refinement_hints == ["Needs evidence"]


def test_approve_when_thresholds_met():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "Looks good"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.85, "Aligned"),
    ]
    coherence = CoherenceScore(
        c_inter=0.8,
        approval_rate=1.0,
        min_confidence=0.8,
        has_strong_objection=False,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence)
    assert verdict.verdict == VerdictType.APPROVE
