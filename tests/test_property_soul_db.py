from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import given, settings
from hypothesis import strategies as st

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource


def _db_path(tmpdir: str) -> Path:
    return Path(tmpdir) / "self_journal.jsonl"


def _record(text: str, timestamp: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"text": text, "title": text[:40], "relevance_score": 0.8}
    if timestamp is not None:
        payload["timestamp"] = timestamp
    return payload


class TestSoulDbProperties:
    @settings(max_examples=15, deadline=5000)
    @given(items=st.lists(st.text(min_size=1, max_size=40), min_size=1, max_size=8))
    def test_append_then_stream_preserves_cardinality(self, items) -> None:
        with TemporaryDirectory() as tmpdir:
            db = JsonlSoulDB(source_map={MemorySource.CUSTOM: _db_path(tmpdir)})
            for item in items:
                db.append(MemorySource.CUSTOM, _record(item))

            streamed = list(db.stream(MemorySource.CUSTOM))

        assert len(streamed) == len(items)

    @settings(max_examples=12, deadline=5000)
    @given(items=st.lists(st.text(min_size=1, max_size=40), min_size=1, max_size=6))
    def test_detail_round_trip_returns_inserted_ids(self, items) -> None:
        with TemporaryDirectory() as tmpdir:
            db = JsonlSoulDB(source_map={MemorySource.CUSTOM: _db_path(tmpdir)})
            ids = [db.append(MemorySource.CUSTOM, _record(item)) for item in items]
            details = db.detail(ids)

        assert {item["id"] for item in details} == set(ids)

    @settings(max_examples=12, deadline=5000)
    @given(items=st.lists(st.text(min_size=2, max_size=30), min_size=1, max_size=6))
    def test_search_finds_inserted_keyword(self, items) -> None:
        with TemporaryDirectory() as tmpdir:
            db = JsonlSoulDB(source_map={MemorySource.CUSTOM: _db_path(tmpdir)})
            for item in items:
                db.append(MemorySource.CUSTOM, _record(f"governance {item}"))
            results = db.search("governance", limit=5)

        assert len(results) >= 1
        assert all("governance" in item["title"].lower() for item in results)

    @settings(max_examples=12, deadline=5000)
    @given(
        items=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=8),
        limit=st.integers(min_value=1, max_value=5),
    )
    def test_query_limit_never_exceeds_requested_bound(self, items, limit) -> None:
        with TemporaryDirectory() as tmpdir:
            db = JsonlSoulDB(source_map={MemorySource.CUSTOM: _db_path(tmpdir)})
            for item in items:
                db.append(MemorySource.CUSTOM, _record(item))
            results = list(db.query(MemorySource.CUSTOM, limit=limit))

        assert len(results) <= limit

    @settings(max_examples=10, deadline=5000)
    @given(text=st.text(min_size=1, max_size=30))
    def test_decay_gating_filters_old_low_value_records(self, text) -> None:
        with TemporaryDirectory() as tmpdir:
            db = JsonlSoulDB(source_map={MemorySource.CUSTOM: _db_path(tmpdir)})
            old = (
                (datetime.now(timezone.utc) - timedelta(days=90))
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            db.append(MemorySource.CUSTOM, _record(text, timestamp=old))
            results = list(
                db.query(
                    MemorySource.CUSTOM,
                    apply_decay=True,
                    now=datetime.now(timezone.utc),
                )
            )

        assert results == []
