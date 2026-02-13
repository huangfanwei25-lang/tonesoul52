"""Tests for session-end decay cleanup wiring."""

from __future__ import annotations

from datetime import datetime, timezone

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SqliteSoulDB


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _append_old_and_recent_records(db, source: MemorySource) -> None:
    db.append(
        source,
        {
            "timestamp": "2000-01-01T00:00:00Z",
            "statement": "very old and weak memory",
            "relevance_score": 0.2,
            "access_count": 0,
        },
    )
    db.append(
        source,
        {
            "timestamp": _iso_now(),
            "statement": "recent memory",
            "relevance_score": 0.9,
            "access_count": 0,
        },
    )


def test_jsonl_cleanup_decayed_returns_integer_count(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    _append_old_and_recent_records(db, source)

    cleaned = db.cleanup_decayed(source)

    assert isinstance(cleaned, int)
    assert cleaned >= 1


def test_sqlite_cleanup_decayed_returns_integer_count(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    _append_old_and_recent_records(db, source)

    cleaned = db.cleanup_decayed(source)

    assert isinstance(cleaned, int)
    assert cleaned >= 1
