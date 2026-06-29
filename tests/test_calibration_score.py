from __future__ import annotations

import pytest

from tonesoul.calibration_score import (
    brier_score,
    calibration_report,
    expected_calibration_error,
    reliability_buckets,
)


def _pairs(spec: list[tuple[float, int, int]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for conf, hits, total in spec:
        out += [(conf, 1.0)] * hits + [(conf, 0.0)] * (total - hits)
    return out


def test_brier_known_values() -> None:
    assert brier_score([(1.0, 1.0), (0.0, 0.0)]) == 0.0  # perfect
    assert brier_score([(1.0, 0.0), (0.0, 1.0)]) == 1.0  # maximally wrong
    assert brier_score([(0.5, 1.0), (0.5, 0.0)]) == 0.25
    assert brier_score([]) is None


def test_perfectly_calibrated_is_calibrated() -> None:
    report = calibration_report(_pairs([(0.9, 9, 10), (0.6, 6, 10), (0.3, 3, 10)]))
    assert report.verdict == "calibrated"
    assert report.ece is not None and report.ece < 0.02
    assert report.weighted_gap is not None and abs(report.weighted_gap) < 0.02


def test_systematic_overconfidence_is_flagged() -> None:
    # states 0.9 confidence but right only half the time (KalshiBench-shaped)
    report = calibration_report(_pairs([(0.9, 50, 100)]))
    assert report.verdict == "overconfident"
    assert report.weighted_gap is not None and report.weighted_gap > 0.05
    top = [b for b in report.buckets if b.n and b.mean_confidence and b.mean_confidence > 0.8]
    assert top and top[0].gap is not None and top[0].gap > 0  # below the diagonal


def test_underconfidence_is_flagged() -> None:
    report = calibration_report(_pairs([(0.4, 90, 100)]))  # says 0.4 but right 90%
    assert report.verdict == "underconfident"
    assert report.weighted_gap is not None and report.weighted_gap < -0.05


def test_canceling_miscalibration_is_not_called_calibrated() -> None:
    # 0.9 confidence right 50%, AND 0.1 confidence right 50%: the directional biases cancel
    # (weighted_gap ~ 0) but each bin is badly off (high ece). Must NOT read as "calibrated".
    # (Found by a cross-model review; the author's own tests missed this canceling case.)
    report = calibration_report(_pairs([(0.9, 50, 100), (0.1, 50, 100)]))
    assert report.verdict == "miscalibrated"
    assert report.weighted_gap is not None and abs(report.weighted_gap) <= 0.05
    assert report.ece is not None and report.ece > 0.1


def test_rejects_bad_parameters() -> None:
    with pytest.raises(ValueError):
        calibration_report([], min_n=0)  # would otherwise divide by zero
    with pytest.raises(ValueError):
        calibration_report([(0.5, 1.0)], n_bins=0)
    with pytest.raises(ValueError):
        calibration_report([(0.5, 1.0)], tolerance=-0.1)


def test_insufficient_sample_does_not_pretend() -> None:
    report = calibration_report(_pairs([(0.8, 2, 3)]))
    assert report.verdict == "insufficient"
    assert report.brier is None and report.ece is None


def test_rejects_out_of_range_inputs() -> None:
    with pytest.raises(ValueError):
        brier_score([(1.2, 1.0)])
    with pytest.raises(ValueError):
        brier_score([(0.5, 0.5)])  # outcome must be 0.0 or 1.0


def test_ece_zero_when_confidence_matches_hit_rate() -> None:
    ece = expected_calibration_error(_pairs([(0.8, 8, 10)]))  # 0.8 confidence, 80% hit
    assert ece is not None and ece < 1e-9


def test_reliability_buckets_partition_all_claims() -> None:
    buckets = reliability_buckets([(0.05, 1.0), (0.95, 0.0)], n_bins=10)
    assert len(buckets) == 10
    assert sum(b.n for b in buckets) == 2
