"""Tests for visual chain context injection into prompt inputs."""

from __future__ import annotations

from tonesoul.memory.visual_chain import FrameType, VisualChain
from tonesoul.unified_pipeline import UnifiedPipeline


def _build_chain_with_frame() -> VisualChain:
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.3, "verdict": "approve", "council_mode": "hybrid"},
        tags=["auto"],
    )
    return chain


def test_visual_context_markdown_contains_recent_frame():
    chain = _build_chain_with_frame()
    markdown = chain.render_recent_as_markdown(n=3)
    assert "Visual Memory Chain" in markdown
    assert "session_state" in markdown
    assert len(markdown) > 50


def test_pipeline_injects_visual_context_when_frames_exist():
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = _build_chain_with_frame()

    original = "這是一段使用者訊息"
    updated = pipeline._inject_visual_context(original)

    assert updated.startswith("[脈絡記憶 — 最近視覺快照]")
    assert "Visual Memory Chain" in updated
    assert original in updated


def test_pipeline_skips_visual_context_when_chain_is_empty():
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = VisualChain()

    original = "這是一段使用者訊息"
    updated = pipeline._inject_visual_context(original)

    assert updated == original
