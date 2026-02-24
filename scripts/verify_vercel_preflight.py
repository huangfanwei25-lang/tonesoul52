"""
Vercel production preflight checks for web/backend integration.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
SAME_ORIGIN_MARKERS = {"self", "same-origin"}


@dataclass
class SwitchValue:
    raw: str | None
    value: bool | None
    error: str | None = None


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_switch(raw: str | None) -> SwitchValue:
    if raw is None:
        return SwitchValue(raw=None, value=None, error=None)
    text = raw.strip().lower()
    if text in TRUE_VALUES:
        return SwitchValue(raw=raw, value=True, error=None)
    if text in FALSE_VALUES:
        return SwitchValue(raw=raw, value=False, error=None)
    return SwitchValue(raw=raw, value=None, error=f"invalid boolean-like value: {raw!r}")


def _validate_backend_url(
    url: str | None, allow_http: bool, same_origin: bool = False
) -> tuple[bool, str]:
    text = (url or "").strip()

    if same_origin and (not text or text.lower() in SAME_ORIGIN_MARKERS):
        return True, "same-origin backend mode enabled"

    if not text:
        return False, "TONESOUL_BACKEND_URL is missing"

    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        return False, f"TONESOUL_BACKEND_URL is not a valid absolute URL: {text!r}"

    if parsed.hostname and parsed.hostname.lower() in LOCAL_HOSTS:
        return False, f"TONESOUL_BACKEND_URL points to local host: {parsed.hostname!r}"

    if parsed.scheme.lower() != "https" and not allow_http:
        return False, "TONESOUL_BACKEND_URL must use HTTPS in production preflight"

    if parsed.path not in {"", "/"}:
        return True, "backend URL includes a path; prefer origin-only URL"

    return True, "backend URL looks valid"


def _probe_backend_health(backend_url: str, timeout: int) -> tuple[bool, str]:
    endpoint = backend_url.rstrip("/") + "/api/health"
    request = Request(endpoint, method="GET", headers={"User-Agent": "tonesoul-vercel-preflight"})
    try:
        with urlopen(request, timeout=max(1, timeout)) as response:
            status_code = int(response.getcode())
            payload_text = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return False, f"health probe HTTP error: status={exc.code}"
    except URLError as exc:
        return False, f"health probe transport error: {exc.reason}"

    if status_code != 200:
        return False, f"health probe unexpected status: {status_code}"

    try:
        payload = json.loads(payload_text) if payload_text.strip() else {}
    except json.JSONDecodeError:
        return False, "health probe returned non-JSON payload"

    status = payload.get("status")
    if status != "ok":
        return False, f"health payload status is not ok: {status!r}"
    return True, "health probe passed"


def _probe_governance_status(web_base: str, timeout: int) -> tuple[bool, str]:
    endpoint = web_base.rstrip("/") + "/api/governance-status"
    request = Request(endpoint, method="GET", headers={"User-Agent": "tonesoul-vercel-preflight"})
    try:
        with urlopen(request, timeout=max(1, timeout)) as response:
            status_code = int(response.getcode())
            payload_text = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return False, f"governance status probe HTTP error: status={exc.code}"
    except URLError as exc:
        return False, f"governance status probe transport error: {exc.reason}"

    if status_code != 200:
        return False, f"governance status probe unexpected status: {status_code}"

    try:
        payload = json.loads(payload_text) if payload_text.strip() else {}
    except json.JSONDecodeError:
        return False, "governance status probe returned non-JSON payload"

    status = payload.get("status")
    if status != "ok":
        return False, f"governance status payload status is not ok: {status!r}"

    capability = payload.get("governance_capability")
    if capability not in {"mock_only", "runtime_ready"}:
        return False, f"governance capability is invalid: {capability!r}"

    elisa = payload.get("elisa")
    if not isinstance(elisa, dict):
        return False, "governance status payload missing object field 'elisa'"

    integration_ready = elisa.get("integration_ready")
    if integration_ready is not True:
        return False, f"elisa.integration_ready must be true, got {integration_ready!r}"

    return True, "governance status probe passed"


def evaluate_preflight(
    *,
    backend_url: str | None,
    env_values: dict[str, str | None],
    allow_http: bool,
    allow_chat_mock_fallback: bool,
    same_origin: bool,
    probe_health: bool,
    web_base: str | None = None,
    probe_governance_status: bool = False,
    timeout: int,
    health_probe_fn: Callable[[str, int], tuple[bool, str]] | None = None,
    governance_probe_fn: Callable[[str, int], tuple[bool, str]] | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    backend_ok, backend_detail = _validate_backend_url(
        backend_url,
        allow_http=allow_http,
        same_origin=same_origin,
    )
    add_check("backend_url", "pass" if backend_ok else "fail", backend_detail)

    chat_fallback = _parse_switch(env_values.get("TONESOUL_ENABLE_CHAT_MOCK_FALLBACK"))
    if chat_fallback.error:
        add_check("chat_mock_fallback", "fail", chat_fallback.error)
    elif chat_fallback.value is True and not allow_chat_mock_fallback:
        add_check(
            "chat_mock_fallback",
            "fail",
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK is enabled; disable for production",
        )
    else:
        add_check("chat_mock_fallback", "pass", "mock fallback policy accepted")

    chat_mode = (env_values.get("NEXT_PUBLIC_CHAT_EXECUTION_MODE") or "").strip().lower()
    if not chat_mode:
        add_check(
            "chat_execution_mode",
            "warn",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE is unset (default is backend)",
        )
    elif chat_mode != "backend":
        add_check(
            "chat_execution_mode",
            "fail",
            f"NEXT_PUBLIC_CHAT_EXECUTION_MODE must be backend, got {chat_mode!r}",
        )
    else:
        add_check("chat_execution_mode", "pass", "chat execution mode is backend")

    legacy_chat_flag = (env_values.get("NEXT_PUBLIC_BACKEND_CHAT_FIRST") or "").strip().lower()
    if legacy_chat_flag == "0":
        add_check(
            "legacy_chat_override",
            "fail",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST=0 forces legacy provider mode",
        )
    elif legacy_chat_flag:
        add_check("legacy_chat_override", "warn", "legacy NEXT_PUBLIC_BACKEND_CHAT_FIRST is set")
    else:
        add_check("legacy_chat_override", "pass", "no legacy chat override")

    provider_fallback = _parse_switch(env_values.get("NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK"))
    if provider_fallback.error:
        add_check("chat_provider_fallback", "fail", provider_fallback.error)
    elif provider_fallback.value is True:
        add_check(
            "chat_provider_fallback",
            "fail",
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK is enabled; disable in production",
        )
    else:
        add_check("chat_provider_fallback", "pass", "chat provider fallback is disabled")

    report_mode = (env_values.get("NEXT_PUBLIC_REPORT_EXECUTION_MODE") or "").strip().lower()
    if not report_mode:
        add_check(
            "report_execution_mode",
            "warn",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE is unset (default is backend)",
        )
    elif report_mode != "backend":
        add_check(
            "report_execution_mode",
            "fail",
            f"NEXT_PUBLIC_REPORT_EXECUTION_MODE must be backend, got {report_mode!r}",
        )
    else:
        add_check("report_execution_mode", "pass", "report execution mode is backend")

    report_provider_fallback_raw = env_values.get("NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK")
    report_provider_fallback = _parse_switch(report_provider_fallback_raw)
    if report_provider_fallback_raw is None:
        add_check(
            "report_provider_fallback",
            "fail",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK is unset; set to 0 for production",
        )
    elif report_provider_fallback.error:
        add_check("report_provider_fallback", "fail", report_provider_fallback.error)
    elif report_provider_fallback.value is True:
        add_check(
            "report_provider_fallback",
            "fail",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK is enabled; disable in production",
        )
    else:
        add_check("report_provider_fallback", "pass", "report provider fallback is disabled")

    if probe_governance_status:
        web_base_text = (web_base or "").strip()
        if not web_base_text:
            add_check(
                "governance_status_probe",
                "fail",
                "web base URL is required when --probe-governance-status is enabled",
            )
        else:
            parsed_web = urlparse(web_base_text)
            if not parsed_web.scheme or not parsed_web.netloc:
                add_check(
                    "governance_status_probe",
                    "fail",
                    f"web base URL is not a valid absolute URL: {web_base_text!r}",
                )
            elif parsed_web.scheme.lower() != "https" and not allow_http:
                add_check(
                    "governance_status_probe",
                    "fail",
                    "web base URL must use HTTPS in production preflight",
                )
            else:
                probe = governance_probe_fn or _probe_governance_status
                probe_ok, probe_detail = probe(web_base_text, timeout)
                add_check(
                    "governance_status_probe",
                    "pass" if probe_ok else "fail",
                    probe_detail,
                )
    else:
        add_check("governance_status_probe", "skip", "skipped: governance probe disabled")

    if probe_health:
        backend_text = (backend_url or "").strip().lower()
        if same_origin and backend_text in {"", *SAME_ORIGIN_MARKERS}:
            add_check(
                "backend_health_probe",
                "skip",
                "skipped: same-origin mode without explicit --backend-url for probing",
            )
        elif not backend_ok:
            add_check("backend_health_probe", "skip", "skipped: backend URL is invalid")
        else:
            probe = health_probe_fn or _probe_backend_health
            probe_ok, probe_detail = probe(str(backend_url), timeout)
            add_check("backend_health_probe", "pass" if probe_ok else "fail", probe_detail)
    else:
        add_check("backend_health_probe", "skip", "skipped: probe disabled")

    failed = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warn"]
    payload = {
        "generated_at": _iso_now(),
        "ok": len(failed) == 0,
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "checks": checks,
        "backend_url": backend_url or "",
        "config": {
            "allow_http": bool(allow_http),
            "allow_chat_mock_fallback": bool(allow_chat_mock_fallback),
            "same_origin": bool(same_origin),
            "probe_health": bool(probe_health),
            "web_base": (web_base or "").strip(),
            "probe_governance_status": bool(probe_governance_status),
            "timeout": int(max(1, timeout)),
        },
    }
    return payload


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Vercel preflight configuration.")
    parser.add_argument(
        "--backend-url",
        default=None,
        help="Backend URL override. Defaults to env TONESOUL_BACKEND_URL.",
    )
    parser.add_argument("--allow-http", action="store_true", help="Allow non-HTTPS backend URL.")
    parser.add_argument(
        "--allow-chat-mock-fallback",
        action="store_true",
        help="Allow TONESOUL_ENABLE_CHAT_MOCK_FALLBACK=1 in this preflight run.",
    )
    parser.add_argument(
        "--same-origin",
        action="store_true",
        help=(
            "Allow same-origin backend mode (TONESOUL_BACKEND_URL unset/self/same-origin). "
            "Use for Vercel deployments with in-project Python functions."
        ),
    )
    parser.add_argument(
        "--probe-health",
        action="store_true",
        help="Probe <backend>/api/health.",
    )
    parser.add_argument(
        "--web-base",
        default=None,
        help="Web base URL override used by governance status probe.",
    )
    parser.add_argument(
        "--probe-governance-status",
        action="store_true",
        help="Probe <web-base>/api/governance-status for Elisa/governance readiness.",
    )
    parser.add_argument("--timeout", type=int, default=8, help="Health probe timeout seconds.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status when any fail check is detected.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    backend_url = args.backend_url or os.environ.get("TONESOUL_BACKEND_URL")
    web_base = args.web_base or os.environ.get("TONESOUL_WEB_BASE_URL")
    same_origin = (
        bool(args.same_origin)
        or _parse_switch(os.environ.get("TONESOUL_VERCEL_SAME_ORIGIN")).value is True
    )
    env_values = {
        "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": os.environ.get("TONESOUL_ENABLE_CHAT_MOCK_FALLBACK"),
        "NEXT_PUBLIC_CHAT_EXECUTION_MODE": os.environ.get("NEXT_PUBLIC_CHAT_EXECUTION_MODE"),
        "NEXT_PUBLIC_BACKEND_CHAT_FIRST": os.environ.get("NEXT_PUBLIC_BACKEND_CHAT_FIRST"),
        "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": os.environ.get(
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK"
        ),
        "NEXT_PUBLIC_REPORT_EXECUTION_MODE": os.environ.get("NEXT_PUBLIC_REPORT_EXECUTION_MODE"),
        "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": os.environ.get(
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK"
        ),
    }
    payload = evaluate_preflight(
        backend_url=backend_url,
        env_values=env_values,
        allow_http=bool(args.allow_http),
        allow_chat_mock_fallback=bool(args.allow_chat_mock_fallback),
        same_origin=same_origin,
        probe_health=bool(args.probe_health),
        web_base=web_base,
        probe_governance_status=bool(args.probe_governance_status),
        timeout=max(1, args.timeout),
    )
    _emit(payload)

    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
