"""Tests for tonesoul.governance.retro — governance entropy discharge valve."""

from __future__ import annotations

from types import SimpleNamespace

from tonesoul.governance.retro import (
    RetroConfig,
    RetroResult,
    run_retro,
    should_run_retro,
)


class TestRetroConfig:
    def test_default_values(self):
        cfg = RetroConfig()
        assert cfg.soul_integral_threshold == 0.55
        assert cfg.sessions_since_last == 10
        assert cfg.max_stale_days == 14
        assert cfg.crystal_freshness_floor == 0.20
        assert cfg.crystal_promote_threshold == 0.80

    def test_from_dict_overrides_all_fields(self):
        cfg = RetroConfig.from_dict(
            {
                "soul_integral_threshold": 0.70,
                "sessions_since_last": 5,
                "max_stale_days": 7,
                "crystal_freshness_floor": 0.10,
                "crystal_promote_threshold": 0.90,
            }
        )
        assert cfg.soul_integral_threshold == 0.70
        assert cfg.sessions_since_last == 5
        assert cfg.max_stale_days == 7
        assert cfg.crystal_freshness_floor == 0.10
        assert cfg.crystal_promote_threshold == 0.90

    def test_from_dict_empty_uses_defaults(self):
        cfg = RetroConfig.from_dict({})
        assert cfg.soul_integral_threshold == 0.55
        assert cfg.sessions_since_last == 10


class TestRetroResult:
    def test_to_dict_contains_all_keys(self):
        r = RetroResult()
        d = r.to_dict()
        for key in (
            "executed_at",
            "stale_rules_pruned",
            "convictions_refreshed",
            "enforcement_events_archived",
            "crystals_decayed",
            "crystals_promoted",
            "drift_snapshot",
            "notes",
        ):
            assert key in d

    def test_to_dict_round_trip_values(self):
        r = RetroResult(
            executed_at="2026-01-01T00:00:00Z",
            stale_rules_pruned=2,
            convictions_refreshed=3,
            enforcement_events_archived=1,
            crystals_decayed=4,
            crystals_promoted=1,
            drift_snapshot={"semantic": 0.12},
            notes=["note_a"],
        )
        d = r.to_dict()
        assert d["stale_rules_pruned"] == 2
        assert d["convictions_refreshed"] == 3
        assert d["drift_snapshot"] == {"semantic": 0.12}
        assert d["notes"] == ["note_a"]

    def test_to_dict_returns_independent_copies(self):
        r = RetroResult(notes=["original"])
        d = r.to_dict()
        d["notes"].append("mutated")
        assert r.notes == ["original"]


class TestShouldRunRetro:
    def test_below_all_thresholds_returns_false(self):
        ok, reason = should_run_retro(soul_integral=0.3, sessions_since_last_retro=3)
        assert ok is False
        assert "no trigger" in reason

    def test_soul_integral_at_threshold_triggers(self):
        ok, reason = should_run_retro(soul_integral=0.55, sessions_since_last_retro=0)
        assert ok is True
        assert "soul_integral" in reason

    def test_soul_integral_above_threshold_triggers(self):
        ok, _ = should_run_retro(soul_integral=0.99)
        assert ok is True

    def test_sessions_at_threshold_triggers(self):
        ok, reason = should_run_retro(soul_integral=0.0, sessions_since_last_retro=10)
        assert ok is True
        assert "sessions" in reason

    def test_sessions_above_threshold_triggers(self):
        ok, _ = should_run_retro(soul_integral=0.0, sessions_since_last_retro=99)
        assert ok is True

    def test_custom_config_raises_threshold(self):
        cfg = RetroConfig(soul_integral_threshold=0.90, sessions_since_last=50)
        ok, _ = should_run_retro(soul_integral=0.55, sessions_since_last_retro=5, config=cfg)
        assert ok is False

    def test_default_args_return_false(self):
        ok, _ = should_run_retro()
        assert ok is False


class TestRunRetro:
    def test_returns_retro_result_instance(self):
        result = run_retro()
        assert isinstance(result, RetroResult)

    def test_executed_at_ends_with_z(self):
        result = run_retro()
        assert result.executed_at.endswith("Z")

    def test_no_crystals_leaves_counts_at_zero(self):
        result = run_retro(crystals=[])
        assert result.crystals_decayed == 0
        assert result.crystals_promoted == 0

    def test_stale_crystal_increments_decayed(self):
        crystal = SimpleNamespace(freshness_score=0.10, access_count=0, tags=[], freshness_status="fresh")
        result = run_retro(crystals=[crystal])
        assert result.crystals_decayed == 1

    def test_fresh_crystal_not_decayed(self):
        crystal = SimpleNamespace(freshness_score=0.50, access_count=0, tags=[])
        result = run_retro(crystals=[crystal])
        assert result.crystals_decayed == 0

    def test_high_freshness_high_access_crystal_promoted(self):
        crystal = SimpleNamespace(freshness_score=0.85, access_count=5, tags=[])
        result = run_retro(crystals=[crystal])
        assert result.crystals_promoted == 1

    def test_high_freshness_low_access_crystal_not_promoted(self):
        # access_count < 3 → not promoted
        crystal = SimpleNamespace(freshness_score=0.85, access_count=2, tags=[])
        result = run_retro(crystals=[crystal])
        assert result.crystals_promoted == 0

    def test_stale_crystal_tagged_in_non_dry_run(self):
        crystal = SimpleNamespace(freshness_score=0.10, access_count=0, tags=[], freshness_status="fresh")
        run_retro(crystals=[crystal], dry_run=False)
        assert crystal.freshness_status == "stale"
        assert "stale" in crystal.tags

    def test_dry_run_does_not_mutate_crystal(self):
        crystal = SimpleNamespace(freshness_score=0.10, access_count=0, tags=[], freshness_status="fresh")
        run_retro(crystals=[crystal], dry_run=True)
        assert crystal.freshness_status == "fresh"

    def test_enforcement_log_archived_count(self):
        log = [
            {"step": "soul_band"},
            {"step": "drift_caution_inject"},
            {"step": "drift_risk_inject"},
            {"step": "other_event"},
        ]
        result = run_retro(enforcement_log=log)
        assert result.enforcement_events_archived == 3

    def test_unrecognized_enforcement_step_not_archived(self):
        log = [{"step": "something_else"}]
        result = run_retro(enforcement_log=log)
        assert result.enforcement_events_archived == 0

    def test_posture_vows_refreshed(self):
        posture = SimpleNamespace(
            vows=[{"id": "v1"}, {"id": "v2"}],
            baseline_drift={},
        )
        result = run_retro(posture=posture)
        assert result.convictions_refreshed == 2

    def test_posture_baseline_drift_captured(self):
        posture = SimpleNamespace(baseline_drift={"semantic": 0.25, "tonal": 0.10})
        result = run_retro(posture=posture)
        assert abs(result.drift_snapshot["semantic"] - 0.25) < 0.001
        assert abs(result.drift_snapshot["tonal"] - 0.10) < 0.001

    def test_non_numeric_drift_fields_excluded(self):
        posture = SimpleNamespace(baseline_drift={"label": "high", "score": 0.5})
        result = run_retro(posture=posture)
        assert "label" not in result.drift_snapshot
        assert "score" in result.drift_snapshot

    def test_notes_list_is_non_empty(self):
        result = run_retro()
        assert len(result.notes) >= 1

    def test_total_actions_appears_in_notes(self):
        log = [{"step": "soul_band"}, {"step": "drift_caution_inject"}]
        crystal = SimpleNamespace(freshness_score=0.10, access_count=0, tags=[], freshness_status="fresh")
        result = run_retro(enforcement_log=log, crystals=[crystal])
        combined_notes = " ".join(result.notes)
        assert "retro complete" in combined_notes
