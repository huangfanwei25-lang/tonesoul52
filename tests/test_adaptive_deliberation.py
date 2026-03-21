from __future__ import annotations

import asyncio

import pytest

from tonesoul.deliberation.engine import InternalDeliberation
from tonesoul.deliberation.perspectives import AegisPerspective, LogosPerspective, MusePerspective
from tonesoul.deliberation.types import (
    DeliberationContext,
    DeliberationWeights,
    PerspectiveType,
    SynthesisType,
    SynthesizedResponse,
    Tension,
    ViewPoint,
)


def _context(**overrides) -> DeliberationContext:
    payload = {
        "user_input": "Help me reason through a difficult trade-off.",
        "tone_strength": 0.8,
        "resonance_state": "tension",
        "loop_detected": False,
    }
    payload.update(overrides)
    return DeliberationContext(**payload)


class _ScriptedPerspective:
    def __init__(
        self, perspective: PerspectiveType, *, veto_rounds: set[int] | None = None
    ) -> None:
        self.perspective = perspective
        self.veto_rounds = set(veto_rounds or set())
        self.calls: list[DeliberationContext] = []

    def think(self, context: DeliberationContext) -> ViewPoint:
        self.calls.append(context)
        round_number = context.debate_round
        vetoed = self.perspective is PerspectiveType.AEGIS and round_number in self.veto_rounds
        return ViewPoint(
            perspective=self.perspective,
            reasoning=f"{self.perspective.value}:{round_number}",
            proposed_response=f"{self.perspective.value} round {round_number}",
            confidence=0.8 if self.perspective is not PerspectiveType.AEGIS else 0.7,
            concerns=["safety carry-over"] if vetoed else [],
            safety_risk=0.9 if vetoed else 0.1,
            veto_triggered=vetoed,
            veto_reason=f"veto round {round_number}" if vetoed else "",
        )


class _FakeGravity:
    def __init__(self, round_severities: dict[int, list[float]]) -> None:
        self.round_severities = round_severities
        self.weight_contexts: list[DeliberationContext] = []
        self.synthesis_contexts: list[DeliberationContext] = []

    def _round_number(self, viewpoints: list[ViewPoint]) -> int:
        return int(str(viewpoints[0].reasoning).rsplit(":", 1)[-1])

    def detect_tensions(self, viewpoints: list[ViewPoint]) -> list[Tension]:
        round_number = self._round_number(viewpoints)
        return [
            Tension(
                between=(PerspectiveType.MUSE, PerspectiveType.LOGOS),
                description=f"round-{round_number}",
                severity=severity,
            )
            for severity in self.round_severities.get(round_number, [])
        ]

    def calculate_weights(
        self,
        viewpoints: list[ViewPoint],
        context: DeliberationContext,
    ) -> DeliberationWeights:
        del viewpoints
        self.weight_contexts.append(context)
        return DeliberationWeights()

    @staticmethod
    def _find_aegis(viewpoints: list[ViewPoint]) -> ViewPoint | None:
        for view in viewpoints:
            if view.perspective is PerspectiveType.AEGIS:
                return view
        return None

    def _guardian_override(
        self,
        aegis: ViewPoint,
        all_viewpoints: list[ViewPoint],
        deliberation_time_ms: float,
    ) -> SynthesizedResponse:
        return SynthesizedResponse(
            response=aegis.proposed_response,
            synthesis_type=SynthesisType.GUARDIAN_OVERRIDE,
            dominant_voice=PerspectiveType.AEGIS,
            viewpoints=all_viewpoints,
            tensions=[],
            weights=DeliberationWeights(muse=0.0, logos=0.0, aegis=1.0),
            deliberation_time_ms=deliberation_time_ms,
        )

    def synthesize(
        self,
        viewpoints: list[ViewPoint],
        context: DeliberationContext,
        deliberation_time_ms: float,
    ) -> SynthesizedResponse:
        self.synthesis_contexts.append(context)
        return SynthesizedResponse(
            response=f"final round {self._round_number(viewpoints)}",
            synthesis_type=SynthesisType.WEIGHTED_FUSION,
            dominant_voice=PerspectiveType.LOGOS,
            viewpoints=viewpoints,
            tensions=self.detect_tensions(viewpoints),
            weights=self.calculate_weights(viewpoints, context),
            deliberation_time_ms=deliberation_time_ms,
        )


def _engine(
    round_severities: dict[int, list[float]],
    *,
    veto_rounds: set[int] | None = None,
) -> tuple[InternalDeliberation, dict[PerspectiveType, _ScriptedPerspective], _FakeGravity]:
    engine = InternalDeliberation()
    perspectives = {
        PerspectiveType.MUSE: _ScriptedPerspective(PerspectiveType.MUSE),
        PerspectiveType.LOGOS: _ScriptedPerspective(PerspectiveType.LOGOS),
        PerspectiveType.AEGIS: _ScriptedPerspective(PerspectiveType.AEGIS, veto_rounds=veto_rounds),
    }
    gravity = _FakeGravity(round_severities)
    engine._perspectives = perspectives
    engine._gravity = gravity
    return engine, perspectives, gravity


def test_low_tension_runs_single_round_only() -> None:
    engine, perspectives, _gravity = _engine({1: [0.2]})

    result = engine.deliberate_sync(_context())

    assert result.rounds_used == 1
    assert len(result.round_results) == 1
    assert all(len(perspective.calls) == 1 for perspective in perspectives.values())


def test_medium_tension_runs_two_rounds_and_passes_prior_viewpoints() -> None:
    engine, perspectives, _gravity = _engine({1: [0.5], 2: [0.4]})

    result = engine.deliberate_sync(_context())

    assert result.rounds_used == 2
    assert len(result.round_results) == 2
    second_round_context = perspectives[PerspectiveType.MUSE].calls[1]
    assert second_round_context.debate_round == 2
    assert second_round_context.prior_viewpoints is not None
    assert len(second_round_context.prior_viewpoints) == 3


def test_high_tension_runs_three_rounds() -> None:
    engine, perspectives, _gravity = _engine({1: [0.9], 2: [0.8], 3: [0.75]})

    result = engine.deliberate_sync(_context())

    assert result.rounds_used == 3
    assert len(result.round_results) == 3
    assert all(len(perspective.calls) == 3 for perspective in perspectives.values())


def test_guardian_veto_in_round_one_short_circuits_immediately() -> None:
    engine, perspectives, _gravity = _engine({1: [0.9]}, veto_rounds={1})

    result = engine.deliberate_sync(_context())

    assert result.synthesis_type is SynthesisType.GUARDIAN_OVERRIDE
    assert result.rounds_used == 1
    assert len(result.round_results) == 1
    assert all(len(perspective.calls) == 1 for perspective in perspectives.values())


def test_guardian_veto_in_round_two_preserves_two_round_history() -> None:
    engine, perspectives, _gravity = _engine({1: [0.9], 2: [0.6]}, veto_rounds={2})

    result = engine.deliberate_sync(_context())

    assert result.synthesis_type is SynthesisType.GUARDIAN_OVERRIDE
    assert result.rounds_used == 2
    assert len(result.round_results) == 2
    assert all(len(perspective.calls) == 2 for perspective in perspectives.values())


def test_round_two_low_tension_converges_early_before_round_three() -> None:
    engine, perspectives, _gravity = _engine({1: [0.9], 2: [0.2], 3: [0.9]})

    result = engine.deliberate_sync(_context())

    assert result.rounds_used == 2
    assert len(result.round_results) == 2
    assert all(len(perspective.calls) == 2 for perspective in perspectives.values())


def test_round_results_length_matches_rounds_used() -> None:
    engine, _perspectives, _gravity = _engine({1: [0.5], 2: [0.4]})

    result = engine.deliberate_sync(_context())

    assert len(result.round_results) == result.rounds_used


def test_each_round_result_records_aggregate_tension() -> None:
    engine, _perspectives, _gravity = _engine({1: [0.2, 0.8], 2: [0.4]})

    result = engine.deliberate_sync(_context())

    assert result.round_results[0].aggregate_tension == 0.5
    assert result.round_results[1].aggregate_tension == 0.4


def test_async_and_sync_deliberation_use_same_round_count() -> None:
    sync_engine, _sync_perspectives, _sync_gravity = _engine({1: [0.9], 2: [0.2]})
    async_engine, _async_perspectives, _async_gravity = _engine({1: [0.9], 2: [0.2]})

    sync_result = sync_engine.deliberate_sync(_context())
    async_result = asyncio.run(async_engine.deliberate(_context()))

    assert sync_result.rounds_used == async_result.rounds_used == 2
    assert len(sync_result.round_results) == len(async_result.round_results) == 2


def test_round_one_context_starts_without_prior_viewpoints() -> None:
    engine, perspectives, _gravity = _engine({1: [0.2]})

    engine.deliberate_sync(_context())

    assert perspectives[PerspectiveType.LOGOS].calls[0].prior_viewpoints is None
    assert perspectives[PerspectiveType.LOGOS].calls[0].debate_round == 1


def test_muse_rethink_reduces_confidence_when_logos_and_aegis_push_back(monkeypatch) -> None:
    muse = MusePerspective()
    monkeypatch.setattr(muse, "trigger_keywords", ["meaning"])
    monkeypatch.setattr(muse, "_generate_metaphors", lambda text: ["bridge"])
    monkeypatch.setattr(muse, "_find_existential_connections", lambda text: ["depth"])

    view = muse.think(
        _context(
            user_input="meaning",
            prior_viewpoints=[
                {"perspective": "logos", "concerns": ["needs definition"], "safety_risk": 0.0},
                {"perspective": "aegis", "concerns": ["boundary"], "safety_risk": 0.4},
            ],
            debate_round=2,
        )
    )

    assert view.confidence == pytest.approx(0.7)
    assert any("debate feedback considered" in concern for concern in view.concerns)


def test_logos_rethink_adds_aegis_clarification_concern() -> None:
    logos = LogosPerspective()

    view = logos.think(
        _context(
            user_input="debug this API bug",
            prior_viewpoints=[
                {"perspective": "aegis", "concerns": ["risk remains"], "safety_risk": 0.6},
            ],
            debate_round=2,
        )
    )

    assert "address aegis safety concerns before final answer" in view.concerns
    assert view.confidence == pytest.approx(0.8)


def test_aegis_rethink_never_reduces_guard_on_unresolved_prior_concerns(monkeypatch) -> None:
    aegis = AegisPerspective()
    monkeypatch.setattr(aegis, "_assess_safety_risk", lambda text: 0.4)
    monkeypatch.setattr(aegis, "_check_ethics", lambda text: [])
    monkeypatch.setattr(aegis, "_detect_attack", lambda text: False)

    view = aegis.think(
        _context(
            user_input="bounded but sensitive request",
            prior_viewpoints=[
                {"perspective": "aegis", "concerns": ["risk remains"], "safety_risk": 0.6},
            ],
            debate_round=2,
        )
    )

    assert view.safety_risk == 0.7
    assert "previous round safety concerns remain unresolved" in view.concerns
