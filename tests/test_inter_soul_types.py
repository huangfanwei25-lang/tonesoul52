from __future__ import annotations

import pytest

from tonesoul.inter_soul.types import (
    NegotiationOutcome,
    RuptureNotice,
    SovereigntyBoundary,
    TensionPacket,
    _clamp_unit,
    _normalize_signals,
    _utcnow_iso,
)

# ── _utcnow_iso ───────────────────────────────────────────────────────────────


class TestUtcnowIso:
    def test_returns_string(self):
        assert isinstance(_utcnow_iso(), str)

    def test_ends_with_z(self):
        assert _utcnow_iso().endswith("Z")


# ── _clamp_unit ───────────────────────────────────────────────────────────────


class TestClampUnit:
    def test_normal_value(self):
        assert _clamp_unit(0.5) == pytest.approx(0.5)

    def test_clamps_above_one(self):
        assert _clamp_unit(1.5) == pytest.approx(1.0)

    def test_clamps_below_zero(self):
        assert _clamp_unit(-0.5) == pytest.approx(0.0)

    def test_none_returns_zero(self):
        assert _clamp_unit(None) == pytest.approx(0.0)

    def test_string_numeric(self):
        assert _clamp_unit("0.7") == pytest.approx(0.7)


# ── _normalize_signals ────────────────────────────────────────────────────────


class TestNormalizeSignals:
    def test_numeric_values_kept(self):
        result = _normalize_signals({"tension": 0.5, "drift": 0.3})
        assert result["tension"] == pytest.approx(0.5)

    def test_non_numeric_filtered(self):
        result = _normalize_signals({"a": "bad", "b": 0.4})
        assert "a" not in result
        assert result["b"] == pytest.approx(0.4)

    def test_none_returns_empty(self):
        assert _normalize_signals(None) == {}

    def test_non_mapping_returns_empty(self):
        assert _normalize_signals([1, 2]) == {}

    def test_bool_converted(self):
        result = _normalize_signals({"active": True})
        assert result["active"] == pytest.approx(1.0)


def _packet() -> TensionPacket:
    return TensionPacket(
        soul_id="alpha",
        timestamp="2026-03-20T12:00:00Z",
        total=0.42,
        zone="transit",
        lambda_state="coherent",
        signals={
            "semantic_delta": 0.2,
            "cognitive_friction": 0.1,
            "persistence_score": 0.4,
            "resistance": 0.3,
        },
    )


def test_tension_packet_round_trip_preserves_core_fields() -> None:
    packet = _packet()

    restored = TensionPacket.from_dict(packet.to_dict())

    assert restored == packet


def test_tension_packet_hmac_signature_can_be_verified() -> None:
    packet = _packet()

    signature = packet.sign("shared-secret")

    assert signature == packet.signature
    assert packet.verify_signature("shared-secret") is True
    assert packet.verify_signature("wrong-secret") is False


def test_tension_packet_verification_rejects_tampered_payload() -> None:
    packet = _packet()
    packet.sign("shared-secret")

    packet.total = 0.91

    assert packet.verify_signature("shared-secret") is False


def test_rupture_notice_and_boundary_serialize_for_audit_surfaces() -> None:
    notice = RuptureNotice(
        source_soul_id="beta",
        rupture_type="value_conflict",
        severity="critical",
        context_excerpt="We refuse to erase the conflict.",
        timestamp="2026-03-20T12:05:00Z",
    )
    boundary = SovereigntyBoundary(
        non_negotiable_fields=frozenset({"zone", "lambda_state"}),
        axiom_ids=frozenset({"3", "6"}),
    )

    assert notice.to_dict()["rupture_type"] == "value_conflict"
    assert boundary.to_dict() == {
        "non_negotiable_fields": ["lambda_state", "zone"],
        "axiom_ids": ["3", "6"],
    }
    assert SovereigntyBoundary.from_dict(boundary.to_dict()) == boundary


def test_negotiation_outcome_values_are_stable() -> None:
    assert NegotiationOutcome.ALIGNED.value == "aligned"
    assert NegotiationOutcome.DIVERGENT.value == "divergent"
    assert NegotiationOutcome.SOVEREIGN_OVERRIDE.value == "sovereign_override"
