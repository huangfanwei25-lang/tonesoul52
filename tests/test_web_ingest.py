from __future__ import annotations

import builtins
import hashlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

from tonesoul.perception.web_ingest import IngestResult, WebIngestor


def _fake_crawl4ai_module(
    *, result: object | None = None, error: Exception | None = None
) -> ModuleType:
    module = ModuleType("crawl4ai")

    class AsyncWebCrawler:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def arun(self, *, url, config):
            del url, config
            if error is not None:
                raise error
            return result

    class CrawlerRunConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    module.AsyncWebCrawler = AsyncWebCrawler
    module.CrawlerRunConfig = CrawlerRunConfig
    return module


def test_ingest_result_dataclass_defaults() -> None:
    result = IngestResult(url="https://example.com", title="Example", markdown="")

    assert result.content_hash == ""
    assert result.word_count == 0
    assert result.success is True
    assert result.error is None
    assert result.ingested_at != ""


def test_ingest_result_post_init_hash() -> None:
    result = IngestResult(url="https://example.com", title="Example", markdown="hello world")

    assert result.content_hash == hashlib.sha256("hello world".encode("utf-8")).hexdigest()[:16]
    assert result.word_count == 2


def test_is_available_without_crawl4ai(monkeypatch) -> None:
    original_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "crawl4ai":
            raise ImportError("missing crawl4ai")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    ingestor = WebIngestor()

    assert ingestor.is_available() is False


def test_ingest_urls_sync_mock(monkeypatch) -> None:
    ingestor = WebIngestor()

    async def _fake_ingest(_urls, *, extract_links=False):
        assert extract_links is False
        return [
            IngestResult(
                url="https://example.com/a",
                title="Example",
                markdown="hello world",
            )
        ]

    monkeypatch.setattr(ingestor, "ingest_urls", _fake_ingest)

    results = ingestor.ingest_urls_sync(["https://example.com/a"])

    assert len(results) == 1
    assert results[0].title == "Example"
    assert results[0].success is True


@pytest.mark.asyncio
async def test_ingest_error_handling(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules,
        "crawl4ai",
        _fake_crawl4ai_module(error=RuntimeError("boom failure")),
    )
    ingestor = WebIngestor()
    ingestor._crawl4ai_available = True

    result = await ingestor._ingest_single("https://example.com/error")

    assert result.success is False
    assert result.error == "boom failure"


@pytest.mark.asyncio
async def test_max_content_length_truncation(monkeypatch) -> None:
    monkeypatch.setitem(
        sys.modules,
        "crawl4ai",
        _fake_crawl4ai_module(
            result=SimpleNamespace(
                success=True,
                markdown="word " * 50,
                title="Long page",
            )
        ),
    )
    ingestor = WebIngestor(max_content_length=40)
    ingestor._crawl4ai_available = True

    result = await ingestor._ingest_single("https://example.com/long")

    assert result.success is True
    assert result.title == "Long page"
    assert result.markdown.endswith("[... truncated]")
