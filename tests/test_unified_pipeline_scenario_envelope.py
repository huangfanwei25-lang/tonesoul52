from __future__ import annotations

from tonesoul.unified_pipeline import UnifiedPipeline


def test_build_scenario_envelope_available() -> None:
    pipeline = UnifiedPipeline(gemini_client=None)
    envelope = pipeline._build_scenario_envelope("請分析這個提案", history=[])

    assert envelope["enabled"] is True
    assert len(envelope["frames"]) == 3
    assert envelope["frames"][0]["label"] == "bull"


def test_build_scenario_envelope_handles_empty_input() -> None:
    pipeline = UnifiedPipeline(gemini_client=None)
    envelope = pipeline._build_scenario_envelope("", history=[])

    assert envelope["enabled"] is True
    assert "scenario_envelope_ready" in envelope["summary"]
