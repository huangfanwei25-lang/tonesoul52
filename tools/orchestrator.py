"""
Orchestrator MVP

Aligns with docs/ORCHESTRATOR_MVP.md and tools/handoff_builder.py style.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Callable, Dict, Optional, Any, List
import time

from tools.handoff_builder import (
    HandoffBuilder,
    Phase,
    PendingTask,
    DriftEntry,
    ContextSummary,
)
from memory.observer import MemoryObserver


@dataclass
class HealthStatus:
    """Health snapshot for the current model/session."""
    quota_remaining: float  # 0.0 ~ 1.0
    latency_ms: int
    consecutive_failures: int
    timestamp: str


class HealthMonitor:
    """Monitor token usage, latency, and failure streak."""

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
        return HealthStatus(
            quota_remaining=self._quota_remaining,
            latency_ms=self._latency_ms,
            consecutive_failures=self._consecutive_failures,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )


class DecisionEngine:
    """Decide when to switch models."""

    def __init__(
        self,
        quota_threshold: float = 0.10,
        failure_threshold: int = 3,
        latency_threshold_ms: int = 30000,
    ) -> None:
        self.quota_threshold = quota_threshold
        self.failure_threshold = failure_threshold
        self.latency_threshold_ms = latency_threshold_ms

    def should_switch(self, health: HealthStatus) -> bool:
        if health.quota_remaining < self.quota_threshold:
            return True
        if health.consecutive_failures > self.failure_threshold:
            return True
        if health.latency_ms > self.latency_threshold_ms:
            return True
        return False


class InstanceLauncher:
    """Return a next_model_config for manual handoff (MVP)."""

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
    """Main orchestrator that stitches monitor, decision, handoff, and launch."""

    def __init__(
        self,
        source_model: str,
        target_model: str,
        health_monitor: Optional[HealthMonitor] = None,
        decision_engine: Optional[DecisionEngine] = None,
        handoff_builder: Optional[HandoffBuilder] = None,
        instance_launcher: Optional[InstanceLauncher] = None,
        observer: Optional[MemoryObserver] = None,
    ) -> None:
        self.source_model = source_model
        self.target_model = target_model
        self.health_monitor = health_monitor or HealthMonitor()
        self.decision_engine = decision_engine or DecisionEngine()
        self.handoff_builder = handoff_builder or HandoffBuilder()
        self.instance_launcher = instance_launcher or InstanceLauncher(next_model=target_model)
        self.observer = observer or MemoryObserver()
        self._last_health: Optional[HealthStatus] = None

    def handle_request(
        self,
        input_text: str,
        context_summary: ContextSummary,
        pending_tasks: Optional[List[PendingTask]] = None,
        drift_log: Optional[List[DriftEntry]] = None,
        phase: Optional[Phase] = None,
        handler: Optional[Callable[[str], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        before_health = self._last_health
        start = time.perf_counter()
        result: Dict[str, Any] = {}
        error: Optional[Exception] = None

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

        health = self.health_monitor.snapshot()
        self._last_health = health
        should_switch = self.decision_engine.should_switch(health)
        packet_path = None
        launch_info: Optional[Dict[str, str]] = None

        if should_switch:
            packet = self.handoff_builder.build(
                source_model=self.source_model,
                target_model=self.target_model,
                phase=phase or Phase(current="霧", reason="自動切換：健康狀態觸發"),
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
        }
        decision = DecisionSnapshot(
            verdict="handoff" if should_switch else "continue",
            summary="Handoff triggered by health thresholds."
            if should_switch
            else "Continue on current model.",
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
            "status": "handoff" if should_switch else "continue",
            "result": result,
            "health": health,
            "switched": should_switch,
            "error": str(error) if error else None,
        }
        if should_switch:
            response["handoff_packet"] = packet_path
            response["launch"] = launch_info
        return response


if __name__ == "__main__":
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="建立多模型調度器",
        key_concepts=["handoff", "health monitor", "decision engine"],
        current_files=["tools/orchestrator.py"],
    )

    output = orchestrator.handle_request(
        "hello",
        context_summary=context,
        pending_tasks=[
            PendingTask(id="task_001", description="驗證 handoff", status="in_progress")
        ],
    )
    print(output)
