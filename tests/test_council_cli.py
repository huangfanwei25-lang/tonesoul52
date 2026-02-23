from __future__ import annotations

from tonesoul.council import council_cli
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _vote(reasoning: str) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=PerspectiveType.GUARDIAN,
        decision=VoteDecision.CONCERN,
        confidence=0.6,
        reasoning=reasoning,
    )


def _verdict(votes: list[PerspectiveVote]) -> CouncilVerdict:
    return CouncilVerdict(
        verdict=VerdictType.REFINE,
        coherence=CoherenceScore(
            c_inter=0.5,
            approval_rate=0.25,
            min_confidence=0.5,
            has_strong_objection=False,
        ),
        votes=votes,
        summary="test summary",
        divergence_analysis={
            "agree": [],
            "concern": ["guardian"],
            "object": [],
            "core_divergence": "fallback path test",
            "recommended_action": "inspect fallback",
            "quality": {"score": 0.52, "band": "medium"},
        },
    )


def test_fallback_triggered_from_votes_detects_marker() -> None:
    assert (
        council_cli._fallback_triggered_from_votes(
            [_vote("[fallback_to_rules] VTP Philosopher fallback to rules; rule vote")]
        )
        is True
    )


def test_fallback_triggered_from_votes_handles_regular_reasoning() -> None:
    assert council_cli._fallback_triggered_from_votes([_vote("no fallback used")]) is False


def test_run_council_surfaces_fallback_triggered(monkeypatch) -> None:
    import tonesoul.council.runtime as runtime_mod

    monkeypatch.setattr(council_cli, "_build_council_request", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        runtime_mod.CouncilRuntime,
        "deliberate",
        lambda self, request: _verdict(
            [_vote("[fallback_to_rules] VTP Philosopher fallback to rules; rules verdict")]
        ),
    )

    result = council_cli._run_council(
        draft="draft output",
        intent="intent",
        mode="local",
    )
    assert result["fallback_triggered"] is True
