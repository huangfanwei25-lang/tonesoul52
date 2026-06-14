"""CI-safe tests for the stance-survival probe's pure metric.

The model arms (qwen2.5:1.5b + nomic-embed) cannot run in CI; these pin the
deterministic cosine/mean helpers so the metric itself is trustworthy.
"""

from __future__ import annotations

import math

from tools.probe.stance_survival_probe import _cosine, _mean


def test_cosine_identical_is_one() -> None:
    assert _cosine([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 1.0


def test_cosine_orthogonal_is_zero() -> None:
    assert _cosine([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_opposite_is_negative_one() -> None:
    assert _cosine([1.0, 1.0], [-1.0, -1.0]) == round(-1.0, 4)


def test_cosine_handles_empty_and_mismatched() -> None:
    assert _cosine([], [1.0]) == 0.0
    assert _cosine([1.0, 2.0], [1.0]) == 0.0
    assert _cosine([0.0, 0.0], [0.0, 0.0]) == 0.0  # zero vector -> 0, not NaN


def test_cosine_known_value() -> None:
    # angle 45 deg between (1,0) and (1,1): cos = 1/sqrt(2)
    assert _cosine([1.0, 0.0], [1.0, 1.0]) == round(1.0 / math.sqrt(2), 4)


def test_mean() -> None:
    assert _mean([0.8, 0.9, 1.0]) == 0.9
    assert _mean([]) == 0.0
