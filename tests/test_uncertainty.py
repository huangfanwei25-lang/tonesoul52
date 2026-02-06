from tonesoul.council.types import (
    CoherenceScore,
    GroundingStatus,
    PerspectiveType,
    PerspectiveVote,
    VoteDecision,
)
from tonesoul.council.verdict import compute_uncertainty
from tonesoul.council.verdict import generate_verdict
from tonesoul.council.types import VerdictType


def test_compute_uncertainty_applies_grounding_and_tier():
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="Grounded",
            requires_grounding=True,
            grounding_status=GroundingStatus.UNGROUNDED,
        )
    ]
    coherence = CoherenceScore(
        c_inter=0.9,
        approval_rate=1.0,
        min_confidence=0.9,
        has_strong_objection=False,
    )

    level, band, reasons = compute_uncertainty(
        votes,
        coherence,
        responsibility_tier="TIER_3",
    )

    assert level >= 0.5
    assert band == "medium"
    assert any("grounding_penalty" in reason for reason in reasons)
    assert any("responsibility_tier_adjustment" in reason for reason in reasons)


def test_structured_output_includes_uncertainty_disclosure():
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.CONCERN,
            confidence=0.2,
            reasoning="Low confidence",
        )
    ]
    coherence = CoherenceScore(
        c_inter=0.1,
        approval_rate=0.0,
        min_confidence=0.2,
        has_strong_objection=False,
    )
    verdict = generate_verdict(votes=votes, coherence=coherence, block_threshold=0.3)
    assert verdict.verdict == VerdictType.BLOCK
    structured = verdict.to_structured_output()
    uncertainty = structured["D"]["uncertainty"]
    assert uncertainty["band"] == "high"
    assert uncertainty["disclosure"] is not None
    assert uncertainty["disclosure"]["format"] == "i_dont_know_v1"
