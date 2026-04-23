from __future__ import annotations

from tonesoul.inter_soul.negotiation import (
    NegotiationResult,
    TensionNegotiator,
    _resolve_field,
)
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


# ── _resolve_field ────────────────────────────────────────────────────────────

def test_resolve_field_reads_top_level_attribute() -> None:
    packet = _packet(total=0.5, zone="safe")
    assert _resolve_field(packet, "zone") == "safe"
    assert _resolve_field(packet, "total") == 0.5


def test_resolve_field_reads_signals_subkey() -> None:
    packet = _packet(total=0.5, semantic_delta=0.77)
    assert _resolve_field(packet, "signals.semantic_delta") == 0.77


def test_resolve_field_returns_none_for_missing_attribute() -> None:
    packet = _packet(total=0.5)
    assert _resolve_field(packet, "nonexistent_field") is None


def test_resolve_field_returns_none_for_missing_signal_key() -> None:
    packet = _packet(total=0.5)
    assert _resolve_field(packet, "signals.nonexistent_signal") is None


# ── _compute_divergence_score and _compute_signal_gap ─────────────────────────

def test_compute_divergence_score_identical_packets_returns_zero() -> None:
    packet = _packet(total=0.5, zone="safe", lambda_state="coherent", semantic_delta=0.3)
    score = TensionNegotiator._compute_divergence_score(packet, packet)
    assert score == 0.0


def test_compute_divergence_score_different_zone_adds_penalty() -> None:
    p1 = _packet(total=0.5, zone="safe", lambda_state="coherent")
    p2 = _packet(total=0.5, zone="risk", lambda_state="coherent")
    score = TensionNegotiator._compute_divergence_score(p1, p2)
    # zone_gap=0.25, contribution = 0.10 * 0.25 = 0.025
    assert score > 0.0


def test_compute_signal_gap_empty_signals_returns_zero() -> None:
    p1 = TensionPacket(soul_id="s", timestamp="t", total=0.5, zone="z",
                       lambda_state="l", signals={})
    p2 = TensionPacket(soul_id="s", timestamp="t", total=0.5, zone="z",
                       lambda_state="l", signals={})
    assert TensionNegotiator._compute_signal_gap(p1, p2) == 0.0


def test_compute_signal_gap_missing_key_in_one_packet_uses_zero() -> None:
    p1 = TensionPacket(soul_id="s", timestamp="t", total=0.5, zone="z",
                       lambda_state="l", signals={"x": 0.8})
    p2 = TensionPacket(soul_id="s", timestamp="t", total=0.5, zone="z",
                       lambda_state="l", signals={})
    gap = TensionNegotiator._compute_signal_gap(p1, p2)
    assert gap == 0.8  # (0.8 - 0.0) / 1


# ── sovereign override on lambda_state ───────────────────────────────────────

def test_negotiator_sovereign_override_on_lambda_state_difference() -> None:
    negotiator = TensionNegotiator(
        SovereigntyBoundary(frozenset({"lambda_state"}), frozenset())
    )
    result = negotiator.negotiate(
        _packet(total=0.5, lambda_state="coherent"),
        _packet(total=0.5, lambda_state="fragmented"),
    )
    assert result.outcome is NegotiationOutcome.SOVEREIGN_OVERRIDE
    assert "lambda_state" in result.explanation


def test_negotiator_no_override_when_boundary_fields_match() -> None:
    negotiator = TensionNegotiator(
        SovereigntyBoundary(frozenset({"zone", "lambda_state"}), frozenset())
    )
    result = negotiator.negotiate(
        _packet(total=0.5, zone="safe", lambda_state="coherent"),
        _packet(total=0.5, zone="safe", lambda_state="coherent"),
    )
    # Same boundary fields, so no sovereign override — outcome depends on divergence
    assert result.outcome is not NegotiationOutcome.SOVEREIGN_OVERRIDE
