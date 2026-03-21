from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tonesoul.memory.subjectivity_handoff import build_handoff_surface
from tonesoul.scribe.scribe_engine import ScribeDraftResult

DEFAULT_STATUS_OUT = Path("docs/status/scribe_status_latest.json")
_REPRESENTATION_ROUTE_MARKERS = ("log entry", "date front matter")
_ROLE_BOUNDARY_ROUTE_MARKERS = ("the user",)
_RUNTIME_SELF_ROUTE_MARKERS = (
    "data streams",
    "processing cycles",
    "processing loops",
    "operational framework",
    "operational core",
    "processors",
    "my systems",
    "algorithms execute",
)
_EXECUTION_ROUTE_STATUSES = {"timeout", "llm_unavailable", "failed", "empty_response"}


def _route_label(route: dict[str, str]) -> str:
    return f"{route.get('family_code', '')}_{route.get('family', '')}"


def _route(
    *,
    family_code: str,
    family: str,
    broken_invariant: str,
    first_repair_surface: str,
    do_not_repair_first: str,
) -> dict[str, str]:
    return {
        "family_code": family_code,
        "family": family,
        "broken_invariant": broken_invariant,
        "first_repair_surface": first_repair_surface,
        "do_not_repair_first": do_not_repair_first,
    }


def _route_priority(route: dict[str, str]) -> int:
    broken_invariant = str(route.get("broken_invariant") or "")
    priority_map = {
        "observed_anchor_closure": 10,
        "chronicle_container_fidelity": 20,
        "chronicle_self_scope": 30,
        "observed_history_grounding": 40,
        "local_generation_latency_closure": 50,
        "local_model_availability": 60,
        "response_nonempty_generation": 70,
        "local_generation_closure": 80,
    }
    return priority_map.get(broken_invariant, 999)


def _dedupe_routes(routes: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for route in routes:
        key = (
            str(route.get("family_code") or ""),
            str(route.get("broken_invariant") or ""),
            str(route.get("first_repair_surface") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(route)
    return deduped


def scribe_queue_shape(result: ScribeDraftResult) -> str:
    if result.ok and result.chronicle_path is not None:
        return "scribe_chronicle_ready"
    if result.companion_path is not None:
        return "scribe_companion_only"
    return "scribe_generation_untracked"


def scribe_state_document_posture(result: ScribeDraftResult) -> str:
    tensions = int(result.observed_counts.get("tensions", 0))
    collisions = int(result.observed_counts.get("collisions", 0))
    crystals = int(result.observed_counts.get("crystals", 0))
    if tensions > 0 and collisions == 0 and crystals == 0:
        return "pressure_without_counterweight"
    if tensions > 0 and collisions > 0 and crystals == 0:
        return "contested_pressure"
    if tensions > 0 and crystals > 0:
        return "pressure_with_counterweight"
    if collisions > 0 and crystals > 0 and tensions == 0:
        return "contradiction_with_retained_belief"
    if collisions > 0 and tensions == 0:
        return "contradiction_visible"
    if crystals > 0 and tensions == 0 and collisions == 0:
        return "retained_belief_leaning"
    return "anchor_only"


def _boundary_messages(result: ScribeDraftResult) -> list[str]:
    messages: list[str] = []
    for attempt in result.llm_attempts:
        if str(attempt.get("status") or "").strip() != "boundary_rejected":
            continue
        message = str(attempt.get("error") or "").strip()
        if message:
            messages.append(message)
    return messages


def _candidate_problem_routes(result: ScribeDraftResult) -> list[dict[str, str]]:
    # Successful direct publication does not need a troubleshooting route.
    if result.ok and str(result.generation_mode or "").strip() == "llm_chronicle":
        return []

    boundary_messages = _boundary_messages(result)
    execution_statuses = [
        str(attempt.get("status") or "").strip()
        for attempt in result.llm_attempts
        if str(attempt.get("status") or "").strip() in _EXECUTION_ROUTE_STATUSES
    ]
    routes: list[dict[str, str]] = []

    if boundary_messages:
        joined = " | ".join(boundary_messages).casefold()
        if "missing_observed_anchor" in joined:
            routes.append(
                _route(
                    family_code="F1",
                    family="grounding_evidence_integrity",
                    broken_invariant="observed_anchor_closure",
                    first_repair_surface="anchor_selection_and_grounding_prompt",
                    do_not_repair_first="chronicle_style_or_personality_docs",
                )
            )
        if any(marker in joined for marker in _REPRESENTATION_ROUTE_MARKERS):
            routes.append(
                _route(
                    family_code="F7",
                    family="representation_localization_integrity",
                    broken_invariant="chronicle_container_fidelity",
                    first_repair_surface="post_generation_boundary_filter",
                    do_not_repair_first="memory_or_identity_layers",
                )
            )
        if any(marker in joined for marker in _ROLE_BOUNDARY_ROUTE_MARKERS) or any(
            marker in joined for marker in _RUNTIME_SELF_ROUTE_MARKERS
        ):
            routes.append(
                _route(
                    family_code="F6",
                    family="semantic_role_boundary_integrity",
                    broken_invariant="chronicle_self_scope",
                    first_repair_surface="semantic_boundary_guardrail",
                    do_not_repair_first="memory_import_or_style_rewrite",
                )
            )
        if not routes:
            routes.append(
                _route(
                    family_code="F1",
                    family="grounding_evidence_integrity",
                    broken_invariant="observed_history_grounding",
                    first_repair_surface="anchor_and_boundary_guardrail",
                    do_not_repair_first="prompt_style_or_personality_docs",
                )
            )

    if execution_statuses:
        if "timeout" in execution_statuses:
            routes.append(
                _route(
                    family_code="F4",
                    family="execution_contract_integrity",
                    broken_invariant="local_generation_latency_closure",
                    first_repair_surface="model_runtime_timeout_budget",
                    do_not_repair_first="chronicle_style_rewrite",
                )
            )
        elif "llm_unavailable" in execution_statuses:
            routes.append(
                _route(
                    family_code="F4",
                    family="execution_contract_integrity",
                    broken_invariant="local_model_availability",
                    first_repair_surface="model_allowlist_and_runtime_readiness",
                    do_not_repair_first="chronicle_style_rewrite",
                )
            )
        elif "empty_response" in execution_statuses:
            routes.append(
                _route(
                    family_code="F4",
                    family="execution_contract_integrity",
                    broken_invariant="response_nonempty_generation",
                    first_repair_surface="response_validation_and_retry_gate",
                    do_not_repair_first="chronicle_style_rewrite",
                )
            )
        else:
            routes.append(
                _route(
                    family_code="F4",
                    family="execution_contract_integrity",
                    broken_invariant="local_generation_closure",
                    first_repair_surface="model_runtime_and_fallback_ladder",
                    do_not_repair_first="chronicle_style_rewrite",
                )
            )

    return _dedupe_routes(routes)


def scribe_problem_route(result: ScribeDraftResult) -> dict[str, Any] | None:
    routes = _candidate_problem_routes(result)
    if not routes:
        return None

    ordered_routes = sorted(routes, key=_route_priority)
    dominant = dict(ordered_routes[0])
    secondary_routes = [dict(route) for route in ordered_routes[1:]]
    if secondary_routes:
        dominant["secondary_routes"] = secondary_routes
        dominant["secondary_route_labels"] = [_route_label(route) for route in secondary_routes]
    return dominant


def build_scribe_status_payload(result: ScribeDraftResult) -> dict[str, Any]:
    latest_available_source = (
        "chronicle_pair" if result.ok and result.chronicle_path is not None else "companion_only"
    )
    lead_anchor_summary = str(result.lead_anchor_summary or "").strip()
    primary_status_line = (
        f"{result.status} | mode={result.generation_mode or 'unknown'} "
        f"model={result.llm_model or 'unknown'} "
        f"fallback_mode={result.fallback_mode or 'unknown'} "
        f"attempts={len(result.llm_attempts)} latest={latest_available_source}"
    )
    posture = scribe_state_document_posture(result)
    runtime_status_line = (
        "state_document | "
        f"tensions={int(result.observed_counts.get('tensions', 0))} "
        f"collisions={int(result.observed_counts.get('collisions', 0))} "
        f"crystals={int(result.observed_counts.get('crystals', 0))} "
        f"posture={posture}"
    )
    anchor_status_line = f"anchor | {lead_anchor_summary}" if lead_anchor_summary else ""
    problem_route = scribe_problem_route(result)
    problem_route_status_line = ""
    problem_route_secondary_labels: list[str] = []
    if isinstance(problem_route, dict):
        problem_route_status_line = (
            "route | "
            f"family={problem_route.get('family_code', '')}_{problem_route.get('family', '')} "
            f"invariant={problem_route.get('broken_invariant', '')} "
            f"repair={problem_route.get('first_repair_surface', '')}"
        )
        secondary_labels = problem_route.get("secondary_route_labels")
        if isinstance(secondary_labels, list) and secondary_labels:
            problem_route_secondary_labels = [
                str(label).strip() for label in secondary_labels if str(label).strip()
            ]
            if problem_route_secondary_labels:
                problem_route_status_line += " secondary=" + ",".join(
                    problem_route_secondary_labels
                )
    artifact_policy_status_line = (
        f"artifact_source={latest_available_source} | "
        f"chronicle={'yes' if result.chronicle_path is not None else 'no'} "
        f"companion={'yes' if result.companion_path is not None else 'no'}"
    )
    queue_shape = scribe_queue_shape(result)
    handoff_extra_fields: dict[str, Any] = {
        "latest_available_source": latest_available_source,
        "lead_anchor_summary": lead_anchor_summary,
        "anchor_status_line": anchor_status_line,
        "problem_route_status_line": problem_route_status_line,
        "companion_path": None if result.companion_path is None else str(result.companion_path),
        "chronicle_path": None if result.chronicle_path is None else str(result.chronicle_path),
    }
    if problem_route_secondary_labels:
        handoff_extra_fields["problem_route_secondary_labels"] = ",".join(
            problem_route_secondary_labels
        )
    return {
        "generated_at": result.generated_at,
        "status": result.status,
        "title_hint": result.title_hint,
        "source_db_path": result.source_db_path,
        "observed_counts": dict(result.observed_counts),
        "lead_anchor_summary": lead_anchor_summary,
        "fallback_mode": result.fallback_mode,
        "generation_mode": result.generation_mode,
        "state_document_posture": posture,
        "llm_model": result.llm_model,
        "llm_attempt_count": len(result.llm_attempts),
        "llm_attempts": [dict(item) for item in result.llm_attempts],
        "chronicle_path": None if result.chronicle_path is None else str(result.chronicle_path),
        "companion_path": None if result.companion_path is None else str(result.companion_path),
        "latest_available_source": latest_available_source,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "anchor_status_line": anchor_status_line,
        "problem_route": problem_route,
        "problem_route_status_line": problem_route_status_line,
        "problem_route_secondary_labels": problem_route_secondary_labels,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": build_handoff_surface(
            queue_shape=queue_shape,
            requires_operator_action=False,
            status_lines=[
                primary_status_line,
                runtime_status_line,
                anchor_status_line,
                problem_route_status_line,
                artifact_policy_status_line,
            ],
            extra_fields=handoff_extra_fields,
        ),
    }


def write_scribe_status_artifact(
    result: ScribeDraftResult,
    *,
    out_path: Path = DEFAULT_STATUS_OUT,
) -> Path:
    payload = build_scribe_status_payload(result)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


__all__ = [
    "DEFAULT_STATUS_OUT",
    "build_scribe_status_payload",
    "scribe_queue_shape",
    "scribe_state_document_posture",
    "write_scribe_status_artifact",
]
