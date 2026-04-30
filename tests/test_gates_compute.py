"""Tests for tonesoul.gates.compute — pure helpers and ComputeGate/RateLimiter."""

from __future__ import annotations

import pytest

from tonesoul.gates.compute import (
    ComputeGate,
    GovernanceDepth,
    GovernanceDepthPlan,
    RateLimiter,
    RoutingPath,
    _free_tier_limiter,
)

# ── RoutingPath / GovernanceDepth enums ───────────────────────────────────────


class TestEnums:
    def test_routing_path_values(self):
        assert RoutingPath.PASS_LOCAL.value == "route_local_llm"
        assert RoutingPath.PASS_SINGLE.value == "route_single_cloud"
        assert RoutingPath.PASS_COUNCIL.value == "route_full_council"
        assert RoutingPath.BLOCK_RATE_LIMIT.value == "block_rate_limit"

    def test_governance_depth_values(self):
        assert GovernanceDepth.LIGHT.value == "light"
        assert GovernanceDepth.STANDARD.value == "standard"
        assert GovernanceDepth.FULL.value == "full"


# ── GovernanceDepthPlan.to_dict ────────────────────────────────────────────────


class TestGovernanceDepthPlan:
    def test_default_to_dict(self):
        plan = GovernanceDepthPlan()
        d = plan.to_dict()
        assert d["depth"] == "standard"
        assert d["preserve_default_behavior"] is True
        assert isinstance(d["candidate_light_skips"], list)
        assert isinstance(d["required_edges"], list)

    def test_custom_plan(self):
        plan = GovernanceDepthPlan(
            depth="light",
            skip_cross_session_recovery=True,
            candidate_light_skips=("foo", "bar"),
        )
        d = plan.to_dict()
        assert d["depth"] == "light"
        assert d["skip_cross_session_recovery"] is True
        assert "foo" in d["candidate_light_skips"]

    def test_required_edges_default(self):
        plan = GovernanceDepthPlan()
        d = plan.to_dict()
        assert "reflex_arc" in d["required_edges"]
        assert "basic_output_honesty" in d["required_edges"]


# ── RateLimiter ────────────────────────────────────────────────────────────────


class TestRateLimiter:
    def test_consume_returns_true_when_tokens_available(self):
        limiter = RateLimiter(capacity=5.0, refill_rate=1.0)
        assert limiter.consume("user1") is True

    def test_consume_exhausted_returns_false(self):
        limiter = RateLimiter(capacity=2.0, refill_rate=0.0)
        limiter.consume("u", 2.0)
        assert limiter.consume("u") is False

    def test_reset_clears_all_buckets(self):
        limiter = RateLimiter(capacity=1.0, refill_rate=0.0)
        limiter.consume("u1")
        limiter.consume("u2")
        limiter.reset()
        assert limiter.buckets == {}

    def test_different_keys_independent(self):
        limiter = RateLimiter(capacity=1.0, refill_rate=0.0)
        limiter.consume("a", 1.0)
        assert limiter.consume("b") is True

    def test_partial_consume(self):
        limiter = RateLimiter(capacity=5.0, refill_rate=0.0)
        assert limiter.consume("u", 3.0) is True
        assert limiter.consume("u", 3.0) is False  # Only 2 left


# ── ComputeGate._classify_risk_level ──────────────────────────────────────────


class TestClassifyRiskLevel:
    def test_low_below_0_4(self):
        assert ComputeGate._classify_risk_level(0.3) == "low"

    def test_medium_at_0_4(self):
        assert ComputeGate._classify_risk_level(0.4) == "medium"

    def test_medium_between_0_4_and_0_8(self):
        assert ComputeGate._classify_risk_level(0.6) == "medium"

    def test_high_at_0_8(self):
        assert ComputeGate._classify_risk_level(0.8) == "high"

    def test_high_above_0_8(self):
        assert ComputeGate._classify_risk_level(0.95) == "high"

    def test_zero_is_low(self):
        assert ComputeGate._classify_risk_level(0.0) == "low"


# ── ComputeGate._clamp_unit ────────────────────────────────────────────────────


class TestClampUnit:
    def test_normal_value_unchanged(self):
        assert ComputeGate._clamp_unit(0.5) == pytest.approx(0.5)

    def test_above_one_clamped(self):
        assert ComputeGate._clamp_unit(1.5) == pytest.approx(1.0)

    def test_below_zero_clamped(self):
        assert ComputeGate._clamp_unit(-0.3) == pytest.approx(0.0)

    def test_zero(self):
        assert ComputeGate._clamp_unit(0.0) == pytest.approx(0.0)

    def test_one(self):
        assert ComputeGate._clamp_unit(1.0) == pytest.approx(1.0)


# ── ComputeGate._mean_wave_delta ───────────────────────────────────────────────


class TestMeanWaveDelta:
    def test_none_inputs_return_none(self):
        assert ComputeGate._mean_wave_delta(None, None) is None

    def test_non_dict_query_returns_none(self):
        assert ComputeGate._mean_wave_delta("x", {"a": 1.0}) is None

    def test_non_dict_memory_returns_none(self):
        assert ComputeGate._mean_wave_delta({"a": 1.0}, "x") is None

    def test_no_shared_keys_returns_none(self):
        assert ComputeGate._mean_wave_delta({"a": 1.0}, {"b": 2.0}) is None

    def test_identical_waves_returns_zero(self):
        result = ComputeGate._mean_wave_delta({"x": 0.5}, {"x": 0.5})
        assert result == pytest.approx(0.0)

    def test_delta_computed(self):
        result = ComputeGate._mean_wave_delta({"x": 0.8}, {"x": 0.2})
        assert result == pytest.approx(0.6)

    def test_clamped_to_one(self):
        result = ComputeGate._mean_wave_delta({"x": 2.0}, {"x": 0.0})
        assert result == pytest.approx(1.0)

    def test_non_numeric_values_skipped(self):
        result = ComputeGate._mean_wave_delta({"a": "str", "b": 0.5}, {"a": "str", "b": 0.0})
        assert result == pytest.approx(0.5)


# ── ComputeGate.compute_governance_friction ───────────────────────────────────


class TestComputeGovernanceFriction:
    def test_none_tensions_no_wave_no_boundary_returns_none(self):
        result = ComputeGate.compute_governance_friction(
            query_tension=None,
            memory_tension=None,
        )
        assert result is None

    def test_boundary_mismatch_only(self):
        result = ComputeGate.compute_governance_friction(
            query_tension=None,
            memory_tension=None,
            boundary_mismatch=True,
        )
        assert result == pytest.approx(0.20, abs=1e-4)

    def test_same_tension_no_wave_no_mismatch(self):
        result = ComputeGate.compute_governance_friction(
            query_tension=0.5,
            memory_tension=0.5,
        )
        assert result == pytest.approx(0.0, abs=1e-4)

    def test_friction_formula(self):
        # delta_t = 0.3, delta_wave = 0.0, mismatch = 0
        result = ComputeGate.compute_governance_friction(
            query_tension=0.7,
            memory_tension=0.4,
        )
        expected = round(0.45 * 0.3, 4)
        assert result == pytest.approx(expected, abs=1e-4)

    def test_boundary_mismatch_adds_0_2(self):
        result_no = ComputeGate.compute_governance_friction(
            query_tension=0.5,
            memory_tension=0.5,
            boundary_mismatch=False,
        )
        result_yes = ComputeGate.compute_governance_friction(
            query_tension=0.5,
            memory_tension=0.5,
            boundary_mismatch=True,
        )
        assert result_yes - result_no == pytest.approx(0.20, abs=1e-4)

    def test_clamped_to_one(self):
        result = ComputeGate.compute_governance_friction(
            query_tension=1.0,
            memory_tension=0.0,
            boundary_mismatch=True,
        )
        assert result <= 1.0


# ── ComputeGate.evaluate ──────────────────────────────────────────────────────


class TestComputeGateEvaluate:
    def setup_method(self):
        _free_tier_limiter.reset()
        self.gate = ComputeGate(local_model_enabled=True)

    def test_short_message_routes_local(self):
        decision = self.gate.evaluate("free", "hi", initial_tension=0.0, user_id="u1")
        assert decision.path == RoutingPath.PASS_LOCAL
        assert decision.journal_eligible is False

    def test_short_message_local_disabled_goes_free(self):
        gate = ComputeGate(local_model_enabled=False)
        _free_tier_limiter.reset()
        decision = gate.evaluate("free", "hi", initial_tension=0.0, user_id="u2")
        # Without local enabled, short low-tension message from free tier uses PASS_SINGLE
        assert decision.path == RoutingPath.PASS_SINGLE

    def test_premium_low_tension_single(self):
        decision = self.gate.evaluate(
            "premium",
            "What is the capital of France?",
            initial_tension=0.1,
            user_id="premium-user",
        )
        assert decision.path == RoutingPath.PASS_SINGLE
        assert decision.journal_eligible is True

    def test_high_tension_routes_council(self):
        decision = self.gate.evaluate(
            "premium",
            "This is a philosophically complex question about ethics and meaning",
            initial_tension=0.9,
            user_id="premium-user",
        )
        assert decision.path == RoutingPath.PASS_COUNCIL

    def test_free_tier_rate_limited(self):
        _free_tier_limiter.reset()
        gate = ComputeGate(local_model_enabled=False)
        msg = "This is a long enough message to bypass the local route threshold"
        # Exhaust the free tier bucket (capacity=5)
        for _ in range(5):
            gate.evaluate("free", msg, initial_tension=0.0, user_id="spammer")
        decision = gate.evaluate("free", msg, initial_tension=0.0, user_id="spammer")
        assert decision.path == RoutingPath.BLOCK_RATE_LIMIT

    def test_free_tier_below_critical_gets_single(self):
        _free_tier_limiter.reset()
        decision = self.gate.evaluate(
            "free",
            "This is a long enough message to avoid local routing path here",
            initial_tension=0.3,
            user_id="free-user",
        )
        assert decision.path == RoutingPath.PASS_SINGLE

    def test_admin_journal_eligible(self):
        decision = self.gate.evaluate(
            "admin",
            "This is a long administrative query for management",
            initial_tension=0.1,
        )
        assert decision.journal_eligible is True

    def test_governance_depth_local_is_light(self):
        decision = self.gate.evaluate("free", "hi", initial_tension=0.0, user_id="u3")
        assert decision.governance_depth == "light"

    def test_governance_depth_council_is_full(self):
        decision = self.gate.evaluate(
            "premium", "long complex ethical question", initial_tension=0.9
        )
        assert decision.governance_depth == "full"

    def test_friction_score_used_as_effective_tension(self):
        # Low initial tension but high friction should route to council
        decision = self.gate.evaluate(
            "premium",
            "normal looking question that has high friction",
            initial_tension=0.1,
            friction_score=0.7,
        )
        assert decision.path == RoutingPath.PASS_COUNCIL

    def test_risk_level_in_decision(self):
        decision = self.gate.evaluate(
            "premium",
            "long high-tension message about dangerous things",
            initial_tension=0.9,
        )
        assert decision.risk_level == "high"

    def test_governance_depth_plan_in_decision(self):
        decision = self.gate.evaluate(
            "premium", "standard question of moderate length", initial_tension=0.2
        )
        assert isinstance(decision.governance_depth_plan, GovernanceDepthPlan)
