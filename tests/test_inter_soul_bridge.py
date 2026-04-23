from __future__ import annotations

from tonesoul.inter_soul.bridge import LocalInterSoulBridge, _clone_notice, _clone_packet
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


# ── _clone_packet isolation ───────────────────────────────────────────────────

def test_clone_packet_produces_independent_copy() -> None:
    original = _packet("alpha", total=0.5)
    clone = _clone_packet(original)

    assert clone.soul_id == original.soul_id
    assert clone is not original
    assert clone.signals is not original.signals


def test_clone_notice_produces_independent_copy() -> None:
    original = RuptureNotice(
        source_soul_id="alpha",
        rupture_type="inversion",
        severity="mild",
        context_excerpt="context here",
        timestamp="2026-04-01T00:00:00Z",
    )
    clone = _clone_notice(original)

    assert clone.source_soul_id == original.source_soul_id
    assert clone is not original


# ── tension_history / rupture_history return copies ──────────────────────────

def test_tension_history_returns_independent_copies() -> None:
    bridge = LocalInterSoulBridge()
    packet = _packet("alpha", total=0.4)
    bridge.share_tension(packet)

    history = bridge.tension_history
    assert len(history) == 1
    assert history[0] is not bridge._tension_history[0]


def test_rupture_history_returns_independent_copies() -> None:
    bridge = LocalInterSoulBridge()
    notice = RuptureNotice(
        source_soul_id="alpha",
        rupture_type="direct_negation",
        severity="significant",
        context_excerpt="excerpt",
        timestamp="2026-04-01T00:00:00Z",
    )
    bridge.propagate_rupture(notice)

    history = bridge.rupture_history
    assert len(history) == 1
    assert history[0] is not bridge._rupture_history[0]


def test_multiple_ruptures_all_stored() -> None:
    bridge = LocalInterSoulBridge()
    for i in range(3):
        bridge.propagate_rupture(RuptureNotice(
            source_soul_id=f"soul_{i}",
            rupture_type="inversion",
            severity="mild",
            context_excerpt="ctx",
            timestamp="2026-04-01T00:00:00Z",
        ))

    assert len(bridge.rupture_history) == 3
    ids = [n.source_soul_id for n in bridge.rupture_history]
    assert ids == ["soul_0", "soul_1", "soul_2"]


def test_share_tension_keeps_copy_in_history_after_receive() -> None:
    bridge = LocalInterSoulBridge()
    bridge.share_tension(_packet("alpha", total=0.3))

    received = bridge.receive_tension()
    assert received is not None
    assert len(bridge.tension_history) == 1  # history persists after receive
