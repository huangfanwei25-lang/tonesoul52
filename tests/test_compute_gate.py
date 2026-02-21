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
