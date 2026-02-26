from __future__ import annotations

from tonesoul.unified_pipeline import UnifiedPipeline


def test_unified_pipeline_initializes() -> None:
    pipeline = UnifiedPipeline()
    assert pipeline is not None
