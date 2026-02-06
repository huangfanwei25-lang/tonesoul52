"""
ToneSoul API smoke check.
Assumes the API server is already running.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Tuple

import requests


def request_json(method: str, url: str, **kwargs: Any) -> Tuple[bool, int, Any, str]:
    response = requests.request(method, url, timeout=10, **kwargs)
    try:
        payload = response.json()
    except ValueError:
        payload = None
    ok = 200 <= response.status_code < 300
    return ok, response.status_code, payload, response.text


def _stdout_is_utf8() -> bool:
    encoding = (sys.stdout.encoding or "").lower().replace("-", "")
    return encoding.startswith("utf8")


def print_result(label: str, ok: bool, status: int, payload: Any) -> None:
    status_label = "OK" if ok else "FAIL"
    print(f"[{status_label}] {label} (HTTP {status})")
    if payload is not None:
        print(json.dumps(payload, ensure_ascii=not _stdout_is_utf8(), indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="ToneSoul API smoke check")
    parser.add_argument(
        "--base",
        default="http://localhost:5000",
        help="Base URL for the API server",
    )
    args = parser.parse_args()

    base = args.base.rstrip("/")

    ok, status, payload, _ = request_json("GET", f"{base}/api/health")
    print_result("GET /api/health", ok, status, payload)
    if not ok:
        return 1

    ok, status, payload, _ = request_json(
        "POST",
        f"{base}/api/validate",
        json={
            "draft_output": "Test message for council validation.",
            "context": {},
            "user_intent": "smoke_check",
        },
    )
    print_result("POST /api/validate", ok, status, payload)
    if not ok:
        return 1

    ok, status, payload, _ = request_json("GET", f"{base}/api/memories?limit=3")
    print_result("GET /api/memories", ok, status, payload)
    if not ok:
        return 1

    ok, status, payload, _ = request_json("GET", f"{base}/api/consolidate")
    print_result("GET /api/consolidate", ok, status, payload)
    if not ok:
        return 1

    ok, status, payload, _ = request_json(
        "POST",
        f"{base}/api/conversation",
        json={"session_id": "smoke_session"},
    )
    print_result("POST /api/conversation", ok, status, payload)
    if not ok:
        return 1

    ok, status, payload, _ = request_json(
        "POST",
        f"{base}/api/consent",
        json={"consent_type": "analysis", "session_id": "smoke_session"},
    )
    print_result("POST /api/consent", ok, status, payload)
    if not ok:
        return 1

    session_id = "smoke_session"
    if isinstance(payload, dict) and payload.get("session_id"):
        session_id = str(payload["session_id"])

    ok, status, payload, _ = request_json("DELETE", f"{base}/api/consent/{session_id}")
    print_result("DELETE /api/consent/<session_id>", ok, status, payload)
    if not ok:
        return 1

    print("Smoke check completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
