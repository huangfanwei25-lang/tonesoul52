from __future__ import annotations

from tonesoul.memory.soul_db import MemoryLayer, MemorySource, SqliteSoulDB
from tonesoul.memory.write_gateway import ENVIRONMENT_STIMULUS_TYPE, MemoryWriteGateway
from tonesoul.perception.stimulus import EnvironmentStimulus
from tonesoul.perception.web_ingest import IngestResult


def _build_stimulus(
    *,
    source_url: str = "https://example.com/article",
    topic: str = "AI Governance Update",
    summary: str = "A note about governance and memory convergence.",
    content_hash: str = "abc123def456",
    ingested_at: str = "2026-03-07T12:00:00Z",
) -> EnvironmentStimulus:
    return EnvironmentStimulus(
        source_url=source_url,
        topic=topic,
        summary=summary,
        content_hash=content_hash,
        ingested_at=ingested_at,
        relevance_score=0.82,
        novelty_score=0.41,
        tags=["ai", "governance"],
        raw_excerpt="governance memory architecture",
    )


def test_gateway_persists_environment_stimulus_into_sqlite(tmp_path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    result = gateway.write_environment_stimuli([_build_stimulus()])
    records = gateway.stream_environment_stimuli()

    assert result.written == 1
    assert result.skipped == 0
    assert result.rejected == 0
    assert len(result.record_ids) == 1
    assert len(records) == 1
    assert records[0].source == MemorySource.CUSTOM
    assert records[0].layer == MemoryLayer.WORKING.value
    assert records[0].payload["type"] == ENVIRONMENT_STIMULUS_TYPE
    assert records[0].payload["timestamp"] == "2026-03-07T12:00:00Z"
    assert records[0].payload["observation_mode"] == "remote_feed"
    assert records[0].payload["evidence"][0] == "governance memory architecture"
    assert records[0].payload["provenance"]["source_url"] == "https://example.com/article"
    assert records[0].payload["provenance"]["observation_mode"] == "remote_feed"
    assert "environment" in records[0].payload["tags"]
    assert "perception" in records[0].payload["tags"]
    assert "observation:remote_feed" in records[0].payload["tags"]
    assert "governance" in records[0].tags


def test_gateway_dedupes_existing_environment_content_hashes(tmp_path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    stimulus = _build_stimulus(content_hash="repeat-me")

    first = gateway.write_environment_stimuli([stimulus])
    second = gateway.write_environment_stimuli([stimulus])

    assert first.written == 1
    assert second.written == 0
    assert second.skipped == 1
    assert len(gateway.stream_environment_stimuli()) == 1


def test_gateway_filters_environment_records_from_custom_stream(tmp_path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    db.append(
        MemorySource.CUSTOM,
        {
            "type": "handoff",
            "timestamp": "2026-03-07T11:00:00Z",
            "summary": "other custom memory",
            "layer": "working",
        },
    )

    gateway.write_environment_stimuli([_build_stimulus(content_hash="only-env")])
    records = gateway.stream_environment_stimuli()

    assert len(records) == 1
    assert records[0].payload["type"] == ENVIRONMENT_STIMULUS_TYPE


def test_gateway_integrates_processor_output_across_sessions(tmp_path) -> None:
    from tonesoul.perception.stimulus import StimulusProcessor

    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    content = "This article discusses AI governance, memory systems, and pipeline design. " * 20

    first_processor = StimulusProcessor(min_word_count=10)
    first_stimuli = first_processor.process_ingested(
        [
            IngestResult(
                url="https://example.com/a",
                title="Governance Note",
                markdown=content,
                success=True,
            )
        ]
    )
    first_result = gateway.write_environment_stimuli(first_stimuli)

    second_processor = StimulusProcessor(min_word_count=10)
    second_stimuli = second_processor.process_ingested(
        [
            IngestResult(
                url="https://example.com/b",
                title="Same Governance Note",
                markdown=content,
                success=True,
            )
        ]
    )
    second_result = gateway.write_environment_stimuli(second_stimuli)

    records = gateway.stream_environment_stimuli()

    assert first_result.written == 1
    assert second_result.written == 0
    assert second_result.skipped == 1
    assert len(records) == 1
    assert records[0].payload["type"] == ENVIRONMENT_STIMULUS_TYPE
    assert records[0].layer == MemoryLayer.WORKING.value
    assert records[0].payload["topic"] == "Governance Note"
    assert records[0].payload["observation_mode"] == "remote_feed"
