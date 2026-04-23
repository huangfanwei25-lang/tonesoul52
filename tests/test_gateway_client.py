from __future__ import annotations

import json

import pytest

from tonesoul.gateway.client import DEFAULT_CHANNEL_ROUTES, GatewayClient, GatewayClientError


# ── sync properties ───────────────────────────────────────────────────────────

class TestConnectedProperty:
    def test_initially_false(self):
        assert GatewayClient().connected is False

    def test_true_when_ws_set(self):
        client = GatewayClient()
        client._ws = object()
        assert client.connected is True


class TestChannelRoutes:
    def test_returns_copy_of_defaults(self):
        client = GatewayClient()
        routes = client.channel_routes
        assert routes == DEFAULT_CHANNEL_ROUTES

    def test_returns_independent_copy(self):
        client = GatewayClient()
        routes = client.channel_routes
        routes["new"] = "/new"
        assert "new" not in client.channel_routes

    def test_custom_routes_merged(self):
        client = GatewayClient(channel_routes={"custom": "/custom"})
        assert client.channel_routes["custom"] == "/custom"
        assert "audit" in client.channel_routes


# ── resolve_route ─────────────────────────────────────────────────────────────

class TestResolveRoute:
    def test_known_channel_returned(self):
        client = GatewayClient()
        assert client.resolve_route("audit") == "/audit"
        assert client.resolve_route("council") == "/council"
        assert client.resolve_route("heartbeat") == "/heartbeat"

    def test_unknown_channel_builds_slash_route(self):
        client = GatewayClient()
        assert client.resolve_route("metrics") == "/metrics"

    def test_empty_channel_defaults_to_audit(self):
        client = GatewayClient()
        assert client.resolve_route("") == "/audit"

    def test_strips_whitespace_and_lowercases(self):
        client = GatewayClient()
        assert client.resolve_route("  AUDIT  ") == "/audit"

    def test_custom_route_overrides_default(self):
        client = GatewayClient(channel_routes={"audit": "/v2/audit"})
        assert client.resolve_route("audit") == "/v2/audit"


# ── async connect / close / send ──────────────────────────────────────────────

class _FakeWS:
    def __init__(self):
        self.sent: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_connect_calls_connect_func_once():
    ws = _FakeWS()
    calls = []

    async def _fake_connect(uri: str) -> _FakeWS:
        calls.append(uri)
        return ws

    client = GatewayClient(uri="ws://test", connect_func=_fake_connect)
    result1 = await client.connect()
    result2 = await client.connect()

    assert result1 is ws
    assert result2 is ws
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_close_clears_ws_and_calls_close():
    ws = _FakeWS()
    client = GatewayClient(connect_func=lambda _: _never())
    client._ws = ws

    await client.close()

    assert ws.closed is True
    assert client.connected is False


@pytest.mark.asyncio
async def test_close_is_idempotent_when_not_connected():
    client = GatewayClient()
    await client.close()  # should not raise
    assert client.connected is False


@pytest.mark.asyncio
async def test_send_builds_envelope_and_returns_it():
    ws = _FakeWS()

    async def _fake_connect(uri: str) -> _FakeWS:
        return ws

    client = GatewayClient(connect_func=_fake_connect)
    envelope = await client.send("audit", {"action": "check"})

    assert envelope["channel"] == "audit"
    assert envelope["route"] == "/audit"
    assert envelope["payload"] == {"action": "check"}
    assert len(ws.sent) == 1
    assert json.loads(ws.sent[0])["channel"] == "audit"


async def _never():
    raise AssertionError("connect_func should not be called")
