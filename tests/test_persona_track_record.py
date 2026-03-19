from __future__ import annotations

from pathlib import Path

from tonesoul.deliberation.persona_track_record import (
    PersonaTrackRecord,
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
