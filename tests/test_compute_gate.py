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
