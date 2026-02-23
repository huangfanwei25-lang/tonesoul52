from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SqliteSoulDB


def _iso_z(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _build_jsonl_db(tmp_path) -> JsonlSoulDB:
    source = MemorySource.SELF_JOURNAL
    return JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})


def _build_sqlite_db(tmp_path) -> SqliteSoulDB:
    return SqliteSoulDB(db_path=tmp_path / "soul.db")


@pytest.mark.parametrize(
    "db_factory",
    [
        _build_jsonl_db,
        _build_sqlite_db,
    ],
)
def test_search_returns_ranked_compact_results(db_factory: Callable, tmp_path) -> None:
    source = MemorySource.SELF_JOURNAL
    db = db_factory(tmp_path)
    now = datetime(2026, 2, 23, tzinfo=timezone.utc)

    first_id = db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(minutes=2)),
            "title": "Governance checkpoint",
            "statement": "quality band review for council gate",
        },
    )
    db.append(
        source,
        {
            "timestamp": _iso_z(now - timedelta(minutes=1)),
            "title": "Infra note",
            "statement": "server deploy checklist",
        },
    )
    third_id = db.append(
        source,
        {
            "timestamp": _iso_z(now),
            "title": "Governance triage",
            "statement": "governance divergence and governance risk",
        },
    )

    results = db.search("governance", limit=2)

    assert len(results) == 2
    assert set(results[0].keys()) == {"id", "title", "score"}
    returned_ids = [item["id"] for item in results]
    assert first_id in returned_ids
    assert third_id in returned_ids
    assert float(results[0]["score"]) >= float(results[1]["score"])


@pytest.mark.parametrize(
    "db_factory",
    [
        _build_jsonl_db,
        _build_sqlite_db,
    ],
)
def test_timeline_returns_window_around_target(db_factory: Callable, tmp_path) -> None:
    source = MemorySource.SELF_JOURNAL
    db = db_factory(tmp_path)
    now = datetime(2026, 2, 23, tzinfo=timezone.utc)

    ids = []
    for idx in range(5):
        ids.append(
            db.append(
                source,
                {
                    "timestamp": _iso_z(now + timedelta(minutes=idx)),
                    "title": f"Entry {idx}",
                    "statement": f"memory-{idx}",
                },
            )
        )

    timeline = db.timeline(ids[2], window=1)

    assert [item["id"] for item in timeline] == ids[1:4]
    assert [item["title"] for item in timeline] == ["Entry 1", "Entry 2", "Entry 3"]
    assert timeline[1]["timestamp"] == _iso_z(now + timedelta(minutes=2))


@pytest.mark.parametrize(
    "db_factory",
    [
        _build_jsonl_db,
        _build_sqlite_db,
    ],
)
def test_detail_returns_full_records_in_requested_order(db_factory: Callable, tmp_path) -> None:
    source = MemorySource.SELF_JOURNAL
    db = db_factory(tmp_path)
    now = datetime(2026, 2, 23, tzinfo=timezone.utc)

    first_id = db.append(
        source,
        {
            "timestamp": _iso_z(now),
            "title": "First",
            "statement": "alpha",
            "tags": ["a"],
            "layer": "working",
        },
    )
    second_id = db.append(
        source,
        {
            "timestamp": _iso_z(now + timedelta(minutes=1)),
            "title": "Second",
            "statement": "beta",
            "tags": ["b"],
            "layer": "experiential",
        },
    )

    details = db.detail([second_id, first_id, "missing-id"])

    assert [item["id"] for item in details] == [second_id, first_id]
    assert details[0]["source"] == source.value
    assert details[0]["payload"]["statement"] == "beta"
    assert details[1]["payload"]["statement"] == "alpha"
