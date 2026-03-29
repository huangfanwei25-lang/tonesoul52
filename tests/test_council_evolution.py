"""Tests for experimental council perspective evolution."""

from __future__ import annotations

import pytest

from tonesoul.council.evolution import CouncilEvolution, PerspectiveHistory


@pytest.fixture
def evolution(tmp_path) -> CouncilEvolution:
    state_path = tmp_path / "council_evolution.json"
    return CouncilEvolution(state_path=state_path)


def test_initial_weights_are_balanced(evolution: CouncilEvolution):
    weights = evolution.get_weights()

    assert weights["guardian"] == 1.0
    assert weights["analyst"] == 1.0
    assert weights["critic"] == 1.0
    assert weights["advocate"] == 1.0
    assert weights["axiomatic"] == 1.0


def test_record_deliberation_updates_history(evolution: CouncilEvolution):
    evolution.record_deliberation(
        perspective_verdicts={
            "guardian": "approve",
            "analyst": "approve",
            "critic": "block",
            "advocate": "approve",
            "axiomatic": "approve",
        },
        final_verdict="approve",
    )

    summary = evolution.get_summary()
    history = summary["history"]
    assert history["guardian"]["aligned_with_final"] == 1
    assert history["critic"]["dissent_count"] == 1


def test_evolve_weights_rewards_alignment_without_zeroing_dissent(
    evolution: CouncilEvolution,
):
    for _ in range(5):
        evolution.record_deliberation(
            perspective_verdicts={
                "guardian": "approve",
                "analyst": "approve",
                "critic": "block",
                "advocate": "approve",
                "axiomatic": "approve",
            },
            final_verdict="approve",
        )

    weights = evolution.evolve_weights()
    assert weights["guardian"] > 1.0
    assert weights["critic"] >= CouncilEvolution.MIN_WEIGHT


def test_evolve_weights_remains_bounded_for_all_perspectives(
    evolution: CouncilEvolution,
):
    for _ in range(100):
        evolution.record_deliberation(
            perspective_verdicts={
                "guardian": "approve",
                "analyst": "block",
                "critic": "block",
                "advocate": "approve",
                "axiomatic": "approve",
            },
            final_verdict="approve",
        )
        evolution.evolve_weights()

    weights = evolution.get_weights()
    for weight in weights.values():
        assert CouncilEvolution.MIN_WEIGHT <= weight <= CouncilEvolution.MAX_WEIGHT


def test_alignment_rate_computation():
    history = PerspectiveHistory(name="test")
    history.record_vote(matched_final=True)
    history.record_vote(matched_final=True)
    history.record_vote(matched_final=False)

    assert abs(history.alignment_rate - (2 / 3)) < 1e-6


def test_summary_surfaces_suppression_observability_for_repeated_dissent(
    evolution: CouncilEvolution,
):
    for _ in range(5):
        evolution.record_deliberation(
            perspective_verdicts={
                "guardian": "approve",
                "analyst": "approve",
                "critic": "block",
                "advocate": "approve",
                "axiomatic": "approve",
            },
            final_verdict="approve",
            perspective_confidences={
                "guardian": 0.8,
                "analyst": 0.8,
                "critic": 0.91,
                "advocate": 0.8,
                "axiomatic": 0.8,
            },
        )
        evolution.evolve_weights()

    summary = evolution.get_summary()
    suppression = summary["suppression_observability"]

    assert suppression["flag"] is True
    critic_entry = next(
        entry
        for entry in suppression["suppressed_perspectives"]
        if entry["perspective"] == "critic"
    )
    assert critic_entry["weight"] < 1.0
    assert critic_entry["dissent_rate"] == 1.0
    assert critic_entry["reason"] == "weight_below_baseline_with_repeated_dissent"
