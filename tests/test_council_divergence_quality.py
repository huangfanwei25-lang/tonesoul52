from tonesoul.council.summary_generator import (
    _confidence_balance,
    _decision_distribution,
    _evidence_coverage,
    _reasoning_specificity,
    _reasoning_specificity_score,
    build_divergence_analysis,
)
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


# ── _reasoning_specificity_score ──────────────────────────────────────────────

def test_reasoning_specificity_score_empty_returns_zero() -> None:
    assert _reasoning_specificity_score("") == 0.0
    assert _reasoning_specificity_score("   ") == 0.0


def test_reasoning_specificity_score_single_word_no_space() -> None:
    score = _reasoning_specificity_score("safe")
    assert 0.0 < score <= 1.0


def test_reasoning_specificity_score_long_text_caps_at_one() -> None:
    long_text = " ".join(["word"] * 20)
    assert _reasoning_specificity_score(long_text) == 1.0


def test_reasoning_specificity_score_sixteen_words_returns_one() -> None:
    text = " ".join(["word"] * 16)
    assert _reasoning_specificity_score(text) == 1.0


# ── _decision_distribution ───────────────────────────────────────────────────

def test_decision_distribution_counts_all_buckets() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok"),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.8, "concern"),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.7, "object"),
    ]
    dist = _decision_distribution(votes)
    assert dist["approve"] == 1
    assert dist["concern"] == 1
    assert dist["object"] == 1
    assert dist["abstain"] == 0


def test_decision_distribution_empty_votes_returns_zeros() -> None:
    dist = _decision_distribution([])
    assert dist == {"approve": 0, "concern": 0, "object": 0, "abstain": 0}


# ── _evidence_coverage ────────────────────────────────────────────────────────

def test_evidence_coverage_all_with_evidence() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok", ["ev-1"]),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.8, "concern", ["ev-2"]),
    ]
    assert _evidence_coverage(votes) == 1.0


def test_evidence_coverage_none_with_evidence() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok"),
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.8, "concern"),
    ]
    assert _evidence_coverage(votes) == 0.0


def test_evidence_coverage_empty_list_returns_zero() -> None:
    assert _evidence_coverage([]) == 0.0


# ── _confidence_balance ───────────────────────────────────────────────────────

def test_confidence_balance_empty_votes_returns_zero() -> None:
    assert _confidence_balance([]) == 0.0


def test_confidence_balance_identical_confidences() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok"),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.9, "ok"),
    ]
    # spread = 0, ideal = 0.35, so balance = 1 - |0 - 0.35| / 0.35 = 0
    assert _confidence_balance(votes) == 0.0


# ── _reasoning_specificity ────────────────────────────────────────────────────

def test_reasoning_specificity_focuses_on_concern_and_object_votes() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.9,
              "This is a detailed specific reasoning sentence with lots of tokens."),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "ok"),
    ]
    score = _reasoning_specificity(votes)
    assert 0.0 < score <= 1.0


def test_reasoning_specificity_empty_votes_returns_zero() -> None:
    assert _reasoning_specificity([]) == 0.0


# ── build_divergence_analysis edge cases ─────────────────────────────────────

def test_divergence_analysis_with_visual_context() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok")]
    divergence = build_divergence_analysis(votes, context={"visual_context": {"key": "val"}})
    assert divergence["visual_context"] == {"key": "val"}


def test_divergence_analysis_without_context_has_none_visual_context() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok")]
    divergence = build_divergence_analysis(votes)
    assert divergence["visual_context"] is None
