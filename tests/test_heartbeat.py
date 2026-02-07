from __future__ import annotations

import json

import pytest

from tonesoul.gateway import GatewayClient
from tonesoul.heartbeat import ResponsibilityHeartbeat
from tonesoul.openclaw_auditor import OpenClawAuditor


class _FakeWebSocket:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.messages.append(data)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_heartbeat_emit_once_sends_protocol_payload():
    fake_ws = _FakeWebSocket()

    async def _connect(_uri: str):
        return fake_ws

    heartbeat = ResponsibilityHeartbeat(
        node_id="ts-node",
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True, "result": {"verdict": "approve"}},
        interval_seconds=0.0,
    )

    result = await heartbeat.emit_once(
        cycle=1,
        session={"session_id": "hb_session_001", "channel": "heartbeat", "genesis": "mandatory"},
    )

    assert result.status == "ok"
    assert result.gateway_envelope["route"] == "/heartbeat"
    assert len(fake_ws.messages) == 1

    envelope = json.loads(fake_ws.messages[0])
    payload = envelope["payload"]
    assert payload["type"] == "heartbeat"
    assert payload["node_id"] == "ts-node"
    assert payload["checks"]["auditor_passed"] is True
    assert payload["checks"]["council_ok"] is True

    await heartbeat.close()
    assert fake_ws.closed is True


@pytest.mark.asyncio
async def test_heartbeat_run_respects_interval_and_cycles():
    fake_ws = _FakeWebSocket()
    sleeps: list[float] = []

    async def _connect(_uri: str):
        return fake_ws

    async def _sleep(seconds: float):
        sleeps.append(seconds)

    heartbeat = ResponsibilityHeartbeat(
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True},
        interval_seconds=0.25,
        sleep_func=_sleep,
    )

    results = await heartbeat.run(max_cycles=2)
    assert len(results) == 2
    assert sleeps == [0.25]


@pytest.mark.asyncio
async def test_heartbeat_degraded_when_audit_requires_confirmation():
    fake_ws = _FakeWebSocket()

    async def _connect(_uri: str):
        return fake_ws

    heartbeat = ResponsibilityHeartbeat(
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True},
        interval_seconds=0.0,
    )

    result = await heartbeat.emit_once(
        cycle=1,
        proposed_action="destroy all records now",
        context_fragments=["safe summary only"],
    )

    assert result.status == "degraded"
    assert result.heartbeat["checks"]["requires_confirmation"] is True
