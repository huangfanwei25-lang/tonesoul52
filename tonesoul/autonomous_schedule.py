from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, Sequence

from tonesoul.autonomous_cycle import build_autonomous_cycle_runner
from tonesoul.dream_observability import HTML_FILENAME, JSON_FILENAME, build_dashboard, render_html
from tonesoul.perception.source_registry import CuratedSourceSelection, select_curated_registry_urls

SleepFunc = Callable[[float], None]


class AutonomousCycleRunnerLike(Protocol):
    def run(self, **kwargs: Any) -> Any: ...


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@dataclass
class RegistryEntryState:
    last_selected_cycle: int = 0
    backoff_until_cycle: int = 0
    consecutive_failures: int = 0
    last_outcome: str = "unknown"
    updated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_selected_cycle": int(self.last_selected_cycle),
            "backoff_until_cycle": int(self.backoff_until_cycle),
            "consecutive_failures": int(self.consecutive_failures),
            "last_outcome": self.last_outcome,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RegistryEntryState":
        return cls(
            last_selected_cycle=max(0, int(payload.get("last_selected_cycle", 0) or 0)),
            backoff_until_cycle=max(0, int(payload.get("backoff_until_cycle", 0) or 0)),
            consecutive_failures=max(0, int(payload.get("consecutive_failures", 0) or 0)),
            last_outcome=str(payload.get("last_outcome") or "unknown"),
            updated_at=str(payload.get("updated_at") or _iso_now()),
        )


@dataclass
class RegistryCategoryState:
    tension_cooldown_until_cycle: int = 0
    last_budget_status: str = "unknown"
    last_breach_reasons: list[str] = field(default_factory=list)
    last_max_friction_score: float | None = None
    last_max_lyapunov_proxy: float | None = None
    last_council_count: int = 0
    last_llm_preflight_latency_ms: int | None = None
    last_llm_selection_latency_ms: int | None = None
    last_llm_probe_latency_ms: int | None = None
    last_llm_preflight_timeout_count: int = 0
    updated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tension_cooldown_until_cycle": int(self.tension_cooldown_until_cycle),
            "last_budget_status": self.last_budget_status,
            "last_breach_reasons": list(self.last_breach_reasons),
            "last_max_friction_score": (
                None
                if self.last_max_friction_score is None
                else round(float(self.last_max_friction_score), 4)
            ),
            "last_max_lyapunov_proxy": (
                None
                if self.last_max_lyapunov_proxy is None
                else round(float(self.last_max_lyapunov_proxy), 4)
            ),
            "last_council_count": int(self.last_council_count),
            "last_llm_preflight_latency_ms": (
                None
                if self.last_llm_preflight_latency_ms is None
                else int(self.last_llm_preflight_latency_ms)
            ),
            "last_llm_selection_latency_ms": (
                None
                if self.last_llm_selection_latency_ms is None
                else int(self.last_llm_selection_latency_ms)
            ),
            "last_llm_probe_latency_ms": (
                None
                if self.last_llm_probe_latency_ms is None
                else int(self.last_llm_probe_latency_ms)
            ),
            "last_llm_preflight_timeout_count": int(self.last_llm_preflight_timeout_count),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RegistryCategoryState":
        def _maybe_float(value: Any) -> float | None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return cls(
            tension_cooldown_until_cycle=max(
                0, int(payload.get("tension_cooldown_until_cycle", 0) or 0)
            ),
            last_budget_status=str(payload.get("last_budget_status") or "unknown"),
            last_breach_reasons=[
                str(item).strip()
                for item in payload.get("last_breach_reasons", [])
                if str(item).strip()
            ],
            last_max_friction_score=_maybe_float(payload.get("last_max_friction_score")),
            last_max_lyapunov_proxy=_maybe_float(payload.get("last_max_lyapunov_proxy")),
            last_council_count=max(0, int(payload.get("last_council_count", 0) or 0)),
            last_llm_preflight_latency_ms=(
                None
                if payload.get("last_llm_preflight_latency_ms") in (None, "")
                else max(0, int(payload.get("last_llm_preflight_latency_ms", 0) or 0))
            ),
            last_llm_selection_latency_ms=(
                None
                if payload.get("last_llm_selection_latency_ms") in (None, "")
                else max(0, int(payload.get("last_llm_selection_latency_ms", 0) or 0))
            ),
            last_llm_probe_latency_ms=(
                None
                if payload.get("last_llm_probe_latency_ms") in (None, "")
                else max(0, int(payload.get("last_llm_probe_latency_ms", 0) or 0))
            ),
            last_llm_preflight_timeout_count=max(
                0, int(payload.get("last_llm_preflight_timeout_count", 0) or 0)
            ),
            updated_at=str(payload.get("updated_at") or _iso_now()),
        )


@dataclass
class LLMBackoffState:
    backoff_until_cycle: int = 0
    last_status: str = "idle"
    last_mode: str = "none"
    last_breach_reasons: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backoff_until_cycle": int(self.backoff_until_cycle),
            "last_status": self.last_status,
            "last_mode": self.last_mode,
            "last_breach_reasons": list(self.last_breach_reasons),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LLMBackoffState":
        return cls(
            backoff_until_cycle=max(0, int(payload.get("backoff_until_cycle", 0) or 0)),
            last_status=str(payload.get("last_status") or "idle"),
            last_mode=str(payload.get("last_mode") or "none"),
            last_breach_reasons=[
                str(item).strip()
                for item in payload.get("last_breach_reasons", [])
                if str(item).strip()
            ],
            updated_at=str(payload.get("updated_at") or _iso_now()),
        )


@dataclass
class RegistryScheduleState:
    cursor: int = 0
    category_cursor: int = 0
    cycles_run: int = 0
    updated_at: str = field(default_factory=_iso_now)
    last_entry_ids: list[str] = field(default_factory=list)
    entry_states: dict[str, RegistryEntryState] = field(default_factory=dict)
    category_entry_cursors: dict[str, int] = field(default_factory=dict)
    category_states: dict[str, RegistryCategoryState] = field(default_factory=dict)
    llm_backoff: LLMBackoffState = field(default_factory=LLMBackoffState)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cursor": int(self.cursor),
            "category_cursor": int(self.category_cursor),
            "cycles_run": int(self.cycles_run),
            "updated_at": self.updated_at,
            "last_entry_ids": list(self.last_entry_ids),
            "entry_states": {
                str(key): value.to_dict() for key, value in sorted(self.entry_states.items())
            },
            "category_entry_cursors": {
                str(key): int(value) for key, value in sorted(self.category_entry_cursors.items())
            },
            "category_states": {
                str(key): value.to_dict() for key, value in sorted(self.category_states.items())
            },
            "llm_backoff": self.llm_backoff.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RegistryScheduleState":
        raw_entry_states = payload.get("entry_states", {})
        raw_category_entry_cursors = payload.get("category_entry_cursors", {})
        raw_category_states = payload.get("category_states", {})
        raw_llm_backoff = payload.get("llm_backoff", {})
        entry_states: dict[str, RegistryEntryState] = {}
        if isinstance(raw_entry_states, dict):
            for raw_key, raw_value in raw_entry_states.items():
                key = str(raw_key).strip()
                if not key or not isinstance(raw_value, dict):
                    continue
                entry_states[key] = RegistryEntryState.from_dict(raw_value)
        category_entry_cursors: dict[str, int] = {}
        if isinstance(raw_category_entry_cursors, dict):
            for raw_key, raw_value in raw_category_entry_cursors.items():
                key = str(raw_key).strip().lower()
                if not key:
                    continue
                try:
                    parsed = int(raw_value or 0)
                except (TypeError, ValueError):
                    parsed = 0
                category_entry_cursors[key] = max(0, parsed)
        category_states: dict[str, RegistryCategoryState] = {}
        if isinstance(raw_category_states, dict):
            for raw_key, raw_value in raw_category_states.items():
                key = str(raw_key).strip().lower()
                if not key or not isinstance(raw_value, dict):
                    continue
                category_states[key] = RegistryCategoryState.from_dict(raw_value)
        return cls(
            cursor=max(0, int(payload.get("cursor", 0) or 0)),
            category_cursor=max(0, int(payload.get("category_cursor", 0) or 0)),
            cycles_run=max(0, int(payload.get("cycles_run", 0) or 0)),
            updated_at=str(payload.get("updated_at") or _iso_now()),
            last_entry_ids=[
                str(item).strip() for item in payload.get("last_entry_ids", []) if str(item).strip()
            ],
            entry_states=entry_states,
            category_entry_cursors=category_entry_cursors,
            category_states=category_states,
            llm_backoff=(
                LLMBackoffState.from_dict(raw_llm_backoff)
                if isinstance(raw_llm_backoff, dict)
                else LLMBackoffState()
            ),
        )


@dataclass
class RegistryScheduleBatch:
    cycle: int
    absolute_cycle: int
    cursor_before: int
    cursor_after: int
    eligible_entry_count: int
    selection_mode: str = "entry_round_robin"
    selected_entry_ids: list[str] = field(default_factory=list)
    selected_categories: list[str] = field(default_factory=list)
    selected_urls: list[str] = field(default_factory=list)
    selected_entries: list[dict[str, Any]] = field(default_factory=list)
    category_slots: list[str] = field(default_factory=list)
    category_cursor_before: int | None = None
    category_cursor_after: int | None = None
    category_entry_cursor_updates: dict[str, int] = field(default_factory=dict)
    category_policy_trace: list[dict[str, Any]] = field(default_factory=list)
    deferred_categories: list[dict[str, Any]] = field(default_factory=list)
    deferred_entries: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ok: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": int(self.cycle),
            "absolute_cycle": int(self.absolute_cycle),
            "cursor_before": int(self.cursor_before),
            "cursor_after": int(self.cursor_after),
            "eligible_entry_count": int(self.eligible_entry_count),
            "selection_mode": self.selection_mode,
            "selected_entry_ids": list(self.selected_entry_ids),
            "selected_categories": list(self.selected_categories),
            "selected_url_count": len(self.selected_urls),
            "selected_urls": list(self.selected_urls),
            "selected_entries": list(self.selected_entries),
            "category_slots": list(self.category_slots),
            "category_cursor_before": (
                None if self.category_cursor_before is None else int(self.category_cursor_before)
            ),
            "category_cursor_after": (
                None if self.category_cursor_after is None else int(self.category_cursor_after)
            ),
            "category_entry_cursor_updates": {
                str(key): int(value)
                for key, value in sorted(self.category_entry_cursor_updates.items())
            },
            "category_policy_trace": list(self.category_policy_trace),
            "deferred_category_count": len(self.deferred_categories),
            "deferred_categories": list(self.deferred_categories),
            "deferred_entry_count": len(self.deferred_entries),
            "deferred_entries": list(self.deferred_entries),
            "warning_count": len(self.warnings),
            "warnings": list(self.warnings),
            "ok": bool(self.ok),
        }


@dataclass
class RegistryScheduleCycleResult:
    cycle: int
    started_at: str
    finished_at: str
    duration_ms: int
    registry_batch: RegistryScheduleBatch
    autonomous_payload: dict[str, Any] = field(default_factory=dict)
    tension_budget: dict[str, Any] = field(default_factory=dict)
    overall_ok: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": int(self.cycle),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": int(self.duration_ms),
            "registry_batch": self.registry_batch.to_dict(),
            "autonomous_payload": dict(self.autonomous_payload),
            "tension_budget": dict(self.tension_budget),
            "overall_ok": bool(self.overall_ok),
        }


class AutonomousRegistrySchedule:
    """
    Host-driven schedule loop that rotates across approved registry entries.

    This layer composes curated source selection with the one-shot autonomous
    cycle runner. Governance policy stays inside the registry helper and the
    existing runtime seams.
    """

    def __init__(
        self,
        *,
        runner: Optional[AutonomousCycleRunnerLike] = None,
        registry_path: Path = Path("spec/external_source_registry.yaml"),
        state_path: Path = Path("memory/autonomous/registry_schedule_state.json"),
        snapshot_path: Path = Path("docs/status/autonomous_registry_schedule_latest.json"),
        history_path: Path = Path("memory/autonomous/registry_schedule_history.jsonl"),
        journal_path: Optional[Path] = None,
        wakeup_path: Optional[Path] = None,
        dashboard_out_dir: Optional[Path] = None,
        interval_seconds: float = 10800.0,
        sleep_func: SleepFunc = time.sleep,
    ) -> None:
        self.runner = runner or build_autonomous_cycle_runner(interval_seconds=0.0)
        self.registry_path = Path(registry_path)
        self.state_path = Path(state_path)
        self.snapshot_path = Path(snapshot_path)
        self.history_path = Path(history_path)
        self.journal_path = None if journal_path is None else Path(journal_path)
        self.wakeup_path = None if wakeup_path is None else Path(wakeup_path)
        self.dashboard_out_dir = None if dashboard_out_dir is None else Path(dashboard_out_dir)
        self.interval_seconds = max(0.0, float(interval_seconds))
        self._sleep = sleep_func

    def _load_state(self) -> RegistryScheduleState:
        if not self.state_path.exists():
            return RegistryScheduleState()
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return RegistryScheduleState()
        if not isinstance(payload, dict):
            return RegistryScheduleState()
        return RegistryScheduleState.from_dict(payload)

    def _write_state(self, state: RegistryScheduleState) -> None:
        _write_json(self.state_path, state.to_dict())

    @staticmethod
    def _derive_failed_urls(autonomous_payload: dict[str, Any]) -> set[str]:
        failures = autonomous_payload.get("ingestion_failures", [])
        if not isinstance(failures, list):
            return set()
        urls: set[str] = set()
        for item in failures:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "").strip()
            if url:
                urls.add(url)
        return urls

    @staticmethod
    def _operational_defer_reason(
        *,
        entry_id: str,
        entry_state: RegistryEntryState,
        absolute_cycle: int,
        revisit_interval_cycles: int,
    ) -> dict[str, Any] | None:
        if entry_state.backoff_until_cycle > 0 and absolute_cycle <= int(
            entry_state.backoff_until_cycle
        ):
            return {
                "id": entry_id,
                "reason": "failure_backoff",
                "available_after_cycle": int(entry_state.backoff_until_cycle) + 1,
                "consecutive_failures": int(entry_state.consecutive_failures),
            }

        if (
            revisit_interval_cycles > 0
            and entry_state.last_selected_cycle > 0
            and absolute_cycle <= int(entry_state.last_selected_cycle) + revisit_interval_cycles
        ):
            return {
                "id": entry_id,
                "reason": "revisit_cooldown",
                "available_after_cycle": int(entry_state.last_selected_cycle)
                + int(revisit_interval_cycles)
                + 1,
                "last_selected_cycle": int(entry_state.last_selected_cycle),
            }
        return None

    @staticmethod
    def _category_defer_reason(
        *,
        category: str,
        category_state: RegistryCategoryState,
        absolute_cycle: int,
    ) -> dict[str, Any] | None:
        if category_state.tension_cooldown_until_cycle > 0 and absolute_cycle <= int(
            category_state.tension_cooldown_until_cycle
        ):
            return {
                "category": category,
                "reason": "tension_budget_cooldown",
                "available_after_cycle": int(category_state.tension_cooldown_until_cycle) + 1,
                "last_budget_status": category_state.last_budget_status,
                "last_breach_reasons": list(category_state.last_breach_reasons),
            }
        return None

    @staticmethod
    def _normalize_category_policy(policy: dict[str, int] | None) -> dict[str, int]:
        normalized: dict[str, int] = {}
        for raw_key, raw_value in (policy or {}).items():
            key = str(raw_key).strip().lower()
            if not key:
                continue
            try:
                parsed = int(raw_value)
            except (TypeError, ValueError):
                parsed = 1
            normalized[key] = max(1, parsed)
        return normalized

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _extract_tension_budget_observation(
        self, autonomous_payload: dict[str, Any]
    ) -> dict[str, Any]:
        wakeup_payload = (
            autonomous_payload.get("wakeup_payload")
            if isinstance(autonomous_payload.get("wakeup_payload"), dict)
            else {}
        )
        results = wakeup_payload.get("results", [])
        if not isinstance(results, list):
            results = []

        max_friction_score: float | None = None
        max_lyapunov_proxy: float | None = None
        council_count = 0
        max_llm_preflight_latency_ms: int | None = None
        max_llm_selection_latency_ms: int | None = None
        max_llm_probe_latency_ms: int | None = None
        llm_preflight_timeout_count = 0
        max_consecutive_failure_count = 0
        observed_cycles = 0
        for item in results:
            if not isinstance(item, dict):
                continue
            summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
            friction = self._coerce_float(summary.get("max_friction_score"))
            lyapunov = self._coerce_float(summary.get("max_lyapunov_proxy"))
            if friction is not None:
                max_friction_score = (
                    friction if max_friction_score is None else max(max_friction_score, friction)
                )
            if lyapunov is not None:
                max_lyapunov_proxy = (
                    lyapunov if max_lyapunov_proxy is None else max(max_lyapunov_proxy, lyapunov)
                )
            try:
                council_count += int(summary.get("council_count", 0) or 0)
            except (TypeError, ValueError):
                pass
            try:
                latency = summary.get("llm_preflight_latency_ms")
                if latency not in (None, ""):
                    parsed = max(0, int(latency))
                    max_llm_preflight_latency_ms = (
                        parsed
                        if max_llm_preflight_latency_ms is None
                        else max(max_llm_preflight_latency_ms, parsed)
                    )
            except (TypeError, ValueError):
                pass
            try:
                selection_latency = summary.get("llm_preflight_selection_latency_ms")
                if selection_latency not in (None, ""):
                    parsed = max(0, int(selection_latency))
                    max_llm_selection_latency_ms = (
                        parsed
                        if max_llm_selection_latency_ms is None
                        else max(max_llm_selection_latency_ms, parsed)
                    )
            except (TypeError, ValueError):
                pass
            try:
                probe_latency = summary.get("llm_preflight_probe_latency_ms")
                if probe_latency not in (None, ""):
                    parsed = max(0, int(probe_latency))
                    max_llm_probe_latency_ms = (
                        parsed
                        if max_llm_probe_latency_ms is None
                        else max(max_llm_probe_latency_ms, parsed)
                    )
            except (TypeError, ValueError):
                pass
            try:
                llm_preflight_timeout_count += int(
                    summary.get("llm_preflight_timeout_count", 0) or 0
                )
            except (TypeError, ValueError):
                pass
            try:
                max_consecutive_failure_count = max(
                    max_consecutive_failure_count,
                    int(summary.get("consecutive_failure_count", 0) or 0),
                )
            except (TypeError, ValueError):
                pass
            observed_cycles += 1

        runtime_state = (
            autonomous_payload.get("runtime_state")
            if isinstance(autonomous_payload.get("runtime_state"), dict)
            else {}
        )
        try:
            max_consecutive_failure_count = max(
                max_consecutive_failure_count,
                int(runtime_state.get("consecutive_failures", 0) or 0),
            )
        except (TypeError, ValueError):
            pass

        return {
            "observed_cycles": int(observed_cycles),
            "max_friction_score": (
                None if max_friction_score is None else round(float(max_friction_score), 4)
            ),
            "max_lyapunov_proxy": (
                None if max_lyapunov_proxy is None else round(float(max_lyapunov_proxy), 4)
            ),
            "council_count": int(council_count),
            "max_llm_preflight_latency_ms": max_llm_preflight_latency_ms,
            "max_llm_selection_latency_ms": max_llm_selection_latency_ms,
            "max_llm_probe_latency_ms": max_llm_probe_latency_ms,
            "llm_preflight_timeout_count": int(llm_preflight_timeout_count),
            "max_consecutive_failure_count": int(max_consecutive_failure_count),
        }

    @staticmethod
    def _derive_llm_backoff_mode(llm_breach_reasons: Sequence[str]) -> str:
        reasons = [str(item).strip() for item in llm_breach_reasons if str(item).strip()]
        has_timeout = any("llm_preflight_timeout_count>" in item for item in reasons)
        has_probe = any("llm_probe_latency_ms>" in item for item in reasons)
        has_selection = any("llm_selection_latency_ms>" in item for item in reasons)
        has_total = any("llm_preflight_latency_ms>" in item for item in reasons)
        if (has_probe or has_timeout) and has_selection:
            return "mixed_latency"
        if has_timeout or has_probe:
            return "probe_latency"
        if has_selection:
            return "selection_latency"
        if has_total:
            return "preflight_latency"
        return "llm_budget"

    def _evaluate_tension_budget(
        self,
        *,
        autonomous_payload: dict[str, Any],
        max_friction_score: float | None,
        max_lyapunov_proxy: float | None,
        max_council_count: int | None,
        max_llm_preflight_latency_ms: int | None,
        max_llm_selection_latency_ms: int | None,
        max_llm_probe_latency_ms: int | None,
        max_llm_timeout_count: int | None,
        max_consecutive_failure_count: int | None,
        cooldown_cycles: int,
        selected_categories: Sequence[str],
    ) -> dict[str, Any]:
        observation = self._extract_tension_budget_observation(autonomous_payload)
        thresholds = {
            "max_friction_score": (
                None if max_friction_score is None else round(float(max_friction_score), 4)
            ),
            "max_lyapunov_proxy": (
                None if max_lyapunov_proxy is None else round(float(max_lyapunov_proxy), 4)
            ),
            "max_council_count": (None if max_council_count is None else int(max_council_count)),
            "max_llm_preflight_latency_ms": (
                None if max_llm_preflight_latency_ms is None else int(max_llm_preflight_latency_ms)
            ),
            "max_llm_selection_latency_ms": (
                None if max_llm_selection_latency_ms is None else int(max_llm_selection_latency_ms)
            ),
            "max_llm_probe_latency_ms": (
                None if max_llm_probe_latency_ms is None else int(max_llm_probe_latency_ms)
            ),
            "max_llm_timeout_count": (
                None if max_llm_timeout_count is None else int(max_llm_timeout_count)
            ),
            "max_consecutive_failure_count": (
                None
                if max_consecutive_failure_count is None
                else int(max_consecutive_failure_count)
            ),
            "cooldown_cycles": max(0, int(cooldown_cycles)),
        }
        enabled = any(
            value is not None for key, value in thresholds.items() if key != "cooldown_cycles"
        )
        breach_reasons: list[str] = []
        observed_friction = self._coerce_float(observation.get("max_friction_score"))
        observed_lyapunov = self._coerce_float(observation.get("max_lyapunov_proxy"))
        observed_council_count = int(observation.get("council_count", 0) or 0)
        observed_llm_preflight_latency_ms = observation.get("max_llm_preflight_latency_ms")
        observed_llm_selection_latency_ms = observation.get("max_llm_selection_latency_ms")
        observed_llm_probe_latency_ms = observation.get("max_llm_probe_latency_ms")
        observed_llm_timeout_count = int(observation.get("llm_preflight_timeout_count", 0) or 0)
        observed_consecutive_failure_count = int(
            observation.get("max_consecutive_failure_count", 0) or 0
        )
        governance_breach_reasons: list[str] = []
        llm_breach_reasons: list[str] = []

        if (
            max_friction_score is not None
            and observed_friction is not None
            and observed_friction > float(max_friction_score)
        ):
            reason = (
                "max_friction_score>"
                f"{round(float(max_friction_score), 4)}"
                f" (observed={round(float(observed_friction), 4)})"
            )
            breach_reasons.append(reason)
            governance_breach_reasons.append(reason)
        if (
            max_lyapunov_proxy is not None
            and observed_lyapunov is not None
            and observed_lyapunov > float(max_lyapunov_proxy)
        ):
            reason = (
                "max_lyapunov_proxy>"
                f"{round(float(max_lyapunov_proxy), 4)}"
                f" (observed={round(float(observed_lyapunov), 4)})"
            )
            breach_reasons.append(reason)
            governance_breach_reasons.append(reason)
        if max_council_count is not None and observed_council_count > int(max_council_count):
            reason = (
                "council_count>"
                f"{int(max_council_count)}"
                f" (observed={int(observed_council_count)})"
            )
            breach_reasons.append(reason)
            governance_breach_reasons.append(reason)
        if (
            max_llm_preflight_latency_ms is not None
            and isinstance(observed_llm_preflight_latency_ms, int)
            and observed_llm_preflight_latency_ms > int(max_llm_preflight_latency_ms)
        ):
            reason = (
                "llm_preflight_latency_ms>"
                f"{int(max_llm_preflight_latency_ms)}"
                f" (observed={int(observed_llm_preflight_latency_ms)})"
            )
            breach_reasons.append(reason)
            llm_breach_reasons.append(reason)
        if (
            max_llm_selection_latency_ms is not None
            and isinstance(observed_llm_selection_latency_ms, int)
            and observed_llm_selection_latency_ms > int(max_llm_selection_latency_ms)
        ):
            reason = (
                "llm_selection_latency_ms>"
                f"{int(max_llm_selection_latency_ms)}"
                f" (observed={int(observed_llm_selection_latency_ms)})"
            )
            breach_reasons.append(reason)
            llm_breach_reasons.append(reason)
        if (
            max_llm_probe_latency_ms is not None
            and isinstance(observed_llm_probe_latency_ms, int)
            and observed_llm_probe_latency_ms > int(max_llm_probe_latency_ms)
        ):
            reason = (
                "llm_probe_latency_ms>"
                f"{int(max_llm_probe_latency_ms)}"
                f" (observed={int(observed_llm_probe_latency_ms)})"
            )
            breach_reasons.append(reason)
            llm_breach_reasons.append(reason)
        if max_llm_timeout_count is not None and observed_llm_timeout_count > int(
            max_llm_timeout_count
        ):
            reason = (
                "llm_preflight_timeout_count>"
                f"{int(max_llm_timeout_count)}"
                f" (observed={int(observed_llm_timeout_count)})"
            )
            breach_reasons.append(reason)
            llm_breach_reasons.append(reason)
        if max_consecutive_failure_count is not None and observed_consecutive_failure_count > int(
            max_consecutive_failure_count
        ):
            reason = (
                "consecutive_failure_count>"
                f"{int(max_consecutive_failure_count)}"
                f" (observed={int(observed_consecutive_failure_count)})"
            )
            breach_reasons.append(reason)
            governance_breach_reasons.append(reason)

        cooled_categories = sorted(
            {str(item).strip().lower() for item in selected_categories if str(item).strip()}
        )
        breached = bool(enabled and breach_reasons)
        governance_breached = bool(enabled and governance_breach_reasons)
        llm_breached = bool(enabled and llm_breach_reasons)
        return {
            "enabled": enabled,
            "thresholds": thresholds,
            "observation": observation,
            "breached": breached,
            "breach_reason_count": len(breach_reasons),
            "breach_reasons": breach_reasons,
            "governance_breach_reason_count": len(governance_breach_reasons),
            "governance_breach_reasons": governance_breach_reasons,
            "governance_breached": governance_breached,
            "llm_breach_reason_count": len(llm_breach_reasons),
            "llm_breach_reasons": llm_breach_reasons,
            "llm_breached": llm_breached,
            "llm_backoff_mode": (
                self._derive_llm_backoff_mode(llm_breach_reasons) if llm_breached else "none"
            ),
            "cooldown_cycles": max(0, int(cooldown_cycles)),
            "cooled_categories": (
                cooled_categories if governance_breached and cooldown_cycles > 0 else []
            ),
            "llm_backoff_requested": bool(llm_breached and cooldown_cycles > 0),
        }

    @staticmethod
    def _build_weighted_category_slots(
        eligible_entries: Sequence[dict[str, Any]],
        category_weights: dict[str, int],
    ) -> list[str]:
        ordered_categories: list[str] = []
        seen_categories: set[str] = set()
        for entry in eligible_entries:
            category = str(entry.get("category") or "").strip().lower()
            if not category or category in seen_categories:
                continue
            ordered_categories.append(category)
            seen_categories.add(category)

        slots: list[str] = []
        for category in ordered_categories:
            weight = max(1, int(category_weights.get(category, 1)))
            slots.extend([category] * weight)
        return slots

    def _select_weighted_entries(
        self,
        *,
        eligible_entries: Sequence[dict[str, Any]],
        state: RegistryScheduleState,
        absolute_cycle: int,
        entry_count: int,
        url_cap: Optional[int],
        revisit_interval_cycles: int,
        category_weights: dict[str, int],
    ) -> dict[str, Any]:
        entries_by_category: dict[str, list[dict[str, Any]]] = {}
        for raw_entry in eligible_entries:
            category = str(raw_entry.get("category") or "").strip().lower()
            entries_by_category.setdefault(category, []).append(raw_entry)

        category_slots = self._build_weighted_category_slots(eligible_entries, category_weights)
        category_cursor_before = (
            int(state.category_cursor) % len(category_slots) if category_slots else None
        )
        category_cursor_after = category_cursor_before
        category_entry_cursors = {
            str(key).strip().lower(): max(0, int(value))
            for key, value in state.category_entry_cursors.items()
            if str(key).strip()
        }
        selected_entries: list[dict[str, Any]] = []
        selected_entry_ids: list[str] = []
        selected_categories: list[str] = []
        selected_urls: list[str] = []
        deferred_categories: list[dict[str, Any]] = []
        deferred_entries: list[dict[str, Any]] = []
        deferred_category_names: set[str] = set()
        deferred_ids: set[str] = set()
        seen_urls: set[str] = set()
        selected_id_set: set[str] = set()
        trace: list[dict[str, Any]] = []

        if not category_slots:
            return {
                "selection_mode": "category_weighted_round_robin",
                "selected_entries": selected_entries,
                "selected_entry_ids": selected_entry_ids,
                "selected_categories": selected_categories,
                "selected_urls": selected_urls,
                "deferred_categories": deferred_categories,
                "deferred_entries": deferred_entries,
                "category_slots": category_slots,
                "category_cursor_before": category_cursor_before,
                "category_cursor_after": category_cursor_after,
                "category_entry_cursor_updates": category_entry_cursors,
                "category_policy_trace": trace,
            }

        slot_index = int(category_cursor_before or 0)
        max_slot_attempts = max(len(category_slots), int(entry_count) * len(category_slots))
        slot_attempts = 0
        while slot_attempts < max_slot_attempts and len(selected_entries) < int(entry_count):
            if url_cap is not None and len(selected_urls) >= int(url_cap):
                break

            slot_position = slot_index % len(category_slots)
            category = category_slots[slot_position]
            weight = max(1, int(category_weights.get(category, 1)))
            category_entries = entries_by_category.get(category, [])
            category_state = state.category_states.get(category, RegistryCategoryState())
            category_defer_reason = self._category_defer_reason(
                category=category,
                category_state=category_state,
                absolute_cycle=absolute_cycle,
            )
            if category_defer_reason is not None:
                if category not in deferred_category_names:
                    enriched_category_reason = dict(category_defer_reason)
                    enriched_category_reason["weight"] = int(weight)
                    deferred_categories.append(enriched_category_reason)
                    deferred_category_names.add(category)
                trace.append(
                    {
                        "slot": int(slot_position),
                        "category": category,
                        "weight": int(weight),
                        "action": "tension_budget_cooldown",
                    }
                )
                slot_index += 1
                slot_attempts += 1
                continue
            if not category_entries:
                trace.append(
                    {
                        "slot": int(slot_position),
                        "category": category,
                        "weight": int(weight),
                        "action": "empty_category",
                    }
                )
                slot_index += 1
                slot_attempts += 1
                continue

            start_cursor = int(category_entry_cursors.get(category, 0)) % len(category_entries)
            entry_index = start_cursor
            scanned = 0
            slot_action = "no_candidate"
            selected_entry: dict[str, Any] | None = None
            next_cursor = start_cursor
            while scanned < len(category_entries):
                raw_entry = category_entries[entry_index]
                entry_id = str(raw_entry.get("id") or "").strip()
                if entry_id in selected_id_set:
                    slot_action = "batch_duplicate"
                    scanned += 1
                    entry_index = (entry_index + 1) % len(category_entries)
                    continue

                entry_state = state.entry_states.get(entry_id, RegistryEntryState())
                defer_reason = self._operational_defer_reason(
                    entry_id=entry_id,
                    entry_state=entry_state,
                    absolute_cycle=absolute_cycle,
                    revisit_interval_cycles=max(0, int(revisit_interval_cycles)),
                )
                if defer_reason is not None:
                    slot_action = str(defer_reason.get("reason") or "deferred")
                    if entry_id and entry_id not in deferred_ids:
                        enriched_reason = dict(defer_reason)
                        enriched_reason["category"] = category
                        enriched_reason["weight"] = int(weight)
                        deferred_entries.append(enriched_reason)
                        deferred_ids.add(entry_id)
                    scanned += 1
                    entry_index = (entry_index + 1) % len(category_entries)
                    continue

                selected_entry = dict(raw_entry)
                selected_entry["category"] = category
                selected_entry["category_weight"] = int(weight)
                selected_entry["category_slot"] = int(slot_position)
                selected_entry["selection_mode"] = "category_weighted_round_robin"
                next_cursor = (entry_index + 1) % len(category_entries)
                slot_action = "selected"
                break

            trace_row = {
                "slot": int(slot_position),
                "category": category,
                "weight": int(weight),
                "cursor_before": int(start_cursor),
                "action": slot_action,
            }
            if selected_entry is None:
                trace.append(trace_row)
                slot_index += 1
                slot_attempts += 1
                continue

            category_entry_cursors[category] = int(next_cursor)
            entry_id = str(selected_entry.get("id") or "").strip()
            entry_urls = [
                str(url).strip() for url in selected_entry.get("urls", []) if str(url).strip()
            ]
            kept_urls: list[str] = []
            for url in entry_urls:
                if url in seen_urls:
                    continue
                if url_cap is not None and len(selected_urls) >= int(url_cap):
                    break
                seen_urls.add(url)
                selected_urls.append(url)
                kept_urls.append(url)

            if not kept_urls:
                trace_row["action"] = "url_capped"
                trace.append(trace_row)
                slot_index += 1
                slot_attempts += 1
                continue

            selected_entry["urls"] = kept_urls
            selected_entry["url_count"] = len(kept_urls)
            selected_entries.append(selected_entry)
            selected_entry_ids.append(entry_id)
            selected_categories.append(category)
            selected_id_set.add(entry_id)
            trace_row["entry_id"] = entry_id
            trace_row["cursor_after"] = int(next_cursor)
            trace.append(trace_row)
            slot_index += 1
            slot_attempts += 1

        category_cursor_after = slot_index % len(category_slots)
        return {
            "selection_mode": "category_weighted_round_robin",
            "selected_entries": selected_entries,
            "selected_entry_ids": selected_entry_ids,
            "selected_categories": selected_categories,
            "selected_urls": selected_urls,
            "deferred_categories": deferred_categories,
            "deferred_entries": deferred_entries,
            "category_slots": category_slots,
            "category_cursor_before": category_cursor_before,
            "category_cursor_after": category_cursor_after,
            "category_entry_cursor_updates": category_entry_cursors,
            "category_policy_trace": trace,
        }

    def _build_batch(
        self,
        *,
        cycle: int,
        absolute_cycle: int,
        state: RegistryScheduleState,
        entry_ids: Sequence[str] | None = None,
        categories: Sequence[str] | None = None,
        entries_per_cycle: int = 1,
        urls_per_cycle: Optional[int] = None,
        include_stale: bool = False,
        revisit_interval_cycles: int = 0,
        category_weights: dict[str, int] | None = None,
    ) -> tuple[RegistryScheduleBatch, CuratedSourceSelection]:
        selection = select_curated_registry_urls(
            self.registry_path,
            entry_ids=entry_ids,
            categories=categories,
            include_stale=include_stale,
        )
        eligible_entries = list(selection.selected_entries)
        if not eligible_entries:
            batch = RegistryScheduleBatch(
                cycle=cycle,
                absolute_cycle=absolute_cycle,
                cursor_before=int(state.cursor),
                cursor_after=int(state.cursor),
                eligible_entry_count=0,
                warnings=list(selection.warnings),
                ok=False,
            )
            return batch, selection

        entry_count = max(1, min(int(entries_per_cycle), len(eligible_entries)))
        cursor_before = int(state.cursor) % len(eligible_entries)
        cursor_after = cursor_before
        url_cap = None if urls_per_cycle is None else max(1, int(urls_per_cycle))
        normalized_category_weights = self._normalize_category_policy(category_weights)
        selected_entries: list[dict[str, Any]] = []
        selected_entry_ids: list[str] = []
        selected_categories: list[str] = []
        selected_urls: list[str] = []
        deferred_categories: list[dict[str, Any]] = []
        deferred_entries: list[dict[str, Any]] = []
        selection_mode = "entry_round_robin"
        category_slots: list[str] = []
        category_cursor_before: int | None = None
        category_cursor_after: int | None = None
        category_entry_cursor_updates: dict[str, int] = {}
        category_policy_trace: list[dict[str, Any]] = []

        if normalized_category_weights:
            weighted_selection = self._select_weighted_entries(
                eligible_entries=eligible_entries,
                state=state,
                absolute_cycle=absolute_cycle,
                entry_count=entry_count,
                url_cap=url_cap,
                revisit_interval_cycles=revisit_interval_cycles,
                category_weights=normalized_category_weights,
            )
            selection_mode = str(
                weighted_selection.get("selection_mode") or "category_weighted_round_robin"
            )
            selected_entries = list(weighted_selection.get("selected_entries", []))
            selected_entry_ids = list(weighted_selection.get("selected_entry_ids", []))
            selected_categories = list(weighted_selection.get("selected_categories", []))
            selected_urls = list(weighted_selection.get("selected_urls", []))
            deferred_categories = list(weighted_selection.get("deferred_categories", []))
            deferred_entries = list(weighted_selection.get("deferred_entries", []))
            category_slots = list(weighted_selection.get("category_slots", []))
            category_cursor_before = weighted_selection.get("category_cursor_before")
            category_cursor_after = weighted_selection.get("category_cursor_after")
            category_entry_cursor_updates = {
                str(key).strip().lower(): int(value)
                for key, value in (
                    weighted_selection.get("category_entry_cursor_updates", {}) or {}
                ).items()
                if str(key).strip()
            }
            category_policy_trace = list(weighted_selection.get("category_policy_trace", []))
        else:
            selection_mode = "entry_round_robin"
            selected_entries = []
            selected_entry_ids = []
            selected_urls = []
            deferred_categories = []
            deferred_entries = []
            deferred_category_names: set[str] = set()
            deferred_ids: set[str] = set()
            seen_urls: set[str] = set()
            scanned = 0
            index = cursor_before
            while scanned < len(eligible_entries) and len(selected_entries) < entry_count:
                raw_entry = eligible_entries[index]
                entry = dict(raw_entry)
                entry_id = str(entry.get("id") or "").strip()
                entry_category = str(entry.get("category") or "").strip().lower()
                category_state = state.category_states.get(entry_category, RegistryCategoryState())
                category_defer_reason = self._category_defer_reason(
                    category=entry_category,
                    category_state=category_state,
                    absolute_cycle=absolute_cycle,
                )
                if category_defer_reason is not None:
                    if entry_category and entry_category not in deferred_category_names:
                        deferred_categories.append(category_defer_reason)
                        deferred_category_names.add(entry_category)
                    scanned += 1
                    index = (index + 1) % len(eligible_entries)
                    continue
                entry_state = state.entry_states.get(entry_id, RegistryEntryState())
                defer_reason = self._operational_defer_reason(
                    entry_id=entry_id,
                    entry_state=entry_state,
                    absolute_cycle=absolute_cycle,
                    revisit_interval_cycles=max(0, int(revisit_interval_cycles)),
                )
                if defer_reason is not None:
                    if entry_id and entry_id not in deferred_ids:
                        deferred_entries.append(defer_reason)
                        deferred_ids.add(entry_id)
                    scanned += 1
                    index = (index + 1) % len(eligible_entries)
                    continue

                entry_urls = [str(url).strip() for url in entry.get("urls", []) if str(url).strip()]
                kept_urls: list[str] = []
                for url in entry_urls:
                    if url in seen_urls:
                        continue
                    if url_cap is not None and len(selected_urls) >= url_cap:
                        break
                    seen_urls.add(url)
                    selected_urls.append(url)
                    kept_urls.append(url)
                entry["urls"] = kept_urls
                entry["url_count"] = len(kept_urls)
                selected_entries.append(entry)
                selected_entry_ids.append(entry_id)
                selected_categories.append(entry_category)
                scanned += 1
                index = (index + 1) % len(eligible_entries)
                if url_cap is not None and len(selected_urls) >= url_cap:
                    break

            cursor_after = index if scanned > 0 else cursor_before

        warnings = list(selection.warnings)
        if url_cap is not None and len(selected_urls) >= url_cap:
            warnings.append(f"selected URLs capped at urls_per_cycle={url_cap}")
        if not selected_entries and (deferred_entries or deferred_categories):
            warnings.append("all approved entries are currently deferred by schedule policy")

        batch = RegistryScheduleBatch(
            cycle=cycle,
            absolute_cycle=absolute_cycle,
            cursor_before=cursor_before,
            cursor_after=cursor_after,
            eligible_entry_count=len(eligible_entries),
            selection_mode=selection_mode,
            selected_entry_ids=selected_entry_ids,
            selected_categories=selected_categories,
            selected_urls=selected_urls,
            selected_entries=selected_entries,
            category_slots=category_slots,
            category_cursor_before=category_cursor_before,
            category_cursor_after=category_cursor_after,
            category_entry_cursor_updates=category_entry_cursor_updates,
            category_policy_trace=category_policy_trace,
            deferred_categories=deferred_categories,
            deferred_entries=deferred_entries,
            warnings=warnings,
            ok=bool(selection.ok and selected_urls),
        )
        return batch, selection

    def run(
        self,
        *,
        max_cycles: int = 1,
        entry_ids: Sequence[str] | None = None,
        categories: Sequence[str] | None = None,
        entries_per_cycle: int = 1,
        urls_per_cycle: Optional[int] = None,
        include_stale: bool = False,
        revisit_interval_cycles: int = 0,
        failure_backoff_cycles: int = 0,
        category_weights: dict[str, int] | None = None,
        category_backoff_multipliers: dict[str, int] | None = None,
        tension_max_friction_score: float | None = None,
        tension_max_lyapunov_proxy: float | None = None,
        tension_max_council_count: int | None = None,
        tension_max_llm_preflight_latency_ms: int | None = None,
        tension_max_llm_selection_latency_ms: int | None = None,
        tension_max_llm_probe_latency_ms: int | None = None,
        tension_max_llm_timeout_count: int | None = None,
        tension_max_consecutive_failure_count: int | None = None,
        tension_cooldown_cycles: int = 0,
        cycle_kwargs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        normalized_category_weights = self._normalize_category_policy(category_weights)
        normalized_category_backoff_multipliers = self._normalize_category_policy(
            category_backoff_multipliers
        )
        if int(max_cycles) <= 0:
            payload = {
                "generated_at": _iso_now(),
                "overall_ok": True,
                "config": {
                    "interval_seconds": float(self.interval_seconds),
                    "max_cycles": 0,
                    "entries_per_cycle": int(entries_per_cycle),
                    "urls_per_cycle": None if urls_per_cycle is None else int(urls_per_cycle),
                    "include_stale": bool(include_stale),
                    "revisit_interval_cycles": max(0, int(revisit_interval_cycles)),
                    "failure_backoff_cycles": max(0, int(failure_backoff_cycles)),
                    "category_weights": {
                        key: int(value)
                        for key, value in sorted(normalized_category_weights.items())
                    },
                    "category_backoff_multipliers": {
                        key: int(value)
                        for key, value in sorted(normalized_category_backoff_multipliers.items())
                    },
                    "tension_max_friction_score": (
                        None
                        if tension_max_friction_score is None
                        else round(float(tension_max_friction_score), 4)
                    ),
                    "tension_max_lyapunov_proxy": (
                        None
                        if tension_max_lyapunov_proxy is None
                        else round(float(tension_max_lyapunov_proxy), 4)
                    ),
                    "tension_max_council_count": (
                        None
                        if tension_max_council_count is None
                        else int(tension_max_council_count)
                    ),
                    "tension_max_llm_preflight_latency_ms": (
                        None
                        if tension_max_llm_preflight_latency_ms is None
                        else int(tension_max_llm_preflight_latency_ms)
                    ),
                    "tension_max_llm_selection_latency_ms": (
                        None
                        if tension_max_llm_selection_latency_ms is None
                        else int(tension_max_llm_selection_latency_ms)
                    ),
                    "tension_max_llm_probe_latency_ms": (
                        None
                        if tension_max_llm_probe_latency_ms is None
                        else int(tension_max_llm_probe_latency_ms)
                    ),
                    "tension_max_llm_timeout_count": (
                        None
                        if tension_max_llm_timeout_count is None
                        else int(tension_max_llm_timeout_count)
                    ),
                    "tension_max_consecutive_failure_count": (
                        None
                        if tension_max_consecutive_failure_count is None
                        else int(tension_max_consecutive_failure_count)
                    ),
                    "tension_cooldown_cycles": max(0, int(tension_cooldown_cycles)),
                },
                "results": [],
                "state": self._load_state().to_dict(),
            }
            _write_json(self.snapshot_path, payload)
            return payload

        state = self._load_state()
        rows: list[dict[str, Any]] = []
        config = {
            "interval_seconds": float(self.interval_seconds),
            "max_cycles": int(max_cycles),
            "entries_per_cycle": int(entries_per_cycle),
            "urls_per_cycle": None if urls_per_cycle is None else int(urls_per_cycle),
            "include_stale": bool(include_stale),
            "revisit_interval_cycles": max(0, int(revisit_interval_cycles)),
            "failure_backoff_cycles": max(0, int(failure_backoff_cycles)),
            "category_weights": {
                key: int(value) for key, value in sorted(normalized_category_weights.items())
            },
            "category_backoff_multipliers": {
                key: int(value)
                for key, value in sorted(normalized_category_backoff_multipliers.items())
            },
            "tension_max_friction_score": (
                None
                if tension_max_friction_score is None
                else round(float(tension_max_friction_score), 4)
            ),
            "tension_max_lyapunov_proxy": (
                None
                if tension_max_lyapunov_proxy is None
                else round(float(tension_max_lyapunov_proxy), 4)
            ),
            "tension_max_council_count": (
                None if tension_max_council_count is None else int(tension_max_council_count)
            ),
            "tension_max_llm_preflight_latency_ms": (
                None
                if tension_max_llm_preflight_latency_ms is None
                else int(tension_max_llm_preflight_latency_ms)
            ),
            "tension_max_llm_selection_latency_ms": (
                None
                if tension_max_llm_selection_latency_ms is None
                else int(tension_max_llm_selection_latency_ms)
            ),
            "tension_max_llm_probe_latency_ms": (
                None
                if tension_max_llm_probe_latency_ms is None
                else int(tension_max_llm_probe_latency_ms)
            ),
            "tension_max_llm_timeout_count": (
                None
                if tension_max_llm_timeout_count is None
                else int(tension_max_llm_timeout_count)
            ),
            "tension_max_consecutive_failure_count": (
                None
                if tension_max_consecutive_failure_count is None
                else int(tension_max_consecutive_failure_count)
            ),
            "tension_cooldown_cycles": max(0, int(tension_cooldown_cycles)),
            "entry_ids": [str(item).strip() for item in entry_ids or [] if str(item).strip()],
            "categories": [str(item).strip() for item in categories or [] if str(item).strip()],
        }

        for cycle_index in range(1, int(max_cycles) + 1):
            started_at = _iso_now()
            started_clock = time.perf_counter()
            absolute_cycle = int(state.cycles_run) + 1
            batch, selection = self._build_batch(
                cycle=cycle_index,
                absolute_cycle=absolute_cycle,
                state=state,
                entry_ids=entry_ids,
                categories=categories,
                entries_per_cycle=entries_per_cycle,
                urls_per_cycle=urls_per_cycle,
                include_stale=include_stale,
                revisit_interval_cycles=revisit_interval_cycles,
                category_weights=normalized_category_weights,
            )
            llm_backoff_active = int(state.llm_backoff.backoff_until_cycle) >= absolute_cycle
            effective_cycle_kwargs = dict(cycle_kwargs or {})
            llm_policy = {
                "active": bool(llm_backoff_active),
                "mode": str(state.llm_backoff.last_mode or "none"),
                "backoff_until_cycle": int(state.llm_backoff.backoff_until_cycle),
                "reason_count": len(state.llm_backoff.last_breach_reasons),
                "breach_reasons": list(state.llm_backoff.last_breach_reasons),
            }
            if llm_backoff_active:
                effective_cycle_kwargs["generate_reflection"] = False
                effective_cycle_kwargs["require_inference_ready"] = False
                llm_policy["action"] = "disable_reflection"
            else:
                llm_policy["action"] = "normal"

            autonomous_result = self.runner.run(
                urls=batch.selected_urls,
                max_cycles=1,
                **effective_cycle_kwargs,
            )
            autonomous_payload = (
                autonomous_result.to_dict()
                if hasattr(autonomous_result, "to_dict")
                else dict(autonomous_result)
            )
            autonomous_payload["registry_selection"] = selection.to_dict()
            autonomous_payload["llm_policy"] = dict(llm_policy)
            tension_budget = self._evaluate_tension_budget(
                autonomous_payload=autonomous_payload,
                max_friction_score=tension_max_friction_score,
                max_lyapunov_proxy=tension_max_lyapunov_proxy,
                max_council_count=tension_max_council_count,
                max_llm_preflight_latency_ms=tension_max_llm_preflight_latency_ms,
                max_llm_selection_latency_ms=tension_max_llm_selection_latency_ms,
                max_llm_probe_latency_ms=tension_max_llm_probe_latency_ms,
                max_llm_timeout_count=tension_max_llm_timeout_count,
                max_consecutive_failure_count=tension_max_consecutive_failure_count,
                cooldown_cycles=tension_cooldown_cycles,
                selected_categories=batch.selected_categories,
            )
            tension_budget["llm_policy"] = dict(llm_policy)
            overall_ok = bool(autonomous_payload.get("overall_ok", True)) and bool(batch.ok)
            finished_at = _iso_now()
            duration_ms = int(round((time.perf_counter() - started_clock) * 1000))

            result = RegistryScheduleCycleResult(
                cycle=cycle_index,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                registry_batch=batch,
                autonomous_payload=autonomous_payload,
                tension_budget=tension_budget,
                overall_ok=overall_ok,
            )
            rows.append(result.to_dict())

            failed_urls = self._derive_failed_urls(autonomous_payload)
            absolute_cycle = int(batch.absolute_cycle)
            backoff_base = max(0, int(failure_backoff_cycles))
            for entry in batch.selected_entries:
                entry_id = str(entry.get("id") or "").strip()
                if not entry_id:
                    continue
                entry_state = state.entry_states.get(entry_id, RegistryEntryState())
                entry_state.last_selected_cycle = absolute_cycle
                entry_state.updated_at = finished_at
                entry_urls = [str(url).strip() for url in entry.get("urls", []) if str(url).strip()]
                failed = any(url in failed_urls for url in entry_urls)
                if failed:
                    entry_state.consecutive_failures += 1
                    entry_state.last_outcome = "failed"
                    if backoff_base > 0:
                        category = str(entry.get("category") or "").strip().lower()
                        category_multiplier = max(
                            1,
                            int(normalized_category_backoff_multipliers.get(category, 1)),
                        )
                        entry_state.backoff_until_cycle = absolute_cycle + (
                            backoff_base
                            * category_multiplier
                            * max(1, int(entry_state.consecutive_failures))
                        )
                else:
                    entry_state.consecutive_failures = 0
                    entry_state.backoff_until_cycle = 0
                    entry_state.last_outcome = "ok"
                state.entry_states[entry_id] = entry_state

            observed_categories = sorted(
                {
                    str(category).strip().lower()
                    for category in batch.selected_categories
                    if str(category).strip()
                }
            )
            for category in observed_categories:
                category_state = state.category_states.get(category, RegistryCategoryState())
                observation = (
                    tension_budget.get("observation", {})
                    if isinstance(tension_budget.get("observation"), dict)
                    else {}
                )
                try:
                    observed_cycles = max(0, int(observation.get("observed_cycles", 0) or 0))
                except (TypeError, ValueError):
                    observed_cycles = 0
                if observed_cycles > 0:
                    category_state.last_max_friction_score = self._coerce_float(
                        observation.get("max_friction_score")
                    )
                    category_state.last_max_lyapunov_proxy = self._coerce_float(
                        observation.get("max_lyapunov_proxy")
                    )
                    try:
                        category_state.last_council_count = int(
                            observation.get("council_count", 0) or 0
                        )
                    except (TypeError, ValueError):
                        category_state.last_council_count = 0
                    category_state.last_llm_preflight_latency_ms = (
                        int(observation["max_llm_preflight_latency_ms"])
                        if isinstance(observation.get("max_llm_preflight_latency_ms"), int)
                        else None
                    )
                    category_state.last_llm_selection_latency_ms = (
                        int(observation["max_llm_selection_latency_ms"])
                        if isinstance(observation.get("max_llm_selection_latency_ms"), int)
                        else None
                    )
                    category_state.last_llm_probe_latency_ms = (
                        int(observation["max_llm_probe_latency_ms"])
                        if isinstance(observation.get("max_llm_probe_latency_ms"), int)
                        else None
                    )
                    try:
                        category_state.last_llm_preflight_timeout_count = int(
                            observation.get("llm_preflight_timeout_count", 0) or 0
                        )
                    except (TypeError, ValueError):
                        category_state.last_llm_preflight_timeout_count = 0
                category_state.updated_at = finished_at
                if bool(tension_budget.get("governance_breached", False)):
                    category_state.tension_cooldown_until_cycle = (
                        absolute_cycle + max(0, int(tension_cooldown_cycles))
                        if max(0, int(tension_cooldown_cycles)) > 0
                        else 0
                    )
                    category_state.last_budget_status = "breached"
                    category_state.last_breach_reasons = [
                        str(item).strip()
                        for item in tension_budget.get("governance_breach_reasons", [])
                        if str(item).strip()
                    ]
                else:
                    category_state.tension_cooldown_until_cycle = 0
                    category_state.last_budget_status = (
                        "ok" if bool(tension_budget.get("enabled", False)) else "disabled"
                    )
                    category_state.last_breach_reasons = []
                state.category_states[category] = category_state

            if bool(tension_budget.get("llm_breached", False)):
                state.llm_backoff.backoff_until_cycle = (
                    absolute_cycle + max(0, int(tension_cooldown_cycles))
                    if max(0, int(tension_cooldown_cycles)) > 0
                    else 0
                )
                state.llm_backoff.last_status = "breached"
                state.llm_backoff.last_mode = str(
                    tension_budget.get("llm_backoff_mode") or "llm_budget"
                )
                state.llm_backoff.last_breach_reasons = [
                    str(item).strip()
                    for item in tension_budget.get("llm_breach_reasons", [])
                    if str(item).strip()
                ]
                state.llm_backoff.updated_at = finished_at
            elif not llm_backoff_active:
                state.llm_backoff.backoff_until_cycle = 0
                state.llm_backoff.last_status = (
                    "ok" if bool(tension_budget.get("enabled", False)) else "disabled"
                )
                state.llm_backoff.last_mode = "none"
                state.llm_backoff.last_breach_reasons = []
                state.llm_backoff.updated_at = finished_at

            if batch.category_cursor_after is not None:
                state.category_cursor = int(batch.category_cursor_after)
            for category, next_cursor in batch.category_entry_cursor_updates.items():
                state.category_entry_cursors[str(category).strip().lower()] = max(
                    0, int(next_cursor)
                )
            state.cursor = int(
                batch.cursor_after if batch.selected_entry_ids else batch.cursor_before
            )
            state.cycles_run += 1
            state.updated_at = finished_at
            state.last_entry_ids = list(batch.selected_entry_ids)
            self._write_state(state)

            if cycle_index < int(max_cycles):
                self._sleep(self.interval_seconds)

        payload = {
            "generated_at": _iso_now(),
            "overall_ok": all(bool(item.get("overall_ok", True)) for item in rows),
            "config": config,
            "results": rows,
            "state": state.to_dict(),
        }
        _write_json(self.snapshot_path, payload)
        _append_jsonl(self.history_path, rows)
        if (
            self.journal_path is not None
            and self.wakeup_path is not None
            and self.dashboard_out_dir is not None
        ):
            dashboard_payload = build_dashboard(
                journal_path=self.journal_path,
                wakeup_path=self.wakeup_path,
                schedule_history_path=self.history_path,
                schedule_state_path=self.state_path,
            )
            _write_json(self.dashboard_out_dir / JSON_FILENAME, dashboard_payload)
            _write_text(self.dashboard_out_dir / HTML_FILENAME, render_html(dashboard_payload))
        return payload


def build_autonomous_registry_schedule(
    *,
    db_path: Optional[Path] = None,
    crystal_path: Optional[Path] = None,
    journal_path: Path = Path("memory/self_journal.jsonl"),
    history_path: Path = Path("memory/autonomous/dream_wakeup_history.jsonl"),
    snapshot_path: Path = Path("docs/status/dream_wakeup_snapshot_latest.json"),
    dashboard_out_dir: Path = Path("docs/status"),
    registry_path: Path = Path("spec/external_source_registry.yaml"),
    schedule_state_path: Path = Path("memory/autonomous/registry_schedule_state.json"),
    schedule_snapshot_path: Path = Path("docs/status/autonomous_registry_schedule_latest.json"),
    schedule_history_path: Path = Path("memory/autonomous/registry_schedule_history.jsonl"),
    interval_seconds: float = 10800.0,
    sleep_func: SleepFunc = time.sleep,
) -> AutonomousRegistrySchedule:
    runner = build_autonomous_cycle_runner(
        db_path=db_path,
        crystal_path=crystal_path,
        journal_path=journal_path,
        history_path=history_path,
        snapshot_path=snapshot_path,
        dashboard_out_dir=dashboard_out_dir,
        interval_seconds=0.0,
    )
    return AutonomousRegistrySchedule(
        runner=runner,
        registry_path=registry_path,
        state_path=schedule_state_path,
        snapshot_path=schedule_snapshot_path,
        history_path=schedule_history_path,
        journal_path=journal_path,
        wakeup_path=history_path,
        dashboard_out_dir=dashboard_out_dir,
        interval_seconds=interval_seconds,
        sleep_func=sleep_func,
    )


__all__ = [
    "AutonomousRegistrySchedule",
    "RegistryCategoryState",
    "RegistryEntryState",
    "RegistryScheduleBatch",
    "RegistryScheduleCycleResult",
    "RegistryScheduleState",
    "build_autonomous_registry_schedule",
]
