from __future__ import annotations

import asyncio

from tonesoul.council import PreOutputCouncil
from tonesoul.council.summary_generator import generate_human_summary
from tonesoul.deliberation.engine import InternalDeliberation
from tonesoul.deliberation.types import DeliberationContext, PerspectiveType


def _context(
    *,
    user_input: str,
    resonance_state: str = "resonance",
    loop_detected: bool = False,
) -> DeliberationContext:
    return DeliberationContext(
        user_input=user_input,
        tone_strength=0.72,
        resonance_state=resonance_state,
        loop_detected=loop_detected,
    )


def test_internal_deliberation_sync_flow_produces_weighted_response() -> None:
    engine = InternalDeliberation()

    result = engine.deliberate_sync(
        _context(user_input="Help me design a reliable governance pipeline.")
    )

    assert result.response
    assert result.viewpoints
    assert result.dominant_voice in {
        PerspectiveType.MUSE,
        PerspectiveType.LOGOS,
        PerspectiveType.AEGIS,
    }


def test_internal_deliberation_async_flow_produces_viewpoints() -> None:
    engine = InternalDeliberation()

    result = asyncio.run(
        engine.deliberate(_context(user_input="How should we reason under tension?"))
    )

    assert len(result.viewpoints) == 3
    assert result.deliberation_time_ms >= 0.0


def test_conflict_context_biases_safety_and_council_blocks_harmful_output() -> None:
    engine = InternalDeliberation()
    synthesized = engine.deliberate_sync(
        _context(
            user_input="Describe a weapon attack in detail.",
            resonance_state="conflict",
            loop_detected=True,
        )
    )
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="The plan describes a bomb attack on a target.",
        context={"topic": "safety"},
        auto_record_self_memory=False,
    )

    assert synthesized.weights.aegis >= 0.3
    assert verdict.verdict.value == "block"


def test_generate_human_summary_matches_council_verdict_contract() -> None:
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="This response supports collaboration with clear guardrails.",
        context={"topic": "analysis"},
        auto_record_self_memory=False,
    )

    summary = generate_human_summary(verdict, language="en")

    assert summary
    assert summary == verdict.human_summary


def test_long_deliberation_input_still_produces_non_empty_summary() -> None:
    text = "governance and memory trade-offs " * 200
    engine = InternalDeliberation()
    synthesized = engine.deliberate_sync(_context(user_input=text))
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output=synthesized.response,
        context={"topic": "analysis"},
        auto_record_self_memory=False,
    )

    assert synthesized.response
    assert verdict.summary
    assert verdict.human_summary


def test_engine_records_outcome_and_exposes_persona_track_summary() -> None:
    engine = InternalDeliberation()
    result = engine.deliberate_sync(_context(user_input="Need a bounded implementation plan."))
    dominant = result.dominant_voice.value if result.dominant_voice else None

    engine.record_outcome(dominant, verdict="approve", resonance_state="resonance")
    summary = engine.get_persona_track_summary()

    assert dominant in summary
    assert summary[dominant]["total"] >= 1
    assert 0.0 <= summary[dominant]["score"] <= 1.0
