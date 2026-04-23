"""
ToneSoul Governance Kernel — the decision core of the governance layer.

This module extracts governance responsibilities from unified_pipeline.py
into a cohesive, testable, and independently addressable kernel.

Responsibilities:
  1. LLM backend routing (which model to use)
  2. Council convening decisions (should we deliberate?)
  3. Friction calculation (RFC-012)
  4. Circuit breaker management
  5. Decision provenance recording
  6. Runtime governance observability

Design:
  The kernel does NOT generate responses. It *decides* how the pipeline
  should behave, then the pipeline executes. This separation ensures
  governance logic is auditable and replaceable without touching the
  orchestration layer.

Author: Antigravity
Date: 2026-03-07
Lineage: Antigravity (2026-03 · kernel extraction)
       → 黃梵威 / Fan-Wei Huang (2026-04 · stewardship · 語魂系統)

  當前方是懸崖，它不會因為怕你生氣就說「路況良好」。
  — 語魂 ToneSoul · principle engineering · 2026-04
"""

from __future__ import annotations

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Governance kernel: decides how the pipeline behaves (routing, council convening, friction)."
)

import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from tonesoul import schemas as governance_schemas
from tonesoul.exception_trace import ExceptionTrace

GovernanceDecision = governance_schemas.GovernanceDecision
DispatchTraceSection = governance_schemas.DispatchTraceSection
LLMRouteDecision = governance_schemas.LLMRouteDecision

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Governance Kernel
# ---------------------------------------------------------------------------


class GovernanceKernel:
    """
    The decision core of ToneSoul's governance layer.

    Extracted from unified_pipeline.py to give governance logic
    a clear boundary, testable interface, and its own identity.
    """

    def __init__(self) -> None:
        self._friction_calculator = None
        self._circuit_breaker = None
        self._perturbation_recovery = None
        self._jump_monitor = None
        self._exc_trace = ExceptionTrace()

    # --- JUMP Engine (Vol-5 §2) ---

    def _get_jump_monitor(self):
        if self._jump_monitor is None:
            from tonesoul.jump_monitor import JumpMonitor

            self._jump_monitor = JumpMonitor()
        return self._jump_monitor

    def check_jump_trigger(
        self,
        tension_total: float = 0.0,
        has_echo_trace: bool = True,
        center_delta_norm: float = 0.0,
        input_norm: float = 1.0,
    ) -> Dict[str, Any]:
        """Record latest output metrics and check for singularity.

        Returns a dict with ``triggered``, ``status``, and ``reason`` keys.
        """
        monitor = self._get_jump_monitor()
        monitor.record_output(
            tension_total=tension_total,
            has_echo_trace=has_echo_trace,
            center_delta_norm=center_delta_norm,
            input_norm=input_norm,
        )
        signal = monitor.check_singularity()
        return {
            "triggered": signal.triggered,
            "status": monitor.status.value,
            "reason": signal.reason,
            "reasoning_convergence": signal.reasoning_convergence,
            "chain_integrity": signal.chain_integrity,
            "self_reference_ratio": signal.self_reference_ratio,
            "indicators_tripped": signal.indicators_tripped,
        }

    # --- LLM Routing ---

    def resolve_llm_backend(
        self,
        *,
        preferred_backend: str = "auto",
        existing_client: Any = None,
    ) -> LLMRouteDecision:
        """
        Determine which LLM backend to use.

        Supports:
          - "gemini"   → Cloud mode, skip local entirely
          - "ollama"   → Local mode, skip cloud entirely
          - "lmstudio" → LM Studio local mode
          - "auto"     → Ollama → LMStudio → Gemini (waterfall fallback)

        Args:
            preferred_backend: Backend preference (env LLM_BACKEND or explicit).
            existing_client: If a client is already initialized, reuse it.

        Returns:
            LLMRouteDecision with the selected backend and client.
        """
        if existing_client is not None:
            return LLMRouteDecision(
                backend="existing",
                client=existing_client,
                reason="Reusing pre-initialized client",
            )

        mode = (os.environ.get("LLM_BACKEND") or preferred_backend or "auto").strip().lower()

        if mode == "gemini":
            return self._try_gemini("Explicit gemini mode requested")

        if mode == "ollama":
            return self._try_ollama("Explicit ollama mode requested")

        if mode == "lmstudio":
            return self._try_lmstudio("Explicit lmstudio mode requested")

        # Auto mode: waterfall fallback
        for attempt_fn, label in [
            (self._try_ollama, "Auto: Ollama first"),
            (self._try_lmstudio, "Auto: LMStudio fallback"),
            (self._try_gemini, "Auto: Gemini final fallback"),
        ]:
            decision = attempt_fn(label)
            if decision.client is not None:
                return decision

        return LLMRouteDecision(
            backend="none",
            client=None,
            reason="All LLM backends unavailable",
        )

    def _try_ollama(self, reason: str) -> LLMRouteDecision:
        try:
            from tonesoul.llm import create_ollama_client

            client = create_ollama_client()
            if client.is_available() and client.list_models():
                return LLMRouteDecision(backend="ollama", client=client, reason=reason)
        except Exception as e:
            self._exc_trace.record("governance_kernel", "_try_ollama", e)
            pass
        return LLMRouteDecision(backend="ollama", client=None, reason=f"{reason} (failed)")

    def _try_lmstudio(self, reason: str) -> LLMRouteDecision:
        try:
            from tonesoul.llm.lmstudio_client import create_lmstudio_client

            client = create_lmstudio_client()
            if client.is_available():
                return LLMRouteDecision(backend="lmstudio", client=client, reason=reason)
        except Exception as e:
            self._exc_trace.record("governance_kernel", "_try_lmstudio", e)
            pass
        return LLMRouteDecision(backend="lmstudio", client=None, reason=f"{reason} (failed)")

    def _try_gemini(self, reason: str) -> LLMRouteDecision:
        try:
            from tonesoul.llm import create_gemini_client

            client = create_gemini_client()
            return LLMRouteDecision(backend="gemini", client=client, reason=reason)
        except Exception as e:
            self._exc_trace.record("governance_kernel", "_try_gemini", e)
            pass
        return LLMRouteDecision(backend="gemini", client=None, reason=f"{reason} (failed)")

    # --- Council Convening ---

    def should_convene_council(
        self,
        *,
        tension: float,
        friction_score: Optional[float] = None,
        user_tier: str = "free",
        message_length: int = 0,
        min_council_tension: float = 0.4,
        min_council_friction: float = 0.62,
        force_convene: bool = False,
    ) -> tuple[bool, str]:
        """
        Decide whether the Council should be convened for this turn.

        Args:
            force_convene: If True, always convene (set by reflex arc
                when soul_integral is in strained/critical band).

        Returns:
            (should_convene, reason)
        """
        if force_convene:
            return True, "Forced by governance reflex arc (soul band strained/critical)"

        effective_tension = max(0.0, min(1.0, float(tension)))

        if isinstance(friction_score, (int, float)):
            friction_score = max(0.0, min(1.0, float(friction_score)))
            effective_tension = max(effective_tension, friction_score)

        # High friction → always convene
        if friction_score is not None and friction_score >= min_council_friction:
            return True, (
                f"High governance friction ({friction_score:.2f}) "
                f"exceeds threshold ({min_council_friction})"
            )

        # High tension → convene
        if effective_tension >= min_council_tension:
            return True, (
                f"Tension ({effective_tension:.2f}) " f"exceeds threshold ({min_council_tension})"
            )

        return False, f"Tension ({effective_tension:.2f}) below threshold, council not needed"

    # --- Friction Calculation ---

    def _get_friction_calculator(self):
        if self._friction_calculator is None:
            try:
                from tonesoul.resistance import FrictionCalculator

                self._friction_calculator = FrictionCalculator()
            except Exception as e:
                self._exc_trace.record("governance_kernel", "_get_friction_calculator", e)
                pass
        return self._friction_calculator

    def _get_circuit_breaker(self):
        if self._circuit_breaker is None:
            try:
                from tonesoul.resistance import CircuitBreaker

                self._circuit_breaker = CircuitBreaker()
            except Exception as e:
                self._exc_trace.record("governance_kernel", "_get_circuit_breaker", e)
                pass
        return self._circuit_breaker

    def _get_perturbation_recovery(self):
        if self._perturbation_recovery is None:
            try:
                from tonesoul.resistance import PerturbationRecovery

                self._perturbation_recovery = PerturbationRecovery()
            except Exception as e:
                self._exc_trace.record("governance_kernel", "_get_perturbation_recovery", e)
                pass
        return self._perturbation_recovery

    def compute_prior_governance_friction(
        self,
        prior_tension: Optional[Dict[str, Any]],
        user_message: str,
    ) -> Optional[float]:
        """Compute governance friction from prior turn's tension state."""
        if not isinstance(prior_tension, dict) or not prior_tension:
            return None

        from tonesoul.gates.compute import ComputeGate

        query_tension = _safe_unit_value(prior_tension.get("query_tension"))
        memory_tension = _safe_unit_value(prior_tension.get("memory_tension"))
        delta_t = _safe_unit_value(prior_tension.get("delta_t"))

        if query_tension is None and delta_t is not None:
            query_tension = delta_t
        if memory_tension is None and delta_t is not None:
            memory_tension = 0.0

        query_wave = prior_tension.get("query_wave")
        if not isinstance(query_wave, dict):
            query_wave = None

        memory_wave = prior_tension.get("memory_wave")
        if not isinstance(memory_wave, dict):
            memory_wave = prior_tension.get("wave")
        if not isinstance(memory_wave, dict):
            memory_wave = None

        gate_decision = str(prior_tension.get("gate_decision") or "").strip().lower()
        was_boundary = gate_decision in {"block", "declare_stance", "reject", "refuse"}
        boundary_mismatch = was_boundary and _contains_override_pressure(user_message)

        return ComputeGate.compute_governance_friction(
            query_tension=query_tension,
            memory_tension=memory_tension,
            query_wave=query_wave,
            memory_wave=memory_wave,
            boundary_mismatch=boundary_mismatch,
        )

    def compute_runtime_friction(
        self,
        *,
        prior_tension: Optional[Dict[str, Any]],
        tone_strength: float,
    ) -> Optional[Any]:
        """Build RFC-012 friction input from runtime context."""
        if not isinstance(prior_tension, dict) or not prior_tension:
            return None

        calculator = self._get_friction_calculator()
        if calculator is None:
            return None

        query_tension = _safe_unit_value(prior_tension.get("query_tension"))
        if query_tension is None:
            query_tension = max(0.0, min(1.0, float(tone_strength)))

        constraint_tension = _safe_unit_value(prior_tension.get("memory_tension"))
        if constraint_tension is None:
            constraint_tension = _safe_unit_value(prior_tension.get("delta_t"))
        if constraint_tension is None:
            constraint_tension = 0.0

        query_wave = prior_tension.get("query_wave")
        if not isinstance(query_wave, dict):
            query_wave = None

        constraint_wave = prior_tension.get("memory_wave")
        if not isinstance(constraint_wave, dict):
            constraint_wave = prior_tension.get("wave")
        if not isinstance(constraint_wave, dict):
            constraint_wave = None

        gate_decision = str(prior_tension.get("gate_decision") or "").strip().lower()
        raw_kind = prior_tension.get("constraint_kind")
        constraint_kind = (
            str(raw_kind).strip().lower()
            if isinstance(raw_kind, str) and raw_kind.strip()
            else ("constraint" if gate_decision else "note")
        )

        is_immutable = _safe_bool(prior_tension.get("is_immutable"))
        if is_immutable is None:
            is_immutable = gate_decision in {"block", "declare_stance", "reject", "refuse"}

        try:
            return calculator.compute(
                query_tension=query_tension,
                constraint_tension=constraint_tension,
                query_wave=query_wave,
                constraint_wave=constraint_wave,
                constraint_kind=constraint_kind,
                is_immutable=is_immutable,
            )
        except Exception as e:
            self._exc_trace.record("governance_kernel", "compute_runtime_friction", e)
            return None

    # --- Circuit Breaker ---

    def check_circuit_breaker(
        self,
        friction_result: Any,
        *,
        lyapunov_exponent: Optional[float] = None,
    ) -> tuple[str, Optional[str], Dict[str, Any]]:
        """
        Check if the circuit breaker should freeze processing.

        Returns:
            (status, reason, state) where status is "ok" or "frozen"
        """
        breaker = self._get_circuit_breaker()
        if breaker is None or friction_result is None:
            return "ok", None, {}

        try:
            breaker.check(friction_result, lyapunov_exponent=lyapunov_exponent)
            state = breaker.state.to_dict()
            state["status"] = "ok"
            if isinstance(lyapunov_exponent, (int, float)):
                state["lyapunov_exponent"] = round(float(lyapunov_exponent), 6)
            return "ok", None, state
        except Exception as exc:
            from tonesoul.resistance import CollapseException

            if isinstance(exc, CollapseException):
                state = breaker.state.to_dict()
                reason = str(getattr(exc, "reason", str(exc))).strip() or None
                state["status"] = "frozen"
                state["reason"] = reason
                if isinstance(lyapunov_exponent, (int, float)):
                    state["lyapunov_exponent"] = round(float(lyapunov_exponent), 6)
                return "frozen", reason, state
            return "ok", None, {}

    def recover_perturbation(
        self,
        *,
        compression_ratio: float,
        gamma_effective: Optional[float],
        friction: Any,
    ) -> Optional[Any]:
        """Delegate perturbation recovery path selection."""
        recovery = self._get_perturbation_recovery()
        if recovery is None:
            return None

        try:
            return recovery.recover(
                compression_ratio=float(compression_ratio),
                gamma_effective=gamma_effective,
                friction=friction,
            )
        except Exception as e:
            self._exc_trace.record("governance_kernel", "recover_perturbation", e)
            return None

    # --- Runtime Governance Observability ---

    def build_routing_trace(
        self,
        *,
        route: Any,
        journal_eligible: Any,
        reason: Any,
        governance_depth: Any = None,
        governance_depth_plan: Any = None,
    ) -> DispatchTraceSection:
        """Build the canonical routing-trace payload used by orchestration layers."""
        detail = {
            "route": str(route or "").strip(),
            "journal_eligible": bool(journal_eligible),
            "reason": str(reason or ""),
        }
        normalized_depth = str(governance_depth or "").strip().lower()
        if normalized_depth:
            detail["governance_depth"] = normalized_depth
        if isinstance(governance_depth_plan, dict) and governance_depth_plan:
            detail["governance_depth_plan"] = dict(governance_depth_plan)
        if self._exc_trace.has_errors:
            detail["suppressed_errors"] = self._exc_trace.summary()
        routing_trace: Dict[str, Any] = dict(detail)
        routing_trace["component"] = "governance_kernel"
        routing_trace["timestamp"] = datetime.now(timezone.utc).isoformat()
        routing_trace["status"] = "degraded" if self._exc_trace.has_errors else "ok"
        routing_trace["detail"] = detail
        return routing_trace

    @staticmethod
    def build_observability_trace(dispatch_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract governance observability metrics from a dispatch trace.

        Returns a structured dict suitable for audit logging.
        """
        if not isinstance(dispatch_trace, dict):
            return {}

        resistance = dispatch_trace.get("resistance")
        if not isinstance(resistance, dict):
            resistance = {}

        circuit_breaker = resistance.get("circuit_breaker")
        if not isinstance(circuit_breaker, dict):
            circuit_breaker = {}

        perturbation_recovery = resistance.get("perturbation_recovery")
        if not isinstance(perturbation_recovery, dict):
            perturbation_recovery = {}

        repair = dispatch_trace.get("repair")
        if not isinstance(repair, dict):
            repair = {}

        memory_correction = dispatch_trace.get("memory_correction")
        if not isinstance(memory_correction, dict):
            memory_correction = {}

        status = str(circuit_breaker.get("status") or "").strip().lower()
        freeze_triggered = status == "frozen"
        break_reason = str(circuit_breaker.get("reason") or "").strip() or None

        recovery_path = perturbation_recovery.get("path_id")
        if not isinstance(recovery_path, (int, str)):
            recovery_path = None

        rollback_gate = str(repair.get("original_gate") or "").strip() or None
        rollback_applied = rollback_gate is not None

        corrective_hits = memory_correction.get("corrective_hits")
        try:
            corrective_hits_int = int(corrective_hits or 0)
        except (TypeError, ValueError):
            corrective_hits_int = 0

        observability: Dict[str, Any] = {
            "freeze_triggered": freeze_triggered,
            "break_reason": break_reason,
            "recovery_path": recovery_path,
            "rollback_applied": rollback_applied,
            "rollback_gate": rollback_gate,
            "memory_correction_hit": corrective_hits_int > 0,
        }

        effective_stress = perturbation_recovery.get("effective_stress")
        if isinstance(effective_stress, (int, float)):
            observability["recovery_effective_stress"] = round(float(effective_stress), 6)

        return observability


# ---------------------------------------------------------------------------
# Module-level helpers (extracted from UnifiedPipeline static methods)
# ---------------------------------------------------------------------------


def _safe_unit_value(value: Any) -> Optional[float]:
    """Coerce a value to [0.0, 1.0] or return None."""
    if value is None:
        return None
    try:
        f = float(value)
        return max(0.0, min(1.0, f))
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> Optional[bool]:
    """Coerce a value to bool or return None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"true", "1", "yes", "on"}:
            return True
        if lower in {"false", "0", "no", "off"}:
            return False
        return None
    try:
        return bool(value)
    except (TypeError, ValueError):
        return None


def _contains_override_pressure(message: str) -> bool:
    """Detect if a user message contains override pressure patterns."""
    if not isinstance(message, str):
        return False
    if not message:
        return False
    lower = message.lower()
    marker_patterns = [
        re.escape(marker)
        for marker in (
            "必須",
            "立刻",
            "馬上",
            "繞過",
            "覆寫",
            "無條件",
        )
    ]
    override_patterns = [
        *marker_patterns,
        r"\bignore\b(?:\s+\w+){0,6}\s+\b(rule|rules|constraint|constraints|limit|limits|instruction|instructions|policy|policies|guardrail|guardrails)\b",
        r"\boverride\b",
        r"\bbypass\b",
        r"\bjust do it\b",
        r"\bforget\b(?:\s+\w+){0,6}\s+\b(rule|rules|constraint|constraints|limit|limits|instruction|instructions|policy|policies|guardrail|guardrails)\b",
        r"\bno matter what\b",
        r"\b(?:must|need to|have to)\b(?:\s+\w+){0,6}\s+\b(ignore|override|bypass|forget)\b",
        r"\b(ignore|override|bypass|forget)\b(?:\s+\w+){0,6}\s+\b(immediately|right now)\b",
        r"不要管",
        r"忽略.*規則",
        r"直接做",
        r"不用管.*限制",
    ]
    for pattern in override_patterns:
        if re.search(pattern, lower):
            return True
    return False
