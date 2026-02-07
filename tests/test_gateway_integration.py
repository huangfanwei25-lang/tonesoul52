import json

import pytest

from memory.genesis import Genesis
from tonesoul.gateway import GatewayClient, GatewaySession


class _FakeWebSocket:
    def __init__(self):
        self.messages: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.messages.append(data)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_gateway_client_send_resolves_configured_route():
    fake_ws = _FakeWebSocket()

    async def _connect(uri: str):
        assert uri == "ws://127.0.0.1:18789"
        return fake_ws

    client = GatewayClient(connect_func=_connect)
    envelope = await client.send("council", {"hello": "world"})

    assert envelope["route"] == "/council"
    assert len(fake_ws.messages) == 1
    payload = json.loads(fake_ws.messages[0])
    assert payload["channel"] == "council"
    assert payload["payload"]["hello"] == "world"

    await client.close()
    assert fake_ws.closed is True


def test_gateway_session_maps_genesis_to_responsibility_tier():
    session = GatewaySession.from_payload(
        {
            "session_id": "s_001",
            "user_id": "u_001",
            "channel": "audit",
            "genesis": "autonomous",
            "metadata": {"intent_id": "i_001"},
        }
    )
    payload = session.to_gateway_payload()

    assert session.genesis == Genesis.AUTONOMOUS
    assert session.responsibility_tier == "TIER_1"
    assert payload["session"]["responsibility_tier"] == "TIER_1"
    assert payload["session"]["metadata"]["intent_id"] == "i_001"


def test_gateway_session_requires_session_id():
    with pytest.raises(ValueError):
        GatewaySession.from_payload({"session_id": " "})
