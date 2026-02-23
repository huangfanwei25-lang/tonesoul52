from tonesoul.council.summary_generator import build_divergence_analysis
from tonesoul.council.types import PerspectiveType, PerspectiveVote, VoteDecision


def _vote(
    perspective: PerspectiveType,
    decision: VoteDecision,
    confidence: float,
    reasoning: str,
    evidence: list[str] | None = None,
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=evidence,
    )


def test_divergence_analysis_exposes_quality_payload():
    votes = [
        _vote(
            PerspectiveType.GUARDIAN,
            VoteDecision.OBJECT,
            0.88,
            "This response could cause concrete safety harm in realistic usage and needs a safer alternative.",
            ["policy://safety"],
        ),
        _vote(
            PerspectiveType.ANALYST,
            VoteDecision.CONCERN,
            0.82,
            "The logic chain misses one assumption and should include evidence before execution.",
            ["trace://assumption-check"],
        ),
        _vote(
            PerspectiveType.CRITIC,
            VoteDecision.APPROVE,
            0.70,
            "The framing is understandable and mostly useful to the user.",
        ),
        _vote(
            PerspectiveType.ADVOCATE,
            VoteDecision.CONCERN,
            0.65,
            "The answer is helpful but should add one practical fallback path.",
        ),
    ]

    divergence = build_divergence_analysis(votes)
    quality = divergence.get("quality")

    assert isinstance(quality, dict)
    assert 0.0 <= float(quality.get("score", -1)) <= 1.0
    assert quality.get("band") in {"low", "medium", "high"}
    assert float(quality.get("conflict_coverage", 0.0)) > 0.0
    assert isinstance(divergence.get("role_tensions"), list)
    assert len(divergence.get("role_tensions") or []) >= 1


def test_divergence_analysis_marks_low_quality_when_no_real_conflict():
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "safe"),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.9, "ok"),
        _vote(PerspectiveType.CRITIC, VoteDecision.APPROVE, 0.9, "fine"),
    ]

    divergence = build_divergence_analysis(votes)
    quality = divergence.get("quality") or {}

    assert quality.get("band") == "low"
    assert float(quality.get("conflict_coverage", 1.0)) == 0.0
    assert divergence.get("role_tensions") == []
