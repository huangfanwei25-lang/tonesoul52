"""Tests for tonesoul.memory.freshness — zone freshness tracking."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tonesoul.memory.freshness import (
    HALF_LIFE_DAYS,
    build_freshness_report,
    compute_zone_freshness,
    filter_stale_zones,
    touch_zone,
)


def _now():
    return datetime.now(timezone.utc)


def _ts(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ── compute_zone_freshness ────────────────────────────────────────────────────


class TestComputeZoneFreshness:
    def test_just_touched_score_is_one(self):
        now = _now()
        result = compute_zone_freshness("z1", _ts(now), now=now)
        assert abs(result.freshness_score - 1.0) < 0.01

    def test_half_life_score_is_half(self):
        now = _now()
        past = now - timedelta(days=HALF_LIFE_DAYS)
        result = compute_zone_freshness("z1", _ts(past), now=now)
        assert abs(result.freshness_score - 0.5) < 0.02

    def test_double_half_life_score_is_quarter(self):
        now = _now()
        past = now - timedelta(days=HALF_LIFE_DAYS * 2)
        result = compute_zone_freshness("z1", _ts(past), now=now)
        assert abs(result.freshness_score - 0.25) < 0.02

    def test_needs_review_when_below_stale_threshold(self):
        now = _now()
        past = now - timedelta(days=30)
        result = compute_zone_freshness("z1", _ts(past), now=now)
        assert result.needs_review is True

    def test_not_needs_review_when_fresh(self):
        now = _now()
        result = compute_zone_freshness("z1", _ts(now), now=now)
        assert result.needs_review is False

    def test_is_critical_when_below_critical_threshold(self):
        now = _now()
        past = now - timedelta(days=60)
        result = compute_zone_freshness("z1", _ts(past), now=now)
        assert result.is_critical is True

    def test_days_since_touch_accurate(self):
        now = _now()
        past = now - timedelta(days=3)
        result = compute_zone_freshness("z1", _ts(past), now=now)
        assert abs(result.days_since_touch - 3.0) < 0.1

    def test_invalid_timestamp_gives_zero_score(self):
        result = compute_zone_freshness("z1", "not-a-date")
        assert result.freshness_score == 0.0
        assert result.is_critical is True

    def test_empty_timestamp_gives_zero_score(self):
        result = compute_zone_freshness("z1", "")
        assert result.freshness_score == 0.0

    def test_zone_id_preserved(self):
        result = compute_zone_freshness("my-zone", _ts(_now()))
        assert result.zone_id == "my-zone"

    def test_to_dict_has_required_keys(self):
        result = compute_zone_freshness("z1", _ts(_now()))
        d = result.to_dict()
        for key in (
            "zone_id",
            "last_touched_at",
            "freshness_score",
            "needs_review",
            "is_critical",
            "days_since_touch",
        ):
            assert key in d

    def test_score_is_clamped_non_negative(self):
        # Even for extremely old timestamps, score should not go below 0
        result = compute_zone_freshness("z1", "2000-01-01T00:00:00Z")
        assert result.freshness_score >= 0.0


# ── touch_zone ────────────────────────────────────────────────────────────────


class TestTouchZone:
    def test_returns_freshness_one(self):
        result = touch_zone("z1")
        assert result.freshness_score == 1.0

    def test_needs_review_is_false(self):
        result = touch_zone("z1")
        assert result.needs_review is False

    def test_is_critical_is_false(self):
        result = touch_zone("z1")
        assert result.is_critical is False

    def test_days_since_touch_is_zero(self):
        result = touch_zone("z1")
        assert result.days_since_touch == 0.0

    def test_zone_id_preserved(self):
        result = touch_zone("my-special-zone")
        assert result.zone_id == "my-special-zone"

    def test_custom_now_used(self):
        fixed = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = touch_zone("z1", now=fixed)
        assert "2026-01-01" in result.last_touched_at


# ── build_freshness_report ────────────────────────────────────────────────────


class TestBuildFreshnessReport:
    def _mixed_zones(self, now):
        return {
            "fresh": _ts(now),
            "stale": _ts(now - timedelta(days=20)),
            "critical": _ts(now - timedelta(days=90)),
        }

    def test_total_zones_count(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert report.total_zones == 3

    def test_stale_count_correct(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert report.stale_count >= 2  # stale and critical are both stale

    def test_critical_count_correct(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert report.critical_count >= 1

    def test_stale_zone_ids_contains_stale(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert "stale" in report.stale_zone_ids

    def test_critical_zone_ids_contains_critical(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert "critical" in report.critical_zone_ids

    def test_fresh_zone_not_in_stale_list(self):
        now = _now()
        report = build_freshness_report(self._mixed_zones(now), now=now)
        assert "fresh" not in report.stale_zone_ids

    def test_background_tension_delta_zero_when_all_fresh(self):
        now = _now()
        all_fresh = {"z1": _ts(now), "z2": _ts(now)}
        report = build_freshness_report(all_fresh, now=now)
        assert report.background_tension_delta() == 0.0

    def test_background_tension_delta_positive_when_stale(self):
        now = _now()
        all_stale = {"z1": _ts(now - timedelta(days=60))}
        report = build_freshness_report(all_stale, now=now)
        assert report.background_tension_delta() > 0.0

    def test_background_tension_delta_capped_at_one(self):
        now = _now()
        all_ancient = {f"z{i}": "2000-01-01T00:00:00Z" for i in range(20)}
        report = build_freshness_report(all_ancient, now=now)
        assert report.background_tension_delta() <= 1.0

    def test_empty_registry_gives_zero_tension(self):
        report = build_freshness_report({})
        assert report.background_tension_delta() == 0.0
        assert report.total_zones == 0

    def test_to_dict_has_required_keys(self):
        report = build_freshness_report({})
        d = report.to_dict()
        for key in (
            "generated_at",
            "total_zones",
            "stale_count",
            "critical_count",
            "background_tension_delta",
            "stale_zone_ids",
            "critical_zone_ids",
        ):
            assert key in d


# ── filter_stale_zones ────────────────────────────────────────────────────────


class TestFilterStaleZones:
    def test_returns_stale_zone_ids(self):
        now = _now()
        zones = {
            "fresh": _ts(now),
            "old": _ts(now - timedelta(days=30)),
        }
        result = filter_stale_zones(zones, now=now)
        assert "old" in result
        assert "fresh" not in result

    def test_custom_threshold_respected(self):
        now = _now()
        zones = {"medium": _ts(now - timedelta(days=5))}
        # threshold=0.95 → almost everything is stale
        result = filter_stale_zones(zones, threshold=0.95, now=now)
        assert "medium" in result

    def test_empty_registry_returns_empty(self):
        assert filter_stale_zones({}) == []
