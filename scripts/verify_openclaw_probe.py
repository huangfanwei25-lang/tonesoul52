"""
Verify OpenClaw runtime probe against a local mock websocket gateway.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.openclaw.runtime import OpenClawRuntimeBridge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify OpenClaw gateway probe with local mock server."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18789)
    parser.add_argument("--timeout", type=float, default=3.0)
    return parser


async def _run(args: argparse.Namespace) -> int:
    try:
        import websockets
    except ImportError as exc:
        print(json.dumps({"ok": False, "error": f"Missing dependency: {exc}"}))
        return 1

    received_messages: list[dict[str, Any]] = []

    async def _handler(ws):
        async for message in ws:
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                payload = {"raw": message}
            received_messages.append(payload)

    gateway_uri = f"ws://{args.host}:{args.port}"
    async with websockets.serve(_handler, args.host, args.port):
        runtime = OpenClawRuntimeBridge.build(dry_run=False, gateway_uri=gateway_uri)
        try:
            probe_result = await runtime.probe_gateway(timeout_seconds=max(0.1, args.timeout))
        finally:
            await runtime.close()

    payload = {
        "ok": bool(probe_result.get("ok")) and len(received_messages) > 0,
        "probe": probe_result,
        "received_count": len(received_messages),
        "received_preview": received_messages[:1],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
