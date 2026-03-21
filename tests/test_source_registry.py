from __future__ import annotations

from datetime import date
from pathlib import Path
from textwrap import dedent

from tonesoul.perception.source_registry import select_curated_registry_urls


def _write_registry(path: Path, body: str) -> Path:
    path.write_text(dedent(body).strip() + "\n", encoding="utf-8")
    return path


def test_select_curated_registry_urls_filters_by_id_and_limit(tmp_path: Path) -> None:
    registry_path = _write_registry(
        tmp_path / "external_source_registry.yaml",
        """
        policy:
          review_cycle_days: 120
          allowed_hosts:
            - "example.org"
            - "docs.example.org"
          blocked_hosts:
            - "bit.ly"
        registries:
          - id: "alpha"
            name: "Alpha"
            category: "research"
            urls:
              - "https://example.org/a"
              - "https://docs.example.org/b"
            reviewed_at: "2026-03-01"
          - id: "beta"
            name: "Beta"
            category: "research"
            urls:
              - "https://example.org/a"
              - "https://example.org/c"
              - "https://example.org/d"
            reviewed_at: "2026-03-01"
          - id: "gamma"
            name: "Gamma"
            category: "news"
            urls:
              - "https://example.org/d"
            reviewed_at: "2026-03-01"
        """,
    )

    selection = select_curated_registry_urls(
        registry_path,
        today=date(2026, 3, 7),
        entry_ids=["alpha", "beta"],
        limit=3,
    )

    assert selection.ok is True
    assert selection.selected_urls == [
        "https://example.org/a",
        "https://docs.example.org/b",
        "https://example.org/c",
    ]
    assert [entry["id"] for entry in selection.selected_entries] == ["alpha", "beta"]
    assert any("truncated to limit=3" in item for item in selection.warnings)


def test_select_curated_registry_urls_filters_by_category(tmp_path: Path) -> None:
    registry_path = _write_registry(
        tmp_path / "external_source_registry.yaml",
        """
        policy:
          review_cycle_days: 120
          allowed_hosts:
            - "example.org"
          blocked_hosts: []
        registries:
          - id: "research_alpha"
            name: "Research Alpha"
            category: "research"
            urls:
              - "https://example.org/research"
            reviewed_at: "2026-03-01"
          - id: "news_alpha"
            name: "News Alpha"
            category: "news"
            urls:
              - "https://example.org/news"
            reviewed_at: "2026-03-01"
        """,
    )

    selection = select_curated_registry_urls(
        registry_path,
        today=date(2026, 3, 7),
        categories=["news"],
    )

    assert selection.ok is True
    assert selection.selected_urls == ["https://example.org/news"]
    assert [entry["id"] for entry in selection.selected_entries] == ["news_alpha"]


def test_select_curated_registry_urls_skips_stale_unless_opted_in(tmp_path: Path) -> None:
    registry_path = _write_registry(
        tmp_path / "external_source_registry.yaml",
        """
        policy:
          review_cycle_days: 30
          allowed_hosts:
            - "example.org"
          blocked_hosts: []
        registries:
          - id: "stale_alpha"
            name: "Stale Alpha"
            category: "research"
            urls:
              - "https://example.org/stale"
            reviewed_at: "2025-12-01"
        """,
    )

    skipped = select_curated_registry_urls(
        registry_path,
        today=date(2026, 3, 7),
    )
    included = select_curated_registry_urls(
        registry_path,
        today=date(2026, 3, 7),
        include_stale=True,
    )

    assert skipped.ok is False
    assert skipped.selected_urls == []
    assert skipped.skipped_entries[0]["id"] == "stale_alpha"
    assert "stale review" in skipped.skipped_entries[0]["reason"]
    assert included.ok is True
    assert included.selected_urls == ["https://example.org/stale"]
    assert any("was included" in item for item in included.warnings)
