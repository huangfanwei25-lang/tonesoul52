from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from integrations.openclaw.skills.tonesoul import invoke_skill, list_skills
from tonesoul.gateway import GatewayClient
from tonesoul.heartbeat import ResponsibilityHeartbeat
from tonesoul.openclaw_auditor import OpenClawAuditor


class _MemoryWebSocket:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.messages.append(data)

    async def close(self) -> None:
        self.closed = True


@dataclass(slots=True)
class OpenClawRuntimeBridge:
    gateway_client: GatewayClient
    heartbeat: ResponsibilityHeartbeat

    @classmethod
    def build(
        cls,
        *,
        dry_run: bool = False,
        interval_seconds: float = 60.0,
        gateway_uri: str = "ws://127.0.0.1:18789",
    ) -> "OpenClawRuntimeBridge":
        if dry_run:
            mem_ws = _MemoryWebSocket()

            async def _connect(_uri: str):
                return mem_ws

            gateway_client = GatewayClient(uri=gateway_uri, connect_func=_connect)
        else:
            gateway_client = GatewayClient(uri=gateway_uri)
        heartbeat = ResponsibilityHeartbeat(
            gateway_client=gateway_client,
            auditor=OpenClawAuditor(persist_to_ledger=True),
            interval_seconds=interval_seconds,
        )
        return cls(gateway_client=gateway_client, heartbeat=heartbeat)

    def list_skills(self) -> list[dict[str, str]]:
        return list_skills()

    def invoke_skill(self, name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        return invoke_skill(name, payload)

    async def heartbeat_once(
        self,
        *,
        cycle: int = 1,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        session = {"session_id": session_id, "channel": "heartbeat"} if session_id else None
        result = await self.heartbeat.emit_once(cycle=cycle, session=session)
        return result.to_dict()

    async def probe_gateway(self, *, timeout_seconds: float = 5.0) -> dict[str, Any]:
        timeout = max(0.1, float(timeout_seconds))
        payload = {"type": "probe", "source": "openclaw-runtime-bridge"}
        try:
            await asyncio.wait_for(self.gateway_client.connect(), timeout=timeout)
            envelope = await asyncio.wait_for(
                self.gateway_client.send("heartbeat", payload),
                timeout=timeout,
            )
            return {
                "ok": True,
                "gateway_uri": self.gateway_client.uri,
                "route": envelope.get("route"),
                "channel": envelope.get("channel"),
                "sent": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "gateway_uri": self.gateway_client.uri,
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            }

    async def close(self) -> None:
        await self.heartbeat.close()


def _parse_json_payload(payload_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"payload-json is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("payload-json must be a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw runtime bridge for ToneSoul integrations.")
    parser.add_argument("--dry-run", action="store_true", help="Use in-memory gateway transport.")
    parser.add_argument(
        "--gateway-uri",
        default="ws://127.0.0.1:18789",
        help="Gateway websocket URI (default: ws://127.0.0.1:18789).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-skills", help="List available ToneSoul OpenClaw skills.")

    invoke = sub.add_parser("invoke-skill", help="Invoke one skill with JSON payload.")
    invoke.add_argument("--name", required=True, help="Skill name")
    invoke.add_argument("--payload-json", required=True, help="JSON object payload")

    hb = sub.add_parser("heartbeat-once", help="Run one heartbeat cycle and emit envelope.")
    hb.add_argument("--cycle", type=int, default=1)
    hb.add_argument("--session-id", default=None)

    probe = sub.add_parser("probe-gateway", help="Probe gateway connectivity with one send operation.")
    probe.add_argument("--timeout", type=float, default=5.0)

    return parser


async def _run_async(args: argparse.Namespace) -> int:
    runtime = OpenClawRuntimeBridge.build(
        dry_run=bool(args.dry_run),
        gateway_uri=str(args.gateway_uri),
    )
    try:
        if args.command == "list-skills":
            print(json.dumps({"skills": runtime.list_skills()}, ensure_ascii=False, indent=2))
            return 0

        if args.command == "invoke-skill":
            payload = _parse_json_payload(args.payload_json)
            result = runtime.invoke_skill(args.name, payload)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("ok", False) else 1

        if args.command == "heartbeat-once":
            result = await runtime.heartbeat_once(cycle=max(1, int(args.cycle)), session_id=args.session_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "probe-gateway":
            result = await runtime.probe_gateway(timeout_seconds=float(args.timeout))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("ok", False) else 1

        print(json.dumps({"error": f"Unknown command: {args.command}"}, ensure_ascii=False))
        return 1
    finally:
        await runtime.close()


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(_run_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
