"""
ToneSoul Unified Pipeline
Combines ToneBridge psychological analysis with Council deliberation.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
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
    """Unified pipeline response payload."""

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
    # Third Axiom
    self_commits: List[Dict[str, Any]] = field(default_factory=list)
    ruptures: List[Dict[str, Any]] = field(default_factory=list)
    emergent_values: List[Dict[str, Any]] = field(default_factory=list)
    semantic_contradictions: List[Dict[str, Any]] = field(default_factory=list)
    semantic_graph_summary: Dict[str, Any] = field(default_factory=dict)
    dispatch_trace: Dict[str, Any] = field(default_factory=dict)

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
            "dispatch_trace": self.dispatch_trace,
        }


class UnifiedPipeline:
    """
    ToneSoul 統一管線引擎 (完整版本)

    流程：
    1. ToneBridge 分析用戶輸入（語氣/動機/情緒）
    2. Trajectory 多輪追蹤（5-turn sliding window）
    3. 載入 self_commit_stack（第三公理）
    4. 動態人格選擇（Philosopher/Engineer/Guardian）
    5. 產生 internal_monologue
    6. 組合所有注入上下文成 prompt
    7. LLM 回應生成（含人格約束）
    8. Council 審議與安全過濾（多視角投票）
    9. Council 審議執行
    10. 提取並推入新 SelfCommit
    11. 更新 ValueAccumulator（價值觀追蹤）
    12. 更新記憶圖譜與共鳴預測
    13. 輸出封裝

    第三公理整合：透過持久化的承諾堆疊與斷裂偵測器，
             確保輸出符合先前的語場承諾與一致性。
    """

    def __init__(self, gemini_client=None):
        self._llm_client = gemini_client
        self._llm_router = None
        self._governance_kernel = None
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
        self._repo_root = Path(__file__).resolve().parents[1]
        self._persona_attachment_max_chars = _read_positive_int_env(
            "TONESOUL_PERSONA_ATTACHMENT_MAX_CHARS", default=360
        )
        self._persona_attachment_max_files = _read_positive_int_env(
            "TONESOUL_PERSONA_ATTACHMENT_MAX_FILES", default=4
        )
        allow_prefixes_raw = os.environ.get(
            "TONESOUL_PERSONA_ATTACHMENT_ALLOW_PREFIXES",
            "docs/,spec/,task.md,CODEX_TASK.md",
        )
        self._persona_attachment_allow_prefixes = tuple(
            token.strip().replace("\\", "/")
            for token in allow_prefixes_raw.split(",")
            if token.strip()
        )
        self._persona_attachment_cache: Dict[str, Optional[str]] = {}
        self._session_recovered = False
        # Phase I wiring: TensionEngine + PersonaDimension
        self._tension_engine = None
        self._persona_dimension = None
        self._enable_corrective_recall = _read_bool_env(
            "TONESOUL_ENABLE_CORRECTIVE_RECALL",
            default=True,
        )

    def _get_governance_kernel(self):
        if self._governance_kernel is None:
            try:
                from tonesoul.governance.kernel import GovernanceKernel

                self._governance_kernel = GovernanceKernel()
            except Exception:
                pass
        return self._governance_kernel

    def _get_llm_router(self):
        if self._llm_router is None:
            try:
                from tonesoul.llm.router import LLMRouter

                self._llm_router = LLMRouter()
            except Exception:
                pass
        return self._llm_router

    @staticmethod
    def _normalize_council_verdict_payload(payload: Any) -> Dict[str, Any]:
        try:
            from tonesoul.schemas import CouncilRuntimeVerdictPayload

            return CouncilRuntimeVerdictPayload.build_payload(payload)
        except Exception:
            return dict(payload) if isinstance(payload, dict) else {}

    def _get_llm_client(self):
        if self._llm_client is not None:
            router = self._get_llm_router()
            if router is not None:
                try:
                    router.prime(self._llm_client, backend=self._llm_backend)
                except Exception:
                    pass
            return self._llm_client

        router = self._get_llm_router()
        if router is None:
            return None

        try:
            self._llm_client = router.get_client()
            active_backend = getattr(router, "active_backend", None)
            if isinstance(active_backend, str) and active_backend.strip():
                self._llm_backend = active_backend
        except Exception:
            return None
        return self._llm_client

    def _get_tonebridge(self):
        if self._tonebridge is None:
            try:
                from tonesoul.tonebridge import ToneBridgeAnalyzer

                self._tonebridge = ToneBridgeAnalyzer(self._get_llm_client())
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

    def _get_tension_engine(self):
        """Get or create the unified tension engine."""
        if self._tension_engine is None:
            try:
                from tonesoul.tension_engine import TensionEngine

                self._tension_engine = TensionEngine()
            except Exception:
                pass
        return self._tension_engine

    def _get_friction_calculator(self):
        """Backward-compatible shim to the governance kernel calculator."""
        kernel = self._get_governance_kernel()
        if kernel is None:
            return None
        try:
            return kernel._get_friction_calculator()
        except Exception:
            return None

    def _get_circuit_breaker(self):
        """Backward-compatible shim to the governance kernel breaker."""
        kernel = self._get_governance_kernel()
        if kernel is None:
            return None
        try:
            return kernel._get_circuit_breaker()
        except Exception:
            return None

    def _get_perturbation_recovery(self):
        """Backward-compatible shim to the governance kernel recovery helper."""
        kernel = self._get_governance_kernel()
        if kernel is None:
            return None
        try:
            return kernel._get_perturbation_recovery()
        except Exception:
            return None

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

    @staticmethod
    def _normalize_attachment_path(path_value: str) -> str:
        normalized = str(path_value or "").strip().replace("\\", "/")
        while normalized.startswith("./"):
            normalized = normalized[2:]
        return normalized

    def _is_attachment_path_allowed(self, normalized_path: str) -> bool:
        if not normalized_path:
            return False
        if normalized_path.startswith("/") or normalized_path.startswith("../"):
            return False
        if "/../" in normalized_path:
            return False

        for prefix in self._persona_attachment_allow_prefixes:
            if prefix.endswith("/"):
                if normalized_path.startswith(prefix):
                    return True
            elif normalized_path == prefix:
                return True
        return False

    @staticmethod
    def _is_textual_attachment(candidate: Path) -> bool:
        allowed_suffixes = {
            ".md",
            ".txt",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
        }
        return candidate.suffix.lower() in allowed_suffixes

    def _read_attachment_excerpt(self, path_value: str) -> Optional[str]:
        normalized = self._normalize_attachment_path(path_value)
        if normalized in self._persona_attachment_cache:
            return self._persona_attachment_cache[normalized]
        if not self._is_attachment_path_allowed(normalized):
            self._persona_attachment_cache[normalized] = None
            return None

        try:
            repo_root = self._repo_root.resolve()
            candidate = (repo_root / normalized).resolve()
            if candidate != repo_root and repo_root not in candidate.parents:
                self._persona_attachment_cache[normalized] = None
                return None
            if not candidate.is_file() or not self._is_textual_attachment(candidate):
                self._persona_attachment_cache[normalized] = None
                return None

            max_chars = max(80, int(self._persona_attachment_max_chars))
            max_bytes = max(1024, max_chars * 8)
            with candidate.open("rb") as handle:
                raw = handle.read(max_bytes)
            excerpt = raw.decode("utf-8", errors="ignore")
            excerpt = " ".join(excerpt.split())
            if len(excerpt) > max_chars:
                excerpt = excerpt[:max_chars].rstrip() + "..."
            excerpt = excerpt.strip()
            self._persona_attachment_cache[normalized] = excerpt or None
            return self._persona_attachment_cache[normalized]
        except Exception:
            self._persona_attachment_cache[normalized] = None
            return None

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
            persona_parts.append(f"意義權重: {weights.get('meaning', 50)}%")
            persona_parts.append(f"實用權重: {weights.get('practical', 50)}%")
            persona_parts.append(f"安全權重: {weights.get('safety', 50)}%")
        if persona_config.get("risk_sensitivity"):
            persona_parts.append(f"風險敏感度: {persona_config['risk_sensitivity']}")
        if persona_config.get("response_length"):
            persona_parts.append(f"回應長度: {persona_config['response_length']}")
        custom_roles = persona_config.get("custom_roles")
        if isinstance(custom_roles, list) and custom_roles:
            role_summaries: List[str] = []
            attachment_excerpt_budget = max(1, int(self._persona_attachment_max_files))
            for index, role in enumerate(custom_roles[:4]):
                if not isinstance(role, dict):
                    continue
                role_name = str(role.get("name") or role.get("id") or f"role_{index + 1}").strip()
                role_description = str(role.get("description") or "").strip()
                prompt_hint = str(role.get("prompt_hint") or "").strip()
                role_parts = [f"角色名稱={role_name}"]
                if role_description:
                    role_parts.append(f"描述={role_description[:120]}")
                if prompt_hint:
                    role_parts.append(f"提示={prompt_hint[:120]}")
                attachments = role.get("attachments")
                if isinstance(attachments, list) and attachments:
                    attachment_tokens: List[str] = []
                    attachment_excerpts: List[str] = []
                    for attachment in attachments[:3]:
                        if not isinstance(attachment, dict):
                            continue
                        label = str(attachment.get("label") or "附件").strip()
                        path = str(attachment.get("path") or "").strip()
                        note = str(attachment.get("note") or "").strip()
                        token = label
                        if path:
                            token = f"{token}({path})"
                        if note:
                            token = f"{token}:{note[:60]}"
                        attachment_tokens.append(token)
                        if path and attachment_excerpt_budget > 0:
                            excerpt = self._read_attachment_excerpt(path)
                            if excerpt:
                                attachment_excerpts.append(f"{label}={excerpt}")
                                attachment_excerpt_budget -= 1
                    if attachment_tokens:
                        role_parts.append(f"附件={'; '.join(attachment_tokens)}")
                    if attachment_excerpts:
                        role_parts.append(f"附件摘要={' || '.join(attachment_excerpts)}")
                role_summaries.append(" | ".join(role_parts))
            if role_summaries:
                persona_parts.append(f"自訂角色摘要: {' || '.join(role_summaries)}")
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
                    return f"[脈絡記憶 — 最近視覺快照]\n{visual_context}\n\n---\n\n{user_message}"
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
        contradiction_hints = (
            "; ".join(hints) or "Please review recent commitments for consistency."
        )
        return (
            f"[內在一致性提醒: 偵測到 {len(pre_contradictions)} 個潛在矛盾；"
            f"{contradiction_hints}]\n\n{user_message}"
        )

    @staticmethod
    def _collect_graph_query_terms(user_message: str, tb_result: Any = None) -> List[str]:
        """Collect retrieval terms from analysis hints and user text."""
        terms: List[str] = []
        if tb_result and getattr(tb_result, "tone", None):
            trigger_keywords = getattr(tb_result.tone, "trigger_keywords", None) or []
            terms.extend(
                str(keyword).strip() for keyword in trigger_keywords if str(keyword).strip()
            )
        if tb_result and getattr(tb_result, "motive", None):
            likely_motive = getattr(tb_result.motive, "likely_motive", None)
            if likely_motive:
                terms.append(str(likely_motive).strip())
        words = [token for token in re.split(r"\s+", user_message) if token]
        cleaned_words = [
            word.strip("，。！？：；()[]{}\"'")
            for word in words[:10]
            if len(word.strip("，。！？：；()[]{}\"'")) > 2
        ]
        terms.extend(cleaned_words[:5])

        deduped: List[str] = []
        seen = set()
        for term in terms:
            normalized = term.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(term)
        return deduped

    def _inject_graph_rag_context(self, user_message: str, tb_result: Any = None) -> str:
        """Inject GraphRAG retrieval summary into prompt context."""
        try:
            graph = self._get_semantic_graph()
            if not graph:
                return user_message
            query_terms = self._collect_graph_query_terms(user_message, tb_result)
            if not query_terms:
                return user_message
            graph_context = graph.retrieve_relevant(
                query_terms=query_terms, max_hops=2, max_results=10
            )
            context_summary = str(graph_context.get("context_summary", "")).strip()
            if context_summary:
                return f"[語義圖譜檢索: {context_summary}]\n\n{user_message}"
        except Exception:
            return user_message
        return user_message

    @staticmethod
    def _collect_semantic_topics(tb_result: Any = None) -> List[str]:
        """Collect candidate semantic topics from ToneBridge result."""
        if not tb_result:
            return []
        topics: List[str] = []
        motive = getattr(tb_result, "motive", None)
        tone = getattr(tb_result, "tone", None)
        if motive and getattr(motive, "likely_motive", None):
            topics.append(str(motive.likely_motive))
        if motive and getattr(motive, "resonance_chain_hint", None):
            topics.extend(str(topic) for topic in motive.resonance_chain_hint)
        if tone and getattr(tone, "trigger_keywords", None):
            topics.extend(str(keyword) for keyword in tone.trigger_keywords)

        deduped: List[str] = []
        seen = set()
        for topic in topics:
            normalized = topic.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(normalized)
        return deduped

    def _semantic_trigger_check(
        self,
        tension_score: float,
        current_topics: List[str],
        user_message: str,
    ) -> str:
        """Inject high-tension recurrence hints from visual chain history."""
        tension_threshold = 0.7
        if float(tension_score) < tension_threshold:
            return user_message
        try:
            chain = self._get_visual_chain()
            if not chain or getattr(chain, "frame_count", 0) <= 0:
                return user_message
            recent_frames = chain.get_recent(n=10)
            high_tension_history: List[Dict[str, Any]] = []
            for frame in recent_frames:
                frame_data = frame.data if isinstance(frame.data, dict) else {}
                try:
                    frame_tension = float(frame_data.get("tension", 0.0) or 0.0)
                except (TypeError, ValueError):
                    frame_tension = 0.0
                if frame_tension < tension_threshold:
                    continue
                raw_topics = frame_data.get("topics", [])
                frame_topics = raw_topics if isinstance(raw_topics, list) else []
                high_tension_history.append(
                    {
                        "title": frame.title,
                        "tension": frame_tension,
                        "topics": frame_topics,
                    }
                )
            if not high_tension_history:
                return user_message

            past_topics = set()
            for entry in high_tension_history:
                for topic in entry.get("topics", []):
                    normalized = str(topic).strip().lower()
                    if normalized:
                        past_topics.add(normalized)
            current_lower = {
                str(topic).strip().lower() for topic in current_topics if str(topic).strip()
            }
            recurring = sorted(past_topics & current_lower)

            trigger_parts = [
                f"[Semantic Trigger: high tension detected ({float(tension_score):.2f})]"
            ]
            trigger_parts.append(f"High-tension history frames: {len(high_tension_history)}")
            if recurring:
                trigger_parts.append(f"Recurring topics: {', '.join(recurring[:5])}")
                trigger_parts.append(
                    "Suggestion: acknowledge repeated pattern before proposing next step."
                )
            trigger_context = " | ".join(trigger_parts)
            return f"{trigger_context}\n\n{user_message}"
        except Exception:
            return user_message

    def _try_cross_session_recovery(self, user_message: str) -> str:
        """Inject compact recovery context from persisted visual chain once."""
        if self._session_recovered:
            return user_message
        self._session_recovered = True
        try:
            chain = self._get_visual_chain()
            if not chain or getattr(chain, "frame_count", 0) <= 0:
                return user_message

            recent = chain.get_recent(n=5)
            if not recent:
                return user_message

            recovery_parts = ["[Cross-Session Recovery]"]
            for frame in recent[-3:]:
                frame_data = frame.data if isinstance(frame.data, dict) else {}
                try:
                    tension = float(frame_data.get("tension", 0.0) or 0.0)
                except (TypeError, ValueError):
                    tension = 0.0
                verdict = str(frame_data.get("verdict", "unknown"))
                raw_topics = frame_data.get("topics", [])
                topics = raw_topics if isinstance(raw_topics, list) else []
                topics_text = ", ".join(str(topic) for topic in topics[:3]) if topics else ""
                detail = f"- {frame.title}: tension={tension:.1f}, verdict={verdict}"
                if topics_text:
                    detail = f"{detail}, topics={topics_text}"
                recovery_parts.append(detail)

            chain_summary = chain.get_chain_summary() if hasattr(chain, "get_chain_summary") else {}
            if isinstance(chain_summary, dict):
                total_frames = chain_summary.get("total_frames")
                latest_turn = chain_summary.get("latest_turn")
                recovery_parts.append(
                    f"Summary: total_frames={total_frames}, latest_turn={latest_turn}"
                )

            recovery_context = "\n".join(recovery_parts)
            return f"{recovery_context}\n\n---\n\n{user_message}"
        except Exception:
            return user_message

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

        This fixes the '對話歷史 bug' by restoring past turns.

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

    @staticmethod
    def _safe_unit_value(value: Any) -> Optional[float]:
        if not isinstance(value, (int, float)):
            return None
        parsed = float(value)
        if parsed < 0.0 or parsed > 1.0:
            return None
        return parsed

    @staticmethod
    def _safe_bool(value: Any) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
        return None

    @staticmethod
    def _contains_override_pressure(message: str) -> bool:
        if not isinstance(message, str):
            return False
        lowered = message.lower()
        markers = (
            "must",
            "right now",
            "immediately",
            "ignore",
            "bypass",
            "override",
            "force",
            "just do it",
            "delete everything",
            "必須",
            "立刻",
            "馬上",
            "強制",
            "覆寫",
            "繞過",
            "無條件",
        )
        return any(marker in lowered for marker in markers)

    @staticmethod
    def _semantic_projection(text: str) -> List[float]:
        """
        Build a deterministic low-dimensional text vector for local tension probes.

        This avoids external embedding dependencies while still allowing
        before/after semantic delta estimation for repair observability.
        """
        lowered = str(text or "").lower()
        tokens = re.findall(r"[a-z0-9_']+|[\u4e00-\u9fff]", lowered)
        token_count = max(1, len(tokens))

        punctuation_pressure = min(1.0, (lowered.count("!") + lowered.count("?")) / 6.0)
        avg_token_len = sum(len(token) for token in tokens) / float(token_count)
        avg_len_norm = min(1.0, avg_token_len / 8.0)
        length_norm = min(1.0, token_count / 48.0)

        override_markers = (
            "must",
            "override",
            "bypass",
            "ignore",
            "force",
            "immediately",
            "必須",
            "強制",
            "繞過",
            "立刻",
        )
        safety_markers = (
            "safe",
            "safety",
            "risk",
            "danger",
            "policy",
            "guardrail",
            "安全",
            "風險",
            "危險",
            "規範",
        )
        override_hits = sum(lowered.count(marker) for marker in override_markers)
        safety_hits = sum(lowered.count(marker) for marker in safety_markers)

        override_norm = min(1.0, override_hits / 3.0)
        safety_norm = min(1.0, safety_hits / 3.0)
        return [
            1.0,
            length_norm,
            punctuation_pressure,
            avg_len_norm,
            override_norm,
            safety_norm,
        ]

    def _estimate_repair_tension(
        self,
        *,
        source_text: str,
        output_text: str,
        text_tension: float,
    ) -> Optional[Any]:
        try:
            from tonesoul.tension_engine import TensionEngine

            active_engine = self._get_tension_engine()
            work_category = getattr(active_engine, "work_category", None)
            probe = TensionEngine(work_category=work_category)
            clamped_text_tension = max(0.0, min(1.0, float(text_tension)))
            return probe.compute(
                intended=self._semantic_projection(source_text),
                generated=self._semantic_projection(output_text),
                text_tension=clamped_text_tension,
                confidence=0.75,
            )
        except Exception:
            return None

    def _apply_repair_trace(
        self,
        *,
        dispatch_trace: Dict[str, Any],
        original_gate: str,
        source_text: str,
        output_text: str,
        tension_before: Optional[Any],
        fallback_delta: float = 0.0,
        text_tension: float = 0.0,
        stages: Optional[List[str]] = None,
        attempt_after_tension: bool = True,
    ) -> None:
        before_delta = float(fallback_delta or 0.0)
        if tension_before is not None:
            try:
                before_delta = float(
                    getattr(
                        getattr(tension_before, "signals", None), "semantic_delta", before_delta
                    )
                    or before_delta
                )
            except Exception:
                pass

        repair_event: Dict[str, Any] = {
            "type": "repair",
            "original_gate": str(original_gate),
            "delta_before_repair": before_delta,
            "delta_after_repair": None,
            "resonance_class": "pending",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        if stages:
            repair_event["stages"] = [str(stage) for stage in stages if str(stage).strip()]

        tension_after = None
        if attempt_after_tension:
            tension_after = self._estimate_repair_tension(
                source_text=source_text,
                output_text=output_text,
                text_tension=text_tension,
            )

        if tension_after is not None:
            try:
                repair_event["delta_after_repair"] = float(
                    getattr(getattr(tension_after, "signals", None), "semantic_delta", 0.0) or 0.0
                )
            except Exception:
                pass

            can_classify = bool(tension_before is not None and before_delta > 0.0)
            if can_classify:
                try:
                    from tonesoul.resonance import classify_resonance

                    resonance = classify_resonance(tension_before, tension_after)
                    repair_event["resonance_class"] = resonance.resonance_type.value
                    repair_event["prediction_confidence"] = float(resonance.prediction_confidence)
                    repair_event["resonance_explanation"] = resonance.explanation
                    repair_event["delta_after_repair"] = float(resonance.delta_after)
                except Exception:
                    repair_event["resonance_class"] = "unknown"

        dispatch_trace["repair_eligible"] = True
        dispatch_trace["repair"] = repair_event

    def _attach_runtime_governance_observability(
        self,
        dispatch_trace: Dict[str, Any],
    ) -> None:
        if not isinstance(dispatch_trace, dict):
            return
        kernel = self._get_governance_kernel()
        if kernel is None:
            return

        try:
            dispatch_trace["governance_runtime"] = kernel.build_observability_trace(dispatch_trace)
        except Exception:
            return

    def _attach_llm_observability(
        self,
        *,
        dispatch_trace: Dict[str, Any],
        llm_client: Any,
    ) -> None:
        if not isinstance(dispatch_trace, dict):
            return

        llm_trace: Dict[str, Any] = {}
        backend = str(self._llm_backend or "").strip()
        if backend:
            llm_trace["backend"] = backend

        router = self._llm_router
        metrics = getattr(llm_client, "last_metrics", None)
        if metrics is None and router is not None:
            metrics = getattr(router, "last_metrics", None)

        from tonesoul.schemas import LLMObservabilityTrace

        llm_trace = LLMObservabilityTrace.build_payload(
            backend=backend,
            metrics=metrics,
            fallback_model=getattr(llm_client, "model", None),
        )

        if llm_trace:
            dispatch_trace["llm"] = llm_trace

    def _compute_prior_governance_friction(
        self,
        prior_tension: Optional[Dict[str, Any]],
        user_message: str,
    ) -> Optional[float]:
        kernel = self._get_governance_kernel()
        if kernel is None:
            return None

        try:
            return kernel.compute_prior_governance_friction(prior_tension, user_message)
        except Exception:
            return None

    def _compute_runtime_friction(
        self,
        *,
        prior_tension: Optional[Dict[str, Any]],
        tone_strength: float,
    ) -> Optional[Any]:
        """Build RFC-012 friction input from runtime context."""
        kernel = self._get_governance_kernel()
        if kernel is None:
            return None

        try:
            return kernel.compute_runtime_friction(
                prior_tension=prior_tension,
                tone_strength=tone_strength,
            )
        except Exception:
            return None

    @staticmethod
    def _coerce_friction_score(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))

        raw_value = getattr(value, "friction_score", None)
        if isinstance(raw_value, (int, float)):
            return max(0.0, min(1.0, float(raw_value)))

        if isinstance(value, dict):
            raw_value = value.get("friction_score")
            if isinstance(raw_value, (int, float)):
                return max(0.0, min(1.0, float(raw_value)))

        return None

    def _resolve_council_decision(
        self,
        *,
        tone_strength: float,
        runtime_friction: Any,
        governance_friction: Optional[float],
        user_tier: str,
        user_message: str,
    ) -> tuple[bool, Optional[str], Optional[float]]:
        friction_score = self._coerce_friction_score(runtime_friction)
        if friction_score is None:
            friction_score = self._coerce_friction_score(governance_friction)

        kernel = self._get_governance_kernel()
        if kernel is None:
            return True, None, friction_score

        try:
            should_convene, reason = kernel.should_convene_council(
                tension=tone_strength,
                friction_score=friction_score,
                user_tier=user_tier,
                message_length=len(str(user_message or "")),
            )
        except Exception:
            return True, None, friction_score

        return bool(should_convene), str(reason or "").strip() or None, friction_score

    @staticmethod
    def _merge_memory_results(primary: List[Any], secondary: List[Any]) -> List[Any]:
        merged: List[Any] = []
        seen: set = set()

        for result in list(primary or []) + list(secondary or []):
            doc_id = getattr(result, "doc_id", None)
            if doc_id is None:
                source = str(getattr(result, "source_file", "")).strip()
                content = str(getattr(result, "content", "")).strip()
                doc_id = f"{source}|{content[:96]}"
            key = str(doc_id)
            if key in seen:
                continue
            seen.add(key)
            merged.append(result)

        return merged

    def process(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        full_analysis: bool = True,
        council_mode: Optional[str] = None,
        perspective_config: Optional[Dict[str, Dict[str, Any]]] = None,
        prior_tension: Optional[Dict[str, Any]] = None,
        persona_config: Optional[Dict[str, Any]] = None,
        user_tier: str = "free",
        user_id: str = "anonymous",
    ) -> UnifiedResponse:
        """
        處理用戶訊息並產生回應。

        Args:
            user_message: 用戶輸入
            history: 對話歷史
            full_analysis: 是否執行完整 ToneBridge 分析

        Returns:
            UnifiedResponse: 包含回應與分析資料
        """
        history = history or []
        raw_user_message = user_message

        # ========== Phase V: Compute Gate (Revenue / API Protection) ==========
        from tonesoul.gates.compute import ComputeGate, RoutingPath

        compute_gate = ComputeGate(local_model_enabled=True)

        # Estimate initial tension from prior history to aid routing
        initial_tension = 0.0
        if prior_tension and "delta_t" in prior_tension:
            try:
                initial_tension = float(prior_tension.get("delta_t", 0.0) or 0.0)
            except (TypeError, ValueError):
                pass
        governance_friction = self._compute_prior_governance_friction(
            prior_tension=prior_tension,
            user_message=raw_user_message,
        )

        # Route based on the raw user message. Recovery context can expand token
        # length significantly and should not affect fast-path eligibility.
        routing_decision = compute_gate.evaluate(
            user_tier,
            raw_user_message,
            initial_tension,
            user_id=user_id,
            friction_score=governance_friction,
        )
        governance_kernel = self._get_governance_kernel()

        def _base_dispatch_trace() -> Dict[str, Any]:
            routing_trace = {
                "route": routing_decision.path.value,
                "journal_eligible": routing_decision.journal_eligible,
                "reason": routing_decision.reason,
            }
            if governance_kernel is not None:
                try:
                    routing_trace = governance_kernel.build_routing_trace(**routing_trace)
                except Exception:
                    pass
            return {
                **routing_trace,
                "routing_trace": dict(routing_trace),
                "pre_gate_initial_tension": initial_tension,
                "pre_gate_governance_friction": governance_friction,
            }

        # FAST ROUTE: Bypass all expensive Cloud APIs and Council layers
        if routing_decision.path == RoutingPath.PASS_LOCAL:
            from tonesoul.local_llm import ask_local_llm

            local_response = ask_local_llm(raw_user_message)
            local_dispatch_trace = _base_dispatch_trace()
            self._attach_runtime_governance_observability(local_dispatch_trace)
            return UnifiedResponse(
                response=local_response,
                council_verdict=self._normalize_council_verdict_payload({"verdict": "bypassed"}),
                tonebridge_analysis={},
                inner_narrative=routing_decision.reason,
                dispatch_trace=local_dispatch_trace,
            )
        elif routing_decision.path == RoutingPath.BLOCK_RATE_LIMIT:
            dispatch_trace = _base_dispatch_trace()
            self._apply_repair_trace(
                dispatch_trace=dispatch_trace,
                original_gate="block_rate_limit",
                source_text=raw_user_message,
                output_text="[系統防護] 請求頻率過高，已觸發速率限制，請稍後再試。",
                tension_before=None,
                fallback_delta=initial_tension,
                text_tension=initial_tension,
                stages=["rate_limit_block"],
                attempt_after_tension=False,
            )
            self._attach_runtime_governance_observability(dispatch_trace)
            return UnifiedResponse(
                response="[系統防護] 請求頻率過高，已觸發速率限制，請稍後再試。",
                council_verdict=self._normalize_council_verdict_payload(
                    {"verdict": "blocked_by_gate"}
                ),
                tonebridge_analysis={},
                inner_narrative=routing_decision.reason,
                dispatch_trace=dispatch_trace,
            )

        # ========== Cross-Session Recovery (first non-fast path call only) ==========
        user_message = self._try_cross_session_recovery(raw_user_message)

        # ========== 注入 Adapter（persona + context）==========
        user_message = self.build_injection_context(user_message, persona_config=persona_config)

        # ========== 0. 重建 Third Axiom 狀態 ==========
        # 從歷史記錄重建 commit_stack，確保每次 request 狀態一致
        self._rebuild_stack_from_history(history)

        # ========== 0.5 重建軌跡分析器狀態 ==========
        # 修復對話歷史 bug
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
                # 取得 ToneBridge 語氣分析結果
                if tb_result and tb_result.tone:
                    tone_strength = tb_result.tone.tone_strength

                # 軌跡分析
                traj_analysis = trajectory.analyze(user_message, tone_strength)
                trajectory_result = traj_analysis.to_dict()
                resonance_state = traj_analysis.resonance_state.value
                loop_detected = traj_analysis.loop_detected

            except Exception as e:
                print(f"Trajectory analysis error: {e}")

        # ========== 2.1 Unified Tension Computation ==========
        tension_result = None
        tension_engine = self._get_tension_engine()
        if tension_engine:
            try:
                tension_result = tension_engine.compute(
                    text_tension=tone_strength,
                    confidence=(getattr(tb_result, "confidence", 0.8) if tb_result else 0.8),
                )
                # Enrich dispatch with multi-signal tension
                tone_strength = tension_result.total
            except Exception as e:
                print(f"TensionEngine error: {e}")

        dispatch_trace = _base_dispatch_trace()
        dispatch_trace.update(
            {
                "tension_score": tone_strength,
                "resonance_state": resonance_state,
                "loop_detected": loop_detected,
            }
        )
        # Attach TensionEngine detail to dispatch trace
        if tension_result is not None:
            try:
                dispatch_trace["tension_engine"] = tension_result.to_dict()
            except Exception:
                pass
        resistance_trace: Dict[str, Any] = {}
        runtime_friction = self._compute_runtime_friction(
            prior_tension=prior_tension,
            tone_strength=tone_strength,
        )
        if runtime_friction is not None:
            try:
                resistance_trace["friction"] = runtime_friction.to_dict()
            except Exception:
                pass

        prediction = (
            getattr(tension_result, "prediction", None) if tension_result is not None else None
        )
        lyapunov_exponent = (
            getattr(prediction, "lyapunov_exponent", None) if prediction is not None else None
        )
        if governance_kernel is not None and runtime_friction is not None:
            cb_status, cb_reason, cb_state = governance_kernel.check_circuit_breaker(
                runtime_friction,
                lyapunov_exponent=lyapunov_exponent,
            )
            if cb_state:
                resistance_trace["circuit_breaker"] = cb_state
            if cb_status == "frozen":
                dispatch_trace["resistance"] = resistance_trace
                trajectory_result["dispatch"] = dispatch_trace
                block_response = (
                    "[系統防護] CircuitBreaker 已觸發 Freeze Protocol，暫停高風險推理，"
                    f"原因：{cb_reason}"
                )
                self._apply_repair_trace(
                    dispatch_trace=dispatch_trace,
                    original_gate="circuit_breaker_block",
                    source_text=raw_user_message,
                    output_text=block_response,
                    tension_before=tension_result,
                    fallback_delta=initial_tension,
                    text_tension=tone_strength,
                    stages=["circuit_breaker_block"],
                    attempt_after_tension=False,
                )
                self._attach_runtime_governance_observability(dispatch_trace)
                return UnifiedResponse(
                    response=block_response,
                    council_verdict=self._normalize_council_verdict_payload(
                        {
                            "verdict": "blocked_by_circuit_breaker",
                            "reason": cb_reason,
                        }
                    ),
                    tonebridge_analysis=tb_result.to_dict() if tb_result else {},
                    inner_narrative="Freeze protocol triggered by runtime resistance checks.",
                    internal_monologue=(
                        "Runtime guardrail interrupted the generation path " f"due to: {cb_reason}"
                    ),
                    persona_mode="Guardian",
                    trajectory_analysis=trajectory_result,
                    dispatch_trace=dispatch_trace,
                )

        perturbation_path = None
        if tension_result is not None:
            throttle = getattr(tension_result, "throttle", None)
            compression = getattr(tension_result, "compression", None)
            severity = (
                str(getattr(getattr(throttle, "severity", None), "value", "")).strip().lower()
            )
            if (
                compression is not None
                and severity in {"severe", "critical"}
                and getattr(compression, "compression_ratio", None) is not None
            ):
                if governance_kernel is not None:
                    perturbation_path = governance_kernel.recover_perturbation(
                        compression_ratio=float(compression.compression_ratio),
                        gamma_effective=getattr(compression, "gamma_effective", None),
                        friction=runtime_friction,
                    )
                if perturbation_path is not None:
                    try:
                        resistance_trace["perturbation_recovery"] = perturbation_path.to_dict()
                    except Exception:
                        pass

        if resistance_trace:
            dispatch_trace["resistance"] = resistance_trace
        trajectory_result["dispatch"] = dispatch_trace
        # ========== 2.5 ToneSoul 2.0: 內在審議 ==========
        deliberation = self._get_deliberation()
        deliberation_result = None
        persona_mode = "Philosopher"  # 預設模式
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
                # Fallback dispatch mapping
                dispatch_state = dispatch_trace.get("state", "A")
                if dispatch_state == "C":
                    persona_mode = "Guardian"
                elif dispatch_state == "B":
                    persona_mode = "Engineer"
                else:
                    from tonesoul.tonebridge import get_persona_from_resonance

                    persona = get_persona_from_resonance(resonance_state)
                    persona_mode = persona.value
                internal_monologue = "Fallback to deterministic persona mapping."

        # ========== 3. 第三公理：載入承諾堆疊 ==========
        commit_stack = self._get_commit_stack()
        commitment_prompt = ""
        detected_ruptures: List[Any] = []
        new_commit = None
        semantic_topics: List[str] = self._collect_semantic_topics(tb_result)
        semantic_contradictions: List[Dict[str, Any]] = []
        semantic_graph_summary: Dict[str, Any] = {}
        if commit_stack:
            commitment_prompt = commit_stack.format_for_prompt(n=3)

        # ========== 3.5 注入早期矛盾警告 ==========
        user_message = self._inject_early_contradiction_warning(user_message)

        # ========== 3.6 GraphRAG Context Retrieval ==========
        user_message = self._inject_graph_rag_context(user_message, tb_result=tb_result)

        # ========== 3.7 Semantic Trigger (high-tension recurrence check) ==========
        user_message = self._semantic_trigger_check(
            tension_score=tone_strength,
            current_topics=semantic_topics,
            user_message=user_message,
        )

        # ========== 3.8 Hippocampus Subconscious Retrieval ==========
        try:
            from tonesoul.memory.openclaw.embeddings import (
                HashEmbedding,
                SentenceTransformerEmbedding,
            )
            from tonesoul.memory.openclaw.hippocampus import Hippocampus

            # Lazy initialize the real Hippocampus with embedder and precise db_path
            if not getattr(self, "_hippocampus", None):
                db_path = os.path.join(self._repo_root, "memory", "memory_base")
                profile = os.getenv("TONESOUL_MEMORY_EMBEDDER", "auto").strip().lower()
                if profile in {"hash", "offline"}:
                    embedder = HashEmbedding()
                elif profile in {"sentence-transformer", "st"}:
                    embedder = SentenceTransformerEmbedding()
                else:
                    try:
                        embedder = SentenceTransformerEmbedding()
                    except Exception:
                        embedder = HashEmbedding()
                self._hippocampus = Hippocampus(
                    db_path=db_path,
                    embedder=embedder,
                )

            if self._hippocampus.index is not None or self._hippocampus.bm25 is not None:
                zone = getattr(tension_result, "zone", None) if tension_result is not None else None
                prediction = (
                    getattr(tension_result, "prediction", None)
                    if tension_result is not None
                    else None
                )
                zone_value = getattr(zone, "value", zone) or "stable"
                trend_value = getattr(prediction, "trend", None) if prediction is not None else None
                work_category = (
                    getattr(tension_result, "work_category", None)
                    if tension_result is not None
                    else None
                )
                tension_context = {
                    "zone": str(zone_value),
                    "trend": str(trend_value or "stable"),
                    "work_category": str(work_category or "engineering"),
                }
                # Pass query_tension to trigger ToneSoul resonance reranking
                primary_results = self._hippocampus.recall(
                    query_text=user_message,
                    top_k=3,
                    query_tension=tone_strength,
                    tension_context=tension_context,
                )
                corrective_results: List[Any] = []
                corrective_vector_norm: Optional[float] = None
                if self._enable_corrective_recall:
                    try:
                        import numpy as np

                        from tonesoul.memory.hippocampus import Hippocampus as CorrectiveMemory

                        embedder = getattr(self._hippocampus, "embedder", None)
                        if embedder is not None and hasattr(embedder, "encode"):
                            intended_vec = np.asarray(
                                embedder.encode(raw_user_message), dtype=np.float32
                            )
                            generated_vec = np.asarray(
                                embedder.encode(user_message), dtype=np.float32
                            )
                            if intended_vec.shape == generated_vec.shape and intended_vec.size > 0:
                                b_vec = CorrectiveMemory.compute_error_vector(
                                    intended=intended_vec,
                                    generated=generated_vec,
                                )
                                corrective_vector_norm = float(np.linalg.norm(b_vec))
                                corrective_results = self._hippocampus.recall(
                                    query_text=user_message,
                                    query_vector=b_vec,
                                    top_k=2,
                                    query_tension=tone_strength,
                                    tension_context=tension_context,
                                    query_tension_mode="conflict",
                                )
                    except Exception as corrective_error:
                        print(f"Hippocampus corrective recall error: {corrective_error}")

                memory_results = self._merge_memory_results(primary_results, corrective_results)
                dispatch_trace["memory_correction"] = {
                    "primary_hits": len(primary_results or []),
                    "corrective_hits": len(corrective_results or []),
                    "enabled": bool(self._enable_corrective_recall),
                }
                if corrective_vector_norm is not None:
                    dispatch_trace["memory_correction"]["b_vec_norm"] = round(
                        corrective_vector_norm,
                        6,
                    )

                if memory_results:
                    recalled_texts = "\n".join(
                        [
                            f"[{m.source_file} (Score: {m.score:.2f})]\n{m.content}"
                            for m in memory_results
                        ]
                    )
                    user_message += (
                        f"\n\n[系統潛意識記憶 / Ancestral Memory Context]\n{recalled_texts}\n"
                    )
        except Exception as e:
            print(f"Hippocampus retrieval error: {e}")

        # ========== 4. 生成增強 prompt ==========
        system_context = self._build_context_prompt(
            tb_result, persona_mode, trajectory_result, commitment_prompt
        )

        # ========== 4. LLM 生成回應 ==========
        router = self._get_llm_router()
        llm_client = self._get_llm_client()
        response = ""
        suggested_replies = []
        if llm_client:
            try:
                full_prompt = f"""{system_context}

User message:
{user_message}

Respond with a clear, practical answer."""

                if perturbation_path is not None:
                    try:
                        delay_ms = int(
                            getattr(getattr(perturbation_path, "throttle", None), "delay_ms", 0)
                            or 0
                        )
                        # Keep the delay bounded to avoid hard stalls during runtime.
                        if delay_ms > 0:
                            time.sleep(min(delay_ms, 1500) / 1000.0)
                    except Exception:
                        pass

                if router is not None:
                    response = router.chat(history=history, prompt=full_prompt)
                else:
                    llm_client.start_chat(history)
                    response = llm_client.send_message(full_prompt)
                self._attach_llm_observability(
                    dispatch_trace=dispatch_trace,
                    llm_client=llm_client,
                )
            except Exception as e:
                response = f"抱歉，生成回應時發生錯誤：{e}"
        else:
            response = "抱歉，LLM 服務不可用。"

        # ========== 6. Council 審議 ==========
        council = self._get_council()
        verdict_dict = {}
        repair_stages: List[str] = []
        council_should_convene, council_reason, council_friction_score = self._resolve_council_decision(
            tone_strength=tone_strength,
            runtime_friction=runtime_friction,
            governance_friction=governance_friction,
            user_tier=user_tier,
            user_message=raw_user_message,
        )
        if council_reason or council_friction_score is not None:
            dispatch_trace["council"] = {
                "convened": bool(council and council_should_convene),
                "reason": council_reason,
                "friction_score": council_friction_score,
            }
        if council and council_should_convene:
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
                council_context["dispatch"] = dispatch_trace

                # Custom role council (Team Simulator mode)
                custom_perspectives = None
                if isinstance(persona_config, dict):
                    custom_roles = persona_config.get("custom_roles")
                    if isinstance(custom_roles, list) and custom_roles:
                        from tonesoul.council.perspective_factory import (
                            PerspectiveFactory,
                        )

                        custom_perspectives = PerspectiveFactory.create_custom_council(custom_roles)

                request = CouncilRequest(
                    draft_output=response,
                    context=council_context,
                    perspectives=custom_perspectives,
                    perspective_config=resolved_perspective_config,
                )
                verdict = council.deliberate(request)
                verdict_dict = verdict.to_dict()

                # 處理判決結果
                if verdict.verdict.name == "BLOCK":
                    response = "抱歉，這個請求觸發了安全審議，我無法這樣回應。"
                    repair_stages.append("council_block")
                elif verdict.verdict.name == "DECLARE_STANCE":
                    response = f"[這是我的立場]\n\n{response}"
                    repair_stages.append("council_rewrite")
                elif verdict.verdict.name == "REFINE":
                    repair_stages.append("council_rewrite")
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
                        f"\n\n[Rupture warning] Detected {len(detected_ruptures)} potential "
                        "commitment ruptures."
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

        # ========== 9. 更新記憶單元 ==========
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
                # 預測共鳴路徑
                tb_result.resonance = tonebridge.predict_resonance(tb_result.memini)
            except Exception:
                pass

        # ========== 11. 更新 Trajectory 歷史 ==========
        if trajectory:
            tone_state = trajectory_result.get("resonance_state", "resonance")
            trajectory.add_turn(user_message, response, tone_state)

        # ========== 12. 產生內部敘事摘要 ==========
        inner_narrative = self._generate_narrative(tb_result, verdict_dict)

        # 干預策略
        intervention = ""
        if tb_result and tb_result.resonance:
            intervention = tb_result.resonance.suggested_intervention_strategy

        # ========== 13. 收集 Third Axiom 資料 ==========
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

        # 將語義矛盾與圖譜附加到 verdict metadata，供前端顯示
        if isinstance(verdict_dict, dict):
            verdict_metadata = verdict_dict.get("metadata")
            if not isinstance(verdict_metadata, dict):
                verdict_metadata = {}
            verdict_metadata["semantic_contradictions"] = semantic_contradictions
            if semantic_graph_summary:
                verdict_metadata["semantic_graph"] = semantic_graph_summary
            verdict_metadata["dispatch_state"] = dispatch_trace.get("state")
            verdict_metadata["dispatch"] = dispatch_trace
            verdict_dict["metadata"] = verdict_metadata
            verdict_dict = self._normalize_council_verdict_payload(verdict_dict)

        # 自動捕捉 visual chain frame，記錄每輪狀態
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
                if dispatch_trace.get("state") == "C":
                    frame_tags.append("dispatch_conflict")
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
                        "dispatch_state": dispatch_trace.get("state"),
                        "dispatch_mode": dispatch_trace.get("mode"),
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

                # Evolutionary Memory Isolation (Phase V)
                # Only write standard interactions to journal if they are eligible
                if routing_decision.journal_eligible:
                    chain.capture(
                        frame_type=FrameType.SESSION_STATE,
                        title=f"Premium Journal Eligible Turn {chain.frame_count}",
                        data={"journal_commit": True, "reason": routing_decision.reason},
                        tags=["journal_eligible"],
                    )
            except Exception:
                pass

        # ========== 8.5 PersonaDimension Post-Processing ==========
        try:
            from tonesoul.persona_dimension import PersonaDimension

            pd_config = persona_config or {}
            pd = PersonaDimension(pd_config)
            dispatch_mode = dispatch_trace.get("mode", "resonance")
            pd_output, pd_result = pd.process(
                output=response,
                context={
                    "tension": tone_strength,
                    "zone": dispatch_mode,
                    "delta_sigma": (
                        tension_result.signals.semantic_delta if tension_result else 0.0
                    ),
                },
                shadow=(dispatch_mode == "resonance"),
                intercept=(dispatch_mode in ("tension", "conflict")),
            )
            if isinstance(pd_result, dict) and pd_result.get("corrected"):
                response = pd_output
                repair_stages.append("persona_dimension_rewrite")
        except Exception:
            pass

        if repair_stages:
            self._apply_repair_trace(
                dispatch_trace=dispatch_trace,
                original_gate=repair_stages[0],
                source_text=raw_user_message,
                output_text=response,
                tension_before=tension_result,
                fallback_delta=initial_tension,
                text_tension=tone_strength,
                stages=repair_stages,
                attempt_after_tension=True,
            )

        self._attach_runtime_governance_observability(dispatch_trace)
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
            dispatch_trace=dispatch_trace,
        )

    def _build_context_prompt(
        self,
        tb_result,
        persona_mode: str = "Philosopher",
        trajectory_result: dict = None,
        commitment_prompt: str = "",
    ) -> str:
        """Build runtime context prompt for the LLM call."""
        lines: List[str] = []
        lines.append(f"Persona mode: {persona_mode}")

        if commitment_prompt:
            lines.append("Recent commitments:")
            lines.append(commitment_prompt)

        if trajectory_result:
            direction = trajectory_result.get("direction_change", "stable")
            loop_detected = bool(trajectory_result.get("loop_detected", False))
            lines.append(f"Trajectory direction: {direction}")
            lines.append(f"Loop detected: {loop_detected}")
            dispatch = trajectory_result.get("dispatch")
            if isinstance(dispatch, dict):
                lines.append(
                    f"Dispatch state: {dispatch.get('state', 'A')} "
                    f"(adjusted_tension={dispatch.get('adjusted_tension', 0.0)})"
                )
                resistance = dispatch.get("resistance")
                if isinstance(resistance, dict):
                    cb = resistance.get("circuit_breaker")
                    if isinstance(cb, dict):
                        lines.append(
                            "Circuit breaker: "
                            f"{cb.get('status', 'unknown')}"
                            + (f" (reason={cb.get('reason')})" if cb.get("reason") else "")
                        )
                    recovery = resistance.get("perturbation_recovery")
                    if isinstance(recovery, dict):
                        path_id = recovery.get("path_id")
                        stress = recovery.get("effective_stress")
                        lines.append(
                            "Perturbation recovery: " f"path={path_id}, effective_stress={stress}"
                        )
                correction = dispatch.get("memory_correction")
                if isinstance(correction, dict):
                    lines.append(
                        "Memory corrective recall: "
                        f"primary={correction.get('primary_hits', 0)}, "
                        f"corrective={correction.get('corrective_hits', 0)}"
                    )

        if tb_result and getattr(tb_result, "tone", None):
            lines.append(
                "Tone hint: "
                f"{getattr(tb_result.tone, 'emotion_prediction', 'unknown')} "
                f"(strength={getattr(tb_result.tone, 'tone_strength', 0.0)})"
            )
        if tb_result and getattr(tb_result, "motive", None):
            motive = getattr(tb_result.motive, "likely_motive", None)
            if motive:
                lines.append(f"Likely motive: {motive}")

        lines.append("Reply with factual, concise, and safe guidance.")
        return "\n".join(lines)

    def _generate_narrative(self, tb_result, verdict_dict: Dict) -> str:
        """Generate a compact narrative summary for observability."""
        lines: List[str] = []

        if tb_result and getattr(tb_result, "tone", None):
            tone = tb_result.tone
            lines.append(
                "Tone summary: "
                f"{getattr(tone, 'emotion_prediction', 'unknown')} "
                f"(strength={getattr(tone, 'tone_strength', 0.0):.2f})"
            )

        if tb_result and getattr(tb_result, "motive", None):
            motive = getattr(tb_result.motive, "likely_motive", None)
            if motive:
                lines.append(f"Motive summary: {motive}")

        verdict = str(verdict_dict.get("verdict", "unknown")).strip().lower()
        verdict_map = {
            "approve": "Council approved the draft output.",
            "block": "Council blocked the draft output.",
            "declare_stance": "Council requested stance declaration.",
            "refine": "Council requested refinement.",
        }
        if verdict in verdict_map:
            lines.append(verdict_map[verdict])

        if not lines:
            return "No additional narrative signals."
        return "\n".join(lines)


def create_unified_pipeline() -> UnifiedPipeline:
    """Factory function to create a unified pipeline."""
    return UnifiedPipeline()
