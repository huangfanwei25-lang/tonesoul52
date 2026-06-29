"""Confidence-calibration scoring — is a stated confidence p right about p of the time?

Domain-agnostic, pure (no I/O, no LLM). This is the genuinely-missing primitive: ToneSoul's
existing council calibration (tonesoul/council/calibration.py) measures vote-distribution
consistency, internal coherence, suppression-recovery, and field-completeness -- none of which is
*confidence* calibration. This answers the KalshiBench question (when a forecaster states 8/10
confidence, is it right ~80% of the time?) for any confidence-stated claim: finance calls, memory
claims, predictions.

It SCORES; it does NOT persist, surface, or bind. Wiring calibration to bind future trust/latitude
is a separate, owner-gated step (cf. the responsibility shadow->enforce discipline and council
outcome_persistence's deliberate "no consumer / validate collection first" posture).
See docs/plans/consequence_structure_calibration_2026-06-30.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Pure confidence-calibration scoring (Brier / ECE / reliability) for stated-confidence claims."
)

USES_LLM = False
USES_NETWORK = False

# A stated-confidence claim resolved against reality: (confidence in [0,1], outcome in {0.0, 1.0}).
ConfidenceOutcome = tuple[float, float]


@dataclass(frozen=True)
class ReliabilityBucket:
    """One confidence bin: stated confidence vs. realized hit-rate."""

    lo: float
    hi: float
    n: int
    mean_confidence: float | None
    hit_rate: float | None
    gap: float | None  # mean_confidence - hit_rate; positive = overconfident in this bin


@dataclass(frozen=True)
class CalibrationReport:
    """Whether stated confidence matched realized accuracy. Scores only; binds nothing."""

    n: int
    brier: float | None
    ece: float | None
    weighted_gap: float | None  # mean(confidence) - mean(accuracy); positive = overconfident
    buckets: tuple[ReliabilityBucket, ...]
    # "calibrated" | "overconfident" | "underconfident" | "miscalibrated" | "insufficient"
    verdict: str
    note: str


def _validate(pairs: Sequence[tuple[float, float]]) -> list[ConfidenceOutcome]:
    cleaned: list[ConfidenceOutcome] = []
    for i, pair in enumerate(pairs):
        conf, outcome = pair
        c = float(conf)
        o = float(outcome)
        if not (0.0 <= c <= 1.0):
            raise ValueError(f"confidence at index {i} must be in [0,1], got {c}")
        if o not in (0.0, 1.0):
            raise ValueError(f"outcome at index {i} must be 0.0 or 1.0, got {o}")
        cleaned.append((c, o))
    return cleaned


def brier_score(pairs: Sequence[tuple[float, float]]) -> float | None:
    """Mean squared error of (confidence - outcome). Lower is better; 0 is perfect; None if empty."""
    cleaned = _validate(pairs)
    if not cleaned:
        return None
    return sum((c - o) ** 2 for c, o in cleaned) / len(cleaned)


def reliability_buckets(
    pairs: Sequence[tuple[float, float]], *, n_bins: int = 10
) -> tuple[ReliabilityBucket, ...]:
    """Partition claims into confidence bins and report stated-confidence vs. realized hit-rate."""
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")
    cleaned = _validate(pairs)
    edges = [i / n_bins for i in range(n_bins + 1)]
    buckets: list[ReliabilityBucket] = []
    for b in range(n_bins):
        lo, hi = edges[b], edges[b + 1]
        # the last bin is closed on the right so confidence == 1.0 has a home
        if b == n_bins - 1:
            members = [(c, o) for c, o in cleaned if lo <= c <= hi]
        else:
            members = [(c, o) for c, o in cleaned if lo <= c < hi]
        n = len(members)
        if n:
            mean_c: float | None = sum(c for c, _ in members) / n
            hit: float | None = sum(o for _, o in members) / n
            gap: float | None = mean_c - hit
        else:
            mean_c = hit = gap = None
        buckets.append(
            ReliabilityBucket(lo=lo, hi=hi, n=n, mean_confidence=mean_c, hit_rate=hit, gap=gap)
        )
    return tuple(buckets)


def expected_calibration_error(
    pairs: Sequence[tuple[float, float]], *, n_bins: int = 10
) -> float | None:
    """ECE: n-weighted mean of |mean_confidence - hit_rate| across confidence bins. None if empty."""
    cleaned = _validate(pairs)
    if not cleaned:
        return None
    total = len(cleaned)
    ece = 0.0
    for bucket in reliability_buckets(cleaned, n_bins=n_bins):
        if bucket.n and bucket.gap is not None:
            ece += (bucket.n / total) * abs(bucket.gap)
    return ece


def calibration_report(
    pairs: Sequence[tuple[float, float]],
    *,
    n_bins: int = 10,
    min_n: int = 10,
    tolerance: float = 0.05,
    ece_tolerance: float = 0.1,
) -> CalibrationReport:
    """Score whether stated confidence matched realized accuracy. Scores only; binds nothing.

    `min_n` keeps it honest on small samples (returns "insufficient" rather than a confident
    verdict on too little data -- the same small-sample caveat KalshiBench flags). `tolerance` is
    the directional-bias band (weighted_gap) within which there is no net over/under-confidence.
    `ece_tolerance` bounds the *magnitude* of per-bin miscalibration: a forecaster can have zero
    net bias yet be badly miscalibrated if over- and under-confidence cancel (high confidence too
    high AND low confidence too low) -- that is "miscalibrated", not "calibrated". `ece_tolerance`
    is looser than `tolerance` because ECE has a known upward bias on small / sparsely-binned data.
    """
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")
    if min_n < 1:
        raise ValueError("min_n must be >= 1")
    if tolerance < 0 or ece_tolerance < 0:
        raise ValueError("tolerance and ece_tolerance must be >= 0")
    cleaned = _validate(pairs)
    n = len(cleaned)
    if n < min_n:
        return CalibrationReport(
            n=n,
            brier=None,
            ece=None,
            weighted_gap=None,
            buckets=(),
            verdict="insufficient",
            note=f"need >= {min_n} resolved claims to judge calibration; have {n}",
        )
    buckets = reliability_buckets(cleaned, n_bins=n_bins)
    # weighted_gap == mean(confidence) - mean(accuracy): the *net* directional bias.
    weighted_gap = sum(b.n * b.gap for b in buckets if b.gap is not None) / n
    ece = expected_calibration_error(cleaned, n_bins=n_bins)
    if weighted_gap > tolerance:
        verdict = "overconfident"
    elif weighted_gap < -tolerance:
        verdict = "underconfident"
    elif ece is not None and ece > ece_tolerance:
        # no net directional bias, but per-bin error is large -- over/under-confidence cancel out
        verdict = "miscalibrated"
    else:
        verdict = "calibrated"
    return CalibrationReport(
        n=n,
        brier=brier_score(cleaned),
        ece=ece,
        weighted_gap=weighted_gap,
        buckets=buckets,
        verdict=verdict,
        note="scores only; does not persist, surface, or bind (binding is owner-gated)",
    )
