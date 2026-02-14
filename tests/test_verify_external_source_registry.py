from datetime import date

import scripts.verify_external_source_registry as verify_registry


def _registry_payload() -> dict:
    return {
        "policy": {
            "review_cycle_days": 90,
            "allowed_hosts": ["github.com", "gitlab.com", "example.org", "docs.example.org"],
            "blocked_hosts": ["bit.ly"],
        },
        "registries": [
            {
                "id": "trusted_example",
                "name": "Trusted Example",
                "category": "test",
                "urls": ["https://example.org/docs"],
                "reviewed_at": "2026-02-01",
            }
        ],
    }


def _apps_payload() -> dict:
    return {
        "apps": [
            {
                "app": {
                    "name": "Sample App",
                    "repo": "https://github.com/example/sample-app",
                    "website": "https://docs.example.org/project",
                }
            }
        ]
    }


def test_validate_url_rejects_http_scheme() -> None:
    ok, detail, host = verify_registry._validate_url(
        "http://example.org/docs",
        allowed_hosts={"example.org"},
        blocked_hosts=set(),
    )
    assert ok is False
    assert host == ""
    assert "HTTPS" in detail


def test_evaluate_registry_passes_for_allowlisted_sources() -> None:
    payload = verify_registry.evaluate_registry(
        registry_payload=_registry_payload(),
        apps_payload=_apps_payload(),
        today=date(2026, 2, 14),
    )
    assert payload["ok"] is True
    assert payload["failed_count"] == 0


def test_evaluate_registry_fails_for_non_allowlisted_host() -> None:
    registry = _registry_payload()
    registry["registries"][0]["urls"] = ["https://malicious.example.net/docs"]
    payload = verify_registry.evaluate_registry(
        registry_payload=registry,
        apps_payload=_apps_payload(),
        today=date(2026, 2, 14),
    )
    assert payload["ok"] is False
    assert any("not in allowlist" in check["detail"] for check in payload["checks"])


def test_evaluate_registry_fails_for_stale_review_date() -> None:
    registry = _registry_payload()
    registry["registries"][0]["reviewed_at"] = "2025-01-01"
    payload = verify_registry.evaluate_registry(
        registry_payload=registry,
        apps_payload=_apps_payload(),
        today=date(2026, 2, 14),
    )
    assert payload["ok"] is False
    assert any("stale review" in check["detail"] for check in payload["checks"])


def test_evaluate_registry_requires_github_repo_for_shared_apps() -> None:
    apps = _apps_payload()
    apps["apps"][0]["app"]["repo"] = "https://gitlab.com/example/sample-app"
    payload = verify_registry.evaluate_registry(
        registry_payload=_registry_payload(),
        apps_payload=apps,
        today=date(2026, 2, 14),
    )
    assert payload["ok"] is False
    assert any("repo host must be github.com" in check["detail"] for check in payload["checks"])
