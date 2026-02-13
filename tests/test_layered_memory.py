"""Tests for layered memory support in soul_db."""

from __future__ import annotations

from tonesoul.memory.soul_db import JsonlSoulDB, MemoryLayer, MemoryRecord, MemorySource


def test_memory_record_has_layer():
    record = MemoryRecord(
        source=MemorySource.SELF_JOURNAL,
        timestamp="2026-01-01T00:00:00Z",
        payload={"text": "test"},
        layer=MemoryLayer.FACTUAL.value,
    )
    assert record.layer == MemoryLayer.FACTUAL.value


def test_default_layer_is_experiential():
    record = MemoryRecord(
        source=MemorySource.SELF_JOURNAL,
        timestamp="2026-01-01T00:00:00Z",
        payload={"text": "test"},
    )
    assert record.layer == MemoryLayer.EXPERIENTIAL.value


def test_query_filter_by_layer(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    db.append(source, {"text": "fact1", "layer": MemoryLayer.FACTUAL.value})
    db.append(source, {"text": "exp1", "layer": MemoryLayer.EXPERIENTIAL.value})
    db.append(source, {"text": "work1", "layer": MemoryLayer.WORKING.value})

    factual = list(db.query(source, layer=MemoryLayer.FACTUAL.value))
    experiential = list(db.query(source, layer=MemoryLayer.EXPERIENTIAL.value))
    working = list(db.query(source, layer=MemoryLayer.WORKING.value))
    all_records = list(db.query(source))

    assert len(all_records) == 3
    assert len(factual) == 1
    assert len(experiential) == 1
    assert len(working) == 1


def test_layer_backward_compatible(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    db.append(source, {"text": "old record"})

    records = list(db.query(source, layer=MemoryLayer.EXPERIENTIAL.value))

    assert len(records) >= 1
