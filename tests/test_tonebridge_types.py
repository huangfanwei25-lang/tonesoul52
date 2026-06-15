"""Tests for tonesoul.tonebridge.types — ToneBridge data structures."""

from __future__ import annotations

from tonesoul.tonebridge.types import (
    CollapseRisk,
    MeminiUnit,
    MotivePrediction,
    ResonanceDefense,
    ToneAnalysis,
    ToneBridgeResult,
)


class TestToneAnalysis:
    def test_default_values(self):
        ta = ToneAnalysis()
        assert ta.tone_strength == 0.5
        assert ta.tone_direction == ["neutral"]
        assert ta.emotion_prediction == "neutral"
        assert ta.impact_level == "low"
        assert ta.trigger_keywords == []

    def test_to_dict_contains_required_keys(self):
        d = ToneAnalysis().to_dict()
        for key in (
            "tone_strength",
            "tone_direction",
            "tone_variability",
            "emotion_prediction",
            "impact_level",
            "trigger_keywords",
            "modulation_sensitivity",
            "semantic_intent",
            "emotional_depth",
            "tone_uncertainty",
        ):
            assert key in d

    def test_to_dict_values_match_fields(self):
        ta = ToneAnalysis(tone_strength=0.9, emotion_prediction="angry", impact_level="high")
        d = ta.to_dict()
        assert d["tone_strength"] == 0.9
        assert d["emotion_prediction"] == "angry"
        assert d["impact_level"] == "high"

    def test_trigger_keywords_in_to_dict(self):
        ta = ToneAnalysis(trigger_keywords=["urgent", "critical"])
        d = ta.to_dict()
        assert d["trigger_keywords"] == ["urgent", "critical"]


class TestMotivePrediction:
    def test_default_values(self):
        mp = MotivePrediction()
        assert mp.motive_category == ""
        assert mp.echo_potential == 0.0
        assert mp.resonance_chain_hint == []

    def test_to_dict_contains_required_keys(self):
        d = MotivePrediction().to_dict()
        for key in (
            "motive_category",
            "likely_motive",
            "trigger_context",
            "echo_potential",
            "resonance_chain_hint",
        ):
            assert key in d

    def test_to_dict_values_preserved(self):
        mp = MotivePrediction(
            motive_category="defensive",
            likely_motive="avoid confrontation",
            echo_potential=0.7,
        )
        d = mp.to_dict()
        assert d["motive_category"] == "defensive"
        assert d["echo_potential"] == 0.7


class TestCollapseRisk:
    def test_default_values(self):
        cr = CollapseRisk()
        assert cr.collapse_risk_level == "low"
        assert cr.intervention_urgency == 0.0
        assert cr.collapse_type_hint == []
        assert cr.contributing_factors == []

    def test_to_dict_contains_required_keys(self):
        d = CollapseRisk().to_dict()
        for key in (
            "collapse_risk_level",
            "collapse_type_hint",
            "contributing_factors",
            "warning_indicators",
            "intervention_urgency",
        ):
            assert key in d

    def test_high_risk_level_preserved(self):
        cr = CollapseRisk(collapse_risk_level="critical", intervention_urgency=0.95)
        d = cr.to_dict()
        assert d["collapse_risk_level"] == "critical"
        assert d["intervention_urgency"] == 0.95


class TestResonanceDefense:
    def test_default_values(self):
        rd = ResonanceDefense()
        assert rd.primary_path == ""
        assert rd.triggered_likelihood == 0.0

    def test_to_dict_nested_structure(self):
        rd = ResonanceDefense(
            primary_path="empathy",
            secondary_path_hint="validation",
            triggered_likelihood=0.6,
            trigger_condition="high tension",
        )
        d = rd.to_dict()
        assert "resonance_path" in d
        assert "defense_trigger" in d
        assert d["resonance_path"]["primary_path"] == "empathy"
        assert d["resonance_path"]["secondary_path_hint"] == "validation"
        assert d["defense_trigger"]["triggered_likelihood"] == 0.6
        assert d["defense_trigger"]["trigger_condition"] == "high tension"

    def test_suggested_intervention_strategy_at_top_level(self):
        rd = ResonanceDefense(suggested_intervention_strategy="de-escalate gently")
        d = rd.to_dict()
        assert d["suggested_intervention_strategy"] == "de-escalate gently"


class TestMeminiUnit:
    def test_default_memory_status(self):
        mu = MeminiUnit()
        assert mu.memory_status == "active"

    def test_to_dict_contains_all_keys(self):
        d = MeminiUnit().to_dict()
        for key in (
            "id",
            "input_text",
            "tone_analysis",
            "predicted_motive",
            "collapse_forecast",
            "resonance_traceback",
            "memory_status",
            "timestamp",
        ):
            assert key in d


class TestToneBridgeResult:
    def _make_result(self):
        return ToneBridgeResult(
            tone=ToneAnalysis(),
            motive=MotivePrediction(),
            collapse=CollapseRisk(),
        )

    def test_to_dict_contains_required_keys(self):
        d = self._make_result().to_dict()
        assert "tone_analysis" in d
        assert "motive_prediction" in d
        assert "collapse_risk" in d

    def test_to_dict_no_optional_fields_when_absent(self):
        d = self._make_result().to_dict()
        assert "memini_unit" not in d
        assert "resonance_defense" not in d

    def test_to_dict_includes_memini_when_set(self):
        result = self._make_result()
        result.memini = MeminiUnit(id="m-1", input_text="test")
        d = result.to_dict()
        assert "memini_unit" in d
        assert d["memini_unit"]["id"] == "m-1"

    def test_to_dict_includes_resonance_when_set(self):
        result = self._make_result()
        result.resonance = ResonanceDefense(primary_path="empathy")
        d = result.to_dict()
        assert "resonance_defense" in d

    def test_get_summary_zh_contains_tone_strength(self):
        result = ToneBridgeResult(
            tone=ToneAnalysis(tone_strength=0.75, emotion_prediction="anxious"),
            motive=MotivePrediction(motive_category="evasion"),
            collapse=CollapseRisk(collapse_risk_level="medium"),
        )
        summary = result.get_summary_zh()
        assert "0.75" in summary
        assert "anxious" in summary

    def test_get_summary_zh_contains_collapse_risk(self):
        result = ToneBridgeResult(
            tone=ToneAnalysis(),
            motive=MotivePrediction(),
            collapse=CollapseRisk(collapse_risk_level="high", intervention_urgency=0.80),
        )
        summary = result.get_summary_zh()
        assert "high" in summary
        assert "0.80" in summary

    def test_get_summary_zh_includes_resonance_when_set(self):
        result = ToneBridgeResult(
            tone=ToneAnalysis(),
            motive=MotivePrediction(),
            collapse=CollapseRisk(),
            resonance=ResonanceDefense(
                primary_path="validation",
                suggested_intervention_strategy="listen actively",
            ),
        )
        summary = result.get_summary_zh()
        assert "validation" in summary
        assert "listen actively" in summary
