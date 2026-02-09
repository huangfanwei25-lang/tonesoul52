"""
ToneSoul Web API smoke check.

Verifies Next.js API routes and backend health together.
Assumes web app and backend are already running.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional, Tuple

import requests


def request_json(
    method: str, url: str, timeout: int = 10, **kwargs: Any
) -> Tuple[bool, int, Any, str]:
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        error_payload = {"error": str(exc), "error_type": exc.__class__.__name__}
        return False, 0, error_payload, str(exc)
    try:
        payload = response.json()
    except ValueError:
        payload = None
    ok = 200 <= response.status_code < 300
    return ok, response.status_code, payload, response.text


def _stdout_is_utf8() -> bool:
    encoding = (sys.stdout.encoding or "").lower().replace("-", "")
    return encoding.startswith("utf8")


def _json_dump(payload: Any) -> str:
    # Non-UTF8 terminals can display mojibake; escape non-ASCII for readable diagnostics.
    return json.dumps(payload, ensure_ascii=not _stdout_is_utf8(), indent=2)


def _summarize_payload(label: str, payload: Any, verbose: bool) -> Any:
    if verbose or not isinstance(payload, dict):
        return payload

    if label == "POST web /api/chat":
        verdict = payload.get("verdict")
        verdict_name = verdict.get("verdict") if isinstance(verdict, dict) else None
        response_preview = str(payload.get("response") or "")[:160]
        return {
            "response_preview": response_preview,
            "has_verdict": isinstance(verdict, dict),
            "verdict": verdict_name,
            "backend_mode": payload.get("backend_mode", "backend"),
        }

    if label == "POST web /api/session-report":
        report = payload.get("report")
        summary_preview = ""
        report_keys: list[str] = []
        if isinstance(report, dict):
            summary_preview = str(report.get("summary_text") or "")[:160]
            report_keys = sorted(report.keys())
        return {
            "success": payload.get("success"),
            "backend_mode": payload.get("backend_mode", "backend"),
            "report_keys": report_keys,
            "summary_preview": summary_preview,
        }

    return payload


def print_result(label: str, ok: bool, status: int, payload: Any, verbose: bool) -> None:
    status_label = "OK" if ok else "FAIL"
    status_text = str(status) if status > 0 else "N/A"
    print(f"[{status_label}] {label} (HTTP {status_text})")
    if isinstance(payload, dict) and "backend_mode" in payload:
        print(f"  backend_mode: {payload.get('backend_mode')}")
    if payload is not None:
        print(_json_dump(_summarize_payload(label, payload, verbose)))


def _require_backend_check(
    label: str,
    payload: Any,
    require_backend: bool,
) -> bool:
    if not require_backend:
        return True
    if isinstance(payload, dict) and payload.get("backend_mode") == "mock_fallback":
        print(f"[FAIL] {label}: backend fallback detected while --require-backend is enabled.")
        return False
    return True


def _expect_dict(payload: Any, label: str) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, dict):
        print(f"[FAIL] {label}: expected JSON object payload.")
        return None
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="ToneSoul web API smoke check")
    parser.add_argument(
        "--web-base",
        default="http://localhost:3000",
        help="Base URL for Next.js web app",
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:5000",
        help="Base URL for Flask backend",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--require-backend",
        action="store_true",
        help="Fail if any web route returns backend_mode=mock_fallback",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full payload instead of summarized payload for large endpoints.",
    )
    args = parser.parse_args()

    web_base = args.web_base.rstrip("/")
    api_base = args.api_base.rstrip("/")
    timeout = max(1, args.timeout)
    require_backend = bool(args.require_backend)
    verbose = bool(args.verbose)

    all_ok = True

    # 1) Backend health
    ok, status, payload, _ = request_json("GET", f"{api_base}/api/health", timeout=timeout)
    print_result("GET backend /api/health", ok, status, payload, verbose)
    if not ok and require_backend:
        return 1
    if not ok:
        all_ok = False

    # 2) Web conversation create
    ok, status, payload, _ = request_json(
        "POST",
        f"{web_base}/api/conversation",
        timeout=timeout,
        json={"session_id": "web_smoke_session"},
    )
    print_result("POST web /api/conversation", ok, status, payload, verbose)
    if not ok or not _require_backend_check("POST web /api/conversation", payload, require_backend):
        all_ok = False
    conversation_id = "web_smoke_conversation"
    session_id = "web_smoke_session"
    payload_dict = _expect_dict(payload, "POST web /api/conversation")
    if payload_dict:
        conversation_id = str(payload_dict.get("conversation_id") or conversation_id)
        session_id = str(payload_dict.get("session_id") or session_id)

    # 3) Web consent create
    ok, status, payload, _ = request_json(
        "POST",
        f"{web_base}/api/consent",
        timeout=timeout,
        json={"consent_type": "analysis", "session_id": session_id},
    )
    print_result("POST web /api/consent", ok, status, payload, verbose)
    if not ok or not _require_backend_check("POST web /api/consent", payload, require_backend):
        all_ok = False
    payload_dict = _expect_dict(payload, "POST web /api/consent")
    if payload_dict:
        session_id = str(payload_dict.get("session_id") or session_id)

    # 4) Web chat
    ok, status, payload, _ = request_json(
        "POST",
        f"{web_base}/api/chat",
        timeout=timeout,
        json={
            "conversation_id": conversation_id,
            "message": "Web API smoke test message",
            "history": [{"role": "user", "content": "hello"}],
            "full_analysis": False,
        },
    )
    print_result("POST web /api/chat", ok, status, payload, verbose)
    if not ok or not _require_backend_check("POST web /api/chat", payload, require_backend):
        all_ok = False
    payload_dict = _expect_dict(payload, "POST web /api/chat")
    if payload_dict and not isinstance(payload_dict.get("response"), str):
        print("[FAIL] POST web /api/chat: missing string field 'response'.")
        all_ok = False

    # 5) Web session report
    ok, status, payload, _ = request_json(
        "POST",
        f"{web_base}/api/session-report",
        timeout=timeout,
        json={
            "history": [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
                {"role": "user", "content": "can you summarize"},
                {"role": "assistant", "content": "yes"},
            ]
        },
    )
    print_result("POST web /api/session-report", ok, status, payload, verbose)
    if not ok or not _require_backend_check(
        "POST web /api/session-report", payload, require_backend
    ):
        all_ok = False
    payload_dict = _expect_dict(payload, "POST web /api/session-report")
    if payload_dict and not isinstance(payload_dict.get("report"), dict):
        print("[FAIL] POST web /api/session-report: missing object field 'report'.")
        all_ok = False

    # 6) Web consent delete
    ok, status, payload, _ = request_json(
        "DELETE",
        f"{web_base}/api/consent",
        timeout=timeout,
        json={"session_id": session_id},
    )
    print_result("DELETE web /api/consent", ok, status, payload, verbose)
    if not ok or not _require_backend_check("DELETE web /api/consent", payload, require_backend):
        all_ok = False

    if all_ok:
        print("Web API smoke check completed.")
        return 0
    print("Web API smoke check completed with failures.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
