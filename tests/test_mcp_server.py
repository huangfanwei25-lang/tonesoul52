from __future__ import annotations

import json
from io import StringIO

from tonesoul import mcp_server


def test_handle_initialize_returns_tools_capability() -> None:
    response = mcp_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})

    assert response is not None
    assert response["result"]["protocolVersion"] == "2025-03-26"
    assert response["result"]["capabilities"] == {"tools": {}}
    assert response["result"]["serverInfo"]["name"] == "tonesoul-mcp"


def test_handle_tools_list_can_hide_gateway_tools() -> None:
    response = mcp_server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        include_gateway=False,
    )

    assert response is not None
    names = [tool["name"] for tool in response["result"]["tools"]]
    assert names == [
        "council_deliberate",
        "council_check_claim",
        "council_get_calibration",
        "council_get_status",
    ]


def test_governance_status_compacts_session_start(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "_run_session_start",
        lambda agent_id, tier=0: {
            "readiness": {"status": "pass"},
            "claim_boundary": {"current_tier": "collaborator_beta"},
        },
    )

    result = mcp_server.call_tool("council_get_status", {"agent_id": "codex"})

    assert result["_compact"] is True
    assert result["kind"] == "governance_summary"
    assert result["readiness"] == "pass"
    assert result["claim_tier"] == "collaborator_beta"
    assert "council_deliberate" in result["available_tools"]


def test_claim_check_blocks_public_launch_overclaim(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "_run_session_start",
        lambda agent_id, tier=2: {
            "claim_boundary": {"current_tier": "collaborator_beta"},
        },
    )

    result = mcp_server.call_tool(
        "council_check_claim",
        {"claim_text": "ToneSoul is production ready and validated at scale."},
    )

    assert result["_compact"] is True
    assert result["ceiling"] == "collaborator_beta"
    assert result["evidence_level"] == "blocked_overclaim"
    assert "production_readiness_overclaim" in result["blocked_reasons"]
    assert "live_shared_memory_overclaim" in result["blocked_reasons"]


def test_calibration_tool_returns_compact_snapshot(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "_run_calibration",
        lambda: {
            "status": "v0a_realism_baseline",
            "language_boundary": {"ceiling_effect": "none"},
            "metrics": {
                "agreement_stability": {
                    "status": "computed",
                    "sample_count": 10,
                    "mean_dominant_verdict_ratio": 1.0,
                    "mean_split_half_jsd": 0.0,
                },
                "internal_self_consistency": {
                    "status": "computed",
                    "sample_count": 10,
                    "consistency_rate": 0.8,
                    "inconsistent_count": 2,
                },
                "suppression_recovery_rate": {
                    "status": "computed",
                    "sample_count": 2,
                    "recovery_rate": 0.5,
                    "recovery_events": 1,
                },
                "persistence_coverage": {
                    "status": "computed",
                    "sample_count": 3,
                    "overall_field_coverage": 1.0,
                },
            },
        },
    )

    result = mcp_server.call_tool("council_get_calibration")

    assert result["_compact"] is True
    assert result["status"] == "v0a_realism_baseline"
    assert result["agreement_stability"]["n"] == 10
    assert "realism_score" not in str(result)


def test_handle_tools_call_wraps_structured_content(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "call_tool",
        lambda name, arguments=None: {
            "_compact": True,
            "kind": "council_verdict",
            "verdict": "approve",
        },
    )

    response = mcp_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "council_deliberate",
                "arguments": {"draft_output": "ok"},
            },
        }
    )

    assert response is not None
    payload = response["result"]
    assert payload["structuredContent"]["verdict"] == "approve"
    assert json.loads(payload["content"][0]["text"])["kind"] == "council_verdict"


def test_handle_tools_call_unknown_tool_returns_error() -> None:
    response = mcp_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "missing_tool", "arguments": {}},
        }
    )

    assert response is not None
    assert response["error"]["code"] == -32601


def test_handle_tools_call_invalid_params_returns_error() -> None:
    response = mcp_server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "governance_commit",
                "arguments": {"topics": "abc"},
            },
        }
    )

    assert response is not None
    assert response["error"]["code"] == -32602
    assert "topics" in response["error"]["message"]


def test_serve_stdio_emits_one_jsonrpc_line(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "handle_request",
        lambda request, include_gateway=True: {"jsonrpc": "2.0", "id": request["id"], "result": {}},
    )
    in_stream = StringIO(json.dumps({"jsonrpc": "2.0", "id": 9, "method": "initialize"}) + "\n")
    out_stream = StringIO()

    mcp_server.serve_stdio(in_stream, out_stream)

    lines = [line for line in out_stream.getvalue().splitlines() if line.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["id"] == 9


def test_serve_stdio_emits_batch_response_for_batch_request(monkeypatch) -> None:
    monkeypatch.setattr(
        mcp_server,
        "handle_request",
        lambda request, include_gateway=True: (
            None
            if request.get("method") == "notifications/initialized"
            else {"jsonrpc": "2.0", "id": request["id"], "result": {"echo": request["id"]}}
        ),
    )
    in_stream = StringIO(
        json.dumps(
            [
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    mcp_server.serve_stdio(in_stream, out_stream)

    lines = [line for line in out_stream.getvalue().splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert isinstance(payload, list)
    assert [item["id"] for item in payload] == [1, 2]
