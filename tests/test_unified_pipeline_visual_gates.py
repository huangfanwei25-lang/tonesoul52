from __future__ import annotations

from tonesoul.unified_pipeline import UnifiedPipeline


class _DummyChain:
    def __init__(self, frame_count: int):
        self.frame_count = frame_count


def test_visual_capture_disabled_by_env(monkeypatch):
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_ENABLED", "0")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_SAMPLE_EVERY", "1")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_MAX_FRAMES", "10")

    pipeline = UnifiedPipeline()
    assert pipeline._should_capture_visual_frame(_DummyChain(0)) is False


def test_visual_capture_respects_sampling_frequency(monkeypatch):
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_ENABLED", "1")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_SAMPLE_EVERY", "3")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_MAX_FRAMES", "10")

    pipeline = UnifiedPipeline()
    assert pipeline._should_capture_visual_frame(_DummyChain(1)) is False
    assert pipeline._should_capture_visual_frame(_DummyChain(2)) is True


def test_visual_capture_respects_max_frames(monkeypatch):
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_ENABLED", "1")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_SAMPLE_EVERY", "1")
    monkeypatch.setenv("TONESOUL_VISUAL_CHAIN_MAX_FRAMES", "3")

    pipeline = UnifiedPipeline()
    assert pipeline._should_capture_visual_frame(_DummyChain(2)) is True
    assert pipeline._should_capture_visual_frame(_DummyChain(3)) is False
