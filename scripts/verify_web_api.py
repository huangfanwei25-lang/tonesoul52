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
        transcript = verdict.get("transcript") if isinstance(verdict, dict) else None
        mode_observability = (
            transcript.get("council_mode_observability") if isinstance(transcript, dict) else None
        )
        distillation_guard = payload.get("distillation_guard")
        response_preview = str(payload.get("response") or "")[:160]
        return {
            "response_preview": response_preview,
            "has_verdict": isinstance(verdict, dict),
            "verdict": verdict_name,
            "backend_mode": payload.get("backend_mode", "backend"),
            "execution_profile": payload.get("execution_profile"),
            "distillation_guard_level": (
                distillation_guard.get("level") if isinstance(distillation_guard, dict) else None
            ),
            "distillation_guard_policy": (
                distillation_guard.get("policy_action")
                if isinstance(distillation_guard, dict)
                else None
            ),
            "council_mode": (
                mode_observability.get("mode") if isinstance(mode_observability, dict) else None
            ),
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


def _validate_chat_council_mode(payload: Any, requested_mode: str) -> bool:
    payload_dict = _expect_dict(payload, "POST web /api/chat (mode check)")
    if payload_dict is None:
        return False
    verdict = payload_dict.get("verdict")
    if not isinstance(verdict, dict):
        print("[FAIL] POST web /api/chat (mode check): missing object field 'verdict'.")
        return False
    transcript = verdict.get("transcript")
    if not isinstance(transcript, dict):
        print("[FAIL] POST web /api/chat (mode check): missing object field 'verdict.transcript'.")
        return False
    mode_observability = transcript.get("council_mode_observability")
    if not isinstance(mode_observability, dict):
        print(
            "[FAIL] POST web /api/chat (mode check): missing object field "
            "'verdict.transcript.council_mode_observability'."
        )
        return False
    mode = mode_observability.get("mode")
    if mode != requested_mode:
        print(
            "[FAIL] POST web /api/chat (mode check): "
            f"expected mode={requested_mode!r}, got {mode!r}."
        )
        return False
    return True


def _validate_execution_profile(payload: Any, expected_profile: str, label: str) -> bool:
    payload_dict = _expect_dict(payload, label)
    if payload_dict is None:
        return False
    profile = payload_dict.get("execution_profile")
    if profile != expected_profile:
        print(f"[FAIL] {label}: expected execution_profile={expected_profile!r}, got {profile!r}.")
        return False
    return True


def _validate_distillation_guard(payload: Any, label: str) -> bool:
    payload_dict = _expect_dict(payload, label)
    if payload_dict is None:
        return False

    guard = payload_dict.get("distillation_guard")
    if guard is None:
        return True
    if not isinstance(guard, dict):
        print(f"[FAIL] {label}: distillation_guard must be an object when present.")
        return False

    level = guard.get("level")
    if level not in {"low", "medium", "high"}:
        print(f"[FAIL] {label}: invalid distillation_guard.level={level!r}.")
        return False

    policy_action = guard.get("policy_action")
    if policy_action not in {"normal", "reduce_detail", "constrain_reasoning"}:
        print(f"[FAIL] {label}: invalid distillation_guard.policy_action={policy_action!r}.")
        return False

    score = guard.get("score")
    if not isinstance(score, (int, float)):
        print(f"[FAIL] {label}: distillation_guard.score must be numeric.")
        return False

    signals = guard.get("signals")
    if not isinstance(signals, list) or any(not isinstance(signal, str) for signal in signals):
        print(f"[FAIL] {label}: distillation_guard.signals must be string list.")
        return False

    return True


def _validate_same_origin_backend_health(payload: Any, label: str) -> bool:
    payload_dict = _expect_dict(payload, label)
    if payload_dict is None:
        return False

    if payload_dict.get("ok") is not True:
        print(f"[FAIL] {label}: expected payload.ok=true.")
        return False

    backend_mode = payload_dict.get("backend_mode")
    if backend_mode != "same_origin":
        print(f"[FAIL] {label}: expected backend_mode='same_origin', got {backend_mode!r}.")
        return False

    cap = payload_dict.get("governance_capability")
    if cap is not None and cap not in {"mock_only", "runtime_ready"}:
        print(
            f"[FAIL] {label}: expected governance_capability in "
            f"{{'mock_only','runtime_ready'}}, got {cap!r}."
        )
        return False

    return True


def _validate_external_backend_health(payload: Any, label: str) -> bool:
    payload_dict = _expect_dict(payload, label)
    if payload_dict is None:
        return False

    if payload_dict.get("ok") is not True and payload_dict.get("status") != "ok":
        print(f"[FAIL] {label}: expected payload.ok=true or payload.status='ok'.")
        return False

    cap = payload_dict.get("governance_capability")
    if cap is not None and cap != "runtime_ready":
        print(f"[FAIL] {label}: expected governance_capability='runtime_ready', got {cap!r}.")
        return False

    return True


def _validate_backend_health_fallback(payload: Any, label: str) -> bool:
    payload_dict = _expect_dict(payload, label)
    if payload_dict is None:
        return False

    backend_mode = payload_dict.get("backend_mode")
    if backend_mode == "same_origin":
        return _validate_same_origin_backend_health(payload_dict, label)
    if backend_mode == "external_backend":
        return _validate_external_backend_health(payload_dict, label)

    print(
        f"[FAIL] {label}: expected backend_mode in "
        f"{{'same_origin','external_backend'}}, got {backend_mode!r}."
    )
    return False


def _build_elisa_chat_payload(conversation_id: str, session_id: str) -> Dict[str, Any]:
    return {
        "conversation_id": conversation_id,
        "session_id": session_id,
        "execution_profile": "engineering",
        "message": "Elisa integration smoke: assess governance risk for this patch.",
        "history": [{"role": "user", "content": "Review this code change for risk."}],
        "full_analysis": False,
        "council_mode": "rules",
        "perspective_config": {
            "guardian": {"mode": "rules"},
            "engineer": {"mode": "hybrid"},
        },
        "elisa_context": {
            "source": "elisa_ide",
            "session_id": session_id,
            "trigger": "post_codegen_review",
            "workspace": {
                "project_id": "tonesoul52",
                "repo": "Fan1234-1/tonesoul52",
                "branch": "master",
                "changed_files": [
                    "apps/web/src/app/api/chat/route.ts",
                    "scripts/verify_web_api.py",
                ],
            },
        },
    }


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
    parser.add_argument(
        "--check-council-modes",
        action="store_true",
        help="Run extra /api/chat checks for council_mode switching and observability.",
    )
    parser.add_argument(
        "--same-origin",
        action="store_true",
        help=(
            "Expect same-origin backend mode and verify via /api/backend-health "
            "(requires backend_mode=same_origin)."
        ),
    )
    parser.add_argument(
        "--elisa-scenario",
        action="store_true",
        help=(
            "Run additional Elisa integration payload scenario against /api/chat "
            "(session/file envelope + council settings)."
        ),
    )
    args = parser.parse_args()

    web_base = args.web_base.rstrip("/")
    api_base = args.api_base.rstrip("/")
    timeout = max(1, args.timeout)
    require_backend = bool(args.require_backend)
    verbose = bool(args.verbose)
    check_council_modes = bool(args.check_council_modes)
    same_origin = bool(args.same_origin)
    elisa_scenario = bool(args.elisa_scenario)

    all_ok = True

    # 1) Backend health
    if same_origin:
        ok, status, payload, _ = request_json(
            "GET", f"{web_base}/api/backend-health", timeout=timeout
        )
        print_result("GET web /api/backend-health", ok, status, payload, verbose)
        if not ok or not _validate_same_origin_backend_health(
            payload, "GET web /api/backend-health"
        ):
            all_ok = False
    else:
        ok, status, payload, _ = request_json("GET", f"{api_base}/api/health", timeout=timeout)
        print_result("GET backend /api/health", ok, status, payload, verbose)
        if not ok or not _validate_external_backend_health(payload, "GET backend /api/health"):
            # Auto-detect same-origin deployments where /api/health may not exist yet.
            fallback_ok, fallback_status, fallback_payload, _ = request_json(
                "GET",
                f"{web_base}/api/backend-health",
                timeout=timeout,
            )
            print_result(
                "GET web /api/backend-health (same-origin fallback)",
                fallback_ok,
                fallback_status,
                fallback_payload,
                verbose,
            )
            fallback_valid = fallback_ok and _validate_backend_health_fallback(
                fallback_payload,
                "GET web /api/backend-health (same-origin fallback)",
            )
            if fallback_valid:
                ok = True

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
    if payload_dict and not _validate_execution_profile(
        payload,
        "interactive",
        "POST web /api/chat",
    ):
        all_ok = False
    if payload_dict and not _validate_distillation_guard(payload, "POST web /api/chat"):
        all_ok = False
    if payload_dict and check_council_modes:
        for mode in ("rules", "full_llm"):
            check_ok, check_status, check_payload, _ = request_json(
                "POST",
                f"{web_base}/api/chat",
                timeout=timeout,
                json={
                    "conversation_id": conversation_id,
                    "message": f"Web API council mode smoke ({mode})",
                    "history": [{"role": "user", "content": "hello"}],
                    "full_analysis": False,
                    "council_mode": mode,
                },
            )
            print_result(
                f"POST web /api/chat mode={mode}", check_ok, check_status, check_payload, verbose
            )
            if not check_ok or not _require_backend_check(
                f"POST web /api/chat mode={mode}", check_payload, require_backend
            ):
                all_ok = False
                continue
            if not _validate_chat_council_mode(check_payload, mode):
                all_ok = False

    if elisa_scenario:
        elisa_payload = _build_elisa_chat_payload(conversation_id, session_id)
        elisa_ok, elisa_status, elisa_response, _ = request_json(
            "POST",
            f"{web_base}/api/chat",
            timeout=timeout,
            json=elisa_payload,
        )
        print_result(
            "POST web /api/chat (elisa scenario)",
            elisa_ok,
            elisa_status,
            elisa_response,
            verbose,
        )
        if not elisa_ok or not _require_backend_check(
            "POST web /api/chat (elisa scenario)",
            elisa_response,
            require_backend,
        ):
            all_ok = False
        elisa_response_dict = _expect_dict(elisa_response, "POST web /api/chat (elisa scenario)")
        if elisa_response_dict and not isinstance(elisa_response_dict.get("response"), str):
            print("[FAIL] POST web /api/chat (elisa scenario): missing string field 'response'.")
            all_ok = False
        if elisa_response_dict and not _validate_execution_profile(
            elisa_response,
            "engineering",
            "POST web /api/chat (elisa scenario)",
        ):
            all_ok = False
        if elisa_response_dict and not _validate_distillation_guard(
            elisa_response,
            "POST web /api/chat (elisa scenario)",
        ):
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
