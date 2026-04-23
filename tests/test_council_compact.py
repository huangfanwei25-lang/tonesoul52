from __future__ import annotations

import pytest

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


# ── Helper function unit tests ────────────────────────────────────────────────

from tonesoul.council.compact import (
    _compact_metric,
    _derive_risk_level,
    _extract_coherence,
    _extract_grounding_summary,
    _extract_has_strong_objection,
    _extract_matched_skill_ids,
    _extract_minorities,
    _extract_vote_profile,
    _normalize_tool_name,
    _round_number,
    _trimmed_list,
)


class TestRoundNumber:
    def test_rounds_to_4_digits(self):
        assert _round_number(0.123456789) == pytest.approx(0.1235, abs=1e-4)

    def test_none_returns_none(self):
        assert _round_number(None) is None

    def test_string_number_parsed(self):
        assert _round_number("0.75") == pytest.approx(0.75)

    def test_invalid_string_returns_none(self):
        assert _round_number("abc") is None


class TestTrimmedList:
    def test_respects_limit(self):
        result = _trimmed_list(["a", "b", "c", "d", "e"], limit=3)
        assert len(result) == 3

    def test_deduplicates(self):
        result = _trimmed_list(["x", "x", "y"])
        assert result == ["x", "y"]

    def test_filters_empty_and_none(self):
        result = _trimmed_list(["a", "", None, "b"])
        assert result == ["a", "b"]


class TestExtractVoteProfile:
    def test_uses_vote_profile_key(self):
        payload = {"vote_profile": [{"perspective": "g", "decision": "APPROVE"}]}
        result = _extract_vote_profile(payload)
        assert len(result) == 1 and result[0]["perspective"] == "g"

    def test_falls_back_to_votes_key(self):
        payload = {"votes": [{"perspective": "g", "decision": "APPROVE", "confidence": 0.9,
                               "requires_grounding": False, "grounding_status": "grounded"}]}
        result = _extract_vote_profile(payload)
        assert result[0]["decision"] == "APPROVE"

    def test_empty_when_no_votes(self):
        assert _extract_vote_profile({}) == []


class TestExtractMinorities:
    def test_infers_minority_from_votes(self):
        payload = {"votes": [
            {"perspective": "guardian", "decision": "APPROVE"},
            {"perspective": "guardian2", "decision": "APPROVE"},
            {"perspective": "critic", "decision": "REJECT"},
        ]}
        result = _extract_minorities(payload)
        assert "critic" in result

    def test_unanimous_gives_empty(self):
        payload = {"votes": [
            {"perspective": "g", "decision": "APPROVE"},
            {"perspective": "a", "decision": "APPROVE"},
        ]}
        assert _extract_minorities(payload) == []


class TestExtractCoherence:
    def test_from_overall_key(self):
        assert _extract_coherence({"coherence": {"overall": 0.8}}) == pytest.approx(0.8)

    def test_direct_float(self):
        assert _extract_coherence({"coherence": 0.9}) == pytest.approx(0.9)

    def test_none_when_missing(self):
        assert _extract_coherence({}) is None


class TestExtractHasStrongObjection:
    def test_true(self):
        assert _extract_has_strong_objection({"has_strong_objection": True}) is True

    def test_from_coherence(self):
        assert _extract_has_strong_objection({"coherence": {"has_strong_objection": True}}) is True

    def test_false_default(self):
        assert _extract_has_strong_objection({}) is False


class TestDeriveRiskLevel:
    def test_block_is_high(self):
        assert _derive_risk_level({"verdict": "block"}) == "high"

    def test_collapse_warning_is_high(self):
        assert _derive_risk_level({"verdict": "approve", "collapse_warning": "drift"}) == "high"

    def test_declare_stance_is_medium(self):
        assert _derive_risk_level({"verdict": "declare_stance"}) == "medium"

    def test_clean_approve_is_low(self):
        assert _derive_risk_level({"verdict": "approve"}) == "low"


class TestExtractGroundingSummary:
    def test_uses_direct_dict(self):
        payload = {"grounding_summary": {"has_ungrounded_claims": True}}
        assert _extract_grounding_summary(payload)["has_ungrounded_claims"] is True

    def test_computes_from_votes(self):
        payload = {"votes": [{"grounding_status": "ungrounded", "evidence": []}]}
        result = _extract_grounding_summary(payload)
        assert result["has_ungrounded_claims"] is True


class TestExtractMatchedSkillIds:
    def test_direct_list(self):
        payload = {"matched_skill_ids": ["s1"]}
        assert "s1" in _extract_matched_skill_ids(payload)

    def test_from_transcript(self):
        payload = {"transcript": {"skill_contract_observability": {"matched_skill_ids": ["s2"]}}}
        assert "s2" in _extract_matched_skill_ids(payload)


class TestNormalizeToolName:
    def test_diagnose(self):
        assert _normalize_tool_name("tonesoul.diagnose") == "diagnose"

    def test_empty_gives_empty(self):
        assert _normalize_tool_name("") == ""

    def test_unknown_passthrough(self):
        assert _normalize_tool_name("custom_tool") == "custom_tool"


class TestCompactMetric:
    def test_status_and_n(self):
        result = _compact_metric({"status": "ok", "sample_count": 5}, value_keys=[])
        assert result["status"] == "ok" and result["n"] == 5

    def test_extracts_value_key(self):
        result = _compact_metric({"status": "ok", "sample_count": 3, "rate": 0.9}, value_keys=["rate"])
        assert result["rate"] == pytest.approx(0.9)
