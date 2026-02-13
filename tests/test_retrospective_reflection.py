"""Test retrospective memory reflection heuristics."""

from __future__ import annotations

import pytest

from tonesoul.memory.decay import apply_retrospective, retrospective_score
from tonesoul.memory.soul_db import MemoryRecord, MemorySource


def test_topic_match_boosts_score():
    payload = {"text": "We discussed honesty and trust"}
    adjustment = retrospective_score(
        payload,
        current_topics=["honesty"],
        active_commitments=[],
    )
    assert adjustment > 0


def test_commitment_match_boosts_score():
    payload = {"text": "I promised to always be transparent"}
    adjustment = retrospective_score(
        payload,
        current_topics=[],
        active_commitments=["transparent"],
    )
    assert adjustment > 0


def test_stale_record_penalized():
    payload = {"text": "old memory", "access_count": 0}
    adjustment = retrospective_score(
        payload,
        current_topics=[],
        active_commitments=[],
    )
    assert adjustment < 0


def test_accessed_record_not_penalized():
    payload = {"text": "accessed memory", "access_count": 3}
    adjustment = retrospective_score(
        payload,
        current_topics=[],
        active_commitments=[],
    )
    assert adjustment >= 0


def test_combined_boost_and_penalty():
    payload = {"text": "honesty matters", "access_count": 0}
    adjustment = retrospective_score(
        payload,
        current_topics=["honesty"],
        active_commitments=[],
    )
    assert adjustment == pytest.approx(0.2)


def test_adjustment_clamped_to_supported_range():
    payload = {"text": "neutral"}
    adjustment = retrospective_score(
        payload,
        current_topics=[],
        active_commitments=[],
    )
    assert -0.5 <= adjustment <= 0.5


def test_apply_retrospective_returns_new_records_without_mutation():
    records = [
        MemoryRecord(
            source=MemorySource.SELF_JOURNAL,
            timestamp="2026-01-01",
            payload={"text": "honesty is important"},
            relevance_score=0.5,
        )
    ]
    result = apply_retrospective(records, current_topics=["honesty"])

    assert len(result) == 1
    assert result[0].relevance_score > records[0].relevance_score
    assert records[0].relevance_score == 0.5
