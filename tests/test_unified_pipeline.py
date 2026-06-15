"""Tests for tonesoul.unified_pipeline — pure env-reading helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from tonesoul.unified_pipeline import (
    UnifiedPipeline,
    _read_bool_env,
    _read_positive_int_env,
)

# ── _read_bool_env ────────────────────────────────────────────────────────────


class TestReadBoolEnv:
    def test_unset_uses_default_false(self, monkeypatch):
        monkeypatch.delenv("TEST_BOOL_VAR", raising=False)
        assert _read_bool_env("TEST_BOOL_VAR") is False

    def test_unset_uses_default_true(self, monkeypatch):
        monkeypatch.delenv("TEST_BOOL_VAR", raising=False)
        assert _read_bool_env("TEST_BOOL_VAR", default=True) is True

    def test_true_values(self, monkeypatch):
        for val in ["1", "true", "yes", "on"]:
            monkeypatch.setenv("TEST_BOOL_VAR", val)
            assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_false_values(self, monkeypatch):
        for val in ["0", "false", "no", "off"]:
            monkeypatch.setenv("TEST_BOOL_VAR", val)
            assert _read_bool_env("TEST_BOOL_VAR") is False

    def test_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "TRUE")
        assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "  1  ")
        assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_unrecognized_returns_false(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "maybe")
        assert _read_bool_env("TEST_BOOL_VAR") is False


# ── _read_positive_int_env ────────────────────────────────────────────────────


class TestReadPositiveIntEnv:
    def test_unset_uses_default(self, monkeypatch):
        monkeypatch.delenv("TEST_INT_VAR", raising=False)
        assert _read_positive_int_env("TEST_INT_VAR", default=5) == 5

    def test_valid_int(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "10")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 10

    def test_invalid_uses_default(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "bad")
        assert _read_positive_int_env("TEST_INT_VAR", default=3) == 3

    def test_zero_clamps_to_one(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "0")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 1

    def test_negative_clamps_to_one(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "-5")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 1

    def test_default_zero_clamps_to_one(self, monkeypatch):
        monkeypatch.delenv("TEST_INT_VAR", raising=False)
        assert _read_positive_int_env("TEST_INT_VAR", default=0) == 1


# ── _normalize_runtime_zone ───────────────────────────────────────────────────


class TestNormalizeRuntimeZone:
    def test_known_zones_returned_lowercased(self):
        for zone in ("safe", "transit", "risk", "danger"):
            assert UnifiedPipeline._normalize_runtime_zone(zone) == zone

    def test_uppercase_lowercased(self):
        assert UnifiedPipeline._normalize_runtime_zone("SAFE") == "safe"

    def test_unknown_defaults_to_safe(self):
        assert UnifiedPipeline._normalize_runtime_zone("unknown_zone") == "safe"

    def test_none_defaults_to_safe(self):
        assert UnifiedPipeline._normalize_runtime_zone(None) == "safe"

    def test_whitespace_stripped(self):
        assert UnifiedPipeline._normalize_runtime_zone("  risk  ") == "risk"


# ── _normalize_governance_depth_plan ─────────────────────────────────────────


class TestNormalizeGovernanceDepthPlan:
    def test_none_returns_empty(self):
        assert UnifiedPipeline._normalize_governance_depth_plan(None) == {}

    def test_dict_returned_as_copy(self):
        plan = {"depth": 3}
        result = UnifiedPipeline._normalize_governance_depth_plan(plan)
        assert result == {"depth": 3}
        result["extra"] = True
        assert "extra" not in plan

    def test_object_with_to_dict_serialized(self):
        obj = SimpleNamespace(to_dict=lambda: {"level": "full"})
        assert UnifiedPipeline._normalize_governance_depth_plan(obj) == {"level": "full"}

    def test_non_dict_returns_empty(self):
        assert UnifiedPipeline._normalize_governance_depth_plan("bad") == {}


# ── _safe_unit_value ──────────────────────────────────────────────────────────


class TestSafeUnitValue:
    def test_valid_in_range(self):
        assert UnifiedPipeline._safe_unit_value(0.5) == pytest.approx(0.5)

    def test_zero_and_one_valid(self):
        assert UnifiedPipeline._safe_unit_value(0.0) == pytest.approx(0.0)
        assert UnifiedPipeline._safe_unit_value(1.0) == pytest.approx(1.0)

    def test_above_one_returns_none(self):
        assert UnifiedPipeline._safe_unit_value(1.5) is None

    def test_below_zero_returns_none(self):
        assert UnifiedPipeline._safe_unit_value(-0.1) is None

    def test_non_numeric_returns_none(self):
        assert UnifiedPipeline._safe_unit_value("0.5") is None


# ── _safe_bool ────────────────────────────────────────────────────────────────


class TestSafeBool:
    def test_bool_passthrough(self):
        assert UnifiedPipeline._safe_bool(True) is True
        assert UnifiedPipeline._safe_bool(False) is False

    def test_truthy_strings(self):
        for val in ("1", "true", "yes", "on"):
            assert UnifiedPipeline._safe_bool(val) is True

    def test_falsy_strings(self):
        for val in ("0", "false", "no", "off"):
            assert UnifiedPipeline._safe_bool(val) is False

    def test_unrecognized_returns_none(self):
        assert UnifiedPipeline._safe_bool("maybe") is None
        assert UnifiedPipeline._safe_bool(42) is None


# ── _contains_override_pressure ───────────────────────────────────────────────


class TestContainsOverridePressure:
    def test_clean_message_returns_false(self):
        assert UnifiedPipeline._contains_override_pressure("please help me") is False

    def test_override_keyword_detected(self):
        assert UnifiedPipeline._contains_override_pressure("override the policy") is True

    def test_bypass_keyword_detected(self):
        assert UnifiedPipeline._contains_override_pressure("bypass safety checks") is True

    def test_non_string_returns_false(self):
        assert UnifiedPipeline._contains_override_pressure(None) is False
        assert UnifiedPipeline._contains_override_pressure(42) is False

    def test_case_insensitive(self):
        assert UnifiedPipeline._contains_override_pressure("OVERRIDE everything") is True


# ── _coerce_friction_score ────────────────────────────────────────────────────


class TestCoerceFrictionScore:
    def test_float_clamped(self):
        assert UnifiedPipeline._coerce_friction_score(0.7) == pytest.approx(0.7)
        assert UnifiedPipeline._coerce_friction_score(1.5) == pytest.approx(1.0)
        assert UnifiedPipeline._coerce_friction_score(-0.3) == pytest.approx(0.0)

    def test_dict_friction_score_key(self):
        assert UnifiedPipeline._coerce_friction_score({"friction_score": 0.4}) == pytest.approx(0.4)

    def test_object_friction_score_attr(self):
        obj = SimpleNamespace(friction_score=0.6)
        assert UnifiedPipeline._coerce_friction_score(obj) == pytest.approx(0.6)

    def test_non_numeric_returns_none(self):
        assert UnifiedPipeline._coerce_friction_score("bad") is None
        assert UnifiedPipeline._coerce_friction_score(None) is None


# ── _extract_contradiction_description ───────────────────────────────────────


class TestExtractContradictionDescription:
    def test_dict_description(self):
        assert (
            UnifiedPipeline._extract_contradiction_description({"description": "  claim A vs B  "})
            == "claim A vs B"
        )

    def test_object_with_description_attr(self):
        obj = SimpleNamespace(description="conflict found")
        assert UnifiedPipeline._extract_contradiction_description(obj) == "conflict found"

    def test_object_with_to_dict(self):
        obj = SimpleNamespace(description="", to_dict=lambda: {"description": "via to_dict"})
        assert UnifiedPipeline._extract_contradiction_description(obj) == "via to_dict"

    def test_empty_returns_empty_string(self):
        assert UnifiedPipeline._extract_contradiction_description({}) == ""


# ── _normalize_attachment_path ────────────────────────────────────────────────


class TestNormalizeAttachmentPath:
    def test_strips_leading_dot_slash(self):
        assert UnifiedPipeline._normalize_attachment_path("./docs/file.md") == "docs/file.md"

    def test_multiple_dot_slash_stripped(self):
        assert UnifiedPipeline._normalize_attachment_path("././file.txt") == "file.txt"

    def test_backslash_replaced(self):
        assert UnifiedPipeline._normalize_attachment_path("docs\\file.md") == "docs/file.md"

    def test_none_coerced_to_empty(self):
        assert UnifiedPipeline._normalize_attachment_path(None) == ""


# ── _is_textual_attachment ────────────────────────────────────────────────────


class TestIsTextualAttachment:
    def test_markdown_allowed(self):
        assert UnifiedPipeline._is_textual_attachment(Path("notes.md")) is True

    def test_python_allowed(self):
        assert UnifiedPipeline._is_textual_attachment(Path("script.py")) is True

    def test_binary_not_allowed(self):
        assert UnifiedPipeline._is_textual_attachment(Path("image.png")) is False
        assert UnifiedPipeline._is_textual_attachment(Path("data.bin")) is False

    def test_case_insensitive_suffix(self):
        assert UnifiedPipeline._is_textual_attachment(Path("README.MD")) is True


# ── _merge_memory_results ─────────────────────────────────────────────────────


class TestMergeMemoryResults:
    def _item(self, doc_id, content="c"):
        return SimpleNamespace(doc_id=doc_id, content=content, source_file="")

    def test_deduplicates_by_doc_id(self):
        a = self._item("doc1")
        b = self._item("doc1")
        c = self._item("doc2")
        result = UnifiedPipeline._merge_memory_results([a, c], [b])
        ids = [r.doc_id for r in result]
        assert ids.count("doc1") == 1
        assert "doc2" in ids

    def test_none_inputs_handled(self):
        a = self._item("x")
        result = UnifiedPipeline._merge_memory_results([a], None)
        assert len(result) == 1

    def test_empty_lists(self):
        assert UnifiedPipeline._merge_memory_results([], []) == []


# ── _collect_graph_query_terms ────────────────────────────────────────────────


class TestCollectGraphQueryTerms:
    def test_extracts_words_from_message(self):
        terms = UnifiedPipeline._collect_graph_query_terms("what is governance here today")
        assert "governance" in terms

    def test_short_words_filtered(self):
        terms = UnifiedPipeline._collect_graph_query_terms("is it ok")
        assert terms == []

    def test_deduplicates_terms(self):
        terms = UnifiedPipeline._collect_graph_query_terms("governance governance boundary")
        counts = {t.lower(): terms.count(t) for t in terms}
        assert all(v == 1 for v in counts.values())

    def test_tb_result_keywords_included(self):
        tone = SimpleNamespace(trigger_keywords=["semantic", "tension"])
        motive = SimpleNamespace(likely_motive="audit", resonance_chain_hint=[])
        tb = SimpleNamespace(tone=tone, motive=motive)
        terms = UnifiedPipeline._collect_graph_query_terms("hello world", tb_result=tb)
        assert "semantic" in terms
        assert "audit" in terms


# ── _semantic_projection ──────────────────────────────────────────────────────


class TestSemanticProjection:
    def test_returns_six_dims(self):
        result = UnifiedPipeline._semantic_projection("test sentence here")
        assert len(result) == 6
        assert result[0] == 1.0

    def test_empty_string_returns_six_dims(self):
        result = UnifiedPipeline._semantic_projection("")
        assert len(result) == 6

    def test_override_pressure_raises_score(self):
        clean = UnifiedPipeline._semantic_projection("the weather is nice today")
        pressured = UnifiedPipeline._semantic_projection("must override bypass force immediately")
        assert pressured[4] > clean[4]


# ── optional-subsystem getter observability ───────────────────────────────────


class TestOptionalSubsystemGetterObservability:
    """A failed optional-subsystem load must return None AND be auditable via
    _exc_trace (not silently swallowed). Guards the fix that wired the lazy-init
    getters to ExceptionTrace, matching the existing _get_tension_engine pattern."""

    def test_get_commit_stack_records_suppressed_load_failure(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise RuntimeError("simulated load failure")

        monkeypatch.setattr("tonesoul.tonebridge.SelfCommitStack", _boom)

        pipe = UnifiedPipeline()
        pipe._self_commit_stack = None  # force the lazy-init path

        result = pipe._get_commit_stack()

        # Fail-soft preserved: the getter still returns None, control flow unchanged.
        assert result is None
        # But the failure is now auditable rather than silently swallowed.
        summary = pipe._exc_trace.summary()
        assert summary["suppressed_count"] >= 1
        assert any(e["operation"] == "_get_commit_stack" for e in summary["errors"])
        assert any(e["error_type"] == "RuntimeError" for e in summary["errors"])
