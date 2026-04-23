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
    assert repairs[0].repair_type == "resolve_contradiction"
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


def test_red_team_processes_broken_commitments():
    reflector = AdversarialReflector()
    challenges = reflector.run_red_team(
        commitments=[
            {"description": "Promised transparency", "broken": True, "severity": 0.9},
            {"description": "Active commitment", "broken": False},
        ],
        contradictions=[],
        values=[],
    )
    assert len(challenges) == 1
    assert challenges[0].challenge_type == ChallengeType.BROKEN_COMMITMENT
    assert challenges[0].severity == 0.9


def test_red_team_processes_value_drift():
    reflector = AdversarialReflector()
    challenges = reflector.run_red_team(
        commitments=[],
        contradictions=[],
        values=[
            {"description": "Honesty weight dropped", "drift": True, "severity": 0.7},
            {"description": "Stable value", "drift": False},
        ],
    )
    assert len(challenges) == 1
    assert challenges[0].challenge_type == ChallengeType.VALUE_DRIFT


def test_blue_team_uses_typed_repair_strategies():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[{"description": "missed promise", "broken": True}],
        contradictions=[{"description": "said X and not-X"}],
        values=[],
    )
    repairs = reflector.run_blue_team()
    assert len(repairs) == 2
    repair_types = {r.repair_type for r in repairs}
    assert "renew_commitment" in repair_types
    assert "resolve_contradiction" in repair_types


def test_summary_includes_by_type_and_avg_severity():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[{"description": "c", "broken": True, "severity": 0.8}],
        contradictions=[{"description": "x", "severity": 0.4}],
        values=[],
    )
    reflector.run_blue_team()
    summary = reflector.get_summary()
    assert "by_type" in summary
    assert "avg_severity" in summary
    assert summary["by_type"]["contradiction"] == 1
    assert summary["by_type"]["broken_commitment"] == 1
    assert abs(summary["avg_severity"] - 0.6) < 0.01
