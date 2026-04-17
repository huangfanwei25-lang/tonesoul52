from __future__ import annotations

import argparse
import io
import json
from contextlib import redirect_stdout
from typing import Any, Callable, Iterable, TextIO

from tonesoul.council.compact import (
    compact_calibration,
    compact_governance_summary,
    compact_verdict,
)

_SERVER_INFO = {
    "name": "tonesoul-mcp",
    "version": "1.2.0-alpha",
}
_PROTOCOL_VERSION = "2025-03-26"
_TOOLSETS = ("council", "gateway")


def _quiet_call(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    sink = io.StringIO()
    with redirect_stdout(sink):
        return fn(*args, **kwargs)


def _normalize_mode(mode: Any) -> str:
    candidate = str(mode or "rules").strip().lower()
    if candidate == "rules_only":
        return "rules"
    if candidate not in {"rules", "hybrid", "full_llm"}:
        return "rules"
    return candidate


def _list_tool_definitions(*, include_gateway: bool = True) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = [
        {
            "name": "council_deliberate",
            "description": (
                "Run ToneSoul council deliberation and return a compact verdict. "
                "Use rules/hybrid/full_llm mode, but compact output is always bounded."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "draft_output": {"type": "string"},
                    "user_intent": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["rules", "hybrid", "full_llm"],
                    },
                },
                "required": ["draft_output"],
                "additionalProperties": False,
            },
        },
        {
            "name": "council_check_claim",
            "description": (
                "Check whether a public claim stays inside ToneSoul's current collaborator-beta "
                "claim boundary. Returns ceiling, evidence level, and compact blocked reasons."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "claim_text": {"type": "string"},
                },
                "required": ["claim_text"],
                "additionalProperties": False,
            },
        },
        {
            "name": "council_get_calibration",
            "description": "Return the compact v0a council calibration realism baseline.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "council_get_status",
            "description": (
                "Return compact governance status for agent entry: readiness, claim tier, "
                "and available council tools."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    ]

    if include_gateway:
        tools.extend(
            [
                {
                    "name": "governance_load",
                    "description": "Load current governance posture and return compact status.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                        },
                        "additionalProperties": False,
                    },
                },
                {
                    "name": "governance_commit",
                    "description": "Commit a bounded session trace and return a compact commit result.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "agent": {"type": "string"},
                            "topics": {"type": "array", "items": {"type": "string"}},
                            "tension_events": {"type": "array", "items": {"type": "object"}},
                            "vow_events": {"type": "array", "items": {"type": "object"}},
                            "key_decisions": {"type": "array", "items": {"type": "string"}},
                            "duration_minutes": {"type": "number"},
                        },
                        "additionalProperties": False,
                    },
                },
                {
                    "name": "governance_summary",
                    "description": "Return the current human-readable governance summary clipped for tool use.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
                {
                    "name": "governance_visitors",
                    "description": "Return a compact readout of recent governance visitors.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
                {
                    "name": "governance_audit",
                    "description": "Return a compact Aegis integrity audit readout.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            ]
        )

    return tools


def _tool_name_set(*, include_gateway: bool = True) -> list[str]:
    return [tool["name"] for tool in _list_tool_definitions(include_gateway=include_gateway)]


def _require_string_list(arguments: dict[str, Any], key: str) -> list[str]:
    value = arguments.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array of strings")

    items: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{key}[{idx}] must be a string")
        text = item.strip()
        if text:
            items.append(text)
    return items


def _require_object_list(arguments: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = arguments.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array of objects")

    items: list[dict[str, Any]] = []
    for idx, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{key}[{idx}] must be an object")
        items.append(item)
    return items


def _require_duration_minutes(arguments: dict[str, Any]) -> float:
    raw_value = arguments.get("duration_minutes", 0.0)
    try:
        duration = float(raw_value or 0.0)
    except (TypeError, ValueError) as exc:
        raise ValueError("duration_minutes must be a number") from exc
    if duration < 0:
        raise ValueError("duration_minutes must be >= 0")
    return duration


def _claim_blocked_reasons(claim_text: str) -> list[str]:
    normalized = " ".join(str(claim_text or "").lower().split())
    checks = [
        (
            "production_readiness_overclaim",
            (
                "production-ready",
                "production ready",
                "launch-mature",
                "public launch ready",
                "mature",
            ),
        ),
        (
            "ai_selfhood_overclaim",
            (
                "consciousness",
                "self-awareness",
                "self awareness",
                "genuine emotion",
                "genuine emotions",
            ),
        ),
        (
            "council_accuracy_overclaim",
            ("calibrated accuracy", "council agreement equals correctness", "council as truth"),
        ),
        (
            "absolute_safety_overclaim",
            ("prevents all harmful outputs", "prevents all harm", "guarantees safe output"),
        ),
        (
            "live_shared_memory_overclaim",
            ("redis/live shared memory", "live shared memory", "validated at scale"),
        ),
    ]
    blocked: list[str] = []
    for code, patterns in checks:
        if any(pattern in normalized for pattern in patterns):
            blocked.append(code)
    return blocked


def _claim_evidence_level(claim_text: str, blocked_reasons: list[str]) -> str:
    if blocked_reasons:
        return "blocked_overclaim"

    normalized = " ".join(str(claim_text or "").lower().split())
    safe_patterns = (
        "governance framework under active development",
        "session continuity works across agent handoffs",
        "governance state is computed and persisted",
        "structured dossiers with dissent visibility",
    )
    if any(pattern in normalized for pattern in safe_patterns):
        return "bounded_current_truth"
    return "needs_human_review"


def _run_session_start(agent_id: str, *, tier: int = 0) -> dict[str, Any]:
    from scripts.start_agent_session import run_session_start_bundle

    return _quiet_call(run_session_start_bundle, agent_id=agent_id, tier=tier, no_ack=True)


def _run_calibration() -> dict[str, Any]:
    from tonesoul.council.calibration import run_calibration_wave

    return _quiet_call(run_calibration_wave)


def _deliberate(*, draft_output: str, user_intent: str = "", mode: str = "rules") -> dict[str, Any]:
    from tonesoul.council.runtime import CouncilRequest, CouncilRuntime

    runtime = CouncilRuntime()
    verdict = _quiet_call(
        runtime.deliberate,
        CouncilRequest(
            draft_output=draft_output,
            user_intent=user_intent or None,
            context={
                "agent_id": "mcp-council",
                "source": "mcp_server",
                "council_mode_override": _normalize_mode(mode),
            },
        ),
    )
    return compact_verdict(verdict)


def _claim_check(*, claim_text: str) -> dict[str, Any]:
    state = _run_session_start("mcp-claim-check", tier=2)
    claim_boundary = state.get("claim_boundary")
    claim_boundary = claim_boundary if isinstance(claim_boundary, dict) else {}
    blocked_reasons = _claim_blocked_reasons(claim_text)
    return {
        "_compact": True,
        "kind": "claim_check",
        "ceiling": str(claim_boundary.get("current_tier", "unknown")).strip(),
        "evidence_level": _claim_evidence_level(claim_text, blocked_reasons),
        "blocked_reasons": blocked_reasons[:3],
    }


def _calibration_status() -> dict[str, Any]:
    return compact_calibration(_run_calibration())


def _governance_status(*, agent_id: str = "mcp-status") -> dict[str, Any]:
    status = _run_session_start(agent_id, tier=0)
    status["available_tools"] = _tool_name_set(include_gateway=False)
    return compact_governance_summary(status)


def _governance_load(*, agent_id: str = "mcp-load") -> dict[str, Any]:
    status = _run_session_start(agent_id, tier=0)
    status["available_tools"] = _tool_name_set(include_gateway=True)
    return compact_governance_summary(status)


def _governance_commit(arguments: dict[str, Any]) -> dict[str, Any]:
    from tonesoul.runtime_adapter import SessionTrace, commit

    trace = SessionTrace(
        agent=str(arguments.get("agent", "mcp-gateway")).strip() or "mcp-gateway",
        topics=_require_string_list(arguments, "topics"),
        tension_events=_require_object_list(arguments, "tension_events"),
        vow_events=_require_object_list(arguments, "vow_events"),
        key_decisions=_require_string_list(arguments, "key_decisions"),
        duration_minutes=_require_duration_minutes(arguments),
    )
    posture = _quiet_call(commit, trace)
    risk = posture.risk_posture or {}
    return {
        "_compact": True,
        "kind": "governance_commit",
        "status": "committed",
        "session_id": trace.session_id,
        "soul_integral": round(float(posture.soul_integral), 4),
        "risk_level": str(risk.get("level", "unknown")).strip(),
    }


def _governance_summary() -> dict[str, Any]:
    from tonesoul.runtime_adapter import summary

    text = str(_quiet_call(summary)).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "_compact": True,
        "kind": "governance_summary_text",
        "line_count": len(lines),
        "headline": lines[0] if lines else "",
        "preview": " | ".join(lines[1:4]) if len(lines) > 1 else "",
    }


def _governance_visitors() -> dict[str, Any]:
    from tonesoul.runtime_adapter import get_recent_visitors

    visitors = _quiet_call(get_recent_visitors, n=20)
    agents: list[str] = []
    for item in visitors:
        if not isinstance(item, dict):
            continue
        agent = str(item.get("agent", "")).strip()
        if agent and agent not in agents:
            agents.append(agent)
    return {
        "_compact": True,
        "kind": "governance_visitors",
        "count": len(visitors),
        "agents": agents[:5],
    }


def _governance_audit() -> dict[str, Any]:
    from tonesoul.aegis_shield import AegisShield
    from tonesoul.store import get_store

    store = _quiet_call(get_store)
    shield = _quiet_call(AegisShield.load, store)
    audit = _quiet_call(shield.audit, store)
    return {
        "_compact": True,
        "kind": "governance_audit",
        "integrity": str(audit.get("integrity", "unknown")).strip(),
        "chain_valid": bool(audit.get("chain_valid")),
        "signature_failures": len(list(audit.get("signature_failures") or [])),
        "chain_errors": len(list(audit.get("chain_errors") or [])),
    }


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments if isinstance(arguments, dict) else {}
    handlers: dict[str, Callable[..., dict[str, Any]]] = {
        "council_deliberate": lambda: _deliberate(
            draft_output=str(args.get("draft_output", "")),
            user_intent=str(args.get("user_intent", "")),
            mode=str(args.get("mode", "rules")),
        ),
        "council_check_claim": lambda: _claim_check(claim_text=str(args.get("claim_text", ""))),
        "council_get_calibration": _calibration_status,
        "council_get_status": lambda: _governance_status(
            agent_id=str(args.get("agent_id", "mcp-status"))
        ),
        "governance_load": lambda: _governance_load(agent_id=str(args.get("agent_id", "mcp-load"))),
        "governance_commit": lambda: _governance_commit(args),
        "governance_summary": _governance_summary,
        "governance_visitors": _governance_visitors,
        "governance_audit": _governance_audit,
    }
    handler = handlers.get(name)
    if handler is None:
        raise KeyError(f"unknown tool: {name}")
    return handler()


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _response_payload(
    message: Any,
    *,
    include_gateway: bool = True,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    if isinstance(message, list):
        if not message:
            return _jsonrpc_error(None, -32600, "invalid request")

        responses: list[dict[str, Any]] = []
        for item in message:
            if not isinstance(item, dict):
                responses.append(_jsonrpc_error(None, -32600, "invalid request"))
                continue
            response = handle_request(item, include_gateway=include_gateway)
            if response is not None:
                responses.append(response)
        return responses or None

    if not isinstance(message, dict):
        return _jsonrpc_error(None, -32600, "invalid request")

    return handle_request(message, include_gateway=include_gateway)


def handle_request(
    request: dict[str, Any],
    *,
    include_gateway: bool = True,
) -> dict[str, Any] | None:
    method = str(request.get("method", "")).strip()
    request_id = request.get("id")
    params = request.get("params")
    params = params if isinstance(params, dict) else {}

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return _jsonrpc_result(
            request_id,
            {
                "protocolVersion": _PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": _SERVER_INFO,
            },
        )

    if method == "tools/list":
        return _jsonrpc_result(
            request_id,
            {"tools": _list_tool_definitions(include_gateway=include_gateway)},
        )

    if method == "tools/call":
        name = str(params.get("name", "")).strip()
        arguments = params.get("arguments")
        arguments = arguments if isinstance(arguments, dict) else {}
        try:
            result = call_tool(name, arguments)
        except KeyError as exc:
            return _jsonrpc_error(request_id, -32601, str(exc))
        except ValueError as exc:
            return _jsonrpc_error(request_id, -32602, str(exc))
        except Exception as exc:  # pragma: no cover - defensive transport path
            return _jsonrpc_error(request_id, -32000, f"tool call failed: {exc}")
        return _jsonrpc_result(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "structuredContent": result,
            },
        )

    return _jsonrpc_error(request_id, -32601, f"unknown method: {method}")


def serve_stdio(
    in_stream: TextIO,
    out_stream: TextIO,
    *,
    include_gateway: bool = True,
) -> None:
    for raw_line in in_stream:
        line = raw_line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            response_payload = _jsonrpc_error(None, -32700, "invalid json")
        else:
            response_payload = _response_payload(message, include_gateway=include_gateway)
        if response_payload is None:
            continue
        out_stream.write(json.dumps(response_payload, ensure_ascii=False) + "\n")
        out_stream.flush()


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ToneSoul MCP server over stdio.")
    parser.add_argument(
        "--toolset",
        choices=_TOOLSETS,
        default="gateway",
        help="Expose only core council tools or include gateway extensions.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    serve_stdio(
        in_stream=__import__("sys").stdin,
        out_stream=__import__("sys").stdout,
        include_gateway=args.toolset == "gateway",
    )


if __name__ == "__main__":
    main()
