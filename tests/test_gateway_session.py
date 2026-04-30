"""Tests for tonesoul.gateway.session — pure helpers and GatewaySession."""

from __future__ import annotations

import pytest

from memory.genesis import Genesis
from tonesoul.gateway.session import GatewaySession, _parse_genesis, _utc_now

# ── _utc_now ──────────────────────────────────────────────────────────────────


class TestUtcNow:
    def test_returns_string(self):
        assert isinstance(_utc_now(), str)

    def test_ends_with_z(self):
        assert _utc_now().endswith("Z")


# ── _parse_genesis ────────────────────────────────────────────────────────────


class TestParseGenesis:
    def test_valid_value(self):
        result = _parse_genesis("autonomous", Genesis.REACTIVE_USER)
        assert result == Genesis.AUTONOMOUS

    def test_case_insensitive(self):
        result = _parse_genesis("REACTIVE_USER", Genesis.AUTONOMOUS)
        assert result == Genesis.REACTIVE_USER

    def test_none_returns_default(self):
        result = _parse_genesis(None, Genesis.MANDATORY)
        assert result == Genesis.MANDATORY

    def test_empty_returns_default(self):
        result = _parse_genesis("", Genesis.MANDATORY)
        assert result == Genesis.MANDATORY

    def test_unknown_returns_default(self):
        result = _parse_genesis("unknown_genesis", Genesis.REACTIVE_USER)
        assert result == Genesis.REACTIVE_USER

    def test_strips_whitespace(self):
        result = _parse_genesis("  mandatory  ", Genesis.REACTIVE_USER)
        assert result == Genesis.MANDATORY


# ── GatewaySession.from_payload ───────────────────────────────────────────────


class TestGatewaySessionFromPayload:
    def test_minimal_payload(self):
        session = GatewaySession.from_payload({"session_id": "s1"})
        assert session.session_id == "s1"

    def test_missing_session_id_raises(self):
        with pytest.raises(ValueError):
            GatewaySession.from_payload({})

    def test_empty_session_id_raises(self):
        with pytest.raises(ValueError):
            GatewaySession.from_payload({"session_id": "   "})

    def test_user_id_parsed(self):
        session = GatewaySession.from_payload({"session_id": "s1", "user_id": "u42"})
        assert session.user_id == "u42"

    def test_none_user_id_preserved(self):
        session = GatewaySession.from_payload({"session_id": "s1", "user_id": None})
        assert session.user_id is None

    def test_genesis_parsed(self):
        session = GatewaySession.from_payload({"session_id": "s1", "genesis": "autonomous"})
        assert session.genesis == Genesis.AUTONOMOUS

    def test_channel_default_audit(self):
        session = GatewaySession.from_payload({"session_id": "s1"})
        assert session.channel == "audit"

    def test_channel_custom(self):
        session = GatewaySession.from_payload({"session_id": "s1", "channel": "debug"})
        assert session.channel == "debug"

    def test_metadata_parsed(self):
        session = GatewaySession.from_payload({"session_id": "s1", "metadata": {"k": "v"}})
        assert session.metadata == {"k": "v"}

    def test_non_dict_metadata_defaults_empty(self):
        session = GatewaySession.from_payload({"session_id": "s1", "metadata": "bad"})
        assert session.metadata == {}


# ── GatewaySession.to_gateway_payload ────────────────────────────────────────


class TestGatewaySessionToGatewayPayload:
    def _make(self, **kw):
        defaults = dict(session_id="s1", genesis=Genesis.REACTIVE_USER)
        defaults.update(kw)
        return GatewaySession(**defaults)

    def test_type_field(self):
        d = self._make().to_gateway_payload()
        assert d["type"] == "session_open"

    def test_custom_event_type(self):
        d = self._make().to_gateway_payload("session_close")
        assert d["type"] == "session_close"

    def test_session_id_in_payload(self):
        d = self._make().to_gateway_payload()
        assert d["session"]["session_id"] == "s1"

    def test_genesis_serialized_as_string(self):
        d = self._make().to_gateway_payload()
        assert d["session"]["genesis"] == "reactive_user"

    def test_responsibility_tier_present(self):
        d = self._make().to_gateway_payload()
        assert "responsibility_tier" in d["session"]
