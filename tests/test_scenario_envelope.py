from __future__ import annotations

from tonesoul.tonebridge.scenario_envelope import ScenarioEnvelopeBuilder


def test_scenario_envelope_has_three_frames() -> None:
    builder = ScenarioEnvelopeBuilder()
    envelope = builder.build("請幫我評估架構風險", history=[])

    assert envelope["enabled"] is True
    assert envelope["source"] == "deterministic_heuristic_v1"
    assert len(envelope["frames"]) == 3
    labels = [f["label"] for f in envelope["frames"]]
    assert labels == ["bull", "base", "bear"]


def test_scenario_envelope_includes_history_turns() -> None:
    builder = ScenarioEnvelopeBuilder()
    history = [{"user": "a", "assistant": "b"}, {"user": "c", "assistant": "d"}]
    envelope = builder.build("整理下一步", history=history)

    assert envelope["history_turns"] == 2


def test_scenario_envelope_summary_line_present() -> None:
    builder = ScenarioEnvelopeBuilder()
    envelope = builder.build("這是一段測試輸入")

    assert "scenario_envelope_ready" in envelope["summary"]
    assert "frames=3" in envelope["summary"]
