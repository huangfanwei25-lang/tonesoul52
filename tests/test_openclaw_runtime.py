from __future__ import annotations

import asyncio

from integrations.openclaw.runtime import OpenClawRuntimeBridge


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
