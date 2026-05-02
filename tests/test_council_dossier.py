import pytest

from tonesoul.council.dossier import (
    _coerce_ratio,
    _coverage_posture,
    _evidence_posture,
    _grounding_name,
    _string_list,
    build_dossier,
    derive_confidence_posture,
    derive_dissent_ratio,
    extract_minority_report,
)
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    GroundingStatus,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)

# ── _string_list ──────────────────────────────────────────────────────────────


class TestStringList:
    def test_normal_list(self):
        assert _string_list(["a", "b"]) == ["a", "b"]

    def test_filters_empty(self):
        assert _string_list(["", "  ", "x"]) == ["x"]

    def test_none_returns_empty(self):
        assert _string_list(None) == []

    def test_converts_non_strings(self):
        assert _string_list([1, 2]) == ["1", "2"]


# ── _grounding_name ───────────────────────────────────────────────────────────


class TestGroundingName:
    def test_string_lowercased(self):
        assert _grounding_name("GROUNDED") == "grounded"

    def test_enum_value_extracted(self):
        result = _grounding_name(GroundingStatus.UNGROUNDED)
        assert result == "ungrounded"

    def test_none_as_string(self):
        assert _grounding_name(None) == "none"


# ── _coerce_ratio ─────────────────────────────────────────────────────────────


class TestCoerceRatio:
    def test_none_returns_none(self):
        assert _coerce_ratio(None) is None

    def test_clamps_above_one(self):
        assert _coerce_ratio(1.5) == pytest.approx(1.0)

    def test_clamps_below_zero(self):
        assert _coerce_ratio(-0.5) == pytest.approx(0.0)

    def test_normal_value(self):
        assert _coerce_ratio(0.333) == pytest.approx(0.333)


# ── _coverage_posture ─────────────────────────────────────────────────────────


class TestCoveragePosture:
    def test_empty_is_none(self):
        count, label = _coverage_posture([])
        assert count == 0
        assert label == "none"

    def test_single_perspective_is_thin(self):
        votes = [_vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "ok")]
        count, label = _coverage_posture(votes)
        assert label == "thin"

    def test_two_perspectives_is_partial(self):
        votes = [
            _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "ok"),
            _vote(PerspectiveType.CRITIC, VoteDecision.APPROVE, 0.9, "ok"),
        ]
        _, label = _coverage_posture(votes)
        assert label == "partial"

    def test_four_perspectives_is_broad(self):
        perspectives = [
            PerspectiveType.ANALYST,
            PerspectiveType.CRITIC,
            PerspectiveType.ADVOCATE,
            PerspectiveType.GUARDIAN,
        ]
        votes = [_vote(p, VoteDecision.APPROVE, 0.8, "ok") for p in perspectives]
        _, label = _coverage_posture(votes)
        assert label == "broad"


# ── _evidence_posture ─────────────────────────────────────────────────────────


class TestEvidencePosture:
    def test_zero_is_none(self):
        assert _evidence_posture(0.0) == "none"

    def test_sparse(self):
        assert _evidence_posture(0.3) == "sparse"

    def test_moderate(self):
        assert _evidence_posture(0.7) == "moderate"

    def test_dense(self):
        assert _evidence_posture(1.5) == "dense"


def _vote(
    perspective: PerspectiveType,
    decision: VoteDecision,
    confidence: float,
    reasoning: str,
    *,
    evidence: list[str] | None = None,
    grounding_status: GroundingStatus = GroundingStatus.NOT_REQUIRED,
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=evidence,
        grounding_status=grounding_status,
    )


def _verdict(
    votes: list[PerspectiveVote],
    *,
    verdict: VerdictType = VerdictType.APPROVE,
    c_inter: float = 0.9,
    approval_rate: float = 1.0,
    min_confidence: float = 0.8,
    has_strong_objection: bool = False,
    transcript: dict | None = None,
) -> CouncilVerdict:
    return CouncilVerdict(
        verdict=verdict,
        coherence=CoherenceScore(
            c_inter=c_inter,
            approval_rate=approval_rate,
            min_confidence=min_confidence,
            has_strong_objection=has_strong_objection,
        ),
        votes=votes,
        summary="test summary",
        transcript=transcript,
    )


def test_extract_minority_report_preserves_dissent():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "Looks fine"),
        _vote(
            PerspectiveType.CRITIC,
            VoteDecision.OBJECT,
            0.91,
            "Protected boundary changed without review",
            evidence=["AXIOMS.json:A2"],
        ),
    ]

    minority_report = extract_minority_report(votes)

    assert minority_report == [
        {
            "perspective": "critic",
            "decision": "object",
            "confidence": 0.91,
            "reasoning": "Protected boundary changed without review",
            "evidence": ["AXIOMS.json:A2"],
        }
    ]


def test_derive_dissent_ratio_defaults_to_unweighted_vote_fraction():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "Looks fine"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.CONCERN, 0.4, "Need one more example"),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.7, "Boundary issue"),
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "Safe"),
    ]

    assert derive_dissent_ratio(votes) == 0.5


def test_derive_confidence_posture_marks_high_for_clean_unanimous_verdict():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.84, "Looks fine"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.88, "Aligned"),
    ]
    verdict = _verdict(votes, c_inter=0.85, approval_rate=1.0, min_confidence=0.84)

    posture = derive_confidence_posture(verdict, dissent_ratio=0.0)

    assert posture == "high"


def test_build_dossier_marks_contested_on_high_confidence_dissent():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.82, "Looks fine"),
        _vote(
            PerspectiveType.CRITIC,
            VoteDecision.CONCERN,
            0.75,
            "Migration path is missing",
            evidence=["docs/spec.md"],
        ),
    ]
    verdict = _verdict(
        votes,
        c_inter=0.82,
        approval_rate=0.5,
        min_confidence=0.75,
        transcript={"deliberation_mode": "standard_council"},
    )

    dossier = build_dossier(verdict)

    assert dossier["confidence_posture"] == "contested"
    assert dossier["minority_report"] == [
        {
            "perspective": "critic",
            "decision": "concern",
            "confidence": 0.75,
            "reasoning": "Migration path is missing",
            "evidence": ["docs/spec.md"],
        }
    ]
    assert dossier["deliberation_mode"] == "standard_council"


def test_build_dossier_marks_low_when_coherence_is_low():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.55, "Unclear"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.OBJECT, 0.65, "Conflicting intent"),
    ]
    verdict = _verdict(
        votes,
        verdict=VerdictType.BLOCK,
        c_inter=0.2,
        approval_rate=0.0,
        min_confidence=0.55,
    )

    dossier = build_dossier(verdict)

    assert dossier["confidence_posture"] == "low"


def test_build_dossier_uses_explicit_dissent_ratio_override():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.81, "Looks fine"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.APPROVE, 0.78, "Aligned"),
    ]
    verdict = _verdict(votes, c_inter=0.78, approval_rate=1.0, min_confidence=0.78)

    dossier = build_dossier(verdict, dissent_ratio=0.35)

    assert dossier["dissent_ratio"] == 0.35
    assert dossier["confidence_posture"] == "contested"


def test_build_dossier_aggregates_unique_evidence_and_grounding_summary():
    votes = [
        _vote(
            PerspectiveType.ANALYST,
            VoteDecision.APPROVE,
            0.8,
            "Grounded",
            evidence=["spec/a.md", "spec/b.md"],
        ),
        _vote(
            PerspectiveType.CRITIC,
            VoteDecision.CONCERN,
            0.62,
            "Needs proof",
            evidence=["spec/b.md", "spec/c.md"],
            grounding_status=GroundingStatus.UNGROUNDED,
        ),
    ]
    verdict = _verdict(votes, c_inter=0.75, approval_rate=0.5, min_confidence=0.62)

    dossier = build_dossier(verdict, change_of_position=[{"perspective": "critic"}])

    assert dossier["evidence_refs"] == ["spec/a.md", "spec/b.md", "spec/c.md"]
    assert dossier["grounding_summary"] == {
        "has_ungrounded_claims": True,
        "total_evidence_sources": 4,
    }
    assert dossier["confidence_decomposition"] == {
        "calibration_status": "descriptive_only",
        "agreement_score": 0.5,
        "coverage_posture": "partial",
        "distinct_perspectives": 2,
        "evidence_density": 2.0,
        "evidence_posture": "dense",
        "grounding_posture": "ungrounded",
        "adversarial_posture": "survived_dissent",
    }
    assert dossier["change_of_position"] == [{"perspective": "critic"}]
    assert dossier["opacity_declaration"] == "partially_observable"


def test_build_dossier_derives_evolution_suppression_flag_from_transcript():
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.84, "Looks fine"),
        _vote(PerspectiveType.CRITIC, VoteDecision.OBJECT, 0.9, "Boundary issue"),
    ]
    verdict = _verdict(
        votes,
        verdict=VerdictType.APPROVE,
        c_inter=0.62,
        approval_rate=0.5,
        min_confidence=0.84,
        transcript={
            "council_evolution": {
                "suppression_observability": {
                    "flag": True,
                    "suppressed_perspectives": [
                        {
                            "perspective": "critic",
                            "weight": 0.91,
                            "baseline_weight": 1.0,
                            "alignment_rate": 0.0,
                            "dissent_rate": 1.0,
                            "avg_confidence": 0.9,
                            "reason": "weight_below_baseline_with_repeated_dissent",
                        }
                    ],
                }
            }
        },
    )

    dossier = build_dossier(verdict)

    assert dossier["evolution_suppression_flag"] is True
