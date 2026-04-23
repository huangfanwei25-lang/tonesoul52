from __future__ import annotations

import json
from io import StringIO

import pytest

from tonesoul import mcp_server
from tonesoul.mcp_server import (
    _claim_blocked_reasons,
    _claim_evidence_level,
    _normalize_mode,
    _require_duration_minutes,
    _require_object_list,
    _require_string_list,
)


# ── _normalize_mode ───────────────────────────────────────────────────────────

class TestNormalizeMode:
    def test_rules_passthrough(self):
        assert _normalize_mode("rules") == "rules"

    def test_hybrid_passthrough(self):
        assert _normalize_mode("hybrid") == "hybrid"

    def test_full_llm_passthrough(self):
        assert _normalize_mode("full_llm") == "full_llm"

    def test_rules_only_aliases_to_rules(self):
        assert _normalize_mode("rules_only") == "rules"

    def test_none_defaults_to_rules(self):
        assert _normalize_mode(None) == "rules"

    def test_unknown_defaults_to_rules(self):
        assert _normalize_mode("custom") == "rules"

    def test_strips_whitespace(self):
        assert _normalize_mode("  hybrid  ") == "hybrid"


# ── _require_string_list ──────────────────────────────────────────────────────

class TestRequireStringList:
    def test_returns_empty_when_missing(self):
        assert _require_string_list({}, "key") == []

    def test_returns_empty_for_none_value(self):
        assert _require_string_list({"key": None}, "key") == []

    def test_non_list_raises(self):
        with pytest.raises(ValueError, match="must be an array"):
            _require_string_list({"key": "not-a-list"}, "key")

    def test_non_string_item_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            _require_string_list({"key": [1, 2]}, "key")

    def test_filters_empty_strings(self):
        result = _require_string_list({"key": ["a", "", "  ", "b"]}, "key")
        assert result == ["a", "b"]


# ── _require_object_list ──────────────────────────────────────────────────────

class TestRequireObjectList:
    def test_returns_empty_when_missing(self):
        assert _require_object_list({}, "key") == []

    def test_non_list_raises(self):
        with pytest.raises(ValueError, match="must be an array"):
            _require_object_list({"key": "bad"}, "key")

    def test_non_dict_item_raises(self):
        with pytest.raises(ValueError, match="must be an object"):
            _require_object_list({"key": ["not-a-dict"]}, "key")

    def test_valid_list(self):
        result = _require_object_list({"key": [{"a": 1}, {"b": 2}]}, "key")
        assert result == [{"a": 1}, {"b": 2}]


# ── _require_duration_minutes ─────────────────────────────────────────────────

class TestRequireDurationMinutes:
    def test_zero_default(self):
        assert _require_duration_minutes({}) == pytest.approx(0.0)

    def test_valid_duration(self):
        assert _require_duration_minutes({"duration_minutes": 30.0}) == pytest.approx(30.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            _require_duration_minutes({"duration_minutes": -5})

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="must be a number"):
            _require_duration_minutes({"duration_minutes": "bad"})


# ── _claim_blocked_reasons ────────────────────────────────────────────────────

class TestClaimBlockedReasons:
    def test_production_ready_blocked(self):
        reasons = _claim_blocked_reasons("ToneSoul is production-ready")
        assert "production_readiness_overclaim" in reasons

    def test_consciousness_blocked(self):
        reasons = _claim_blocked_reasons("AI with genuine consciousness")
        assert "ai_selfhood_overclaim" in reasons

    def test_clean_claim_no_blocks(self):
        reasons = _claim_blocked_reasons("ToneSoul is a governance framework")
        assert reasons == []

    def test_multiple_patterns_detected(self):
        reasons = _claim_blocked_reasons("production ready with validated at scale")
        assert "production_readiness_overclaim" in reasons
        assert "live_shared_memory_overclaim" in reasons


# ── _claim_evidence_level ─────────────────────────────────────────────────────

class TestClaimEvidenceLevel:
    def test_blocked_reasons_returns_blocked_overclaim(self):
        level = _claim_evidence_level("anything", ["some_block"])
        assert level == "blocked_overclaim"

    def test_safe_pattern_returns_bounded_current_truth(self):
        level = _claim_evidence_level(
            "governance state is computed and persisted", []
        )
        assert level == "bounded_current_truth"

    def test_unknown_returns_needs_human_review(self):
        level = _claim_evidence_level("Some claim without safe patterns", [])
        assert level == "needs_human_review"


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
