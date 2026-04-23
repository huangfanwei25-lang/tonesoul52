from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tonesoul.runtime_adapter_subject_refresh import (
    build_subject_refresh_summary,
    entries_newer_than,
)


_PARSE_DT = datetime.fromisoformat

_EMPTY_ROUTING = {"total_events": 0, "misroute_signal_count": 0, "dominant_surface": ""}
_STABLE_RISK = {"level": "stable"}


def _make_summary(**kwargs):
    defaults = dict(
        subject_snapshots=[],
        checkpoints=[],
        compactions=[],
        claims=[],
        routing_summary=_EMPTY_ROUTING,
        project_memory_summary={},
        risk_posture=_STABLE_RISK,
        parse_dt=_PARSE_DT,
    )
    defaults.update(kwargs)
    return build_subject_refresh_summary(**defaults)


# ─── entries_newer_than ──────────────────────────────────────────────────────

class TestEntriesNewerThan:
    def test_filters_old_entries(self):
        marker = datetime.fromisoformat("2026-04-14T12:00:00+00:00")
        entries = [
            {"updated_at": "2026-04-14T11:00:00+00:00", "id": "old"},
            {"updated_at": "2026-04-14T13:00:00+00:00", "id": "new"},
        ]
        fresh = entries_newer_than(entries, marker_dt=marker, parse_dt=_PARSE_DT)
        assert [e["id"] for e in fresh] == ["new"]

    def test_none_marker_returns_all(self):
        entries = [{"id": "a"}, {"id": "b"}]
        result = entries_newer_than(entries, marker_dt=None, parse_dt=_PARSE_DT)
        assert len(result) == 2

    def test_empty_entries_returns_empty(self):
        marker = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
        assert entries_newer_than([], marker_dt=marker, parse_dt=_PARSE_DT) == []

    def test_invalid_timestamp_excluded(self):
        marker = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
        entries = [{"updated_at": "not-a-date", "id": "bad"}]
        result = entries_newer_than(entries, marker_dt=marker, parse_dt=_PARSE_DT)
        assert result == []

    def test_custom_timestamp_key(self):
        marker = datetime.fromisoformat("2026-04-14T12:00:00+00:00")
        entries = [{"ts": "2026-04-14T13:00:00+00:00", "id": "x"}]
        fresh = entries_newer_than(
            entries, marker_dt=marker, parse_dt=_PARSE_DT, timestamp_key="ts"
        )
        assert len(fresh) == 1

    def test_exactly_at_marker_excluded(self):
        marker = datetime.fromisoformat("2026-04-14T12:00:00+00:00")
        entries = [{"updated_at": "2026-04-14T12:00:00+00:00"}]
        result = entries_newer_than(entries, marker_dt=marker, parse_dt=_PARSE_DT)
        assert result == []


# ─── no_snapshot status ──────────────────────────────────────────────────────

class TestNoSnapshotStatus:
    def test_all_empty_returns_no_snapshot(self):
        summary = _make_summary()
        assert summary["status"] == "no_snapshot"
        assert summary["refresh_recommended"] is False
        assert summary["snapshot_present"] is False

    def test_contains_required_top_level_keys(self):
        summary = _make_summary()
        for key in ("status", "refresh_recommended", "snapshot_present", "latest_snapshot_id",
                    "snapshot_updated_at", "risk_level", "newer_compaction_count",
                    "newer_checkpoint_count", "active_claim_count",
                    "routing_misroute_signal_count", "field_guidance", "promotion_hazards",
                    "recommended_command", "summary_text"):
            assert key in summary

    def test_no_snapshot_no_compactions_adds_hazard(self):
        summary = _make_summary()
        assert any("no subject snapshot" in h.lower() or "traces alone" in h.lower()
                   for h in summary["promotion_hazards"])


# ─── seed_snapshot status ─────────────────────────────────────────────────────

class TestSeedSnapshotStatus:
    def test_recommends_seed_snapshot(self):
        summary = build_subject_refresh_summary(
            subject_snapshots=[],
            checkpoints=[],
            compactions=[
                {
                    "updated_at": "2026-04-14T13:00:00+00:00",
                    "carry_forward": ["keep packet-first cadence stable"],
                    "evidence_refs": ["docs/AI_QUICKSTART.md"],
                }
            ],
            claims=[],
            routing_summary={"total_events": 1, "dominant_surface": "compaction",
                             "misroute_signal_count": 0},
            project_memory_summary={"focus_topics": ["runtime_adapter", "redis"]},
            risk_posture={"level": "stable"},
            parse_dt=_PARSE_DT,
        )
        active = next(i for i in summary["field_guidance"] if i["field"] == "active_threads")
        assert summary["status"] == "seed_snapshot"
        assert summary["refresh_recommended"] is True
        assert active["action"] == "may_refresh_directly"
        assert "apply_subject_refresh.py" in summary["recommended_command"]

    def test_seed_with_checkpoint_only(self):
        summary = _make_summary(checkpoints=[{"updated_at": "2026-04-14T13:00:00+00:00"}])
        assert summary["status"] == "seed_snapshot"
        assert summary["refresh_recommended"] is True


# ─── manual_review status ────────────────────────────────────────────────────

class TestManualReviewStatus:
    def test_misroute_causes_hazard(self):
        summary = build_subject_refresh_summary(
            subject_snapshots=[{
                "snapshot_id": "snap-1",
                "updated_at": "2026-04-14T12:00:00+00:00",
            }],
            checkpoints=[{"updated_at": "2026-04-14T13:00:00+00:00"}],
            compactions=[],
            claims=[{"task_id": "shared-lane"}],
            routing_summary={"misroute_signal_count": 1, "total_events": 2,
                             "dominant_surface": ""},
            project_memory_summary={},
            risk_posture={"level": "elevated"},
            parse_dt=_PARSE_DT,
        )
        assert summary["status"] == "manual_review"
        assert summary["refresh_recommended"] is False
        assert any("routing ambiguity" in h for h in summary["promotion_hazards"])

    def test_claim_count_hazard(self):
        summary = _make_summary(
            subject_snapshots=[{"snapshot_id": "s", "updated_at": "2026-01-01T00:00:00+00:00"}],
            claims=[{"task_id": "t1"}],
        )
        assert any("active claims" in h for h in summary["promotion_hazards"])

    def test_elevated_risk_adds_hazard(self):
        summary = _make_summary(
            subject_snapshots=[{"snapshot_id": "s", "updated_at": "2026-01-01T00:00:00+00:00"}],
            risk_posture={"level": "elevated"},
        )
        assert any("Elevated runtime risk" in h for h in summary["promotion_hazards"])

    def test_checkpoint_without_compaction_hazard(self):
        summary = build_subject_refresh_summary(
            subject_snapshots=[{"snapshot_id": "s", "updated_at": "2026-04-01T00:00:00+00:00"}],
            checkpoints=[{"updated_at": "2026-04-14T12:00:00+00:00"}],
            compactions=[],
            claims=[],
            routing_summary={"misroute_signal_count": 0, "total_events": 0, "dominant_surface": ""},
            project_memory_summary={},
            risk_posture=_STABLE_RISK,
            parse_dt=_PARSE_DT,
        )
        assert any("Checkpoint-only" in h for h in summary["promotion_hazards"])


# ─── stable status ───────────────────────────────────────────────────────────

class TestStableStatus:
    def test_existing_snapshot_no_newer_activity_is_stable(self):
        summary = _make_summary(
            subject_snapshots=[{
                "snapshot_id": "snap-1",
                "updated_at": "2026-04-14T12:00:00+00:00",
            }],
        )
        assert summary["status"] == "stable"
        assert summary["refresh_recommended"] is False


# ─── field_guidance structure ────────────────────────────────────────────────

class TestFieldGuidanceStructure:
    def test_five_fields_always_present(self):
        summary = _make_summary()
        fields = [item["field"] for item in summary["field_guidance"]]
        for f in ("stable_vows", "durable_boundaries", "decision_preferences",
                  "verified_routines", "active_threads"):
            assert f in fields

    def test_stable_vows_always_must_not_auto_promote(self):
        summary = _make_summary()
        sv = next(i for i in summary["field_guidance"] if i["field"] == "stable_vows")
        assert sv["action"] == "must_not_auto_promote"

    def test_durable_boundaries_always_manual_operator_only(self):
        summary = _make_summary()
        db = next(i for i in summary["field_guidance"] if i["field"] == "durable_boundaries")
        assert db["action"] == "manual_operator_only"

    def test_decision_preferences_with_routing_events(self):
        summary = _make_summary(
            routing_summary={"total_events": 5, "dominant_surface": "compaction",
                             "misroute_signal_count": 0}
        )
        dp = next(i for i in summary["field_guidance"] if i["field"] == "decision_preferences")
        assert dp["action"] == "may_influence_only"
        assert any("compaction" in v for v in dp["candidate_values"])


# ─── summary_text ────────────────────────────────────────────────────────────

class TestSummaryText:
    def test_summary_text_starts_with_subject_refresh(self):
        summary = _make_summary()
        assert summary["summary_text"].startswith("subject_refresh=")

    def test_summary_text_contains_evidence_counts(self):
        summary = _make_summary()
        assert "c0/k0" in summary["summary_text"]
