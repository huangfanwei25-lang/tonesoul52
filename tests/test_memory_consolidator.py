from tonesoul.memory.consolidator import consolidate, generate_meta_reflection, identify_patterns
from tonesoul.memory.stats import average_coherence, count_by_verdict, most_common_divergence


def _sample_entries():
    return [
        {
            "verdict": "block",
            "transcript": {
                "coherence": {"c_inter": 0.2},
                "divergence_analysis": {"concern": ["Safety Council"], "object": []},
            },
        },
        {
            "transcript": {
                "verdict": {"verdict": "declare_stance"},
                "coherence": {"c_inter": 0.5},
                "divergence_analysis": {
                    "concern": ["Safety Council", "Critic Lens"],
                    "object": [],
                },
            },
        },
        {
            "verdict": {"verdict": "declare_stance"},
            "coherence": 0.7,
            "divergence_analysis": {"concern": ["Advocate Voice"], "object": []},
        },
    ]


def test_stats_helpers():
    entries = _sample_entries()
    counts = count_by_verdict(entries)
    assert counts["block"] == 1
    assert counts["declare_stance"] == 2

    common = most_common_divergence(entries)
    assert common == "Safety Council"

    avg = average_coherence(entries)
    assert round(avg, 2) == 0.47


def test_patterns_and_reflection():
    entries = _sample_entries()
    patterns = identify_patterns(entries)
    assert patterns["block"] == 1
    assert patterns["declare_stance"] == 2
    assert patterns["most_common_divergence"] == "Safety Council"

    reflection = generate_meta_reflection(patterns)
    assert "Based on my remembered decisions" in reflection
    assert "blocked 1 request(s)" in reflection
    assert "declared stance 2 time(s)" in reflection
    assert "Safety Council" in reflection


def test_consolidate_returns_meta_reflection():
    entries = _sample_entries()
    result = consolidate(entries)
    assert result.meta_reflection.startswith("Based on my remembered decisions")
