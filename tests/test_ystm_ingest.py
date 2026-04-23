"""Tests for tonesoul.ystm.ingest — YSTM segment normalization."""

from __future__ import annotations

import json

import pytest

from tonesoul.ystm.ingest import (
    _prune_none,
    _to_float,
    _to_optional_float,
    _to_optional_str,
    load_segments,
    normalize_segments,
)


class TestToFloat:
    def test_numeric_string_converted(self):
        assert _to_float("3.14") == pytest.approx(3.14)

    def test_int_converted(self):
        assert _to_float(5) == 5.0

    def test_none_returns_default(self):
        assert _to_float(None) == 0.0
        assert _to_float(None, 1.5) == 1.5

    def test_non_numeric_string_returns_default(self):
        assert _to_float("hello") == 0.0
        assert _to_float("hello", 99.0) == 99.0


class TestToOptionalFloat:
    def test_numeric_string_converted(self):
        result = _to_optional_float("2.5")
        assert result == pytest.approx(2.5)

    def test_none_returns_none(self):
        assert _to_optional_float(None) is None

    def test_invalid_returns_none(self):
        assert _to_optional_float("abc") is None

    def test_integer_converted(self):
        assert _to_optional_float(7) == 7.0


class TestToOptionalStr:
    def test_none_returns_none(self):
        assert _to_optional_str(None) is None

    def test_empty_string_returns_none(self):
        assert _to_optional_str("") is None

    def test_whitespace_only_returns_none(self):
        assert _to_optional_str("   ") is None

    def test_valid_string_stripped(self):
        assert _to_optional_str("  hello  ") == "hello"

    def test_non_string_converted(self):
        assert _to_optional_str(42) == "42"


class TestPruneNone:
    def test_dict_with_none_values_pruned(self):
        result = _prune_none({"a": 1, "b": None, "c": "val"})
        assert result == {"a": 1, "c": "val"}

    def test_list_with_none_items_pruned(self):
        result = _prune_none([1, None, 2, None])
        assert result == [1, 2]

    def test_nested_dict_pruned(self):
        result = _prune_none({"outer": {"inner": None, "keep": "x"}})
        assert result == {"outer": {"keep": "x"}}

    def test_non_dict_non_list_returned_as_is(self):
        assert _prune_none(42) == 42
        assert _prune_none("text") == "text"

    def test_already_clean_dict_unchanged(self):
        result = _prune_none({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}


class TestNormalizeSegments:
    def _minimal(self, **kwargs):
        base = {"text": "hello", "mode": "eval", "domain": "governance"}
        base.update(kwargs)
        return base

    def test_valid_segment_normalized(self):
        result = normalize_segments([self._minimal()])
        assert len(result) == 1
        assert result[0]["text"] == "hello"
        assert result[0]["mode"] == "eval"

    def test_non_dict_segment_raises(self):
        with pytest.raises(ValueError, match="JSON object"):
            normalize_segments(["not a dict"])

    def test_missing_required_field_text_raises(self):
        with pytest.raises(ValueError, match="text"):
            normalize_segments([{"mode": "eval", "domain": "gov"}])

    def test_missing_required_field_mode_raises(self):
        with pytest.raises(ValueError, match="mode"):
            normalize_segments([{"text": "x", "domain": "gov"}])

    def test_missing_required_field_domain_raises(self):
        with pytest.raises(ValueError, match="domain"):
            normalize_segments([{"text": "x", "mode": "eval"}])

    def test_turn_id_defaults_to_index_plus_one(self):
        segments = [self._minimal(), self._minimal()]
        result = normalize_segments(segments)
        assert result[0]["turn_id"] == 1
        assert result[1]["turn_id"] == 2

    def test_explicit_turn_id_used(self):
        result = normalize_segments([self._minimal(turn_id=42)])
        assert result[0]["turn_id"] == 42

    def test_default_confidences_are_point_nine(self):
        result = normalize_segments([self._minimal()])
        assert result[0]["mode_confidence"] == pytest.approx(0.9)
        assert result[0]["domain_confidence"] == pytest.approx(0.9)

    def test_explicit_confidence_used(self):
        seg = self._minimal(mode_confidence=0.7, domain_confidence=0.5)
        result = normalize_segments([seg])
        assert result[0]["mode_confidence"] == pytest.approx(0.7)
        assert result[0]["domain_confidence"] == pytest.approx(0.5)

    def test_default_e_srsp_and_e_risk_are_zero(self):
        result = normalize_segments([self._minimal()])
        assert result[0]["E_srsp"] == 0.0
        assert result[0]["E_risk"] == 0.0

    def test_explicit_e_values_used(self):
        seg = self._minimal(E_srsp=0.3, E_risk=0.7)
        result = normalize_segments([seg])
        assert result[0]["E_srsp"] == pytest.approx(0.3)
        assert result[0]["E_risk"] == pytest.approx(0.7)

    def test_flat_source_fields_normalized(self):
        seg = self._minimal(source_type="doc", source_uri="file.md", source_grade="A")
        result = normalize_segments([seg])
        assert "source" in result[0]
        assert result[0]["source"]["type"] == "doc"
        assert result[0]["source"]["uri"] == "file.md"
        assert result[0]["source_grade"] == "A"

    def test_nested_source_dict_normalized(self):
        seg = self._minimal(source={"type": "web", "uri": "http://example.com", "grade": "B"})
        result = normalize_segments([seg])
        assert result[0]["source"]["type"] == "web"
        assert result[0]["source_grade"] == "B"

    def test_no_source_means_no_source_key(self):
        result = normalize_segments([self._minimal()])
        assert "source" not in result[0]

    def test_math_coords_flat_keys(self):
        seg = self._minimal(math_height=0.5, math_geology="sedimentary")
        result = normalize_segments([seg])
        assert "math_coords" in result[0]
        assert result[0]["math_coords"]["height"] == pytest.approx(0.5)
        assert result[0]["math_coords"]["geology"] == "sedimentary"

    def test_math_coords_nested_dict(self):
        seg = self._minimal(math_coords={"height": 0.8, "ruggedness": 0.3})
        result = normalize_segments([seg])
        assert result[0]["math_coords"]["height"] == pytest.approx(0.8)

    def test_no_math_coords_no_key(self):
        result = normalize_segments([self._minimal()])
        assert "math_coords" not in result[0]

    def test_multiple_segments_all_normalized(self):
        segs = [self._minimal(text=f"seg{i}") for i in range(3)]
        result = normalize_segments(segs)
        assert len(result) == 3
        assert [r["text"] for r in result] == ["seg0", "seg1", "seg2"]


class TestLoadSegments:
    def test_list_format_loaded(self, tmp_path):
        data = [{"text": "hello", "mode": "eval", "domain": "gov"}]
        path = tmp_path / "segments.json"
        path.write_text(json.dumps(data))
        result = load_segments(str(path))
        assert len(result) == 1
        assert result[0]["text"] == "hello"

    def test_wrapper_format_loaded(self, tmp_path):
        data = {"segments": [{"text": "hi", "mode": "eval", "domain": "gov"}]}
        path = tmp_path / "segments.json"
        path.write_text(json.dumps(data))
        result = load_segments(str(path))
        assert len(result) == 1

    def test_non_list_format_raises(self, tmp_path):
        path = tmp_path / "segments.json"
        path.write_text(json.dumps({"not": "segments"}))
        with pytest.raises(ValueError, match="list of segments"):
            load_segments(str(path))
