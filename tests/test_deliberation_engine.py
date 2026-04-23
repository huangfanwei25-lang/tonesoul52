from __future__ import annotations

import asyncio

from tonesoul.deliberation.engine import InternalDeliberation
from tonesoul.deliberation.types import DeliberationContext, DeliberationWeights, RoundResult


def test_deliberate_sync_uses_asyncio_run_when_no_loop_is_running(monkeypatch) -> None:
    engine = InternalDeliberation()
    context = DeliberationContext(user_input="hello")
    sentinel_viewpoints = ["parallel"]
    calls: list[tuple[str, object]] = []

    async def _fake_parallel(context_arg):
        calls.append(("parallel", context_arg))
        return sentinel_viewpoints

    def _fake_sequential(context_arg):
        calls.append(("sequential", context_arg))
        return ["sequential"]

    monkeypatch.setattr(engine, "_parallel_think", _fake_parallel)
    monkeypatch.setattr(engine, "_sequential_think", _fake_sequential)
    monkeypatch.setattr(
        engine,
        "_build_round_result",
        lambda round_number, viewpoints, _context: RoundResult(
            round_number=round_number,
            viewpoints=viewpoints,
            tensions=[],
            weights=DeliberationWeights(),
            aggregate_tension=0.0,
        ),
    )
    monkeypatch.setattr(
        engine._gravity,
        "synthesize",
        lambda viewpoints, _context, _elapsed_ms: {"viewpoints": viewpoints},
    )
    monkeypatch.setattr(engine._gravity, "_find_aegis", lambda viewpoints: None)

    result = engine.deliberate_sync(context)

    assert result == {"viewpoints": sentinel_viewpoints}
    assert calls == [("parallel", context)]


def test_deliberate_sync_falls_back_to_sequential_inside_running_loop(monkeypatch) -> None:
    engine = InternalDeliberation()
    context = DeliberationContext(user_input="hello")
    calls: list[tuple[str, object]] = []

    async def _fake_parallel(context_arg):
        calls.append(("parallel", context_arg))
        return ["parallel"]

    def _fake_sequential(context_arg):
        calls.append(("sequential", context_arg))
        return ["sequential"]

    monkeypatch.setattr(engine, "_parallel_think", _fake_parallel)
    monkeypatch.setattr(engine, "_sequential_think", _fake_sequential)
    monkeypatch.setattr(
        engine,
        "_build_round_result",
        lambda round_number, viewpoints, _context: RoundResult(
            round_number=round_number,
            viewpoints=viewpoints,
            tensions=[],
            weights=DeliberationWeights(),
            aggregate_tension=0.0,
        ),
    )
    monkeypatch.setattr(
        engine._gravity,
        "synthesize",
        lambda viewpoints, _context, _elapsed_ms: {"viewpoints": viewpoints},
    )
    monkeypatch.setattr(engine._gravity, "_find_aegis", lambda viewpoints: None)

    async def _exercise():
        return engine.deliberate_sync(context)

    result = asyncio.run(_exercise())

    assert result == {"viewpoints": ["sequential"]}
    assert calls == [("sequential", context)]


def test_record_outcome_updates_persona_track_summary(tmp_path, monkeypatch) -> None:
    from tonesoul.deliberation.persona_track_record import create_persona_track_record

    engine = InternalDeliberation()
    engine._persona_track_record = create_persona_track_record(tmp_path / "ptr.json")
    engine._gravity._track_record = engine._persona_track_record

    engine.record_outcome(
        dominant_voice="muse",
        verdict="approve",
        resonance_state="resonance",
        loop_detected=False,
    )

    summary = engine.get_persona_track_summary()
    assert summary["muse"]["total"] == 1


# ── _build_debate_context ─────────────────────────────────────────────────────

def test_build_debate_context_copies_fields_and_adds_prior_viewpoints() -> None:
    from tonesoul.deliberation.types import ViewPoint, PerspectiveType

    context = DeliberationContext(
        user_input="hello",
        tone_strength=0.7,
        resonance_state="resonance",
        loop_detected=True,
    )
    vp = ViewPoint(perspective=PerspectiveType.MUSE, confidence=0.8, reasoning="ok", proposed_response="resp")

    debate_ctx = InternalDeliberation._build_debate_context(context, [vp], round_number=2)

    assert debate_ctx.user_input == "hello"
    assert debate_ctx.tone_strength == 0.7
    assert debate_ctx.loop_detected is True
    assert debate_ctx.debate_round == 2
    assert len(debate_ctx.prior_viewpoints) == 1
    assert debate_ctx.prior_viewpoints[0]["perspective"] == "muse"


# ── _attach_round_metadata ────────────────────────────────────────────────────

def test_attach_round_metadata_sets_rounds_used_and_results() -> None:
    from types import SimpleNamespace

    result = SimpleNamespace(rounds_used=0, round_results=[])
    round_results = [
        RoundResult(round_number=1, viewpoints=[], tensions=[], weights=DeliberationWeights(), aggregate_tension=0.0),
        RoundResult(round_number=2, viewpoints=[], tensions=[], weights=DeliberationWeights(), aggregate_tension=0.0),
    ]

    InternalDeliberation._attach_round_metadata(result, round_results)

    assert result.rounds_used == 2
    assert len(result.round_results) == 2


def test_attach_round_metadata_skips_objects_without_attrs() -> None:
    from types import SimpleNamespace

    result = SimpleNamespace()  # no rounds_used / round_results
    InternalDeliberation._attach_round_metadata(result, [])
    # should not raise


# ── get_last_debate ───────────────────────────────────────────────────────────

def test_get_last_debate_returns_no_debate_status_when_empty() -> None:
    engine = InternalDeliberation()
    assert engine.get_last_debate() == {"status": "no_debate_yet"}


# ── deliberation_count ────────────────────────────────────────────────────────

def test_deliberation_count_starts_at_zero() -> None:
    assert InternalDeliberation().deliberation_count == 0


# ── record_outcome with no dominant_voice ─────────────────────────────────────

def test_record_outcome_skips_when_no_dominant_voice() -> None:
    engine = InternalDeliberation()
    before = engine.deliberation_count
    engine.record_outcome(dominant_voice=None, verdict="approve")
    # count should not have changed and muse total remains 0
    summary = engine.get_persona_track_summary()
    assert summary.get("muse", {}).get("total", 0) == 0
