from __future__ import annotations

from tonesoul.tonebridge.analyzer import ToneBridgeAnalyzer
from tonesoul.tonebridge.types import (
    CollapseRisk,
    MeminiUnit,
    MotivePrediction,
    ResonanceDefense,
    ToneAnalysis,
)


class FakeClient:
    def __init__(self, response: str):
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def test_is_available_uses_injected_client() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    assert analyzer.is_available() is True


def test_call_gemini_parses_raw_json() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient('{"tone_strength": 0.8}'))

    payload = analyzer._call_gemini("prompt")

    assert payload["tone_strength"] == 0.8


def test_call_gemini_parses_markdown_json_block() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient('```json\n{"tone_strength": 0.7}\n```'))

    payload = analyzer._call_gemini("prompt")

    assert payload["tone_strength"] == 0.7


def test_call_gemini_extracts_embedded_json_object() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient('prefix {"tone_strength": 0.6} suffix'))

    payload = analyzer._call_gemini("prompt")

    assert payload["tone_strength"] == 0.6


def test_call_gemini_raises_when_json_is_missing() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("no json here"))

    try:
        analyzer._call_gemini("prompt")
    except ValueError as exc:
        assert "Cannot parse JSON" in str(exc)
    else:
        raise AssertionError("expected ValueError when response does not contain JSON")


def test_call_gemini_raises_when_client_is_unavailable() -> None:
    analyzer = ToneBridgeAnalyzer()
    analyzer._client_error = RuntimeError("boom")

    try:
        analyzer._call_gemini("prompt")
    except RuntimeError as exc:
        assert "Gemini client not available" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when no Gemini client is available")


def test_analyze_tone_maps_json_payload_into_dataclass(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    monkeypatch.setattr(
        analyzer,
        "_call_gemini",
        lambda prompt: {
            "tone_strength": "0.9",
            "tone_direction": ["assertive", "questioning"],
            "tone_variability": "0.4",
            "emotion_prediction": "curious",
            "impact_level": "high",
            "trigger_keywords": ["debug", "api"],
            "modulation_sensitivity": "0.2",
            "semantic_intent": "seek_clarity",
            "emotional_depth": "0.7",
            "tone_uncertainty": "0.1",
        },
    )

    tone = analyzer.analyze_tone("debug this API")

    assert tone == ToneAnalysis(
        tone_strength=0.9,
        tone_direction=["assertive", "questioning"],
        tone_variability=0.4,
        emotion_prediction="curious",
        impact_level="high",
        trigger_keywords=["debug", "api"],
        modulation_sensitivity=0.2,
        semantic_intent="seek_clarity",
        emotional_depth=0.7,
        tone_uncertainty=0.1,
    )


def test_analyze_tone_falls_back_to_unknown_when_call_fails(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    monkeypatch.setattr(
        analyzer, "_call_gemini", lambda prompt: (_ for _ in ()).throw(ValueError())
    )

    tone = analyzer.analyze_tone("hello")

    assert tone.emotion_prediction == "unknown"
    assert tone.tone_direction == ["neutral"]
    assert tone.tone_strength == 0.5


def test_predict_motive_maps_json_payload(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    tone = ToneAnalysis(emotion_prediction="focused")
    monkeypatch.setattr(
        analyzer,
        "_call_gemini",
        lambda prompt: {
            "motive_category": "clarification",
            "likely_motive": "reduce ambiguity",
            "trigger_context": "technical uncertainty",
            "echo_potential": "0.55",
            "resonance_chain_hint": ["precision", "repair"],
        },
    )

    motive = analyzer.predict_motive("please clarify", tone)

    assert motive == MotivePrediction(
        motive_category="clarification",
        likely_motive="reduce ambiguity",
        trigger_context="technical uncertainty",
        echo_potential=0.55,
        resonance_chain_hint=["precision", "repair"],
    )


def test_predict_motive_falls_back_to_empty_prediction(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    monkeypatch.setattr(
        analyzer, "_call_gemini", lambda prompt: (_ for _ in ()).throw(RuntimeError())
    )

    motive = analyzer.predict_motive("hello", ToneAnalysis())

    assert motive == MotivePrediction()


def test_forecast_collapse_maps_json_payload(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    monkeypatch.setattr(
        analyzer,
        "_call_gemini",
        lambda prompt: {
            "collapse_risk_level": "critical",
            "collapse_type_hint": ["spiral"],
            "contributing_factors": ["stress"],
            "warning_indicators": ["looping"],
            "intervention_urgency": "0.95",
        },
    )

    collapse = analyzer.forecast_collapse("hello", ToneAnalysis(), MotivePrediction())

    assert collapse == CollapseRisk(
        collapse_risk_level="critical",
        collapse_type_hint=["spiral"],
        contributing_factors=["stress"],
        warning_indicators=["looping"],
        intervention_urgency=0.95,
    )


def test_generate_memini_unit_truncates_input_and_tracks_verdict() -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))

    memini = analyzer.generate_memini_unit(
        text="x" * 250,
        tone=ToneAnalysis(
            tone_strength=0.9,
            tone_direction=["assertive"],
            emotion_prediction="determined",
        ),
        motive=MotivePrediction(likely_motive="protect user"),
        collapse=CollapseRisk(collapse_risk_level="high", intervention_urgency=0.8),
        council_verdict={"verdict": "approve"},
    )

    assert memini.id.startswith("tone_")
    assert memini.input_text == "x" * 200
    assert memini.tone_analysis == {
        "strength": 0.9,
        "direction": ["assertive"],
        "emotion": "determined",
    }
    assert memini.collapse_forecast == {"risk_level": "high", "urgency": 0.8}
    assert memini.resonance_traceback["council_verdict"] == "approve"
    assert memini.memory_status == "active"


def test_predict_resonance_returns_fallback_strategy_when_call_fails(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    monkeypatch.setattr(
        analyzer, "_call_gemini", lambda prompt: (_ for _ in ()).throw(ValueError())
    )

    resonance = analyzer.predict_resonance(MeminiUnit(id="m1"))

    assert isinstance(resonance, ResonanceDefense)
    assert resonance.suggested_intervention_strategy


def test_analyze_runs_all_stages_for_full_analysis(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    calls: list[str] = []
    tone = ToneAnalysis(emotion_prediction="calm")
    motive = MotivePrediction(likely_motive="understand")
    collapse = CollapseRisk(collapse_risk_level="medium")
    memini = MeminiUnit(id="m1")
    resonance = ResonanceDefense(primary_path="reflect")

    monkeypatch.setattr(analyzer, "analyze_tone", lambda text: calls.append("tone") or tone)
    monkeypatch.setattr(
        analyzer,
        "predict_motive",
        lambda text, tone_analysis: calls.append("motive") or motive,
    )
    monkeypatch.setattr(
        analyzer,
        "forecast_collapse",
        lambda text, tone_analysis, motive_prediction: calls.append("collapse") or collapse,
    )
    monkeypatch.setattr(
        analyzer,
        "generate_memini_unit",
        lambda text, tone_analysis, motive_prediction, collapse_risk: calls.append("memini")
        or memini,
    )
    monkeypatch.setattr(
        analyzer,
        "predict_resonance",
        lambda memini_unit: calls.append("resonance") or resonance,
    )

    result = analyzer.analyze("hello", full_analysis=True)

    assert calls == ["tone", "motive", "collapse", "memini", "resonance"]
    assert result.memini is memini
    assert result.resonance is resonance


def test_analyze_skips_late_stages_when_full_analysis_is_disabled(monkeypatch) -> None:
    analyzer = ToneBridgeAnalyzer(gemini_client=FakeClient("{}"))
    tone = ToneAnalysis()
    motive = MotivePrediction()
    collapse = CollapseRisk()
    memini_calls: list[str] = []

    monkeypatch.setattr(analyzer, "analyze_tone", lambda text: tone)
    monkeypatch.setattr(analyzer, "predict_motive", lambda text, tone_analysis: motive)
    monkeypatch.setattr(
        analyzer,
        "forecast_collapse",
        lambda text, tone_analysis, motive_prediction: collapse,
    )
    monkeypatch.setattr(
        analyzer,
        "generate_memini_unit",
        lambda *args, **kwargs: memini_calls.append("memini"),
    )
    monkeypatch.setattr(
        analyzer,
        "predict_resonance",
        lambda *args, **kwargs: memini_calls.append("resonance"),
    )

    result = analyzer.analyze("hello", full_analysis=False)

    assert memini_calls == []
    assert result.memini is None
    assert result.resonance is None
