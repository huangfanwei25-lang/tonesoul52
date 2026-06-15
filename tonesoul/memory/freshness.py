# DORMANT (as of 2026-06-15): Module is completely unwired from production runtime. No production code imports freshness.py or calls any of its exported functions (ZoneFreshness, FreshnessReport, compute_zone_freshness, touch_zone, build_freshness_report, filter_stale_zones). Only mention is in hybrid_search.py docstring (aspirational, not implemented). hybrid_search.py itself is not imported by any production code; see docs/architecture/architecture_legibility_2026-06-15.md
"""Zone Freshness Tracker — staleness detection for the world model.

Every zone in the ToneSoul world model was last updated at some point.
As time passes without anyone touching a zone, its conceptual map may
no longer reflect reality. This module computes how fresh each zone is
and identifies which zones are ready to become dream candidates.

Freshness model:
  score = exp(-λ · days_since_touch)
  λ = log(2) / HALF_LIFE_DAYS           (same λ as memory/decay.py)

  score = 1.0   immediately after touch
  score = 0.5   after HALF_LIFE_DAYS days
  score = 0.0   asymptotically (treated as stale below STALE_THRESHOLD)

Relationship to world_sense / dream candidates:
  Zones with freshness < STALE_THRESHOLD can be fed into
  WorldSenseSnapshot as low-confidence "known stale" signals — they
  don't trigger Seabed Lockdown, but they do raise the background
  tension that eventually surfaces as a DreamCandidate.

  The zone registry (ts:zones / zone_registry.json) does not need to
  be modified — freshness is computed lazily from last_touched_at.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__ts_layer__ = "memory"
__ts_purpose__ = (
    "Zone freshness: compute staleness scores and surface stale zones "
    "as candidates for world-model review."
)

HALF_LIFE_DAYS: float = 7.0
_LAMBDA: float = math.log(2) / HALF_LIFE_DAYS

STALE_THRESHOLD: float = 0.3  # below this → zone needs review
CRITICAL_THRESHOLD: float = 0.1  # below this → zone is unreliable, raises tension


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class ZoneFreshness:
    """Freshness record for a single zone."""

    zone_id: str
    last_touched_at: str  # ISO-8601, UTC
    freshness_score: float  # 0.0 (stale) → 1.0 (fresh)
    needs_review: bool = False
    is_critical: bool = False
    days_since_touch: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "last_touched_at": self.last_touched_at,
            "freshness_score": round(self.freshness_score, 4),
            "needs_review": self.needs_review,
            "is_critical": self.is_critical,
            "days_since_touch": round(self.days_since_touch, 2),
        }


@dataclass
class FreshnessReport:
    """Aggregated freshness snapshot across all tracked zones."""

    generated_at: str = field(default_factory=lambda: _utcnow())
    total_zones: int = 0
    stale_count: int = 0  # below STALE_THRESHOLD
    critical_count: int = 0  # below CRITICAL_THRESHOLD
    zone_records: List[ZoneFreshness] = field(default_factory=list)

    @property
    def stale_zone_ids(self) -> List[str]:
        return [r.zone_id for r in self.zone_records if r.needs_review]

    @property
    def critical_zone_ids(self) -> List[str]:
        return [r.zone_id for r in self.zone_records if r.is_critical]

    def background_tension_delta(self) -> float:
        """Estimate how much stale zones add to the system's background tension.

        Each stale zone contributes proportionally to how far below STALE_THRESHOLD
        it has fallen. Critical zones contribute double.
        """
        if self.total_zones == 0:
            return 0.0
        delta = 0.0
        for r in self.zone_records:
            if r.is_critical:
                delta += 2 * (STALE_THRESHOLD - r.freshness_score)
            elif r.needs_review:
                delta += STALE_THRESHOLD - r.freshness_score
        return min(1.0, round(delta / max(1, self.total_zones), 4))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "total_zones": self.total_zones,
            "stale_count": self.stale_count,
            "critical_count": self.critical_count,
            "background_tension_delta": self.background_tension_delta(),
            "stale_zone_ids": self.stale_zone_ids,
            "critical_zone_ids": self.critical_zone_ids,
            "zone_records": [r.to_dict() for r in self.zone_records],
        }


# ── Core calculations ─────────────────────────────────────────────────────────


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(ts[:19], fmt[: len(fmt)])
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def compute_zone_freshness(
    zone_id: str,
    last_touched_at: str,
    *,
    now: Optional[datetime] = None,
) -> ZoneFreshness:
    """Compute freshness score for a single zone.

    If ``last_touched_at`` cannot be parsed, score defaults to 0.0 (stale).
    """
    reference = now or datetime.now(timezone.utc)
    parsed = _parse_iso(last_touched_at)

    if parsed is None:
        return ZoneFreshness(
            zone_id=zone_id,
            last_touched_at=last_touched_at,
            freshness_score=0.0,
            needs_review=True,
            is_critical=True,
            days_since_touch=float("inf"),
        )

    delta = reference - parsed
    days = max(0.0, delta.total_seconds() / 86400.0)
    score = math.exp(-_LAMBDA * days)

    return ZoneFreshness(
        zone_id=zone_id,
        last_touched_at=last_touched_at,
        freshness_score=round(score, 4),
        needs_review=score < STALE_THRESHOLD,
        is_critical=score < CRITICAL_THRESHOLD,
        days_since_touch=round(days, 2),
    )


def touch_zone(
    zone_id: str,
    *,
    now: Optional[datetime] = None,
) -> ZoneFreshness:
    """Return a fresh ZoneFreshness as if the zone was just touched."""
    ts = _utcnow() if now is None else now.isoformat().replace("+00:00", "Z")
    return ZoneFreshness(
        zone_id=zone_id,
        last_touched_at=ts,
        freshness_score=1.0,
        needs_review=False,
        is_critical=False,
        days_since_touch=0.0,
    )


def build_freshness_report(
    zone_timestamps: Dict[str, str],
    *,
    now: Optional[datetime] = None,
) -> FreshnessReport:
    """Build a freshness report from a mapping of zone_id → last_touched_at.

    ``zone_timestamps`` can come from the zone registry or from Redis ts:zones.
    """
    records = [
        compute_zone_freshness(zone_id, ts, now=now) for zone_id, ts in zone_timestamps.items()
    ]
    stale = [r for r in records if r.needs_review]
    critical = [r for r in records if r.is_critical]

    return FreshnessReport(
        generated_at=_utcnow() if now is None else now.isoformat().replace("+00:00", "Z"),
        total_zones=len(records),
        stale_count=len(stale),
        critical_count=len(critical),
        zone_records=records,
    )


def filter_stale_zones(
    zone_timestamps: Dict[str, str],
    *,
    threshold: float = STALE_THRESHOLD,
    now: Optional[datetime] = None,
) -> List[str]:
    """Return zone_ids whose freshness score falls below ``threshold``."""
    result: List[str] = []
    for zone_id, ts in zone_timestamps.items():
        r = compute_zone_freshness(zone_id, ts, now=now)
        if r.freshness_score < threshold:
            result.append(zone_id)
    return result
