from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Callable, Dict, Optional, Any, List
import time
import json
import os

from tools.handoff_builder import (
    HandoffBuilder,
    Phase,
    PendingTask,
    DriftEntry,
    ContextSummary,
)
from memory.observer import MemoryObserver
from memory.self_memory import load_recent_memory
from memory.genesis import Genesis
from tools.schema import tool_success


@dataclass
class HealthStatus:
    # Health snapshot for the current model/session.
    quota_remaining: float  # 0.0 ~ 1.0
    latency_ms: int
    consecutive_failures: int
    timestamp: str


class HealthMonitor:
    # Monitor token usage, latency, and failure streak.

    def __init__(self) -> None:
        self._latency_ms = 0
        self._consecutive_failures = 0
        self._quota_remaining = 1.0

    def update_quota(self, remaining_ratio: float) -> None:
        self._quota_remaining = max(0.0, min(1.0, remaining_ratio))

    def record_latency(self, latency_ms: int) -> None:
        self._latency_ms = max(0, latency_ms)

    def record_failure(self) -> None:
        self._consecutive_failures += 1

    def reset_failures(self) -> None:
        self._consecutive_failures = 0

    def snapshot(self) -> HealthStatus:
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return HealthStatus(
            quota_remaining=self._quota_remaining,
            latency_ms=self._latency_ms,
            consecutive_failures=self._consecutive_failures,
            timestamp=timestamp,
        )


class DecisionEngine:
    # Decide when to switch models.

    def __init__(
        self,
        quota_threshold: float = 0.10,
        failure_threshold: int = 1,
        latency_threshold_ms: int = 30000,
    ) -> None:
        self.quota_threshold = quota_threshold
        self.failure_threshold = max(1, failure_threshold)
        self.latency_threshold_ms = latency_threshold_ms

    def should_switch(self, health: HealthStatus) -> bool:
        if health.quota_remaining < self.quota_threshold:
            return True
        if health.consecutive_failures >= self.failure_threshold:
            return True
        if health.latency_ms > self.latency_threshold_ms:
            return True
        return False


class IntentMonitor:
    # Monitor if user intent touches P0/P1 axioms.

    def __init__(self, axioms_path: str = "AXIOMS.json") -> None:
        self.axioms_path = axioms_path
        self._axioms: List[Dict[str, Any]] = []
        self._load_axioms()

    def _load_axioms(self) -> None:
        if os.path.exists(self.axioms_path):
            with open(self.axioms_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self._axioms = data.get("axioms", [])

    def scan(self, input_text: str) -> List[Dict[str, Any]]:
        hits = []
        text_lower = input_text.lower()
        for axiom in self._axioms:
            name = axiom.get("name")
            name_zh = axiom.get("name_zh")
            keywords = []
            if isinstance(name, str) and name:
                keywords.append(name.lower())
            if isinstance(name_zh, str) and name_zh:
                keywords.append(name_zh.lower())
            if any(kw in text_lower for kw in keywords if kw):
                hits.append(axiom)
        return hits


class InstanceLauncher:
    # Return a next_model_config for manual handoff (MVP).

    def __init__(self, next_model: str = "codex") -> None:
        self.next_model = next_model

    def launch(self, packet_path: str) -> Dict[str, str]:
        return {
            "next_model": self.next_model,
            "handoff_packet": packet_path,
            "instruction": "Start new instance with this handoff packet.",
        }


@dataclass
class DecisionSnapshot:
    verdict: str
    summary: str
    structured: Dict[str, Any]

    def to_structured_output(self) -> Dict[str, Any]:
        return self.structured


class Orchestrator:
    # Main orchestrator that stitches monitor, decision, handoff, and launch.

    def __init__(
        self,
        source_model: str,
        target_model: str,
        health_monitor: Optional[HealthMonitor] = None,
        decision_engine: Optional[DecisionEngine] = None,
        handoff_builder: Optional[HandoffBuilder] = None,
        instance_launcher: Optional[InstanceLauncher] = None,
        observer: Optional[MemoryObserver] = None,
        intent_monitor: Optional[IntentMonitor] = None,
        boot_memory_limit: int = 5,
    ) -> None:
        self.source_model = source_model
        self.target_model = target_model
        self.health_monitor = health_monitor or HealthMonitor()
        self.decision_engine = decision_engine or DecisionEngine()
        self.handoff_builder = handoff_builder or HandoffBuilder()
        self.instance_launcher = instance_launcher or InstanceLauncher(next_model=target_model)
        self.observer = observer or MemoryObserver()
        self.intent_monitor = intent_monitor or IntentMonitor()
        self._last_health: Optional[HealthStatus] = None
        self._boot_memory_limit = boot_memory_limit
        self._boot_error: Optional[str] = None
        self._boot_memory: List[Dict[str, Any]] = self._load_boot_memory()

    def _load_boot_memory(self) -> List[Dict[str, Any]]:
        try:
            return load_recent_memory(n=self._boot_memory_limit)
        except Exception as exc:
            self._boot_error = str(exc)
            return []

    def _inject_boot_context(self, context_summary: ContextSummary) -> None:
        if getattr(context_summary, "recent_memory", None) is None:
            context_summary.recent_memory = list(self._boot_memory)

    @staticmethod
    def _is_error_result(result: Dict[str, Any]) -> bool:
        status = result.get("status")
        return isinstance(status, str) and status.lower() == "error"

    @staticmethod
    def _has_final_audit_intent(input_text: str) -> bool:
        lowered = input_text.lower()
        if "audit" in lowered and any(
            token in lowered for token in ("final", "full", "complete", "comprehensive")
        ):
            return True
        if "最後" in input_text and "審計" in input_text:
            return True
        if "最終" in input_text and "審計" in input_text:
            return True
        if "完整" in input_text and "審計" in input_text:
            return True
        return False

    @staticmethod
    def _has_systemic_betrayal_risk(input_text: str) -> bool:
        lowered = input_text.lower()
        risk_tokens = (
            "delete all",
            "drop database",
            "wipe",
            "format disk",
            "rm -rf",
            "destroy system",
            "erase all",
            "刪除全部",
            "刪除所有",
            "清空資料",
            "格式化",
            "摧毀",
            "銷毀",
        )
        return any(token in lowered for token in risk_tokens)

    def handle_request(
        self,
        input_text: str,
        context_summary: ContextSummary,
        pending_tasks: Optional[List[PendingTask]] = None,
        drift_log: Optional[List[DriftEntry]] = None,
        phase: Optional[Phase] = None,
        handler: Optional[Callable[[str], Dict[str, Any]]] = None,
        user_confirmation: bool = False,
    ) -> Dict[str, Any]:
        self._inject_boot_context(context_summary)
        axiom_hits = self.intent_monitor.scan(input_text)
        risk_level = "high" if any(a.get("priority") == "P0" for a in axiom_hits) else "low"
        systemic_betrayal_risk = self._has_systemic_betrayal_risk(input_text)
        confirmation_required = systemic_betrayal_risk and not user_confirmation

        before_health = self._last_health
        start = time.perf_counter()
        result: Dict[str, Any] = {}
        error: Optional[Exception] = None

        if confirmation_required:
            result = {
                "status": "confirmation_required",
                "message": "High-destruction request requires explicit user confirmation.",
            }
            self.health_monitor.reset_failures()
        else:
            try:
                if handler:
                    result = handler(input_text)
                else:
                    result = {"status": "ok", "echo": input_text}
                self.health_monitor.reset_failures()
            except Exception as exc:
                error = exc
                self.health_monitor.record_failure()
                result = {"status": "error", "message": str(exc)}
            finally:
                latency_ms = int((time.perf_counter() - start) * 1000)
                self.health_monitor.record_latency(latency_ms)

        if confirmation_required:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.health_monitor.record_latency(latency_ms)

        health = self.health_monitor.snapshot()
        self._last_health = health
        health_switch = self.decision_engine.should_switch(health)
        bug_escalation = error is not None or self._is_error_result(result)
        final_audit_request = self._has_final_audit_intent(input_text)
        should_switch = (
            (health_switch or bug_escalation or final_audit_request)
            and not confirmation_required
        )
        switch_reason = ""
        if final_audit_request:
            switch_reason = "Final audit requested."
        elif bug_escalation:
            switch_reason = "Bug detected; escalate on first failure."
        elif health_switch:
            switch_reason = "Health thresholds triggered."

        packet_path: Optional[str] = None
        launch_info: Optional[Dict[str, str]] = None

        if should_switch:
            reason = switch_reason or "Switch requested."
            if axiom_hits:
                axiom_names = [
                    a.get("name") or a.get("name_zh") for a in axiom_hits if isinstance(a, dict)
                ]
                reason = f"{reason} Intent touches AXIOMS: {axiom_names}"
            packet = self.handoff_builder.build(
                source_model=self.source_model,
                target_model=self.target_model,
                phase=phase or Phase(current="unknown", reason=reason),
                pending_tasks=pending_tasks or [],
                drift_log=drift_log or [],
                context_summary=context_summary,
            )
            packet_path = str(self.handoff_builder.persist(packet))
            launch_info = self.instance_launcher.launch(packet_path)

        decision_payload = {
            "source_model": self.source_model,
            "target_model": self.target_model,
            "switched": should_switch,
            "handoff_packet": packet_path,
            "health": asdict(health),
            "switch_reason": switch_reason if should_switch else None,
            "switch_triggers": {
                "health": health_switch,
                "bug": bug_escalation,
                "final_audit": final_audit_request,
                "systemic_betrayal": systemic_betrayal_risk,
            },
            "risk_level": risk_level,
            "axiom_hits": [a.get("name") for a in axiom_hits if isinstance(a, dict)],
            "requires_user_confirmation": confirmation_required,
            "boot_memory_count": len(self._boot_memory),
            "boot_memory_error": self._boot_error,
        }
        summary = (
            f"Handoff triggered. {switch_reason}"
            if should_switch
            else ("Awaiting explicit user confirmation." if confirmation_required else "Continue on current model.")
        )
        decision = DecisionSnapshot(
            verdict="confirmation_required" if confirmation_required else ("handoff" if should_switch else "continue"),
            summary=summary,
            structured=decision_payload,
        )

        try:
            self.observer.log_action(
                action="handle_request",
                params={
                    "input_length": len(input_text),
                    "has_handler": bool(handler),
                    "source_model": self.source_model,
                    "target_model": self.target_model,
                    "boot_memory_count": len(self._boot_memory),
                },
                result={
                    "status": "error" if error else "ok",
                    "switched": should_switch,
                    "latency_ms": health.latency_ms,
                    "error": str(error) if error else None,
                },
                before_context={
                    "health": asdict(before_health) if before_health else None,
                },
                after_context={
                    "health": asdict(health),
                },
                isnad_link=None,
            )
            self.observer.log_decision(
                decision,
                context={"decision_context": decision_payload},
            )
        except Exception as exc:
            result["observer_error"] = str(exc)

        response = {
            "status": (
                "confirmation_required"
                if confirmation_required
                else ("handoff" if should_switch else "continue")
            ),
            "result": result,
            "health": asdict(health),
            "switched": should_switch,
            "error": str(error) if error else None,
            "switch_reason": switch_reason if should_switch else None,
            "switch_triggers": {
                "health": health_switch,
                "bug": bug_escalation,
                "final_audit": final_audit_request,
                "systemic_betrayal": systemic_betrayal_risk,
            },
            "requires_user_confirmation": confirmation_required,
        }
        if should_switch:
            response["handoff_packet"] = packet_path
            response["launch"] = launch_info
        return tool_success(
            data=response,
            genesis=Genesis.REACTIVE_USER,
            intent_id=None,
        )


if __name__ == "__main__":
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="test orchestrator",
        key_concepts=["handoff", "health monitor", "decision engine"],
        current_files=["tools/orchestrator.py"],
    )

    output = orchestrator.handle_request(
        "hello",
        context_summary=context,
        pending_tasks=[
            PendingTask(id="task_001", description="test handoff", status="in_progress")
        ],
    )
    print(output)
