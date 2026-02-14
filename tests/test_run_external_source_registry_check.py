from pathlib import Path

import scripts.run_external_source_registry_check as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_render_markdown_includes_failure_section() -> None:
    payload = {
        "generated_at": "2026-02-14T00:00:00Z",
        "ok": False,
        "failed_count": 1,
        "warning_count": 1,
        "checks": [
            {"name": "policy.allowed_hosts", "status": "pass", "detail": "loaded"},
            {"name": "app:demo:repo", "status": "fail", "detail": "not in allowlist"},
            {"name": "open_source_apps", "status": "warn", "detail": "empty"},
        ],
    }
    markdown = runner._render_markdown(payload)
    assert "# External Source Registry Latest" in markdown
    assert "| app:demo:repo | FAIL | not in allowlist |" in markdown
    assert "## Failures" in markdown
    assert "## Warnings" in markdown


def test_run_check_ok_with_valid_registry_and_apps(tmp_path: Path) -> None:
    _write(
        tmp_path / "spec" / "external_source_registry.yaml",
        """
policy:
  review_cycle_days: 120
  allowed_hosts:
    - github.com
    - example.org
  blocked_hosts:
    - bit.ly
registries:
  - id: test
    name: Test
    category: sample
    urls:
      - https://example.org/docs
    reviewed_at: "2026-02-14"
""".strip() + "\n",
    )
    _write(
        tmp_path / "spec" / "open_source_apps.yaml",
        """
apps:
  - app:
      name: Demo
      repo: https://github.com/example/demo
      website: https://example.org/demo
""".strip() + "\n",
    )

    payload = runner.run_check(
        repo_root=tmp_path,
        registry_relpath="spec/external_source_registry.yaml",
        open_source_apps_relpath="spec/open_source_apps.yaml",
        today_override="2026-02-14",
    )
    assert payload["ok"] is True
    assert payload["failed_count"] == 0


def test_run_check_fails_on_invalid_today_override(tmp_path: Path) -> None:
    payload = runner.run_check(
        repo_root=tmp_path,
        registry_relpath="spec/external_source_registry.yaml",
        open_source_apps_relpath="spec/open_source_apps.yaml",
        today_override="2026-99-99",
    )
    assert payload["ok"] is False
    assert payload["checks"][0]["name"] == "today"
