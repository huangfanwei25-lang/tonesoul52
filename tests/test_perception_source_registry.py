"""Tests for tonesoul.perception.source_registry — pure helpers and evaluate_registry."""

from __future__ import annotations

from datetime import date, datetime

import yaml

from tonesoul.perception.source_registry import (
    CuratedSourceSelection,
    _as_str_list,
    _extract_open_source_apps,
    _host_allowed,
    _is_ip,
    _iso_now,
    _normalized_filters,
    _parse_date,
    _resolve_today,
    _validate_url,
    evaluate_registry,
    select_curated_registry_urls,
)

# ── _iso_now ──────────────────────────────────────────────────────────────────


class TestIsoNow:
    def test_returns_string(self):
        assert isinstance(_iso_now(), str)

    def test_ends_with_z(self):
        assert _iso_now().endswith("Z")

    def test_parseable(self):
        ts = _iso_now()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ── _as_str_list ──────────────────────────────────────────────────────────────


class TestAsStrList:
    def test_non_list_returns_empty(self):
        assert _as_str_list("not-a-list") == []
        assert _as_str_list(None) == []

    def test_converts_to_lowercase_stripped(self):
        result = _as_str_list(["  GITHUB.COM  ", "example.org"])
        assert "github.com" in result
        assert "example.org" in result

    def test_none_items_skipped(self):
        result = _as_str_list([None, "github.com"])
        assert None not in result
        assert "github.com" in result

    def test_empty_strings_filtered(self):
        result = _as_str_list(["", "  ", "x.com"])
        assert "" not in result
        assert "  " not in result


# ── _host_allowed ─────────────────────────────────────────────────────────────


class TestHostAllowed:
    def test_exact_match(self):
        assert _host_allowed("github.com", {"github.com", "example.com"}) is True

    def test_not_in_list(self):
        assert _host_allowed("evil.com", {"github.com"}) is False

    def test_wildcard_subdomain_match(self):
        assert _host_allowed("api.github.com", {"*.github.com"}) is True

    def test_wildcard_non_match_different_suffix(self):
        assert _host_allowed("api.evil.com", {"*.github.com"}) is False

    def test_wildcard_requires_subdomain(self):
        # bare domain doesn't match *.github.com
        assert _host_allowed("github.com", {"*.github.com"}) is False

    def test_empty_allowed_hosts(self):
        assert _host_allowed("github.com", set()) is False


# ── _is_ip ────────────────────────────────────────────────────────────────────


class TestIsIp:
    def test_ipv4_is_ip(self):
        assert _is_ip("192.168.1.1") is True

    def test_ipv6_is_ip(self):
        assert _is_ip("::1") is True

    def test_hostname_not_ip(self):
        assert _is_ip("github.com") is False

    def test_localhost_not_ip(self):
        assert _is_ip("localhost") is False


# ── _validate_url ─────────────────────────────────────────────────────────────


class TestValidateUrl:
    def _call(self, url, allowed=None, blocked=None):
        return _validate_url(
            url,
            allowed_hosts=allowed or {"github.com", "pypi.org"},
            blocked_hosts=blocked or set(),
        )

    def test_valid_https_url_accepted(self):
        ok, _, host = self._call("https://github.com/foo/bar")
        assert ok is True
        assert host == "github.com"

    def test_empty_url_fails(self):
        ok, msg, _ = self._call("")
        assert ok is False
        assert "missing" in msg.lower()

    def test_http_rejected(self):
        ok, msg, _ = self._call("http://github.com/repo")
        assert ok is False
        assert "HTTPS" in msg

    def test_localhost_rejected(self):
        ok, msg, _ = self._call("https://localhost/path")
        assert ok is False
        assert "localhost" in msg

    def test_ip_rejected(self):
        ok, msg, _ = self._call("https://192.168.1.1/path")
        assert ok is False

    def test_blocked_host_rejected(self):
        ok, msg, _ = self._call(
            "https://blocked.com/path", allowed={"blocked.com"}, blocked={"blocked.com"}
        )
        assert ok is False

    def test_non_allowlisted_host_rejected(self):
        ok, msg, _ = self._call("https://unknown.com/path")
        assert ok is False
        assert "allowlist" in msg

    def test_url_with_userinfo_rejected(self):
        ok, msg, _ = self._call("https://user:pass@github.com/repo")
        assert ok is False
        assert "userinfo" in msg

    def test_relative_url_rejected(self):
        ok, msg, _ = self._call("github.com/repo")
        assert ok is False


# ── _parse_date ───────────────────────────────────────────────────────────────


class TestParseDate:
    def test_valid_date(self):
        result = _parse_date("2026-01-15")
        assert result == date(2026, 1, 15)

    def test_invalid_format_returns_none(self):
        assert _parse_date("15/01/2026") is None

    def test_empty_returns_none(self):
        assert _parse_date("") is None

    def test_gibberish_returns_none(self):
        assert _parse_date("not-a-date") is None


# ── _resolve_today ────────────────────────────────────────────────────────────


class TestResolveToday:
    def test_none_returns_today(self):
        today = _resolve_today(None)
        assert today == date.today()

    def test_valid_string_returns_parsed(self):
        result = _resolve_today("2026-06-01")
        assert result == date(2026, 6, 1)

    def test_invalid_string_returns_none(self):
        assert _resolve_today("invalid") is None


# ── _extract_open_source_apps ─────────────────────────────────────────────────


class TestExtractOpenSourceApps:
    def test_list_of_dicts(self):
        payload = [
            {"name": "App1", "repo": "https://github.com/x/y", "website": ""},
        ]
        apps = _extract_open_source_apps(payload)
        assert len(apps) == 1
        assert apps[0]["name"] == "App1"

    def test_dict_with_apps_key(self):
        payload = {"apps": [{"name": "App2", "repo": "https://github.com/a/b"}]}
        apps = _extract_open_source_apps(payload)
        assert len(apps) == 1

    def test_nested_app_key(self):
        payload = [{"app": {"name": "App3", "repo_url": "https://github.com/c/d"}}]
        apps = _extract_open_source_apps(payload)
        assert len(apps) == 1

    def test_empty_returns_empty(self):
        assert _extract_open_source_apps([]) == []

    def test_none_returns_empty(self):
        assert _extract_open_source_apps(None) == []

    def test_repo_url_fallback(self):
        payload = [{"repo_url": "https://github.com/a/b"}]
        apps = _extract_open_source_apps(payload)
        assert apps[0]["repo"] == "https://github.com/a/b"


# ── _normalized_filters ───────────────────────────────────────────────────────


class TestNormalizedFilters:
    def test_lowercases(self):
        result = _normalized_filters(["GITHUB", "PyPI"])
        assert "github" in result
        assert "pypi" in result

    def test_strips_whitespace(self):
        result = _normalized_filters(["  foo  "])
        assert "foo" in result

    def test_empty_strings_excluded(self):
        result = _normalized_filters(["", "  "])
        assert "" not in result

    def test_none_input_empty_set(self):
        assert _normalized_filters(None) == set()

    def test_deduplicates(self):
        result = _normalized_filters(["foo", "FOO"])
        assert len(result) == 1


# ── evaluate_registry ─────────────────────────────────────────────────────────


class TestEvaluateRegistry:
    def _today(self):
        return date(2026, 4, 22)

    def _payload(self, registries=None, policy=None):
        return {
            "policy": policy
            or {
                "allowed_hosts": ["github.com"],
                "blocked_hosts": [],
                "review_cycle_days": 120,
            },
            "registries": registries or [],
        }

    def test_non_dict_payload_fails(self):
        result = evaluate_registry(
            registry_payload=None,
            apps_payload=None,
            today=self._today(),
        )
        assert result["ok"] is False

    def test_empty_allowed_hosts_fails(self):
        payload = self._payload(policy={"allowed_hosts": [], "review_cycle_days": 120})
        result = evaluate_registry(
            registry_payload=payload,
            apps_payload=None,
            today=self._today(),
        )
        assert result["ok"] is False

    def test_empty_registries_fails(self):
        result = evaluate_registry(
            registry_payload=self._payload(),
            apps_payload=None,
            today=self._today(),
        )
        assert result["ok"] is False

    def test_valid_registry_passes(self):
        registries = [
            {
                "id": "reg-1",
                "urls": ["https://github.com/foo/bar"],
                "reviewed_at": "2026-03-01",
            }
        ]
        result = evaluate_registry(
            registry_payload=self._payload(registries=registries),
            apps_payload=None,
            today=self._today(),
        )
        assert result["ok"] is True

    def test_stale_registry_fails(self):
        registries = [
            {
                "id": "reg-1",
                "urls": ["https://github.com/foo/bar"],
                "reviewed_at": "2025-01-01",  # Very old
            }
        ]
        result = evaluate_registry(
            registry_payload=self._payload(registries=registries),
            apps_payload=None,
            today=self._today(),
        )
        assert result["ok"] is False

    def test_result_has_required_keys(self):
        result = evaluate_registry(
            registry_payload=self._payload(),
            apps_payload=None,
            today=self._today(),
        )
        for k in ("generated_at", "ok", "failed_count", "warning_count", "checks", "policy"):
            assert k in result


# ── CuratedSourceSelection.to_dict ────────────────────────────────────────────


class TestCuratedSourceSelectionToDict:
    def test_all_keys_present(self):
        sel = CuratedSourceSelection(registry_path="/tmp/reg.yaml")
        d = sel.to_dict()
        for k in (
            "generated_at",
            "registry_path",
            "filters",
            "selected_url_count",
            "selected_urls",
            "selected_entry_count",
            "selected_entries",
            "skipped_entries",
            "warning_count",
            "warnings",
            "policy",
            "ok",
        ):
            assert k in d

    def test_counts_accurate(self):
        sel = CuratedSourceSelection(
            registry_path="/tmp",
            selected_urls=["https://example.com/a", "https://example.com/b"],
        )
        d = sel.to_dict()
        assert d["selected_url_count"] == 2


# ── select_curated_registry_urls (basic) ──────────────────────────────────────


class TestSelectCuratedRegistryUrls:
    def _write_registry(self, tmp_path, entries=None, policy=None):
        content = {
            "policy": policy
            or {
                "allowed_hosts": ["github.com"],
                "blocked_hosts": [],
                "review_cycle_days": 120,
            },
            "registries": entries or [],
        }
        f = tmp_path / "registry.yaml"
        f.write_text(yaml.dump(content), encoding="utf-8")
        return f

    def test_missing_file_fails(self, tmp_path):
        sel = select_curated_registry_urls(tmp_path / "missing.yaml", today=date(2026, 4, 22))
        assert sel.ok is False

    def test_empty_registries_no_urls(self, tmp_path):
        path = self._write_registry(tmp_path)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22))
        assert sel.ok is False
        assert sel.selected_urls == []

    def test_valid_entry_included(self, tmp_path):
        entries = [
            {
                "id": "reg-1",
                "name": "Test",
                "category": "code",
                "urls": ["https://github.com/foo/bar"],
                "reviewed_at": "2026-03-01",
            }
        ]
        path = self._write_registry(tmp_path, entries=entries)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22))
        assert "https://github.com/foo/bar" in sel.selected_urls

    def test_stale_entry_excluded_by_default(self, tmp_path):
        entries = [
            {
                "id": "stale",
                "urls": ["https://github.com/stale/repo"],
                "reviewed_at": "2024-01-01",  # Very old
            }
        ]
        path = self._write_registry(tmp_path, entries=entries)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22))
        assert "https://github.com/stale/repo" not in sel.selected_urls

    def test_stale_entry_included_with_flag(self, tmp_path):
        entries = [
            {
                "id": "stale",
                "urls": ["https://github.com/stale/repo"],
                "reviewed_at": "2024-01-01",
            }
        ]
        path = self._write_registry(tmp_path, entries=entries)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22), include_stale=True)
        assert "https://github.com/stale/repo" in sel.selected_urls

    def test_limit_truncates_urls(self, tmp_path):
        entries = [
            {
                "id": f"reg-{i}",
                "urls": [f"https://github.com/foo/bar{i}"],
                "reviewed_at": "2026-03-01",
            }
            for i in range(5)
        ]
        path = self._write_registry(tmp_path, entries=entries)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22), limit=2)
        assert len(sel.selected_urls) == 2

    def test_category_filter_applied(self, tmp_path):
        entries = [
            {
                "id": "a",
                "category": "code",
                "urls": ["https://github.com/a/b"],
                "reviewed_at": "2026-03-01",
            },
            {
                "id": "b",
                "category": "docs",
                "urls": ["https://github.com/c/d"],
                "reviewed_at": "2026-03-01",
            },
        ]
        path = self._write_registry(tmp_path, entries=entries)
        sel = select_curated_registry_urls(path, today=date(2026, 4, 22), categories=["code"])
        ids = [e["id"] for e in sel.selected_entries]
        assert "a" in ids
        assert "b" not in ids
