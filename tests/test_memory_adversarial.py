"""Tests for experimental adversarial self-reflection stub."""

from __future__ import annotations

from tonesoul.memory.adversarial import AdversarialReflector, Challenge, ChallengeType


def test_challenge_to_dict():
    challenge = Challenge(
        challenge_type=ChallengeType.CONTRADICTION,
        description="stated X then stated not-X",
        evidence=["turn-4", "turn-9"],
        severity=0.8,
    )
    payload = challenge.to_dict()

    assert payload["type"] == "contradiction"
    assert payload["description"] == "stated X then stated not-X"
    assert payload["evidence"] == ["turn-4", "turn-9"]
    assert payload["severity"] == 0.8


def test_red_team_converts_contradictions_and_clamps_severity():
    reflector = AdversarialReflector()
    challenges = reflector.run_red_team(
        commitments=[],
        contradictions=[
            {"description": "honesty vs deception", "path": ["a", "b"], "severity": 2.0},
            {"description": "missing severity", "path": "single-node"},
        ],
        values=[],
    )

    assert len(challenges) == 2
    assert challenges[0].severity == 1.0
    assert challenges[0].evidence == ["a", "b"]
    assert challenges[1].evidence == ["single-node"]


def test_blue_team_uses_last_red_team_results_by_default():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[],
        contradictions=[{"description": "c1"}],
        values=[],
    )

    repairs = reflector.run_blue_team()
    assert len(repairs) == 1
    assert repairs[0].repair_type == "acknowledge_change"
    assert "c1" in repairs[0].explanation


def test_summary_counts_challenges_and_repairs():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[],
        contradictions=[{"description": "c1"}, {"description": "c2"}],
        values=[],
    )
    reflector.run_blue_team()

    summary = reflector.get_summary()
    assert summary["challenges_found"] == 2
    assert summary["repairs_proposed"] == 2
    assert len(summary["challenges"]) == 2
    assert len(summary["repairs"]) == 2
