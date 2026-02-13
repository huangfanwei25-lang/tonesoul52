"""
ToneSoul Unified Pipeline
Combines ToneBridge psychological analysis with Council deliberation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _read_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_positive_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return max(1, int(default))
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return max(1, int(default))
    return max(1, parsed)


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
    semantic_contradictions: List[Dict[str, Any]] = field(default_factory=list)
    semantic_graph_summary: Dict[str, Any] = field(default_factory=dict)

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
            "semantic_contradictions": self.semantic_contradictions,
            "semantic_graph_summary": self.semantic_graph_summary,
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
        # ToneSoul 2.0: Internal Deliberation
        self._deliberation = None
        # Memory layer integrations
        self._semantic_graph = None
        self._visual_chain = None
        self._visual_chain_enabled = _read_bool_env("TONESOUL_VISUAL_CHAIN_ENABLED", default=True)
        self._visual_chain_sample_every = _read_positive_int_env(
            "TONESOUL_VISUAL_CHAIN_SAMPLE_EVERY", default=1
        )
        self._visual_chain_max_frames = _read_positive_int_env(
            "TONESOUL_VISUAL_CHAIN_MAX_FRAMES", default=500
        )

    def _get_gemini(self):
        """Get LLM client based on LLM_BACKEND env var.

        Supported values:
          - 'gemini'  -> Cloud mode, skip Ollama entirely
          - 'ollama'  -> Local mode, skip Gemini entirely
          - 'auto'    -> (default) Try Ollama first, Gemini fallback
        """
        if self._gemini is not None:
            return self._gemini

        import os

        llm_mode = (os.environ.get("LLM_BACKEND") or "auto").strip().lower()

        if llm_mode == "gemini":
            try:
                from tonesoul.llm import create_gemini_client

                self._gemini = create_gemini_client()
                self._llm_backend = "Gemini"
            except Exception:
                pass
            return self._gemini

        if llm_mode == "ollama":
            try:
                from tonesoul.llm import create_ollama_client

                client = create_ollama_client()
                if client.is_available() and client.list_models():
                    self._gemini = client
                    self._llm_backend = "Ollama"
            except Exception:
                pass
            return self._gemini

        # Auto mode: Ollama first, Gemini fallback
        try:
            from tonesoul.llm import create_ollama_client

            client = create_ollama_client()
            if client.is_available() and client.list_models():
                self._gemini = client
                self._llm_backend = "Ollama"
                return self._gemini
        except Exception:
            pass

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
                from tonesoul.council import CouncilRuntime

                self._council = CouncilRuntime()
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

    # ===== ToneSoul 2.0: Internal Deliberation =====
    def _get_deliberation(self):
        """Get or create the Internal Deliberation engine."""
        if self._deliberation is None:
            try:
                from tonesoul.deliberation import InternalDeliberation

                self._deliberation = InternalDeliberation()
            except Exception:
                pass
        return self._deliberation

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

    def _get_semantic_graph(self):
        """Get or create a session-level semantic graph."""
        if self._semantic_graph is None:
            try:
                from tonesoul.memory.semantic_graph import SemanticGraph

                self._semantic_graph = SemanticGraph()
            except Exception:
                pass
        return self._semantic_graph

    def _get_visual_chain(self):
        """Get or create visual chain for lightweight scene snapshots."""
        if self._visual_chain is None:
            try:
                from pathlib import Path

                from tonesoul.memory.visual_chain import VisualChain

                self._visual_chain = VisualChain(storage_path=Path("data/visual_chain.json"))
            except Exception:
                pass
        return self._visual_chain

    def _should_capture_visual_frame(self, chain: Any) -> bool:
        """Gate automatic visual capture with env-configurable controls."""
        if chain is None or not self._visual_chain_enabled:
            return False
        try:
            frame_count = int(getattr(chain, "frame_count", 0))
        except (TypeError, ValueError):
            frame_count = 0
        if frame_count >= self._visual_chain_max_frames:
            return False
        if self._visual_chain_sample_every > 1:
            next_index = frame_count + 1
            if next_index % self._visual_chain_sample_every != 0:
                return False
        return True

    @staticmethod
    def _extract_contradiction_description(contradiction: Any) -> str:
        """Normalize contradiction descriptions from object/dict variants."""
        if isinstance(contradiction, dict):
            return str(contradiction.get("description", "")).strip()
        description = str(getattr(contradiction, "description", "")).strip()
        if description:
            return description
        to_dict = getattr(contradiction, "to_dict", None)
        if callable(to_dict):
            try:
                raw = to_dict()
            except Exception:
                return ""
            if isinstance(raw, dict):
                return str(raw.get("description", "")).strip()
        return ""

    def _inject_persona_memory(
        self, user_message: str, persona_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Inject persona-oriented preference memory into the prompt input."""
        if not persona_config:
            return user_message
        persona_parts: List[str] = []
        if persona_config.get("style"):
            persona_parts.append(f"回應風格: {persona_config['style']}")
        weights = persona_config.get("weights", {})
        if weights:
            persona_parts.append(f"意義探索權重: {weights.get('meaning', 50)}%")
            persona_parts.append(f"實用導向權重: {weights.get('practical', 50)}%")
            persona_parts.append(f"安全考量權重: {weights.get('safety', 50)}%")
        if persona_config.get("risk_sensitivity"):
            persona_parts.append(f"風險敏感度: {persona_config['risk_sensitivity']}")
        if persona_config.get("response_length"):
            persona_parts.append(f"回應長度: {persona_config['response_length']}")
        if not persona_parts:
            return user_message
        persona_context = " | ".join(persona_parts)
        return f"[用戶偏好: {persona_context}]\n\n{user_message}"

    def _inject_visual_context(self, user_message: str) -> str:
        """Inject recent visual chain snapshots into the message context."""
        try:
            chain = self._get_visual_chain()
            if chain and chain.frame_count > 0:
                visual_context = chain.render_recent_as_markdown(n=3)
                if visual_context and len(visual_context) > 50:
                    return (
                        f"[脈絡記憶 — 最近視覺快照]\n{visual_context}\n\n" f"---\n\n{user_message}"
                    )
        except Exception:
            pass
        return user_message

    def _inject_early_contradiction_warning(self, user_message: str) -> str:
        """Inject contradiction hints before prompt generation."""
        try:
            graph = self._get_semantic_graph()
            if not graph:
                return user_message
            pre_contradictions = graph.detect_contradictions()
        except Exception:
            return user_message

        if not pre_contradictions:
            return user_message

        hints: List[str] = []
        for contradiction in pre_contradictions[:3]:
            description = self._extract_contradiction_description(contradiction)
            if description:
                hints.append(description[:60])
        contradiction_hints = "; ".join(hints) or "請檢查近期承諾與邊界的一致性"
        return (
            f"[內在一致性提醒: 偵測到 {len(pre_contradictions)} 個潛在矛盾 — "
            f"{contradiction_hints}]\n\n{user_message}"
        )

    def build_injection_context(
        self, user_message: str, persona_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build injection context from one canonical source without data duplication.

        The adapter splits views into:
        - persona slice: stable user preference memory
        - context slice: recent visual memory chain
        """
        injected = self._inject_persona_memory(user_message, persona_config)
        injected = self._inject_visual_context(injected)
        return injected

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
                if i > 0 and history[i - 1].get("role") == "user":
                    user_input = history[i - 1].get("content", "")

                commit = extractor.extract(
                    ai_response=ai_response, user_input=user_input, turn_index=turn_index
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
                if i + 1 < len(history) and history[i + 1].get("role") == "assistant":
                    ai_response = history[i + 1].get("content", "")

                # Add turn to trajectory (with default tone_strength)
                trajectory.add_turn(
                    user_input=user_input, ai_response=ai_response, tone_strength=0.5
                )

    def process(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        full_analysis: bool = True,
        council_mode: Optional[str] = None,
        perspective_config: Optional[Dict[str, Dict[str, Any]]] = None,
        prior_tension: Optional[Dict[str, Any]] = None,
        persona_config: Optional[Dict[str, Any]] = None,
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

        # ========== 記憶注入 Adapter（persona + context） ==========
        user_message = self.build_injection_context(user_message, persona_config=persona_config)

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
        tone_strength = 0.5
        resonance_state = "resonance"
        loop_detected = False

        if trajectory:
            try:
                # 計算語氣強度（使用 ToneBridge 結果或預設）
                if tb_result and tb_result.tone:
                    tone_strength = tb_result.tone.tone_strength

                # 軌跡分析
                traj_analysis = trajectory.analyze(user_message, tone_strength)
                trajectory_result = traj_analysis.to_dict()
                resonance_state = traj_analysis.resonance_state.value
                loop_detected = traj_analysis.loop_detected

            except Exception as e:
                print(f"Trajectory analysis error: {e}")

        # ========== 2.5 ToneSoul 2.0: 內在審議 ==========
        deliberation = self._get_deliberation()
        deliberation_result = None
        persona_mode = "Philosopher"  # 預設
        internal_monologue = ""

        if deliberation:
            try:
                from tonesoul.deliberation import DeliberationContext

                context = DeliberationContext(
                    user_input=user_message,
                    conversation_history=history,
                    tone_strength=tone_strength,
                    resonance_state=resonance_state,
                    loop_detected=loop_detected,
                )
                deliberation_result = deliberation.deliberate_sync(context)

                # 從審議結果獲取 persona 和 monologue
                if deliberation_result.dominant_voice:
                    voice_map = {"muse": "Philosopher", "logos": "Engineer", "aegis": "Guardian"}
                    persona_mode = voice_map.get(
                        deliberation_result.dominant_voice.value, "Philosopher"
                    )

                # 生成 internal monologue 從審議
                internal_debate = deliberation_result.get_internal_debate()
                if internal_debate:
                    dominant = (
                        deliberation_result.dominant_voice.value
                        if deliberation_result.dominant_voice
                        else "muse"
                    )
                    if dominant in internal_debate:
                        internal_monologue = internal_debate[dominant].get("reasoning", "")

            except Exception as e:
                print(f"Deliberation error: {e}")
                # Fallback to old persona logic
                from tonesoul.tonebridge import get_persona_from_resonance

                persona = get_persona_from_resonance(resonance_state)
                persona_mode = persona.value
                internal_monologue = "使用舊版人格選擇邏輯。"

        # ========== 3. 第三公理：載入承諾堆疊 ==========
        commit_stack = self._get_commit_stack()
        commitment_prompt = ""
        detected_ruptures: List[Any] = []
        new_commit = None
        semantic_topics: List[str] = []
        semantic_contradictions: List[Dict[str, Any]] = []
        semantic_graph_summary: Dict[str, Any] = {}
        if commit_stack:
            commitment_prompt = commit_stack.format_for_prompt(n=3)

        # ========== 3.5 回應前矛盾檢查 ==========
        user_message = self._inject_early_contradiction_warning(user_message)

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
                from tonesoul.council import CouncilRequest
                from tonesoul.council.model_registry import get_council_config

                resolved_perspective_config = perspective_config
                if resolved_perspective_config is None and council_mode:
                    resolved_perspective_config = get_council_config(council_mode)
                council_context = {"language": "zh"}
                if isinstance(prior_tension, dict) and prior_tension:
                    council_context["prior_tension"] = prior_tension
                if council_mode:
                    council_context["council_mode_override"] = council_mode

                request = CouncilRequest(
                    draft_output=response,
                    context=council_context,
                    perspective_config=resolved_perspective_config,
                )
                verdict = council.deliberate(request)
                verdict_dict = verdict.to_dict()

                # 處理判決
                if verdict.verdict.name == "BLOCK":
                    response = "抱歉，這個請求觸發了我的安全審議，我無法這樣回應。"
                elif verdict.verdict.name == "DECLARE_STANCE":
                    response = f"[這是我的個人看法]\n\n{response}"
            except Exception as e:
                verdict_dict = {"error": str(e)}

        # ========== 7. 第三公理：語場斷裂偵測 ==========
        rupture_detector = self._get_rupture_detector()
        if rupture_detector and commit_stack:
            try:
                detected_ruptures = rupture_detector.detect(response, commit_stack)
                if detected_ruptures:
                    rupture_detector.format_rupture_warning(detected_ruptures)
                    # 將斷裂記錄到 internal_monologue
                    internal_monologue += (
                        f"\n\n⚠️ 語場斷裂風險：偵測到 {len(detected_ruptures)} 個潛在矛盾。"
                    )
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
                    turn_index=turn_index,
                )
                if new_commit:
                    commit_stack.push(new_commit)
            except Exception as e:
                print(f"Commit extraction error: {e}")

        # ========== 9. 語義圖譜更新 ==========
        graph = self._get_semantic_graph()
        if graph:
            try:
                if new_commit:
                    graph.extract_from_commitment(
                        {
                            "content": getattr(new_commit, "content", ""),
                            "type": getattr(
                                getattr(new_commit, "assertion_type", None),
                                "value",
                                "commitment",
                            ),
                            "turn_index": turn_index,
                        }
                    )

                if tb_result:
                    if tb_result.motive and tb_result.motive.likely_motive:
                        semantic_topics.append(tb_result.motive.likely_motive)
                    if tb_result.motive and tb_result.motive.resonance_chain_hint:
                        semantic_topics.extend(tb_result.motive.resonance_chain_hint)
                    if tb_result.tone and tb_result.tone.trigger_keywords:
                        semantic_topics.extend(tb_result.tone.trigger_keywords)

                semantic_topics = [
                    str(topic).strip() for topic in semantic_topics if str(topic).strip()
                ]
                if response:
                    graph.extract_from_response(response, semantic_topics)
                graph.increment_turn()
                semantic_contradictions = [c.to_dict() for c in graph.detect_contradictions()]
                semantic_graph_summary = graph.get_summary()
            except Exception as e:
                print(f"Semantic graph error: {e}")

        # ========== 10. 更新記憶單元 ==========
        if tb_result and tb_result.memini and tonebridge:
            try:
                # 更新記憶單元的 council_verdict
                tb_result.memini.resonance_traceback["council_verdict"] = verdict_dict.get(
                    "verdict", "unknown"
                )
                # 重新預測共鳴路徑
                tb_result.resonance = tonebridge.predict_resonance(tb_result.memini)
            except Exception:
                pass

        # ========== 11. 更新 Trajectory 歷史 ==========
        if trajectory:
            tone_state = trajectory_result.get("resonance_state", "resonance")
            trajectory.add_turn(user_message, response, tone_state)

        # ========== 12. 生成內在推理敘事 ==========
        inner_narrative = self._generate_narrative(tb_result, verdict_dict)

        # 介入策略
        intervention = ""
        if tb_result and tb_result.resonance:
            intervention = tb_result.resonance.suggested_intervention_strategy

        # ========== 13. 收集 Third Axiom 數據 ==========
        self_commits_data = []
        ruptures_data = []
        emergent_values_data = []

        if commit_stack:
            try:
                self_commits_data = [c.to_dict() for c in commit_stack.get_recent(5)]
            except Exception:
                pass
        if detected_ruptures:
            try:
                ruptures_data = [r.to_dict() for r in detected_ruptures]
            except Exception:
                ruptures_data = [{"summary": str(r)} for r in detected_ruptures]

        value_acc = self._get_value_accumulator()
        if value_acc:
            try:
                emergent_values_data = [v.to_dict() for v in value_acc.get_active_values(0.3)]
            except Exception:
                pass

        # 將語義矛盾資訊放入 verdict metadata，避免破壞既有回傳結構
        if isinstance(verdict_dict, dict):
            verdict_metadata = verdict_dict.get("metadata")
            if not isinstance(verdict_metadata, dict):
                verdict_metadata = {}
            verdict_metadata["semantic_contradictions"] = semantic_contradictions
            if semantic_graph_summary:
                verdict_metadata["semantic_graph"] = semantic_graph_summary
            verdict_dict["metadata"] = verdict_metadata

        # 自動拍攝 visual chain frame，不影響主流程
        chain = self._get_visual_chain()
        if self._should_capture_visual_frame(chain):
            try:
                from tonesoul.memory.visual_chain import FrameType

                tension_score = (
                    float(tb_result.tone.tone_strength) if tb_result and tb_result.tone else 0.0
                )
                frame_tags = ["auto"]
                if tension_score >= 0.7:
                    frame_tags.append("high_tension")
                if semantic_contradictions:
                    frame_tags.append("contradiction")
                verdict_name = (
                    str(verdict_dict.get("verdict", "unknown"))
                    if isinstance(verdict_dict, dict)
                    else "unknown"
                )
                chain.capture(
                    frame_type=FrameType.SESSION_STATE,
                    title=f"Turn {chain.frame_count}",
                    data={
                        "tension": tension_score,
                        "verdict": verdict_name,
                        "council_mode": council_mode or "hybrid",
                        "topics": semantic_topics,
                        "commitments_active": len(self_commits_data),
                        "ruptures": len(ruptures_data),
                        "values_count": len(emergent_values_data),
                    },
                    tags=frame_tags,
                    branch="main",
                )
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
            semantic_contradictions=semantic_contradictions,
            semantic_graph_summary=semantic_graph_summary,
        )

    def _build_context_prompt(
        self,
        tb_result,
        persona_mode: str = "Philosopher",
        trajectory_result: dict = None,
        commitment_prompt: str = "",
    ) -> str:
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
                lines.append(
                    f"用戶語氣：{tb_result.tone.emotion_prediction}，強度 {tb_result.tone.tone_strength:.1f}"
                )
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
                        lines.append(
                            f"警示：{', '.join(tb_result.collapse.warning_indicators[:2])}"
                        )

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
                lines.append(
                    f"我感知到用戶的語氣帶有「{tb_result.tone.emotion_prediction}」的色彩，強度約 {tb_result.tone.tone_strength:.0%}。"
                )

            if tb_result.motive and tb_result.motive.likely_motive:
                lines.append(f"我推測用戶的動機可能是「{tb_result.motive.likely_motive}」。")

            if tb_result.collapse and tb_result.collapse.collapse_risk_level != "low":
                lines.append(
                    f"我注意到一些情緒風險信號（{tb_result.collapse.collapse_risk_level}），需要謹慎回應。"
                )

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
        if (
            tb_result
            and tb_result.resonance
            and tb_result.resonance.suggested_intervention_strategy
        ):
            lines.append(
                f"基於共鳴路徑分析，建議採用「{tb_result.resonance.suggested_intervention_strategy}」策略。"
            )

        if not lines:
            return "（內在推理暫不可用）"

        return "\n".join(lines)


def create_unified_pipeline() -> UnifiedPipeline:
    """Factory function to create a unified pipeline."""
    return UnifiedPipeline()
