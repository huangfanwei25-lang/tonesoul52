from __future__ import annotations

from tonesoul.council.compact import (
    compact_calibration,
    compact_governance_summary,
    compact_verdict,
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


def _verdict() -> CouncilVerdict:
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.91,
            reasoning="bounded approve",
            evidence=["doc:a"],
            requires_grounding=True,
            grounding_status=GroundingStatus.GROUNDED,
        ),
        PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.OBJECT,
            confidence=0.86,
            reasoning="risky path",
            evidence=[],
            requires_grounding=True,
            grounding_status=GroundingStatus.UNGROUNDED,
        ),
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.82,
            reasoning="approve with caution",
            evidence=["doc:b"],
            requires_grounding=True,
            grounding_status=GroundingStatus.GROUNDED,
        ),
    ]
    return CouncilVerdict(
        verdict=VerdictType.REFINE,
        coherence=CoherenceScore(
            c_inter=0.72,
            approval_rate=0.5,
            min_confidence=0.86,
            has_strong_objection=True,
        ),
        votes=votes,
        summary="long summary that should not survive compact output",
        transcript={
            "skill_contract_observability": {
                "matched_skill_ids": ["narrative_oceanic_phase_transition", "governance.review"]
            }
        },
        responsibility_tier="tier_2",
        collapse_warning="tension spike",
        uncertainty_band="medium",
    )


def test_compact_verdict_from_council_verdict_stays_bounded() -> None:
    result = compact_verdict(_verdict())

    assert result["_compact"] is True
    assert result["kind"] == "council_verdict"
    assert result["verdict"] == "refine"
    assert result["coherence"] == 0.3
    assert result["minority"] == ["critic"]
    assert result["risk_level"] == "high"
    assert result["matched_skill_ids"] == [
        "narrative_oceanic_phase_transition",
        "governance.review",
    ]
    assert result["responsibility_tier"] == "tier_2"
    assert result["collapse_warning"] == "tension spike"
    assert result["uncertainty_band"] == "medium"
    assert "summary" not in result
    assert "votes" not in result
    assert "transcript" not in result
    assert "reasoning" not in str(result)
    assert "evidence" not in str(result)


def test_compact_verdict_accepts_bounded_dict_payload() -> None:
    result = compact_verdict(
        {
            "verdict": "approve",
            "coherence": 0.88,
            "minority_perspectives": [],
            "matched_skill_ids": ["safe.skill"],
            "vote_profile": [
                {"perspective": "guardian", "decision": "approve", "confidence": 0.9},
                {"perspective": "analyst", "decision": "approve", "confidence": 0.8},
            ],
        }
    )

    assert result["verdict"] == "approve"
    assert result["risk_level"] == "low"
    assert result["matched_skill_ids"] == ["safe.skill"]


def test_compact_calibration_preserves_independent_metrics_only() -> None:
    result = compact_calibration(
        {
            "status": "v0a_realism_baseline",
            "language_boundary": {"ceiling_effect": "none"},
            "metrics": {
                "agreement_stability": {
                    "status": "computed",
                    "sample_count": 6,
                    "mean_dominant_verdict_ratio": 1.0,
                    "mean_split_half_jsd": 0.0,
                },
                "internal_self_consistency": {
                    "status": "computed",
                    "sample_count": 200,
                    "consistency_rate": 0.743,
                    "inconsistent_count": 46,
                },
                "suppression_recovery_rate": {
                    "status": "insufficient_data",
                    "sample_count": 1,
                    "recovery_rate": 0.0,
                    "recovery_events": 0,
                },
                "persistence_coverage": {
                    "status": "computed",
                    "sample_count": 5,
                    "overall_field_coverage": 1.0,
                },
            },
        }
    )

    assert result["_compact"] is True
    assert result["kind"] == "council_calibration"
    assert result["status"] == "v0a_realism_baseline"
    assert result["ceiling_effect"] == "none"
    assert result["agreement_stability"] == {
        "status": "computed",
        "n": 6,
        "mean_dominant_verdict_ratio": 1.0,
        "mean_split_half_jsd": 0.0,
    }
    assert result["internal_self_consistency"]["consistency_rate"] == 0.743
    assert result["suppression_recovery_rate"]["status"] == "insufficient_data"
    assert result["persistence_coverage"]["overall_field_coverage"] == 1.0
    flat = str(result)
    assert "realism_score" not in flat
    assert "council_health" not in flat
    assert "composite" not in flat


def test_compact_governance_summary_prefers_explicit_available_tools() -> None:
    result = compact_governance_summary(
        {
            "readiness": {"status": "pass"},
            "claim_boundary": {"current_tier": "collaborator_beta"},
            "available_tools": [
                "council_deliberate",
                "council_check_claim",
                "council_get_calibration",
                "council_get_status",
            ],
        }
    )

    assert result == {
        "_compact": True,
        "kind": "governance_summary",
        "readiness": "pass",
        "claim_tier": "collaborator_beta",
        "claim_rule": "evidence_bounded",
        "available_tools": [
            "council_deliberate",
            "council_check_claim",
            "council_get_calibration",
            "council_get_status",
        ],
    }


def test_compact_governance_summary_can_derive_tool_names_from_commands() -> None:
    result = compact_governance_summary(
        {
            "readiness": {"status": "needs_clarification"},
            "claim_boundary": {
                "current_tier": "collaborator_beta",
                "receiver_note": "Do not claim production readiness, AI consciousness, or council-as-truth.",
            },
            "underlying_commands": [
                "python -m tonesoul.diagnose --agent codex",
                "python scripts/start_agent_session.py --agent codex",
                "python scripts/run_observer_window.py --agent codex",
            ],
        }
    )

    assert result["readiness"] == "needs_clarification"
    assert result["available_tools"] == ["diagnose", "session_start", "observer_window"]
