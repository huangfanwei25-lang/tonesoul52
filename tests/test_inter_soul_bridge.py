from __future__ import annotations

from tonesoul.inter_soul.bridge import LocalInterSoulBridge
from tonesoul.inter_soul.types import RuptureNotice, SovereigntyBoundary, TensionPacket


def _packet(
    soul_id: str,
    *,
    total: float,
    zone: str = "transit",
    lambda_state: str = "coherent",
    semantic_delta: float = 0.2,
    cognitive_friction: float = 0.1,
) -> TensionPacket:
    return TensionPacket(
        soul_id=soul_id,
        timestamp="2026-03-20T12:00:00Z",
        total=total,
        zone=zone,
        lambda_state=lambda_state,
        signals={
            "semantic_delta": semantic_delta,
            "cognitive_friction": cognitive_friction,
            "persistence_score": 0.4,
            "resistance": 0.2,
        },
    )


def test_local_bridge_share_receive_is_fifo_and_preserves_history() -> None:
    bridge = LocalInterSoulBridge()
    first = _packet("alpha", total=0.32)
    second = _packet("beta", total=0.61)

    bridge.share_tension(first)
    bridge.share_tension(second)

    assert bridge.receive_tension().soul_id == "alpha"
    assert bridge.receive_tension().soul_id == "beta"
    assert bridge.receive_tension() is None
    assert [packet.soul_id for packet in bridge.tension_history] == ["alpha", "beta"]


def test_local_bridge_propagates_rupture_notice_without_erasing_it() -> None:
    bridge = LocalInterSoulBridge()
    notice = RuptureNotice(
        source_soul_id="alpha",
        rupture_type="direct_negation",
        severity="significant",
        context_excerpt="The two souls now disagree in public.",
        timestamp="2026-03-20T12:10:00Z",
    )

    bridge.propagate_rupture(notice)

    assert len(bridge.rupture_history) == 1
    assert bridge.rupture_history[0].rupture_type == "direct_negation"


def test_local_bridge_negotiate_returns_aligned_for_nearby_packets() -> None:
    bridge = LocalInterSoulBridge()
    boundary = SovereigntyBoundary(frozenset({"zone", "lambda_state"}), frozenset({"3", "6"}))

    outcome = bridge.negotiate(
        _packet("alpha", total=0.42, semantic_delta=0.2),
        _packet("beta", total=0.45, semantic_delta=0.22),
        boundary,
    )

    assert outcome.value == "aligned"


def test_local_bridge_negotiate_returns_sovereign_override_for_protected_mismatch() -> None:
    bridge = LocalInterSoulBridge()
    boundary = SovereigntyBoundary(frozenset({"zone"}), frozenset({"3"}))

    outcome = bridge.negotiate(
        _packet("alpha", total=0.42, zone="safe"),
        _packet("beta", total=0.42, zone="risk"),
        boundary,
    )

    assert outcome.value == "sovereign_override"
