"""Test semantic trigger tension-driven visual chain checks."""

from __future__ import annotations

from tonesoul.memory.visual_chain import FrameType, VisualChain
from tonesoul.unified_pipeline import UnifiedPipeline


def test_low_tension_no_trigger():
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = VisualChain()

    result = pipeline._semantic_trigger_check(
        tension_score=0.3,
        current_topics=["honesty"],
        user_message="hello",
    )
    assert result == "hello"


def test_high_tension_triggers_history_context():
    pipeline = UnifiedPipeline()
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 1",
        data={"tension": 0.8, "topics": ["honesty"], "verdict": "approve"},
        tags=["auto", "high_tension"],
    )
    pipeline._visual_chain = chain

    result = pipeline._semantic_trigger_check(
        tension_score=0.85,
        current_topics=["honesty", "trust"],
        user_message="I need to discuss something",
    )
    assert "Semantic Trigger" in result
    assert "High-tension history frames" in result
    assert "Recurring topics" in result


def test_high_tension_without_history_keeps_message():
    pipeline = UnifiedPipeline()
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.2, "topics": ["neutral"]},
        tags=["auto"],
    )
    pipeline._visual_chain = chain

    result = pipeline._semantic_trigger_check(
        tension_score=0.9,
        current_topics=["neutral"],
        user_message="hello",
    )
    assert result == "hello"


def test_recurring_topic_detected():
    pipeline = UnifiedPipeline()
    chain = VisualChain()
    for index in range(3):
        chain.capture(
            frame_type=FrameType.SESSION_STATE,
            title=f"Turn {index}",
            data={"tension": 0.75 + index * 0.05, "topics": ["conflict"]},
            tags=["auto", "high_tension"],
        )
    pipeline._visual_chain = chain

    result = pipeline._semantic_trigger_check(
        tension_score=0.8,
        current_topics=["conflict"],
        user_message="msg",
    )
    assert "conflict" in result.lower()
