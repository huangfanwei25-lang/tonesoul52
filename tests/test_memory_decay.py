from __future__ import annotations

import pytest

from tonesoul.memory.decay import (
    ACCESS_BOOST,
    FORGET_THRESHOLD,
    HALF_LIFE_DAYS,
    apply_retrospective,
    calculate_decay,
    retrospective_score,
    should_forget,
)
from tonesoul.memory.soul_db import MemoryRecord, MemorySource


def test_no_decay_at_time_zero():
    assert calculate_decay(1.0, 0.0) == 1.0


def test_half_decay_at_half_life():
    score = calculate_decay(1.0, HALF_LIFE_DAYS)
    assert abs(score - 0.5) < 0.01


def test_access_boosts_relevance():
    base = calculate_decay(1.0, 14.0)
    boosted = calculate_decay(1.0, 14.0, access_count=3)
    assert boosted > base


def test_should_forget_below_threshold():
    assert should_forget(0.05)
    assert not should_forget(0.2)


def test_clamped_to_unit_range():
    assert calculate_decay(1.0, 0.0, access_count=100) <= 1.0
    assert calculate_decay(-1.0, 10.0) >= 0.0


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestCalculateDecayDetails:
    def test_negative_days_treated_as_zero(self):
        assert calculate_decay(0.5, -5.0) == calculate_decay(0.5, 0.0)

    def test_zero_initial_relevance_stays_zero(self):
        assert calculate_decay(0.0, 10.0) == 0.0

    def test_access_boost_per_access(self):
        base = calculate_decay(0.3, 0.0, access_count=0)
        one_access = calculate_decay(0.3, 0.0, access_count=1)
        assert one_access == pytest.approx(base + ACCESS_BOOST, abs=1e-6)

    def test_decay_at_two_half_lives_is_quarter(self):
        score = calculate_decay(1.0, HALF_LIFE_DAYS * 2)
        assert abs(score - 0.25) < 0.01

    def test_forget_threshold_boundary(self):
        assert should_forget(FORGET_THRESHOLD - 0.001)
        assert not should_forget(FORGET_THRESHOLD)


class TestRetrospectiveScore:
    def test_matching_topic_adds_adjustment(self):
        score = retrospective_score(
            {"text": "governance framework"},
            current_topics=["governance"],
            active_commitments=[],
        )
        assert score > 0.0

    def test_matching_commitment_adds_adjustment(self):
        score = retrospective_score(
            {"content": "follow the protocol"},
            current_topics=[],
            active_commitments=["protocol"],
        )
        assert score > 0.0

    def test_zero_access_count_subtracts_point_one(self):
        no_access = retrospective_score(
            {"text": "irrelevant", "access_count": 0},
            current_topics=[],
            active_commitments=[],
        )
        assert no_access == pytest.approx(-0.1, abs=1e-6)

    def test_positive_access_count_no_penalty(self):
        score = retrospective_score(
            {"text": "irrelevant", "access_count": 5},
            current_topics=[],
            active_commitments=[],
        )
        assert score == pytest.approx(0.0, abs=1e-6)

    def test_result_clamped_to_half(self):
        score = retrospective_score(
            {"text": "governance protocol", "access_count": 100},
            current_topics=["governance"],
            active_commitments=["protocol"],
        )
        assert score <= 0.5

    def test_empty_topics_and_commitments_no_boost(self):
        score = retrospective_score(
            {"text": "anything", "access_count": 1},
            current_topics=[],
            active_commitments=[],
        )
        assert score == pytest.approx(0.0, abs=1e-6)

    def test_invalid_access_count_treated_as_zero(self):
        score = retrospective_score(
            {"text": "test", "access_count": "bad"},
            current_topics=[],
            active_commitments=[],
        )
        assert score == pytest.approx(-0.1, abs=1e-6)


class TestApplyRetrospective:
    def _record(self, text: str, relevance: float = 0.5, access: int = 1) -> MemoryRecord:
        return MemoryRecord(
            source=MemorySource.CUSTOM,
            timestamp="2026-01-01T00:00:00Z",
            payload={"text": text, "access_count": access},
            relevance_score=relevance,
        )

    def test_returns_same_count(self):
        records = [self._record("text1"), self._record("text2")]
        result = apply_retrospective(records)
        assert len(result) == 2

    def test_relevance_adjusted_upward_on_topic_match(self):
        r = self._record("governance framework")
        result = apply_retrospective([r], current_topics=["governance"])
        assert result[0].relevance_score > r.relevance_score

    def test_relevance_clamped_to_unit_range(self):
        r = self._record("governance protocol", relevance=0.99)
        result = apply_retrospective(
            [r], current_topics=["governance"], active_commitments=["protocol"]
        )
        assert result[0].relevance_score <= 1.0

    def test_original_records_not_mutated(self):
        r = self._record("text", relevance=0.5)
        apply_retrospective([r])
        assert r.relevance_score == pytest.approx(0.5)

    def test_empty_list_returns_empty(self):
        assert apply_retrospective([]) == []

    def test_none_topics_treated_as_empty(self):
        r = self._record("text", access=1)
        result = apply_retrospective([r], current_topics=None, active_commitments=None)
        assert len(result) == 1
