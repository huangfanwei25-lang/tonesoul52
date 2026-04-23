from __future__ import annotations

import pytest

from tonesoul.memory import stats as stats_mod


def test_extract_helpers_cover_flat_nested_and_invalid_entries():
    assert stats_mod._extract_verdict({"verdict": "APPROVE"}) == "approve"
    assert (
        stats_mod._extract_verdict({"transcript": {"verdict": {"decision": "Concern"}}})
        == "concern"
    )
    assert stats_mod._extract_verdict("bad") is None

    assert stats_mod._extract_divergence({"divergence_analysis": {"concern": ["risk"]}}) == {
        "concern": ["risk"]
    }
    assert stats_mod._extract_divergence(
        {"transcript": {"divergence_analysis": {"object": ["proof"]}}}
    ) == {"object": ["proof"]}
    assert stats_mod._extract_divergence("bad") is None

    assert stats_mod._extract_coherence({"coherence": 0.5}) == 0.5
    assert stats_mod._extract_coherence({"coherence": {"approval_rate": 0.4}}) == 0.4
    assert (
        stats_mod._extract_coherence({"transcript": {"coherence": {"min_confidence": 0.3}}}) == 0.3
    )
    assert stats_mod._extract_coherence("bad") is None


def test_count_by_verdict_and_most_common_divergence():
    entries = [
        {"verdict": "approve", "divergence_analysis": {"concern": ["risk"], "object": ["proof"]}},
        {
            "transcript": {
                "verdict": {"decision": "approve"},
                "divergence_analysis": {"concern": ["risk"]},
            }
        },
        {"verdict": "concern"},
    ]

    assert stats_mod.count_by_verdict(entries) == {"approve": 2, "concern": 1}
    assert stats_mod.most_common_divergence(entries) == "risk"


def test_average_coherence_returns_mean_or_zero():
    entries = [
        {"coherence": {"overall": 0.8}},
        {"transcript": {"coherence": {"min_confidence": 0.4}}},
        {"coherence": None},
    ]

    assert stats_mod.average_coherence(entries) == pytest.approx(0.6)
    assert stats_mod.average_coherence([]) == 0.0


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestExtractVerdict:
    def test_flat_dict_verdict_with_decision_key(self):
        assert stats_mod._extract_verdict({"verdict": {"decision": "Refine"}}) == "refine"

    def test_whitespace_stripped(self):
        assert stats_mod._extract_verdict({"verdict": "  block  "}) == "block"

    def test_non_string_verdict_returns_none(self):
        assert stats_mod._extract_verdict({"verdict": 42}) is None

    def test_empty_dict_returns_none(self):
        assert stats_mod._extract_verdict({}) is None


class TestExtractCoherence:
    def test_c_inter_key_used(self):
        assert stats_mod._extract_coherence({"coherence": {"c_inter": 0.75}}) == pytest.approx(0.75)

    def test_transcript_nested_overall_key(self):
        entry = {"transcript": {"coherence": {"overall": 0.9}}}
        assert stats_mod._extract_coherence(entry) == pytest.approx(0.9)

    def test_integer_coherence_converted_to_float(self):
        assert isinstance(stats_mod._extract_coherence({"coherence": 1}), float)

    def test_none_coherence_value_returns_none(self):
        assert stats_mod._extract_coherence({"coherence": None}) is None


class TestMostCommonDivergence:
    def test_empty_entries_returns_none(self):
        assert stats_mod.most_common_divergence([]) is None

    def test_no_divergence_key_returns_none(self):
        assert stats_mod.most_common_divergence([{"verdict": "approve"}]) is None

    def test_repeated_item_wins(self):
        entries = [
            {"divergence_analysis": {"concern": ["item_a", "item_b"]}},
            {"divergence_analysis": {"concern": ["item_a"]}},
        ]
        assert stats_mod.most_common_divergence(entries) == "item_a"

    def test_non_list_values_skipped(self):
        entries = [{"divergence_analysis": {"concern": "not-a-list"}}]
        assert stats_mod.most_common_divergence(entries) is None


class TestCountByVerdict:
    def test_empty_returns_empty_dict(self):
        assert stats_mod.count_by_verdict([]) == {}

    def test_no_verdict_entries_returns_empty(self):
        assert stats_mod.count_by_verdict([{"text": "hello"}]) == {}

    def test_multiple_verdicts_counted(self):
        entries = [
            {"verdict": "approve"},
            {"verdict": "approve"},
            {"verdict": "block"},
        ]
        result = stats_mod.count_by_verdict(entries)
        assert result == {"approve": 2, "block": 1}


class TestAverageCoherence:
    def test_single_entry(self):
        assert stats_mod.average_coherence([{"coherence": 0.7}]) == pytest.approx(0.7)

    def test_entries_without_coherence_excluded(self):
        entries = [{"coherence": 0.8}, {"verdict": "approve"}, {"coherence": 0.4}]
        assert stats_mod.average_coherence(entries) == pytest.approx(0.6)

    def test_rounded_to_four_decimal_places(self):
        entries = [{"coherence": 1.0 / 3}]
        result = stats_mod.average_coherence(entries)
        assert result == pytest.approx(0.3333, abs=1e-4)
