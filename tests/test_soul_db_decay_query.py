from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SqliteSoulDB


def _iso_z(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def test_jsonl_query_decay_is_opt_in_and_ranks_results(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    now = datetime(2026, 2, 13, tzinfo=timezone.utc)

    recent_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=1)),
            "statement": "recent",
            "relevance_score": 0.5,
            "access_count": 0,
        },
    )
    boosted_old_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=30)),
            "statement": "old but frequently accessed",
            "relevance_score": 0.2,
            "access_count": 4,
        },
    )
    forgotten_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=45)),
            "statement": "stale",
            "relevance_score": 0.3,
            "access_count": 0,
        },
    )

    baseline_ids = [record.record_id for record in db.query(source)]
    assert baseline_ids == [recent_id, boosted_old_id, forgotten_id]

    decayed = list(db.query(source, apply_decay=True, now=now))
    decayed_ids = [record.record_id for record in decayed]

    assert decayed_ids[:2] == [boosted_old_id, recent_id]
    assert forgotten_id not in decayed_ids


def test_sqlite_query_decay_supports_threshold_and_limit(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    now = datetime(2026, 2, 13, tzinfo=timezone.utc)

    recent_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=5)),
            "statement": "recent moderate",
            "relevance_score": 0.6,
            "access_count": 0,
        },
    )
    boosted_old_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=21)),
            "statement": "old but reinforced",
            "relevance_score": 0.25,
            "access_count": 5,
        },
    )
    db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(days=60)),
            "statement": "very stale",
            "relevance_score": 0.3,
            "access_count": 0,
        },
    )

    top_record = list(db.query(source, limit=1, apply_decay=True, now=now))
    assert len(top_record) == 1
    assert top_record[0].record_id == boosted_old_id
    assert top_record[0].relevance_score > 0.7

    strict = list(db.query(source, apply_decay=True, now=now, forget_threshold=0.7))
    strict_ids = [record.record_id for record in strict]
    assert strict_ids == [boosted_old_id]
    assert recent_id not in strict_ids
