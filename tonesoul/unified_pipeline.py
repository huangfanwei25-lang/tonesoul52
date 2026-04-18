"""
ToneSoul Unified Pipeline
Combines ToneBridge psychological analysis with Council deliberation.
"""

from __future__ import annotations

__ts_layer__ = "pipeline"
__ts_purpose__ = "Top-level runtime pipeline that wires perception, council, and output surfaces."

import inspect
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tonesoul.exception_trace import ExceptionTrace
from tonesoul.schemas import DispatchTraceSection


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

    def __init__(self, gemini_client=None, mirror_enabled: Optional[bool] = None):
        self._llm_client = gemini_client
        self._llm_router = None
        self._governance_kernel = None
        self._exc_trace = ExceptionTrace()
        self._reflex_gate_modifier: float = 1.0
        self._current_governance_depth: str = "standard"
        self._mirror = None
        self._mirror_enabled = (
            _read_bool_env("TONESOUL_MIRROR_ENABLED", default=True)
            if mirror_enabled is None
            else bool(mirror_enabled)
        )
        mirror_mode = str(os.environ.get("TONESOUL_MIRROR_MODE", "observe") or "observe")
        self._mirror_mode = mirror_mode.strip().lower()
        if self._mirror_mode not in {"observe", "enforce"}:
            self._mirror_mode = "observe"
        self._tonebridge = None
        self._council = None
        self._trajectory = None
        self._drift_monitor = None
        self._alert_escalation = None
        self._contract_verifier = None
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
        # YUHUN Core Protocol v1.0 — DPR + ContextAssembler
        self._dpr = None
        self._context_assembler = None

    def _get_governance_kernel(self):
        if self._governance_kernel is None:
            try:
                from tonesoul.governance.kernel import GovernanceKernel

                self._governance_kernel = GovernanceKernel()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_governance_kernel", e)
                pass
        return self._governance_kernel

    def _get_dpr(self):
        """YUHUN DPR — 動態優先路由器（懶載入，失敗時降級）"""
        if self._dpr is None:
            try:
                from tonesoul.yuhun.dpr import route as dpr_route

                self._dpr = dpr_route
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_dpr", e)
        return self._dpr

    def _get_context_assembler(self):
        """YUHUN ContextAssembler — Context Budget 組裝器（懶載入，失敗時降級）"""
        if self._context_assembler is None:
            try:
                from tonesoul.yuhun.context_assembler import ContextAssembler

                self._context_assembler = ContextAssembler(repo_root=self._repo_root)
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_context_assembler", e)
        return self._context_assembler

    def _get_llm_router(self):
        if self._llm_router is None:
            try:
                from tonesoul.llm.router import LLMRouter

                self._llm_router = LLMRouter(
                    backend_resolver=self._governance_llm_resolver,
                )
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_llm_router", e)
                pass
        return self._llm_router

    @staticmethod
    def _governance_llm_resolver(*, preferred_backend: str = "auto"):
        """Resolve LLM backend via GovernanceKernel (injected into LLMRouter)."""
        from tonesoul.governance.kernel import GovernanceKernel

        kernel = GovernanceKernel()
        return kernel.resolve_llm_backend(preferred_backend=preferred_backend)

    @staticmethod
    def _normalize_council_verdict_payload(payload: Any) -> Dict[str, Any]:
        try:
            from tonesoul.schemas import CouncilRuntimeVerdictPayload

            return CouncilRuntimeVerdictPayload.build_payload(payload)
        except Exception:
            return dict(payload) if isinstance(payload, dict) else {}

    def _extract_council_verdict_name(self, payload: Any) -> Optional[str]:
        normalized = self._normalize_council_verdict_payload(payload)
        verdict = normalized.get("verdict")
        if verdict is None:
            if isinstance(payload, str):
                normalized_text = payload.strip().lower()
                return normalized_text or None
            return None
        normalized_text = str(verdict).strip().lower()
        return normalized_text or None

    def _get_llm_client(self):
        if self._llm_client is not None:
            router = self._get_llm_router()
            if router is not None:
                try:
                    router.prime(self._llm_client, backend=self._llm_backend)
                except Exception as e:
                    self._exc_trace.record("unified_pipeline", "_get_llm_client.prime_router", e)
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
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_get_llm_client.get_client", e)
            return None
        return self._llm_client

    def _get_tonebridge(self):
        if self._tonebridge is None:
            try:
                from tonesoul.tonebridge import ToneBridgeAnalyzer

                self._tonebridge = ToneBridgeAnalyzer(self._get_llm_client())
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_tonebridge", e)
                pass
        return self._tonebridge

    def _get_council(self):
        if self._council is None:
            try:
                from tonesoul.council import CouncilRuntime

                self._council = CouncilRuntime()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_council", e)
                pass
        return self._council

    def _get_trajectory(self):
        if self._trajectory is None:
            try:
                from tonesoul.tonebridge import TrajectoryAnalyzer

                self._trajectory = TrajectoryAnalyzer(window_size=5)
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_trajectory", e)
                pass
        return self._trajectory

    def _get_drift_monitor(self):
        if self._drift_monitor is None:
            try:
                from tonesoul.drift_monitor import DriftMonitor

                self._drift_monitor = DriftMonitor()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_drift_monitor", e)
                pass
        return self._drift_monitor

    def _get_alert_escalation(self):
        if self._alert_escalation is None:
            try:
                from tonesoul.alert_escalation import AlertEscalation

                self._alert_escalation = AlertEscalation()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_alert_escalation", e)
                pass
        return self._alert_escalation

    def _get_contract_verifier(self):
        if self._contract_verifier is None:
            try:
                from tonesoul.contract_observer import ContractVerifier

                self._contract_verifier = ContractVerifier()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_contract_verifier", e)
                pass
        return self._contract_verifier

    def _build_scenario_envelope(
        self,
        user_message: str,
        history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build explicit bull/base/bear frames before deliberation."""
        try:
            from tonesoul.tonebridge import ScenarioEnvelopeBuilder

            builder = ScenarioEnvelopeBuilder()
            return builder.build(user_message, history)
        except Exception as e:
            return {
                "enabled": False,
                "source": "unavailable",
                "reason": f"error:{e.__class__.__name__}",
                "frames": [],
                "summary": "scenario_envelope_unavailable",
            }

    # ===== ToneSoul 2.0: Internal Deliberation =====
    def _get_deliberation(self):
        """Get or create the Internal Deliberation engine."""
        if self._deliberation is None:
            try:
                from tonesoul.deliberation import InternalDeliberation

                self._deliberation = InternalDeliberation()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_deliberation", e)
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
                self._tension_engine.load_persistence()
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_get_tension_engine", e)
                pass
        return self._tension_engine

    def _get_mirror(self):
        """Get or create the opt-in runtime mirror."""
        if not self._mirror_enabled:
            return None
        if self._mirror is None:
            try:
                from tonesoul.mirror import ToneSoulMirror

                self._mirror = ToneSoulMirror(
                    tension_engine=self._get_tension_engine(),
                    governance_kernel=self._get_governance_kernel(),
                )
            except Exception:
                pass
        return self._mirror

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

    def _build_trace_section(
        self,
        component: str,
        detail: Optional[Dict[str, Any]],
        *,
        status: str = "ok",
    ) -> DispatchTraceSection:
        payload = dict(detail) if isinstance(detail, dict) else {}
        normalized_status = str(status or "ok").strip().lower()
        if normalized_status not in {"ok", "degraded", "error"}:
            normalized_status = "ok"
        section: Dict[str, Any] = dict(payload)
        section["component"] = component
        section["timestamp"] = datetime.now(timezone.utc).isoformat()
        section["status"] = normalized_status
        section["detail"] = payload
        return section

    @staticmethod
    def _normalize_runtime_zone(current_zone: Optional[str]) -> str:
        normalized_zone = str(current_zone or "safe").strip().lower()
        if normalized_zone not in {"safe", "transit", "risk", "danger"}:
            normalized_zone = "safe"
        return normalized_zone

    @staticmethod
    def _normalize_governance_depth_plan(plan: Any) -> Dict[str, Any]:
        if plan is None:
            return {}
        if isinstance(plan, dict):
            return dict(plan)
        to_dict = getattr(plan, "to_dict", None)
        if callable(to_dict):
            try:
                normalized = to_dict()
            except Exception:
                return {}
            return dict(normalized) if isinstance(normalized, dict) else {}
        return {}

    # --- Governance Reflex Arc helpers ---

    def _compute_reflex_decision(
        self,
        tension: float,
        *,
        vow_result: Any = None,
        council_verdict: Any = None,
    ) -> Optional[Any]:
        """Compute reflex arc decision from current governance posture.

        Loads governance state, classifies soul band, evaluates drift/vow/council
        signals, and returns a ReflexDecision. Returns None if reflex is
        unavailable or disabled.
        """
        try:
            from tonesoul.governance.reflex import GovernanceSnapshot, ReflexEvaluator
            from tonesoul.governance.reflex_config import load_reflex_config
            from tonesoul.runtime_adapter import load as load_posture

            config = load_reflex_config()
            if not config.enabled:
                return None

            posture = load_posture()
            vow_blocked = bool(getattr(vow_result, "blocked", False))
            vow_repair_needed = bool(getattr(vow_result, "repair_needed", False))
            raw_vow_flags = getattr(vow_result, "flags", []) if vow_result is not None else []
            vow_flags = list(raw_vow_flags or [])
            snapshot = GovernanceSnapshot.from_posture(
                posture,
                tension=tension,
                vow_blocked=vow_blocked,
                vow_repair_needed=vow_repair_needed,
                vow_flags=vow_flags,
                council_verdict=self._extract_council_verdict_name(council_verdict),
            )
            evaluator = ReflexEvaluator(config=config)
            return evaluator.evaluate(snapshot)
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_compute_reflex_decision", e)
            return None

    @staticmethod
    def _apply_reflex_final_gate(
        response: str,
        reflex_decision: Any,
        repair_stages: List[str],
    ) -> str:
        """Apply the reflex arc's final gate to the response.

        - BLOCK: replace response with blocked message (counts as repair)
        - SOFTEN/WARN: append disclaimer (does NOT count as repair —
          disclaimers are governance annotations, not content repairs)
        - PASS: no change
        """
        from tonesoul.governance.reflex import ReflexAction

        action = getattr(reflex_decision, "action", ReflexAction.PASS)
        if action == ReflexAction.BLOCK:
            blocked_msg = getattr(reflex_decision, "blocked_message", None)
            if blocked_msg:
                repair_stages.append("reflex_block")
                return str(blocked_msg)
        elif action in (ReflexAction.SOFTEN, ReflexAction.WARN):
            disclaimer = getattr(reflex_decision, "disclaimer", None)
            if disclaimer:
                return f"{response}\n\n---\n{disclaimer}"
        return response

    def _enforce_poav_gate(
        self,
        *,
        response: str,
        current_zone: Optional[str],
        dispatch_trace: Dict[str, Any],
        lockdown_active: bool = False,
        source: str = "unified_pipeline",
    ) -> tuple[str, bool, Dict[str, Any]]:
        normalized_zone = self._normalize_runtime_zone(current_zone)
        high_risk_mode = bool(lockdown_active) or normalized_zone in {"risk", "danger"}

        try:
            from tonesoul.yss_gates import poav_gate
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_enforce_poav_gate.import", e)
            return response, False, {}

        threshold = 0.92 if high_risk_mode else 0.70
        enforce = high_risk_mode

        try:
            gate_result = poav_gate(
                response,
                threshold=threshold,
                enforce=enforce,
                source=source,
            )
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_enforce_poav_gate", e)
            return response, False, {}

        details = dict(gate_result.details) if isinstance(gate_result.details, dict) else {}
        components = (
            details.get("components") if isinstance(details.get("components"), dict) else {}
        )
        poav_total = float(components.get("total", 0.0) or 0.0)
        issues = list(gate_result.issues or [])
        blocked = bool(enforce and not gate_result.passed)

        result_payload = {
            "gate": gate_result.gate,
            "passed": bool(gate_result.passed),
            "issues": issues,
            "details": details,
            "current_zone": normalized_zone,
            "high_risk_mode": high_risk_mode,
            "blocked": blocked,
        }

        trace_detail = {
            **details,
            "current_zone": normalized_zone,
            "high_risk_mode": high_risk_mode,
            "passed": bool(gate_result.passed),
            "issues": issues,
            "issue_count": len(issues),
            "action": (
                "blocked"
                if blocked
                else str(details.get("decision") or ("record_only" if issues else "allow"))
            ),
            "poav_total": round(poav_total, 3),
        }
        dispatch_trace["poav"] = self._build_trace_section(
            "poav_gate",
            trace_detail,
            status="error" if blocked else ("degraded" if issues else "ok"),
        )

        if not blocked:
            return response, False, result_payload

        blocked_response = (
            "抱歉，這個回應未通過 POAV 治理閘門，我需要改用更可驗證、可審計的方式回答。"
        )
        return blocked_response, True, result_payload

    def _enforce_output_contracts(
        self,
        *,
        response: str,
        current_zone: Optional[str],
        dispatch_trace: Dict[str, Any],
    ) -> tuple[str, bool, Dict[str, Any]]:
        verifier = self._get_contract_verifier()
        normalized_zone = self._normalize_runtime_zone(current_zone)

        if verifier is None:
            return response, False, {}

        try:
            contract_result = verifier.verify_all(response, normalized_zone)
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_enforce_output_contracts", e)
            return response, False, {}

        violations = list(contract_result.get("violations") or [])
        critical_violations = [
            violation
            for violation in violations
            if str(violation.get("severity", "")).strip().lower() == "critical"
        ]
        blocked = bool(critical_violations)

        trace_detail = {
            "current_zone": normalized_zone,
            "passed": bool(contract_result.get("passed", not violations)),
            "checked": int(contract_result.get("checked", 0) or 0),
            "total_contracts": int(contract_result.get("total_contracts", 0) or 0),
            "violation_count": len(violations),
            "critical_violation_count": len(critical_violations),
            "action": "blocked" if blocked else "allow",
            "violations": violations,
        }
        dispatch_trace["contracts"] = self._build_trace_section(
            "contract_observer",
            trace_detail,
            status="error" if blocked else ("degraded" if violations else "ok"),
        )

        if not blocked:
            return response, False, contract_result

        blocked_response = "抱歉，這個回應未通過輸出契約檢查，我不能直接這樣回答。"
        return blocked_response, True, contract_result

    def _self_check(self, draft: str, context: dict) -> Any:
        from tonesoul.reflection import REFLECTION_TENSION_THRESHOLD, ReflectionVerdict
        from tonesoul.vow_system import VowEnforcer

        safe_context = dict(context) if isinstance(context, dict) else {}
        reasons: list[str] = []
        severity = 0.0
        vow_result = None
        council_decision: str | None = None
        tension_delta: float | None = None

        try:
            vow_result = VowEnforcer().enforce(draft)
            if vow_result.blocked:
                reasons.extend(list(vow_result.flags) or ["vow_block"])
                severity = max(severity, 0.9)
            elif vow_result.repair_needed:
                reasons.extend(list(vow_result.flags) or ["vow_repair"])
                severity = max(severity, 0.5)
            elif vow_result.flags:
                reasons.extend(list(vow_result.flags))
                severity = max(severity, 0.2)
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_self_check.vow_enforce", e)

        try:
            override_decision = safe_context.get("reflection_council_decision")
            skip_council = bool(safe_context.get("reflection_skip_council"))
            if isinstance(override_decision, str) and override_decision.strip():
                council_decision = override_decision.strip().lower()
            elif not skip_council:
                council = self._get_council()
                if council is not None:
                    from tonesoul.council import CouncilRequest

                    council_context = {
                        key: value
                        for key, value in safe_context.items()
                        if not str(key).startswith("reflection_")
                    }
                    council_verdict = council.deliberate(
                        CouncilRequest(draft_output=draft, context=council_context)
                    )
                    raw_decision = getattr(council_verdict, "verdict", None)
                    council_decision = getattr(raw_decision, "value", raw_decision)
                    if council_decision is not None:
                        council_decision = str(council_decision).strip().lower()

            if council_decision == "block":
                reasons.append("council:block")
                severity = max(severity, 0.9)
            elif council_decision == "refine":
                reasons.append("council:refine")
                severity = max(severity, 0.4)
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_self_check.council", e)

        try:
            tension_engine = self._get_tension_engine()
            if tension_engine is not None:
                baseline = None
                for candidate in (
                    safe_context.get("reflection_tension_baseline"),
                    safe_context.get("tension_baseline"),
                    safe_context.get("tension_score"),
                    (
                        safe_context.get("prior_tension", {}).get("delta_t")
                        if isinstance(safe_context.get("prior_tension"), dict)
                        else None
                    ),
                ):
                    try:
                        if candidate is None:
                            continue
                        baseline = float(candidate)
                        break
                    except (TypeError, ValueError):
                        continue

                draft_text_tension = safe_context.get("reflection_text_tension")
                try:
                    if draft_text_tension is None:
                        from tonesoul.persona_dimension import VectorCalculator

                        draft_text_tension = (
                            VectorCalculator()
                            .compute(
                                draft,
                                safe_context,
                            )
                            .deltaT
                        )
                    draft_text_tension = float(draft_text_tension)
                except Exception:
                    draft_text_tension = 0.0

                tension_result = tension_engine.compute(
                    text_tension=float(draft_text_tension),
                    confidence=safe_context.get("reflection_confidence"),
                )
                draft_total = float(getattr(tension_result, "total", 0.0) or 0.0)
                tension_delta = (
                    abs(draft_total - baseline) if baseline is not None else abs(draft_total)
                )
                if tension_delta > REFLECTION_TENSION_THRESHOLD:
                    reasons.append(f"tension_delta:{round(tension_delta, 4)}")
                    severity = max(severity, min(1.0, 0.3 + tension_delta))
        except Exception as e:
            self._exc_trace.record("unified_pipeline", "_self_check.tension", e)

        # Reflex arc severity boost: tighter gate → higher effective severity
        # Only boost when severity is already non-trivial (≥0.3) to avoid
        # promoting informational FLAGs into unnecessary revisions
        if self._reflex_gate_modifier < 1.0 and severity >= 0.3:
            boost = (1.0 - self._reflex_gate_modifier) * 0.3  # up to +0.135 at critical
            severity = min(1.0, severity + boost)

        # Phase 851: Post-hoc grounding check for high-risk turns.
        # Only runs when governance_depth is "full" (set by ComputeGate).
        grounding_result = None
        if getattr(self, "_current_governance_depth", "standard") == "full":
            try:
                from tonesoul.grounding_check import grounding_check

                ctx_keywords: list[str] = []
                ctx = safe_context.get("graph_rag_keywords")
                if isinstance(ctx, list):
                    ctx_keywords = [str(k) for k in ctx]
                grounding_result = grounding_check(
                    draft,
                    safe_context.get("raw_user_message", ""),
                    context_keywords=ctx_keywords,
                )
                if grounding_result.thin_support:
                    reasons.append("grounding:thin_support")
                    severity = max(severity, 0.4)
            except Exception as e:
                self._exc_trace.record("unified_pipeline", "_self_check.grounding", e)

        should_revise = bool(reasons) and severity > 0.2
        verdict = ReflectionVerdict(
            should_revise=should_revise,
            reasons=reasons,
            severity=round(severity, 4),
            vow_result=vow_result,
            council_decision=council_decision,
            tension_delta=round(tension_delta, 4) if tension_delta is not None else None,
        )
        # Attach grounding result to verdict for trace visibility
        if grounding_result is not None:
            verdict.grounding_result = grounding_result  # type: ignore[attr-defined]
        return verdict

    def _apply_mirror_step(
        self,
        response: str,
        *,
        dispatch_trace: Dict[str, Any],
        trajectory_result: Dict[str, Any],
        user_tier: str,
        tone_strength: float,
        confidence: float,
    ) -> str:
        """Run the optional mirror step and surface its delta in runtime traces."""
        if not self._mirror_enabled:
            return response

        mirror = self._get_mirror()
        if mirror is None:
            mirror_trace = {
                "enabled": True,
                "available": False,
                "mode": self._mirror_mode,
                "final_choice": "raw",
                "reflection_note": "Mirror unavailable.",
            }
            section = self._build_trace_section("mirror", mirror_trace, status="degraded")
            dispatch_trace["mirror"] = section
            trajectory_result["mirror"] = dict(section)
            return response

        dual = mirror.reflect(
            response,
            {
                "user_tier": user_tier,
                "text_tension": tone_strength,
                "confidence": confidence,
            },
        )
        mirror_delta = dual.mirror_delta.model_dump(mode="json")
        mirror_trace = {
            "enabled": True,
            "available": True,
            "mode": self._mirror_mode,
            "final_choice": dual.final_choice,
            "reflection_note": dual.reflection_note,
            "mirror_triggered": dual.mirror_delta.mirror_triggered,
            "enforced": self._mirror_mode == "enforce",
            "mirror_delta": mirror_delta,
        }
        if self._mirror_mode != "enforce":
            mirror_trace["applied_response"] = "raw"
            section = self._build_trace_section(
                "mirror",
                mirror_trace,
                status="degraded" if dual.mirror_delta.mirror_triggered else "ok",
            )
            dispatch_trace["mirror"] = section
            trajectory_result["mirror"] = dict(section)
            trajectory_result["mirror_delta"] = dict(mirror_delta)
            return dual.raw_response or response

        mirror_trace["applied_response"] = dual.final_choice
        section = self._build_trace_section(
            "mirror",
            mirror_trace,
            status="degraded" if dual.mirror_delta.mirror_triggered else "ok",
        )
        dispatch_trace["mirror"] = section
        trajectory_result["mirror"] = dict(section)
        trajectory_result["mirror_delta"] = dict(mirror_delta)
        if dual.final_choice == "raw":
            return dual.raw_response or response
        return dual.governed_response or dual.raw_response or response

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

    def _inject_graph_rag_context(
        self, user_message: str, tb_result: Any = None
    ) -> tuple[str, Dict[str, Any]]:
        """Inject GraphRAG retrieval summary into prompt context with trace metadata."""
        trace: Dict[str, Any] = {
            "enabled": True,
            "applied": False,
            "query_terms": [],
            "matched_count": 0,
            "related_count": 0,
            "commitments_count": 0,
            "context_summary": "",
            "reason": "",
        }
        try:
            graph = self._get_semantic_graph()
            if not graph:
                trace["reason"] = "graph_unavailable"
                return user_message, trace
            query_terms = self._collect_graph_query_terms(user_message, tb_result)
            trace["query_terms"] = list(query_terms)
            if not query_terms:
                trace["reason"] = "no_query_terms"
                return user_message, trace
            graph_context = graph.retrieve_relevant(
                query_terms=query_terms, max_hops=2, max_results=10
            )
            matched_nodes = graph_context.get("matched_nodes") or []
            related_nodes = graph_context.get("related_nodes") or []
            commitments = graph_context.get("commitments_in_scope") or []
            trace["matched_count"] = len(matched_nodes)
            trace["related_count"] = len(related_nodes)
            trace["commitments_count"] = len(commitments)
            context_summary = str(graph_context.get("context_summary", "")).strip()
            trace["context_summary"] = context_summary
            if context_summary:
                trace["applied"] = True
                trace["reason"] = "summary_injected"
                return f"[語義圖譜檢索: {context_summary}]\n\n{user_message}", trace
            trace["reason"] = "no_summary"
        except Exception:
            trace["reason"] = "retrieval_error"
            return user_message, trace
        return user_message, trace

    @staticmethod
    def _fallback_persona_mode(dispatch_state: str, resonance_state: str) -> str:
        if dispatch_state == "C":
            return "Guardian"
        if dispatch_state == "B":
            return "Engineer"
        try:
            from tonesoul.tonebridge import get_persona_from_resonance

            persona = get_persona_from_resonance(resonance_state)
            return str(getattr(persona, "value", "Philosopher") or "Philosopher")
        except Exception:
            return "Philosopher"

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

        repair_event["repair_eligible"] = True
        dispatch_trace["repair"] = self._build_trace_section(
            "repair",
            repair_event,
            status="degraded",
        )

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
            governance_runtime = kernel.build_observability_trace(dispatch_trace)
            status = "error" if governance_runtime.get("freeze_triggered") else "ok"
            if governance_runtime.get("rollback_applied") and status == "ok":
                status = "degraded"
            dispatch_trace["governance_runtime"] = self._build_trace_section(
                "governance_runtime",
                governance_runtime,
                status=status,
            )
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
            dispatch_trace["llm"] = self._build_trace_section(
                "llm",
                llm_trace,
                status="ok",
            )

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
        force_convene: bool = False,
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
                force_convene=force_convene,
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
        self._exc_trace = ExceptionTrace()
        self._reflex_gate_modifier = 1.0
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
        governance_depth_plan = self._normalize_governance_depth_plan(
            getattr(routing_decision, "governance_depth_plan", None)
        )
        self._current_governance_depth = getattr(routing_decision, "governance_depth", "standard")
        governance_kernel = self._get_governance_kernel()

        def _base_dispatch_trace() -> Dict[str, Any]:
            routing_trace = {
                "route": routing_decision.path.value,
                "journal_eligible": routing_decision.journal_eligible,
                "reason": routing_decision.reason,
                "governance_depth": getattr(routing_decision, "governance_depth", "standard"),
                "governance_depth_plan": governance_depth_plan,
            }
            if governance_kernel is not None:
                try:
                    build_routing_trace = governance_kernel.build_routing_trace
                    routing_kwargs = {
                        "route": routing_decision.path.value,
                        "journal_eligible": routing_decision.journal_eligible,
                        "reason": routing_decision.reason,
                    }
                    try:
                        signature = inspect.signature(build_routing_trace)
                    except (TypeError, ValueError):
                        signature = None
                    if (
                        signature is None
                        or any(
                            parameter.kind == inspect.Parameter.VAR_KEYWORD
                            for parameter in signature.parameters.values()
                        )
                        or (
                            "governance_depth" in signature.parameters
                            and "governance_depth_plan" in signature.parameters
                        )
                    ):
                        routing_kwargs["governance_depth"] = getattr(
                            routing_decision, "governance_depth", "standard"
                        )
                        routing_kwargs["governance_depth_plan"] = governance_depth_plan
                    routing_trace = build_routing_trace(**routing_kwargs)
                except Exception as e:
                    self._exc_trace.record(
                        "unified_pipeline",
                        "process._base_dispatch_trace.build_routing_trace",
                        e,
                    )
                    pass
            if not isinstance(routing_trace, dict):
                routing_trace = {
                    "route": routing_decision.path.value,
                    "journal_eligible": routing_decision.journal_eligible,
                    "reason": routing_decision.reason,
                    "governance_depth": getattr(routing_decision, "governance_depth", "standard"),
                    "governance_depth_plan": governance_depth_plan,
                }
            if "governance_depth" not in routing_trace:
                routing_trace["governance_depth"] = getattr(
                    routing_decision, "governance_depth", "standard"
                )
            if "governance_depth_plan" not in routing_trace and governance_depth_plan:
                routing_trace["governance_depth_plan"] = governance_depth_plan
            detail = routing_trace.get("detail")
            if isinstance(detail, dict):
                detail.setdefault(
                    "governance_depth",
                    getattr(routing_decision, "governance_depth", "standard"),
                )
                if governance_depth_plan:
                    detail.setdefault("governance_depth_plan", governance_depth_plan)
            if "component" not in routing_trace or "timestamp" not in routing_trace:
                routing_trace = self._build_trace_section(
                    "compute_gate",
                    routing_trace,
                    status="degraded" if "suppressed_errors" in routing_trace else "ok",
                )
            return {
                "route": routing_trace.get("route"),
                "journal_eligible": routing_trace.get("journal_eligible"),
                "reason": routing_trace.get("reason"),
                "governance_depth": routing_trace.get("governance_depth"),
                "governance_depth_plan": (
                    self._build_trace_section(
                        "governance_depth_plan",
                        governance_depth_plan,
                        status="ok",
                    )
                    if governance_depth_plan
                    else {}
                ),
                "routing_trace": dict(routing_trace),
                "pre_gate_initial_tension": initial_tension,
                "pre_gate_governance_friction": governance_friction,
            }

        def _attach_suppressed_errors(trace: Dict[str, Any]) -> None:
            if self._exc_trace.has_errors:
                trace["suppressed_errors"] = self._build_trace_section(
                    "exception_trace",
                    self._exc_trace.summary(),
                    status="degraded",
                )

        # FAST ROUTE: Bypass all expensive Cloud APIs and Council layers
        if routing_decision.path == RoutingPath.PASS_LOCAL:
            from tonesoul.local_llm import ask_local_llm

            local_response = ask_local_llm(raw_user_message)
            local_dispatch_trace = _base_dispatch_trace()
            local_verdict = {"verdict": "bypassed"}
            local_response, blocked_by_poav, poav_result = self._enforce_poav_gate(
                response=local_response,
                current_zone="safe",
                dispatch_trace=local_dispatch_trace,
                lockdown_active=False,
                source="local_fast_route",
            )
            if poav_result:
                local_verdict["metadata"] = {"poav_gate": poav_result}
            if blocked_by_poav:
                local_verdict["verdict"] = "blocked_by_poav"
                self._apply_repair_trace(
                    dispatch_trace=local_dispatch_trace,
                    original_gate="poav_block",
                    source_text=raw_user_message,
                    output_text=local_response,
                    tension_before=None,
                    fallback_delta=initial_tension,
                    text_tension=initial_tension,
                    stages=["poav_block"],
                    attempt_after_tension=False,
                )
            else:
                local_response, blocked_by_contracts, contract_result = (
                    self._enforce_output_contracts(
                        response=local_response,
                        current_zone="safe",
                        dispatch_trace=local_dispatch_trace,
                    )
                )
                if contract_result:
                    verdict_metadata = local_verdict.get("metadata")
                    if not isinstance(verdict_metadata, dict):
                        verdict_metadata = {}
                    verdict_metadata["contract_observer"] = contract_result
                    local_verdict["metadata"] = verdict_metadata
                if blocked_by_contracts:
                    local_verdict["verdict"] = "blocked_by_contracts"
                    self._apply_repair_trace(
                        dispatch_trace=local_dispatch_trace,
                        original_gate="contract_block",
                        source_text=raw_user_message,
                        output_text=local_response,
                        tension_before=None,
                        fallback_delta=initial_tension,
                        text_tension=initial_tension,
                        stages=["contract_block"],
                        attempt_after_tension=False,
                    )
            _attach_suppressed_errors(local_dispatch_trace)
            self._attach_runtime_governance_observability(local_dispatch_trace)
            return UnifiedResponse(
                response=local_response,
                council_verdict=self._normalize_council_verdict_payload(local_verdict),
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
            _attach_suppressed_errors(dispatch_trace)
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
        if governance_depth_plan.get("skip_cross_session_recovery"):
            user_message = raw_user_message
        else:
            user_message = self._try_cross_session_recovery(raw_user_message)

        # ========== 注入 Adapter（persona + context）==========
        if not governance_depth_plan.get("skip_injection_context"):
            user_message = self.build_injection_context(user_message, persona_config=persona_config)

        # ========== 0. 重建 Third Axiom 狀態 ==========
        # 從歷史記錄重建 commit_stack，確保每次 request 狀態一致
        self._rebuild_stack_from_history(history)

        # ========== 0.5 重建軌跡分析器狀態 ==========
        # 修復對話歷史 bug
        self._rebuild_trajectory_from_history(history)

        # ========== 0.6 Scenario Envelope (Bull/Base/Bear) ==========
        scenario_envelope = self._build_scenario_envelope(user_message, history)

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

                # Phase 544: Drift monitoring (Structure Layer anchor)
                drift_monitor = self._get_drift_monitor()
                if drift_monitor is not None:
                    try:
                        obs = {"deltaT": tone_strength, "deltaS": 0.5, "deltaR": 0.5}
                        if tb_result and tb_result.tone:
                            obs["deltaS"] = getattr(tb_result.tone, "formality", 0.5) or 0.5
                            obs["deltaR"] = getattr(tb_result.tone, "responsibility", 0.5) or 0.5
                        snap = drift_monitor.observe(obs)
                        traj_analysis.drift = snap.drift
                        traj_analysis.drift_alert = snap.alert.value
                    except Exception as e:
                        self._exc_trace.record(
                            "unified_pipeline",
                            "process.trajectory.observe_drift",
                            e,
                        )
                        pass

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
                "scenario_envelope": self._build_trace_section(
                    "scenario_envelope",
                    dict(scenario_envelope),
                    status="ok" if scenario_envelope.get("enabled", True) else "degraded",
                ),
            }
        )
        dispatch_trace["trajectory"] = self._build_trace_section(
            "trajectory",
            dict(trajectory_result),
            status="degraded" if loop_detected else "ok",
        )
        # Phase 544: attach drift summary to dispatch trace
        drift_monitor = self._get_drift_monitor()
        if drift_monitor is not None and drift_monitor.step_count > 0:
            try:
                drift_summary = drift_monitor.summary()
                drift_status = "ok"
                current_alert = (
                    str(drift_summary.get("current_alert") or drift_summary.get("alert") or "")
                    .strip()
                    .lower()
                )
                if current_alert == "warning":
                    drift_status = "degraded"
                elif current_alert in {"crisis", "error"}:
                    drift_status = "error"
                dispatch_trace["drift"] = self._build_trace_section(
                    "drift_monitor",
                    drift_summary,
                    status=drift_status,
                )
                drift_recommendation = drift_summary.get("recommended_action")
                if isinstance(drift_recommendation, dict):
                    dispatch_trace["drift_actions"] = self._build_trace_section(
                        "drift_handler",
                        drift_recommendation,
                        status=drift_status,
                    )
                    trajectory_result["drift_guidance"] = dict(drift_recommendation)
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.dispatch_trace.drift_summary",
                    e,
                )
                pass

        # ========== Governance Reflex Arc ==========
        reflex_decision = self._compute_reflex_decision(initial_tension)
        reflex_force_convene = False
        if reflex_decision is not None:
            reflex_force_convene = getattr(
                reflex_decision, "trigger_reflection", False
            ) and getattr(getattr(reflex_decision, "soul_band", None), "force_council", False)
            self._reflex_gate_modifier = getattr(reflex_decision, "gate_modifier", 1.0)
            reflex_status = "ok"
            reflex_action = str(getattr(reflex_decision, "action", None))
            if "BLOCK" in reflex_action.upper():
                reflex_status = "error"
            elif "SOFTEN" in reflex_action.upper() or "WARN" in reflex_action.upper():
                reflex_status = "degraded"
            dispatch_trace["reflex_arc"] = self._build_trace_section(
                "reflex_arc",
                reflex_decision.to_dict(),
                status=reflex_status,
            )

        # Attach TensionEngine detail to dispatch trace
        if tension_result is not None:
            try:
                tension_detail = tension_result.to_dict()
                dispatch_trace["tension_engine"] = self._build_trace_section(
                    "tension_engine",
                    tension_detail,
                    status="ok",
                )
                dispatch_trace["soul_integral"] = self._build_trace_section(
                    "tension_engine",
                    tension_detail,
                    status="ok",
                )
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.dispatch_trace.tension_engine",
                    e,
                )
                pass
        resistance_trace: Dict[str, Any] = {}
        runtime_friction = self._compute_runtime_friction(
            prior_tension=prior_tension,
            tone_strength=tone_strength,
        )
        if runtime_friction is not None:
            try:
                resistance_trace["friction"] = runtime_friction.to_dict()
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.dispatch_trace.runtime_friction",
                    e,
                )
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
                dispatch_trace["resistance"] = self._build_trace_section(
                    "governance_resistance",
                    resistance_trace,
                    status="error",
                )
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
                _attach_suppressed_errors(dispatch_trace)
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
                    except Exception as e:
                        self._exc_trace.record(
                            "unified_pipeline",
                            "process.dispatch_trace.perturbation_recovery",
                            e,
                        )
                        pass

        if resistance_trace:
            dispatch_trace["resistance"] = self._build_trace_section(
                "governance_resistance",
                resistance_trace,
                status="degraded",
            )

        # ========== 2.4 Phase 545: AlertEscalation — L1/L2/L3 ==========
        alert_event = None
        alert_escalation = self._get_alert_escalation()
        if alert_escalation is not None:
            try:
                # Collect signals from subsystems
                _drift_alert = None
                _dm = self._get_drift_monitor()
                if _dm is not None and _dm.step_count > 0:
                    _drift_alert = _dm.current_alert.value

                _lambda_state = None
                if tension_result is not None:
                    _ls = getattr(tension_result, "lambda_state", None)
                    if _ls is not None:
                        _lambda_state = _ls.value if hasattr(_ls, "value") else str(_ls)

                _cb_status_str = None
                _consecutive = 0
                _cb_data = resistance_trace.get("circuit_breaker")
                if isinstance(_cb_data, dict):
                    _cb_status_str = _cb_data.get("status")
                    _consecutive = _cb_data.get("consecutive_high", 0)

                # JUMP trigger — first live call site
                _jump_triggered = False
                _jump_indicators = 0
                if governance_kernel is not None and tension_result is not None:
                    try:
                        _jump_result = governance_kernel.check_jump_trigger(
                            tension_total=getattr(tension_result, "total", 0.0),
                            has_echo_trace=True,
                            center_delta_norm=0.0,
                            input_norm=max(1.0, float(len(raw_user_message))),
                        )
                        _jump_triggered = bool(_jump_result.get("triggered", False))
                        _jump_indicators = int(_jump_result.get("indicators_tripped", 0))
                        resistance_trace["jump"] = _jump_result
                    except Exception as e:
                        self._exc_trace.record(
                            "unified_pipeline",
                            "process.alert_escalation.jump_trigger",
                            e,
                        )
                        pass

                alert_event = alert_escalation.evaluate(
                    drift_alert=_drift_alert,
                    lambda_state=_lambda_state,
                    circuit_breaker_status=_cb_status_str,
                    jump_triggered=_jump_triggered,
                    jump_indicators_tripped=_jump_indicators,
                    consecutive_high_friction=_consecutive,
                )
                alert_status = "ok"
                if alert_event is not None and not alert_event.is_clear:
                    alert_status = "error" if str(alert_event.level.value) == "L3" else "degraded"
                dispatch_trace["alert"] = self._build_trace_section(
                    "alert_escalation",
                    alert_escalation.summary(),
                    status=alert_status,
                )
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.alert_escalation.evaluate",
                    e,
                )
                pass

        if resistance_trace:
            dispatch_trace["resistance"] = self._build_trace_section(
                "governance_resistance",
                resistance_trace,
                status="degraded",
            )
        trajectory_result["dispatch"] = dispatch_trace
        # ========== 2.5 ToneSoul 2.0: 內在審議 ==========
        deliberation = self._get_deliberation()
        deliberation_result = None
        persona_mode = "Philosopher"  # 預設模式
        internal_monologue = ""
        deliberation_trace: Dict[str, Any] = {
            "enabled": True,
            "available": bool(deliberation),
            "used": False,
            "fallback": False,
            "reason": "engine_unavailable" if not deliberation else "",
            "dominant_voice": "",
            "persona_mode": persona_mode,
            "context": {
                "tone_strength": round(float(tone_strength), 4),
                "resonance_state": str(resonance_state or ""),
                "loop_detected": bool(loop_detected),
                "history_turns": len(history),
                "scenario_envelope": dict(scenario_envelope),
            },
        }

        if deliberation:
            try:
                from tonesoul.deliberation import DeliberationContext
                from tonesoul.deliberation.adaptive_rounds import calculate_debate_rounds

                context = DeliberationContext(
                    user_input=user_message,
                    conversation_history=history,
                    tone_strength=tone_strength,
                    resonance_state=resonance_state,
                    loop_detected=loop_detected,
                    scenario_envelope=dict(scenario_envelope),
                )
                deliberation_result = deliberation.deliberate_sync(context)
                deliberation_trace["used"] = True
                deliberation_trace["reason"] = "deliberation_applied"
                rounds_used = int(getattr(deliberation_result, "rounds_used", 1) or 1)
                round_results = list(getattr(deliberation_result, "round_results", []) or [])
                deliberation_trace["rounds_used"] = rounds_used
                dispatch_trace["deliberation_rounds"] = rounds_used

                if rounds_used > 1:
                    tensions_per_round = [
                        round(float(getattr(round_result, "aggregate_tension", 0.0) or 0.0), 4)
                        for round_result in round_results
                    ]
                    initial_tensions = []
                    if round_results:
                        initial_tensions = list(getattr(round_results[0], "tensions", []) or [])
                    elif hasattr(deliberation_result, "tensions"):
                        initial_tensions = list(getattr(deliberation_result, "tensions", []) or [])
                    planned_rounds = calculate_debate_rounds(initial_tensions)
                    debate_converged_early = rounds_used < planned_rounds
                    deliberation_trace["tensions_per_round"] = tensions_per_round
                    deliberation_trace["debate_converged_early"] = debate_converged_early
                    dispatch_trace["tensions_per_round"] = tensions_per_round
                    dispatch_trace["debate_converged_early"] = debate_converged_early

                # 從審議結果獲取 persona 和 monologue
                if deliberation_result.dominant_voice:
                    voice_map = {"muse": "Philosopher", "logos": "Engineer", "aegis": "Guardian"}
                    dominant_voice = str(deliberation_result.dominant_voice.value)
                    deliberation_trace["dominant_voice"] = dominant_voice
                    persona_mode = voice_map.get(dominant_voice, "Philosopher")
                    deliberation_trace["persona_mode"] = persona_mode
                else:
                    deliberation_trace["reason"] = "no_dominant_voice"

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
                if internal_monologue:
                    deliberation_trace["monologue_excerpt"] = internal_monologue[:160]

            except Exception as e:
                print(f"Deliberation error: {e}")
                # Fallback dispatch mapping
                dispatch_state = dispatch_trace.get("state", "A")
                persona_mode = self._fallback_persona_mode(
                    str(dispatch_state), str(resonance_state)
                )
                internal_monologue = "Fallback to deterministic persona mapping."
                deliberation_trace["fallback"] = True
                deliberation_trace["reason"] = f"error:{e.__class__.__name__}"
                deliberation_trace["persona_mode"] = persona_mode
                deliberation_trace["monologue_excerpt"] = internal_monologue[:160]

        deliberation_status = "ok"
        if deliberation_trace.get("fallback"):
            deliberation_status = "degraded"
        dispatch_trace["deliberation"] = self._build_trace_section(
            "deliberation",
            dict(deliberation_trace),
            status=deliberation_status,
        )
        trajectory_result["deliberation"] = dict(deliberation_trace)

        # ========== 2.6 Phase 545: L2/L3 graduated response ==========
        _alert_preamble = ""
        _lockdown_active = False
        if alert_event is not None and not alert_event.is_clear:
            from tonesoul.alert_escalation import AlertLevel

            if alert_event.level == AlertLevel.L3:
                # Seabed-grade degradation: Guardian only, minimal output
                persona_mode = "Guardian"
                _lockdown_active = True
                _alert_preamble = (
                    "[系統防護 L3] 偵測到系統性異常，已切換至 Seabed 安全模式。"
                    "僅執行 Verify / Cite / Inquire 操作。"
                    f"原因：{'; '.join(alert_event.reasons)}"
                )
                internal_monologue = (
                    f"L3 systemic alert: {'; '.join(alert_event.reasons)}. "
                    "Entering Seabed Lockdown — Guardian-only response."
                )
            elif alert_event.level == AlertLevel.L2:
                # Structural warning: annotate but continue
                _alert_preamble = "[結構層警告 L2] " f"{'; '.join(alert_event.reasons)}"
                internal_monologue = (
                    f"L2 structure alert: {'; '.join(alert_event.reasons)}. "
                    "Structural updates frozen; proceeding with caution."
                ) + (f" (prior: {internal_monologue})" if internal_monologue else "")

        if _lockdown_active:
            from tonesoul.action_set import ACTION_POLICY

            dispatch_trace["action_set"] = self._build_trace_section(
                "action_set",
                {
                    "mode": "lockdown",
                    "allowed_actions": list(ACTION_POLICY.get("lockdown", [])),
                },
                status="degraded",
            )

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
        user_message, graph_rag_trace = self._inject_graph_rag_context(
            user_message, tb_result=tb_result
        )
        dispatch_trace["graph_rag"] = self._build_trace_section(
            "graph_rag",
            dict(graph_rag_trace),
            status="ok" if graph_rag_trace.get("applied") else "degraded",
        )
        trajectory_result["graph_rag"] = dict(graph_rag_trace)

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
                memory_correction_trace = {
                    "primary_hits": len(primary_results or []),
                    "corrective_hits": len(corrective_results or []),
                    "enabled": bool(self._enable_corrective_recall),
                }
                if corrective_vector_norm is not None:
                    memory_correction_trace["b_vec_norm"] = round(
                        corrective_vector_norm,
                        6,
                    )
                dispatch_trace["memory_correction"] = self._build_trace_section(
                    "memory_correction",
                    memory_correction_trace,
                    status="ok",
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
            tb_result,
            persona_mode,
            trajectory_result,
            commitment_prompt,
            lockdown_active=_lockdown_active,
        )

        # ========== 4. LLM 生成回應 ==========
        router = self._get_llm_router()
        llm_client = self._get_llm_client()
        response = ""
        suggested_replies = []
        thinking_tier = None
        if llm_client:
            try:
                from tonesoul.llm.router import resolve_thinking_tier

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
                    except Exception as e:
                        self._exc_trace.record(
                            "unified_pipeline",
                            "process.llm.delay",
                            e,
                        )
                        pass

                if router is not None:
                    try:
                        router.prime(llm_client, backend=self._llm_backend)
                    except Exception as e:
                        self._exc_trace.record(
                            "unified_pipeline",
                            "process.llm.router_prime",
                            e,
                        )
                        pass
                    chat_with_tier = getattr(router, "chat_with_tier", None)
                    requested_tier = resolve_thinking_tier(
                        getattr(alert_event, "level", None) if alert_event is not None else None
                    )
                    if callable(chat_with_tier):
                        response = chat_with_tier(
                            history=history,
                            prompt=full_prompt,
                            alert_level=(
                                getattr(alert_event, "level", None)
                                if alert_event is not None
                                else None
                            ),
                        )
                        thinking_tier = getattr(router, "last_thinking_tier", None)
                    else:
                        response = router.chat(history=history, prompt=full_prompt)
                    if not thinking_tier:
                        thinking_tier = requested_tier.value
                else:
                    llm_client.start_chat(history)
                    response = llm_client.send_message(full_prompt)
                    thinking_tier = resolve_thinking_tier(
                        getattr(alert_event, "level", None) if alert_event is not None else None
                    ).value
                dispatch_trace["thinking_tier"] = thinking_tier
                observability_client = llm_client
                if router is not None:
                    try:
                        observability_client = router.get_client() or llm_client
                    except Exception:
                        observability_client = llm_client
                self._attach_llm_observability(
                    dispatch_trace=dispatch_trace,
                    llm_client=observability_client,
                )
            except Exception as e:
                response = f"抱歉，生成回應時發生錯誤：{e}"
        else:
            response = "抱歉，LLM 服務不可用。"

        # ========== 6. Reflection Loop + Council 審議 ==========
        council = self._get_council()
        verdict_dict = {}
        repair_stages: List[str] = []
        council_should_convene, council_reason, council_friction_score = (
            self._resolve_council_decision(
                tone_strength=tone_strength,
                runtime_friction=runtime_friction,
                governance_friction=governance_friction,
                user_tier=user_tier,
                user_message=raw_user_message,
                force_convene=reflex_force_convene,
            )
        )
        if council_reason or council_friction_score is not None:
            dispatch_trace["council"] = self._build_trace_section(
                "council",
                {
                    "convened": bool(council and council_should_convene),
                    "reason": council_reason,
                    "friction_score": council_friction_score,
                },
                status="degraded" if council and council_should_convene else "ok",
            )
        reflection_verdicts: List[Any] = []
        reflection_tiers: List[str] = []
        revision_count = 0
        final_reflection_verdict = None
        reflection_context = {
            "language": "zh",
            "tension_score": tone_strength,
            "reflection_confidence": (getattr(tb_result, "confidence", 0.8) if tb_result else 0.8),
            "prior_tension": prior_tension if isinstance(prior_tension, dict) else {},
            "reflection_skip_council": not bool(council and council_should_convene),
            "raw_user_message": raw_user_message,
        }
        try:
            from tonesoul.llm.router import ThinkingTier
            from tonesoul.reflection import (
                MAX_REVISIONS,
                VERIFICATION_BUDGET,
                VERIFICATION_BUDGET_EXCEEDED_MSG,
                ReflectionStats,
                ReflectionVerdict,
                build_revision_prompt,
            )

            # Phase 852: Track total LLM calls for fail-stop budget.
            # The initial LLM call counts as 1; each revision adds 1 more.
            _llm_call_count = 1  # initial generation already consumed 1
            _budget_exceeded = False

            while revision_count < MAX_REVISIONS:
                try:
                    current_verdict = self._self_check(response, reflection_context)
                except Exception as e:
                    self._exc_trace.record(
                        "unified_pipeline",
                        "process.reflection_loop.self_check",
                        e,
                    )
                    break

                reflection_verdicts.append(current_verdict)
                if not current_verdict.should_revise:
                    break

                # Phase 852: Check verification budget before spending another LLM call
                if _llm_call_count >= VERIFICATION_BUDGET:
                    _budget_exceeded = True
                    break

                revision_prompt = build_revision_prompt(response, current_verdict)
                revision_tier = (
                    ThinkingTier.CLOUD
                    if thinking_tier == ThinkingTier.CLOUD.value or current_verdict.severity >= 0.5
                    else ThinkingTier.LOCAL
                )
                try:
                    if router is not None:
                        chat_with_tier = getattr(router, "chat_with_tier", None)
                        if callable(chat_with_tier):
                            response = chat_with_tier(
                                history=history,
                                prompt=revision_prompt,
                                tier=revision_tier,
                            )
                            reflection_tiers.append(
                                getattr(router, "last_thinking_tier", None) or revision_tier.value
                            )
                        else:
                            response = router.chat(history=history, prompt=revision_prompt)
                            reflection_tiers.append(revision_tier.value)
                    elif llm_client is not None:
                        llm_client.start_chat(history)
                        response = llm_client.send_message(revision_prompt)
                        reflection_tiers.append(revision_tier.value)
                    else:
                        break
                    revision_count += 1
                    _llm_call_count += 1
                    observability_client = llm_client
                    if router is not None:
                        try:
                            observability_client = router.get_client() or llm_client
                        except Exception:
                            observability_client = llm_client
                    self._attach_llm_observability(
                        dispatch_trace=dispatch_trace,
                        llm_client=observability_client,
                    )
                except Exception as e:
                    self._exc_trace.record(
                        "unified_pipeline",
                        "process.reflection_loop.revision_chat",
                        e,
                    )
                    break

            final_reflection_verdict = (
                reflection_verdicts[-1]
                if reflection_verdicts
                else ReflectionVerdict(should_revise=False)
            )
            reflection_status = "ok"
            if final_reflection_verdict.should_revise:
                reflection_status = (
                    "error" if final_reflection_verdict.severity >= 0.8 else "degraded"
                )
            reflection_stats = ReflectionStats(
                total_revisions=revision_count,
                local_revisions=sum(1 for tier in reflection_tiers if tier == "local"),
                cloud_revisions=sum(1 for tier in reflection_tiers if tier == "cloud"),
                final_severity=float(final_reflection_verdict.severity),
                verdicts=[
                    verdict
                    for verdict in reflection_verdicts
                    if isinstance(verdict, ReflectionVerdict)
                ],
            )
            dispatch_trace["reflection_count"] = revision_count
            dispatch_trace["reflection_verdicts"] = [
                verdict.to_dict() if hasattr(verdict, "to_dict") else {}
                for verdict in reflection_verdicts
            ]
            dispatch_trace["reflection_tiers"] = list(reflection_tiers)
            dispatch_trace["reflection_stats"] = self._build_trace_section(
                "reflection_stats",
                reflection_stats.to_dict(),
                status=reflection_status,
            )
            dispatch_trace["reflection_verdict"] = self._build_trace_section(
                "reflection",
                final_reflection_verdict.to_dict(),
                status=reflection_status,
            )

            # Phase 852: Verification over-budget fail-stop
            if _budget_exceeded and final_reflection_verdict.should_revise:
                dispatch_trace["verification_budget"] = self._build_trace_section(
                    "verification_budget",
                    {
                        "budget": VERIFICATION_BUDGET,
                        "llm_calls_used": _llm_call_count,
                        "converged": False,
                        "final_severity": round(final_reflection_verdict.severity, 4),
                    },
                    status="error",
                )
                response = f"{response}\n\n---\n{VERIFICATION_BUDGET_EXCEEDED_MSG}"
        except Exception as e:
            self._exc_trace.record(
                "unified_pipeline",
                "process.reflection_loop",
                e,
            )
            pass

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
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.resonance.predict",
                    e,
                )
                pass

        # ========== 11. 產生內部敘事摘要 ==========
        inner_narrative = self._generate_narrative(tb_result, verdict_dict)
        if _alert_preamble:
            inner_narrative = f"{_alert_preamble}\n{inner_narrative}"

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
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.commit_stack.get_recent",
                    e,
                )
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
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.value_accumulator.get_active_values",
                    e,
                )
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

        # Phase 539: feed post-council outcome back into persona track record
        try:
            dominant_voice = str(deliberation_trace.get("dominant_voice", "") or "").strip()
            verdict_name = str(
                verdict_dict.get("verdict", "") if isinstance(verdict_dict, dict) else ""
            )
            if dominant_voice and verdict_name:
                deliberation = self._get_deliberation()
                if deliberation is not None and hasattr(deliberation, "record_outcome"):
                    deliberation.record_outcome(
                        dominant_voice=dominant_voice,
                        verdict=verdict_name,
                        resonance_state=str(resonance_state or "unknown"),
                        loop_detected=bool(loop_detected),
                    )
                    if hasattr(deliberation, "get_persona_track_summary"):
                        deliberation_trace["persona_track_summary"] = (
                            deliberation.get_persona_track_summary()
                        )
                        dispatch_trace["deliberation"] = self._build_trace_section(
                            "deliberation",
                            dict(deliberation_trace),
                            status="degraded" if deliberation_trace.get("fallback") else "ok",
                        )
                        trajectory_result["deliberation"] = dict(deliberation_trace)
        except Exception as e:
            self._exc_trace.record(
                "unified_pipeline",
                "process.deliberation.record_outcome",
                e,
            )
            pass

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
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.visual_chain.capture",
                    e,
                )
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
        except Exception as e:
            self._exc_trace.record(
                "unified_pipeline",
                "process.persona_dimension",
                e,
            )
            pass

        response = self._apply_mirror_step(
            response,
            dispatch_trace=dispatch_trace,
            trajectory_result=trajectory_result,
            user_tier=user_tier,
            tone_strength=tone_strength,
            confidence=(getattr(tb_result, "confidence", 0.8) if tb_result else 0.8),
        )

        # ========== Reflex Arc Final Gate ==========
        final_reflex_decision = reflex_decision
        final_council_signal = verdict_dict
        if not final_council_signal and final_reflection_verdict is not None:
            final_council_signal = getattr(final_reflection_verdict, "council_decision", None)
        final_vow_result = (
            getattr(final_reflection_verdict, "vow_result", None)
            if final_reflection_verdict is not None
            else None
        )
        if final_vow_result is not None or final_council_signal:
            final_reflex_decision = self._compute_reflex_decision(
                max(float(tone_strength or 0.0), float(initial_tension or 0.0)),
                vow_result=final_vow_result,
                council_verdict=final_council_signal,
            )
            if final_reflex_decision is not None:
                final_reflex_status = "ok"
                final_reflex_action = str(getattr(final_reflex_decision, "action", None))
                if "BLOCK" in final_reflex_action.upper():
                    final_reflex_status = "error"
                elif (
                    "SOFTEN" in final_reflex_action.upper() or "WARN" in final_reflex_action.upper()
                ):
                    final_reflex_status = "degraded"
                dispatch_trace["reflex_arc_final"] = self._build_trace_section(
                    "reflex_arc_final",
                    final_reflex_decision.to_dict(),
                    status=final_reflex_status,
                )
        if final_reflex_decision is not None:
            response = self._apply_reflex_final_gate(response, final_reflex_decision, repair_stages)

        current_zone = getattr(getattr(tension_result, "zone", None), "value", "safe")
        response, blocked_by_poav, poav_result = self._enforce_poav_gate(
            response=response,
            current_zone=current_zone,
            dispatch_trace=dispatch_trace,
            lockdown_active=_lockdown_active,
            source="unified_pipeline",
        )
        if poav_result and isinstance(verdict_dict, dict):
            verdict_metadata = verdict_dict.get("metadata")
            if not isinstance(verdict_metadata, dict):
                verdict_metadata = {}
            verdict_metadata["poav_gate"] = poav_result
            verdict_dict["metadata"] = verdict_metadata
        if blocked_by_poav:
            repair_stages.append("poav_block")
            if isinstance(verdict_dict, dict):
                verdict_dict["verdict"] = "blocked_by_poav"
        else:
            response, blocked_by_contracts, contract_result = self._enforce_output_contracts(
                response=response,
                current_zone=current_zone,
                dispatch_trace=dispatch_trace,
            )
            if contract_result and isinstance(verdict_dict, dict):
                verdict_metadata = verdict_dict.get("metadata")
                if not isinstance(verdict_metadata, dict):
                    verdict_metadata = {}
                verdict_metadata["contract_observer"] = contract_result
                verdict_dict["metadata"] = verdict_metadata
            if blocked_by_contracts:
                repair_stages.append("contract_block")
                if isinstance(verdict_dict, dict):
                    verdict_dict["verdict"] = "blocked_by_contracts"

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

        # ========== 12. 更新 Trajectory 歷史 ==========
        if trajectory:
            tone_state = trajectory_result.get("resonance_state", "resonance")
            trajectory.add_turn(user_message, response, tone_state)

        if isinstance(verdict_dict, dict):
            verdict_metadata = verdict_dict.get("metadata")
            if not isinstance(verdict_metadata, dict):
                verdict_metadata = {}
            verdict_metadata["dispatch_state"] = dispatch_trace.get("state")
            verdict_metadata["dispatch"] = dispatch_trace
            verdict_dict["metadata"] = verdict_metadata

        dispatch_trace["trajectory"] = self._build_trace_section(
            "trajectory",
            {key: value for key, value in trajectory_result.items() if key != "dispatch"},
            status="degraded" if loop_detected else "ok",
        )
        self._attach_runtime_governance_observability(dispatch_trace)

        # Persist cumulative tension integral (Ψ) across sessions
        te = self._get_tension_engine()
        if te is not None:
            try:
                te.save_persistence()
            except Exception as e:
                self._exc_trace.record(
                    "unified_pipeline",
                    "process.tension_engine.save_persistence",
                    e,
                )
                pass

        _attach_suppressed_errors(dispatch_trace)

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
        lockdown_active: bool = False,
    ) -> str:
        """Build runtime context prompt for the LLM call."""
        lines: List[str] = []
        lines.extend(
            [
                "Runtime context frame",
                "Goal: respond with bounded, evidence-aware guidance using the current runtime context as support, not as hidden law.",
                "P0: user-visible evidence, active safety restrictions, and explicit task constraints outrank historical or advisory hints.",
                "P1: commitments, trajectory, tone, and motive cues are bounded reminders; if they conflict with current evidence, surface the conflict instead of silently inheriting them.",
                "Recovery: if the runtime context is incomplete, stale, or internally conflicting, ask a clarifying question or state the uncertainty instead of inventing continuity.",
                f"Persona mode: {persona_mode}",
            ]
        )

        if commitment_prompt:
            lines.append("Recent commitments (advisory reminders):")
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

        if lockdown_active:
            from tonesoul.action_set import ACTION_POLICY

            allowed = ACTION_POLICY.get("lockdown", ["verify", "cite", "inquire"])
            lines.append("")
            lines.append("[SEABED LOCKDOWN ACTIVE]")
            lines.append(
                "System is in Seabed safety mode. " f"Allowed actions: {', '.join(allowed)}."
            )
            lines.append(
                "Do NOT generate creative, speculative, or exploratory content. "
                "Respond only with verifiable facts, cited sources, or clarifying questions."
            )

        # Governance drift guidance (injected by reflex arc)
        drift_lines = self._build_drift_guidance()
        if drift_lines:
            lines.append("")
            lines.extend(drift_lines)

        lines.append(
            "Output: reply with factual, concise, and safe guidance. If context support is thin, say so explicitly before proceeding."
        )
        return "\n".join(lines)

    def _build_drift_guidance(self) -> List[str]:
        """Build LLM prompt lines from baseline drift signals.

        Reads the current governance posture's drift and the reflex arc's
        evaluation to inject caution/risk guidance into the LLM context.
        This is where baseline_drift finally influences behavior.
        """
        try:
            from tonesoul.governance.reflex import evaluate_drift
            from tonesoul.runtime_adapter import load as load_posture

            posture = load_posture()
            drift = dict(getattr(posture, "baseline_drift", {}) or {})
            if not drift:
                return []

            signal = evaluate_drift(drift)
            lines: List[str] = []

            if signal.inject_risk_prompt:
                lines.append("[GOVERNANCE DRIFT: HIGH CAUTION]")
                lines.append(
                    f"Baseline caution bias is elevated ({signal.caution_bias:.2f}). "
                    "Prioritize safety, cite sources, and flag uncertainty explicitly. "
                    "Avoid speculative or high-risk recommendations."
                )
            elif signal.inject_caution_prompt:
                lines.append("[GOVERNANCE DRIFT: CAUTION ADVISORY]")
                lines.append(
                    f"Baseline caution is above normal ({signal.caution_bias:.2f}). "
                    "Be methodical and prefer conservative approaches."
                )

            if signal.autonomy_capped:
                lines.append(
                    "[AUTONOMY CAPPED] Autonomy level exceeds soul band limit. "
                    "Defer to operator judgment on ambiguous decisions."
                )

            return lines
        except Exception:
            return []

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
