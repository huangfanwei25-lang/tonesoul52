from __future__ import annotations

import json
import sys

import pytest

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


def _verdict(
    votes: list[PerspectiveVote],
    divergence: dict | None = None,
) -> CouncilVerdict:
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
        divergence_analysis=divergence or {
            "agree": [],
            "concern": ["guardian"],
            "object": [],
            "core_divergence": "fallback path test",
            "recommended_action": "inspect fallback",
            "quality": {"score": 0.52, "band": "medium"},
        },
    )


# ─── _fallback_triggered_from_votes ──────────────────────────────────────────

class TestFallbackTriggeredFromVotes:
    def test_detects_bracket_fallback_marker(self):
        assert council_cli._fallback_triggered_from_votes(
            [_vote("[fallback_to_rules] VTP Philosopher fallback to rules; rule vote")]
        ) is True

    def test_detects_plain_fallback_to_rules(self):
        assert council_cli._fallback_triggered_from_votes(
            [_vote("fallback to rules used here")]
        ) is True

    def test_detects_vtp_philosopher_marker(self):
        assert council_cli._fallback_triggered_from_votes(
            [_vote("vtp philosopher fallback to rules invoked")]
        ) is True

    def test_regular_reasoning_returns_false(self):
        assert council_cli._fallback_triggered_from_votes([_vote("no fallback used")]) is False

    def test_empty_list_returns_false(self):
        assert council_cli._fallback_triggered_from_votes([]) is False

    def test_non_list_returns_false(self):
        assert council_cli._fallback_triggered_from_votes("not-a-list") is False

    def test_vote_without_reasoning_attr_skipped(self):
        class NoReasoning:
            pass

        assert council_cli._fallback_triggered_from_votes([NoReasoning()]) is False

    def test_non_string_reasoning_skipped(self):
        vote = _vote("ok")
        vote.reasoning = 42  # type: ignore[assignment]
        assert council_cli._fallback_triggered_from_votes([vote]) is False


# ─── _run_council ─────────────────────────────────────────────────────────────

class TestRunCouncil:
    def _setup_monkeypatch(self, monkeypatch, votes=None, divergence=None):
        import tonesoul.council.runtime as runtime_mod

        monkeypatch.setattr(council_cli, "_build_council_request", lambda *a, **kw: object())
        monkeypatch.setattr(
            runtime_mod.CouncilRuntime,
            "deliberate",
            lambda self, request: _verdict(votes or [_vote("ok")], divergence),
        )

    def test_surfaces_fallback_triggered(self, monkeypatch):
        import tonesoul.council.runtime as runtime_mod

        monkeypatch.setattr(council_cli, "_build_council_request", lambda *a, **kw: object())
        monkeypatch.setattr(
            runtime_mod.CouncilRuntime,
            "deliberate",
            lambda self, req: _verdict(
                [_vote("[fallback_to_rules] VTP Philosopher fallback to rules; rules verdict")]
            ),
        )
        result = council_cli._run_council(draft="draft output", intent="intent", mode="local")
        assert result["fallback_triggered"] is True

    def test_returns_required_keys(self, monkeypatch):
        self._setup_monkeypatch(monkeypatch)
        result = council_cli._run_council(draft="text", intent="", mode="local")
        for key in ("verdict", "summary", "tension", "quality_band", "quality_score",
                    "fallback_triggered", "divergence"):
            assert key in result

    def test_tension_computed_from_divergence(self, monkeypatch):
        self._setup_monkeypatch(
            monkeypatch,
            divergence={
                "agree": ["a"],
                "concern": ["b", "c"],
                "object": ["d"],
                "quality": {"score": 0.5, "band": "medium"},
            },
        )
        result = council_cli._run_council(draft="text", intent="", mode="local")
        # tension = (1*1.0 + 2*0.5) / max(1+2+1, 1) = 2.0/4 = 0.5
        assert result["tension"] == pytest.approx(0.5, abs=0.01)

    def test_quality_score_rounded(self, monkeypatch):
        self._setup_monkeypatch(
            monkeypatch,
            divergence={"agree": [], "concern": [], "object": [],
                        "quality": {"score": 0.76543, "band": "high"}},
        )
        result = council_cli._run_council(draft="text", intent="", mode="local")
        assert result["quality_score"] == pytest.approx(0.765, abs=0.001)

    def test_verdict_string_extracted(self, monkeypatch):
        self._setup_monkeypatch(monkeypatch)
        result = council_cli._run_council(draft="text", intent="", mode="local")
        assert isinstance(result["verdict"], str)


# ─── main() ──────────────────────────────────────────────────────────────────

class TestMain:
    def test_main_outputs_json_to_stdout(self, monkeypatch, capsys):
        import tonesoul.council.runtime as runtime_mod

        monkeypatch.setattr(council_cli, "_build_council_request", lambda *a, **kw: object())
        monkeypatch.setattr(
            runtime_mod.CouncilRuntime,
            "deliberate",
            lambda self, req: _verdict([_vote("ok")]),
        )
        council_cli.main(["--draft", "test output"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "verdict" in data

    def test_main_error_outputs_concern_json(self, monkeypatch, capsys):
        def _bad_build(*args, **kwargs):
            raise RuntimeError("deliberation error")

        monkeypatch.setattr(council_cli, "_run_council", _bad_build)
        with pytest.raises(SystemExit) as exc_info:
            council_cli.main(["--draft", "some text"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["verdict"] == "CONCERN"
        assert "Council CLI error" in data["summary"]
