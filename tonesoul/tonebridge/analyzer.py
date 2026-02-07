"""
ToneBridge Analyzer
5-stage psychological analysis using Gemini API.
Based on 語魂論文 ToneBridge architecture.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from .types import (
    CollapseRisk,
    MeminiUnit,
    MotivePrediction,
    ResonanceDefense,
    ToneAnalysis,
    ToneBridgeResult,
)


def generate_unique_id() -> str:
    """生成唯一 ID"""
    now = datetime.now()
    import random

    return f"tone_{now.strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"


class ToneBridgeAnalyzer:
    """
    ToneBridge 五階段分析器

    階段 1: 語氣分析 (Tone Analysis)
    階段 2: 動機預測 (Motive Prediction)
    階段 3: 崩潰風險預測 (Collapse Forecasting)
    階段 4: 記憶單元生成 (Memini Unit Generation)
    階段 5: 共鳴路徑與防衛觸發 (Resonance & Defense)
    """

    def __init__(self, gemini_client=None):
        self._client = gemini_client
        self._client_error = None

    def _get_client(self):
        """Lazy load Gemini client"""
        if self._client is not None:
            return self._client
        if self._client_error is not None:
            return None
        try:
            from tonesoul.llm import create_gemini_client

            self._client = create_gemini_client()
            return self._client
        except Exception as e:
            self._client_error = e
            return None

    def is_available(self) -> bool:
        """Check if analyzer is available (Gemini client works)"""
        return self._get_client() is not None

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini and parse JSON response"""
        client = self._get_client()
        if client is None:
            raise RuntimeError("Gemini client not available")

        response_text = client.generate(prompt)

        # Parse JSON from response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re

            match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text)
            if match:
                return json.loads(match.group(1))
            # Try to find JSON object
            match = re.search(r"\{[\s\S]*\}", response_text)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Cannot parse JSON from response: {response_text[:200]}")

    # ========== 階段 1: 語氣分析 ==========
    def analyze_tone(self, text: str) -> ToneAnalysis:
        """
        階段 1: 語氣分析
        分析語句的情緒特徵、強度、方向等
        """
        prompt = f"""你是一個語氣分析助手。請分析以下中文語句，輸出 JSON。

輸出格式：
{{
  "tone_strength": 0.00,
  "tone_direction": ["", ""],
  "tone_variability": 0.00,
  "emotion_prediction": "",
  "impact_level": "low",
  "trigger_keywords": [],
  "modulation_sensitivity": 0.00,
  "semantic_intent": "",
  "emotional_depth": 0.00,
  "tone_uncertainty": 0.00
}}

數值範圍：0.00-1.00
impact_level: low/medium/high
tone_direction: 最多兩個描述語氣方向的詞，如 "questioning", "assertive", "defensive", "anxious"

語句：「{text}」

請直接輸出 JSON，不要其他說明。"""

        try:
            data = self._call_gemini(prompt)
            return ToneAnalysis(
                tone_strength=float(data.get("tone_strength", 0.5)),
                tone_direction=data.get("tone_direction", ["neutral"]),
                tone_variability=float(data.get("tone_variability", 0.0)),
                emotion_prediction=data.get("emotion_prediction", "neutral"),
                impact_level=data.get("impact_level", "low"),
                trigger_keywords=data.get("trigger_keywords", []),
                modulation_sensitivity=float(data.get("modulation_sensitivity", 0.5)),
                semantic_intent=data.get("semantic_intent", ""),
                emotional_depth=float(data.get("emotional_depth", 0.5)),
                tone_uncertainty=float(data.get("tone_uncertainty", 0.5)),
            )
        except Exception:
            # Fallback to basic analysis
            return ToneAnalysis(emotion_prediction="unknown")

    # ========== 階段 2: 動機預測 ==========
    def predict_motive(self, text: str, tone: ToneAnalysis) -> MotivePrediction:
        """
        階段 2: 動機預測
        預測語者內在動機與觸發背景
        """
        prompt = f"""你是動機預測模組。根據語句和語氣分析，預測內在動機。

輸入：
語句：「{text}」
語氣分析：{json.dumps(tone.to_dict(), ensure_ascii=False)}

輸出格式：
{{
  "motive_category": "",
  "likely_motive": "",
  "trigger_context": "",
  "echo_potential": 0.00,
  "resonance_chain_hint": []
}}

motive_category: 如 "尋求認可", "表達不滿", "自我防衛", "建立連結" 等

請直接輸出 JSON。"""

        try:
            data = self._call_gemini(prompt)
            return MotivePrediction(
                motive_category=data.get("motive_category", ""),
                likely_motive=data.get("likely_motive", ""),
                trigger_context=data.get("trigger_context", ""),
                echo_potential=float(data.get("echo_potential", 0.0)),
                resonance_chain_hint=data.get("resonance_chain_hint", []),
            )
        except Exception:
            return MotivePrediction()

    # ========== 階段 3: 崩潰風險預測 ==========
    def forecast_collapse(
        self, text: str, tone: ToneAnalysis, motive: MotivePrediction
    ) -> CollapseRisk:
        """
        階段 3: 崩潰風險預測
        預測對話可能出現情緒崩潰的風險點
        """
        prompt = f"""你是語氣崩潰點預測器。預測對話中情緒可能崩潰的風險。

輸入：
語句：「{text}」
語氣分析：{json.dumps(tone.to_dict(), ensure_ascii=False)}
動機預測：{json.dumps(motive.to_dict(), ensure_ascii=False)}

輸出格式：
{{
  "collapse_risk_level": "low",
  "collapse_type_hint": [],
  "contributing_factors": [],
  "warning_indicators": [],
  "intervention_urgency": 0.00
}}

collapse_risk_level: low/medium/high/critical
intervention_urgency: 0.00-1.00

請直接輸出 JSON。"""

        try:
            data = self._call_gemini(prompt)
            return CollapseRisk(
                collapse_risk_level=data.get("collapse_risk_level", "low"),
                collapse_type_hint=data.get("collapse_type_hint", []),
                contributing_factors=data.get("contributing_factors", []),
                warning_indicators=data.get("warning_indicators", []),
                intervention_urgency=float(data.get("intervention_urgency", 0.0)),
            )
        except Exception:
            return CollapseRisk()

    # ========== 階段 4: 記憶單元生成 ==========
    def generate_memini_unit(
        self,
        text: str,
        tone: ToneAnalysis,
        motive: MotivePrediction,
        collapse: CollapseRisk,
        response: str = "",
        council_verdict: Optional[Dict] = None,
    ) -> MeminiUnit:
        """
        階段 4: 記憶單元生成
        整合分析結果成可存儲的記憶單元
        """
        return MeminiUnit(
            id=generate_unique_id(),
            input_text=text[:200],  # Truncate for storage
            tone_analysis={
                "strength": tone.tone_strength,
                "direction": tone.tone_direction,
                "emotion": tone.emotion_prediction,
            },
            predicted_motive=motive.likely_motive,
            collapse_forecast={
                "risk_level": collapse.collapse_risk_level,
                "urgency": collapse.intervention_urgency,
            },
            resonance_traceback={
                "council_verdict": (
                    council_verdict.get("verdict", "unknown") if council_verdict else "pending"
                ),
            },
            memory_status="active",
            timestamp=datetime.now().isoformat(),
        )

    # ========== 階段 5: 共鳴路徑與防衛觸發 ==========
    def predict_resonance(self, memini: MeminiUnit) -> ResonanceDefense:
        """
        階段 5: 共鳴路徑與防衛觸發預測
        預測對話走向與建議介入策略
        """
        prompt = f"""你是語氣共鳴路徑預測器。根據記憶單元預測對話走向。

輸入：
{json.dumps(memini.to_dict(), ensure_ascii=False)}

輸出格式：
{{
  "primary_path": "",
  "secondary_path_hint": "",
  "triggered_likelihood": 0.00,
  "trigger_condition": "",
  "expected_defense_response": "",
  "suggested_intervention_strategy": ""
}}

primary_path: 如 "情緒宣洩", "尋求理解", "對抗升級" 等
suggested_intervention_strategy: 建議的回應策略

請直接輸出 JSON。"""

        try:
            data = self._call_gemini(prompt)
            return ResonanceDefense(
                primary_path=data.get("primary_path", ""),
                secondary_path_hint=data.get("secondary_path_hint", ""),
                triggered_likelihood=float(data.get("triggered_likelihood", 0.0)),
                trigger_condition=data.get("trigger_condition", ""),
                expected_defense_response=data.get("expected_defense_response", ""),
                suggested_intervention_strategy=data.get("suggested_intervention_strategy", ""),
            )
        except Exception:
            return ResonanceDefense(suggested_intervention_strategy="採用同理心回應")

    # ========== 完整分析 ==========
    def analyze(self, text: str, full_analysis: bool = True) -> ToneBridgeResult:
        """
        執行完整 ToneBridge 分析

        Args:
            text: 要分析的語句
            full_analysis: 是否執行全部 5 個階段

        Returns:
            ToneBridgeResult 包含所有分析結果
        """
        # 階段 1-3 總是執行
        tone = self.analyze_tone(text)
        motive = self.predict_motive(text, tone)
        collapse = self.forecast_collapse(text, tone, motive)

        memini = None
        resonance = None

        if full_analysis:
            # 階段 4-5
            memini = self.generate_memini_unit(text, tone, motive, collapse)
            resonance = self.predict_resonance(memini)

        return ToneBridgeResult(
            tone=tone,
            motive=motive,
            collapse=collapse,
            memini=memini,
            resonance=resonance,
        )
