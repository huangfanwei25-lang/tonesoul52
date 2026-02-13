"""Test cross-session memory recovery behavior."""

from __future__ import annotations

from tonesoul.memory.visual_chain import FrameType, VisualChain
from tonesoul.unified_pipeline import UnifiedPipeline


def test_recovery_runs_once():
    pipeline = UnifiedPipeline()
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.5, "verdict": "approve", "topics": ["intro"]},
        tags=["auto"],
    )
    pipeline._visual_chain = chain

    first = pipeline._try_cross_session_recovery("first")
    second = pipeline._try_cross_session_recovery("second")

    assert "Cross-Session Recovery" in first
    assert first.endswith("first")
    assert second == "second"


def test_recovery_with_existing_frames():
    pipeline = UnifiedPipeline()
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.5, "verdict": "approve", "topics": ["intro"]},
        tags=["auto"],
    )
    pipeline._visual_chain = chain

    result = pipeline._try_cross_session_recovery("hello")
    assert "Cross-Session Recovery" in result
    assert "hello" in result
    assert "Turn 0" in result


def test_recovery_empty_chain():
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = VisualChain()

    result = pipeline._try_cross_session_recovery("hello")
    assert result == "hello"
