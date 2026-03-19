from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Optional, Sequence

from tonesoul.memory.subjectivity_handoff import build_handoff_surface

JSON_FILENAME = "dream_observability_latest.json"
HTML_FILENAME = "dream_observability_latest.html"

_JOURNAL_FRICTION_SPECS = (
    {
        "path": ("tension_before", "signals", "cognitive_friction"),
        "timestamp_path": ("tension_before", "timestamp"),
        "phase": "before",
        "label": "cognitive_friction",
    },
    {
        "path": ("tension_after", "signals", "cognitive_friction"),
        "timestamp_path": ("tension_after", "timestamp"),
        "phase": "after",
        "label": "cognitive_friction",
    },
    {
        "path": ("dispatch_trace", "pre_gate_governance_friction"),
        "timestamp_path": ("timestamp",),
        "phase": "dispatch",
        "label": "pre_gate_governance_friction",
    },
    {
        "path": ("context", "dispatch_trace", "pre_gate_governance_friction"),
        "timestamp_path": ("timestamp",),
        "phase": "context_dispatch",
        "label": "pre_gate_governance_friction",
    },
    {
        "path": ("dispatch_trace", "governance_observability", "friction_score"),
        "timestamp_path": ("timestamp",),
        "phase": "dispatch",
        "label": "friction_score",
    },
    {
        "path": ("context", "dispatch_trace", "governance_observability", "friction_score"),
        "timestamp_path": ("timestamp",),
        "phase": "context_dispatch",
        "label": "friction_score",
    },
)

_JOURNAL_LYAPUNOV_SPECS = (
    {
        "path": ("tension_before", "prediction", "lyapunov_exponent"),
        "timestamp_path": ("tension_before", "timestamp"),
        "phase": "before",
        "label": "lyapunov_exponent",
    },
    {
        "path": ("tension_after", "prediction", "lyapunov_exponent"),
        "timestamp_path": ("tension_after", "timestamp"),
        "phase": "after",
        "label": "lyapunov_exponent",
    },
    {
        "path": ("dispatch_trace", "governance_observability", "lyapunov_exponent"),
        "timestamp_path": ("timestamp",),
        "phase": "dispatch",
        "label": "lyapunov_exponent",
    },
    {
        "path": ("context", "dispatch_trace", "governance_observability", "lyapunov_exponent"),
        "timestamp_path": ("timestamp",),
        "phase": "context_dispatch",
        "label": "lyapunov_exponent",
    },
    {
        "path": ("dispatch_trace", "governance_observability", "lyapunov_proxy"),
        "timestamp_path": ("timestamp",),
        "phase": "dispatch",
        "label": "lyapunov_proxy",
    },
    {
        "path": ("context", "dispatch_trace", "governance_observability", "lyapunov_proxy"),
        "timestamp_path": ("timestamp",),
        "phase": "context_dispatch",
        "label": "lyapunov_proxy",
    },
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: object) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _round_or_none(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def _compact_timestamp(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return "n/a"
    if "T" in text:
        date_part, time_part = text.split("T", 1)
        return f"{date_part} {time_part[:8]}"
    return text[:19]


def _path_get(payload: object, path: Sequence[str]) -> object:
    current = payload
    for segment in path:
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    if not path.exists() or not path.is_file():
        return [], 0

    rows: list[dict[str, Any]] = []
    invalid_count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_count += 1
                continue
            if isinstance(payload, dict):
                rows.append(payload)
            else:
                invalid_count += 1
    return rows, invalid_count


def _entry_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload")
    return payload if isinstance(payload, dict) else row


def _append_point(
    points: list[dict[str, Any]],
    seen: set[tuple[object, ...]],
    *,
    timestamp: object,
    value: object,
    source: str,
    phase: str,
    label: str,
) -> None:
    numeric = _to_float(value)
    if numeric is None:
        return
    text_timestamp = str(timestamp or "").strip() or "n/a"
    key = (text_timestamp, source, phase, label, round(numeric, 6))
    if key in seen:
        return
    seen.add(key)
    points.append(
        {
            "timestamp": text_timestamp,
            "value": round(numeric, 4),
            "source": source,
            "phase": phase,
            "label": label,
        }
    )


def _extract_journal_points(rows: Sequence[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    friction_points: list[dict[str, Any]] = []
    lyapunov_points: list[dict[str, Any]] = []
    seen_friction: set[tuple[object, ...]] = set()
    seen_lyapunov: set[tuple[object, ...]] = set()

    for row in rows:
        entry = _entry_payload(row)
        entry_timestamp = (
            str(entry.get("timestamp") or "").strip()
            or str(row.get("timestamp") or "").strip()
            or "n/a"
        )

        for spec in _JOURNAL_FRICTION_SPECS:
            timestamp = _path_get(entry, spec["timestamp_path"]) or entry_timestamp
            value = _path_get(entry, spec["path"])
            _append_point(
                friction_points,
                seen_friction,
                timestamp=timestamp,
                value=value,
                source="journal",
                phase=str(spec["phase"]),
                label=str(spec["label"]),
            )

        for spec in _JOURNAL_LYAPUNOV_SPECS:
            timestamp = _path_get(entry, spec["timestamp_path"]) or entry_timestamp
            value = _path_get(entry, spec["path"])
            _append_point(
                lyapunov_points,
                seen_lyapunov,
                timestamp=timestamp,
                value=value,
                source="journal",
                phase=str(spec["phase"]),
                label=str(spec["label"]),
            )

    return {
        "journal_friction": friction_points,
        "journal_lyapunov": lyapunov_points,
    }


def _load_result_rows(path: Path, *, label: str) -> tuple[list[dict[str, Any]], int, list[str]]:
    if not path.exists() or not path.is_file():
        return [], 0, []

    warnings: list[str] = []
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        rows, invalid_count = _read_jsonl(path)
        return rows, invalid_count, warnings

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], 1, [f"{label} is not valid JSON: {path.as_posix()}"]

    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            rows = [item for item in results if isinstance(item, dict)]
            invalid_count = len(results) - len(rows)
            return rows, invalid_count, warnings
        warnings.append(f"{label} snapshot missing 'results' list: {path.as_posix()}")
        return [], 1, warnings

    if isinstance(payload, list):
        rows = [item for item in payload if isinstance(item, dict)]
        invalid_count = len(payload) - len(rows)
        return rows, invalid_count, warnings

    return [], 1, [f"{label} has unsupported JSON shape: {path.as_posix()}"]


def _load_wakeup_rows(path: Path) -> tuple[list[dict[str, Any]], int, list[str]]:
    return _load_result_rows(path, label="wakeup history")


def _load_schedule_rows(path: Path) -> tuple[list[dict[str, Any]], int, list[str]]:
    return _load_result_rows(path, label="schedule history")


def _load_schedule_state(path: Path) -> tuple[dict[str, Any], int, list[str]]:
    if not path.exists() or not path.is_file():
        return {}, 0, []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, 1, [f"schedule state is not valid JSON: {path.as_posix()}"]
    if not isinstance(payload, dict):
        return {}, 1, [f"schedule state has unsupported JSON shape: {path.as_posix()}"]
    return payload, 0, []


def _extract_wakeup_points(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    avg_friction_points: list[dict[str, Any]] = []
    max_friction_points: list[dict[str, Any]] = []
    max_lyapunov_points: list[dict[str, Any]] = []
    collision_success_rate_points: list[dict[str, Any]] = []
    consecutive_failure_points: list[dict[str, Any]] = []
    session_resumed_points: list[dict[str, Any]] = []
    council_count_points: list[dict[str, Any]] = []
    frozen_count_points: list[dict[str, Any]] = []
    write_gateway_written_points: list[dict[str, Any]] = []
    write_gateway_skipped_points: list[dict[str, Any]] = []
    write_gateway_rejected_points: list[dict[str, Any]] = []
    llm_call_count_points: list[dict[str, Any]] = []
    llm_prompt_tokens_points: list[dict[str, Any]] = []
    llm_completion_tokens_points: list[dict[str, Any]] = []
    llm_total_tokens_points: list[dict[str, Any]] = []
    llm_preflight_latency_points: list[dict[str, Any]] = []
    llm_selection_latency_points: list[dict[str, Any]] = []
    llm_probe_latency_points: list[dict[str, Any]] = []
    llm_preflight_timeout_points: list[dict[str, Any]] = []
    scribe_triggered_points: list[dict[str, Any]] = []
    recent_cycles: list[dict[str, Any]] = []
    session_ids: set[str] = set()
    resumed_cycle_count = 0
    latest_session_id: str | None = None
    latest_resume_state_path: str | None = None
    latest_heartbeat_window_cycle: int | None = None
    latest_consecutive_failure_count = 0
    latest_scribe_status: str | None = None
    latest_scribe_generation_mode: str | None = None
    latest_scribe_state_document_posture: str | None = None
    latest_scribe_anchor_status_line: str | None = None
    latest_scribe_problem_route_status_line: str | None = None
    latest_scribe_problem_route_secondary_labels: str | None = None
    latest_scribe_available_source: str | None = None
    latest_scribe_skip_reason: str | None = None

    for row in rows:
        summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
        timestamp = (
            str(row.get("finished_at") or "").strip()
            or str(row.get("started_at") or "").strip()
            or str(row.get("generated_at") or "").strip()
            or "n/a"
        )
        cycle = row.get("cycle")
        status = str(row.get("status") or "").strip() or "unknown"
        session_id = str(summary.get("session_id") or "").strip() or None
        session_resumed = bool(summary.get("session_resumed", False))
        heartbeat_window_cycle = _to_int(summary.get("heartbeat_window_cycle"))
        consecutive_failure_count = max(0, int(summary.get("consecutive_failure_count", 0) or 0))
        resume_state_path = str(summary.get("resume_state_path") or "").strip() or None
        if session_id:
            session_ids.add(session_id)
            latest_session_id = session_id
        if session_resumed:
            resumed_cycle_count += 1
        if heartbeat_window_cycle is not None:
            latest_heartbeat_window_cycle = heartbeat_window_cycle
        if resume_state_path:
            latest_resume_state_path = resume_state_path
        latest_consecutive_failure_count = consecutive_failure_count
        has_scribe_signal = any(
            key in summary
            for key in (
                "scribe_evaluated",
                "scribe_triggered",
                "scribe_status",
                "scribe_generation_mode",
                "scribe_state_document_posture",
                "scribe_anchor_status_line",
                "scribe_problem_route_status_line",
                "scribe_problem_route_secondary_labels",
                "scribe_latest_available_source",
                "scribe_skip_reason",
            )
        )
        scribe_evaluated = bool(summary.get("scribe_evaluated", False))
        scribe_triggered = bool(summary.get("scribe_triggered", False))
        scribe_status = str(summary.get("scribe_status") or "").strip() or None
        scribe_generation_mode = str(summary.get("scribe_generation_mode") or "").strip() or None
        scribe_state_document_posture = (
            str(summary.get("scribe_state_document_posture") or "").strip() or None
        )
        scribe_anchor_status_line = (
            str(summary.get("scribe_anchor_status_line") or "").strip() or None
        )
        scribe_problem_route_status_line = (
            str(summary.get("scribe_problem_route_status_line") or "").strip() or None
        )
        scribe_problem_route_secondary_labels = (
            str(summary.get("scribe_problem_route_secondary_labels") or "").strip() or None
        )
        scribe_latest_available_source = (
            str(summary.get("scribe_latest_available_source") or "").strip() or None
        )
        scribe_skip_reason = str(summary.get("scribe_skip_reason") or "").strip() or None
        if has_scribe_signal:
            latest_scribe_status = scribe_status
            latest_scribe_generation_mode = scribe_generation_mode
            latest_scribe_state_document_posture = scribe_state_document_posture
            latest_scribe_anchor_status_line = scribe_anchor_status_line
            latest_scribe_problem_route_status_line = scribe_problem_route_status_line
            latest_scribe_problem_route_secondary_labels = scribe_problem_route_secondary_labels
            latest_scribe_available_source = scribe_latest_available_source
            latest_scribe_skip_reason = scribe_skip_reason

        _append_point(
            avg_friction_points,
            set(),
            timestamp=timestamp,
            value=summary.get("avg_friction_score"),
            source="wakeup",
            phase="cycle",
            label="avg_friction_score",
        )
        _append_point(
            max_friction_points,
            set(),
            timestamp=timestamp,
            value=summary.get("max_friction_score"),
            source="wakeup",
            phase="cycle",
            label="max_friction_score",
        )
        _append_point(
            max_lyapunov_points,
            set(),
            timestamp=timestamp,
            value=summary.get("max_lyapunov_proxy"),
            source="wakeup",
            phase="cycle",
            label="max_lyapunov_proxy",
        )
        _append_point(
            collision_success_rate_points,
            set(),
            timestamp=timestamp,
            value=summary.get("collision_success_rate"),
            source="wakeup",
            phase="cycle",
            label="collision_success_rate",
        )
        _append_point(
            consecutive_failure_points,
            set(),
            timestamp=timestamp,
            value=consecutive_failure_count,
            source="wakeup",
            phase="runtime",
            label="consecutive_failure_count",
        )
        _append_point(
            session_resumed_points,
            set(),
            timestamp=timestamp,
            value=1 if session_resumed else 0,
            source="wakeup",
            phase="runtime",
            label="session_resumed",
        )
        _append_point(
            council_count_points,
            set(),
            timestamp=timestamp,
            value=summary.get("council_count"),
            source="wakeup",
            phase="cycle",
            label="council_count",
        )
        _append_point(
            frozen_count_points,
            set(),
            timestamp=timestamp,
            value=summary.get("frozen_count"),
            source="wakeup",
            phase="cycle",
            label="frozen_count",
        )
        _append_point(
            write_gateway_written_points,
            set(),
            timestamp=timestamp,
            value=summary.get("write_gateway_written"),
            source="wakeup",
            phase="cycle",
            label="write_gateway_written",
        )
        _append_point(
            write_gateway_skipped_points,
            set(),
            timestamp=timestamp,
            value=summary.get("write_gateway_skipped"),
            source="wakeup",
            phase="cycle",
            label="write_gateway_skipped",
        )
        _append_point(
            write_gateway_rejected_points,
            set(),
            timestamp=timestamp,
            value=summary.get("write_gateway_rejected"),
            source="wakeup",
            phase="cycle",
            label="write_gateway_rejected",
        )
        _append_point(
            llm_call_count_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_call_count"),
            source="wakeup",
            phase="cycle",
            label="llm_call_count",
        )
        _append_point(
            llm_prompt_tokens_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_prompt_tokens_total"),
            source="wakeup",
            phase="cycle",
            label="llm_prompt_tokens_total",
        )
        _append_point(
            llm_completion_tokens_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_completion_tokens_total"),
            source="wakeup",
            phase="cycle",
            label="llm_completion_tokens_total",
        )
        _append_point(
            llm_total_tokens_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_total_tokens"),
            source="wakeup",
            phase="cycle",
            label="llm_total_tokens",
        )
        _append_point(
            llm_preflight_latency_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_preflight_latency_ms"),
            source="wakeup",
            phase="cycle",
            label="llm_preflight_latency_ms",
        )
        _append_point(
            llm_selection_latency_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_preflight_selection_latency_ms"),
            source="wakeup",
            phase="cycle",
            label="llm_preflight_selection_latency_ms",
        )
        _append_point(
            llm_probe_latency_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_preflight_probe_latency_ms"),
            source="wakeup",
            phase="cycle",
            label="llm_preflight_probe_latency_ms",
        )
        _append_point(
            llm_preflight_timeout_points,
            set(),
            timestamp=timestamp,
            value=summary.get("llm_preflight_timeout_count"),
            source="wakeup",
            phase="cycle",
            label="llm_preflight_timeout_count",
        )
        if has_scribe_signal:
            _append_point(
                scribe_triggered_points,
                set(),
                timestamp=timestamp,
                value=1 if scribe_triggered else 0,
                source="wakeup",
                phase="scribe",
                label="scribe_triggered",
            )

        recent_cycles.append(
            {
                "cycle": int(cycle) if isinstance(cycle, int) else cycle,
                "status": status,
                "timestamp": timestamp,
                "session_id": session_id,
                "session_resumed": session_resumed,
                "heartbeat_window_cycle": heartbeat_window_cycle,
                "consecutive_failure_count": consecutive_failure_count,
                "resume_state_path": resume_state_path,
                "avg_friction_score": _round_or_none(_to_float(summary.get("avg_friction_score"))),
                "max_friction_score": _round_or_none(_to_float(summary.get("max_friction_score"))),
                "max_lyapunov_proxy": _round_or_none(_to_float(summary.get("max_lyapunov_proxy"))),
                "collision_success_rate": _round_or_none(
                    _to_float(summary.get("collision_success_rate"))
                ),
                "council_count": int(summary.get("council_count", 0) or 0),
                "frozen_count": int(summary.get("frozen_count", 0) or 0),
                "write_gateway_written": int(summary.get("write_gateway_written", 0) or 0),
                "write_gateway_skipped": int(summary.get("write_gateway_skipped", 0) or 0),
                "write_gateway_rejected": int(summary.get("write_gateway_rejected", 0) or 0),
                "llm_call_count": int(summary.get("llm_call_count", 0) or 0),
                "llm_prompt_tokens_total": int(summary.get("llm_prompt_tokens_total", 0) or 0),
                "llm_completion_tokens_total": int(
                    summary.get("llm_completion_tokens_total", 0) or 0
                ),
                "llm_total_tokens": int(summary.get("llm_total_tokens", 0) or 0),
                "llm_backends": list(summary.get("llm_backends") or []),
                "llm_models": list(summary.get("llm_models") or []),
                "llm_preflight_latency_ms": (
                    None
                    if summary.get("llm_preflight_latency_ms") in (None, "")
                    else int(summary.get("llm_preflight_latency_ms", 0) or 0)
                ),
                "llm_preflight_selection_latency_ms": (
                    None
                    if summary.get("llm_preflight_selection_latency_ms") in (None, "")
                    else int(summary.get("llm_preflight_selection_latency_ms", 0) or 0)
                ),
                "llm_preflight_probe_latency_ms": (
                    None
                    if summary.get("llm_preflight_probe_latency_ms") in (None, "")
                    else int(summary.get("llm_preflight_probe_latency_ms", 0) or 0)
                ),
                "llm_preflight_timeout_count": int(
                    summary.get("llm_preflight_timeout_count", 0) or 0
                ),
                "llm_preflight_reason": (
                    str(summary.get("llm_preflight_reason") or "").strip() or None
                ),
                "consolidation_ran": bool(summary.get("consolidation_ran", False)),
                "consolidation_promoted_count": int(
                    summary.get("consolidation_promoted_count", 0) or 0
                ),
                "scribe_evaluated": scribe_evaluated,
                "scribe_triggered": scribe_triggered,
                "scribe_status": scribe_status,
                "scribe_generation_mode": scribe_generation_mode,
                "scribe_state_document_posture": scribe_state_document_posture,
                "scribe_anchor_status_line": scribe_anchor_status_line,
                "scribe_problem_route_status_line": scribe_problem_route_status_line,
                "scribe_problem_route_secondary_labels": scribe_problem_route_secondary_labels,
                "scribe_latest_available_source": scribe_latest_available_source,
                "scribe_skip_reason": scribe_skip_reason,
                "failure_pause_seconds": _to_int(summary.get("failure_pause_seconds")) or 0,
                "circuit_breaker_paused": bool(summary.get("circuit_breaker_paused", False)),
            }
        )

    return {
        "wakeup_avg_friction": avg_friction_points,
        "wakeup_max_friction": max_friction_points,
        "wakeup_max_lyapunov": max_lyapunov_points,
        "wakeup_collision_success_rate": collision_success_rate_points,
        "wakeup_consecutive_failures": consecutive_failure_points,
        "wakeup_session_resumed": session_resumed_points,
        "wakeup_council_count": council_count_points,
        "wakeup_frozen_count": frozen_count_points,
        "wakeup_write_gateway_written": write_gateway_written_points,
        "wakeup_write_gateway_skipped": write_gateway_skipped_points,
        "wakeup_write_gateway_rejected": write_gateway_rejected_points,
        "wakeup_llm_call_count": llm_call_count_points,
        "wakeup_llm_prompt_tokens": llm_prompt_tokens_points,
        "wakeup_llm_completion_tokens": llm_completion_tokens_points,
        "wakeup_llm_total_tokens": llm_total_tokens_points,
        "wakeup_llm_preflight_latency": llm_preflight_latency_points,
        "wakeup_llm_selection_latency": llm_selection_latency_points,
        "wakeup_llm_probe_latency": llm_probe_latency_points,
        "wakeup_llm_preflight_timeout_count": llm_preflight_timeout_points,
        "wakeup_scribe_triggered": scribe_triggered_points,
        "wakeup_runtime_state": {
            "session_count": len(session_ids),
            "latest_session_id": latest_session_id,
            "resumed_cycle_count": resumed_cycle_count,
            "latest_resume_state_path": latest_resume_state_path,
            "latest_heartbeat_window_cycle": latest_heartbeat_window_cycle,
            "latest_consecutive_failure_count": latest_consecutive_failure_count,
        },
        "wakeup_scribe_state": {
            "latest_status": latest_scribe_status,
            "latest_generation_mode": latest_scribe_generation_mode,
            "latest_state_document_posture": latest_scribe_state_document_posture,
            "latest_anchor_status_line": latest_scribe_anchor_status_line,
            "latest_problem_route_status_line": latest_scribe_problem_route_status_line,
            "latest_problem_route_secondary_labels": latest_scribe_problem_route_secondary_labels,
            "latest_available_source": latest_scribe_available_source,
            "latest_skip_reason": latest_scribe_skip_reason,
        },
        "recent_wakeup_cycles": recent_cycles[-8:],
    }


def _extract_schedule_points(
    rows: Sequence[dict[str, Any]], state_payload: dict[str, Any]
) -> dict[str, Any]:
    governance_cooldown_applied_points: list[dict[str, Any]] = []
    governance_cooldown_deferred_points: list[dict[str, Any]] = []
    llm_backoff_requested_points: list[dict[str, Any]] = []
    llm_backoff_active_points: list[dict[str, Any]] = []
    wakeup_session_resumed_points: list[dict[str, Any]] = []
    wakeup_consecutive_failures_points: list[dict[str, Any]] = []
    recent_cycles: list[dict[str, Any]] = []
    wakeup_session_ids: set[str] = set()
    wakeup_resumed_cycle_count = 0
    latest_wakeup_session_id: str | None = None
    latest_wakeup_state_path: str | None = None
    latest_wakeup_consecutive_failures = 0

    for row in rows:
        registry_batch = (
            row.get("registry_batch") if isinstance(row.get("registry_batch"), dict) else {}
        )
        tension_budget = (
            row.get("tension_budget") if isinstance(row.get("tension_budget"), dict) else {}
        )
        autonomous_payload = (
            row.get("autonomous_payload") if isinstance(row.get("autonomous_payload"), dict) else {}
        )
        llm_policy = (
            autonomous_payload.get("llm_policy")
            if isinstance(autonomous_payload.get("llm_policy"), dict)
            else {}
        )
        runtime_state = (
            autonomous_payload.get("runtime_state")
            if isinstance(autonomous_payload.get("runtime_state"), dict)
            else {}
        )
        timestamp = (
            str(row.get("finished_at") or "").strip()
            or str(row.get("started_at") or "").strip()
            or str(row.get("generated_at") or "").strip()
            or "n/a"
        )
        cycle = _to_int(row.get("cycle"))
        cooled_categories = [
            str(item).strip().lower()
            for item in (tension_budget.get("cooled_categories") or [])
            if str(item).strip()
        ]
        deferred_category_count = _to_int(registry_batch.get("deferred_category_count"))
        if deferred_category_count is None:
            deferred_categories = registry_batch.get("deferred_categories") or []
            deferred_category_count = (
                len(deferred_categories) if isinstance(deferred_categories, list) else 0
            )
        llm_backoff_requested = bool(tension_budget.get("llm_backoff_requested", False))
        llm_backoff_active = bool(llm_policy.get("active", False))
        llm_backoff_reason_count = _to_int(llm_policy.get("reason_count"))
        if llm_backoff_reason_count is None:
            reasons = llm_policy.get("breach_reasons") or []
            llm_backoff_reason_count = len(reasons) if isinstance(reasons, list) else 0
        wakeup_session_id = str(runtime_state.get("session_id") or "").strip() or None
        wakeup_session_resumed = bool(runtime_state.get("resumed", False))
        wakeup_consecutive_failures = max(0, int(runtime_state.get("consecutive_failures", 0) or 0))
        wakeup_next_cycle = _to_int(runtime_state.get("next_cycle"))
        wakeup_state_path = str(runtime_state.get("state_path") or "").strip() or None
        if wakeup_session_id:
            wakeup_session_ids.add(wakeup_session_id)
            latest_wakeup_session_id = wakeup_session_id
        if wakeup_session_resumed:
            wakeup_resumed_cycle_count += 1
        if wakeup_state_path:
            latest_wakeup_state_path = wakeup_state_path
        latest_wakeup_consecutive_failures = wakeup_consecutive_failures

        _append_point(
            governance_cooldown_applied_points,
            set(),
            timestamp=timestamp,
            value=len(cooled_categories),
            source="schedule",
            phase="cycle",
            label="governance_cooldown_applied",
        )
        _append_point(
            governance_cooldown_deferred_points,
            set(),
            timestamp=timestamp,
            value=deferred_category_count,
            source="schedule",
            phase="cycle",
            label="governance_cooldown_deferred",
        )
        _append_point(
            llm_backoff_requested_points,
            set(),
            timestamp=timestamp,
            value=1 if llm_backoff_requested else 0,
            source="schedule",
            phase="cycle",
            label="llm_backoff_requested",
        )
        _append_point(
            llm_backoff_active_points,
            set(),
            timestamp=timestamp,
            value=1 if llm_backoff_active else 0,
            source="schedule",
            phase="cycle",
            label="llm_backoff_active",
        )
        _append_point(
            wakeup_session_resumed_points,
            set(),
            timestamp=timestamp,
            value=1 if wakeup_session_resumed else 0,
            source="schedule",
            phase="runtime",
            label="wakeup_session_resumed",
        )
        _append_point(
            wakeup_consecutive_failures_points,
            set(),
            timestamp=timestamp,
            value=wakeup_consecutive_failures,
            source="schedule",
            phase="runtime",
            label="wakeup_consecutive_failures",
        )

        recent_cycles.append(
            {
                "cycle": cycle if cycle is not None else row.get("cycle"),
                "timestamp": timestamp,
                "selected_categories": [
                    str(item).strip().lower()
                    for item in (registry_batch.get("selected_categories") or [])
                    if str(item).strip()
                ],
                "cooled_categories": cooled_categories,
                "deferred_category_count": int(deferred_category_count or 0),
                "llm_backoff_requested": llm_backoff_requested,
                "llm_backoff_active": llm_backoff_active,
                "llm_backoff_mode": str(llm_policy.get("mode") or "none"),
                "llm_backoff_action": str(llm_policy.get("action") or "normal"),
                "llm_backoff_reason_count": int(llm_backoff_reason_count or 0),
                "wakeup_session_id": wakeup_session_id,
                "wakeup_session_resumed": wakeup_session_resumed,
                "wakeup_consecutive_failures": wakeup_consecutive_failures,
                "wakeup_next_cycle": wakeup_next_cycle,
                "wakeup_state_path": wakeup_state_path,
                "governance_breach_reasons": [
                    str(item).strip()
                    for item in (tension_budget.get("governance_breach_reasons") or [])
                    if str(item).strip()
                ],
                "llm_breach_reasons": [
                    str(item).strip()
                    for item in (tension_budget.get("llm_breach_reasons") or [])
                    if str(item).strip()
                ],
            }
        )

    cycles_run = max(0, _to_int(state_payload.get("cycles_run")) or 0)
    category_states = (
        state_payload.get("category_states")
        if isinstance(state_payload.get("category_states"), dict)
        else {}
    )
    active_governance_categories = sorted(
        str(category).strip().lower()
        for category, raw_state in category_states.items()
        if isinstance(raw_state, dict)
        and max(0, _to_int(raw_state.get("tension_cooldown_until_cycle")) or 0) > cycles_run
    )
    llm_backoff_state = (
        state_payload.get("llm_backoff")
        if isinstance(state_payload.get("llm_backoff"), dict)
        else {}
    )
    llm_backoff_until_cycle = max(0, _to_int(llm_backoff_state.get("backoff_until_cycle")) or 0)
    llm_backoff_reasons = [
        str(item).strip()
        for item in (llm_backoff_state.get("last_breach_reasons") or [])
        if str(item).strip()
    ]
    schedule_state = {
        "cycles_run": cycles_run,
        "updated_at": str(state_payload.get("updated_at") or "").strip() or None,
        "active_governance_cooldown_categories": active_governance_categories,
        "active_governance_cooldown_count": len(active_governance_categories),
        "llm_backoff_active": llm_backoff_until_cycle > cycles_run,
        "llm_backoff_until_cycle": llm_backoff_until_cycle,
        "llm_backoff_mode": str(llm_backoff_state.get("last_mode") or "none"),
        "llm_backoff_status": str(llm_backoff_state.get("last_status") or "unknown"),
        "llm_backoff_reason_count": len(llm_backoff_reasons),
        "llm_backoff_breach_reasons": llm_backoff_reasons,
    }

    return {
        "schedule_governance_cooldown_applied": governance_cooldown_applied_points,
        "schedule_governance_cooldown_deferred": governance_cooldown_deferred_points,
        "schedule_llm_backoff_requested": llm_backoff_requested_points,
        "schedule_llm_backoff_active": llm_backoff_active_points,
        "schedule_wakeup_session_resumed": wakeup_session_resumed_points,
        "schedule_wakeup_consecutive_failures": wakeup_consecutive_failures_points,
        "schedule_runtime_state": {
            "session_count": len(wakeup_session_ids),
            "latest_session_id": latest_wakeup_session_id,
            "resumed_cycle_count": wakeup_resumed_cycle_count,
            "latest_state_path": latest_wakeup_state_path,
            "latest_consecutive_failures": latest_wakeup_consecutive_failures,
        },
        "recent_schedule_cycles": recent_cycles[-8:],
        "schedule_state": schedule_state,
    }


def _truncate_points(points: Sequence[dict[str, Any]], max_points: int) -> list[dict[str, Any]]:
    limit = max(1, int(max_points))
    return list(points[-limit:])


def _metric_trend(points: Sequence[dict[str, Any]]) -> str:
    if len(points) < 2:
        return "insufficient"
    window = points[-3:] if len(points) >= 3 else points[-2:]
    delta = float(window[-1]["value"]) - float(window[0]["value"])
    max_abs = max(abs(float(point["value"])) for point in window)
    epsilon = max(0.03, max_abs * 0.08)
    if abs(delta) <= epsilon:
        return "stable"
    return "rising" if delta > 0 else "falling"


def _count_convergence_events(
    points: Sequence[dict[str, Any]],
    *,
    high_threshold: float,
    settle_threshold: float,
    min_drop: float,
) -> int:
    count = 0
    values = [float(point["value"]) for point in points]
    for index, value in enumerate(values[:-1]):
        if value < high_threshold:
            continue
        window = values[index + 1 : index + 4]
        if any(
            candidate <= settle_threshold or candidate <= (value - min_drop) for candidate in window
        ):
            count += 1
    return count


def _summarize_metric(
    points: Sequence[dict[str, Any]],
    *,
    high_threshold: Optional[float] = None,
    settle_threshold: Optional[float] = None,
    min_drop: float = 0.15,
) -> dict[str, Any]:
    if not points:
        return {
            "point_count": 0,
            "latest": None,
            "min": None,
            "max": None,
            "average": None,
            "trend": "empty",
            "convergence_events": 0,
        }

    values = [float(point["value"]) for point in points]
    summary = {
        "point_count": len(values),
        "latest": round(values[-1], 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "average": round(sum(values) / len(values), 4),
        "trend": _metric_trend(points),
        "convergence_events": 0,
    }
    if high_threshold is not None and settle_threshold is not None:
        summary["convergence_events"] = _count_convergence_events(
            points,
            high_threshold=high_threshold,
            settle_threshold=settle_threshold,
            min_drop=min_drop,
        )
    return summary


def _dashboard_status_surface(
    *,
    overall_ok: bool,
    summary: dict[str, Any],
    metrics: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    primary_status_line = (
        "dream_observability_ready | "
        f"wakeup_cycles={int(metrics.get('wakeup_cycle_count', 0) or 0)} "
        f"schedule_cycles={int(metrics.get('schedule_cycle_count', 0) or 0)} "
        f"warnings={int(summary.get('warning_count', 0) or 0)} "
        f"overall_ok={'yes' if overall_ok else 'no'}"
    )
    runtime_status_line = (
        "wakeup_scribe | "
        f"status={summary.get('wakeup_latest_scribe_status') or 'none'} "
        f"posture={summary.get('wakeup_latest_scribe_state_document_posture') or 'none'} "
        f"source={summary.get('wakeup_latest_scribe_available_source') or 'none'}"
    )
    anchor_status_line = str(summary.get("wakeup_latest_scribe_anchor_status_line") or "").strip()
    problem_route_status_line = str(
        summary.get("wakeup_latest_scribe_problem_route_status_line") or ""
    ).strip()
    problem_route_secondary_labels = str(
        summary.get("wakeup_latest_scribe_problem_route_secondary_labels") or ""
    ).strip()
    artifact_policy_status_line = (
        "dashboard_inputs | "
        f"wakeup={'yes' if str(inputs.get('wakeup_path') or '').strip() else 'no'} "
        f"schedule={'yes' if str(inputs.get('schedule_history_path') or '').strip() else 'no'} "
        f"invalid_json={int(summary.get('invalid_json_total', 0) or 0)}"
    )
    handoff_extra_fields: dict[str, Any] = {
        "anchor_status_line": anchor_status_line,
        "problem_route_status_line": problem_route_status_line,
        "latest_scribe_status": summary.get("wakeup_latest_scribe_status") or "",
        "latest_scribe_state_document_posture": (
            summary.get("wakeup_latest_scribe_state_document_posture") or ""
        ),
        "latest_scribe_available_source": summary.get("wakeup_latest_scribe_available_source")
        or "",
    }
    if problem_route_secondary_labels:
        handoff_extra_fields["problem_route_secondary_labels"] = problem_route_secondary_labels
    return {
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "anchor_status_line": anchor_status_line,
        "problem_route_status_line": problem_route_status_line,
        "problem_route_secondary_labels": problem_route_secondary_labels,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": build_handoff_surface(
            queue_shape="dream_observability_ready",
            requires_operator_action=not overall_ok,
            status_lines=[
                primary_status_line,
                runtime_status_line,
                problem_route_status_line,
                artifact_policy_status_line,
            ],
            extra_fields=handoff_extra_fields,
        ),
    }


def build_dashboard(
    *,
    journal_path: Path,
    wakeup_path: Path,
    schedule_history_path: Optional[Path] = None,
    schedule_state_path: Optional[Path] = None,
    max_points: int = 120,
) -> dict[str, Any]:
    warnings: list[str] = []
    max_points = max(10, int(max_points))

    if not journal_path.exists():
        warnings.append(f"journal path does not exist: {journal_path.as_posix()}")
    if not wakeup_path.exists():
        warnings.append(f"wakeup history path does not exist: {wakeup_path.as_posix()}")
    if schedule_history_path is not None and not schedule_history_path.exists():
        warnings.append(f"schedule history path does not exist: {schedule_history_path.as_posix()}")
    if schedule_state_path is not None and not schedule_state_path.exists():
        warnings.append(f"schedule state path does not exist: {schedule_state_path.as_posix()}")

    journal_rows, journal_invalid_json_line_count = _read_jsonl(journal_path)
    wakeup_rows, wakeup_invalid_json_line_count, wakeup_warnings = _load_wakeup_rows(wakeup_path)
    warnings.extend(wakeup_warnings)
    schedule_rows: list[dict[str, Any]] = []
    schedule_invalid_json_line_count = 0
    if schedule_history_path is not None:
        schedule_rows, schedule_invalid_json_line_count, schedule_warnings = _load_schedule_rows(
            schedule_history_path
        )
        warnings.extend(schedule_warnings)
    schedule_state_payload: dict[str, Any] = {}
    schedule_state_invalid_json_count = 0
    if schedule_state_path is not None:
        (
            schedule_state_payload,
            schedule_state_invalid_json_count,
            schedule_state_warnings,
        ) = _load_schedule_state(schedule_state_path)
        warnings.extend(schedule_state_warnings)

    journal_series = _extract_journal_points(journal_rows)
    wakeup_payload = _extract_wakeup_points(wakeup_rows)
    schedule_payload = _extract_schedule_points(schedule_rows, schedule_state_payload)

    series = {
        "journal_friction": _truncate_points(journal_series["journal_friction"], max_points),
        "journal_lyapunov": _truncate_points(journal_series["journal_lyapunov"], max_points),
        "wakeup_avg_friction": _truncate_points(wakeup_payload["wakeup_avg_friction"], max_points),
        "wakeup_max_friction": _truncate_points(wakeup_payload["wakeup_max_friction"], max_points),
        "wakeup_max_lyapunov": _truncate_points(wakeup_payload["wakeup_max_lyapunov"], max_points),
        "wakeup_collision_success_rate": _truncate_points(
            wakeup_payload["wakeup_collision_success_rate"], max_points
        ),
        "wakeup_consecutive_failures": _truncate_points(
            wakeup_payload["wakeup_consecutive_failures"], max_points
        ),
        "wakeup_session_resumed": _truncate_points(
            wakeup_payload["wakeup_session_resumed"], max_points
        ),
        "wakeup_council_count": _truncate_points(
            wakeup_payload["wakeup_council_count"], max_points
        ),
        "wakeup_frozen_count": _truncate_points(wakeup_payload["wakeup_frozen_count"], max_points),
        "wakeup_write_gateway_written": _truncate_points(
            wakeup_payload["wakeup_write_gateway_written"], max_points
        ),
        "wakeup_write_gateway_skipped": _truncate_points(
            wakeup_payload["wakeup_write_gateway_skipped"], max_points
        ),
        "wakeup_write_gateway_rejected": _truncate_points(
            wakeup_payload["wakeup_write_gateway_rejected"], max_points
        ),
        "wakeup_llm_call_count": _truncate_points(
            wakeup_payload["wakeup_llm_call_count"], max_points
        ),
        "wakeup_llm_prompt_tokens": _truncate_points(
            wakeup_payload["wakeup_llm_prompt_tokens"], max_points
        ),
        "wakeup_llm_completion_tokens": _truncate_points(
            wakeup_payload["wakeup_llm_completion_tokens"], max_points
        ),
        "wakeup_llm_total_tokens": _truncate_points(
            wakeup_payload["wakeup_llm_total_tokens"], max_points
        ),
        "wakeup_llm_preflight_latency": _truncate_points(
            wakeup_payload["wakeup_llm_preflight_latency"], max_points
        ),
        "wakeup_llm_selection_latency": _truncate_points(
            wakeup_payload["wakeup_llm_selection_latency"], max_points
        ),
        "wakeup_llm_probe_latency": _truncate_points(
            wakeup_payload["wakeup_llm_probe_latency"], max_points
        ),
        "wakeup_llm_preflight_timeout_count": _truncate_points(
            wakeup_payload["wakeup_llm_preflight_timeout_count"], max_points
        ),
        "wakeup_scribe_triggered": _truncate_points(
            wakeup_payload["wakeup_scribe_triggered"], max_points
        ),
        "schedule_governance_cooldown_applied": _truncate_points(
            schedule_payload["schedule_governance_cooldown_applied"], max_points
        ),
        "schedule_governance_cooldown_deferred": _truncate_points(
            schedule_payload["schedule_governance_cooldown_deferred"], max_points
        ),
        "schedule_llm_backoff_requested": _truncate_points(
            schedule_payload["schedule_llm_backoff_requested"], max_points
        ),
        "schedule_llm_backoff_active": _truncate_points(
            schedule_payload["schedule_llm_backoff_active"], max_points
        ),
        "schedule_wakeup_session_resumed": _truncate_points(
            schedule_payload["schedule_wakeup_session_resumed"], max_points
        ),
        "schedule_wakeup_consecutive_failures": _truncate_points(
            schedule_payload["schedule_wakeup_consecutive_failures"], max_points
        ),
    }

    summary = {
        "journal_friction": _summarize_metric(
            series["journal_friction"],
            high_threshold=0.62,
            settle_threshold=0.35,
            min_drop=0.15,
        ),
        "journal_lyapunov": _summarize_metric(
            series["journal_lyapunov"],
            high_threshold=0.1,
            settle_threshold=0.0,
            min_drop=0.2,
        ),
        "wakeup_avg_friction": _summarize_metric(
            series["wakeup_avg_friction"],
            high_threshold=0.62,
            settle_threshold=0.35,
            min_drop=0.15,
        ),
        "wakeup_max_friction": _summarize_metric(
            series["wakeup_max_friction"],
            high_threshold=0.7,
            settle_threshold=0.4,
            min_drop=0.2,
        ),
        "wakeup_max_lyapunov": _summarize_metric(
            series["wakeup_max_lyapunov"],
            high_threshold=0.1,
            settle_threshold=0.0,
            min_drop=0.15,
        ),
        "wakeup_collision_success_rate": _summarize_metric(
            series["wakeup_collision_success_rate"],
        ),
        "wakeup_consecutive_failures": _summarize_metric(
            series["wakeup_consecutive_failures"],
        ),
        "wakeup_session_resumed": _summarize_metric(
            series["wakeup_session_resumed"],
        ),
        "wakeup_write_gateway_written": _summarize_metric(
            series["wakeup_write_gateway_written"],
        ),
        "wakeup_write_gateway_skipped": _summarize_metric(
            series["wakeup_write_gateway_skipped"],
        ),
        "wakeup_write_gateway_rejected": _summarize_metric(
            series["wakeup_write_gateway_rejected"],
        ),
        "wakeup_llm_prompt_tokens": _summarize_metric(
            series["wakeup_llm_prompt_tokens"],
        ),
        "wakeup_llm_completion_tokens": _summarize_metric(
            series["wakeup_llm_completion_tokens"],
        ),
        "wakeup_llm_total_tokens": _summarize_metric(
            series["wakeup_llm_total_tokens"],
        ),
        "wakeup_llm_preflight_latency": _summarize_metric(
            series["wakeup_llm_preflight_latency"],
        ),
        "wakeup_llm_selection_latency": _summarize_metric(
            series["wakeup_llm_selection_latency"],
        ),
        "wakeup_llm_probe_latency": _summarize_metric(
            series["wakeup_llm_probe_latency"],
        ),
        "wakeup_llm_preflight_timeout_count": _summarize_metric(
            series["wakeup_llm_preflight_timeout_count"],
        ),
        "wakeup_scribe_triggered": _summarize_metric(
            series["wakeup_scribe_triggered"],
        ),
        "schedule_governance_cooldown_applied": _summarize_metric(
            series["schedule_governance_cooldown_applied"],
        ),
        "schedule_governance_cooldown_deferred": _summarize_metric(
            series["schedule_governance_cooldown_deferred"],
        ),
        "schedule_llm_backoff_requested": _summarize_metric(
            series["schedule_llm_backoff_requested"],
        ),
        "schedule_llm_backoff_active": _summarize_metric(
            series["schedule_llm_backoff_active"],
        ),
        "schedule_wakeup_session_resumed": _summarize_metric(
            series["schedule_wakeup_session_resumed"],
        ),
        "schedule_wakeup_consecutive_failures": _summarize_metric(
            series["schedule_wakeup_consecutive_failures"],
        ),
        "wakeup_council_total": int(
            sum(float(point["value"]) for point in series["wakeup_council_count"])
        ),
        "wakeup_frozen_total": int(
            sum(float(point["value"]) for point in series["wakeup_frozen_count"])
        ),
        "wakeup_write_gateway_written_total": int(
            sum(float(point["value"]) for point in series["wakeup_write_gateway_written"])
        ),
        "wakeup_write_gateway_skipped_total": int(
            sum(float(point["value"]) for point in series["wakeup_write_gateway_skipped"])
        ),
        "wakeup_write_gateway_rejected_total": int(
            sum(float(point["value"]) for point in series["wakeup_write_gateway_rejected"])
        ),
        "wakeup_llm_call_total": int(
            sum(float(point["value"]) for point in series["wakeup_llm_call_count"])
        ),
        "wakeup_llm_preflight_timeout_total": int(
            sum(float(point["value"]) for point in series["wakeup_llm_preflight_timeout_count"])
        ),
        "wakeup_scribe_triggered_total": int(
            sum(float(point["value"]) for point in series["wakeup_scribe_triggered"])
        ),
        "wakeup_runtime_session_count": int(
            wakeup_payload["wakeup_runtime_state"].get("session_count", 0) or 0
        ),
        "wakeup_resumed_cycle_total": int(
            wakeup_payload["wakeup_runtime_state"].get("resumed_cycle_count", 0) or 0
        ),
        "wakeup_latest_session_id": (
            str(wakeup_payload["wakeup_runtime_state"].get("latest_session_id") or "").strip()
            or None
        ),
        "wakeup_latest_resume_state_path": (
            str(
                wakeup_payload["wakeup_runtime_state"].get("latest_resume_state_path") or ""
            ).strip()
            or None
        ),
        "wakeup_latest_heartbeat_window_cycle": _to_int(
            wakeup_payload["wakeup_runtime_state"].get("latest_heartbeat_window_cycle")
        ),
        "wakeup_latest_scribe_status": (
            str(wakeup_payload["wakeup_scribe_state"].get("latest_status") or "").strip() or None
        ),
        "wakeup_latest_scribe_generation_mode": (
            str(wakeup_payload["wakeup_scribe_state"].get("latest_generation_mode") or "").strip()
            or None
        ),
        "wakeup_latest_scribe_state_document_posture": (
            str(
                wakeup_payload["wakeup_scribe_state"].get("latest_state_document_posture") or ""
            ).strip()
            or None
        ),
        "wakeup_latest_scribe_anchor_status_line": (
            str(
                wakeup_payload["wakeup_scribe_state"].get("latest_anchor_status_line") or ""
            ).strip()
            or None
        ),
        "wakeup_latest_scribe_problem_route_status_line": (
            str(
                wakeup_payload["wakeup_scribe_state"].get("latest_problem_route_status_line") or ""
            ).strip()
            or None
        ),
        "wakeup_latest_scribe_problem_route_secondary_labels": (
            str(
                wakeup_payload["wakeup_scribe_state"].get("latest_problem_route_secondary_labels")
                or ""
            ).strip()
            or None
        ),
        "wakeup_latest_scribe_available_source": (
            str(wakeup_payload["wakeup_scribe_state"].get("latest_available_source") or "").strip()
            or None
        ),
        "wakeup_latest_scribe_skip_reason": (
            str(wakeup_payload["wakeup_scribe_state"].get("latest_skip_reason") or "").strip()
            or None
        ),
        "schedule_governance_cooldown_applied_total": int(
            sum(float(point["value"]) for point in series["schedule_governance_cooldown_applied"])
        ),
        "schedule_governance_cooldown_deferred_total": int(
            sum(float(point["value"]) for point in series["schedule_governance_cooldown_deferred"])
        ),
        "schedule_llm_backoff_requested_total": int(
            sum(float(point["value"]) for point in series["schedule_llm_backoff_requested"])
        ),
        "schedule_llm_backoff_active_total": int(
            sum(float(point["value"]) for point in series["schedule_llm_backoff_active"])
        ),
        "schedule_wakeup_runtime_session_count": int(
            schedule_payload["schedule_runtime_state"].get("session_count", 0) or 0
        ),
        "schedule_wakeup_resumed_cycle_total": int(
            schedule_payload["schedule_runtime_state"].get("resumed_cycle_count", 0) or 0
        ),
        "schedule_wakeup_latest_session_id": (
            str(schedule_payload["schedule_runtime_state"].get("latest_session_id") or "").strip()
            or None
        ),
        "schedule_wakeup_latest_state_path": (
            str(schedule_payload["schedule_runtime_state"].get("latest_state_path") or "").strip()
            or None
        ),
        "warning_count": len(warnings),
        "invalid_json_total": (
            int(journal_invalid_json_line_count)
            + int(wakeup_invalid_json_line_count)
            + int(schedule_invalid_json_line_count)
            + int(schedule_state_invalid_json_count)
        ),
    }

    overall_ok = (
        journal_invalid_json_line_count == 0
        and wakeup_invalid_json_line_count == 0
        and schedule_invalid_json_line_count == 0
        and schedule_state_invalid_json_count == 0
    )
    status_surface = _dashboard_status_surface(
        overall_ok=overall_ok,
        summary=summary,
        metrics={
            "wakeup_cycle_count": len(wakeup_rows),
            "schedule_cycle_count": len(schedule_rows),
        },
        inputs={
            "wakeup_path": wakeup_path.as_posix(),
            "schedule_history_path": (
                None if schedule_history_path is None else schedule_history_path.as_posix()
            ),
        },
    )
    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        **status_surface,
        "inputs": {
            "journal_path": journal_path.as_posix(),
            "wakeup_path": wakeup_path.as_posix(),
            "schedule_history_path": (
                None if schedule_history_path is None else schedule_history_path.as_posix()
            ),
            "schedule_state_path": (
                None if schedule_state_path is None else schedule_state_path.as_posix()
            ),
            "max_points": max_points,
        },
        "metrics": {
            "journal_entry_count": len(journal_rows),
            "journal_invalid_json_line_count": journal_invalid_json_line_count,
            "wakeup_cycle_count": len(wakeup_rows),
            "wakeup_invalid_json_line_count": wakeup_invalid_json_line_count,
            "schedule_cycle_count": len(schedule_rows),
            "schedule_invalid_json_line_count": schedule_invalid_json_line_count,
            "schedule_state_invalid_json_count": schedule_state_invalid_json_count,
            "journal_friction_point_count": len(series["journal_friction"]),
            "journal_lyapunov_point_count": len(series["journal_lyapunov"]),
            "wakeup_avg_friction_point_count": len(series["wakeup_avg_friction"]),
            "wakeup_max_friction_point_count": len(series["wakeup_max_friction"]),
            "wakeup_max_lyapunov_point_count": len(series["wakeup_max_lyapunov"]),
            "wakeup_collision_success_rate_point_count": len(
                series["wakeup_collision_success_rate"]
            ),
            "wakeup_consecutive_failures_point_count": len(series["wakeup_consecutive_failures"]),
            "wakeup_session_resumed_point_count": len(series["wakeup_session_resumed"]),
            "wakeup_write_gateway_written_point_count": len(series["wakeup_write_gateway_written"]),
            "wakeup_write_gateway_skipped_point_count": len(series["wakeup_write_gateway_skipped"]),
            "wakeup_write_gateway_rejected_point_count": len(
                series["wakeup_write_gateway_rejected"]
            ),
            "wakeup_llm_call_count_point_count": len(series["wakeup_llm_call_count"]),
            "wakeup_llm_prompt_tokens_point_count": len(series["wakeup_llm_prompt_tokens"]),
            "wakeup_llm_completion_tokens_point_count": len(series["wakeup_llm_completion_tokens"]),
            "wakeup_llm_total_tokens_point_count": len(series["wakeup_llm_total_tokens"]),
            "wakeup_llm_preflight_latency_point_count": len(series["wakeup_llm_preflight_latency"]),
            "wakeup_llm_selection_latency_point_count": len(series["wakeup_llm_selection_latency"]),
            "wakeup_llm_probe_latency_point_count": len(series["wakeup_llm_probe_latency"]),
            "wakeup_llm_preflight_timeout_count_point_count": len(
                series["wakeup_llm_preflight_timeout_count"]
            ),
            "wakeup_scribe_triggered_point_count": len(series["wakeup_scribe_triggered"]),
            "schedule_governance_cooldown_applied_point_count": len(
                series["schedule_governance_cooldown_applied"]
            ),
            "schedule_governance_cooldown_deferred_point_count": len(
                series["schedule_governance_cooldown_deferred"]
            ),
            "schedule_llm_backoff_requested_point_count": len(
                series["schedule_llm_backoff_requested"]
            ),
            "schedule_llm_backoff_active_point_count": len(series["schedule_llm_backoff_active"]),
            "schedule_wakeup_session_resumed_point_count": len(
                series["schedule_wakeup_session_resumed"]
            ),
            "schedule_wakeup_consecutive_failures_point_count": len(
                series["schedule_wakeup_consecutive_failures"]
            ),
        },
        "summary": summary,
        "series": series,
        "wakeup_runtime_state": wakeup_payload["wakeup_runtime_state"],
        "wakeup_scribe_state": wakeup_payload["wakeup_scribe_state"],
        "recent_wakeup_cycles": wakeup_payload["recent_wakeup_cycles"],
        "recent_schedule_cycles": schedule_payload["recent_schedule_cycles"],
        "schedule_runtime_state": schedule_payload["schedule_runtime_state"],
        "schedule_state": schedule_payload["schedule_state"],
        "warnings": warnings,
    }


def _render_value(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _render_cards(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    schedule_state = payload.get("schedule_state", {})
    schedule_runtime_state = payload.get("schedule_runtime_state", {})
    llm_backoff_active = bool(schedule_state.get("llm_backoff_active", False))
    llm_backoff_mode = str(schedule_state.get("llm_backoff_mode") or "none")
    cards = [
        (
            "Journal Friction",
            summary["journal_friction"]["latest"],
            summary["journal_friction"]["trend"],
        ),
        (
            "Journal Lyapunov",
            summary["journal_lyapunov"]["latest"],
            summary["journal_lyapunov"]["trend"],
        ),
        (
            "Wake-up Avg Friction",
            summary["wakeup_avg_friction"]["latest"],
            summary["wakeup_avg_friction"]["trend"],
        ),
        (
            "Collision Success",
            summary["wakeup_collision_success_rate"]["latest"],
            summary["wakeup_collision_success_rate"]["trend"],
        ),
        (
            "Wake-up Max Lyapunov",
            summary["wakeup_max_lyapunov"]["latest"],
            summary["wakeup_max_lyapunov"]["trend"],
        ),
        (
            "Runtime Sessions",
            summary["wakeup_runtime_session_count"],
            "wakeup",
        ),
        (
            "Resumed Cycles",
            summary["wakeup_resumed_cycle_total"],
            "cycles",
        ),
        (
            "Failure Streak",
            summary["wakeup_consecutive_failures"]["latest"],
            summary["wakeup_consecutive_failures"]["trend"],
        ),
        (
            "Scribe Status",
            summary["wakeup_latest_scribe_status"] or "none",
            (
                summary["wakeup_latest_scribe_problem_route_secondary_labels"]
                or summary["wakeup_latest_scribe_problem_route_status_line"]
                or summary["wakeup_latest_scribe_state_document_posture"]
                or summary["wakeup_latest_scribe_generation_mode"]
                or "wakeup"
            ),
        ),
        (
            "Scribe Triggered",
            summary["wakeup_scribe_triggered_total"],
            "cycles",
        ),
        (
            "Gateway Writes",
            summary["wakeup_write_gateway_written_total"],
            "records",
        ),
        (
            "Gateway Rejected",
            summary["wakeup_write_gateway_rejected_total"],
            "records",
        ),
        (
            "Wake-up LLM Tokens",
            summary["wakeup_llm_total_tokens"]["latest"],
            summary["wakeup_llm_total_tokens"]["trend"],
        ),
        (
            "Prompt Tokens",
            summary["wakeup_llm_prompt_tokens"]["latest"],
            summary["wakeup_llm_prompt_tokens"]["trend"],
        ),
        (
            "Completion Tokens",
            summary["wakeup_llm_completion_tokens"]["latest"],
            summary["wakeup_llm_completion_tokens"]["trend"],
        ),
        (
            "LLM Preflight",
            summary["wakeup_llm_preflight_latency"]["latest"],
            "ms",
        ),
        (
            "LLM Timeouts",
            summary["wakeup_llm_preflight_timeout_total"],
            "cycles",
        ),
        (
            "Cooldown Applied",
            summary["schedule_governance_cooldown_applied_total"],
            "schedule",
        ),
        (
            "Cooldown Deferred",
            summary["schedule_governance_cooldown_deferred_total"],
            "schedule",
        ),
        (
            "LLM Backoff",
            "active" if llm_backoff_active else "idle",
            llm_backoff_mode,
        ),
        (
            "Schedule Wakeup Sessions",
            summary["schedule_wakeup_runtime_session_count"],
            "schedule",
        ),
        (
            "Schedule Resumed",
            summary["schedule_wakeup_resumed_cycle_total"],
            "cycles",
        ),
        (
            "Sched Failure Streak",
            summary["schedule_wakeup_consecutive_failures"]["latest"],
            summary["schedule_wakeup_consecutive_failures"]["trend"],
        ),
        (
            "Active Cooldowns",
            schedule_state.get("active_governance_cooldown_count", 0),
            "categories",
        ),
        (
            "Schedule Session",
            schedule_runtime_state.get("latest_session_id") or "n/a",
            "latest",
        ),
        ("LLM Calls", summary["wakeup_llm_call_total"], "cycles"),
        ("Council Total", summary["wakeup_council_total"], "cycles"),
        ("Frozen Total", summary["wakeup_frozen_total"], "cycles"),
    ]
    items = []
    for title, value, subtitle in cards:
        items.append(
            "<article class='card'>"
            f"<div class='card-title'>{escape(title)}</div>"
            f"<div class='card-value'>{escape(_render_value(value))}</div>"
            f"<div class='card-subtitle'>{escape(str(subtitle))}</div>"
            "</article>"
        )
    return "".join(items)


def _series_bounds(
    points: Sequence[dict[str, Any]],
    *,
    fixed_min: Optional[float] = None,
    fixed_max: Optional[float] = None,
    include_zero: bool = False,
) -> tuple[float, float]:
    values = [float(point["value"]) for point in points]
    if include_zero:
        values.append(0.0)
    if not values:
        return (0.0, 1.0)
    low = fixed_min if fixed_min is not None else min(values)
    high = fixed_max if fixed_max is not None else max(values)
    if low == high:
        pad = 0.5 if abs(low) < 1 else abs(low) * 0.2
        low -= pad
        high += pad
    return float(low), float(high)


def _render_chart_svg(
    points: Sequence[dict[str, Any]],
    *,
    color: str,
    width: int = 520,
    height: int = 220,
    fixed_min: Optional[float] = None,
    fixed_max: Optional[float] = None,
    include_zero: bool = False,
    reference_lines: Optional[Sequence[tuple[float, str, str]]] = None,
) -> str:
    if not points:
        return "<div class='empty-chart'>No data available for this source.</div>"

    left = 48
    right = 12
    top = 18
    bottom = 30
    inner_width = width - left - right
    inner_height = height - top - bottom
    low, high = _series_bounds(
        points,
        fixed_min=fixed_min,
        fixed_max=fixed_max,
        include_zero=include_zero,
    )
    value_range = max(high - low, 1e-6)

    def _x_position(index: int) -> float:
        if len(points) == 1:
            return float(left + (inner_width / 2))
        return float(left + (inner_width * (index / (len(points) - 1))))

    def _y_position(value: float) -> float:
        normalized = (value - low) / value_range
        return float(top + inner_height - (normalized * inner_height))

    grid_lines = []
    for step in range(5):
        value = low + ((high - low) * (step / 4))
        y = _y_position(value)
        grid_lines.append(
            f"<line class='grid' x1='{left}' y1='{y:.2f}' x2='{width-right}' y2='{y:.2f}' />"
            f"<text class='axis-label' x='6' y='{y + 4:.2f}'>{escape(_render_value(round(value, 2)))}</text>"
        )

    refs = []
    for line_value, label, css_class in reference_lines or ():
        if line_value < low or line_value > high:
            continue
        y = _y_position(line_value)
        refs.append(
            f"<line class='reference {escape(css_class)}' x1='{left}' y1='{y:.2f}' "
            f"x2='{width-right}' y2='{y:.2f}' />"
            f"<text class='reference-label' x='{width-right-2}' y='{y - 4:.2f}'>{escape(label)}</text>"
        )

    polyline = []
    circles = []
    for index, point in enumerate(points):
        x = _x_position(index)
        y = _y_position(float(point["value"]))
        polyline.append(f"{x:.2f},{y:.2f}")
        title = (
            f"{_compact_timestamp(point['timestamp'])} | {point['phase']} | "
            f"{point['label']} = {_render_value(point['value'])}"
        )
        circles.append(
            f"<circle class='point' cx='{x:.2f}' cy='{y:.2f}' r='3.5' fill='{escape(color)}'>"
            f"<title>{escape(title)}</title></circle>"
        )

    first_timestamp = _compact_timestamp(points[0]["timestamp"])
    last_timestamp = _compact_timestamp(points[-1]["timestamp"])
    return (
        f"<svg viewBox='0 0 {width} {height}' class='chart' role='img' "
        "aria-label='Line chart'>"
        f"{''.join(grid_lines)}"
        f"{''.join(refs)}"
        f"<polyline class='trend-line' fill='none' stroke='{escape(color)}' "
        f"stroke-width='3' points='{' '.join(polyline)}' />"
        f"{''.join(circles)}"
        f"<text class='axis-label' x='{left}' y='{height-8}'>{escape(first_timestamp)}</text>"
        f"<text class='axis-label axis-label-right' x='{width-right}' y='{height-8}'>{escape(last_timestamp)}</text>"
        "</svg>"
    )


def _render_chart_panel(
    *,
    title: str,
    subtitle: str,
    svg: str,
    summary: dict[str, Any],
) -> str:
    footer = (
        f"latest={_render_value(summary['latest'])} | max={_render_value(summary['max'])} | "
        f"trend={summary['trend']} | convergence={summary['convergence_events']}"
    )
    return (
        "<section class='panel'>"
        f"<h2>{escape(title)}</h2>"
        f"<p class='panel-subtitle'>{escape(subtitle)}</p>"
        f"{svg}"
        f"<div class='panel-footer'>{escape(footer)}</div>"
        "</section>"
    )


def _render_recent_cycles(rows: Sequence[dict[str, Any]]) -> str:
    if not rows:
        return "<div class='empty-table'>No wake-up cycles recorded yet.</div>"

    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{escape(str(row.get('cycle') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('status') or 'unknown'))}</td>"
            f"<td>{escape(_compact_timestamp(row.get('timestamp')))}</td>"
            f"<td>{escape(str(row.get('session_id') or 'n/a'))}</td>"
            f"<td>{escape('yes' if row.get('session_resumed') else 'no')}</td>"
            f"<td>{escape(_render_value(row.get('heartbeat_window_cycle')))}</td>"
            f"<td>{escape(str(row.get('consecutive_failure_count') or 0))}</td>"
            f"<td>{escape(_render_value(row.get('avg_friction_score')))}</td>"
            f"<td>{escape(_render_value(row.get('max_lyapunov_proxy')))}</td>"
            f"<td>{escape(_render_value(row.get('collision_success_rate')))}</td>"
            f"<td>{escape(str(row.get('council_count') or 0))}</td>"
            f"<td>{escape(str(row.get('frozen_count') or 0))}</td>"
            f"<td>{escape(str(row.get('write_gateway_written') or 0))}</td>"
            f"<td>{escape(str(row.get('write_gateway_rejected') or 0))}</td>"
            f"<td>{escape(str(row.get('llm_call_count') or 0))}</td>"
            f"<td>{escape(str(row.get('llm_prompt_tokens_total') or 0))}</td>"
            f"<td>{escape(str(row.get('llm_completion_tokens_total') or 0))}</td>"
            f"<td>{escape(str(row.get('llm_total_tokens') or 0))}</td>"
            f"<td>{escape(_render_value(row.get('llm_preflight_latency_ms')))}</td>"
            f"<td>{escape(_render_value(row.get('llm_preflight_selection_latency_ms')))}</td>"
            f"<td>{escape(_render_value(row.get('llm_preflight_probe_latency_ms')))}</td>"
            f"<td>{escape(str(row.get('llm_preflight_timeout_count') or 0))}</td>"
            f"<td>{escape(str(row.get('llm_preflight_reason') or 'n/a'))}</td>"
            f"<td>{escape('yes' if row.get('consolidation_ran') else 'no')}</td>"
            f"<td>{escape(str(row.get('consolidation_promoted_count') or 0))}</td>"
            f"<td>{escape(str(row.get('scribe_status') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('scribe_generation_mode') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('scribe_state_document_posture') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('scribe_problem_route_status_line') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('scribe_problem_route_secondary_labels') or 'n/a'))}</td>"
            f"<td>{escape(str(row.get('scribe_latest_available_source') or 'n/a'))}</td>"
            f"<td>{escape('yes' if row.get('circuit_breaker_paused') else 'no')}</td>"
            f"<td>{escape(', '.join(str(item) for item in (row.get('llm_backends') or [])) or 'n/a')}</td>"
            f"<td>{escape(', '.join(str(item) for item in (row.get('llm_models') or [])) or 'n/a')}</td>"
            "</tr>"
        )
    return (
        "<table class='cycle-table'>"
        "<thead><tr><th>Cycle</th><th>Status</th><th>Timestamp</th>"
        "<th>Session</th><th>Resumed</th><th>Window Cycle</th><th>Failure Streak</th>"
        "<th>Avg Friction</th><th>Max Lyapunov</th><th>Collision Rate</th><th>Council</th><th>Frozen</th>"
        "<th>Gateway Writes</th><th>Gateway Rejected</th><th>LLM Calls</th>"
        "<th>Prompt Tokens</th><th>Completion Tokens</th><th>LLM Tokens</th><th>Preflight ms</th><th>Select ms</th>"
        "<th>Probe ms</th><th>Timeouts</th><th>Preflight Reason</th><th>Consolidated</th><th>Promoted</th>"
        "<th>Scribe Status</th><th>Scribe Mode</th><th>Scribe Posture</th><th>Scribe Route</th>"
        "<th>Scribe Secondary</th><th>Scribe Source</th>"
        "<th>Paused</th><th>Backends</th><th>Models</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def _render_recent_schedule_cycles(rows: Sequence[dict[str, Any]]) -> str:
    if not rows:
        return "<div class='empty-table'>No schedule cycles recorded yet.</div>"

    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td>{escape(str(row.get('cycle') or 'n/a'))}</td>"
            f"<td>{escape(_compact_timestamp(row.get('timestamp')))}</td>"
            f"<td>{escape(', '.join(str(item) for item in (row.get('selected_categories') or [])) or 'n/a')}</td>"
            f"<td>{escape(', '.join(str(item) for item in (row.get('cooled_categories') or [])) or 'n/a')}</td>"
            f"<td>{escape(str(row.get('deferred_category_count') or 0))}</td>"
            f"<td>{escape('yes' if row.get('llm_backoff_requested') else 'no')}</td>"
            f"<td>{escape('yes' if row.get('llm_backoff_active') else 'no')}</td>"
            f"<td>{escape(str(row.get('wakeup_session_id') or 'n/a'))}</td>"
            f"<td>{escape('yes' if row.get('wakeup_session_resumed') else 'no')}</td>"
            f"<td>{escape(str(row.get('wakeup_consecutive_failures') or 0))}</td>"
            f"<td>{escape(_render_value(row.get('wakeup_next_cycle')))}</td>"
            f"<td>{escape(str(row.get('llm_backoff_mode') or 'none'))}</td>"
            f"<td>{escape(str(row.get('llm_backoff_action') or 'normal'))}</td>"
            f"<td>{escape(str(row.get('llm_backoff_reason_count') or 0))}</td>"
            f"<td>{escape(' | '.join(str(item) for item in (row.get('governance_breach_reasons') or [])) or 'n/a')}</td>"
            f"<td>{escape(' | '.join(str(item) for item in (row.get('llm_breach_reasons') or [])) or 'n/a')}</td>"
            "</tr>"
        )
    return (
        "<table class='cycle-table'>"
        "<thead><tr><th>Cycle</th><th>Timestamp</th><th>Selected Categories</th>"
        "<th>Cooled Categories</th><th>Deferred Categories</th><th>LLM Backoff Requested</th>"
        "<th>LLM Backoff Active</th><th>Wake-up Session</th><th>Wake-up Resumed</th>"
        "<th>Failure Streak</th><th>Wake-up Next Cycle</th><th>Backoff Mode</th><th>LLM Action</th>"
        "<th>LLM Reasons</th><th>Governance Breaches</th><th>LLM Breaches</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def render_html(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    wakeup_runtime_state = payload.get("wakeup_runtime_state", {})
    wakeup_scribe_state = payload.get("wakeup_scribe_state", {})
    warnings = payload.get("warnings", [])
    warning_html = ""
    if warnings:
        items = "".join(f"<li>{escape(str(item))}</li>" for item in warnings)
        warning_html = (
            "<section class='warnings'>" "<h2>Warnings</h2>" f"<ul>{items}</ul>" "</section>"
        )

    panels = [
        _render_chart_panel(
            title="Journal Friction",
            subtitle="Extracted from self_journal tension and governance traces.",
            svg=_render_chart_svg(
                payload["series"]["journal_friction"],
                color="#bd3f1d",
                fixed_min=0.0,
                fixed_max=1.0,
                reference_lines=((0.62, "council threshold", "threshold"),),
            ),
            summary=summary["journal_friction"],
        ),
        _render_chart_panel(
            title="Journal Lyapunov",
            subtitle="Prediction instability pulled from journal traces.",
            svg=_render_chart_svg(
                payload["series"]["journal_lyapunov"],
                color="#1f4e79",
                include_zero=True,
                reference_lines=((0.0, "zero line", "zero"),),
            ),
            summary=summary["journal_lyapunov"],
        ),
        _render_chart_panel(
            title="Wake-up Avg Friction",
            subtitle="Cycle-level average friction from autonomous wake-up results.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_avg_friction"],
                color="#8b5e00",
                fixed_min=0.0,
                fixed_max=1.0,
                reference_lines=((0.62, "council threshold", "threshold"),),
            ),
            summary=summary["wakeup_avg_friction"],
        ),
        _render_chart_panel(
            title="Wake-up Max Friction",
            subtitle="Peak friction per autonomous cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_max_friction"],
                color="#7b1e3a",
                fixed_min=0.0,
                fixed_max=1.0,
                reference_lines=((0.7, "peak threshold", "threshold"),),
            ),
            summary=summary["wakeup_max_friction"],
        ),
        _render_chart_panel(
            title="Wake-up Max Lyapunov",
            subtitle="Largest chaos proxy emitted by the wake-up loop per cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_max_lyapunov"],
                color="#2f6f4f",
                include_zero=True,
                reference_lines=((0.0, "zero line", "zero"),),
            ),
            summary=summary["wakeup_max_lyapunov"],
        ),
        _render_chart_panel(
            title="Wake-up Collision Success",
            subtitle="Collision count divided by considered stimuli for each autonomous cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_collision_success_rate"],
                color="#2b6b5d",
                fixed_min=0.0,
                fixed_max=1.0,
                include_zero=True,
                reference_lines=((0.5, "50%", "threshold"),),
            ),
            summary=summary["wakeup_collision_success_rate"],
        ),
        _render_chart_panel(
            title="Wake-up Failure Streak",
            subtitle="Consecutive Dream Engine failures carried across resumable heartbeat windows.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_consecutive_failures"],
                color="#8f2d23",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_consecutive_failures"],
        ),
        _render_chart_panel(
            title="Wake-up Session Resume",
            subtitle="Whether each wake-up cycle continued an existing runtime session.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_session_resumed"],
                color="#2c5f85",
                fixed_min=0.0,
                fixed_max=1.0,
                include_zero=True,
                reference_lines=((1.0, "resumed", "threshold"),),
            ),
            summary=summary["wakeup_session_resumed"],
        ),
        _render_chart_panel(
            title="Write Gateway Written",
            subtitle="Durable dream-collision records accepted by MemoryWriteGateway per cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_write_gateway_written"],
                color="#7f5a1f",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_write_gateway_written"],
        ),
        _render_chart_panel(
            title="Write Gateway Rejected",
            subtitle="Dream-collision writes blocked by provenance or evidence gates.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_write_gateway_rejected"],
                color="#8f2d23",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_write_gateway_rejected"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Prompt Tokens",
            subtitle="Prompt/input tokens observed during dream reflections per cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_prompt_tokens"],
                color="#4f5d8a",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_prompt_tokens"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Completion Tokens",
            subtitle="Completion/output tokens observed during dream reflections per cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_completion_tokens"],
                color="#7a4d7b",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_completion_tokens"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Tokens",
            subtitle="Observed total tokens consumed by dream reflections per cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_total_tokens"],
                color="#5b3f8c",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_total_tokens"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Preflight",
            subtitle="End-to-end LLM readiness latency per wake-up cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_preflight_latency"],
                color="#2c5f85",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_preflight_latency"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Selection Latency",
            subtitle="Backend selection and discovery latency before the probe begins.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_selection_latency"],
                color="#516d35",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_selection_latency"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Probe Latency",
            subtitle="Observed bounded inference-probe latency per wake-up cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_probe_latency"],
                color="#8a4f19",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_probe_latency"],
        ),
        _render_chart_panel(
            title="Wake-up LLM Timeouts",
            subtitle="Count of LLM preflight timeouts per wake-up cycle.",
            svg=_render_chart_svg(
                payload["series"]["wakeup_llm_preflight_timeout_count"],
                color="#8f2d23",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["wakeup_llm_preflight_timeout_count"],
        ),
        _render_chart_panel(
            title="Schedule Cooldown Applied",
            subtitle="How many categories were cooled by governance breaches in each schedule tick.",
            svg=_render_chart_svg(
                payload["series"]["schedule_governance_cooldown_applied"],
                color="#7b1e3a",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["schedule_governance_cooldown_applied"],
        ),
        _render_chart_panel(
            title="Schedule Cooldown Deferred",
            subtitle="How many categories were deferred because governance cooldown was already active.",
            svg=_render_chart_svg(
                payload["series"]["schedule_governance_cooldown_deferred"],
                color="#8b5e00",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["schedule_governance_cooldown_deferred"],
        ),
        _render_chart_panel(
            title="Schedule LLM Backoff Requested",
            subtitle="Cycle-level trigger count for global LLM runtime backoff.",
            svg=_render_chart_svg(
                payload["series"]["schedule_llm_backoff_requested"],
                color="#8f2d23",
                fixed_min=0.0,
                fixed_max=1.0,
                include_zero=True,
                reference_lines=((1.0, "requested", "threshold"),),
            ),
            summary=summary["schedule_llm_backoff_requested"],
        ),
        _render_chart_panel(
            title="Schedule LLM Backoff Active",
            subtitle="Whether the schedule was actively running in degraded reflection mode.",
            svg=_render_chart_svg(
                payload["series"]["schedule_llm_backoff_active"],
                color="#2c5f85",
                fixed_min=0.0,
                fixed_max=1.0,
                include_zero=True,
                reference_lines=((1.0, "active", "threshold"),),
            ),
            summary=summary["schedule_llm_backoff_active"],
        ),
        _render_chart_panel(
            title="Schedule Wake-up Resume",
            subtitle="Whether each schedule tick continued an existing nested wake-up runtime session.",
            svg=_render_chart_svg(
                payload["series"]["schedule_wakeup_session_resumed"],
                color="#2c5f85",
                fixed_min=0.0,
                fixed_max=1.0,
                include_zero=True,
                reference_lines=((1.0, "resumed", "threshold"),),
            ),
            summary=summary["schedule_wakeup_session_resumed"],
        ),
        _render_chart_panel(
            title="Schedule Wake-up Failure Streak",
            subtitle="Nested wake-up consecutive failure count visible from the schedule handoff.",
            svg=_render_chart_svg(
                payload["series"]["schedule_wakeup_consecutive_failures"],
                color="#8f2d23",
                fixed_min=0.0,
                include_zero=True,
            ),
            summary=summary["schedule_wakeup_consecutive_failures"],
        ),
    ]

    schedule_meta_parts = []
    if payload["inputs"].get("schedule_history_path"):
        schedule_meta_parts.append(
            f"schedule_history={escape(str(payload['inputs']['schedule_history_path']))}"
        )
    if payload["inputs"].get("schedule_state_path"):
        schedule_meta_parts.append(
            f"schedule_state={escape(str(payload['inputs']['schedule_state_path']))}"
        )
    schedule_runtime_state = payload.get("schedule_runtime_state", {})
    if schedule_runtime_state.get("latest_session_id"):
        schedule_meta_parts.append(
            f"schedule_wakeup_session={escape(str(schedule_runtime_state['latest_session_id']))}"
        )
    schedule_meta = ""
    if schedule_meta_parts:
        schedule_meta = " | " + " | ".join(schedule_meta_parts)

    wakeup_meta_parts = []
    if wakeup_runtime_state.get("latest_session_id"):
        wakeup_meta_parts.append(
            f"wakeup_session={escape(str(wakeup_runtime_state['latest_session_id']))}"
        )
    if wakeup_runtime_state.get("latest_resume_state_path"):
        wakeup_meta_parts.append(
            f"resume_state={escape(str(wakeup_runtime_state['latest_resume_state_path']))}"
        )
    wakeup_runtime_meta = ""
    if wakeup_meta_parts:
        wakeup_runtime_meta = " | " + " | ".join(wakeup_meta_parts)
    if wakeup_scribe_state.get("latest_status"):
        wakeup_runtime_meta += (
            f" | scribe_status={escape(str(wakeup_scribe_state['latest_status']))}"
        )
    if wakeup_scribe_state.get("latest_state_document_posture"):
        wakeup_runtime_meta += (
            " | "
            f"scribe_posture={escape(str(wakeup_scribe_state['latest_state_document_posture']))}"
        )
    if wakeup_scribe_state.get("latest_problem_route_status_line"):
        wakeup_runtime_meta += (
            " | "
            f"scribe_route={escape(str(wakeup_scribe_state['latest_problem_route_status_line']))}"
        )
    if wakeup_scribe_state.get("latest_problem_route_secondary_labels"):
        wakeup_runtime_meta += (
            " | "
            "scribe_secondary="
            f"{escape(str(wakeup_scribe_state['latest_problem_route_secondary_labels']))}"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ToneSoul Dream Observability Dashboard</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --ink: #18222f;
      --muted: #5e6b76;
      --panel: rgba(255, 252, 246, 0.84);
      --line: rgba(24, 34, 47, 0.12);
      --warning: #8f2d23;
      --shadow: 0 22px 60px rgba(24, 34, 47, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(189, 63, 29, 0.16), transparent 30%),
        radial-gradient(circle at bottom right, rgba(31, 78, 121, 0.18), transparent 34%),
        linear-gradient(180deg, #f8f4ec 0%, var(--bg) 100%);
      font-family: "Segoe UI", "PingFang TC", "Noto Sans TC", sans-serif;
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2rem, 4vw, 3.2rem);
      letter-spacing: 0.02em;
    }}
    .lede {{
      max-width: 860px;
      color: var(--muted);
      line-height: 1.6;
    }}
    .meta {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
      margin: 24px 0;
    }}
    .card, .panel, .warnings, .recent {{
      background: var(--panel);
      border: 1px solid rgba(24, 34, 47, 0.08);
      border-radius: 18px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .card {{
      padding: 16px;
    }}
    .card-title {{
      font-size: 0.86rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .card-value {{
      margin-top: 8px;
      font-size: 1.7rem;
      font-weight: 700;
    }}
    .card-subtitle {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .warnings {{
      padding: 18px 20px;
      margin-bottom: 18px;
      border-left: 6px solid var(--warning);
    }}
    .warnings h2 {{
      margin: 0 0 12px;
      font-size: 1rem;
    }}
    .warnings ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 18px;
    }}
    .panel {{
      padding: 18px;
    }}
    .panel h2 {{
      margin: 0;
      font-size: 1.05rem;
    }}
    .panel-subtitle {{
      margin: 8px 0 14px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }}
    .panel-footer {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.86rem;
    }}
    .chart {{
      width: 100%;
      height: auto;
      display: block;
      overflow: visible;
    }}
    .grid {{
      stroke: var(--line);
      stroke-width: 1;
    }}
    .reference {{
      stroke: rgba(24, 34, 47, 0.24);
      stroke-dasharray: 6 6;
      stroke-width: 1.5;
    }}
    .reference.zero {{
      stroke: rgba(31, 78, 121, 0.4);
    }}
    .reference.threshold {{
      stroke: rgba(189, 63, 29, 0.4);
    }}
    .reference-label, .axis-label {{
      fill: var(--muted);
      font-size: 11px;
      font-family: Consolas, "SFMono-Regular", monospace;
    }}
    .axis-label-right {{
      text-anchor: end;
    }}
    .trend-line {{
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .point {{
      stroke: rgba(255,255,255,0.9);
      stroke-width: 1.2;
    }}
    .empty-chart, .empty-table {{
      min-height: 220px;
      display: grid;
      place-items: center;
      color: var(--muted);
      border: 1px dashed rgba(24, 34, 47, 0.16);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.45);
    }}
    .recent {{
      margin-top: 18px;
      padding: 18px;
    }}
    .recent h2 {{
      margin: 0 0 12px;
      font-size: 1.05rem;
    }}
    .cycle-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.93rem;
    }}
    .cycle-table th,
    .cycle-table td {{
      text-align: left;
      padding: 10px 8px;
      border-top: 1px solid rgba(24, 34, 47, 0.08);
    }}
    .cycle-table th {{
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-size: 0.76rem;
    }}
    @media (max-width: 720px) {{
      main {{ padding: 24px 14px 36px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .cycle-table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Dream Observability Dashboard</h1>
      <p class="lede">
        Static observability artifact for ToneSoul Phase 7. It reads journal traces and
        autonomous wake-up loop outputs, then surfaces friction, runtime readiness, and
        schedule governance trendlines without requiring operators to inspect raw logs.
      </p>
      <div class="meta">
        generated_at={escape(str(payload["generated_at"]))}
        | journal={escape(str(payload["inputs"]["journal_path"]))}
        | wakeup={escape(str(payload["inputs"]["wakeup_path"]))}
        {wakeup_runtime_meta}
        {schedule_meta}
      </div>
    </header>
    <section class="cards">{_render_cards(payload)}</section>
    {warning_html}
    <section class="grid">{''.join(panels)}</section>
    <section class="recent">
      <h2>Recent Wake-up Cycles</h2>
      {_render_recent_cycles(payload.get("recent_wakeup_cycles", []))}
    </section>
    <section class="recent">
      <h2>Recent Schedule Cycles</h2>
      {_render_recent_schedule_cycles(payload.get("recent_schedule_cycles", []))}
    </section>
  </main>
</body>
</html>
"""


__all__ = ["HTML_FILENAME", "JSON_FILENAME", "build_dashboard", "render_html"]
