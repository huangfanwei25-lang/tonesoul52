"""Autonomous cycle: schedule-driven loop that wakes perception, dream, and evolution."""

from __future__ import annotations

__ts_layer__ = "orchestration"
__ts_purpose__ = "Drive the autonomous wake/sense/dream loop without a human trigger."

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol, Sequence

from tonesoul.dream_engine import DreamEngine
from tonesoul.dream_observability import HTML_FILENAME, JSON_FILENAME, build_dashboard, render_html
from tonesoul.governance.kernel import GovernanceKernel
from tonesoul.llm.router import LLMRouter
from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.memory.soul_db import SqliteSoulDB
from tonesoul.memory.write_gateway import MemoryWriteGateway, MemoryWriteResult
from tonesoul.perception.stimulus import StimulusProcessor
from tonesoul.perception.web_ingest import WebIngestor
from tonesoul.scribe.scribe_engine import ToneSoulScribe
from tonesoul.wakeup_loop import AutonomousWakeupLoop


class URLIngestorLike(Protocol):
    def ingest_urls_sync(self, urls: list[str]) -> list[Any]: ...


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _derive_overall_status(results: Sequence[dict[str, Any]]) -> str:
    statuses = [str(item.get("status") or "") for item in results]
    unique_statuses = {status for status in statuses if status}
    if not unique_statuses:
        return "idle"
    if len(unique_statuses) == 1:
        return next(iter(unique_statuses))
    return "mixed"


@dataclass
class AutonomousCycleResult:
    generated_at: str
    urls_requested: int
    urls_ingested: int
    urls_failed: int
    stimuli_processed: int
    memory_write: MemoryWriteResult = field(default_factory=MemoryWriteResult)
    wakeup_overall_status: str = "idle"
    wakeup_cycle_count: int = 0
    dashboard_overall_ok: bool = True
    paths: dict[str, str] = field(default_factory=dict)
    ingestion_failures: list[dict[str, str]] = field(default_factory=list)
    wakeup_payload: dict[str, object] = field(default_factory=dict)
    runtime_state: dict[str, object] = field(default_factory=dict)
    dashboard_payload: dict[str, object] = field(default_factory=dict)
    overall_ok: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "urls_requested": int(self.urls_requested),
            "urls_ingested": int(self.urls_ingested),
            "urls_failed": int(self.urls_failed),
            "stimuli_processed": int(self.stimuli_processed),
            "memory_write": {
                "written": int(self.memory_write.written),
                "skipped": int(self.memory_write.skipped),
                "record_ids": list(self.memory_write.record_ids),
            },
            "wakeup_overall_status": self.wakeup_overall_status,
            "wakeup_cycle_count": int(self.wakeup_cycle_count),
            "dashboard_overall_ok": bool(self.dashboard_overall_ok),
            "paths": dict(self.paths),
            "ingestion_failures": list(self.ingestion_failures),
            "wakeup_payload": dict(self.wakeup_payload),
            "runtime_state": dict(self.runtime_state),
            "dashboard_payload": dict(self.dashboard_payload),
            "overall_ok": bool(self.overall_ok),
        }


class AutonomousDreamCycleRunner:
    """
    One-shot composition seam for Phase 7 autonomous execution.

    This runner does not own policy. It composes ingestion, stimulus filtering,
    memory persistence, wake-up execution, and dashboard artifact refresh.
    """

    def __init__(
        self,
        *,
        db_path: Optional[Path] = None,
        crystal_path: Optional[Path] = None,
        journal_path: Path = Path("memory/self_journal.jsonl"),
        history_path: Path = Path("memory/autonomous/dream_wakeup_history.jsonl"),
        snapshot_path: Path = Path("docs/status/dream_wakeup_snapshot_latest.json"),
        state_path: Path = Path("memory/autonomous/dream_wakeup_state.json"),
        dashboard_out_dir: Path = Path("docs/status"),
        interval_seconds: float = 0.0,
        enable_scribe: bool = True,
        scribe_out_dir: Path = Path("docs/chronicles"),
        scribe_status_path: Path = Path("docs/status/scribe_status_latest.json"),
        scribe_state_path: Path = Path("memory/autonomous/dream_wakeup_scribe_state.json"),
        ingestor: Optional[URLIngestorLike] = None,
        stimulus_processor: Optional[StimulusProcessor] = None,
        write_gateway: Optional[MemoryWriteGateway] = None,
        wakeup_loop: Optional[AutonomousWakeupLoop] = None,
    ) -> None:
        self.db_path = Path(db_path) if db_path is not None else None
        self.crystal_path = Path(crystal_path) if crystal_path is not None else None
        self.journal_path = Path(journal_path)
        self.history_path = Path(history_path)
        self.snapshot_path = Path(snapshot_path)
        self.state_path = Path(state_path)
        self.dashboard_out_dir = Path(dashboard_out_dir)
        self.interval_seconds = max(0.0, float(interval_seconds))
        self.enable_scribe = bool(enable_scribe)
        self.scribe_out_dir = Path(scribe_out_dir)
        self.scribe_status_path = Path(scribe_status_path)
        self.scribe_state_path = Path(scribe_state_path)

        self.ingestor = ingestor or WebIngestor()
        self.stimulus_processor = stimulus_processor or StimulusProcessor()

        if write_gateway is None:
            soul_db = (
                SqliteSoulDB(db_path=self.db_path) if self.db_path is not None else SqliteSoulDB()
            )
            self.write_gateway = MemoryWriteGateway(soul_db)
        else:
            self.write_gateway = write_gateway

        self.wakeup_loop = wakeup_loop or self._build_wakeup_loop()

    def _build_wakeup_loop(self) -> AutonomousWakeupLoop:
        soul_db = self.write_gateway.soul_db
        crystallizer = (
            MemoryCrystallizer(crystal_path=self.crystal_path)
            if self.crystal_path is not None
            else MemoryCrystallizer()
        )
        kernel = GovernanceKernel()
        dream_engine = DreamEngine(
            soul_db=soul_db,
            write_gateway=self.write_gateway,
            governance_kernel=kernel,
            router=LLMRouter(backend_resolver=kernel.resolve_llm_backend),
            crystallizer=crystallizer,
        )
        return AutonomousWakeupLoop(
            dream_engine=dream_engine,
            interval_seconds=self.interval_seconds,
            state_path=self.state_path,
            scribe=(
                None if not self.enable_scribe else ToneSoulScribe(out_dir=str(self.scribe_out_dir))
            ),
            scribe_status_path=(None if not self.enable_scribe else self.scribe_status_path),
            scribe_state_path=(None if not self.enable_scribe else self.scribe_state_path),
        )

    def _check_autonomy_gate(self) -> Optional[AutonomousCycleResult]:
        """Check if reflex arc permits autonomous operation.

        Returns an early-exit result if autonomy is capped, else None.
        """
        try:
            from tonesoul.governance.reflex import GovernanceSnapshot, ReflexEvaluator
            from tonesoul.governance.reflex_config import load_reflex_config
            from tonesoul.runtime_adapter import load as load_posture

            config = load_reflex_config()
            if not config.enabled:
                return None

            posture = load_posture()
            snapshot = GovernanceSnapshot.from_posture(posture, tension=0.0)
            evaluator = ReflexEvaluator(config=config)
            decision = evaluator.evaluate(snapshot)
            band = decision.soul_band

            if band is not None and band.max_autonomy is not None:
                drift = dict(getattr(posture, "baseline_drift", {}) or {})
                current_autonomy = float(drift.get("autonomy_level", 0.35))
                if current_autonomy > band.max_autonomy:
                    return AutonomousCycleResult(
                        generated_at=_iso_now(),
                        urls_requested=0,
                        urls_ingested=0,
                        urls_failed=0,
                        stimuli_processed=0,
                        wakeup_overall_status="blocked_by_autonomy_gate",
                        overall_ok=False,
                        runtime_state={
                            "governance_gate": {
                                "blocked": True,
                                "reason": "autonomy_capped",
                                "current": round(current_autonomy, 4),
                                "max_allowed": round(band.max_autonomy, 4),
                                "soul_band": band.level.value,
                            }
                        },
                    )
        except Exception:
            pass  # fail open — don't block autonomous ops on import errors
        return None

    def run(
        self,
        *,
        urls: Optional[Sequence[str]] = None,
        max_cycles: int = 1,
        limit: int = 3,
        min_priority: float = 0.35,
        related_limit: int = 5,
        crystal_count: int = 5,
        generate_reflection: bool = False,
        require_inference_ready: bool = True,
        inference_timeout_seconds: float = 10.0,
    ) -> AutonomousCycleResult:
        # Autonomy gate: block if soul band caps autonomy level
        gate_result = self._check_autonomy_gate()
        if gate_result is not None:
            return gate_result

        resolved_urls = [str(url).strip() for url in (urls or []) if str(url).strip()]
        # This runner is intentionally sync-only; async callers must await
        # WebIngestor.ingest_urls(...) directly instead of crossing this seam.
        ingest_results = self.ingestor.ingest_urls_sync(resolved_urls) if resolved_urls else []
        ingestion_failures = [
            {
                "url": str(getattr(item, "url", "") or ""),
                "error": str(getattr(item, "error", "") or "ingest_failed"),
            }
            for item in ingest_results
            if not bool(getattr(item, "success", False))
        ]
        urls_ingested = sum(1 for item in ingest_results if bool(getattr(item, "success", False)))

        stimuli = self.stimulus_processor.process_ingested(ingest_results)
        write_result = self.write_gateway.write_environment_stimuli(stimuli)

        wakeup_results = self.wakeup_loop.run(
            max_cycles=max_cycles,
            dream_kwargs={
                "limit": limit,
                "min_priority": min_priority,
                "related_limit": related_limit,
                "crystal_count": crystal_count,
                "generate_reflection": generate_reflection,
                "require_inference_ready": require_inference_ready,
                "inference_timeout_seconds": inference_timeout_seconds,
            },
        )
        wakeup_rows = [result.to_dict() for result in wakeup_results]
        runtime_state = self.wakeup_loop.get_runtime_state_snapshot()
        wakeup_payload: dict[str, object] = {
            "generated_at": _iso_now(),
            "overall_status": _derive_overall_status(wakeup_rows),
            "config": {
                "interval_seconds": float(self.interval_seconds),
                "max_cycles": int(max_cycles),
                "limit": int(limit),
                "min_priority": float(min_priority),
                "related_limit": int(related_limit),
                "crystal_count": int(crystal_count),
                "generate_reflection": bool(generate_reflection),
                "require_inference_ready": bool(require_inference_ready),
                "inference_timeout_seconds": float(inference_timeout_seconds),
            },
            "runtime_state": runtime_state,
            "results": wakeup_rows,
        }
        _write_json(self.snapshot_path, wakeup_payload)
        _append_jsonl(self.history_path, wakeup_rows)

        dashboard_payload = build_dashboard(
            journal_path=self.journal_path,
            wakeup_path=self.history_path,
        )
        _write_json(self.dashboard_out_dir / JSON_FILENAME, dashboard_payload)
        _write_text(self.dashboard_out_dir / HTML_FILENAME, render_html(dashboard_payload))

        overall_ok = bool(dashboard_payload.get("overall_ok", True)) and not ingestion_failures
        return AutonomousCycleResult(
            generated_at=_iso_now(),
            urls_requested=len(resolved_urls),
            urls_ingested=urls_ingested,
            urls_failed=len(ingestion_failures),
            stimuli_processed=len(stimuli),
            memory_write=write_result,
            wakeup_overall_status=str(wakeup_payload.get("overall_status") or "idle"),
            wakeup_cycle_count=len(wakeup_rows),
            dashboard_overall_ok=bool(dashboard_payload.get("overall_ok", True)),
            paths={
                "history_path": self.history_path.as_posix(),
                "snapshot_path": self.snapshot_path.as_posix(),
                "state_path": self.state_path.as_posix(),
                "dashboard_json_path": (self.dashboard_out_dir / JSON_FILENAME).as_posix(),
                "dashboard_html_path": (self.dashboard_out_dir / HTML_FILENAME).as_posix(),
            },
            ingestion_failures=ingestion_failures,
            wakeup_payload=wakeup_payload,
            runtime_state=runtime_state,
            dashboard_payload=dashboard_payload,
            overall_ok=overall_ok,
        )


def build_autonomous_cycle_runner(
    *,
    db_path: Optional[Path] = None,
    crystal_path: Optional[Path] = None,
    journal_path: Path = Path("memory/self_journal.jsonl"),
    history_path: Path = Path("memory/autonomous/dream_wakeup_history.jsonl"),
    snapshot_path: Path = Path("docs/status/dream_wakeup_snapshot_latest.json"),
    state_path: Path = Path("memory/autonomous/dream_wakeup_state.json"),
    dashboard_out_dir: Path = Path("docs/status"),
    interval_seconds: float = 0.0,
    enable_scribe: bool = True,
    scribe_out_dir: Path = Path("docs/chronicles"),
    scribe_status_path: Path = Path("docs/status/scribe_status_latest.json"),
    scribe_state_path: Path = Path("memory/autonomous/dream_wakeup_scribe_state.json"),
) -> AutonomousDreamCycleRunner:
    return AutonomousDreamCycleRunner(
        db_path=db_path,
        crystal_path=crystal_path,
        journal_path=journal_path,
        history_path=history_path,
        snapshot_path=snapshot_path,
        state_path=state_path,
        dashboard_out_dir=dashboard_out_dir,
        interval_seconds=interval_seconds,
        enable_scribe=enable_scribe,
        scribe_out_dir=scribe_out_dir,
        scribe_status_path=scribe_status_path,
        scribe_state_path=scribe_state_path,
    )


__all__ = [
    "AutonomousCycleResult",
    "AutonomousDreamCycleRunner",
    "build_autonomous_cycle_runner",
]
