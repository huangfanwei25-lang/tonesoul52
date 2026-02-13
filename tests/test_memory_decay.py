from __future__ import annotations

from tonesoul.memory.decay import HALF_LIFE_DAYS, calculate_decay, should_forget


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
