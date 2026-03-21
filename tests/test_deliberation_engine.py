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
