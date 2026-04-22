"""Tests for tonesoul.tsr_metrics — Tone-Semantic-Resonance computation."""

from __future__ import annotations

import json
import math

import pytest

from tonesoul.tsr_metrics import (
    _count_hits,
    _safe_scale,
    _tokenize,
    build_tsr_metrics,
    latest_entry,
    load_index,
    resolve_tsr_policy,
    score,
    update_index,
)


class TestSafeScale:
    def test_positive_value_returned_as_is(self):
        assert _safe_scale(5.0) == 5.0

    def test_zero_returns_one(self):
        assert _safe_scale(0.0) == 1.0

    def test_negative_returns_one(self):
        assert _safe_scale(-3.0) == 1.0


class TestTokenize:
    def test_lowercase_words_extracted(self):
        tokens = list(_tokenize("build create advance"))
        assert tokens == ["build", "create", "advance"]

    def test_uppercase_normalized_to_lower(self):
        tokens = list(_tokenize("BUILD CREATE"))
        assert tokens == ["build", "create"]

    def test_punctuation_stripped(self):
        tokens = list(_tokenize("must! ensure? block."))
        assert set(tokens) == {"must", "ensure", "block"}

    def test_empty_string_returns_empty(self):
        assert list(_tokenize("")) == []


class TestCountHits:
    def test_all_matches(self):
        assert _count_hits(["build", "create"], {"build", "create", "advance"}) == 2

    def test_no_matches(self):
        assert _count_hits(["hello", "world"], {"build", "create"}) == 0

    def test_partial_matches(self):
        assert _count_hits(["build", "hello"], {"build", "create"}) == 1

    def test_empty_tokens(self):
        assert _count_hits([], {"build"}) == 0


class TestResolveTsrPolicy:
    def test_empty_policy_returns_defaults(self):
        resolved = resolve_tsr_policy({})
        assert resolved["tension"]["base"] == 0.15
        assert "positive" in resolved["lexicon"]
        assert isinstance(resolved["lexicon"]["positive"], set)

    def test_custom_tension_overrides_default(self):
        resolved = resolve_tsr_policy({"tension": {"base": 0.30}})
        assert resolved["tension"]["base"] == 0.30
        # other tension keys still use defaults
        assert resolved["tension"]["length_weight"] == 0.35

    def test_custom_lexicon_list_replaces_category(self):
        resolved = resolve_tsr_policy({"lexicon": {"positive": ["proceed", "launch"]}})
        assert resolved["lexicon"]["positive"] == {"proceed", "launch"}

    def test_none_policy_uses_defaults(self):
        resolved = resolve_tsr_policy(None)
        assert resolved["tension"]["base"] == 0.15

    def test_invalid_lexicon_type_falls_back_to_default(self):
        resolved = resolve_tsr_policy({"lexicon": {"positive": "not_a_list"}})
        from tonesoul.tsr_metrics import DEFAULT_LEXICON
        assert resolved["lexicon"]["positive"] == set(DEFAULT_LEXICON["positive"])


class TestScore:
    def test_empty_text_returns_base_tension(self):
        result = score("", policy={})
        # tension = base (0.15) with all factors zero
        assert abs(result["tsr"]["T"] - 0.15) < 0.01

    def test_all_positive_words_give_positive_direction(self):
        result = score("build create enable advance", policy={})
        assert result["tsr"]["S"] > 0.0
        assert result["tsr"]["S_norm"] > 0.5

    def test_all_negative_words_give_negative_direction(self):
        result = score("block deny halt stop prevent", policy={})
        assert result["tsr"]["S"] < 0.0
        assert result["tsr"]["S_norm"] < 0.5

    def test_equal_positive_and_negative_gives_zero_direction(self):
        # One positive, one negative → direction = 0
        result = score("build block", policy={})
        assert abs(result["tsr"]["S"]) < 0.01
        assert abs(result["tsr"]["S_norm"] - 0.5) < 0.01

    def test_no_direction_words_gives_neutral_direction(self):
        result = score("hello world foo bar", policy={})
        assert abs(result["tsr"]["S"]) < 0.01
        assert abs(result["tsr"]["S_norm"] - 0.5) < 0.01

    def test_many_strong_modals_increase_tension(self):
        plain = score("hello world", policy={})
        modal = score("must must must must must must ensure shall", policy={})
        assert modal["tsr"]["T"] > plain["tsr"]["T"]

    def test_caution_words_increase_tension(self):
        plain = score("hello world", policy={})
        cautious = score("risk uncertain warning caution may might", policy={})
        assert cautious["tsr"]["T"] > plain["tsr"]["T"]

    def test_tension_capped_at_one(self):
        # Long text with all tension-increasing factors maxed
        big_text = (
            "must ensure shall require " * 10
            + "risk warning caution " * 5
            + "hello " * 200
            + "??? !!!"
        )
        result = score(big_text, policy={})
        assert result["tsr"]["T"] <= 1.0

    def test_energy_radius_matches_formula(self):
        result = score("build must risk", policy={})
        T = result["tsr"]["T"]
        S_norm = result["tsr"]["S_norm"]
        R = result["tsr"]["R"]
        expected = math.sqrt(T**2 + S_norm**2 + R**2)
        assert abs(result["tsr"]["energy_radius"] - round(expected, 4)) < 0.001

    def test_signals_contains_token_count(self):
        result = score("build create enable", policy={})
        assert result["signals"]["token_count"] == 3

    def test_signals_positive_hits_counted(self):
        result = score("build create advance stabilize", policy={})
        assert result["signals"]["positive_hits"] == 4

    def test_question_marks_counted_in_signals(self):
        result = score("is this good? is this right?", policy={})
        assert result["signals"]["question_count"] == 2


class TestBuildTsrMetrics:
    def test_returns_dict_with_required_keys(self):
        payload = build_tsr_metrics("hello world", run_id="r1", policy={})
        for key in ("generated_at", "run_id", "source", "tsr", "signals", "delta"):
            assert key in payload

    def test_run_id_preserved(self):
        payload = build_tsr_metrics("text", run_id="run-xyz", policy={})
        assert payload["run_id"] == "run-xyz"

    def test_no_baseline_gives_delta_unavailable(self):
        payload = build_tsr_metrics("text", policy={})
        assert payload["delta"]["available"] is False

    def test_with_baseline_gives_delta_available(self):
        baseline = {"tsr": {"T": 0.2, "S": 0.1, "S_norm": 0.55, "R": 0.3}}
        payload = build_tsr_metrics("build create enable", baseline_entry=baseline, policy={})
        assert payload["delta"]["available"] is True

    def test_delta_values_are_differences(self):
        baseline = {"tsr": {"T": 0.20, "S": 0.0, "S_norm": 0.5, "R": 0.0}}
        payload = build_tsr_metrics("build create", baseline_entry=baseline, policy={})
        delta = payload["delta"]
        current_T = payload["tsr"]["T"]
        expected_delta_T = round(current_T - 0.20, 4)
        assert abs(delta["T"] - expected_delta_T) < 0.001

    def test_delta_norm_uses_euclidean_distance(self):
        baseline = {"tsr": {"T": 0.0, "S": 0.0, "S_norm": 0.0, "R": 0.0}}
        payload = build_tsr_metrics("build create", baseline_entry=baseline, policy={})
        delta = payload["delta"]
        expected_norm = round(
            math.sqrt(delta["T"] ** 2 + delta["S_norm"] ** 2 + delta["R"] ** 2), 4
        )
        assert abs(delta["delta_norm"] - expected_norm) < 0.001


class TestLoadIndex:
    def test_missing_path_returns_empty_structure(self):
        result = load_index("/nonexistent/path/index.json")
        assert result["entries"] == []
        assert "generated_at" in result

    def test_empty_string_path_returns_empty_structure(self):
        result = load_index("")
        assert result["entries"] == []

    def test_valid_index_file_loaded(self, tmp_path):
        index_file = tmp_path / "index.json"
        data = {"generated_at": "2026-01-01T00:00:00Z", "entries": [{"run_id": "r1"}]}
        index_file.write_text(json.dumps(data))
        result = load_index(str(index_file))
        assert result["entries"][0]["run_id"] == "r1"

    def test_non_dict_json_returns_empty(self, tmp_path):
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps([1, 2, 3]))
        result = load_index(str(index_file))
        assert result["entries"] == []


class TestLatestEntry:
    def test_empty_entries_returns_none(self):
        assert latest_entry({"entries": []}) is None

    def test_no_entries_key_returns_none(self):
        assert latest_entry({}) is None

    def test_single_entry_returned(self):
        entry = {"run_id": "r1"}
        result = latest_entry({"entries": [entry]})
        assert result["run_id"] == "r1"

    def test_last_entry_returned_for_multiple(self):
        entries = [{"run_id": "r1"}, {"run_id": "r2"}, {"run_id": "r3"}]
        result = latest_entry({"entries": entries})
        assert result["run_id"] == "r3"


class TestUpdateIndex:
    def test_new_entry_appended(self, tmp_path):
        index_path = str(tmp_path / "subdir" / "index.json")
        payload = {"tsr": {"T": 0.2}, "generated_at": "2026-01-01Z", "delta": {}}
        update_index(index_path, "run-1", "metrics/r1.json", payload)
        index = load_index(index_path)
        assert len(index["entries"]) == 1
        assert index["entries"][0]["run_id"] == "run-1"

    def test_existing_run_id_replaced(self, tmp_path):
        index_path = str(tmp_path / "index.json")
        payload = {"tsr": {"T": 0.2}, "generated_at": "2026-01-01Z", "delta": {}}
        update_index(index_path, "run-1", "m/r1.json", payload)
        update_index(index_path, "run-1", "m/r1_updated.json", payload)
        index = load_index(index_path)
        assert len(index["entries"]) == 1
        assert index["entries"][0]["metrics_path"] == "m/r1_updated.json"

    def test_max_entries_enforced(self, tmp_path):
        index_path = str(tmp_path / "index.json")
        payload = {"tsr": {"T": 0.2}, "generated_at": "2026-01-01Z", "delta": {}}
        for i in range(5):
            update_index(index_path, f"run-{i}", f"m/r{i}.json", payload, max_entries=3)
        index = load_index(index_path)
        assert len(index["entries"]) == 3
        assert index["entries"][-1]["run_id"] == "run-4"
