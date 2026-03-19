from __future__ import annotations

from typing import Any


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _copy_scalar_keys(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in keys:
        value = payload.get(key)
        if value is not None and _is_scalar(value):
            summary[key] = value
    return summary


def _summarize_registry_batch(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "selection_count",
        "selected_entry_count",
        "selected_url_count",
        "deferred_category_count",
        "deferred_entry_count",
        "warning_count",
        "ok",
    )
    for key in ("selected_entry_ids", "selected_categories", "deferred_categories", "warnings"):
        value = payload.get(key)
        if isinstance(value, list):
            summary[key] = list(value)
    return summary


def _summarize_autonomous_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "overall_ok",
        "generated_at",
        "urls_requested",
        "urls_ingested",
        "urls_failed",
        "stimuli_processed",
        "wakeup_overall_status",
        "wakeup_cycle_count",
        "dashboard_overall_ok",
    )
    runtime_state = payload.get("runtime_state")
    if isinstance(runtime_state, dict):
        summary["runtime_state"] = _copy_scalar_keys(
            runtime_state,
            "session_id",
            "next_cycle",
            "consecutive_failures",
            "last_status",
            "last_started_at",
            "last_finished_at",
            "last_duration_ms",
            "updated_at",
            "resumed",
            "state_path",
        )
    memory_write = payload.get("memory_write")
    if isinstance(memory_write, dict):
        summary["memory_write"] = _copy_scalar_keys(
            memory_write,
            "written",
            "skipped",
        )
    llm_policy = payload.get("llm_policy")
    if isinstance(llm_policy, dict):
        summary["llm_policy"] = dict(llm_policy)
    paths = payload.get("paths")
    if isinstance(paths, dict):
        summary["paths"] = dict(paths)
    wakeup_summary = payload.get("wakeup_summary")
    if isinstance(wakeup_summary, dict):
        compact_wakeup_summary = _summarize_wakeup_summary(wakeup_summary)
        if compact_wakeup_summary:
            summary["wakeup_summary"] = compact_wakeup_summary
    else:
        wakeup_payload = payload.get("wakeup_payload")
        if isinstance(wakeup_payload, dict):
            compact_wakeup_summary = _summarize_wakeup_summary(wakeup_payload)
            if compact_wakeup_summary:
                summary["wakeup_summary"] = compact_wakeup_summary
    return summary


def _summarize_wakeup_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "overall_status",
        "result_count",
        "latest_cycle",
        "latest_status",
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
    results = payload.get("results")
    latest_result: dict[str, Any] | None = None
    if isinstance(results, list):
        if "result_count" not in summary:
            summary["result_count"] = len(results)
        if results:
            candidate = results[-1]
            if isinstance(candidate, dict):
                latest_result = candidate
    latest_result = latest_result or (
        payload.get("latest_result") if isinstance(payload.get("latest_result"), dict) else None
    )
    if isinstance(latest_result, dict):
        if latest_result.get("cycle") is not None:
            summary["latest_cycle"] = latest_result.get("cycle")
        if latest_result.get("status") is not None:
            summary["latest_status"] = latest_result.get("status")
        cycle_summary = (
            latest_result.get("summary") if isinstance(latest_result.get("summary"), dict) else {}
        )
        if cycle_summary:
            summary.update(
                _copy_scalar_keys(
                    cycle_summary,
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
    return summary


def _summarize_tension_budget(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "status",
        "cooldown_cycles",
        "governance_breached",
        "llm_breached",
    )
    for key in ("breach_reasons", "governance_breach_reasons", "llm_breach_reasons"):
        value = payload.get(key)
        if isinstance(value, list):
            summary[key] = list(value)
    llm_policy = payload.get("llm_policy")
    if isinstance(llm_policy, dict):
        summary["llm_policy"] = dict(llm_policy)
    observation = payload.get("observation")
    if isinstance(observation, dict):
        summary["observation"] = _copy_scalar_keys(
            observation,
            "observed_cycles",
            "max_friction_score",
            "max_lyapunov_proxy",
            "council_count",
            "max_council_count",
            "max_llm_preflight_latency_ms",
            "max_llm_selection_latency_ms",
            "max_llm_probe_latency_ms",
            "llm_preflight_timeout_count",
            "max_llm_timeout_count",
            "max_consecutive_failure_count",
            "last_reason",
        )
    return summary


def _summarize_result(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "cycle",
        "status",
        "overall_ok",
        "duration_ms",
        "started_at",
        "finished_at",
    )
    registry_batch = payload.get("registry_batch")
    if isinstance(registry_batch, dict):
        summary["registry_batch"] = _summarize_registry_batch(registry_batch)
    autonomous_payload = payload.get("autonomous_payload")
    if isinstance(autonomous_payload, dict):
        summary["autonomous_payload"] = _summarize_autonomous_payload(autonomous_payload)
    tension_budget = payload.get("tension_budget")
    if isinstance(tension_budget, dict):
        summary["tension_budget"] = _summarize_tension_budget(tension_budget)
    return summary


def _summarize_state(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _copy_scalar_keys(
        payload,
        "cursor",
        "category_cursor",
        "cycles_run",
        "entry_state_count",
        "category_entry_cursor_count",
        "category_state_count",
        "updated_at",
    )
    last_entry_ids = payload.get("last_entry_ids")
    if isinstance(last_entry_ids, list):
        summary["last_entry_ids"] = list(last_entry_ids)
    entry_states = payload.get("entry_states")
    if isinstance(entry_states, dict):
        summary["entry_state_count"] = len(entry_states)
    category_entry_cursors = payload.get("category_entry_cursors")
    if isinstance(category_entry_cursors, dict):
        summary["category_entry_cursor_count"] = len(category_entry_cursors)
    category_states = payload.get("category_states")
    if isinstance(category_states, dict):
        summary["category_state_count"] = len(category_states)
    llm_backoff = payload.get("llm_backoff")
    if isinstance(llm_backoff, dict):
        summary["llm_backoff"] = _copy_scalar_keys(
            llm_backoff,
            "backoff_until_cycle",
            "last_status",
            "last_mode",
            "updated_at",
        )
        breach_reasons = llm_backoff.get("last_breach_reasons")
        if isinstance(breach_reasons, list):
            summary["llm_backoff"]["last_breach_reasons"] = list(breach_reasons)
    return summary


def summarize_schedule_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return payload

    summary = _copy_scalar_keys(
        payload,
        "generated_at",
        "overall_ok",
        "profile",
        "preflight_profile",
    )
    config = payload.get("config")
    if isinstance(config, dict):
        summary["config"] = dict(config)
    results = payload.get("results")
    if isinstance(results, list):
        summary["result_count"] = len(results)
        if results:
            latest = results[-1]
            if isinstance(latest, dict):
                summary["latest_result"] = _summarize_result(latest)
    else:
        result_count = payload.get("result_count")
        if isinstance(result_count, int):
            summary["result_count"] = result_count
        latest_result = payload.get("latest_result")
        if isinstance(latest_result, dict):
            summary["latest_result"] = _summarize_result(latest_result)
    state = payload.get("state")
    if isinstance(state, dict):
        summary["state"] = _summarize_state(state)
    return summary


def summarize_long_run_payload(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return payload

    summary = _copy_scalar_keys(payload, "overall_ok")
    for key in ("experiment", "gate"):
        value = payload.get(key)
        if isinstance(value, dict):
            summary[key] = dict(value)
        else:
            summary[key] = value
    summary["preflight"] = summarize_schedule_payload(payload.get("preflight"))
    summary["schedule"] = summarize_schedule_payload(payload.get("schedule"))
    return summary


__all__ = [
    "summarize_long_run_payload",
    "summarize_schedule_payload",
]
