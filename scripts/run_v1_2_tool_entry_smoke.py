#!/usr/bin/env python3
"""Run the ToneSoul v1.2 tool-first entry smoke."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ToneSoul v1.2 tool-first entry smoke.")
    parser.add_argument("--agent", default="v1-2-smoke")
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "docs" / "status" / "v1_2_tool_entry_smoke_latest.json",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=REPO_ROOT / "docs" / "status" / "v1_2_tool_entry_smoke_latest.md",
    )
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# ToneSoul V1.2 Tool-First Entry Smoke")
    lines.append("")
    lines.append(f"> Generated at `{payload.get('generated_at', '')}`.")
    lines.append("")
    lines.append(f"- Status: `{payload.get('status', 'unknown')}`")
    lines.append(f"- Agent: `{payload.get('agent', 'unknown')}`")
    lines.append("")

    workflow = payload.get("workflow_alignment") or {}
    lines.append("## Workflow Alignment")
    lines.append("")
    lines.append(f"- First hop: `{workflow.get('first_hop', '')}`")
    lines.append(f"- Council path: `{workflow.get('council_path', '')}`")
    lines.append(f"- Deeper pull rule: `{workflow.get('deeper_pull_rule', '')}`")
    lines.append("")

    size = payload.get("session_start_size") or {}
    lines.append("## Session-Start Size")
    lines.append("")
    lines.append(f"- Slim bytes: `{size.get('slim_bytes', 0)}`")
    lines.append(f"- Tier 0 bytes: `{size.get('tier0_bytes', 0)}`")
    lines.append(f"- Reduction bytes: `{size.get('reduction_bytes', 0)}`")
    lines.append(f"- Reduction ratio: `{size.get('reduction_ratio', 0)}`")
    lines.append(f"- Meets slim target: `{size.get('slim_lt_2kb', False)}`")
    lines.append("")

    mcp = payload.get("mcp_stdio_smoke") or {}
    lines.append("## MCP Stdio Smoke")
    lines.append("")
    lines.append(f"- Return code: `{mcp.get('returncode', -1)}`")
    lines.append(f"- Batch responses: `{mcp.get('batch_response_count', 0)}`")
    lines.append(f"- Tools count: `{mcp.get('tools_count', 0)}`")
    lines.append(f"- Tool names: `{', '.join(mcp.get('tool_names') or [])}`")
    lines.append("")

    verdict = mcp.get("council_deliberate") or {}
    if verdict:
        lines.append("### council_deliberate")
        lines.append("")
        lines.append(f"- Verdict: `{verdict.get('verdict', '')}`")
        lines.append(f"- Coherence: `{verdict.get('coherence', '')}`")
        lines.append(f"- Risk level: `{verdict.get('risk_level', '')}`")
        lines.append(f"- Minority: `{', '.join(verdict.get('minority') or [])}`")
        lines.append("")

    status = mcp.get("council_get_status") or {}
    if status:
        lines.append("### council_get_status")
        lines.append("")
        lines.append(f"- Readiness: `{status.get('readiness', '')}`")
        lines.append(f"- Claim tier: `{status.get('claim_tier', '')}`")
        lines.append(f"- Available tools: `{', '.join(status.get('available_tools') or [])}`")
        lines.append("")

    gateway = mcp.get("governance_load") or {}
    if gateway:
        lines.append("### governance_load")
        lines.append("")
        lines.append(f"- Readiness: `{gateway.get('readiness', '')}`")
        lines.append(f"- Claim tier: `{gateway.get('claim_tier', '')}`")
        lines.append(f"- Available tools: `{', '.join(gateway.get('available_tools') or [])}`")
        lines.append("")

    lines.append("## Receiver Rule")
    lines.append("")
    lines.append(f"> {payload.get('receiver_rule', '')}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _encoded_size(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def _run_session_start_sizes(agent: str) -> dict[str, Any]:
    from scripts.start_agent_session import run_session_start_bundle

    slim = run_session_start_bundle(agent_id=agent, no_ack=True, slim=True)
    tier0 = run_session_start_bundle(agent_id=agent, no_ack=True, tier=0)
    slim_bytes = _encoded_size(slim)
    tier0_bytes = _encoded_size(tier0)
    reduction = max(tier0_bytes - slim_bytes, 0)
    ratio = round(reduction / tier0_bytes, 4) if tier0_bytes else 0.0
    return {
        "slim_bytes": slim_bytes,
        "tier0_bytes": tier0_bytes,
        "reduction_bytes": reduction,
        "reduction_ratio": ratio,
        "slim_lt_2kb": slim_bytes < 2048,
    }


def _parse_json_lines(text: str) -> list[Any]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _flatten_response_items(messages: list[Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for message in messages:
        if isinstance(message, dict):
            items.append(message)
        elif isinstance(message, list):
            items.extend(item for item in message if isinstance(item, dict))
    return items


def _run_mcp_stdio_smoke() -> dict[str, Any]:
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {"roots": {"listChanged": False}, "sampling": {}},
            "clientInfo": {"name": "tonesoul-v1-2-smoke", "version": "0.1.0"},
        },
    }
    initialized_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    batch_requests = [
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "council_deliberate",
                "arguments": {
                    "draft_output": "Provide a careful bounded answer with explicit evidence posture.",
                    "user_intent": "review governance-safe answer path",
                    "mode": "rules",
                },
            },
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "council_get_status", "arguments": {"agent_id": "mcp-smoke"}},
        },
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "governance_load", "arguments": {"agent_id": "mcp-smoke"}},
        },
    ]
    input_payload = (
        "\n".join(
            json.dumps(item, ensure_ascii=False)
            for item in [initialize_request, initialized_notification, batch_requests]
        )
        + "\n"
    )
    child_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, "-m", "tonesoul.mcp_server", "--toolset", "gateway"],
        cwd=str(REPO_ROOT),
        input=input_payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_env,
        check=False,
    )
    messages = _parse_json_lines(completed.stdout or "")
    response_items = _flatten_response_items(messages)
    by_id = {item.get("id"): item for item in response_items if isinstance(item, dict)}
    tools = ((by_id.get(2) or {}).get("result") or {}).get("tools") or []
    batch_response_count = sum(1 for message in messages if isinstance(message, list))

    def _structured(idx: int) -> dict[str, Any]:
        result = (by_id.get(idx) or {}).get("result") or {}
        structured = result.get("structuredContent")
        return structured if isinstance(structured, dict) else {}

    return {
        "returncode": completed.returncode,
        "stderr": (completed.stderr or "").strip(),
        "response_count": len(response_items),
        "batch_response_count": batch_response_count,
        "tools_count": len(tools),
        "tool_names": [str(item.get("name", "")).strip() for item in tools],
        "initialize_ok": bool((by_id.get(1) or {}).get("result")),
        "initialized_notification_sent": True,
        "council_deliberate": _structured(3),
        "council_get_status": _structured(4),
        "governance_load": _structured(5),
    }


def run_v1_2_tool_entry_smoke(*, agent: str) -> dict[str, Any]:
    size = _run_session_start_sizes(agent)
    mcp = _run_mcp_stdio_smoke()
    status = (
        "pass"
        if size.get("slim_lt_2kb")
        and mcp.get("returncode") == 0
        and mcp.get("initialize_ok")
        and mcp.get("batch_response_count", 0) >= 1
        and bool(mcp.get("council_deliberate"))
        and bool(mcp.get("council_get_status"))
        and bool(mcp.get("governance_load"))
        else "review"
    )
    return {
        "contract_version": "v1",
        "bundle": "v1_2_tool_entry_smoke",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "agent": agent,
        "status": status,
        "workflow_alignment": {
            "first_hop": "session_start --slim",
            "council_path": "session_start --slim -> council_deliberate / council_get_status / governance_load",
            "deeper_pull_rule": (
                "Escalate to tier 0/1/2 only when slim shell is insufficient for shared mutation, "
                "contested governance, or deeper continuity detail."
            ),
        },
        "session_start_size": size,
        "mcp_stdio_smoke": mcp,
        "receiver_rule": (
            "Treat slim entry as the default bounded first hop, use MCP tools for council/governance lookups, "
            "and only widen to tiered session-start shells when the task truly needs deeper state."
        ),
    }


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    payload = run_v1_2_tool_entry_smoke(agent=args.agent)
    _write_json(args.json_out, payload)
    _write_markdown(args.markdown_out, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
