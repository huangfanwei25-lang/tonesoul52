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
