from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.memory.decay import HALF_LIFE_DAYS, calculate_decay
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.stats import average_coherence, count_by_verdict, most_common_divergence
from tonesoul.memory.subjectivity_admissibility import (
    build_record_axiomatic_admissibility_checklist,
)
from tonesoul.memory.write_gateway import MemoryWriteGateway
from tonesoul.perception.stimulus import EnvironmentStimulus


def _stimulus(
    *,
    summary: str = "A governance note with memory implications.",
    ingested_at: str = "2026-03-20T12:00:00Z",
    content_hash: str = "memory-lifecycle-hash",
) -> EnvironmentStimulus:
    return EnvironmentStimulus(
        source_url="https://example.com/lifecycle",
        topic="Governance Memory Lifecycle",
        summary=summary,
        content_hash=content_hash,
        ingested_at=ingested_at,
        relevance_score=0.81,
        novelty_score=0.52,
        tags=["governance", "memory"],
        raw_excerpt="governance memory lifecycle integration",
    )


def test_gateway_write_then_stream_then_query_round_trip(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    write_result = gateway.write_environment_stimuli([_stimulus()])
    streamed = gateway.stream_environment_stimuli(limit=1)
    queried = list(db.query(MemorySource.CUSTOM, limit=5))

    assert write_result.written == 1
    assert len(streamed) == 1
    assert queried[-1].payload["topic"] == "Governance Memory Lifecycle"


def test_decay_query_prefers_recent_memory_over_stale_records(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    now = datetime(2026, 3, 20, tzinfo=timezone.utc)
    old_time = (now - timedelta(days=HALF_LIFE_DAYS * 4)).isoformat().replace("+00:00", "Z")
    recent_time = (now - timedelta(hours=2)).isoformat().replace("+00:00", "Z")

    recent_id = db.append(
        MemorySource.CUSTOM,
        {"text": "recent governance note", "timestamp": recent_time, "relevance_score": 0.8},
    )
    db.append(
        MemorySource.CUSTOM,
        {"text": "stale governance note", "timestamp": old_time, "relevance_score": 0.8},
    )

    decayed = list(db.query(MemorySource.CUSTOM, apply_decay=True, now=now))

    assert decayed
    assert decayed[0].record_id == recent_id


def test_crystallizer_persists_rules_from_repeated_patterns(tmp_path: Path) -> None:
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=2)

    crystals = crystallizer.crystallize(
        {
            "verdicts": {"block": 3, "approve": 2},
            "collapse_warnings": {"same-pattern": 2},
        }
    )
    loaded = crystallizer.load_crystals()

    assert len(crystals) >= 2
    assert len(loaded) == len(crystals)
    assert crystal_path.exists()


def test_crystallizer_retrieval_refresh_updates_freshness_summary(tmp_path: Path) -> None:
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    crystals = crystallizer.crystallize({"verdicts": {"block": 2}})

    crystallizer.record_retrieval(crystals)
    summary = crystallizer.freshness_summary()

    assert summary["total_crystals"] >= 1
    assert summary["active_count"] >= 1


def test_subjectivity_admissibility_derives_governance_direction_from_record() -> None:
    checklist = build_record_axiomatic_admissibility_checklist(
        {
            "topic": "Council breaker threshold",
            "summary": "Governance threshold and breaker escalation need review.",
            "source_url": "https://example.com/governance",
            "source_record_ids": ["r1", "r2"],
        },
        summary="governance council breaker threshold review",
    )

    assert checklist["derived_direction"] == "governance_escalation"
    assert "authority_and_exception_pressure" in checklist["status_line"]


def test_memory_stats_summarize_consolidated_entries() -> None:
    entries = [
        {"verdict": {"verdict": "approve"}, "coherence": {"overall": 0.8}},
        {
            "transcript": {
                "verdict": {"decision": "block"},
                "divergence_analysis": {"object": ["risk"], "concern": ["risk"]},
                "coherence": {"overall": 0.4},
            }
        },
        {"verdict": "approve", "coherence": 0.6},
    ]

    assert count_by_verdict(entries) == {"approve": 2, "block": 1}
    assert most_common_divergence(entries) == "risk"
    assert average_coherence(entries) == pytest.approx(0.6)


def test_decay_curve_distinguishes_fresh_from_old_records() -> None:
    fresh = calculate_decay(1.0, 0.0, access_count=0)
    stale = calculate_decay(1.0, HALF_LIFE_DAYS * 4, access_count=0)

    assert fresh == 1.0
    assert stale < fresh
