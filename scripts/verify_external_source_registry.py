"""
Verify external source allowlist policy and shared open-source URLs.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _read_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _extract_open_source_apps(payload: Any) -> list[dict[str, Any]]:
    apps: list[dict[str, Any]] = []

    def add_item(item: Any) -> None:
        if not isinstance(item, dict):
            return
        app = item.get("app", item)
        if not isinstance(app, dict):
            return
        name = str(app.get("name") or app.get("title") or f"app_{len(apps) + 1}")
        apps.append(
            {
                "name": name,
                "repo": str(app.get("repo") or app.get("repo_url") or app.get("url") or ""),
                "website": str(app.get("website") or ""),
            }
        )

    if isinstance(payload, dict):
        entries = payload.get("apps")
        if isinstance(entries, list):
            for entry in entries:
                add_item(entry)
        else:
            add_item(payload)
    elif isinstance(payload, list):
        for entry in payload:
            add_item(entry)

    return apps


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip().lower()
        if text:
            result.append(text)
    return result


def _host_allowed(host: str, allowed_hosts: set[str]) -> bool:
    if host in allowed_hosts:
        return True
    for candidate in allowed_hosts:
        if not candidate.startswith("*."):
            continue
        suffix = candidate[2:]
        if suffix and host.endswith("." + suffix):
            return True
    return False


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def _validate_url(
    url: str,
    *,
    allowed_hosts: set[str],
    blocked_hosts: set[str],
) -> tuple[bool, str, str]:
    text = (url or "").strip()
    if not text:
        return False, "URL is missing", ""

    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        return False, f"URL is not absolute: {text!r}", ""
    if parsed.scheme.lower() != "https":
        return False, f"URL must use HTTPS: {text!r}", ""
    if parsed.username or parsed.password:
        return False, "URL must not include userinfo", ""

    host = (parsed.hostname or "").strip().lower()
    if not host:
        return False, f"URL host is missing: {text!r}", ""
    if host in LOCAL_HOSTS:
        return False, f"URL host points to localhost: {host}", host
    if _is_ip(host):
        return False, f"URL host must not be an IP literal: {host}", host
    if host in blocked_hosts:
        return False, f"URL host is blocked by policy: {host}", host
    if not _host_allowed(host, allowed_hosts):
        return False, f"URL host is not in allowlist: {host}", host

    return True, "URL accepted", host


def _parse_date(value: str) -> date | None:
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def _resolve_today(today_override: str | None) -> date | None:
    if today_override is None:
        return date.today()
    parsed = _parse_date(today_override)
    return parsed


def evaluate_registry(
    *,
    registry_payload: Any,
    apps_payload: Any,
    today: date,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    if not isinstance(registry_payload, dict):
        add_check("registry_payload", "fail", "registry payload is missing or invalid")
        failed = [item for item in checks if item["status"] == "fail"]
        return {
            "generated_at": _iso_now(),
            "ok": False,
            "failed_count": len(failed),
            "warning_count": 0,
            "checks": checks,
            "policy": {},
        }

    policy = registry_payload.get("policy", {})
    if not isinstance(policy, dict):
        policy = {}

    allowed_hosts = set(_as_str_list(policy.get("allowed_hosts")))
    blocked_hosts = set(_as_str_list(policy.get("blocked_hosts")))
    review_cycle_days = int(policy.get("review_cycle_days", 120) or 120)

    if not allowed_hosts:
        add_check("policy.allowed_hosts", "fail", "allowed_hosts must not be empty")
    else:
        add_check("policy.allowed_hosts", "pass", f"allowlist loaded ({len(allowed_hosts)} hosts)")

    if review_cycle_days < 1:
        add_check("policy.review_cycle_days", "fail", "review_cycle_days must be >= 1")
        review_cycle_days = 120
    else:
        add_check(
            "policy.review_cycle_days",
            "pass",
            f"review cycle set to {review_cycle_days} days",
        )

    registries = registry_payload.get("registries", [])
    if not isinstance(registries, list):
        registries = []
        add_check("registries", "fail", "registries must be a list")
    elif not registries:
        add_check("registries", "fail", "registries list is empty")
    else:
        add_check("registries", "pass", f"{len(registries)} registry entries found")

    for index, entry in enumerate(registries):
        if not isinstance(entry, dict):
            add_check(f"registry[{index}]", "fail", "entry must be an object")
            continue

        entry_id = str(entry.get("id") or f"entry_{index + 1}")
        urls = entry.get("urls", [])
        if not isinstance(urls, list) or not urls:
            add_check(
                f"registry:{entry_id}:urls", "fail", "entry must define a non-empty urls list"
            )
        else:
            for url_index, raw_url in enumerate(urls):
                ok, detail, _ = _validate_url(
                    str(raw_url),
                    allowed_hosts=allowed_hosts,
                    blocked_hosts=blocked_hosts,
                )
                add_check(
                    f"registry:{entry_id}:url[{url_index}]",
                    "pass" if ok else "fail",
                    detail,
                )

        reviewed_at = str(entry.get("reviewed_at") or "")
        reviewed_date = _parse_date(reviewed_at)
        if reviewed_date is None:
            add_check(
                f"registry:{entry_id}:reviewed_at",
                "fail",
                f"invalid reviewed_at date: {reviewed_at!r}",
            )
            continue
        age_days = (today - reviewed_date).days
        if age_days < 0:
            add_check(
                f"registry:{entry_id}:reviewed_at",
                "fail",
                f"reviewed_at is in the future: {reviewed_at}",
            )
        elif age_days > review_cycle_days:
            add_check(
                f"registry:{entry_id}:reviewed_at",
                "fail",
                f"stale review: age_days={age_days}, max={review_cycle_days}",
            )
        else:
            add_check(
                f"registry:{entry_id}:reviewed_at",
                "pass",
                f"review age ok: {age_days} days",
            )

    apps = _extract_open_source_apps(apps_payload)
    if not apps:
        add_check("open_source_apps", "warn", "no open-source app entries detected")
    else:
        add_check("open_source_apps", "pass", f"{len(apps)} app entries found")

    for app in apps:
        app_name = app["name"]
        repo = app["repo"]
        website = app["website"]

        if not repo:
            add_check(f"app:{app_name}:repo", "fail", "repo URL is missing")
        else:
            repo_ok, repo_detail, repo_host = _validate_url(
                repo,
                allowed_hosts=allowed_hosts,
                blocked_hosts=blocked_hosts,
            )
            if repo_ok and repo_host != "github.com":
                repo_ok = False
                repo_detail = f"repo host must be github.com, got {repo_host}"
            add_check(f"app:{app_name}:repo", "pass" if repo_ok else "fail", repo_detail)

        if website:
            website_ok, website_detail, _ = _validate_url(
                website,
                allowed_hosts=allowed_hosts,
                blocked_hosts=blocked_hosts,
            )
            add_check(
                f"app:{app_name}:website",
                "pass" if website_ok else "fail",
                website_detail,
            )
        else:
            add_check(f"app:{app_name}:website", "warn", "website URL is missing")

    failed = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warn"]
    return {
        "generated_at": _iso_now(),
        "ok": len(failed) == 0,
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "checks": checks,
        "policy": {
            "review_cycle_days": review_cycle_days,
            "allowed_hosts_count": len(allowed_hosts),
            "blocked_hosts_count": len(blocked_hosts),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify external source registry and open-source URL allowlist."
    )
    parser.add_argument(
        "--registry",
        default="spec/external_source_registry.yaml",
        help="Registry YAML path.",
    )
    parser.add_argument(
        "--open-source-apps",
        default="spec/open_source_apps.yaml",
        help="Open-source apps YAML path.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Date override in YYYY-MM-DD for deterministic checks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when checks fail.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    today = _resolve_today(args.today)
    if today is None:
        payload = {
            "generated_at": _iso_now(),
            "ok": False,
            "failed_count": 1,
            "warning_count": 0,
            "checks": [
                {
                    "name": "today",
                    "status": "fail",
                    "detail": f"invalid --today value: {args.today!r}",
                }
            ],
        }
        _emit(payload)
        return 1

    registry_path = Path(args.registry)
    apps_path = Path(args.open_source_apps)
    payload = evaluate_registry(
        registry_payload=_read_yaml(registry_path),
        apps_payload=_read_yaml(apps_path),
        today=today,
    )
    payload["inputs"] = {
        "registry": str(registry_path),
        "open_source_apps": str(apps_path),
        "today": today.isoformat(),
    }
    _emit(payload)

    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
