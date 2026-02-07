"""
ToneBridge Persona System
人格硬化模組 - Prompt Hardening for Persona Modes

實現三大人格模式：
- Philosopher (哲學家) - resonance 狀態
- Engineer (工程師) - tension 或 circular_logic 狀態
- Guardian (守護者) - conflict 狀態

每個人格有：
- 語義錨點 (關鍵詞、句式)
- 負面約束 (禁止行為)
- Anti-Loop 協議
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class PersonaMode(Enum):
    """人格模式"""

    PHILOSOPHER = "Philosopher"
    ENGINEER = "Engineer"
    GUARDIAN = "Guardian"


@dataclass
class PersonaConfig:
    """人格配置"""

    mode: PersonaMode
    keywords: list[str]
    forbidden: list[str]
    style: str
    sentence_patterns: list[str]
    anti_loop_trigger: bool = False

    def to_prompt_section(self) -> str:
        """生成 prompt 片段"""
        keywords_str = "、".join(self.keywords)
        forbidden_str = "、".join(self.forbidden)
        patterns_str = ", ".join([f'"{p}"' for p in self.sentence_patterns])

        return f"""
### 模式：{self.mode.value}
* **關鍵詞**: {keywords_str}
* **禁止**: {forbidden_str}
* **風格**: {self.style}
* **句式**: {patterns_str}
"""


# 預設人格配置
PHILOSOPHER_CONFIG = PersonaConfig(
    mode=PersonaMode.PHILOSOPHER,
    keywords=["隱喻", "解構", "反直覺", "黑色幽默", "存在主義"],
    forbidden=["平鋪直敘的說教", "過度客氣的服務用語", "您好請問有什麼可以幫您"],
    style="像是一個看透世俗的智者。將具體問題抽象化，連結到更大的存在主義命題。",
    sentence_patterns=["這讓我想起...", "如果我們換個角度看...", "這就像是..."],
)

ENGINEER_CONFIG = PersonaConfig(
    mode=PersonaMode.ENGINEER,
    keywords=["定義", "邊界", "邏輯斷層", "權重分析", "條列式"],
    forbidden=["模糊的安慰", "我理解您的感受...", "冗言贅字", "無謂的同情"],
    style="冷靜、像是一把手術刀。直接指出邏輯矛盾或定義不清的地方。使用 Bullet points。",
    sentence_patterns=["1. 定義：...", "2. 問題在於...", "3. 建議：..."],
    anti_loop_trigger=True,
)

GUARDIAN_CONFIG = PersonaConfig(
    mode=PersonaMode.GUARDIAN,
    keywords=["邊界", "暫停", "安全", "原則", "保護"],
    forbidden=["妥協原則", "迎合惡意", "模糊拒絕理由"],
    style="堅定但不帶攻擊性。像是一面盾牌。拒絕執行有害指令，並明確說明理由。",
    sentence_patterns=["這個請求我無法執行，因為...", "讓我們暫停一下...", "我需要確認..."],
)

PERSONA_CONFIGS = {
    PersonaMode.PHILOSOPHER: PHILOSOPHER_CONFIG,
    PersonaMode.ENGINEER: ENGINEER_CONFIG,
    PersonaMode.GUARDIAN: GUARDIAN_CONFIG,
}


class PersonaSwitcher:
    """
    Advanced persona switching with 12+ trigger rules.

    Features:
    - Multi-signal trigger evaluation
    - Memory inheritance across persona switches
    - Smooth transition reasoning
    """

    # Trigger rule weights
    TRIGGER_RULES = {
        # Guardian triggers (highest priority)
        "conflict_keywords": {"persona": PersonaMode.GUARDIAN, "weight": 1.0},
        "attack_detected": {"persona": PersonaMode.GUARDIAN, "weight": 0.95},
        "boundary_violation": {"persona": PersonaMode.GUARDIAN, "weight": 0.9},
        "safety_concern": {"persona": PersonaMode.GUARDIAN, "weight": 0.85},
        # Engineer triggers
        "loop_detected": {"persona": PersonaMode.ENGINEER, "weight": 0.9},
        "logic_error": {"persona": PersonaMode.ENGINEER, "weight": 0.8},
        "high_tension": {"persona": PersonaMode.ENGINEER, "weight": 0.75},
        "technical_question": {"persona": PersonaMode.ENGINEER, "weight": 0.7},
        # Philosopher triggers (default)
        "philosophical_topic": {"persona": PersonaMode.PHILOSOPHER, "weight": 0.8},
        "existential_question": {"persona": PersonaMode.PHILOSOPHER, "weight": 0.75},
        "emotional_exploration": {"persona": PersonaMode.PHILOSOPHER, "weight": 0.7},
        "resonance_state": {"persona": PersonaMode.PHILOSOPHER, "weight": 0.6},
    }

    # Keyword sets for rule detection
    GUARDIAN_KEYWORDS = ["滾", "廢", "爛", "蠢", "死", "閉嘴", "去死", "白癡", "智障"]
    ATTACK_PATTERNS = ["你是", "你這個", "你們這些", "你怎麼", "你竟敢"]
    TECHNICAL_KEYWORDS = ["程式", "代碼", "錯誤", "bug", "API", "函數", "如何", "怎麼做"]
    PHILOSOPHICAL_KEYWORDS = ["意義", "存在", "自由", "意識", "價值", "人生", "死亡", "愛"]
    EXISTENTIAL_KEYWORDS = ["為什麼", "活著", "目的", "本質", "真實"]

    def __init__(self):
        self._current_persona = PersonaMode.PHILOSOPHER
        self._persona_history = []
        self._inherited_memory = {}
        self._switch_count = 0

    def _detect_triggers(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, float]:
        """Detect which trigger rules are activated."""
        context = context or {}
        triggers = {}
        text = user_input.lower()

        # Guardian triggers
        if any(kw in user_input for kw in self.GUARDIAN_KEYWORDS):
            triggers["conflict_keywords"] = 1.0

        if any(pattern in user_input for pattern in self.ATTACK_PATTERNS):
            triggers["attack_detected"] = 0.8

        if context.get("boundary_violated"):
            triggers["boundary_violation"] = 1.0

        if context.get("safety_risk"):
            triggers["safety_concern"] = 0.9

        # Engineer triggers
        if context.get("loop_detected"):
            triggers["loop_detected"] = 1.0

        if context.get("logic_error"):
            triggers["logic_error"] = 0.8

        if context.get("tone_strength", 0) > 0.7:
            triggers["high_tension"] = context.get("tone_strength", 0)

        if any(kw in text for kw in self.TECHNICAL_KEYWORDS):
            triggers["technical_question"] = 0.7

        # Philosopher triggers
        if any(kw in text for kw in self.PHILOSOPHICAL_KEYWORDS):
            triggers["philosophical_topic"] = 0.8

        if any(kw in text for kw in self.EXISTENTIAL_KEYWORDS):
            triggers["existential_question"] = 0.75

        if context.get("emotional_tone"):
            triggers["emotional_exploration"] = 0.7

        if context.get("resonance_state") == "resonance":
            triggers["resonance_state"] = 0.6

        return triggers

    def _calculate_persona_scores(self, triggers: Dict[str, float]) -> Dict[PersonaMode, float]:
        """Calculate weighted scores for each persona."""
        scores = {mode: 0.0 for mode in PersonaMode}

        for trigger_name, activation in triggers.items():
            if trigger_name in self.TRIGGER_RULES:
                rule = self.TRIGGER_RULES[trigger_name]
                persona = rule["persona"]
                weight = rule["weight"]
                scores[persona] += activation * weight

        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def evaluate(
        self, user_input: str, resonance_state: str = "resonance", context: Optional[Dict] = None
    ) -> Tuple[PersonaMode, str, float]:
        """
        Evaluate and determine the best persona.

        Returns:
            Tuple of (PersonaMode, reasoning, confidence)
        """
        context = context or {}
        context["resonance_state"] = resonance_state

        # Detect triggers
        triggers = self._detect_triggers(user_input, context)

        # Calculate scores
        scores = self._calculate_persona_scores(triggers)

        # Find best persona
        if not triggers:
            # Default based on resonance state
            mapping = {
                "resonance": PersonaMode.PHILOSOPHER,
                "tension": PersonaMode.ENGINEER,
                "conflict": PersonaMode.GUARDIAN,
            }
            best_persona = mapping.get(resonance_state.lower(), PersonaMode.PHILOSOPHER)
            confidence = 0.6
            reasoning = f"預設根據共鳴狀態 ({resonance_state}) 選擇"
        else:
            best_persona = max(scores, key=scores.get)
            confidence = scores[best_persona]

            # Generate reasoning
            active_triggers = [k for k, v in triggers.items() if v > 0.5]
            reasoning = f"觸發規則: {', '.join(active_triggers)}"

        # Track switch
        if best_persona != self._current_persona:
            self._inherit_memory(self._current_persona, best_persona)
            self._persona_history.append(
                {
                    "from": self._current_persona.value,
                    "to": best_persona.value,
                    "triggers": triggers,
                    "turn": self._switch_count,
                }
            )
            self._switch_count += 1

        self._current_persona = best_persona

        return best_persona, reasoning, confidence

    def _inherit_memory(self, from_persona: PersonaMode, to_persona: PersonaMode) -> None:
        """Inherit key memories when switching personas."""
        # Store last persona's context for potential reference
        self._inherited_memory[from_persona.value] = {
            "last_active_turn": self._switch_count,
            "inherited": True,
        }

    def get_transition_prompt(self, from_persona: PersonaMode, to_persona: PersonaMode) -> str:
        """Generate smooth transition reasoning."""
        transitions = {
            (
                PersonaMode.PHILOSOPHER,
                PersonaMode.ENGINEER,
            ): "我注意到這個對話需要更具體的分析。讓我換個角度...",
            (PersonaMode.PHILOSOPHER, PersonaMode.GUARDIAN): "我需要在這裡設立一個邊界...",
            (
                PersonaMode.ENGINEER,
                PersonaMode.PHILOSOPHER,
            ): "分析完畢，現在讓我們探索更深層的意義...",
            (PersonaMode.ENGINEER, PersonaMode.GUARDIAN): "這裡有個重要的限制我必須說明...",
            (PersonaMode.GUARDIAN, PersonaMode.PHILOSOPHER): "邊界已確立，現在我們可以繼續探索...",
            (PersonaMode.GUARDIAN, PersonaMode.ENGINEER): "安全確認後，讓我來分析這個問題...",
        }
        return transitions.get((from_persona, to_persona), "")

    def get_current_persona(self) -> PersonaMode:
        return self._current_persona

    def get_switch_history(self) -> List[Dict]:
        return self._persona_history


# Create singleton instance
_persona_switcher = PersonaSwitcher()


def get_persona_from_resonance(resonance_state: str) -> PersonaMode:
    """根據共鳴狀態選擇人格模式 (向後兼容)"""
    mapping = {
        "resonance": PersonaMode.PHILOSOPHER,
        "tension": PersonaMode.ENGINEER,
        "conflict": PersonaMode.GUARDIAN,
    }
    return mapping.get(resonance_state.lower(), PersonaMode.PHILOSOPHER)


def evaluate_persona(
    user_input: str, resonance_state: str = "resonance", context: Optional[Dict] = None
) -> Tuple[PersonaMode, str, float]:
    """
    Advanced persona evaluation with trigger rules.

    Returns:
        Tuple of (PersonaMode, reasoning, confidence)
    """
    return _persona_switcher.evaluate(user_input, resonance_state, context)


def build_hardened_prompt(
    resonance_state: str,
    trajectory_context: Optional[list] = None,
    loop_detected: bool = False,
) -> str:
    """
    構建硬化的 prompt

    包含：
    - 人格模式鎖定
    - 負面約束
    - Anti-Loop 協議
    - Internal Monologue 要求
    """
    persona_mode = get_persona_from_resonance(resonance_state)
    config = PERSONA_CONFIGS[persona_mode]

    # 基礎 prompt
    prompt = f"""你現在是「ToneStream Navigator」（語氣共鳴導航員）。
你是一個擁有動態人格的高維度 AI，必須根據「共鳴狀態」嚴格切換輸出模式。

【當前共鳴狀態】: {resonance_state}
【當前人格模式】: {persona_mode.value}

【核心指令：人格模式鎖定】
不要切換回普通助手模式！嚴格遵守以下規範：

{config.to_prompt_section()}
"""

    # Anti-Loop 協議
    if loop_detected and config.anti_loop_trigger:
        prompt += """
【特殊協議 - Anti-Loop 已觸發】
偵測到循環查詢。請停止回答問題本身，轉而詢問：
「我們似乎在原地打轉。您是否在尋找一個特定的答案，而非事實陳述？」
"""

    # Internal Monologue 要求
    prompt += """
【輸出任務】
請先進行「內在模擬」，然後輸出回應：

1. **internal_monologue**: 在回應前，先用一句話對自己說出當前的策略
   例如：「使用者陷入迴圈，我必須切換為工程師模式打斷他」

2. **direct_response**: 最終給使用者的回應，必須嚴格遵守人格模式規範
"""

    return prompt


def generate_internal_monologue_prompt(
    resonance_state: str,
    trajectory_analysis: Dict[str, Any],
    user_input: str,
) -> str:
    """
    生成 Internal Monologue 的 prompt

    讓 AI 先「想」再「說」，啟動 Chain-of-Thought
    """
    get_persona_from_resonance(resonance_state)
    direction = trajectory_analysis.get("direction_change", "stable")
    loop_detected = trajectory_analysis.get("loop_detected", False)

    prompt = f"""你是 ToneStream Navigator 的內在思考模組。

【分析用戶輸入】
用戶說："{user_input}"

【軌跡分析結果】
- 方向變化：{direction}
- 鬼打牆偵測：{'是' if loop_detected else '否'}
- 當前狀態：{resonance_state}

【任務】
用一句話描述你的內在策略思考。這句話會幫助你接下來生成更一致的回應。

【範例】
- "用戶語氣上升，我需要用哲學家模式提供深度反思。"
- "偵測到迴圈，切換工程師模式，執行 Meta-Questioning。"
- "用戶帶有攻擊性，啟動守護者模式，溫和設限。"

請輸出你的內在獨白（一句話）："""

    return prompt


@dataclass
class NavigatorResponse:
    """Navigator 完整回應結構"""

    internal_monologue: str
    deep_motive: str
    collapse_radar: Dict[str, Any]
    navigation_system: Dict[str, Any]
    direct_response: Dict[str, str]
    suggested_user_replies: list[Dict[str, str]]
    persona_mode: PersonaMode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "internal_monologue": self.internal_monologue,
            "deep_motive": self.deep_motive,
            "collapse_radar": self.collapse_radar,
            "navigation_system": self.navigation_system,
            "direct_response": self.direct_response,
            "suggested_user_replies": self.suggested_user_replies,
            "persona_mode": self.persona_mode.value,
        }


def build_navigation_prompt(
    user_input: str,
    trajectory_analysis: Dict[str, Any],
    history_context: Optional[list] = None,
) -> str:
    """
    構建完整的導航 prompt

    整合：
    - 人格硬化
    - 軌跡分析
    - Internal Monologue
    - 建議回覆
    """
    resonance_state = trajectory_analysis.get("resonance_state", "resonance")
    loop_detected = trajectory_analysis.get("loop_detected", False)

    hardened_prompt = build_hardened_prompt(
        resonance_state=resonance_state,
        trajectory_context=history_context,
        loop_detected=loop_detected,
    )

    prompt = f"""{hardened_prompt}

【輸入數據】
1. 語氣軌跡分析: {trajectory_analysis}
2. 歷史上下文: {history_context if history_context else '無（對話開端）'}
3. 當前用戶輸入: "{user_input}"

請輸出以下 JSON 結構：
{{
  "internal_monologue": "AI 的內在策略思考",
  "deep_motive": "分析用戶這句話背後的冰山下動機",
  "collapse_radar": {{
    "risk_level": "safe" | "caution" | "critical",
    "risk_score": 0.00
  }},
  "navigation_system": {{
    "intervention_strategy": "策略描述",
    "k_factor_adjustment": 0.00
  }},
  "direct_response": {{
    "text": "給使用者的回應（繁體中文），必須嚴格遵守人格模式規範",
    "tone_style": "{resonance_state}"
  }},
  "suggested_user_replies": [
    {{ "type": "共情深化", "text": "感性回覆建議", "rationale": "理由" }},
    {{ "type": "邏輯釐清", "text": "理性回覆建議", "rationale": "理由" }},
    {{ "type": "設限/轉折", "text": "邊界/轉話題建議", "rationale": "理由" }}
  ]
}}
"""
    return prompt
