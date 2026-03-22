"""Tests for ETCL seed lifecycle (T0-T6) in the Crystal system."""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.memory.crystallizer import Crystal, MemoryCrystallizer, SeedStage


def test_seed_stage_enum_values() -> None:
    assert SeedStage.T0_DRAFT.value == "T0"
    assert SeedStage.T6_CANONICAL.value == "T6"
    assert len(SeedStage) == 7


def test_seed_stage_from_value() -> None:
    assert SeedStage.from_value("T3") == SeedStage.T3_ALIGN
    assert SeedStage.from_value("invalid") == SeedStage.T0_DRAFT


def test_crystal_default_stage_is_t0() -> None:
    c = Crystal(rule="test", source_pattern="p", weight=0.5, created_at="2026-01-01T00:00:00Z")
    assert c.stage == "T0"
    assert c.stage_history == []


def test_crystal_advance_stage_forward() -> None:
    c = Crystal(rule="test", source_pattern="p", weight=0.5, created_at="2026-01-01T00:00:00Z")
    assert c.advance_stage(SeedStage.T1_DEPOSIT) is True
    assert c.stage == "T1"
    assert len(c.stage_history) == 1
    assert c.stage_history[0]["from"] == "T0"
    assert c.stage_history[0]["to"] == "T1"


def test_crystal_advance_stage_rejects_backward() -> None:
    c = Crystal(
        rule="test",
        source_pattern="p",
        weight=0.5,
        created_at="2026-01-01T00:00:00Z",
        stage="T3",
    )
    assert c.advance_stage(SeedStage.T1_DEPOSIT) is False
    assert c.stage == "T3"
    assert c.stage_history == []


def test_crystal_advance_stage_rejects_same() -> None:
    c = Crystal(
        rule="test",
        source_pattern="p",
        weight=0.5,
        created_at="2026-01-01T00:00:00Z",
        stage="T2",
    )
    assert c.advance_stage(SeedStage.T2_RETRIEVAL) is False
    assert c.stage == "T2"


def test_crystal_full_lifecycle_t0_to_t6() -> None:
    c = Crystal(rule="test", source_pattern="p", weight=0.5, created_at="2026-01-01T00:00:00Z")
    for stage in list(SeedStage)[1:]:  # T1 through T6
        assert c.advance_stage(stage) is True
    assert c.stage == "T6"
    assert len(c.stage_history) == 6


def test_crystal_to_dict_includes_stage() -> None:
    c = Crystal(
        rule="test",
        source_pattern="p",
        weight=0.5,
        created_at="2026-01-01T00:00:00Z",
        stage="T2",
    )
    d = c.to_dict()
    assert d["stage"] == "T2"
    assert "stage_history" in d


def test_crystal_from_dict_with_stage() -> None:
    payload = {
        "rule": "test",
        "source_pattern": "p",
        "weight": 0.5,
        "created_at": "2026-01-01T00:00:00Z",
        "stage": "T4",
        "stage_history": [{"from": "T0", "to": "T1", "at": "2026-01-01T00:00:00Z"}],
    }
    c = Crystal.from_dict(payload)
    assert c is not None
    assert c.stage == "T4"
    assert len(c.stage_history) == 1


def test_crystal_from_dict_backward_compat_no_stage() -> None:
    """Legacy crystals without stage field default to T0."""
    payload = {
        "rule": "old rule",
        "source_pattern": "p",
        "weight": 0.7,
        "created_at": "2025-01-01T00:00:00Z",
    }
    c = Crystal.from_dict(payload)
    assert c is not None
    assert c.stage == "T0"
    assert c.stage_history == []


def test_crystallize_produces_t1_crystals(tmp_path: Path) -> None:
    """Newly crystallized rules should be at T1 (deposited)."""
    cryst = MemoryCrystallizer(crystal_path=tmp_path / "crystals.jsonl")
    result = cryst.crystallize(
        {
            "verdicts": {"block": 5, "approve": 1},
        }
    )
    assert len(result) >= 1
    for crystal in result:
        assert crystal.stage == "T1"
        assert len(crystal.stage_history) == 1
        assert crystal.stage_history[0]["from"] == "T0"
        assert crystal.stage_history[0]["to"] == "T1"


def test_crystallize_persists_stage_to_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "crystals.jsonl"
    cryst = MemoryCrystallizer(crystal_path=path)
    cryst.crystallize({"verdicts": {"block": 5}})

    raw = path.read_text(encoding="utf-8").strip()
    for line in raw.split("\n"):
        data = json.loads(line)
        assert data["stage"] == "T1"
        assert len(data["stage_history"]) == 1


def test_load_crystals_preserves_stage(tmp_path: Path) -> None:
    path = tmp_path / "crystals.jsonl"
    cryst = MemoryCrystallizer(crystal_path=path)
    cryst.crystallize({"verdicts": {"block": 5}})

    loaded = cryst.load_crystals()
    assert len(loaded) >= 1
    for c in loaded:
        assert c.stage == "T1"


def test_record_retrieval_advances_to_t2(tmp_path: Path) -> None:
    path = tmp_path / "crystals.jsonl"
    cryst = MemoryCrystallizer(crystal_path=path)
    cryst.crystallize({"verdicts": {"block": 5}})

    loaded = cryst.load_crystals()
    cryst.record_retrieval(loaded)

    # Check in-memory
    for c in loaded:
        assert c.stage == "T2"
        assert c.access_count >= 1

    # Check persisted
    reloaded = cryst.load_crystals()
    for c in reloaded:
        assert c.stage == "T2"


def test_record_retrieval_idempotent_above_t2(tmp_path: Path) -> None:
    """Crystals already at T3+ should not regress to T2."""
    path = tmp_path / "crystals.jsonl"
    cryst = MemoryCrystallizer(crystal_path=path)
    cryst.crystallize({"verdicts": {"block": 5}})

    loaded = cryst.load_crystals()
    # Manually advance to T3
    for c in loaded:
        c.advance_stage(SeedStage.T2_RETRIEVAL)
        c.advance_stage(SeedStage.T3_ALIGN)
    cryst._write_crystals(loaded)

    loaded2 = cryst.load_crystals()
    cryst.record_retrieval(loaded2)

    for c in loaded2:
        assert c.stage == "T3"  # should NOT go back to T2


def test_dedupe_keeps_higher_stage(tmp_path: Path) -> None:
    """When deduplicating, the more advanced stage should be kept."""
    path = tmp_path / "crystals.jsonl"
    cryst = MemoryCrystallizer(crystal_path=path)

    c1 = Crystal(
        rule="my rule",
        source_pattern="a",
        weight=0.5,
        created_at="2026-01-01T00:00:00Z",
        stage="T1",
    )
    c2 = Crystal(
        rule="my rule",
        source_pattern="b",
        weight=0.6,
        created_at="2026-01-02T00:00:00Z",
        stage="T3",
    )
    merged = cryst._dedupe_crystals([c1, c2])
    assert len(merged) == 1
    assert merged[0].stage == "T3"
