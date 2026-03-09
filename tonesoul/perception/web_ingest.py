"""
Web Ingestion via Crawl4AI — turning the web into memory-ready stimuli.

This module uses Crawl4AI to fetch web content and convert it to clean
Markdown, which can then be processed by StimulusProcessor and written
to soul.db as environmental memory.

Usage:
    from tonesoul.perception.web_ingest import WebIngestor

    ingestor = WebIngestor()
    results = await ingestor.ingest_urls([
        "https://example.com/article",
        "https://example.com/docs",
    ])
    for result in results:
        print(result.title, len(result.markdown))

Author: Antigravity
Date: 2026-03-07
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class IngestResult:
    """Result of a single web page ingestion."""

    url: str
    title: str
    markdown: str
    ingested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_hash: str = ""
    word_count: int = 0
    success: bool = True
    error: Optional[str] = None

    def __post_init__(self):
        if self.markdown and not self.content_hash:
            self.content_hash = hashlib.sha256(self.markdown.encode("utf-8")).hexdigest()[:16]
        if self.markdown and not self.word_count:
            self.word_count = len(self.markdown.split())


class WebIngestor:
    """
    Crawl4AI-based web content ingestor.

    Fetches web pages and converts them to clean Markdown suitable
    for ingestion into ToneSoul's memory system.
    """

    def __init__(
        self,
        *,
        max_content_length: int = 8000,
        timeout: int = 30,
    ) -> None:
        self._max_content_length = max_content_length
        self._timeout = timeout
        self._crawl4ai_available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if Crawl4AI is installed and usable."""
        if self._crawl4ai_available is not None:
            return self._crawl4ai_available
        try:
            import crawl4ai  # noqa: F401

            self._crawl4ai_available = True
        except ImportError:
            self._crawl4ai_available = False
        return self._crawl4ai_available

    async def ingest_urls(
        self,
        urls: List[str],
        *,
        extract_links: bool = False,
    ) -> List[IngestResult]:
        """
        Ingest multiple URLs and return structured results.

        Args:
            urls: List of URLs to fetch.
            extract_links: Whether to extract and return links found in pages.

        Returns:
            List of IngestResult objects.
        """
        if not self.is_available():
            return [
                IngestResult(
                    url=url,
                    title="",
                    markdown="",
                    success=False,
                    error="Crawl4AI not installed. Run: pip install crawl4ai",
                )
                for url in urls
            ]

        results: List[IngestResult] = []
        for url in urls:
            result = await self._ingest_single(url)
            results.append(result)

        return results

    async def _ingest_single(self, url: str) -> IngestResult:
        """Ingest a single URL using Crawl4AI."""
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

            config = CrawlerRunConfig(
                word_count_threshold=10,
                excluded_tags=["nav", "footer", "header", "aside"],
                exclude_external_links=True,
            )

            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=config)

                if not result.success:
                    return IngestResult(
                        url=url,
                        title="",
                        markdown="",
                        success=False,
                        error=f"Crawl failed: {getattr(result, 'error_message', 'unknown')}",
                    )

                markdown = result.markdown or ""
                if len(markdown) > self._max_content_length:
                    markdown = markdown[: self._max_content_length] + "\n\n[... truncated]"

                title = getattr(result, "title", "") or url.split("/")[-1]

                return IngestResult(
                    url=url,
                    title=title,
                    markdown=markdown,
                    success=True,
                )

        except ImportError:
            return IngestResult(
                url=url,
                title="",
                markdown="",
                success=False,
                error="Crawl4AI not installed",
            )
        except Exception as e:
            return IngestResult(
                url=url,
                title="",
                markdown="",
                success=False,
                error=str(e)[:200],
            )

    def ingest_urls_sync(self, urls: List[str]) -> List[IngestResult]:
        """
        Synchronous wrapper for ingest_urls.

        Convenience method for non-async contexts.

        This fails fast when called from a running event loop because blocking
        the loop thread behind a sync wrapper is not a safe or predictable
        execution model for Crawl4AI-backed ingestion.
        """
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.ingest_urls(urls))
        raise RuntimeError(
            "ingest_urls_sync() cannot be called from a running event loop; "
            "await ingest_urls(...) instead."
        )
