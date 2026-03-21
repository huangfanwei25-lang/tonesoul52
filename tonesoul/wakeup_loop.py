from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol
from uuid import uuid4

from tonesoul.dream_engine import DreamEngine, build_dream_engine
from tonesoul.memory.consolidator import sleep_consolidate
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.scribe.scribe_engine import ScribeDraftResult, ToneSoulScribe
from tonesoul.scribe.status_artifact import (
    build_scribe_status_payload,
    write_scribe_status_artifact,
)

SleepFunc = Callable[[float], None]
ConsolidateFunc = Callable[..., Any]


class DreamEngineLike(Protocol):
    def run_cycle(self, **kwargs: Any) -> Any: ...


class ScribeLike(Protocol):
    def draft_chronicle(
        self,
        db: sqlite3.Connection,
        title_hint: str = "A Day in the Dream Engine",
        source_db_path: str | Path | None = None,
    ) -> ScribeDraftResult: ...


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _new_wakeup_session_id() -> str:
    return f"wakeup_{uuid4().hex[:12]}"


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


@dataclass
class WakeupRuntimeState:
    session_id: str = field(default_factory=_new_wakeup_session_id)
    next_cycle: int = 1
    consecutive_failures: int = 0
    last_status: str = "idle"
    last_started_at: str | None = None
    last_finished_at: str | None = None
    last_duration_ms: int | None = None
    updated_at: str = field(default_factory=_utcnow_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "session_id": self.session_id,
            "next_cycle": max(1, int(self.next_cycle)),
            "consecutive_failures": max(0, int(self.consecutive_failures)),
            "last_status": self.last_status,
            "last_started_at": self.last_started_at,
            "last_finished_at": self.last_finished_at,
            "last_duration_ms": (
                None if self.last_duration_ms is None else max(0, int(self.last_duration_ms))
            ),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "WakeupRuntimeState":
        raw_session_id = str(payload.get("session_id") or "").strip()
        return cls(
            session_id=raw_session_id or _new_wakeup_session_id(),
            next_cycle=max(1, int(payload.get("next_cycle", 1) or 1)),
            consecutive_failures=max(0, int(payload.get("consecutive_failures", 0) or 0)),
            last_status=str(payload.get("last_status") or "idle"),
            last_started_at=(
                None
                if payload.get("last_started_at") in (None, "")
                else str(payload.get("last_started_at"))
            ),
            last_finished_at=(
                None
                if payload.get("last_finished_at") in (None, "")
                else str(payload.get("last_finished_at"))
            ),
            last_duration_ms=(
                None
                if payload.get("last_duration_ms") in (None, "")
                else max(0, int(payload.get("last_duration_ms", 0) or 0))
            ),
            updated_at=str(payload.get("updated_at") or _utcnow_iso()),
        )


@dataclass
class WakeupScribeState:
    last_signature: str = ""
    last_cycle: int = 0
    last_result_status: str = "idle"
    last_generated_at: str | None = None
    updated_at: str = field(default_factory=_utcnow_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "last_signature": str(self.last_signature or ""),
            "last_cycle": max(0, int(self.last_cycle)),
            "last_result_status": str(self.last_result_status or "idle"),
            "last_generated_at": self.last_generated_at,
            "updated_at": str(self.updated_at or _utcnow_iso()),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "WakeupScribeState":
        return cls(
            last_signature=str(payload.get("last_signature") or ""),
            last_cycle=max(0, int(payload.get("last_cycle", 0) or 0)),
            last_result_status=str(payload.get("last_result_status") or "idle"),
            last_generated_at=(
                None
                if payload.get("last_generated_at") in (None, "")
                else str(payload.get("last_generated_at"))
            ),
            updated_at=str(payload.get("updated_at") or _utcnow_iso()),
        )


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
        state_path: Optional[Path] = None,
        scribe: Optional[ScribeLike] = None,
        scribe_status_path: Optional[Path] = None,
        scribe_state_path: Optional[Path] = None,
    ) -> None:
        self.dream_engine = dream_engine or DreamEngine()
        self.interval_seconds = max(0.0, float(interval_seconds))
        self._sleep = sleep_func
        self.consolidate_every_cycles = max(0, int(consolidate_every_cycles))
        self.consolidate_source = consolidate_source
        self._consolidate = consolidate_func
        self.failure_threshold = max(1, int(failure_threshold))
        self.failure_pause_seconds = max(0.0, float(failure_pause_seconds))
        self.state_path = None if state_path is None else Path(state_path)
        self.scribe = scribe
        self.scribe_status_path = None if scribe_status_path is None else Path(scribe_status_path)
        self.scribe_state_path = None if scribe_state_path is None else Path(scribe_state_path)
        self._last_runtime_state: WakeupRuntimeState | None = None
        self._last_runtime_state_resumed = False

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

        runtime_state, resumed = self._load_state()
        self._last_runtime_state = runtime_state
        self._last_runtime_state_resumed = resumed
        results: List[WakeupCycleResult] = []
        cycle = max(1, int(runtime_state.next_cycle))
        cycles_executed = 0
        consecutive_failures = max(0, int(runtime_state.consecutive_failures))
        while True:
            cycle_result = self.emit_once(cycle=cycle, dream_kwargs=dream_kwargs)
            cycles_executed += 1
            if cycle_result.status == "error":
                consecutive_failures += 1
            else:
                consecutive_failures = 0
                self._maybe_run_consolidation(cycle_result)
                self._maybe_run_scribe(cycle_result)

            cycle_result.summary["consecutive_failure_count"] = consecutive_failures
            cycle_result.summary.setdefault("circuit_breaker_paused", False)
            cycle_result.summary.setdefault("failure_pause_seconds", 0.0)
            cycle_result.summary["session_id"] = runtime_state.session_id
            cycle_result.summary["session_resumed"] = resumed
            cycle_result.summary["heartbeat_window_cycle"] = cycles_executed
            cycle_result.summary["resume_state_path"] = (
                None if self.state_path is None else self.state_path.as_posix()
            )
            runtime_state.next_cycle = cycle_result.cycle + 1
            runtime_state.consecutive_failures = consecutive_failures
            runtime_state.last_status = cycle_result.status
            runtime_state.last_started_at = cycle_result.started_at
            runtime_state.last_finished_at = cycle_result.finished_at
            runtime_state.last_duration_ms = cycle_result.duration_ms
            runtime_state.updated_at = _utcnow_iso()
            self._last_runtime_state = runtime_state
            self._last_runtime_state_resumed = resumed
            self._write_state(runtime_state)
            results.append(cycle_result)
            if max_cycles is not None and cycles_executed >= int(max_cycles):
                break
            if consecutive_failures >= self.failure_threshold:
                cycle_result.summary["circuit_breaker_paused"] = True
                cycle_result.summary["failure_pause_seconds"] = self.failure_pause_seconds
                self._sleep(self.failure_pause_seconds)
                consecutive_failures = 0
                runtime_state.consecutive_failures = 0
                runtime_state.updated_at = _utcnow_iso()
                self._last_runtime_state = runtime_state
                self._write_state(runtime_state)
                cycle = max(1, int(runtime_state.next_cycle))
                continue
            self._sleep(self.interval_seconds)
            cycle = max(1, int(runtime_state.next_cycle))
        return results

    def _load_state(self) -> tuple[WakeupRuntimeState, bool]:
        if self.state_path is None or not self.state_path.exists():
            return WakeupRuntimeState(), False
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return WakeupRuntimeState(), False
        if not isinstance(payload, dict):
            return WakeupRuntimeState(), False
        return WakeupRuntimeState.from_dict(payload), True

    def _write_state(self, runtime_state: WakeupRuntimeState) -> None:
        if self.state_path is None:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(runtime_state.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def get_runtime_state_snapshot(self) -> dict[str, object]:
        runtime_state = self._last_runtime_state
        resumed = self._last_runtime_state_resumed
        if runtime_state is None:
            runtime_state, resumed = self._load_state()
        payload = runtime_state.to_dict()
        payload["resumed"] = bool(resumed)
        payload["state_path"] = None if self.state_path is None else self.state_path.as_posix()
        return payload

    def _load_scribe_state(self) -> WakeupScribeState:
        if self.scribe_state_path is None or not self.scribe_state_path.exists():
            return WakeupScribeState()
        try:
            payload = json.loads(self.scribe_state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return WakeupScribeState()
        if not isinstance(payload, dict):
            return WakeupScribeState()
        return WakeupScribeState.from_dict(payload)

    def _write_scribe_state(self, scribe_state: WakeupScribeState) -> None:
        if self.scribe_state_path is None:
            return
        self.scribe_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.scribe_state_path.write_text(
            json.dumps(scribe_state.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _maybe_run_consolidation(self, cycle_result: WakeupCycleResult) -> None:
        cycle_result.summary.setdefault("consolidation_ran", False)
        cycle_result.summary.setdefault("consolidation_promoted_count", 0)
        cycle_result.summary.setdefault("consolidation_cleared_count", 0)
        cycle_result.summary.setdefault("consolidation_gated_count", 0)
        cycle_result.summary.setdefault("consolidation_unresolved_tension_count", 0)
        cycle_result.summary.setdefault("consolidation_vow_count", 0)
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
        subjectivity_summary = (
            consolidation_payload.get("subjectivity_summary")
            if isinstance(consolidation_payload.get("subjectivity_summary"), dict)
            else {}
        )
        by_subjectivity_layer = (
            subjectivity_summary.get("by_subjectivity_layer")
            if isinstance(subjectivity_summary.get("by_subjectivity_layer"), dict)
            else {}
        )
        cycle_result.summary["consolidation_unresolved_tension_count"] = int(
            subjectivity_summary.get("unresolved_tension_count", 0) or 0
        )
        cycle_result.summary["consolidation_vow_count"] = int(
            by_subjectivity_layer.get("vow", 0) or 0
        )

    def _maybe_run_scribe(self, cycle_result: WakeupCycleResult) -> None:
        cycle_result.summary.setdefault("scribe_evaluated", False)
        cycle_result.summary.setdefault("scribe_triggered", False)
        cycle_result.summary.setdefault("scribe_skip_reason", "")
        cycle_result.summary.setdefault("scribe_status", "")
        cycle_result.summary.setdefault("scribe_generation_mode", "")
        cycle_result.summary.setdefault("scribe_state_document_posture", "")
        cycle_result.summary.setdefault("scribe_latest_available_source", "")
        cycle_result.summary.setdefault("scribe_signal_signature", "")
        cycle_result.dream_result.setdefault("scribe", {})

        scribe_payload: Dict[str, object] = {
            "evaluated": True,
            "triggered": False,
            "skip_reason": "",
            "signal_signature": "",
            "status_artifact_path": (
                None if self.scribe_status_path is None else self.scribe_status_path.as_posix()
            ),
            "state_path": (
                None if self.scribe_state_path is None else self.scribe_state_path.as_posix()
            ),
        }
        cycle_result.summary["scribe_evaluated"] = True

        if self.scribe is None:
            scribe_payload["skip_reason"] = "disabled"
            cycle_result.summary["scribe_skip_reason"] = "disabled"
            cycle_result.dream_result["scribe"] = scribe_payload
            return

        signal_present = self._should_trigger_scribe(cycle_result)
        signature = self._build_scribe_signal_signature(cycle_result) if signal_present else ""
        cycle_result.summary["scribe_signal_signature"] = signature
        scribe_payload["signal_signature"] = signature

        if not signal_present:
            scribe_payload["skip_reason"] = "no_material_signal"
            cycle_result.summary["scribe_skip_reason"] = "no_material_signal"
            cycle_result.dream_result["scribe"] = scribe_payload
            return

        scribe_state = self._load_scribe_state()
        if signature and signature == scribe_state.last_signature:
            scribe_payload["skip_reason"] = "duplicate_signal_signature"
            cycle_result.summary["scribe_skip_reason"] = "duplicate_signal_signature"
            cycle_result.dream_result["scribe"] = scribe_payload
            return

        soul_db = getattr(self.dream_engine, "soul_db", None)
        if not isinstance(soul_db, SqliteSoulDB):
            scribe_payload["skip_reason"] = "unsupported_soul_db"
            cycle_result.summary["scribe_skip_reason"] = "unsupported_soul_db"
            cycle_result.dream_result["scribe"] = scribe_payload
            return

        try:
            with sqlite3.connect(soul_db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                result = self.scribe.draft_chronicle(
                    db=conn,
                    title_hint=self._scribe_title_hint(cycle_result),
                    source_db_path=soul_db.db_path,
                )
        except Exception as exc:
            scribe_payload["skip_reason"] = "scribe_runtime_failed"
            scribe_payload["error"] = {
                "type": exc.__class__.__name__,
                "message": str(exc) or exc.__class__.__name__,
            }
            cycle_result.summary["scribe_skip_reason"] = "scribe_runtime_failed"
            cycle_result.dream_result["scribe"] = scribe_payload
            return

        cycle_result.summary["scribe_triggered"] = True
        if self.scribe_status_path is not None:
            status_path = write_scribe_status_artifact(result, out_path=self.scribe_status_path)
            scribe_payload["status_artifact_path"] = status_path.as_posix()
        status_payload = build_scribe_status_payload(result)

        cycle_result.summary["scribe_status"] = str(status_payload.get("status") or "")
        cycle_result.summary["scribe_generation_mode"] = str(
            status_payload.get("generation_mode") or ""
        )
        cycle_result.summary["scribe_state_document_posture"] = str(
            status_payload.get("state_document_posture") or ""
        )
        cycle_result.summary["scribe_anchor_status_line"] = str(
            status_payload.get("anchor_status_line") or ""
        )
        cycle_result.summary["scribe_problem_route_status_line"] = str(
            status_payload.get("problem_route_status_line") or ""
        )
        secondary_route_labels = status_payload.get("problem_route_secondary_labels")
        if isinstance(secondary_route_labels, list):
            cycle_result.summary["scribe_problem_route_secondary_labels"] = ",".join(
                str(label).strip() for label in secondary_route_labels if str(label).strip()
            )
        else:
            cycle_result.summary["scribe_problem_route_secondary_labels"] = str(
                secondary_route_labels or ""
            ).strip()
        cycle_result.summary["scribe_latest_available_source"] = str(
            status_payload.get("latest_available_source") or ""
        )
        cycle_result.dream_result["scribe"] = {
            **scribe_payload,
            "triggered": True,
            "result": status_payload,
        }

        scribe_state.last_signature = signature
        scribe_state.last_cycle = cycle_result.cycle
        scribe_state.last_result_status = result.status
        scribe_state.last_generated_at = result.generated_at
        scribe_state.updated_at = _utcnow_iso()
        self._write_scribe_state(scribe_state)

    @staticmethod
    def _should_trigger_scribe(cycle_result: WakeupCycleResult) -> bool:
        summary = cycle_result.summary
        return any(
            int(summary.get(key, 0) or 0) > 0
            for key in (
                "collision_count",
                "consolidation_promoted_count",
                "consolidation_gated_count",
                "consolidation_unresolved_tension_count",
                "consolidation_vow_count",
            )
        )

    @staticmethod
    def _scribe_title_hint(cycle_result: WakeupCycleResult) -> str:
        summary = cycle_result.summary
        if int(summary.get("consolidation_unresolved_tension_count", 0) or 0) > 0:
            return "The Weight of Unresolved Tensions"
        if int(summary.get("collision_count", 0) or 0) > 0:
            return "After the Wake-Up Collisions"
        if int(summary.get("consolidation_promoted_count", 0) or 0) > 0:
            return "What Sleep Consolidated"
        return "Wake-Up State Document"

    @staticmethod
    def _build_scribe_signal_signature(cycle_result: WakeupCycleResult) -> str:
        summary = cycle_result.summary
        collisions = (
            cycle_result.dream_result.get("collisions")
            if isinstance(cycle_result.dream_result.get("collisions"), list)
            else []
        )
        collision_anchors: list[dict[str, object]] = []
        for item in collisions:
            if not isinstance(item, dict):
                continue
            observability = (
                item.get("observability") if isinstance(item.get("observability"), dict) else {}
            )
            collision_anchors.append(
                {
                    "stimulus_record_id": str(item.get("stimulus_record_id") or ""),
                    "topic": str(item.get("topic") or "").strip()[:120],
                    "write_status": str(observability.get("write_status") or "").strip(),
                    "write_skip_reason": str(observability.get("write_skip_reason") or "").strip(),
                }
            )
        payload = {
            "status": cycle_result.status,
            "collision_count": int(summary.get("collision_count", 0) or 0),
            "council_count": int(summary.get("council_count", 0) or 0),
            "frozen_count": int(summary.get("frozen_count", 0) or 0),
            "consolidation_promoted_count": int(
                summary.get("consolidation_promoted_count", 0) or 0
            ),
            "consolidation_cleared_count": int(summary.get("consolidation_cleared_count", 0) or 0),
            "consolidation_gated_count": int(summary.get("consolidation_gated_count", 0) or 0),
            "consolidation_unresolved_tension_count": int(
                summary.get("consolidation_unresolved_tension_count", 0) or 0
            ),
            "consolidation_vow_count": int(summary.get("consolidation_vow_count", 0) or 0),
            "collision_anchors": collision_anchors,
        }
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _summarize(dream_result: Dict[str, object]) -> Dict[str, object]:
        collisions = (
            dream_result.get("collisions")
            if isinstance(dream_result.get("collisions"), list)
            else []
        )
        write_gateway = (
            dream_result.get("write_gateway")
            if isinstance(dream_result.get("write_gateway"), dict)
            else {}
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
            round(len(collisions) / max(1, stimuli_considered), 4)
            if stimuli_considered > 0
            else 0.0
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
    state_path: Optional[Path] = Path("memory/autonomous/dream_wakeup_state.json"),
    enable_scribe: bool = True,
    scribe_out_dir: Optional[Path] = Path("docs/chronicles"),
    scribe_status_path: Optional[Path] = Path("docs/status/scribe_status_latest.json"),
    scribe_state_path: Optional[Path] = Path("memory/autonomous/dream_wakeup_scribe_state.json"),
) -> AutonomousWakeupLoop:
    scribe = None
    if enable_scribe:
        resolved_out_dir = (
            Path(scribe_out_dir) if scribe_out_dir is not None else Path("docs/chronicles")
        )
        scribe = ToneSoulScribe(out_dir=str(resolved_out_dir))
    return AutonomousWakeupLoop(
        dream_engine=build_dream_engine(db_path=db_path, crystal_path=crystal_path),
        interval_seconds=interval_seconds,
        sleep_func=sleep_func,
        consolidate_every_cycles=consolidate_every_cycles,
        failure_threshold=failure_threshold,
        failure_pause_seconds=failure_pause_seconds,
        state_path=state_path,
        scribe=scribe,
        scribe_status_path=(None if not enable_scribe else scribe_status_path),
        scribe_state_path=(None if not enable_scribe else scribe_state_path),
    )


__all__ = [
    "AutonomousWakeupLoop",
    "WakeupRuntimeState",
    "WakeupScribeState",
    "WakeupCycleResult",
    "build_autonomous_wakeup_loop",
]
