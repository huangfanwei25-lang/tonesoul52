from tonesoul.council.dossier import (
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
