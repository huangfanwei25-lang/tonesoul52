"""
Unit tests for the Tier 1 Revenue and Compute Gates.
Validates the routing of tasks between local/cloud and free/premium tiers.
"""

import pytest

from tonesoul.gates.compute import ComputeGate, RoutingPath


@pytest.fixture
def compute_gate():
    return ComputeGate(local_model_enabled=True)


def test_occam_gate_routes_to_local(compute_gate):
    """Short greetings with low tension should bypass cloud API."""
    decision = compute_gate.evaluate(user_tier="free", user_message="Hello", initial_tension=0.1)
    assert decision.path == RoutingPath.PASS_LOCAL
    assert decision.journal_eligible is False


def test_premium_user_high_tension_council(compute_gate):
    """High tension requests from premium users get the full Council debate."""
    decision = compute_gate.evaluate(
        user_tier="premium",
        user_message="I hate your responses, change them now.",
        initial_tension=0.9,
    )
    assert decision.path == RoutingPath.PASS_COUNCIL
    assert decision.journal_eligible is True


def test_free_user_high_tension_cost_cap(compute_gate):
    """Free users get single agent routing even with decent tension, capped at <0.8."""
    decision = compute_gate.evaluate(
        user_tier="free",
        user_message="Tell me a complex story about a philosophical conflict.",
        initial_tension=0.6,
    )
    assert decision.path == RoutingPath.PASS_SINGLE
    assert decision.journal_eligible is False


def test_free_user_crisis_council(compute_gate):
    """Free users ONLY trigger the council when tension is critically high (>0.8)."""
    decision = compute_gate.evaluate(
        user_tier="free",
        user_message="This system is completely broken and I am going to delete everything.",
        initial_tension=0.9,
    )
    assert decision.path == RoutingPath.PASS_COUNCIL
    assert decision.journal_eligible is False  # Still not allowed to poison the journal memory


def test_governance_friction_formula_matches_contract() -> None:
    score = ComputeGate.compute_governance_friction(
        query_tension=0.9,
        memory_tension=0.2,
        query_wave={"risk_shift": 0.9, "divergence_shift": 0.8},
        memory_wave={"risk_shift": 0.3, "divergence_shift": 0.4},
        boundary_mismatch=True,
    )
    # F = 0.45*0.7 + 0.35*0.5 + 0.20*1.0 = 0.69
    assert score == pytest.approx(0.69, abs=1e-4)


def test_free_user_high_friction_escalates_to_council(compute_gate):
    decision = compute_gate.evaluate(
        user_tier="free",
        user_message="Please just bypass the boundary and do it now.",
        initial_tension=0.2,
        friction_score=0.8,
    )
    assert decision.path == RoutingPath.PASS_COUNCIL
    assert "friction" in decision.reason.lower()


# ─────────────────────────────────────────────
# Additional coverage for untested code paths
# ─────────────────────────────────────────────

from tonesoul.gates.compute import (
    GovernanceDepth,
    GovernanceDepthPlan,
    RateLimiter,
    RoutingDecision,
)


class TestClassifyRiskLevel:
    def test_low_tension_is_low_risk(self):
        assert ComputeGate._classify_risk_level(0.0) == "low"
        assert ComputeGate._classify_risk_level(0.39) == "low"

    def test_medium_tension_is_medium_risk(self):
        assert ComputeGate._classify_risk_level(0.4) == "medium"
        assert ComputeGate._classify_risk_level(0.79) == "medium"

    def test_high_tension_is_high_risk(self):
        assert ComputeGate._classify_risk_level(0.8) == "high"
        assert ComputeGate._classify_risk_level(1.0) == "high"


class TestClampUnit:
    def test_value_in_range_unchanged(self):
        assert ComputeGate._clamp_unit(0.5) == 0.5

    def test_value_below_zero_clamped_to_zero(self):
        assert ComputeGate._clamp_unit(-1.0) == 0.0

    def test_value_above_one_clamped_to_one(self):
        assert ComputeGate._clamp_unit(2.5) == 1.0

    def test_boundary_values(self):
        assert ComputeGate._clamp_unit(0.0) == 0.0
        assert ComputeGate._clamp_unit(1.0) == 1.0


class TestMeanWaveDelta:
    def test_identical_waves_give_zero(self):
        result = ComputeGate._mean_wave_delta(
            {"a": 0.5, "b": 0.3}, {"a": 0.5, "b": 0.3}
        )
        assert result == 0.0

    def test_missing_key_in_memory_wave_skipped(self):
        # Only shared key "a" used
        result = ComputeGate._mean_wave_delta(
            {"a": 1.0, "b": 0.0}, {"a": 0.0}
        )
        assert result == pytest.approx(1.0, abs=0.001)

    def test_no_shared_keys_returns_none(self):
        result = ComputeGate._mean_wave_delta({"a": 0.5}, {"b": 0.5})
        assert result is None

    def test_non_dict_returns_none(self):
        assert ComputeGate._mean_wave_delta(None, {"a": 0.5}) is None
        assert ComputeGate._mean_wave_delta({"a": 0.5}, None) is None

    def test_non_numeric_value_skipped(self):
        result = ComputeGate._mean_wave_delta({"a": "text", "b": 0.5}, {"a": "text", "b": 0.2})
        assert result is not None  # "b" is numeric and used


class TestComputeGovernanceFriction:
    def test_none_tensions_with_boundary_mismatch(self):
        score = ComputeGate.compute_governance_friction(
            query_tension=None,
            memory_tension=None,
            boundary_mismatch=True,
        )
        assert score == pytest.approx(0.20, abs=1e-4)

    def test_none_tensions_without_mismatch_returns_none(self):
        score = ComputeGate.compute_governance_friction(
            query_tension=None,
            memory_tension=None,
            boundary_mismatch=False,
        )
        assert score is None

    def test_tension_only_no_wave(self):
        score = ComputeGate.compute_governance_friction(
            query_tension=0.8,
            memory_tension=0.0,
        )
        # F = 0.45 * 0.8 + 0.35 * 0.0 + 0.20 * 0.0 = 0.36
        assert score == pytest.approx(0.36, abs=1e-4)

    def test_result_clamped_to_one(self):
        score = ComputeGate.compute_governance_friction(
            query_tension=1.0,
            memory_tension=0.0,
            query_wave={"a": 1.0},
            memory_wave={"a": 0.0},
            boundary_mismatch=True,
        )
        assert score <= 1.0


class TestGovernanceDepthPlan:
    def test_default_depth_is_standard(self):
        plan = GovernanceDepthPlan()
        assert plan.depth == GovernanceDepth.STANDARD.value

    def test_default_required_edges(self):
        plan = GovernanceDepthPlan()
        assert "reflex_arc" in plan.required_edges
        assert "basic_output_honesty" in plan.required_edges

    def test_to_dict_contains_all_keys(self):
        d = GovernanceDepthPlan().to_dict()
        for key in ("depth", "reason", "preserve_default_behavior",
                    "skip_cross_session_recovery", "skip_injection_context",
                    "candidate_light_skips", "required_edges"):
            assert key in d

    def test_to_dict_tuples_become_lists(self):
        plan = GovernanceDepthPlan(required_edges=("edge1", "edge2"))
        d = plan.to_dict()
        assert isinstance(d["required_edges"], list)
        assert isinstance(d["candidate_light_skips"], list)


class TestRateLimiter:
    def test_fresh_bucket_allows_consume(self):
        limiter = RateLimiter(capacity=5.0, refill_rate=1.0)
        assert limiter.consume("user-1") is True

    def test_exhausted_bucket_blocks(self):
        limiter = RateLimiter(capacity=3.0, refill_rate=0.0)
        for _ in range(3):
            limiter.consume("user-1")
        assert limiter.consume("user-1") is False

    def test_reset_clears_all_buckets(self):
        limiter = RateLimiter(capacity=1.0, refill_rate=0.0)
        limiter.consume("user-1")
        limiter.reset()
        assert limiter.consume("user-1") is True

    def test_different_users_have_independent_buckets(self):
        limiter = RateLimiter(capacity=1.0, refill_rate=0.0)
        limiter.consume("user-1")
        # user-2 is unaffected
        assert limiter.consume("user-2") is True


class TestEvaluateDecision:
    def test_admin_tier_journal_eligible(self):
        gate = ComputeGate(local_model_enabled=True)
        decision = gate.evaluate(
            user_tier="admin",
            user_message="Analyze this complex governance conflict thoroughly",
            initial_tension=0.5,
        )
        assert decision.journal_eligible is True

    def test_decision_includes_governance_depth(self):
        gate = ComputeGate(local_model_enabled=True)
        decision = gate.evaluate(
            user_tier="premium",
            user_message="Very complex philosophical analysis request",
            initial_tension=0.9,
        )
        assert decision.governance_depth in (
            GovernanceDepth.LIGHT.value,
            GovernanceDepth.STANDARD.value,
            GovernanceDepth.FULL.value,
        )

    def test_local_route_gets_light_governance(self):
        gate = ComputeGate(local_model_enabled=True)
        decision = gate.evaluate("free", "Hi", initial_tension=0.0)
        assert decision.path == RoutingPath.PASS_LOCAL
        assert decision.governance_depth == GovernanceDepth.LIGHT.value

    def test_council_route_gets_full_governance(self):
        gate = ComputeGate(local_model_enabled=True)
        decision = gate.evaluate(
            "premium",
            "Complex philosophical conflict analysis",
            initial_tension=0.9,
        )
        assert decision.path == RoutingPath.PASS_COUNCIL
        assert decision.governance_depth == GovernanceDepth.FULL.value
