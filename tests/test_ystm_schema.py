"""Tests for tonesoul.ystm.schema — YSTM pure-data utilities."""

from __future__ import annotations

from dataclasses import dataclass

from tonesoul.ystm.schema import (
    MathCoords,
    NodeDrift,
    SourceRef,
    WhereField,
    WhereTask,
    WhereTime,
    as_clean_dict,
    prune_none,
    round_floats,
    stable_hash,
    utc_now,
)


class TestUtcNow:
    def test_returns_string(self):
        assert isinstance(utc_now(), str)

    def test_ends_with_z(self):
        assert utc_now().endswith("Z")

    def test_contains_t_separator(self):
        result = utc_now()
        assert "T" in result

    def test_two_calls_both_valid(self):
        t1 = utc_now()
        t2 = utc_now()
        assert t1.endswith("Z")
        assert t2.endswith("Z")


class TestStableHash:
    def test_returns_12_char_string(self):
        h = stable_hash("hello")
        assert len(h) == 12

    def test_output_is_hex(self):
        h = stable_hash("test")
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self):
        assert stable_hash("same") == stable_hash("same")

    def test_different_inputs_produce_different_hashes(self):
        assert stable_hash("abc") != stable_hash("xyz")

    def test_empty_string_produces_hash(self):
        h = stable_hash("")
        assert len(h) == 12


class TestRoundFloats:
    def test_float_rounded_to_digits(self):
        assert round_floats(3.14159265, 3) == 3.142

    def test_non_float_unchanged(self):
        assert round_floats("text", 6) == "text"
        assert round_floats(42, 6) == 42
        assert round_floats(None, 6) is None

    def test_list_of_floats_rounded(self):
        result = round_floats([1.23456789, 9.87654321], 3)
        assert result == [1.235, 9.877]

    def test_nested_dict_rounded(self):
        data = {"a": 1.111111, "b": {"c": 2.999999}}
        result = round_floats(data, 2)
        assert result == {"a": 1.11, "b": {"c": 3.0}}

    def test_mixed_list(self):
        result = round_floats([1.567, "text", None], 2)
        assert result == [1.57, "text", None]

    def test_default_six_digits(self):
        result = round_floats(1.123456789)
        assert result == 1.123457


class TestPruneNone:
    def test_none_value_in_dict_removed(self):
        result = prune_none({"a": 1, "b": None})
        assert result == {"a": 1}

    def test_nested_none_removed(self):
        result = prune_none({"outer": {"inner": None, "keep": "value"}})
        assert result == {"outer": {"keep": "value"}}

    def test_none_element_in_list_kept(self):
        # prune_none doesn't filter list items, only dict values
        result = prune_none([1, None, 3])
        assert result == [1, None, 3]

    def test_empty_dict_after_pruning(self):
        result = prune_none({"a": None, "b": None})
        assert result == {}

    def test_non_dict_non_list_returned_as_is(self):
        assert prune_none(42) == 42
        assert prune_none("text") == "text"
        assert prune_none(None) is None

    def test_list_of_dicts_pruned(self):
        result = prune_none([{"a": 1, "b": None}, {"c": 2}])
        assert result == [{"a": 1}, {"c": 2}]


class TestAsCleanDict:
    def test_dataclass_converted_to_dict(self):
        wt = WhereTime(turn_id=1, event_index=2)
        result = as_clean_dict(wt)
        assert isinstance(result, dict)
        assert result["turn_id"] == 1

    def test_none_fields_pruned(self):
        wt = WhereTime(turn_id=1, event_index=0, timestamp=None, version_id=None)
        result = as_clean_dict(wt)
        assert "timestamp" not in result
        assert "version_id" not in result

    def test_floats_rounded(self):
        wf = WhereField(mode="eval", submode=None, confidence=0.99999999)
        result = as_clean_dict(wf, digits=4)
        assert result["confidence"] == 1.0

    def test_plain_dict_also_works(self):
        d = {"x": 1.123456789, "y": None}
        result = as_clean_dict(d, digits=3)
        assert result == {"x": 1.123}

    def test_where_task_clean_dict(self):
        wt = WhereTask(domain="governance", subdomain=None, confidence=0.75)
        result = as_clean_dict(wt)
        assert result["domain"] == "governance"
        assert "subdomain" not in result
        assert result["confidence"] == 0.75

    def test_source_ref_grade_preserved(self):
        sr = SourceRef(type="doc", uri="file.md", hash=None, grade="A")
        result = as_clean_dict(sr)
        assert result["grade"] == "A"
        assert "hash" not in result
