"""
ToneBridge Types
Data structures for the 5-stage psychological analysis pipeline.
Based on 語魂論文 ToneBridge architecture.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToneAnalysis:
    """階段 1: 語氣分析結果"""

    tone_strength: float = 0.5
    tone_direction: List[str] = field(default_factory=lambda: ["neutral"])
    tone_variability: float = 0.0
    emotion_prediction: str = "neutral"
    impact_level: str = "low"  # low, medium, high
    trigger_keywords: List[str] = field(default_factory=list)
    persona_alignment: str = ""
    modulation_sensitivity: float = 0.5
    semantic_intent: str = ""
    emotional_depth: float = 0.5
    resonance_span: str = ""
    tone_uncertainty: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tone_strength": self.tone_strength,
            "tone_direction": self.tone_direction,
            "tone_variability": self.tone_variability,
            "emotion_prediction": self.emotion_prediction,
            "impact_level": self.impact_level,
            "trigger_keywords": self.trigger_keywords,
            "modulation_sensitivity": self.modulation_sensitivity,
            "semantic_intent": self.semantic_intent,
            "emotional_depth": self.emotional_depth,
            "tone_uncertainty": self.tone_uncertainty,
        }


@dataclass
class MotivePrediction:
    """階段 2: 動機預測結果"""

    motive_category: str = ""
    likely_motive: str = ""
    trigger_context: str = ""
    echo_potential: float = 0.0
    resonance_chain_hint: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motive_category": self.motive_category,
            "likely_motive": self.likely_motive,
            "trigger_context": self.trigger_context,
            "echo_potential": self.echo_potential,
            "resonance_chain_hint": self.resonance_chain_hint,
        }


@dataclass
class CollapseRisk:
    """階段 3: 崩潰風險預測"""

    collapse_risk_level: str = "low"  # low, medium, high, critical
    collapse_type_hint: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    warning_indicators: List[str] = field(default_factory=list)
    intervention_urgency: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collapse_risk_level": self.collapse_risk_level,
            "collapse_type_hint": self.collapse_type_hint,
            "contributing_factors": self.contributing_factors,
            "warning_indicators": self.warning_indicators,
            "intervention_urgency": self.intervention_urgency,
        }


@dataclass
class MeminiUnit:
    """階段 4: 語氣記憶單元"""

    id: str = ""
    input_text: str = ""
    tone_analysis: Dict[str, Any] = field(default_factory=dict)
    predicted_motive: str = ""
    collapse_forecast: Dict[str, Any] = field(default_factory=dict)
    resonance_traceback: Dict[str, Any] = field(default_factory=dict)
    memory_status: str = "active"
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "input_text": self.input_text,
            "tone_analysis": self.tone_analysis,
            "predicted_motive": self.predicted_motive,
            "collapse_forecast": self.collapse_forecast,
            "resonance_traceback": self.resonance_traceback,
            "memory_status": self.memory_status,
            "timestamp": self.timestamp,
        }


@dataclass
class ResonanceDefense:
    """階段 5: 共鳴路徑與防衛觸發預測"""

    primary_path: str = ""
    secondary_path_hint: str = ""
    triggered_likelihood: float = 0.0
    trigger_condition: str = ""
    expected_defense_response: str = ""
    suggested_intervention_strategy: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resonance_path": {
                "primary_path": self.primary_path,
                "secondary_path_hint": self.secondary_path_hint,
            },
            "defense_trigger": {
                "triggered_likelihood": self.triggered_likelihood,
                "trigger_condition": self.trigger_condition,
                "expected_defense_response": self.expected_defense_response,
            },
            "suggested_intervention_strategy": self.suggested_intervention_strategy,
        }


@dataclass
class ToneBridgeResult:
    """ToneBridge 完整分析結果"""

    tone: ToneAnalysis
    motive: MotivePrediction
    collapse: CollapseRisk
    memini: Optional[MeminiUnit] = None
    resonance: Optional[ResonanceDefense] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "tone_analysis": self.tone.to_dict(),
            "motive_prediction": self.motive.to_dict(),
            "collapse_risk": self.collapse.to_dict(),
        }
        if self.memini:
            result["memini_unit"] = self.memini.to_dict()
        if self.resonance:
            result["resonance_defense"] = self.resonance.to_dict()
        return result

    def get_summary_zh(self) -> str:
        """生成中文摘要"""
        lines = []
        lines.append(
            f"語氣強度：{self.tone.tone_strength:.2f}，情緒預測：{self.tone.emotion_prediction}"
        )
        lines.append(
            f"動機類別：{self.motive.motive_category}，觸發情境：{self.motive.trigger_context}"
        )
        lines.append(
            f"崩潰風險：{self.collapse.collapse_risk_level}，介入緊迫度：{self.collapse.intervention_urgency:.2f}"
        )
        if self.resonance:
            lines.append(f"共鳴路徑：{self.resonance.primary_path}")
            lines.append(f"建議策略：{self.resonance.suggested_intervention_strategy}")
        return "\n".join(lines)
