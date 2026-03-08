from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse

import yaml

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
    return _parse_date(today_override)


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


@dataclass
class CuratedSourceSelection:
    registry_path: str
    filters: dict[str, object] = field(default_factory=dict)
    selected_urls: list[str] = field(default_factory=list)
    selected_entries: list[dict[str, Any]] = field(default_factory=list)
    skipped_entries: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ok: bool = True
    generated_at: str = field(default_factory=_iso_now)
    policy: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "registry_path": self.registry_path,
            "filters": dict(self.filters),
            "selected_url_count": len(self.selected_urls),
            "selected_urls": list(self.selected_urls),
            "selected_entry_count": len(self.selected_entries),
            "selected_entries": list(self.selected_entries),
            "skipped_entries": list(self.skipped_entries),
            "warning_count": len(self.warnings),
            "warnings": list(self.warnings),
            "policy": dict(self.policy),
            "ok": bool(self.ok),
        }


def _normalized_filters(values: Sequence[str] | None) -> set[str]:
    result: set[str] = set()
    for value in values or []:
        text = str(value).strip().lower()
        if text:
            result.add(text)
    return result


def select_curated_registry_urls(
    registry_path: Path | str,
    *,
    today: date | None = None,
    entry_ids: Sequence[str] | None = None,
    categories: Sequence[str] | None = None,
    limit: int | None = None,
    include_stale: bool = False,
) -> CuratedSourceSelection:
    path = Path(registry_path)
    payload = _read_yaml(path)
    selection = CuratedSourceSelection(
        registry_path=path.as_posix(),
        filters={
            "entry_ids": sorted(_normalized_filters(entry_ids)),
            "categories": sorted(_normalized_filters(categories)),
            "limit": None if limit is None else int(limit),
            "include_stale": bool(include_stale),
        },
    )
    if today is None:
        today = date.today()

    if not isinstance(payload, dict):
        selection.ok = False
        selection.warnings.append("registry payload is missing or invalid")
        return selection

    policy = payload.get("policy", {})
    if not isinstance(policy, dict):
        policy = {}
    allowed_hosts = set(_as_str_list(policy.get("allowed_hosts")))
    blocked_hosts = set(_as_str_list(policy.get("blocked_hosts")))
    review_cycle_days = int(policy.get("review_cycle_days", 120) or 120)
    if review_cycle_days < 1:
        review_cycle_days = 120
        selection.warnings.append("review_cycle_days was invalid and defaulted to 120")

    selection.policy = {
        "review_cycle_days": review_cycle_days,
        "allowed_hosts_count": len(allowed_hosts),
        "blocked_hosts_count": len(blocked_hosts),
    }

    entries = payload.get("registries", [])
    if not isinstance(entries, list):
        selection.ok = False
        selection.warnings.append("registries list is missing or invalid")
        return selection

    id_filter = _normalized_filters(entry_ids)
    category_filter = _normalized_filters(categories)
    seen_urls: set[str] = set()
    matched_ids: set[str] = set()
    matched_categories: set[str] = set()

    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, dict):
            selection.skipped_entries.append(
                {"id": f"entry_{index + 1}", "reason": "entry must be an object"}
            )
            continue

        entry_id = str(raw_entry.get("id") or f"entry_{index + 1}").strip()
        entry_name = str(raw_entry.get("name") or entry_id).strip()
        entry_category = str(raw_entry.get("category") or "").strip().lower()
        entry_urls = raw_entry.get("urls", [])
        reviewed_at = str(raw_entry.get("reviewed_at") or "").strip()
        rationale = str(raw_entry.get("rationale") or "").strip()

        entry_id_key = entry_id.lower()
        if id_filter and entry_id_key not in id_filter:
            continue
        if category_filter and entry_category not in category_filter:
            continue

        matched_ids.add(entry_id_key)
        if entry_category:
            matched_categories.add(entry_category)

        reviewed_date = _parse_date(reviewed_at)
        if reviewed_date is None:
            selection.skipped_entries.append(
                {"id": entry_id, "reason": f"invalid reviewed_at: {reviewed_at!r}"}
            )
            continue

        age_days = (today - reviewed_date).days
        if age_days < 0:
            selection.skipped_entries.append(
                {"id": entry_id, "reason": f"reviewed_at is in the future: {reviewed_at}"}
            )
            continue
        if age_days > review_cycle_days and not include_stale:
            selection.skipped_entries.append(
                {
                    "id": entry_id,
                    "reason": f"stale review: age_days={age_days}, max={review_cycle_days}",
                }
            )
            continue
        if age_days > review_cycle_days:
            selection.warnings.append(
                f"{entry_id} exceeds review cycle ({age_days}>{review_cycle_days}) but was included"
            )

        if not isinstance(entry_urls, list) or not entry_urls:
            selection.skipped_entries.append(
                {"id": entry_id, "reason": "entry must define a non-empty urls list"}
            )
            continue

        valid_urls: list[str] = []
        for raw_url in entry_urls:
            text_url = str(raw_url).strip()
            ok, detail, _ = _validate_url(
                text_url,
                allowed_hosts=allowed_hosts,
                blocked_hosts=blocked_hosts,
            )
            if not ok:
                selection.warnings.append(f"{entry_id}: {detail}")
                continue
            if text_url in seen_urls:
                continue
            seen_urls.add(text_url)
            valid_urls.append(text_url)

        if not valid_urls:
            selection.skipped_entries.append(
                {"id": entry_id, "reason": "entry has no valid allowlisted URLs"}
            )
            continue

        selection.selected_urls.extend(valid_urls)
        selection.selected_entries.append(
            {
                "id": entry_id,
                "name": entry_name,
                "category": entry_category,
                "reviewed_at": reviewed_at,
                "age_days": age_days,
                "url_count": len(valid_urls),
                "urls": valid_urls,
                "rationale": rationale,
            }
        )

    if id_filter:
        missing_ids = sorted(id_filter - matched_ids)
        if missing_ids:
            selection.warnings.append(f"requested ids not found: {', '.join(missing_ids)}")
    if category_filter:
        missing_categories = sorted(category_filter - matched_categories)
        if missing_categories:
            selection.warnings.append(
                f"requested categories not found: {', '.join(missing_categories)}"
            )

    if limit is not None and limit >= 0 and len(selection.selected_urls) > int(limit):
        allowed_urls = selection.selected_urls[: int(limit)]
        allowed_set = set(allowed_urls)
        trimmed_entries: list[dict[str, Any]] = []
        for entry in selection.selected_entries:
            kept_urls = [url for url in entry["urls"] if url in allowed_set]
            if not kept_urls:
                continue
            updated_entry = dict(entry)
            updated_entry["urls"] = kept_urls
            updated_entry["url_count"] = len(kept_urls)
            trimmed_entries.append(updated_entry)
        selection.selected_entries = trimmed_entries
        selection.selected_urls = allowed_urls
        selection.warnings.append(f"selected URLs truncated to limit={int(limit)}")

    if not selection.selected_urls:
        selection.ok = False
        selection.warnings.append("no approved curated source URLs were selected")

    return selection


__all__ = [
    "CuratedSourceSelection",
    "LOCAL_HOSTS",
    "_as_str_list",
    "_extract_open_source_apps",
    "_host_allowed",
    "_is_ip",
    "_iso_now",
    "_parse_date",
    "_read_yaml",
    "_resolve_today",
    "_validate_url",
    "evaluate_registry",
    "select_curated_registry_urls",
]
