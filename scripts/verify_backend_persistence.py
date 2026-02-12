"""
ToneSoul backend persistence acceptance check.

Runs an end-to-end API flow against a deployed backend:
- health
- create conversation
- chat write
- read conversations
- read conversation detail
- read audit logs
- read status
- read memories
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Tuple

import requests


def request_json(
    method: str,
    url: str,
    *,
    timeout: int,
    **kwargs: Any,
) -> Tuple[bool, int, Any, str]:
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        payload = {"error": str(exc), "error_type": exc.__class__.__name__}
        return False, 0, payload, str(exc)
    try:
        payload = response.json()
    except ValueError:
        payload = None
    ok = 200 <= response.status_code < 300
    return ok, response.status_code, payload, response.text


def _stdout_is_utf8() -> bool:
    encoding = (sys.stdout.encoding or "").lower().replace("-", "")
    return encoding.startswith("utf8")


def _dump_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=not _stdout_is_utf8(), indent=2)


def print_result(label: str, ok: bool, status: int, payload: Any) -> None:
    marker = "OK" if ok else "FAIL"
    status_text = str(status) if status > 0 else "N/A"
    print(f"[{marker}] {label} (HTTP {status_text})")
    if payload is not None:
        print(_dump_json(payload))


def _expect_dict(payload: Any, label: str) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        return payload
    print(f"[FAIL] {label}: expected JSON object")
    return None


def _expect_list(value: Any, label: str) -> list[Any] | None:
    if isinstance(value, list):
        return value
    print(f"[FAIL] {label}: expected JSON array")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="ToneSoul backend persistence acceptance check")
    parser.add_argument(
        "--base",
        default="https://tonesoul52.onrender.com",
        help="Backend base URL",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--allow-disabled-persistence",
        action="store_true",
        help="Do not fail when persistence.enabled=false in /api/health and /api/status",
    )
    parser.add_argument(
        "--delete-after",
        action="store_true",
        help="Delete the generated conversation at the end",
    )
    parser.add_argument(
        "--read-token",
        default="",
        help="Optional read API token for protected read endpoints",
    )
    args = parser.parse_args()

    base = args.base.rstrip("/")
    timeout = max(3, int(args.timeout))
    require_persistence = not args.allow_disabled_persistence
    read_headers = (
        {"Authorization": f"Bearer {args.read_token.strip()}"}
        if isinstance(args.read_token, str) and args.read_token.strip()
        else {}
    )

    session_id = f"acceptance_{int(time.time())}"
    conversation_id = ""
    all_ok = True

    # 1) Health
    ok, status, payload, _ = request_json("GET", f"{base}/api/health", timeout=timeout)
    print_result("GET /api/health", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/health")
    persistence_enabled = False
    if payload_dict is not None:
        persistence = payload_dict.get("persistence")
        if isinstance(persistence, dict):
            persistence_enabled = bool(persistence.get("enabled"))
    if not ok or payload_dict is None:
        return 1
    if require_persistence and not persistence_enabled:
        print("[FAIL] /api/health reports persistence.enabled=false")
        return 1

    # 2) Create conversation
    ok, status, payload, _ = request_json(
        "POST",
        f"{base}/api/conversation",
        timeout=timeout,
        json={"session_id": session_id},
    )
    print_result("POST /api/conversation", ok, status, payload)
    payload_dict = _expect_dict(payload, "POST /api/conversation")
    if not ok or payload_dict is None:
        return 1
    conversation_id = str(payload_dict.get("conversation_id") or "")
    if not conversation_id:
        print("[FAIL] POST /api/conversation: missing conversation_id")
        return 1

    # 3) Chat write
    ok, status, payload, _ = request_json(
        "POST",
        f"{base}/api/chat",
        timeout=timeout,
        json={
            "conversation_id": conversation_id,
            "session_id": session_id,
            "message": "Backend persistence acceptance check",
            "history": [],
            "full_analysis": False,
        },
    )
    print_result("POST /api/chat", ok, status, payload)
    payload_dict = _expect_dict(payload, "POST /api/chat")
    if not ok or payload_dict is None:
        return 1
    if not isinstance(payload_dict.get("response"), str):
        print("[FAIL] POST /api/chat: missing string field 'response'")
        return 1

    # 4) Conversations list
    ok, status, payload, _ = request_json(
        "GET",
        f"{base}/api/conversations?limit=50&offset=0",
        timeout=timeout,
        headers=read_headers,
    )
    print_result("GET /api/conversations", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/conversations")
    if not ok or payload_dict is None:
        return 1
    conversations = _expect_list(
        payload_dict.get("conversations"), "GET /api/conversations.conversations"
    )
    if conversations is None:
        return 1
    if require_persistence and persistence_enabled:
        found = any(
            isinstance(item, dict) and str(item.get("id") or "") == conversation_id
            for item in conversations
        )
        if not found:
            print(
                "[WARN] created conversation not found in first page of /api/conversations; "
                "continuing with detail lookup"
            )
            all_ok = False

    # 5) Conversation detail
    ok, status, payload, _ = request_json(
        "GET",
        f"{base}/api/conversations/{conversation_id}",
        timeout=timeout,
        headers=read_headers,
    )
    print_result("GET /api/conversations/<id>", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/conversations/<id>")
    if not ok or payload_dict is None:
        return 1
    conversation = payload_dict.get("conversation")
    if not isinstance(conversation, dict):
        print("[FAIL] GET /api/conversations/<id>: missing object field 'conversation'")
        return 1
    messages = _expect_list(
        conversation.get("messages"), "GET /api/conversations/<id>.conversation.messages"
    )
    if messages is None:
        return 1
    roles = {
        str(message.get("role"))
        for message in messages
        if isinstance(message, dict) and message.get("role") is not None
    }
    if require_persistence and persistence_enabled and not {"user", "assistant"}.issubset(roles):
        print("[FAIL] conversation detail does not contain both user and assistant messages")
        return 1

    # 6) Audit logs
    ok, status, payload, _ = request_json(
        "GET",
        f"{base}/api/audit-logs?limit=20&offset=0",
        timeout=timeout,
        headers=read_headers,
    )
    print_result("GET /api/audit-logs", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/audit-logs")
    if not ok or payload_dict is None:
        return 1
    logs = _expect_list(payload_dict.get("logs"), "GET /api/audit-logs.logs")
    if logs is None:
        return 1

    # 7) Status
    ok, status, payload, _ = request_json("GET", f"{base}/api/status", timeout=timeout)
    print_result("GET /api/status", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/status")
    if not ok or payload_dict is None:
        return 1
    status_persistence = payload_dict.get("persistence")
    if require_persistence and (
        not isinstance(status_persistence, dict) or not bool(status_persistence.get("enabled"))
    ):
        print("[FAIL] /api/status reports persistence.enabled=false")
        return 1

    # 8) Memories
    ok, status, payload, _ = request_json(
        "GET",
        f"{base}/api/memories?limit=10",
        timeout=timeout,
        headers=read_headers,
    )
    print_result("GET /api/memories", ok, status, payload)
    payload_dict = _expect_dict(payload, "GET /api/memories")
    if not ok or payload_dict is None:
        return 1
    memories = _expect_list(payload_dict.get("memories"), "GET /api/memories.memories")
    if memories is None:
        return 1

    # 9) Optional cleanup
    if args.delete_after and conversation_id:
        ok, status, payload, _ = request_json(
            "DELETE",
            f"{base}/api/conversations/{conversation_id}",
            timeout=timeout,
            headers=read_headers,
        )
        print_result("DELETE /api/conversations/<id>", ok, status, payload)
        if not ok:
            all_ok = False

    if all_ok:
        print("Backend persistence acceptance check passed.")
        return 0

    print("Backend persistence acceptance check completed with warnings.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
