from __future__ import annotations

from tonesoul.inter_soul.negotiation import NegotiationResult, TensionNegotiator
from tonesoul.inter_soul.types import NegotiationOutcome, SovereigntyBoundary, TensionPacket


def _packet(
    *,
    total: float,
    zone: str = "transit",
    lambda_state: str = "coherent",
    semantic_delta: float = 0.2,
    cognitive_friction: float = 0.1,
    persistence_score: float = 0.4,
) -> TensionPacket:
    return TensionPacket(
        soul_id="soul",
        timestamp="2026-03-20T12:00:00Z",
        total=total,
        zone=zone,
        lambda_state=lambda_state,
        signals={
            "semantic_delta": semantic_delta,
            "cognitive_friction": cognitive_friction,
            "persistence_score": persistence_score,
            "resistance": 0.3,
        },
    )


def test_negotiator_returns_aligned_below_threshold() -> None:
    negotiator = TensionNegotiator(
        SovereigntyBoundary(frozenset({"zone", "lambda_state"}), frozenset({"3", "6"}))
    )

    result = negotiator.negotiate(
        _packet(total=0.42, semantic_delta=0.2, cognitive_friction=0.1),
        _packet(total=0.45, semantic_delta=0.22, cognitive_friction=0.11),
    )

    assert result.outcome is NegotiationOutcome.ALIGNED
    assert result.divergence_score < 0.3


def test_negotiator_preserves_visible_divergence_instead_of_erasing_it() -> None:
    negotiator = TensionNegotiator(
        SovereigntyBoundary(frozenset({"zone", "lambda_state"}), frozenset({"3", "6"}))
    )

    result = negotiator.negotiate(
        _packet(total=0.15, semantic_delta=0.1, cognitive_friction=0.05, persistence_score=0.1),
        _packet(total=0.88, semantic_delta=0.8, cognitive_friction=0.75, persistence_score=0.9),
    )

    assert result.outcome is NegotiationOutcome.DIVERGENT
    assert result.divergence_score >= 0.3
    assert "Visible divergence is preserved" in result.explanation


def test_negotiator_returns_sovereign_override_when_boundary_field_differs() -> None:
    negotiator = TensionNegotiator(SovereigntyBoundary(frozenset({"zone"}), frozenset({"3"})))

    result = negotiator.negotiate(
        _packet(total=0.5, zone="safe"),
        _packet(total=0.5, zone="risk"),
    )

    assert result.outcome is NegotiationOutcome.SOVEREIGN_OVERRIDE
    assert result.divergence_score == 1.0
    assert "zone" in result.explanation


def test_negotiation_result_to_dict_exports_public_contract() -> None:
    result = NegotiationResult(
        outcome=NegotiationOutcome.DIVERGENT,
        divergence_score=0.45678,
        explanation="Visible divergence is preserved.",
    )

    assert result.to_dict() == {
        "outcome": "divergent",
        "divergence_score": 0.4568,
        "explanation": "Visible divergence is preserved.",
    }
