"""Tests for tonesoul.memory.soul_db — pure helper functions."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from tonesoul.memory.soul_db import (
    FORGET_THRESHOLD,
    MemoryLayer,
    MemoryRecord,
    MemorySource,
    _coerce_float,
    _coerce_int,
    _deserialize_json,
    _deserialize_json_value,
    _full_record,
    _infer_source_from_filename,
    _iso_now,
    _normalize_memory_layer,
    _normalize_provenance_value,
    _parse_timestamp,
    _record_identifier,
    _record_text,
    _record_title,
    _resolve_decay_threshold,
    _serialize_json,
)


# ── _iso_now ──────────────────────────────────────────────────────────────────

class TestIsoNow:
    def test_returns_string(self):
        assert isinstance(_iso_now(), str)

    def test_ends_with_z(self):
        assert _iso_now().endswith("Z")

    def test_parseable_as_datetime(self):
        ts = _iso_now()
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt.tzinfo is not None


# ── _serialize_json ───────────────────────────────────────────────────────────

class TestSerializeJson:
    def test_dict_serialized(self):
        result = _serialize_json({"a": 1, "b": 2})
        parsed = json.loads(result)
        assert parsed == {"a": 1, "b": 2}

    def test_sort_keys(self):
        result = _serialize_json({"b": 2, "a": 1})
        assert result.index('"a"') < result.index('"b"')

    def test_no_spaces(self):
        result = _serialize_json({"k": "v"})
        assert " " not in result

    def test_list_serialized(self):
        result = _serialize_json([1, 2, 3])
        assert json.loads(result) == [1, 2, 3]


# ── _deserialize_json ─────────────────────────────────────────────────────────

class TestDeserializeJson:
    def test_valid_dict(self):
        result = _deserialize_json('{"a": 1}')
        assert result == {"a": 1}

    def test_invalid_json_returns_empty(self):
        assert _deserialize_json("not json") == {}

    def test_array_returns_empty(self):
        assert _deserialize_json("[1, 2]") == {}

    def test_null_json_returns_empty(self):
        assert _deserialize_json("null") == {}


# ── _deserialize_json_value ───────────────────────────────────────────────────

class TestDeserializeJsonValue:
    def test_valid_dict(self):
        result = _deserialize_json_value('{"k": "v"}')
        assert result == {"k": "v"}

    def test_non_json_string_returned_as_str(self):
        result = _deserialize_json_value("plain text")
        assert result == "plain text"

    def test_empty_string_returns_none(self):
        assert _deserialize_json_value("") is None

    def test_none_returns_none(self):
        assert _deserialize_json_value(None) is None

    def test_whitespace_returns_none(self):
        assert _deserialize_json_value("   ") is None

    def test_number_json(self):
        result = _deserialize_json_value("42")
        assert result == 42


# ── _normalize_provenance_value ───────────────────────────────────────────────

class TestNormalizeProvenanceValue:
    def test_normal_string(self):
        assert _normalize_provenance_value("hello") == "hello"

    def test_empty_string_returns_none(self):
        assert _normalize_provenance_value("") is None

    def test_whitespace_string_returns_none(self):
        assert _normalize_provenance_value("  ") is None

    def test_non_empty_list(self):
        assert _normalize_provenance_value([1, 2]) == [1, 2]

    def test_empty_list_returns_none(self):
        assert _normalize_provenance_value([]) is None

    def test_non_empty_dict(self):
        assert _normalize_provenance_value({"a": 1}) == {"a": 1}

    def test_empty_dict_returns_none(self):
        assert _normalize_provenance_value({}) is None

    def test_integer_returns_none(self):
        assert _normalize_provenance_value(42) is None

    def test_none_returns_none(self):
        assert _normalize_provenance_value(None) is None


# ── _coerce_float ─────────────────────────────────────────────────────────────

class TestCoerceFloat:
    def test_float_passthrough(self):
        assert _coerce_float(1.5) == pytest.approx(1.5)

    def test_int_to_float(self):
        assert _coerce_float(3) == pytest.approx(3.0)

    def test_string_float(self):
        assert _coerce_float("2.5") == pytest.approx(2.5)

    def test_invalid_returns_default(self):
        assert _coerce_float("abc") == pytest.approx(0.0)

    def test_none_returns_default(self):
        assert _coerce_float(None) == pytest.approx(0.0)

    def test_custom_default(self):
        assert _coerce_float("nope", default=99.0) == pytest.approx(99.0)


# ── _coerce_int ───────────────────────────────────────────────────────────────

class TestCoerceInt:
    def test_int_passthrough(self):
        assert _coerce_int(5) == 5

    def test_float_truncated(self):
        assert _coerce_int(3.9) == 3

    def test_string_int(self):
        assert _coerce_int("7") == 7

    def test_invalid_returns_default(self):
        assert _coerce_int("abc") == 0

    def test_none_returns_default(self):
        assert _coerce_int(None) == 0

    def test_custom_default(self):
        assert _coerce_int("bad", default=42) == 42


# ── _parse_timestamp ──────────────────────────────────────────────────────────

class TestParseTimestamp:
    def test_z_suffix(self):
        dt = _parse_timestamp("2026-01-01T12:00:00Z")
        assert isinstance(dt, datetime)
        assert dt.tzinfo is not None

    def test_naive_gets_utc(self):
        dt = _parse_timestamp("2026-01-01T12:00:00")
        assert dt.tzinfo == timezone.utc

    def test_datetime_object_passthrough(self):
        now = datetime.now(timezone.utc)
        result = _parse_timestamp(now)
        assert result.tzinfo is not None

    def test_none_returns_none(self):
        assert _parse_timestamp(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_timestamp("") is None

    def test_invalid_returns_none(self):
        assert _parse_timestamp("not-a-date") is None

    def test_offset_normalized_to_utc(self):
        dt = _parse_timestamp("2026-06-01T12:00:00+05:00")
        assert dt.tzinfo == timezone.utc


# ── _resolve_decay_threshold ──────────────────────────────────────────────────

class TestResolveDecayThreshold:
    def test_none_uses_default(self):
        assert _resolve_decay_threshold(None) == pytest.approx(FORGET_THRESHOLD)

    def test_valid_value_returned(self):
        assert _resolve_decay_threshold(0.3) == pytest.approx(0.3)

    def test_clamped_above_one(self):
        assert _resolve_decay_threshold(2.0) == pytest.approx(1.0)

    def test_clamped_below_zero(self):
        assert _resolve_decay_threshold(-0.5) == pytest.approx(0.0)

    def test_string_coerced(self):
        assert _resolve_decay_threshold("0.4") == pytest.approx(0.4)


# ── _normalize_memory_layer ───────────────────────────────────────────────────

class TestNormalizeMemoryLayer:
    def test_valid_layer(self):
        assert _normalize_memory_layer("factual") == "factual"

    def test_case_insensitive(self):
        assert _normalize_memory_layer("FACTUAL") == "factual"

    def test_none_returns_none(self):
        assert _normalize_memory_layer(None) is None

    def test_empty_returns_none(self):
        assert _normalize_memory_layer("") is None

    def test_whitespace_returns_none(self):
        assert _normalize_memory_layer("  ") is None

    def test_unknown_passthrough(self):
        result = _normalize_memory_layer("custom_layer")
        assert result == "custom_layer"


# ── _record_title ─────────────────────────────────────────────────────────────

def _make_record(payload=None, source=MemorySource.CUSTOM, timestamp="2026-01-01T00:00:00Z", **kw):
    return MemoryRecord(
        source=source,
        timestamp=timestamp,
        payload=payload or {},
        **kw,
    )


class TestRecordTitle:
    def test_uses_title_key(self):
        r = _make_record({"title": "My Title"})
        assert _record_title(r) == "My Title"

    def test_falls_back_to_summary(self):
        r = _make_record({"summary": "My Summary"})
        assert _record_title(r) == "My Summary"

    def test_falls_back_to_content(self):
        r = _make_record({"content": "content text"})
        assert _record_title(r) == "content text"

    def test_empty_payload_uses_fallback(self):
        r = _make_record({})
        title = _record_title(r)
        assert "custom" in title

    def test_truncates_at_120(self):
        r = _make_record({"title": "X" * 200})
        assert len(_record_title(r)) <= 120

    def test_skips_empty_string_values(self):
        r = _make_record({"title": "", "summary": "valid"})
        assert _record_title(r) == "valid"


# ── _record_identifier ────────────────────────────────────────────────────────

class TestRecordIdentifier:
    def test_uses_record_id_when_set(self):
        r = _make_record(record_id="my-id-123")
        assert _record_identifier(r, 0) == "my-id-123"

    def test_fallback_index_used(self):
        r = _make_record()
        ident = _record_identifier(r, 5)
        assert "5" in ident

    def test_fallback_includes_source(self):
        r = _make_record(source=MemorySource.SELF_JOURNAL)
        ident = _record_identifier(r, 0)
        assert "self_journal" in ident


# ── _full_record ──────────────────────────────────────────────────────────────

class TestFullRecord:
    def test_required_keys_present(self):
        r = _make_record({"title": "t"}, record_id="r1")
        d = _full_record(r, 0)
        for k in ("id", "source", "timestamp", "title", "tags", "layer",
                  "relevance_score", "access_count", "last_accessed", "payload"):
            assert k in d

    def test_id_uses_record_id(self):
        r = _make_record(record_id="test-id")
        d = _full_record(r, 0)
        assert d["id"] == "test-id"

    def test_tags_is_list(self):
        r = _make_record(tags=["a", "b"])
        d = _full_record(r, 0)
        assert isinstance(d["tags"], list)
        assert d["tags"] == ["a", "b"]

    def test_relevance_score_is_float(self):
        r = _make_record(relevance_score=0.8)
        d = _full_record(r, 0)
        assert isinstance(d["relevance_score"], float)


# ── _infer_source_from_filename ───────────────────────────────────────────────

class TestInferSourceFromFilename:
    def test_self_journal(self):
        assert _infer_source_from_filename("self_journal.jsonl") == MemorySource.SELF_JOURNAL

    def test_summary_balls(self):
        assert _infer_source_from_filename("summary_balls.jsonl") == MemorySource.SUMMARY_BALLS

    def test_provenance_ledger(self):
        assert _infer_source_from_filename("provenance_ledger.jsonl") == MemorySource.PROVENANCE_LEDGER

    def test_entropy_monitor(self):
        assert _infer_source_from_filename("entropy_monitor_log.jsonl") == MemorySource.ENTROPY_MONITOR

    def test_scan_log(self):
        assert _infer_source_from_filename("scan_log.jsonl") == MemorySource.SCAN_LOG

    def test_unknown_returns_custom(self):
        assert _infer_source_from_filename("random_file.jsonl") == MemorySource.CUSTOM

    def test_case_insensitive(self):
        assert _infer_source_from_filename("SELF_JOURNAL.JSONL") == MemorySource.SELF_JOURNAL
