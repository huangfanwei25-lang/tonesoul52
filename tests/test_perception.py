"""Tests for the perception module — stimulus processing without browser dependency."""

from __future__ import annotations

import asyncio

import pytest


class TestStimulusProcessor:
    """Test stimulus filtering and scoring logic."""

    def test_filters_empty_results(self):
        from tonesoul.perception.stimulus import StimulusProcessor
        from tonesoul.perception.web_ingest import IngestResult

        processor = StimulusProcessor()
        results = [
            IngestResult(url="http://a.com", title="", markdown="", success=False),
            IngestResult(url="http://b.com", title="", markdown="short", success=True),
        ]
        stimuli = processor.process_ingested(results)
        assert len(stimuli) == 0  # Both filtered: one failed, one too short

    def test_processes_valid_content(self):
        from tonesoul.perception.stimulus import StimulusProcessor
        from tonesoul.perception.web_ingest import IngestResult

        processor = StimulusProcessor(min_word_count=10)
        content = "This is a long article about AI governance and memory systems. " * 20
        results = [
            IngestResult(
                url="http://example.com/article",
                title="AI Governance Overview",
                markdown=content,
                success=True,
            )
        ]
        stimuli = processor.process_ingested(results)
        assert len(stimuli) == 1
        assert stimuli[0].topic == "AI Governance Overview"
        assert stimuli[0].relevance_score > 0  # Has relevant keywords
        assert len(stimuli[0].tags) > 0
        assert stimuli[0].observation_mode == "remote_feed"

    def test_deduplication(self):
        from tonesoul.perception.stimulus import StimulusProcessor
        from tonesoul.perception.web_ingest import IngestResult

        processor = StimulusProcessor(min_word_count=10)
        content = "Duplicate content about architecture and pipeline design. " * 10
        results = [
            IngestResult(
                url="http://a.com",
                title="Article A",
                markdown=content,
                success=True,
            ),
            IngestResult(
                url="http://b.com",
                title="Article B",
                markdown=content,  # Same content
                success=True,
            ),
        ]
        stimuli = processor.process_ingested(results)
        assert len(stimuli) == 1  # Second one deduped

    def test_relevance_scoring(self):
        from tonesoul.perception.stimulus import StimulusProcessor
        from tonesoul.perception.web_ingest import IngestResult

        processor = StimulusProcessor(min_word_count=10)

        # Highly relevant
        relevant_content = (
            "This paper discusses AI governance, memory systems, "
            "tension computation, and council deliberation architecture. " * 10
        )
        # Low relevance
        irrelevant_content = (
            "Today we baked cookies and went to the park. "
            "The weather was wonderful and birds were singing. " * 10
        )

        results = [
            IngestResult(
                url="http://relevant.com",
                title="Relevant",
                markdown=relevant_content,
                success=True,
            ),
            IngestResult(
                url="http://irrelevant.com",
                title="Irrelevant",
                markdown=irrelevant_content,
                success=True,
            ),
        ]
        stimuli = processor.process_ingested(results)
        assert len(stimuli) == 2
        relevant_stim = [s for s in stimuli if "relevant" in s.source_url.lower()][0]
        irrelevant_stim = [s for s in stimuli if "irrelevant" in s.source_url.lower()][0]
        assert relevant_stim.relevance_score > irrelevant_stim.relevance_score

    def test_chinese_keywords_drive_relevance_and_tags(self):
        from tonesoul.perception.stimulus import StimulusProcessor
        from tonesoul.perception.web_ingest import IngestResult

        processor = StimulusProcessor(min_word_count=10)
        content = (
            "這篇文章討論 AI 治理、記憶系統、管線架構與語義審議，" "也觸及倫理與意識問題。 " * 12
        )
        results = [
            IngestResult(
                url="http://example.com/zh",
                title="治理與記憶",
                markdown=content,
                success=True,
            )
        ]

        stimuli = processor.process_ingested(results)

        assert len(stimuli) == 1
        assert stimuli[0].relevance_score > 0
        assert "governance" in stimuli[0].tags
        assert "memory" in stimuli[0].tags
        assert "architecture" in stimuli[0].tags

    def test_to_memory_payload(self):
        from tonesoul.perception.stimulus import EnvironmentStimulus

        stimulus = EnvironmentStimulus(
            source_url="http://example.com",
            topic="Test Topic",
            summary="Test summary",
            content_hash="abc123",
            ingested_at="2026-03-07T00:00:00Z",
            relevance_score=0.75,
            novelty_score=0.5,
            tags=["ai", "governance"],
        )
        payload = stimulus.to_memory_payload()
        assert payload["type"] == "environment_stimulus"
        assert payload["relevance_score"] == 0.75
        assert "ai" in payload["tags"]
        assert payload["observation_mode"] == "remote_feed"

    def test_observation_mode_normalizes_unknown_values(self):
        from tonesoul.perception.stimulus import EnvironmentStimulus

        stimulus = EnvironmentStimulus(
            source_url="http://example.com",
            topic="Test Topic",
            summary="Test summary",
            content_hash="abc123",
            ingested_at="2026-03-07T00:00:00Z",
            observation_mode="satellite",
        )

        payload = stimulus.to_memory_payload()

        assert payload["observation_mode"] == "remote_feed"


class TestWebIngestor:
    """Test WebIngestor without actually crawling."""

    def test_ingest_result_dataclass(self):
        from tonesoul.perception.web_ingest import IngestResult

        result = IngestResult(
            url="http://test.com",
            title="Test",
            markdown="Hello world " * 100,
            success=True,
        )
        assert result.word_count == 200
        assert len(result.content_hash) == 16

    def test_ingestor_reports_availability(self):
        from tonesoul.perception.web_ingest import WebIngestor

        ingestor = WebIngestor()
        # Should report True after Crawl4AI is installed
        available = ingestor.is_available()
        assert isinstance(available, bool)

    def test_ingest_urls_sync_runs_outside_event_loop(self, monkeypatch):
        from tonesoul.perception.web_ingest import IngestResult, WebIngestor

        ingestor = WebIngestor()

        async def _fake_ingest(urls):
            return [
                IngestResult(
                    url=str(urls[0]),
                    title="Example",
                    markdown="Hello world " * 20,
                    success=True,
                )
            ]

        monkeypatch.setattr(ingestor, "ingest_urls", _fake_ingest)

        results = ingestor.ingest_urls_sync(["http://example.com"])

        assert len(results) == 1
        assert results[0].success is True

    def test_ingest_urls_sync_rejects_running_event_loop(self):
        from tonesoul.perception.web_ingest import WebIngestor

        ingestor = WebIngestor()

        async def _exercise():
            with pytest.raises(
                RuntimeError,
                match="cannot be called from a running event loop",
            ):
                ingestor.ingest_urls_sync(["http://example.com"])

        asyncio.run(_exercise())
