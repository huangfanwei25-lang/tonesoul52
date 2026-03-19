"""
ToneBridge Trajectory Analysis
軌跡推理模組 - 5-turn sliding window context

實現 ToneStream 的核心概念：
- 從單點位移升級為多點軌跡推理
- 偵測 circular_logic (鬼打牆)
- 計算 shift_magnitude
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class DirectionChange(Enum):
    """語氣變化方向"""

    STABLE = "stable"
    ESCALATING = "escalating"
    DE_ESCALATING = "de-escalating"
    ABRUPT_SHIFT = "abrupt_shift"
    CIRCULAR_LOGIC = "circular_logic"


class ResonanceState(Enum):
    """共鳴狀態 - 決定人格模式"""

    RESONANCE = "resonance"  # 共振 → 哲學家
    TENSION = "tension"  # 張力 → 工程師
    CONFLICT = "conflict"  # 斷裂 → 守護者


@dataclass
class TrajectoryTurn:
    """單輪對話資訊"""

    index: int
    user_input: str
    ai_response: str = ""
    tone_state: Optional[str] = None
    tone_strength: float = 0.5


@dataclass
class TrajectoryAnalysis:
    """軌跡分析結果"""

    shift_magnitude: float = 0.0  # 語氣位移大小 (0-1)
    direction_change: DirectionChange = DirectionChange.STABLE
    reasoning: str = ""
    resonance_state: ResonanceState = ResonanceState.RESONANCE

    # 鬼打牆偵測
    loop_count: int = 0
    loop_detected: bool = False

    # Phase 544: drift from Home vector
    drift: Optional[float] = None
    drift_alert: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "shift_magnitude": self.shift_magnitude,
            "direction_change": self.direction_change.value,
            "reasoning": self.reasoning,
            "resonance_state": self.resonance_state.value,
            "loop_count": self.loop_count,
            "loop_detected": self.loop_detected,
        }
        if self.drift is not None:
            d["drift"] = round(self.drift, 6)
        if self.drift_alert is not None:
            d["drift_alert"] = self.drift_alert
        return d


class TrajectoryAnalyzer:
    """
    軌跡分析器

    使用 5-turn sliding window 進行上下文感知的語氣分析
    """

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.history: List[TrajectoryTurn] = []

        # 鬼打牆偵測
        self._recent_inputs: List[str] = []
        self._loop_threshold = 3  # 連續相似輸入次數閾值

    def add_turn(
        self,
        user_input: str,
        ai_response: str = "",
        tone_state: str = "",
        tone_strength: float = 0.5,
    ):
        """新增一輪對話到歷史"""
        turn = TrajectoryTurn(
            index=len(self.history),
            user_input=user_input,
            ai_response=ai_response,
            tone_state=tone_state,
            tone_strength=tone_strength,
        )
        self.history.append(turn)
        self._recent_inputs.append(user_input.lower().strip())

        # 保持最近輸入在閾值內
        if len(self._recent_inputs) > self._loop_threshold * 2:
            self._recent_inputs = self._recent_inputs[-self._loop_threshold * 2 :]

    def get_context_window(self) -> List[TrajectoryTurn]:
        """取得最近的對話視窗"""
        if len(self.history) == 0:
            return []
        start_idx = max(0, len(self.history) - self.window_size)
        return self.history[start_idx:]

    def get_context_for_prompt(self) -> Optional[List[Dict[str, Any]]]:
        """取得用於 prompt 的上下文格式"""
        window = self.get_context_window()
        if not window:
            return None
        return [
            {
                "index": t.index,
                "user_input": t.user_input,
                "ai_response": t.ai_response,
                "tone_state": t.tone_state,
            }
            for t in window
        ]

    def detect_loop(self, current_input: str) -> tuple[bool, int]:
        """
        偵測鬼打牆 (circular_logic)

        當用戶連續多次輸入相似內容時觸發
        """
        current_normalized = current_input.lower().strip()

        # 簡單相似度：檢查最近輸入是否高度重複
        similar_count = 0
        for past_input in self._recent_inputs[-self._loop_threshold :]:
            if self._is_similar(current_normalized, past_input):
                similar_count += 1

        loop_detected = similar_count >= self._loop_threshold - 1
        return loop_detected, similar_count

    def _is_similar(self, a: str, b: str, threshold: float = 0.7) -> bool:
        """簡單的字串相似度檢查"""
        if not a or not b:
            return False

        # 完全相同
        if a == b:
            return True

        # 包含關係
        if a in b or b in a:
            return True

        # 共同詞彙比例
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return False

        intersection = words_a & words_b
        union = words_a | words_b
        jaccard = len(intersection) / len(union)

        return jaccard >= threshold

    def analyze(self, current_input: str, current_tone_strength: float = 0.5) -> TrajectoryAnalysis:
        """
        分析當前輸入在對話軌跡中的位置

        返回:
        - shift_magnitude: 語氣變化幅度
        - direction_change: 變化方向
        - resonance_state: 決定人格模式
        """
        # 鬼打牆偵測
        loop_detected, loop_count = self.detect_loop(current_input)

        if loop_detected:
            return TrajectoryAnalysis(
                shift_magnitude=0.1,
                direction_change=DirectionChange.CIRCULAR_LOGIC,
                reasoning="偵測到用戶重複詢問類似問題。可能需要元層級的重新定向。",
                resonance_state=ResonanceState.TENSION,  # 工程師模式處理
                loop_count=loop_count,
                loop_detected=True,
            )

        # 取得歷史視窗
        window = self.get_context_window()

        if len(window) == 0:
            # 對話開端
            return TrajectoryAnalysis(
                shift_magnitude=0.0,
                direction_change=DirectionChange.STABLE,
                reasoning="這是對話的開端。",
                resonance_state=self._infer_initial_state(current_input),
            )

        # 計算語氣變化
        prev_strength = window[-1].tone_strength if window else 0.5
        shift = abs(current_tone_strength - prev_strength)

        # 判斷變化方向
        direction = self._determine_direction(prev_strength, current_tone_strength, shift)

        # 推斷共鳴狀態
        resonance_state = self._infer_resonance_state(current_input, window, current_tone_strength)

        # 生成推理說明
        reasoning = self._generate_reasoning(window, current_input, direction, shift)

        return TrajectoryAnalysis(
            shift_magnitude=shift,
            direction_change=direction,
            reasoning=reasoning,
            resonance_state=resonance_state,
            loop_count=loop_count,
            loop_detected=False,
        )

    def _determine_direction(self, prev: float, current: float, shift: float) -> DirectionChange:
        """判斷語氣變化方向"""
        if shift > 0.5:
            return DirectionChange.ABRUPT_SHIFT
        elif shift < 0.1:
            return DirectionChange.STABLE
        elif current > prev:
            return DirectionChange.ESCALATING
        else:
            return DirectionChange.DE_ESCALATING

    def _infer_initial_state(self, text: str) -> ResonanceState:
        """推斷初始共鳴狀態"""
        # 簡單規則：檢查關鍵詞
        negative_indicators = ["不", "沒", "錯", "怎麼", "為什麼", "?", "？"]
        conflict_indicators = ["滾", "廢", "爛", "蠢", "死"]

        text_lower = text.lower()

        for word in conflict_indicators:
            if word in text_lower:
                return ResonanceState.CONFLICT

        question_count = text.count("?") + text.count("？")
        negative_count = sum(1 for w in negative_indicators if w in text)

        if question_count > 1 or negative_count > 2:
            return ResonanceState.TENSION

        return ResonanceState.RESONANCE

    def _infer_resonance_state(
        self, current: str, window: List[TrajectoryTurn], strength: float
    ) -> ResonanceState:
        """推斷當前共鳴狀態"""
        # 高張力指標
        if strength > 0.7:
            return ResonanceState.TENSION

        # 檢查歷史軌跡是否有累積張力
        if len(window) >= 3:
            recent_states = [t.tone_state for t in window[-3:]]
            if recent_states.count("tension") >= 2:
                return ResonanceState.TENSION

        # 檢查衝突指標
        conflict_words = ["停", "夠了", "閉嘴", "不要", "滾", "死"]
        for word in conflict_words:
            if word in current:
                return ResonanceState.CONFLICT

        return ResonanceState.RESONANCE

    def _generate_reasoning(
        self, window: List[TrajectoryTurn], current: str, direction: DirectionChange, shift: float
    ) -> str:
        """生成軌跡推理說明"""
        if not window:
            return "對話開始。"

        window[-1].user_input if window else ""

        if direction == DirectionChange.STABLE:
            return "語氣保持穩定，延續之前的對話風格。"
        elif direction == DirectionChange.ESCALATING:
            return f"語氣強度上升 (+{shift:.2f})，可能表示用戶在強調或激動。"
        elif direction == DirectionChange.DE_ESCALATING:
            return f"語氣強度下降 (-{shift:.2f})，可能表示用戶正在緩和或接受。"
        elif direction == DirectionChange.ABRUPT_SHIFT:
            return f"語氣發生突變 (Δ={shift:.2f})，可能是話題轉換或情緒轉折。"
        else:
            return "無法推斷變化原因。"

    def reset(self):
        """重置分析器狀態"""
        self.history.clear()
        self._recent_inputs.clear()
