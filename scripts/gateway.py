#!/usr/bin/env python3
"""ToneSoul Gateway: HTTP API for multi-agent memory access.

Any AI agent that can make HTTP requests can:
  POST /load      - load governance state and leave a footprint
  POST /commit    - commit a session trace (Aegis-protected)
  POST /claim     - claim a task lock
  POST /release   - release a task lock
  POST /compact   - append a bounded non-canonical resumability summary
  GET  /summary   - current governance summary (text)
  GET  /visitors  - recent visitors (JSON)
  GET  /claims    - active task claims (JSON)
  GET  /packet    - compact R-memory packet (JSON)
  GET  /audit     - Aegis integrity report (JSON)
  GET  /health    - heartbeat
"""

from __future__ import annotations

import argparse
import hmac
import http.server
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

_MAX_BODY_SIZE = 1024 * 1024  # 1 MB — reject oversized payloads

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_AUTH_TOKEN: Optional[str] = None
_CORS_ORIGIN: str = "http://localhost:8501"  # default: Streamlit dashboard


def _read_body(handler) -> bytes:
    length = int(handler.headers.get("Content-Length", 0))
    if length > _MAX_BODY_SIZE:
        raise ValueError(f"Request body too large: {length} bytes (max {_MAX_BODY_SIZE})")
    return handler.rfile.read(length) if length > 0 else b""


def _parse_json(handler) -> Dict[str, Any]:
    raw = _read_body(handler)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _send_json(handler, data: Any, status: int = 200) -> None:
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", _CORS_ORIGIN)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _send_text(handler, text: str, status: int = 200) -> None:
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", _CORS_ORIGIN)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _check_auth(handler) -> bool:
    if _AUTH_TOKEN is None:
        _send_json(handler, {"error": "no auth token configured — start with --token"}, 403)
        return False
    auth = handler.headers.get("Authorization", "")
    expected = f"Bearer {_AUTH_TOKEN}"
    if hmac.compare_digest(auth, expected):
        return True
    _send_json(handler, {"error": "unauthorized"}, 401)
    return False


def handle_load(handler) -> None:
    """POST /load - load governance state and record footprint."""
    body = _parse_json(handler)
    agent_id = body.get("agent_id", "unknown")

    from tonesoul.runtime_adapter import load, summary

    posture = load(agent_id=agent_id, source="gateway")
    _send_json(
        handler,
        {
            "posture": posture.to_dict(),
            "summary": summary(posture),
            "agent": agent_id,
        },
    )


def handle_commit(handler) -> None:
    """POST /commit - commit a session trace with Aegis protection."""
    body = _parse_json(handler)

    from tonesoul.runtime_adapter import SessionTrace, commit, summary

    trace = SessionTrace(
        agent=body.get("agent", "unknown"),
        topics=body.get("topics", []),
        tension_events=body.get("tension_events", []),
        vow_events=body.get("vow_events", []),
        key_decisions=body.get("key_decisions", []),
        duration_minutes=float(body.get("duration_minutes", 0)),
    )
    posture = commit(trace)
    _send_json(
        handler,
        {
            "posture": posture.to_dict(),
            "summary": summary(posture),
            "session_id": trace.session_id,
        },
    )


def handle_claim(handler) -> None:
    """POST /claim - claim a task lock for multi-terminal coordination."""
    body = _parse_json(handler)

    from tonesoul.runtime_adapter import claim_task

    result = claim_task(
        str(body.get("task_id", "")).strip(),
        agent_id=str(body.get("agent", "unknown")).strip() or "unknown",
        summary=str(body.get("summary", "")),
        paths=list(body.get("paths") or []),
        source="gateway",
        ttl_seconds=int(body.get("ttl_seconds", 1800)),
    )
    status = 200 if result["ok"] else 409
    _send_json(handler, result, status=status)


def handle_release(handler) -> None:
    """POST /release - release a task lock."""
    body = _parse_json(handler)

    from tonesoul.runtime_adapter import release_task_claim

    result = release_task_claim(
        str(body.get("task_id", "")).strip(),
        agent_id=str(body.get("agent", "")).strip() or None,
    )
    status = 200 if result["ok"] else 409
    _send_json(handler, result, status=status)


def handle_compact(handler) -> None:
    """POST /compact - write a bounded non-canonical compaction summary."""
    body = _parse_json(handler)

    from tonesoul.runtime_adapter import write_compaction

    result = write_compaction(
        agent_id=str(body.get("agent", "unknown")).strip() or "unknown",
        session_id=str(body.get("session_id", "")),
        summary=str(body.get("summary", "")),
        carry_forward=list(body.get("carry_forward") or []),
        pending_paths=list(body.get("pending_paths") or []),
        evidence_refs=list(body.get("evidence_refs") or []),
        council_dossier=(
            dict(body.get("council_dossier"))
            if isinstance(body.get("council_dossier"), dict)
            else None
        ),
        next_action=str(body.get("next_action", "")),
        source="gateway",
        ttl_seconds=int(body.get("ttl_seconds", 604800)),
        limit=int(body.get("limit", 20)),
    )
    _send_json(handler, result, status=200)


def handle_summary(handler) -> None:
    """GET /summary - text summary of current governance state."""
    from tonesoul.runtime_adapter import load, summary

    posture = load()
    _send_text(handler, summary(posture))


def handle_visitors(handler) -> None:
    """GET /visitors - recent agent visitors."""
    from tonesoul.runtime_adapter import get_recent_visitors

    visitors = get_recent_visitors(n=20)
    _send_json(handler, {"visitors": visitors})


def handle_claims(handler) -> None:
    """GET /claims - list active task claims."""
    from tonesoul.runtime_adapter import list_active_claims

    _send_json(handler, {"claims": list_active_claims()})


def handle_packet(handler) -> None:
    """GET /packet - compact R-memory packet for agent handoff."""
    from tonesoul.runtime_adapter import r_memory_packet

    _send_json(handler, r_memory_packet())


def handle_audit(handler) -> None:
    """GET /audit - Aegis integrity report."""
    from tonesoul.aegis_shield import AegisShield
    from tonesoul.store import get_store

    store = get_store()
    shield = AegisShield.load(store)
    _send_json(handler, shield.audit(store))


def handle_health(handler) -> None:
    """GET /health - heartbeat."""
    from tonesoul.store import get_store

    store = get_store()
    _send_json(handler, {"status": "ok", "backend": store.backend_name})


ROUTES_GET = {
    "/summary": handle_summary,
    "/visitors": handle_visitors,
    "/claims": handle_claims,
    "/packet": handle_packet,
    "/audit": handle_audit,
    "/health": handle_health,
}

ROUTES_POST = {
    "/load": handle_load,
    "/commit": handle_commit,
    "/claim": handle_claim,
    "/release": handle_release,
    "/compact": handle_compact,
}


class GatewayHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if not _check_auth(self):
            return
        handler = ROUTES_GET.get(self.path)
        if handler:
            try:
                handler(self)
            except Exception as exc:
                print(f"  [ERROR] GET {self.path}: {exc}")
                _send_json(self, {"error": "internal server error"}, 500)
        else:
            _send_json(self, {"error": "not found"}, 404)

    def do_POST(self) -> None:
        if not _check_auth(self):
            return
        handler = ROUTES_POST.get(self.path)
        if handler:
            try:
                handler(self)
            except Exception as exc:
                print(f"  [ERROR] POST {self.path}: {exc}")
                _send_json(self, {"error": "internal server error"}, 500)
        else:
            _send_json(self, {"error": "not found"}, 404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        method = args[0] if args else ""
        status = args[1] if len(args) > 1 else ""
        print(f"  {method} -> {status}")


def main() -> None:
    global _AUTH_TOKEN, _CORS_ORIGIN

    parser = argparse.ArgumentParser(description="ToneSoul Gateway API")
    parser.add_argument("--port", type=int, default=7700)
    parser.add_argument("--token", type=str, default=None, help="Require Bearer token")
    parser.add_argument(
        "--cors-origin",
        type=str,
        default="http://localhost:8501",
        help="Allowed CORS origin (default: http://localhost:8501)",
    )
    args = parser.parse_args()

    _AUTH_TOKEN = args.token
    _CORS_ORIGIN = args.cors_origin

    os.environ.setdefault("TONESOUL_REDIS_URL", "redis://localhost:6379/0")
    from tonesoul.store import get_store

    store = get_store()
    server = http.server.HTTPServer(("127.0.0.1", args.port), GatewayHandler)
    port = server.server_address[1]

    print(f"\n[ToneSoul Gateway] http://127.0.0.1:{port}")
    print(f"  Backend: {store.backend_name}")
    print(f"  Auth:    {'token required' if _AUTH_TOKEN else 'LOCKED — pass --token to enable'}")
    print(f"  CORS:    {_CORS_ORIGIN}")
    print("\n  POST /load      載入治理狀態 + 留足跡")
    print("  POST /commit    提交 session trace（Aegis 保護）")
    print("  POST /claim     佔用任務鎖")
    print("  POST /release   釋放任務鎖")
    print("  GET  /summary   治理狀態摘要")
    print("  GET  /visitors  最近訪客")
    print("  GET  /claims    目前任務鎖")
    print("  GET  /packet    R-memory hot-state packet")
    print("  GET  /audit     Aegis 完整性報告")
    print("\n  Ctrl+C 停止。\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Gateway] 已停止。")
        server.shutdown()


if __name__ == "__main__":
    main()
