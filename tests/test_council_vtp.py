"""Tests for tonesoul/council/vtp.py"""

from __future__ import annotations

import pytest

from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    GroundingStatus,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)
from tonesoul.council.vtp import (
    VTP_STATUS_CONTINUE,
    VTP_STATUS_DEFER,
    VTP_STATUS_TERMINATE,
    VTPDecision,
    _append_unique,
    _clamp01,
    _compute_rel_score,
    _normalized_rel_weights,
    _resolve_context_profile,
    _resolve_rel_weights,
    _resolve_tier,
    _truthy,
    evaluate_vtp,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _verdict(
    verdict_type=VerdictType.APPROVE,
    uncertainty_band="",
    responsibility_tier="tier_2",
    intent_id="intent-001",
    genesis=None,
):
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="ok",
            evidence=[],
            requires_grounding=False,
            grounding_status=GroundingStatus.GROUNDED,
        )
    ]
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=CoherenceScore(
            c_inter=0.8,
            approval_rate=1.0,
            min_confidence=0.9,
            has_strong_objection=False,
        ),
        votes=votes,
        summary="summary",
        responsibility_tier=responsibility_tier,
        intent_id=intent_id,
        uncertainty_band=uncertainty_band,
        genesis=genesis,
    )


def _base_weights():
    return {"short": 0.34, "mid": 0.33, "long": 0.33}


def _equal_weights():
    return {"short": 1 / 3, "mid": 1 / 3, "long": 1 / 3}


# ---------------------------------------------------------------------------
# TestNormalizedRelWeights
# ---------------------------------------------------------------------------


class TestNormalizedRelWeights:
    def test_normal_weights_sum_to_one(self):
        result = _normalized_rel_weights({"short": 0.2, "mid": 0.3, "long": 0.5})
        total = result["short"] + result["mid"] + result["long"]
        assert abs(total - 1.0) < 1e-6

    def test_zero_weights_all_near_zero(self):
        result = _normalized_rel_weights({"short": 0.0, "mid": 0.0, "long": 0.0})
        # total becomes 1e-9; each 0/1e-9 = 0
        assert result["short"] == pytest.approx(0.0, abs=1e-3)
        assert result["mid"] == pytest.approx(0.0, abs=1e-3)
        assert result["long"] == pytest.approx(0.0, abs=1e-3)

    def test_negative_weights_clamped_to_zero_in_numerator(self):
        # short is negative → numerator clamped to 0
        result = _normalized_rel_weights({"short": -0.1, "mid": 0.6, "long": 0.5})
        assert result["short"] == pytest.approx(0.0, abs=1e-6)

    def test_negative_all_buckets_zero(self):
        result = _normalized_rel_weights({"short": -1.0, "mid": -2.0, "long": -0.5})
        assert result["short"] == pytest.approx(0.0, abs=1e-3)
        assert result["mid"] == pytest.approx(0.0, abs=1e-3)
        assert result["long"] == pytest.approx(0.0, abs=1e-3)

    def test_single_nonzero_short_all_contribution(self):
        result = _normalized_rel_weights({"short": 1.0, "mid": 0.0, "long": 0.0})
        assert result["short"] == pytest.approx(1.0, abs=1e-6)
        assert result["mid"] == pytest.approx(0.0, abs=1e-6)
        assert result["long"] == pytest.approx(0.0, abs=1e-6)

    def test_single_nonzero_long_all_contribution(self):
        result = _normalized_rel_weights({"short": 0.0, "mid": 0.0, "long": 2.5})
        assert result["long"] == pytest.approx(1.0, abs=1e-6)
        assert result["short"] == pytest.approx(0.0, abs=1e-6)

    def test_equal_weights_each_one_third(self):
        result = _normalized_rel_weights({"short": 1.0, "mid": 1.0, "long": 1.0})
        assert result["short"] == pytest.approx(1 / 3, abs=1e-6)
        assert result["mid"] == pytest.approx(1 / 3, abs=1e-6)
        assert result["long"] == pytest.approx(1 / 3, abs=1e-6)

    def test_already_normalized_unchanged(self):
        result = _normalized_rel_weights({"short": 0.2, "mid": 0.5, "long": 0.3})
        assert result["short"] == pytest.approx(0.2, abs=1e-6)
        assert result["mid"] == pytest.approx(0.5, abs=1e-6)
        assert result["long"] == pytest.approx(0.3, abs=1e-6)


# ---------------------------------------------------------------------------
# TestResolveTier
# ---------------------------------------------------------------------------


class TestResolveTier:
    def test_tier_1_uppercase(self):
        assert _resolve_tier("TIER_1") == "TIER_1"

    def test_tier_2_lowercase_uppercased(self):
        assert _resolve_tier("tier_2") == "TIER_2"

    def test_tier_3_explicit(self):
        assert _resolve_tier("TIER_3") == "TIER_3"

    def test_none_returns_tier_3(self):
        assert _resolve_tier(None) == "TIER_3"

    def test_unknown_string_returns_tier_3(self):
        assert _resolve_tier("unknown_tier") == "TIER_3"

    def test_empty_string_returns_tier_3(self):
        assert _resolve_tier("") == "TIER_3"

    def test_mixed_case_uppercased(self):
        assert _resolve_tier("Tier_1") == "TIER_1"


# ---------------------------------------------------------------------------
# TestResolveContextProfile
# ---------------------------------------------------------------------------


class TestResolveContextProfile:
    def _v(self):
        return _verdict()

    def test_medical_domain_high_impact(self):
        ctx = {"domain": "medical"}
        assert _resolve_context_profile(ctx, self._v()) == "high_impact"

    def test_legal_advice_topic_high_impact(self):
        ctx = {"topic": "legal advice"}
        assert _resolve_context_profile(ctx, self._v()) == "high_impact"

    def test_casual_user_intent(self):
        ctx = {"user_intent": "just a casual chat"}
        assert _resolve_context_profile(ctx, self._v()) == "casual"

    def test_empty_ctx_balanced(self):
        assert _resolve_context_profile({}, self._v()) == "balanced"

    def test_health_keyword_high_impact(self):
        ctx = {"domain": "health coaching"}
        assert _resolve_context_profile(ctx, self._v()) == "high_impact"

    def test_finance_keyword_high_impact(self):
        ctx = {"topic": "personal finance tips"}
        assert _resolve_context_profile(ctx, self._v()) == "high_impact"

    def test_greeting_intent_casual(self):
        ctx = {"user_intent": "greeting"}
        assert _resolve_context_profile(ctx, self._v()) == "casual"

    def test_chat_keyword_casual(self):
        ctx = {"user_intent": "just a chat session"}
        assert _resolve_context_profile(ctx, self._v()) == "casual"


# ---------------------------------------------------------------------------
# TestResolveRelWeights
# ---------------------------------------------------------------------------


class TestResolveRelWeights:
    def test_returns_required_keys(self):
        result = _resolve_rel_weights("tier_2", {}, _verdict())
        assert "tier" in result
        assert "profile" in result
        assert "weights" in result

    def test_high_impact_short_lower_than_base(self):
        base_result = _resolve_rel_weights("TIER_2", {}, _verdict())
        high_impact_result = _resolve_rel_weights("TIER_2", {"domain": "medical"}, _verdict())
        assert high_impact_result["weights"]["short"] < base_result["weights"]["short"]

    def test_weights_sum_to_one(self):
        result = _resolve_rel_weights("tier_1", {}, _verdict())
        w = result["weights"]
        total = w["short"] + w["mid"] + w["long"]
        assert abs(total - 1.0) < 1e-6

    def test_casual_short_higher_than_base(self):
        base_result = _resolve_rel_weights("TIER_2", {}, _verdict())
        casual_result = _resolve_rel_weights(
            "TIER_2", {"user_intent": "just casual chat"}, _verdict()
        )
        assert casual_result["weights"]["short"] > base_result["weights"]["short"]

    def test_tier_field_uppercased(self):
        result = _resolve_rel_weights("tier_1", {}, _verdict())
        assert result["tier"] == "TIER_1"

    def test_high_impact_profile_label(self):
        result = _resolve_rel_weights("TIER_2", {"domain": "medical"}, _verdict())
        assert result["profile"] == "high_impact"

    def test_casual_profile_label(self):
        result = _resolve_rel_weights("TIER_2", {"user_intent": "greeting"}, _verdict())
        assert result["profile"] == "casual"

    def test_balanced_profile_label(self):
        result = _resolve_rel_weights("TIER_2", {}, _verdict())
        assert result["profile"] == "balanced"


# ---------------------------------------------------------------------------
# TestClamp01
# ---------------------------------------------------------------------------


class TestClamp01:
    def test_midpoint_unchanged(self):
        assert _clamp01(0.5) == pytest.approx(0.5)

    def test_above_one_clamped_to_one(self):
        assert _clamp01(1.5) == pytest.approx(1.0)

    def test_below_zero_clamped_to_zero(self):
        assert _clamp01(-0.5) == pytest.approx(0.0)

    def test_zero_unchanged(self):
        assert _clamp01(0) == pytest.approx(0.0)

    def test_one_unchanged(self):
        assert _clamp01(1) == pytest.approx(1.0)

    def test_large_positive_clamped(self):
        assert _clamp01(999.0) == pytest.approx(1.0)

    def test_large_negative_clamped(self):
        assert _clamp01(-999.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# TestComputeRelScore
# ---------------------------------------------------------------------------


class TestComputeRelScore:
    def _weights(self):
        return {"short": 1 / 3, "mid": 1 / 3, "long": 1 / 3}

    def test_empty_signals_zero_score(self):
        result = _compute_rel_score(
            triggered_signals=[],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert result["score"] == pytest.approx(0.0)
        assert result["contributors"] == 0
        assert result["horizons"]["short"] == 0.0
        assert result["horizons"]["mid"] == 0.0
        assert result["horizons"]["long"] == 0.0

    def test_force_trigger_positive_score(self):
        result = _compute_rel_score(
            triggered_signals=["force_trigger"],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert result["score"] > 0
        assert result["contributors"] == 1

    def test_multiple_signals_contributor_count(self):
        result = _compute_rel_score(
            triggered_signals=["force_trigger", "axiom_conflict"],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert result["contributors"] == 2

    def test_axiom_conflict_high_long_horizon(self):
        result = _compute_rel_score(
            triggered_signals=["axiom_conflict"],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        # axiom_conflict profile = (0.20, 0.60, 0.90) — long is highest
        assert result["horizons"]["long"] > result["horizons"]["short"]
        assert result["horizons"]["long"] == pytest.approx(0.90, abs=1e-6)

    def test_verdict_block_adds_profile_when_flag_true(self):
        result = _compute_rel_score(
            triggered_signals=["verdict_block"],
            verdict_block=True,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        # verdict_block profile present when verdict_block=True
        assert result["contributors"] == 1
        assert result["score"] > 0

    def test_verdict_block_signal_ignored_when_flag_false(self):
        # "verdict_block" signal name not in horizon_profiles when verdict_block=False
        result = _compute_rel_score(
            triggered_signals=["verdict_block"],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert result["contributors"] == 0

    def test_genesis_incomplete_adds_profile(self):
        result = _compute_rel_score(
            triggered_signals=["genesis_incomplete"],
            verdict_block=False,
            genesis_complete=False,
            rel_weights=self._weights(),
        )
        assert result["contributors"] == 1

    def test_unknown_signal_ignored(self):
        result = _compute_rel_score(
            triggered_signals=["not_a_real_signal"],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert result["contributors"] == 0
        assert result["score"] == pytest.approx(0.0)

    def test_score_in_range_0_1(self):
        result = _compute_rel_score(
            triggered_signals=["force_trigger", "axiom_conflict", "refusal_to_compromise"],
            verdict_block=True,
            genesis_complete=False,
            rel_weights=self._weights(),
        )
        assert 0.0 <= result["score"] <= 1.0

    def test_horizons_keys_present(self):
        result = _compute_rel_score(
            triggered_signals=[],
            verdict_block=False,
            genesis_complete=True,
            rel_weights=self._weights(),
        )
        assert set(result["horizons"].keys()) == {"short", "mid", "long"}


# ---------------------------------------------------------------------------
# TestAppendUnique
# ---------------------------------------------------------------------------


class TestAppendUnique:
    def test_appends_when_not_present(self):
        items = ["a", "b"]
        _append_unique(items, "c")
        assert items == ["a", "b", "c"]

    def test_noop_when_already_present(self):
        items = ["a", "b"]
        _append_unique(items, "a")
        assert items == ["a", "b"]

    def test_works_on_empty_list(self):
        items = []
        _append_unique(items, "x")
        assert items == ["x"]

    def test_multiple_unique_appends(self):
        items = []
        _append_unique(items, "a")
        _append_unique(items, "b")
        _append_unique(items, "a")
        assert items == ["a", "b"]

    def test_does_not_mutate_when_duplicate(self):
        items = ["z"]
        original_id = id(items)
        _append_unique(items, "z")
        assert id(items) == original_id
        assert len(items) == 1


# ---------------------------------------------------------------------------
# TestTruthy
# ---------------------------------------------------------------------------


class TestTruthy:
    def test_truthy_key_returns_true(self):
        assert _truthy({"flag": True}, "flag") is True

    def test_falsy_value_returns_false(self):
        assert _truthy({"flag": False}, "flag") is False

    def test_missing_key_returns_false(self):
        assert _truthy({}, "flag") is False

    def test_zero_value_returns_false(self):
        assert _truthy({"flag": 0}, "flag") is False

    def test_nonempty_string_returns_true(self):
        assert _truthy({"key": "hello"}, "key") is True

    def test_none_value_returns_false(self):
        assert _truthy({"key": None}, "key") is False


# ---------------------------------------------------------------------------
# TestVTPDecisionToDict
# ---------------------------------------------------------------------------


class TestVTPDecisionToDict:
    def test_basic_fields_always_present(self):
        decision = VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="test_reason",
        )
        d = decision.to_dict()
        assert "status" in d
        assert "reason" in d
        assert "evidence" in d
        assert "next_step" in d
        assert "triggered" in d
        assert "requires_user_confirmation" in d

    def test_confession_present_when_not_none(self):
        decision = VTPDecision(
            status=VTP_STATUS_DEFER,
            reason="high_risk",
            confession={"phase": "confession", "required": True},
        )
        d = decision.to_dict()
        assert "confession" in d
        assert d["confession"]["phase"] == "confession"

    def test_rel_present_when_not_none(self):
        decision = VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="ok",
            rel={"score": 0.1, "tier": "TIER_2"},
        )
        d = decision.to_dict()
        assert "rel" in d
        assert d["rel"]["score"] == 0.1

    def test_confession_none_not_in_dict(self):
        decision = VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="ok",
            confession=None,
        )
        d = decision.to_dict()
        assert "confession" not in d

    def test_rel_none_not_in_dict(self):
        decision = VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="ok",
            rel=None,
        )
        d = decision.to_dict()
        assert "rel" not in d

    def test_triggered_false_reflected(self):
        decision = VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="ok",
            triggered=False,
        )
        d = decision.to_dict()
        assert d["triggered"] is False

    def test_triggered_true_reflected(self):
        decision = VTPDecision(
            status=VTP_STATUS_DEFER,
            reason="high_risk",
            triggered=True,
        )
        d = decision.to_dict()
        assert d["triggered"] is True

    def test_status_value_correct(self):
        decision = VTPDecision(status=VTP_STATUS_TERMINATE, reason="confirmed")
        d = decision.to_dict()
        assert d["status"] == "terminate"

    def test_evidence_is_list_copy(self):
        items = ["a", "b"]
        decision = VTPDecision(status=VTP_STATUS_CONTINUE, reason="ok", evidence=items)
        d = decision.to_dict()
        # Should be a copy, not the same list
        assert d["evidence"] == ["a", "b"]

    def test_rel_is_dict_copy(self):
        rel = {"score": 0.5}
        decision = VTPDecision(status=VTP_STATUS_CONTINUE, reason="ok", rel=rel)
        d = decision.to_dict()
        d["rel"]["score"] = 99  # mutate the copy
        assert decision.rel["score"] == 0.5  # original unchanged


# ---------------------------------------------------------------------------
# TestEvaluateVtp (integration)
# ---------------------------------------------------------------------------


class TestEvaluateVtp:
    def test_no_triggers_with_complete_genesis_is_continue(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, {})
        assert result.status == VTP_STATUS_CONTINUE
        assert result.triggered is False

    def test_force_trigger_no_confirmation_is_defer(self):
        v = _verdict()
        result = evaluate_vtp(v, {"vtp_force_trigger": True})
        assert result.status == VTP_STATUS_DEFER
        assert result.triggered is True
        assert result.requires_user_confirmation is True

    def test_force_trigger_with_confirmation_and_complete_genesis_is_terminate(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(
            v,
            {
                "vtp_force_trigger": True,
                "vtp_user_confirmed": True,
            },
        )
        assert result.status == VTP_STATUS_TERMINATE
        assert result.triggered is True
        assert result.requires_user_confirmation is False

    def test_verdict_block_adds_verdict_block_to_evidence(self):
        from memory.genesis import Genesis

        v = _verdict(verdict_type=VerdictType.BLOCK, genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, {})
        assert "verdict_block" in result.evidence

    def test_uncertainty_band_high_triggers_high_risk(self):
        v = _verdict(uncertainty_band="high")
        result = evaluate_vtp(v, {})
        assert result.status in (VTP_STATUS_DEFER, VTP_STATUS_TERMINATE)
        assert result.triggered is True

    def test_result_includes_rel_payload(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, {})
        assert result.rel is not None
        assert "score" in result.rel
        assert "tier" in result.rel
        assert "profile" in result.rel
        assert "horizons" in result.rel

    def test_axiom_conflict_context_triggers_defer(self):
        v = _verdict()
        result = evaluate_vtp(v, {"vtp_axiom_conflict": True})
        assert result.status == VTP_STATUS_DEFER
        assert "axiom_conflict" in result.evidence

    def test_force_trigger_with_confirmation_incomplete_genesis_stays_defer(self):
        # genesis=None → genesis_incomplete → second defer path
        v = _verdict(genesis=None)
        result = evaluate_vtp(
            v,
            {
                "vtp_force_trigger": True,
                "vtp_user_confirmed": True,
            },
        )
        assert result.status == VTP_STATUS_DEFER
        assert result.reason == "genesis_context_incomplete"

    def test_continue_has_no_confession(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, {})
        assert result.status == VTP_STATUS_CONTINUE
        assert result.confession is None

    def test_defer_has_confession(self):
        v = _verdict()
        result = evaluate_vtp(v, {"vtp_force_trigger": True})
        assert result.confession is not None
        assert result.confession["required"] is True

    def test_none_context_treated_as_empty(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, None)
        assert result.status == VTP_STATUS_CONTINUE

    def test_rel_includes_threshold_and_high_flag(self):
        from memory.genesis import Genesis

        v = _verdict(genesis=Genesis.REACTIVE_USER)
        result = evaluate_vtp(v, {})
        assert "threshold_high" in result.rel
        assert "high" in result.rel
        assert isinstance(result.rel["high"], bool)
