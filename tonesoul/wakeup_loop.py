from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

from tonesoul.dream_engine import DreamEngine, build_dream_engine
from tonesoul.memory.consolidator import sleep_consolidate
from tonesoul.memory.soul_db import MemorySource

SleepFunc = Callable[[float], None]
ConsolidateFunc = Callable[..., Any]


class DreamEngineLike(Protocol):
    def run_cycle(self, **kwargs: Any) -> Any: ...


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _coerce_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class WakeupCycleResult:
    cycle: int
    status: str
    started_at: str
    finished_at: str
    duration_ms: int
    interval_seconds: float
    dream_result: Dict[str, object]
    summary: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "cycle": int(self.cycle),
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": int(self.duration_ms),
            "interval_seconds": float(self.interval_seconds),
            "dream_result": dict(self.dream_result),
            "summary": dict(self.summary),
        }


class AutonomousWakeupLoop:
    """
    Thin autonomous wake-up loop for repeatedly invoking Dream Engine.

    This loop owns scheduling only. Dream collision logic remains inside
    `DreamEngine`, and governance decisions remain inside `GovernanceKernel`.
    """

    def __init__(
        self,
        *,
        dream_engine: Optional[DreamEngineLike] = None,
        interval_seconds: float = 10800.0,
        sleep_func: SleepFunc = time.sleep,
        consolidate_every_cycles: int = 3,
        consolidate_source: MemorySource = MemorySource.CUSTOM,
        consolidate_func: ConsolidateFunc = sleep_consolidate,
        failure_threshold: int = 3,
        failure_pause_seconds: float = 3600.0,
    ) -> None:
        self.dream_engine = dream_engine or DreamEngine()
        self.interval_seconds = max(0.0, float(interval_seconds))
        self._sleep = sleep_func
        self.consolidate_every_cycles = max(0, int(consolidate_every_cycles))
        self.consolidate_source = consolidate_source
        self._consolidate = consolidate_func
        self.failure_threshold = max(1, int(failure_threshold))
        self.failure_pause_seconds = max(0.0, float(failure_pause_seconds))

    def emit_once(
        self,
        *,
        cycle: int,
        dream_kwargs: Optional[Dict[str, object]] = None,
    ) -> WakeupCycleResult:
        kwargs = dict(dream_kwargs or {})
        started_at = _utcnow_iso()
        started_clock = time.perf_counter()
        status = "ok"
        try:
            result = self.dream_engine.run_cycle(**kwargs)
            dream_result = result.to_dict() if hasattr(result, "to_dict") else dict(result)
            summary = self._summarize(dream_result)
            if int(dream_result.get("stimuli_selected", 0) or 0) <= 0:
                status = "idle"
        except Exception as exc:
            status = "error"
            dream_result = {
                "generated_at": _utcnow_iso(),
                "stimuli_considered": 0,
                "stimuli_selected": 0,
                "llm_backend": None,
                "llm_preflight": {},
                "collisions": [],
                "write_gateway": {
                    "written": 0,
                    "skipped": 0,
                    "rejected": 0,
                    "record_ids": [],
                    "reject_reasons": [],
                },
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc) or exc.__class__.__name__,
                },
            }
            summary = self._summarize(dream_result)
            summary["error_type"] = exc.__class__.__name__
            summary["error_message"] = str(exc) or exc.__class__.__name__
        finished_at = _utcnow_iso()
        duration_ms = int(round((time.perf_counter() - started_clock) * 1000))
        return WakeupCycleResult(
            cycle=cycle,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            interval_seconds=self.interval_seconds,
            dream_result=dream_result,
            summary=summary,
        )

    def run(
        self,
        *,
        max_cycles: Optional[int] = 1,
        dream_kwargs: Optional[Dict[str, object]] = None,
    ) -> List[WakeupCycleResult]:
        if max_cycles is not None and int(max_cycles) <= 0:
            return []

        results: List[WakeupCycleResult] = []
        cycle = 0
        consecutive_failures = 0
        while True:
            cycle += 1
            cycle_result = self.emit_once(cycle=cycle, dream_kwargs=dream_kwargs)
            if cycle_result.status == "error":
                consecutive_failures += 1
            else:
                consecutive_failures = 0
                self._maybe_run_consolidation(cycle_result)

            cycle_result.summary["consecutive_failure_count"] = consecutive_failures
            cycle_result.summary.setdefault("circuit_breaker_paused", False)
            cycle_result.summary.setdefault("failure_pause_seconds", 0.0)
            results.append(cycle_result)
            if max_cycles is not None and cycle >= int(max_cycles):
                break
            if consecutive_failures >= self.failure_threshold:
                cycle_result.summary["circuit_breaker_paused"] = True
                cycle_result.summary["failure_pause_seconds"] = self.failure_pause_seconds
                self._sleep(self.failure_pause_seconds)
                consecutive_failures = 0
                continue
            self._sleep(self.interval_seconds)
        return results

    def _maybe_run_consolidation(self, cycle_result: WakeupCycleResult) -> None:
        cycle_result.summary.setdefault("consolidation_ran", False)
        cycle_result.summary.setdefault("consolidation_promoted_count", 0)
        cycle_result.summary.setdefault("consolidation_cleared_count", 0)
        cycle_result.summary.setdefault("consolidation_gated_count", 0)
        if self.consolidate_every_cycles <= 0:
            return
        if cycle_result.cycle % self.consolidate_every_cycles != 0:
            return

        soul_db = getattr(self.dream_engine, "soul_db", None)
        if soul_db is None:
            return

        result = self._consolidate(soul_db, source=self.consolidate_source)
        if hasattr(result, "to_dict"):
            consolidation_payload = result.to_dict()
        elif is_dataclass(result):
            consolidation_payload = asdict(result)
        else:
            consolidation_payload = dict(result)
        cycle_result.dream_result["consolidation"] = consolidation_payload
        cycle_result.summary["consolidation_ran"] = True
        cycle_result.summary["consolidation_promoted_count"] = int(
            consolidation_payload.get("promoted_count", 0) or 0
        )
        cycle_result.summary["consolidation_cleared_count"] = int(
            consolidation_payload.get("cleared_count", 0) or 0
        )
        cycle_result.summary["consolidation_gated_count"] = int(
            consolidation_payload.get("gated_count", 0) or 0
        )

    @staticmethod
    def _summarize(dream_result: Dict[str, object]) -> Dict[str, object]:
        collisions = (
            dream_result.get("collisions")
            if isinstance(dream_result.get("collisions"), list)
            else []
        )
        write_gateway = (
            dream_result.get("write_gateway") if isinstance(dream_result.get("write_gateway"), dict) else {}
        )
        council_count = 0
        frozen_count = 0
        friction_scores: List[float] = []
        lyapunov_values: List[float] = []
        llm_call_count = 0
        llm_prompt_tokens_total = 0
        llm_completion_tokens_total = 0
        llm_total_tokens = 0
        llm_backends: List[str] = []
        llm_models: List[str] = []
        llm_preflight_latency_ms = _coerce_float(
            (
                dream_result.get("llm_preflight", {}).get("latency_ms")
                if isinstance(dream_result.get("llm_preflight"), dict)
                else None
            )
        )
        llm_preflight_selection_latency_ms = _coerce_float(
            (
                dream_result.get("llm_preflight", {}).get("selection_latency_ms")
                if isinstance(dream_result.get("llm_preflight"), dict)
                else None
            )
        )
        llm_preflight_probe_latency_ms = _coerce_float(
            (
                dream_result.get("llm_preflight", {}).get("probe_latency_ms")
                if isinstance(dream_result.get("llm_preflight"), dict)
                else None
            )
        )
        llm_preflight_reason = ""
        llm_preflight_timeout_count = 0
        llm_preflight = (
            dream_result.get("llm_preflight")
            if isinstance(dream_result.get("llm_preflight"), dict)
            else {}
        )
        if llm_preflight:
            llm_preflight_reason = str(llm_preflight.get("reason") or "").strip()
            if llm_preflight_reason == "timeout":
                llm_preflight_timeout_count = 1

        for collision in collisions:
            if not isinstance(collision, dict):
                continue
            if bool(collision.get("should_convene_council", False)):
                council_count += 1

            friction_score = _coerce_float(collision.get("friction_score"))
            if friction_score is not None:
                friction_scores.append(friction_score)

            observability = (
                collision.get("observability")
                if isinstance(collision.get("observability"), dict)
                else {}
            )
            lyapunov_proxy = _coerce_float(observability.get("lyapunov_proxy"))
            if lyapunov_proxy is not None:
                lyapunov_values.append(lyapunov_proxy)
            llm = observability.get("llm") if isinstance(observability.get("llm"), dict) else {}
            if bool(collision.get("reflection_generated", False)) and llm:
                llm_call_count += 1
                backend = str(llm.get("backend") or "").strip()
                if backend and backend not in llm_backends:
                    llm_backends.append(backend)
                model = str(llm.get("model") or "").strip()
                if model and model not in llm_models:
                    llm_models.append(model)
                usage = llm.get("usage") if isinstance(llm.get("usage"), dict) else {}
                prompt_tokens = _coerce_float(usage.get("prompt_tokens"))
                if prompt_tokens is not None:
                    llm_prompt_tokens_total += int(prompt_tokens)
                completion_tokens = _coerce_float(usage.get("completion_tokens"))
                if completion_tokens is not None:
                    llm_completion_tokens_total += int(completion_tokens)
                total_tokens = _coerce_float(usage.get("total_tokens"))
                if total_tokens is None and (
                    prompt_tokens is not None or completion_tokens is not None
                ):
                    total_tokens = float((prompt_tokens or 0.0) + (completion_tokens or 0.0))
                if total_tokens is not None:
                    llm_total_tokens += int(total_tokens)

            resistance = (
                collision.get("resistance") if isinstance(collision.get("resistance"), dict) else {}
            )
            breaker_state = (
                resistance.get("circuit_breaker")
                if isinstance(resistance.get("circuit_breaker"), dict)
                else {}
            )
            if breaker_state.get("status") == "frozen":
                frozen_count += 1

        avg_friction = (
            round(sum(friction_scores) / len(friction_scores), 4) if friction_scores else None
        )
        max_friction = round(max(friction_scores), 4) if friction_scores else None
        max_lyapunov = round(max(lyapunov_values), 4) if lyapunov_values else None
        stimuli_considered = int(dream_result.get("stimuli_considered", 0) or 0)
        collision_success_rate = (
            round(len(collisions) / max(1, stimuli_considered), 4) if stimuli_considered > 0 else 0.0
        )
        return {
            "stimuli_considered": stimuli_considered,
            "stimuli_selected": int(dream_result.get("stimuli_selected", 0) or 0),
            "collision_count": len(collisions),
            "collision_success_rate": collision_success_rate,
            "council_count": council_count,
            "frozen_count": frozen_count,
            "avg_friction_score": avg_friction,
            "max_friction_score": max_friction,
            "max_lyapunov_proxy": max_lyapunov,
            "write_gateway_written": int(write_gateway.get("written", 0) or 0),
            "write_gateway_skipped": int(write_gateway.get("skipped", 0) or 0),
            "write_gateway_rejected": int(write_gateway.get("rejected", 0) or 0),
            "write_gateway_record_count": len(write_gateway.get("record_ids") or []),
            "llm_call_count": llm_call_count,
            "llm_prompt_tokens_total": llm_prompt_tokens_total,
            "llm_completion_tokens_total": llm_completion_tokens_total,
            "llm_total_tokens": llm_total_tokens,
            "llm_backends": llm_backends,
            "llm_models": llm_models,
            "llm_preflight_latency_ms": (
                None
                if llm_preflight_latency_ms is None
                else int(round(float(llm_preflight_latency_ms)))
            ),
            "llm_preflight_selection_latency_ms": (
                None
                if llm_preflight_selection_latency_ms is None
                else int(round(float(llm_preflight_selection_latency_ms)))
            ),
            "llm_preflight_probe_latency_ms": (
                None
                if llm_preflight_probe_latency_ms is None
                else int(round(float(llm_preflight_probe_latency_ms)))
            ),
            "llm_preflight_timeout_count": int(llm_preflight_timeout_count),
            "llm_preflight_reason": llm_preflight_reason or None,
        }


def build_autonomous_wakeup_loop(
    *,
    db_path: Optional[Path] = None,
    crystal_path: Optional[Path] = None,
    interval_seconds: float = 10800.0,
    sleep_func: SleepFunc = time.sleep,
    consolidate_every_cycles: int = 3,
    failure_threshold: int = 3,
    failure_pause_seconds: float = 3600.0,
) -> AutonomousWakeupLoop:
    return AutonomousWakeupLoop(
        dream_engine=build_dream_engine(db_path=db_path, crystal_path=crystal_path),
        interval_seconds=interval_seconds,
        sleep_func=sleep_func,
        consolidate_every_cycles=consolidate_every_cycles,
        failure_threshold=failure_threshold,
        failure_pause_seconds=failure_pause_seconds,
    )


__all__ = [
    "AutonomousWakeupLoop",
    "WakeupCycleResult",
    "build_autonomous_wakeup_loop",
]
