"""Adaptive round selection for tension-aware deliberation."""

from __future__ import annotations

from typing import Iterable

from .types import Tension

TENSION_LOW = 0.3
TENSION_HIGH = 0.7
MAX_DEBATE_ROUNDS = 3


def _clamp_severity(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def aggregate_tension_severity(tensions: Iterable[Tension]) -> float:
    """Return the mean clamped tension severity for a round."""
    normalized = [_clamp_severity(getattr(tension, "severity", 0.0)) for tension in tensions]
    if not normalized:
        return 0.0
    return sum(normalized) / len(normalized)


def calculate_debate_rounds(tensions: Iterable[Tension]) -> int:
    """Map aggregate tension to the number of debate rounds."""
    aggregate = aggregate_tension_severity(tensions)
    if aggregate < TENSION_LOW:
        return 1
    if aggregate < TENSION_HIGH:
        return 2
    return MAX_DEBATE_ROUNDS
