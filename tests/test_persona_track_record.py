from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.deliberation.persona_track_record import (
    PersonaTrackRecord,
    _verdict_score,
    create_persona_track_record,
)


def test_default_multiplier_is_neutral(tmp_path: Path) -> None:
    record = PersonaTrackRecord.create(tmp_path / "ptr.json")
    m = record.get_multiplier("muse", resonance_state="resonance", loop_detected=False)
    assert 0.99 <= m <= 1.01


def test_approve_history_increases_multiplier(tmp_path: Path) -> None:
    record = PersonaTrackRecord.create(tmp_path / "ptr.json")
    for _ in range(12):
        record.record_outcome("muse", "approve", resonance_state="resonance", loop_detected=False)
    m = record.get_multiplier("muse", resonance_state="resonance", loop_detected=False)
    assert m > 1.0


def test_block_history_decreases_multiplier(tmp_path: Path) -> None:
    record = PersonaTrackRecord.create(tmp_path / "ptr.json")
    for _ in range(12):
        record.record_outcome("logos", "block", resonance_state="conflict", loop_detected=False)
    m = record.get_multiplier("logos", resonance_state="conflict", loop_detected=False)
    assert m < 1.0


def test_load_or_create_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "ptr.json"
    record = create_persona_track_record(path)
    record.record_outcome("aegis", "refine", resonance_state="tension", loop_detected=True)

    loaded = create_persona_track_record(path)
    summary = loaded.summary()
    assert summary["aegis"]["total"] == 1


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestVerdictScore:
    def test_approve_returns_one(self):
        assert _verdict_score("approve") == pytest.approx(1.0)

    def test_refine_returns_point_seventy_five(self):
        assert _verdict_score("refine") == pytest.approx(0.75)

    def test_declare_stance_returns_half(self):
        assert _verdict_score("declare_stance") == pytest.approx(0.5)

    def test_block_returns_zero(self):
        assert _verdict_score("block") == pytest.approx(0.0)
        assert _verdict_score("block_hard") == pytest.approx(0.0)

    def test_unknown_verdict_returns_half(self):
        assert _verdict_score("something_unknown") == pytest.approx(0.5)

    def test_none_treated_as_unknown(self):
        assert _verdict_score(None) == pytest.approx(0.5)


class TestNormalizePerspective:
    def test_valid_perspective_names(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for p in ("muse", "logos", "aegis"):
            assert record._normalize_perspective(p) == p

    def test_uppercase_normalized(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_perspective("MUSE") == "muse"

    def test_unknown_perspective_returns_none(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_perspective("oracle") is None

    def test_unknown_perspective_record_outcome_is_noop(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        record.record_outcome("oracle", "approve")
        assert record.summary()["muse"]["total"] == 0


class TestNormalizeVerdict:
    def test_block_prefix_maps_to_block(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_verdict_key("block_hard") == "block"

    def test_unknown_maps_to_unknown(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_verdict_key("withdraw") == "unknown"


class TestNormalizeResonance:
    def test_loop_detected_appends_suffix(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_resonance("tension", True) == "tension:loop"

    def test_no_loop_returns_state(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_resonance("conflict", False) == "conflict"

    def test_empty_state_defaults_to_unknown(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        assert record._normalize_resonance("", False) == "unknown"


class TestMultiplierClamping:
    def test_multiplier_clamped_above_0_85(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for _ in range(50):
            record.record_outcome("logos", "block", resonance_state="conflict", loop_detected=False)
        m = record.get_multiplier("logos", resonance_state="conflict", loop_detected=False)
        assert m >= 0.85

    def test_multiplier_clamped_below_1_15(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        for _ in range(50):
            record.record_outcome(
                "muse", "approve", resonance_state="resonance", loop_detected=False
            )
        m = record.get_multiplier("muse", resonance_state="resonance", loop_detected=False)
        assert m <= 1.15


class TestSummaryStructure:
    def test_summary_has_all_three_personas(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        summary = record.summary()
        assert set(summary.keys()) == {"muse", "logos", "aegis"}

    def test_summary_default_total_is_zero(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        summary = record.summary()
        for p in ("muse", "logos", "aegis"):
            assert summary[p]["total"] == 0

    def test_summary_default_score_is_half(self, tmp_path):
        record = PersonaTrackRecord.create(tmp_path / "ptr.json")
        summary = record.summary()
        assert summary["muse"]["score"] == pytest.approx(0.5)


class TestSaveAndLoad:
    def test_save_creates_json_file(self, tmp_path):
        path = tmp_path / "sub" / "ptr.json"
        record = PersonaTrackRecord.create(path)
        record.save()
        assert path.exists()

    def test_load_or_create_returns_create_when_missing(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        record = PersonaTrackRecord.load_or_create(path)
        assert record.summary()["muse"]["total"] == 0

    def test_corrupted_file_falls_back_to_create(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json!", encoding="utf-8")
        record = PersonaTrackRecord.load_or_create(path)
        assert record.summary()["muse"]["total"] == 0
