"""Memory decay engine for dynamic forgetting in ToneSoul."""

from __future__ import annotations

import math

HALF_LIFE_DAYS = 7.0
DECAY_CONSTANT = math.log(2) / HALF_LIFE_DAYS
FORGET_THRESHOLD = 0.1
ACCESS_BOOST = 0.15


def calculate_decay(initial_relevance: float, days_elapsed: float, access_count: int = 0) -> float:
    """Apply exponential decay with optional access-based reinforcement."""
    base = float(initial_relevance)
    elapsed = max(0.0, float(days_elapsed))
    accesses = max(0, int(access_count))
    decayed = base * math.exp(-DECAY_CONSTANT * elapsed)
    boosted = decayed + accesses * ACCESS_BOOST
    return max(0.0, min(1.0, boosted))


def should_forget(relevance_score: float) -> bool:
    """Return True when relevance falls below forgetting threshold."""
    return float(relevance_score) < FORGET_THRESHOLD
