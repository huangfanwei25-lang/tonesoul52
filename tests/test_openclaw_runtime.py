from __future__ import annotations

import asyncio

from integrations.openclaw.runtime import OpenClawRuntimeBridge, build_parser
from tonesoul.gateway import GatewayClient
from tonesoul.heartbeat import ResponsibilityHeartbeat
from tonesoul.openclaw_auditor import OpenClawAuditor


def test_openclaw_runtime_lists_skills():
    bridge = OpenClawRuntimeBridge.build(dry_run=True)
    skills = bridge.list_skills()
    names = {item["name"] for item in skills}
    assert "benevolence_audit" in names
    assert "council_deliberate" in names
    asyncio.run(bridge.close())


def test_openclaw_runtime_invoke_skill():
    bridge = OpenClawRuntimeBridge.build(dry_run=True)
    result = bridge.invoke_skill(
        "benevolence_audit",
        {
            "proposed_action": "I may be uncertain and should verify this first.",
            "context_fragments": ["verify this first"],
        },
    )
    assert result["ok"] is True
    assert result["skill"] == "benevolence_audit"
    asyncio.run(bridge.close())


def test_openclaw_runtime_heartbeat_once_dry_run():
    bridge = OpenClawRuntimeBridge.build(dry_run=True)
    try:
        payload = asyncio.run(bridge.heartbeat_once(cycle=1, session_id="hb_runtime_001"))
    finally:
        asyncio.run(bridge.close())

    assert payload["status"] in {"ok", "degraded"}
    assert payload["heartbeat"]["type"] == "heartbeat"
    assert payload["gateway_envelope"]["route"] == "/heartbeat"


def test_openclaw_runtime_probe_gateway_dry_run():
    bridge = OpenClawRuntimeBridge.build(dry_run=True)
    try:
        result = asyncio.run(bridge.probe_gateway(timeout_seconds=1.0))
    finally:
        asyncio.run(bridge.close())

    assert result["ok"] is True
    assert result["route"] == "/heartbeat"


def test_openclaw_runtime_probe_gateway_handles_failure():
    async def _connect_fail(_uri: str):
        raise ConnectionError("gateway unreachable")

    gateway = GatewayClient(connect_func=_connect_fail)
    heartbeat = ResponsibilityHeartbeat(
        gateway_client=gateway,
        auditor=OpenClawAuditor(persist_to_ledger=False),
        interval_seconds=0.0,
    )
    bridge = OpenClawRuntimeBridge(gateway_client=gateway, heartbeat=heartbeat)
    try:
        result = asyncio.run(bridge.probe_gateway(timeout_seconds=0.2))
    finally:
        asyncio.run(bridge.close())

    assert result["ok"] is False
    assert result["error_type"] in {"ConnectionError", "TimeoutError"}


def test_openclaw_runtime_build_applies_gateway_uri():
    bridge = OpenClawRuntimeBridge.build(dry_run=True, gateway_uri="ws://127.0.0.1:19999")
    try:
        assert bridge.gateway_client.uri == "ws://127.0.0.1:19999"
    finally:
        asyncio.run(bridge.close())


def test_openclaw_runtime_parser_accepts_gateway_uri():
    parser = build_parser()
    args = parser.parse_args(["--gateway-uri", "ws://127.0.0.1:19999", "list-skills"])
    assert args.gateway_uri == "ws://127.0.0.1:19999"
