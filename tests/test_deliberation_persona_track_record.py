"""Tests for tonesoul.deliberation.persona_track_record — pure helpers and PersonaTrackRecord."""
from __future__ import annotations

import json

import pytest

from tonesoul.deliberation.persona_track_record import (
    PersonaTrackRecord,
    _default_stat,
    _utc_iso,
    _verdict_score,
    create_persona_track_record,
    default_track_record_path,
)


# ── _utc_iso ──────────────────────────────────────────────────────────────────

class TestUtcIso:
    def test_returns_string(self):
        assert isinstance(_utc_iso(), str)

    def test_ends_with_z(self):
        assert _utc_iso().endswith("Z")


# ── _default_stat ─────────────────────────────────────────────────────────────

class TestDefaultStat:
    def test_has_total(self):
        s = _default_stat()
        assert s["total"] == 0

    def test_has_all_verdict_keys(self):
        s = _default_stat()
        for key in ("approve", "refine", "declare_stance", "block", "unknown"):
            assert key in s

    def test_success_sum_is_float(self):
        assert isinstance(_default_stat()["success_sum"], float)


# ── _verdict_score ────────────────────────────────────────────────────────────

class TestVerdictScore:
    def test_approve_is_one(self):
        assert _verdict_score("approve") == pytest.approx(1.0)

    def test_refine_is_0_75(self):
        assert _verdict_score("refine") == pytest.approx(0.75)

    def test_declare_stance_is_0_5(self):
        assert _verdict_score("declare_stance") == pytest.approx(0.5)

    def test_block_is_zero(self):
        assert _verdict_score("block") == pytest.approx(0.0)

    def test_block_prefix_is_zero(self):
        assert _verdict_score("block_explicit") == pytest.approx(0.0)

    def test_unknown_defaults_to_0_5(self):
        assert _verdict_score("random") == pytest.approx(0.5)

    def test_case_insensitive(self):
        assert _verdict_score("APPROVE") == pytest.approx(1.0)

    def test_empty_defaults_to_0_5(self):
        assert _verdict_score("") == pytest.approx(0.5)


# ── PersonaTrackRecord.create ─────────────────────────────────────────────────

class TestPersonaTrackRecordCreate:
    def test_creates_with_three_perspectives(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert "muse" in ptr.global_stats
        assert "logos" in ptr.global_stats
        assert "aegis" in ptr.global_stats

    def test_global_stats_have_default_structure(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert ptr.global_stats["muse"]["total"] == 0
        assert ptr.resonance_stats == {}


# ── PersonaTrackRecord.load_or_create ────────────────────────────────────────

class TestPersonaTrackRecordLoadOrCreate:
    def test_creates_when_file_missing(self, tmp_path):
        ptr = PersonaTrackRecord.load_or_create(tmp_path / "ptr.json")
        assert "muse" in ptr.global_stats

    def test_loads_existing_file(self, tmp_path):
        path = tmp_path / "ptr.json"
        data = {
            "global_stats": {"muse": {"total": 5, "success_sum": 4.0, "approve": 5, "refine": 0,
                                       "declare_stance": 0, "block": 0, "unknown": 0}},
            "resonance_stats": {},
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        ptr = PersonaTrackRecord.load_or_create(path)
        assert ptr.global_stats["muse"]["total"] == 5

    def test_falls_back_when_file_corrupt(self, tmp_path):
        path = tmp_path / "ptr.json"
        path.write_text("not valid json", encoding="utf-8")
        ptr = PersonaTrackRecord.load_or_create(path)
        assert "muse" in ptr.global_stats


# ── PersonaTrackRecord.save ───────────────────────────────────────────────────

class TestPersonaTrackRecordSave:
    def test_save_writes_file(self, tmp_path):
        path = tmp_path / "ptr.json"
        ptr = PersonaTrackRecord.create(path)
        ptr.save()
        assert path.exists()

    def test_saved_file_is_valid_json(self, tmp_path):
        path = tmp_path / "ptr.json"
        ptr = PersonaTrackRecord.create(path)
        ptr.save()
        data = json.loads(path.read_text())
        assert "global_stats" in data
        assert "summary" in data

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "deep" / "nested" / "ptr.json"
        ptr = PersonaTrackRecord.create(path)
        ptr.save()
        assert path.exists()


# ── PersonaTrackRecord static helpers ─────────────────────────────────────────

class TestNormalizePerspective:
    def test_valid_perspectives(self):
        for p in ("muse", "logos", "aegis"):
            assert PersonaTrackRecord._normalize_perspective(p) == p

    def test_case_insensitive(self):
        assert PersonaTrackRecord._normalize_perspective("MUSE") == "muse"

    def test_unknown_returns_none(self):
        assert PersonaTrackRecord._normalize_perspective("unknown") is None

    def test_empty_returns_none(self):
        assert PersonaTrackRecord._normalize_perspective("") is None


class TestNormalizeVerdictKey:
    def test_approve(self):
        assert PersonaTrackRecord._normalize_verdict_key("approve") == "approve"

    def test_refine(self):
        assert PersonaTrackRecord._normalize_verdict_key("refine") == "refine"

    def test_declare_stance(self):
        assert PersonaTrackRecord._normalize_verdict_key("declare_stance") == "declare_stance"

    def test_block_prefix(self):
        assert PersonaTrackRecord._normalize_verdict_key("block_hard") == "block"

    def test_unknown_fallback(self):
        assert PersonaTrackRecord._normalize_verdict_key("something_else") == "unknown"

    def test_case_insensitive(self):
        assert PersonaTrackRecord._normalize_verdict_key("REFINE") == "refine"


class TestNormalizeResonance:
    def test_no_loop(self):
        assert PersonaTrackRecord._normalize_resonance("stable", False) == "stable"

    def test_with_loop(self):
        assert PersonaTrackRecord._normalize_resonance("contested", True) == "contested:loop"

    def test_empty_state_defaults_unknown(self):
        assert PersonaTrackRecord._normalize_resonance("", False) == "unknown"


class TestApplyStat:
    def test_increments_total(self):
        stat = _default_stat()
        PersonaTrackRecord._apply_stat(stat, "approve", 1.0)
        assert stat["total"] == 1

    def test_increments_success_sum(self):
        stat = _default_stat()
        PersonaTrackRecord._apply_stat(stat, "approve", 0.75)
        assert stat["success_sum"] == pytest.approx(0.75)

    def test_increments_verdict_count(self):
        stat = _default_stat()
        PersonaTrackRecord._apply_stat(stat, "approve", 1.0)
        assert stat["approve"] == 1


class TestScore:
    def test_zero_total_returns_0_5(self):
        assert PersonaTrackRecord._score(_default_stat()) == pytest.approx(0.5)

    def test_full_approve_returns_1(self):
        stat = {"total": 2, "success_sum": 2.0}
        assert PersonaTrackRecord._score(stat) == pytest.approx(1.0)

    def test_all_block_returns_0(self):
        stat = {"total": 3, "success_sum": 0.0}
        assert PersonaTrackRecord._score(stat) == pytest.approx(0.0)


# ── PersonaTrackRecord.record_outcome ─────────────────────────────────────────

class TestRecordOutcome:
    def test_records_approve(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        ptr.record_outcome("muse", "approve")
        assert ptr.global_stats["muse"]["total"] == 1
        assert ptr.global_stats["muse"]["approve"] == 1

    def test_unknown_perspective_ignored(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        ptr.record_outcome("shadow", "approve")
        # shadow not in global_stats (beyond the 3 defaults)
        # muse/logos/aegis unaffected
        assert ptr.global_stats["muse"]["total"] == 0

    def test_resonance_stats_updated(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        ptr.record_outcome("logos", "refine", resonance_state="contested")
        assert "contested" in ptr.resonance_stats
        assert ptr.resonance_stats["contested"]["logos"]["total"] == 1

    def test_loop_detected_key(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        ptr.record_outcome("aegis", "block", loop_detected=True)
        assert "unknown:loop" in ptr.resonance_stats


# ── PersonaTrackRecord.get_multiplier ─────────────────────────────────────────

class TestGetMultiplier:
    def test_no_history_returns_1(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        m = ptr.get_multiplier("muse")
        assert m == pytest.approx(1.0)

    def test_unknown_perspective_returns_1(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert ptr.get_multiplier("shadow") == pytest.approx(1.0)

    def test_all_approve_multiplier_above_1(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for _ in range(20):
            ptr.record_outcome("muse", "approve")
        m = ptr.get_multiplier("muse")
        assert m > 1.0

    def test_all_block_multiplier_below_1(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for _ in range(20):
            ptr.record_outcome("logos", "block")
        m = ptr.get_multiplier("logos")
        assert m < 1.0

    def test_multiplier_clamped_to_085_115(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for _ in range(100):
            ptr.record_outcome("aegis", "approve")
        m = ptr.get_multiplier("aegis")
        assert 0.85 <= m <= 1.15


# ── PersonaTrackRecord.summary ────────────────────────────────────────────────

class TestSummary:
    def test_all_three_perspectives_present(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        s = ptr.summary()
        for p in ("muse", "logos", "aegis"):
            assert p in s

    def test_zero_total_score_is_0_5(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        s = ptr.summary()
        assert s["muse"]["score"] == pytest.approx(0.5)

    def test_records_reflected_in_summary(self, tmp_path):
        ptr = PersonaTrackRecord.create(tmp_path / "ptr.json")
        ptr.record_outcome("logos", "approve")
        s = ptr.summary()
        assert s["logos"]["total"] == 1
