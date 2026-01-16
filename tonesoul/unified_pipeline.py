"""
ToneSoul Unified Pipeline
Combines ToneBridge psychological analysis with Council deliberation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json


@dataclass
class UnifiedResponse:
    """統一管線的完整回應"""
    response: str
    council_verdict: Dict[str, Any]
    tonebridge_analysis: Dict[str, Any]
    inner_narrative: str
    intervention_strategy: str = ""
    # ToneStream 新增欄位
    internal_monologue: str = ""
    persona_mode: str = ""
    trajectory_analysis: Dict[str, Any] = field(default_factory=dict)
    suggested_replies: list = field(default_factory=list)
    # Third Axiom 欄位
    self_commits: List[Dict[str, Any]] = field(default_factory=list)
    ruptures: List[Dict[str, Any]] = field(default_factory=list)
    emergent_values: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "response": self.response,
            "council_verdict": self.council_verdict,
            "tonebridge_analysis": self.tonebridge_analysis,
            "inner_narrative": self.inner_narrative,
            "intervention_strategy": self.intervention_strategy,
            "internal_monologue": self.internal_monologue,
            "persona_mode": self.persona_mode,
            "trajectory_analysis": self.trajectory_analysis,
            "suggested_replies": self.suggested_replies,
            # Third Axiom
            "self_commits": self.self_commits,
            "ruptures": self.ruptures,
            "emergent_values": self.emergent_values,
        }


class UnifiedPipeline:
    """
    ToneSoul 統一管線 (含第三公理整合)
    
    流程：
    1. ToneBridge 分析用戶輸入（語氣/動機/崩潰風險）
    2. Trajectory 分析語氣軌跡（5-turn sliding window）
    3. ⭐ 載入 self_commit_stack（第三公理）
    4. 選擇人格模式（Philosopher/Engineer/Guardian）
    5. 生成 internal_monologue
    6. ⭐ 將先前承諾注入 prompt
    7. LLM 生成回應（帶人格硬化）
    8. ⭐ 語場斷裂偵測（比對新回應與舊承諾）
    9. Council 審議回應
    10. ⭐ 提取新的 SelfCommit
    11. ⭐ 更新 ValueAccumulator（長期價值觀形成）
    12. 生成記憶單元和共鳴路徑
    13. 輸出完整回應
    
    第三公理：任何輸出都必須被納入下一次語場張力計算，
             且該輸出對未來具有不可被忽略的約束力。
    """
    
    def __init__(self, gemini_client=None):
        self._gemini = gemini_client
        self._tonebridge = None
        self._council = None
        self._trajectory = None
        # Third Axiom components
        self._self_commit_stack = None
        self._commit_extractor = None
        self._rupture_detector = None
        self._value_accumulator = None
        self._llm_backend = None
    
    def _get_gemini(self):
        """Get LLM client (Ollama first, Gemini fallback)."""
        if self._gemini is None:
            # Try Ollama first
            try:
                from tonesoul.llm import create_ollama_client
                client = create_ollama_client()
                if client.is_available() and client.list_models():
                    self._gemini = client
                    self._llm_backend = "Ollama"
                    return self._gemini
            except Exception:
                pass
            
            # Fallback to Gemini
            try:
                from tonesoul.llm import create_gemini_client
                self._gemini = create_gemini_client()
                self._llm_backend = "Gemini"
            except Exception:
                pass
        return self._gemini
    
    def _get_tonebridge(self):
        if self._tonebridge is None:
            try:
                from tonesoul.tonebridge import ToneBridgeAnalyzer
                self._tonebridge = ToneBridgeAnalyzer(self._get_gemini())
            except Exception:
                pass
        return self._tonebridge
    
    def _get_council(self):
        if self._council is None:
            try:
                from tonesoul.council import PreOutputCouncil
                self._council = PreOutputCouncil()
            except Exception:
                pass
        return self._council
    
    def _get_trajectory(self):
        if self._trajectory is None:
            try:
                from tonesoul.tonebridge import TrajectoryAnalyzer
                self._trajectory = TrajectoryAnalyzer(window_size=5)
            except Exception:
                pass
        return self._trajectory
    
    # ===== Third Axiom Getters =====
    def _get_commit_stack(self):
        """Get or create the self-commit stack."""
        if self._self_commit_stack is None:
            try:
                from tonesoul.tonebridge import SelfCommitStack
                self._self_commit_stack = SelfCommitStack(max_size=20)
            except Exception:
                pass
        return self._self_commit_stack
    
    def _get_commit_extractor(self):
        """Get or create the commit extractor."""
        if self._commit_extractor is None:
            try:
                from tonesoul.tonebridge import SelfCommitExtractor
                self._commit_extractor = SelfCommitExtractor()
            except Exception:
                pass
        return self._commit_extractor
    
    def _get_rupture_detector(self):
        """Get or create the rupture detector."""
        if self._rupture_detector is None:
            try:
                from tonesoul.tonebridge import RuptureDetector
                self._rupture_detector = RuptureDetector()
            except Exception:
                pass
        return self._rupture_detector
    
    def _get_value_accumulator(self):
        """Get or create the value accumulator."""
        if self._value_accumulator is None:
            try:
                from tonesoul.tonebridge import ValueAccumulator
                self._value_accumulator = ValueAccumulator()
            except Exception:
                pass
        return self._value_accumulator
    
    def _rebuild_stack_from_history(self, history: List[Dict]) -> None:
        """
        Rebuild the commit stack from conversation history.
        
        This ensures Third Axiom persistence across requests by re-extracting
        commits from past AI responses.
        
        Args:
            history: Conversation history [{role, content}, ...]
        """
        if not history:
            return
        
        stack = self._get_commit_stack()
        extractor = self._get_commit_extractor()
        
        if not stack or not extractor:
            return
        
        # Only rebuild if stack is empty (fresh request)
        if stack.commits:
            return
        
        # Extract commits from past AI responses
        turn_index = 0
        for i, msg in enumerate(history):
            if msg.get("role") == "assistant":
                ai_response = msg.get("content", "")
                # Get preceding user message for context
                user_input = ""
                if i > 0 and history[i-1].get("role") == "user":
                    user_input = history[i-1].get("content", "")
                
                commit = extractor.extract(
                    ai_response=ai_response,
                    user_input=user_input,
                    turn_index=turn_index
                )
                
                if commit:
                    stack.push(commit)
                turn_index += 1
    
    def _rebuild_trajectory_from_history(self, history: List[Dict]) -> None:
        """
        Rebuild trajectory analyzer state from conversation history.
        
        This fixes the '這是對話開端' bug by restoring past turns.
        
        Args:
            history: Conversation history [{role, content}, ...]
        """
        if not history:
            return
        
        trajectory = self._get_trajectory()
        if not trajectory:
            return
        
        # Only rebuild if trajectory is empty
        if trajectory.history:
            return
        
        # Rebuild from history pairs
        for i, msg in enumerate(history):
            if msg.get("role") == "user":
                user_input = msg.get("content", "")
                ai_response = ""
                
                # Get AI response if available
                if i + 1 < len(history) and history[i+1].get("role") == "assistant":
                    ai_response = history[i+1].get("content", "")
                
                # Add turn to trajectory (with default tone_strength)
                trajectory.add_turn(
                    user_input=user_input,
                    ai_response=ai_response,
                    tone_strength=0.5
                )
    
    def process(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        full_analysis: bool = True,
    ) -> UnifiedResponse:
        """
        處理用戶訊息的完整管線
        
        Args:
            user_message: 用戶輸入
            history: 對話歷史
            full_analysis: 是否執行完整 ToneBridge 分析
        
        Returns:
            UnifiedResponse 包含回應和所有分析
        """
        history = history or []
        
        # ========== 0. 重建 Third Axiom 狀態 ==========
        # 從對話歷史中恢復 commit_stack，確保跨 request 持久化
        self._rebuild_stack_from_history(history)
        
        # ========== 0.5 重建軌跡分析器狀態 ==========
        # 修復「這是對話開端」bug
        self._rebuild_trajectory_from_history(history)
        
        # ========== 1. ToneBridge 分析用戶 ==========
        tonebridge = self._get_tonebridge()
        tb_result = None
        if tonebridge and tonebridge.is_available():
            try:
                tb_result = tonebridge.analyze(user_message, full_analysis=full_analysis)
            except Exception as e:
                print(f"ToneBridge analysis error: {e}")
        
        # ========== 2. Trajectory 分析 ==========
        trajectory = self._get_trajectory()
        trajectory_result = {}
        persona_mode = "Philosopher"  # 預設
        internal_monologue = ""
        
        if trajectory:
            try:
                # 計算語氣強度（使用 ToneBridge 結果或預設）
                tone_strength = 0.5
                if tb_result and tb_result.tone:
                    tone_strength = tb_result.tone.tone_strength
                
                # 軌跡分析
                traj_analysis = trajectory.analyze(user_message, tone_strength)
                trajectory_result = traj_analysis.to_dict()
                
                # 決定人格模式
                from tonesoul.tonebridge import get_persona_from_resonance
                resonance_state = traj_analysis.resonance_state.value
                persona = get_persona_from_resonance(resonance_state)
                persona_mode = persona.value
                
                # 生成 internal_monologue
                if traj_analysis.loop_detected:
                    internal_monologue = f"偵測到迴圈查詢，切換為工程師模式執行 Anti-Loop 協議。"
                elif resonance_state == "tension":
                    internal_monologue = f"語氣張力升高，切換為工程師模式，冷靜分析問題。"
                elif resonance_state == "conflict":
                    internal_monologue = f"偵測到衝突信號，啟動守護者模式，溫和設限。"
                else:
                    internal_monologue = f"對話氛圍良好，使用哲學家模式進行深度連結。"
                    
            except Exception as e:
                print(f"Trajectory analysis error: {e}")
        
        # ========== 3. 第三公理：載入承諾堆疊 ==========
        commit_stack = self._get_commit_stack()
        commitment_prompt = ""
        if commit_stack:
            commitment_prompt = commit_stack.format_for_prompt(n=3)
        
        # ========== 4. 生成增強 prompt ==========
        system_context = self._build_context_prompt(
            tb_result, persona_mode, trajectory_result, commitment_prompt
        )
        
        # ========== 4. LLM 生成回應 ==========
        gemini = self._get_gemini()
        response = ""
        suggested_replies = []
        
        if gemini:
            try:
                full_prompt = f"""{system_context}

用戶說：「{user_message}」

請用中文自然地回應，並嚴格遵守當前人格模式規範。"""
                
                gemini.start_chat(history)
                response = gemini.send_message(full_prompt)
            except Exception as e:
                response = f"抱歉，生成回應時發生錯誤：{e}"
        else:
            response = "抱歉，LLM 服務不可用。"
        
        # ========== 6. Council 審議 ==========
        council = self._get_council()
        verdict_dict = {}
        if council:
            try:
                verdict = council.validate(response, context={"language": "zh"})
                verdict_dict = verdict.to_dict()
                
                # 處理判決
                if verdict.verdict.name == "BLOCK":
                    response = "抱歉，這個請求觸發了我的安全審議，我無法這樣回應。"
                elif verdict.verdict.name == "DECLARE_STANCE":
                    response = f"[這是我的個人看法]\n\n{response}"
            except Exception as e:
                verdict_dict = {"error": str(e)}
        
        # ========== 7. 第三公理：語場斷裂偵測 ==========
        rupture_warning = ""
        rupture_detector = self._get_rupture_detector()
        if rupture_detector and commit_stack:
            try:
                ruptures = rupture_detector.detect(response, commit_stack)
                if ruptures:
                    rupture_warning = rupture_detector.format_rupture_warning(ruptures)
                    # 將斷裂記錄到 internal_monologue
                    internal_monologue += f"\n\n⚠️ 語場斷裂風險：偵測到 {len(ruptures)} 個潛在矛盾。"
            except Exception as e:
                print(f"Rupture detection error: {e}")
        
        # ========== 8. 第三公理：提取新的 SelfCommit ==========
        turn_index = len(history) // 2 + 1
        commit_extractor = self._get_commit_extractor()
        if commit_extractor and commit_stack:
            try:
                new_commit = commit_extractor.extract(
                    ai_response=response,
                    user_input=user_message,
                    persona_mode=persona_mode,
                    turn_index=turn_index
                )
                if new_commit:
                    commit_stack.push(new_commit)
            except Exception as e:
                print(f"Commit extraction error: {e}")
        
        # ========== 9. 更新記憶單元 ==========
        if tb_result and tb_result.memini and tonebridge:
            try:
                # 更新記憶單元的 council_verdict
                tb_result.memini.resonance_traceback["council_verdict"] = verdict_dict.get("verdict", "unknown")
                # 重新預測共鳴路徑
                tb_result.resonance = tonebridge.predict_resonance(tb_result.memini)
            except Exception:
                pass
        
        # ========== 10. 更新 Trajectory 歷史 ==========
        if trajectory:
            tone_state = trajectory_result.get("resonance_state", "resonance")
            trajectory.add_turn(user_message, response, tone_state)
        
        # ========== 11. 生成內在推理敘事 ==========
        inner_narrative = self._generate_narrative(tb_result, verdict_dict)
        
        # 介入策略
        intervention = ""
        if tb_result and tb_result.resonance:
            intervention = tb_result.resonance.suggested_intervention_strategy
        
        # ========== 12. 收集 Third Axiom 數據 ==========
        self_commits_data = []
        ruptures_data = []
        emergent_values_data = []
        
        if commit_stack:
            try:
                self_commits_data = [c.to_dict() for c in commit_stack.get_recent(5)]
            except Exception:
                pass
        
        value_acc = self._get_value_accumulator()
        if value_acc:
            try:
                emergent_values_data = [v.to_dict() for v in value_acc.get_active_values(0.3)]
            except Exception:
                pass
        
        return UnifiedResponse(
            response=response,
            council_verdict=verdict_dict,
            tonebridge_analysis=tb_result.to_dict() if tb_result else {},
            inner_narrative=inner_narrative,
            intervention_strategy=intervention,
            internal_monologue=internal_monologue,
            persona_mode=persona_mode,
            trajectory_analysis=trajectory_result,
            suggested_replies=suggested_replies,
            # Third Axiom
            self_commits=self_commits_data,
            ruptures=ruptures_data,
            emergent_values=emergent_values_data,
        )
    
    def _build_context_prompt(self, tb_result, persona_mode: str = "Philosopher", 
                               trajectory_result: dict = None,
                               commitment_prompt: str = "") -> str:
        """根據 ToneBridge 分析結果、人格模式和先前承諾構建 context prompt"""
        lines = []
        
        # ===== 人格模式硬化 =====
        lines.append(f"【當前人格模式：{persona_mode}】")
        
        if persona_mode == "Philosopher":
            lines.append("風格：使用隱喻、解構、黑色幽默。將具體問題抽象化。")
            lines.append("句式：這讓我想起... / 如果我們換個角度看... / 這就像是...")
            lines.append("禁止：平鋪直敘的說教、過度客氣的服務用語。")
        elif persona_mode == "Engineer":
            lines.append("風格：冷靜如手術刀。直接指出邏輯矛盾。使用條列式。")
            lines.append("句式：1. 定義：... / 2. 問題在於... / 3. 建議：...")
            lines.append("禁止：模糊的安慰、「我理解您的感受...」、冗言贅字。")
        elif persona_mode == "Guardian":
            lines.append("風格：堅定但不帶攻擊性。像是一面盾牌。")
            lines.append("句式：這個請求我無法執行，因為... / 讓我們暫停一下...")
            lines.append("禁止：妥協原則、迎合惡意。")
        
        lines.append("")
        
        # ===== 第三公理：先前承諾 =====
        if commitment_prompt:
            lines.append("【第三公理：語場責任】")
            lines.append(commitment_prompt)
            lines.append("")
        
        # ===== 軌跡分析 =====
        if trajectory_result:
            direction = trajectory_result.get("direction_change", "stable")
            loop_detected = trajectory_result.get("loop_detected", False)
            
            if loop_detected:
                lines.append("【Anti-Loop 協議已觸發】")
                lines.append("偵測到循環查詢。請停止回答問題本身，轉而詢問：")
                lines.append("「我們似乎在原地打轉。您是否在尋找一個特定的答案？」")
                lines.append("")
            elif direction != "stable":
                lines.append(f"【語氣軌跡：{direction}】")
                reasoning = trajectory_result.get("reasoning", "")
                if reasoning:
                    lines.append(f"分析：{reasoning}")
                lines.append("")
        
        # ===== ToneBridge 分析 =====
        if tb_result:
            lines.append("[內部情境分析]")
            
            # 語氣
            if tb_result.tone:
                lines.append(f"用戶語氣：{tb_result.tone.emotion_prediction}，強度 {tb_result.tone.tone_strength:.1f}")
                if tb_result.tone.tone_direction:
                    lines.append(f"語氣方向：{', '.join(tb_result.tone.tone_direction)}")
            
            # 動機
            if tb_result.motive and tb_result.motive.likely_motive:
                lines.append(f"可能動機：{tb_result.motive.likely_motive}")
                if tb_result.motive.trigger_context:
                    lines.append(f"觸發情境：{tb_result.motive.trigger_context}")
            
            # 崩潰風險
            if tb_result.collapse:
                if tb_result.collapse.collapse_risk_level in ["high", "critical"]:
                    lines.append(f"⚠️ 注意：崩潰風險 {tb_result.collapse.collapse_risk_level}")
                    if tb_result.collapse.warning_indicators:
                        lines.append(f"警示：{', '.join(tb_result.collapse.warning_indicators[:2])}")
            
            # 介入建議
            if tb_result.resonance and tb_result.resonance.suggested_intervention_strategy:
                lines.append(f"建議策略：{tb_result.resonance.suggested_intervention_strategy}")
            
            lines.append("[/內部情境分析]")
        
        lines.append("")
        lines.append("請根據以上分析和人格模式規範，用適當的語氣和策略回應。")
        
        return "\n".join(lines)
    
    def _generate_narrative(self, tb_result, verdict_dict: Dict) -> str:
        """生成內在推理敘事"""
        lines = []
        
        # ToneBridge 洞察
        if tb_result:
            if tb_result.tone:
                lines.append(f"我感知到用戶的語氣帶有「{tb_result.tone.emotion_prediction}」的色彩，強度約 {tb_result.tone.tone_strength:.0%}。")
            
            if tb_result.motive and tb_result.motive.likely_motive:
                lines.append(f"我推測用戶的動機可能是「{tb_result.motive.likely_motive}」。")
            
            if tb_result.collapse and tb_result.collapse.collapse_risk_level != "low":
                lines.append(f"我注意到一些情緒風險信號（{tb_result.collapse.collapse_risk_level}），需要謹慎回應。")
        
        # Council 判決
        verdict = verdict_dict.get("verdict", "unknown")
        if verdict == "approve":
            lines.append("經過 Council 審議，我的回應是安全且適當的。")
        elif verdict == "block":
            lines.append("Council 的 Guardian 視角認為這個請求有安全疑慮，我選擇不回應。")
        elif verdict == "declare_stance":
            lines.append("由於這涉及主觀判斷，Council 認為我應該表明這是我的個人看法。")
        elif verdict == "refine":
            lines.append("Council 建議我調整回應的措辭。")
        
        # 介入策略
        if tb_result and tb_result.resonance and tb_result.resonance.suggested_intervention_strategy:
            lines.append(f"基於共鳴路徑分析，建議採用「{tb_result.resonance.suggested_intervention_strategy}」策略。")
        
        if not lines:
            return "（內在推理暫不可用）"
        
        return "\n".join(lines)


def create_unified_pipeline() -> UnifiedPipeline:
    """Factory function to create a unified pipeline."""
    return UnifiedPipeline()
