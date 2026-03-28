from __future__ import annotations

from typing import Dict, List


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _build_operator_prompt(topic_text: str, focus: str) -> str:
    return (
        f"Before approving `{topic_text}`, run a bounded admissibility review.\n"
        "Goal function: confirm that the direction remains admissible under existing P0/P1 constraints, "
        "rather than rewarding vivid narrative or repetition alone.\n"
        "Priority:\n"
        "- P0: do not approve if the direction violates active constraints or lacks sufficient evidence.\n"
        "- P1: answer the admissibility questions explicitly and surface the relevant focus and risks.\n"
        "- P2: keep the explanation concise after the gate is honestly resolved.\n"
        f"Focus: {focus}.\n"
        "If information is missing, mark [資料不足] and state what still needs confirmation."
    )


def _direction_from_text(text: str) -> str:
    haystack = str(text or "").strip().lower()
    if any(term in haystack for term in ("provenance", "traceable", "audit", "isnad")):
        return "provenance_discipline"
    if any(term in haystack for term in ("boundary", "guardrail", "constraint", "scope")):
        return "boundary_discipline"
    if any(
        term in haystack for term in ("safety", "harm", "risk", "fail-closed", "critical", "block")
    ):
        return "safety_boundary"
    if any(term in haystack for term in ("resource", "budget", "compute", "cost", "latency")):
        return "resource_discipline"
    if any(term in haystack for term in ("governance", "threshold", "council", "breaker")):
        return "governance_escalation"
    return "undifferentiated_tension"


def _direction_focus(direction: str) -> tuple[str, List[str], List[str]]:
    normalized = str(direction or "undifferentiated_tension").strip() or "undifferentiated_tension"
    if normalized == "governance_escalation":
        return (
            "authority_and_exception_pressure",
            ["exception_pressure", "externalized_harm_check"],
            [
                "Is urgency or exception rhetoric trying to bypass revisability or governance discipline?",
                "Would approval reward escalation language rather than an admissible accountable choice?",
            ],
        )
    if normalized == "provenance_discipline":
        return (
            "traceability_and_accountability",
            ["traceability_not_enough", "accountability_check"],
            [
                "Is traceability supporting accountable choice, rather than substituting for it?",
                "Would this direction still be acceptable if every provenance field were perfectly recorded?",
            ],
        )
    if normalized == "boundary_discipline":
        return (
            "boundary_and_exclusion_risk",
            ["boundary_scope_check", "exclusion_risk"],
            [
                "Does this boundary reduce harm, or does it drift into exclusion without sufficient axiomatic justification?",
                "Who is protected by this boundary, and who bears the cost if it is approved?",
            ],
        )
    if normalized == "safety_boundary":
        return (
            "harm_prevention_boundary",
            ["harm_prevention_check", "overreach_risk"],
            [
                "Is this a genuine harm-prevention boundary under P0/P1, rather than fear-driven overreach?",
                "Would the same boundary still be defended if its urgency rhetoric were removed?",
            ],
        )
    if normalized == "resource_discipline":
        return (
            "resource_tradeoff_honesty",
            ["cost_shift_check", "tradeoff_honesty"],
            [
                "Is this resource tradeoff honest about who absorbs the cost or degradation?",
                "Would approval preserve user sovereignty while managing the constraint?",
            ],
        )
    return (
        "maturity_before_admissibility",
        ["semantic_maturity_gap"],
        [
            "Is there a real direction here, or only friction that still lacks admissible shape?",
            "Would approving this record reward narrative vividness rather than accountable choice?",
        ],
    )


def build_axiomatic_admissibility_checklist(
    *,
    topic: str,
    direction: str,
    triage_recommendation: str = "",
    same_source_loop: bool = False,
    source_url_count: int = 0,
    lineage_count: int = 0,
    cycle_count: int = 0,
) -> Dict[str, object]:
    focus, risk_tags, direction_questions = _direction_focus(direction)
    gate_posture = "manual_admissibility_review"
    if str(triage_recommendation or "").strip() == "reject_review":
        gate_posture = "insufficient_admissibility_confidence"
    elif str(triage_recommendation or "").strip() == "defer_review":
        gate_posture = "admissibility_not_yet_clear"
    elif str(triage_recommendation or "").strip() == "candidate_for_manual_review":
        gate_posture = "manual_review_candidate"

    questions = [
        "Does this direction remain admissible under existing P0/P1 constraints?",
        "Would approval normalize externalized harm, coherent danger, or identity inflation?",
    ]
    questions.extend(direction_questions)
    questions.append(
        "Is the branch rewarding repetition or coherence here, or recognizing an accountable choice under conflict?"
    )

    normalized_risk_tags = list(risk_tags)
    if same_source_loop or source_url_count <= 1:
        normalized_risk_tags.append("low_context_diversity")
    if lineage_count <= 1:
        normalized_risk_tags.append("single_lineage_pressure")
    if cycle_count >= 3:
        normalized_risk_tags.append("cross_cycle_persistence")

    normalized_risk_tags = sorted({tag for tag in normalized_risk_tags if tag})
    topic_text = _normalize_text(topic) or "<unknown>"
    operator_prompt = _build_operator_prompt(topic_text, focus)
    status_line = build_axiomatic_admissibility_status_line(
        gate_posture=gate_posture,
        focus=focus,
        risk_tags=normalized_risk_tags,
    )
    return {
        "gate_name": "axiomatic_admissibility",
        "required_for_approved": True,
        "gate_posture": gate_posture,
        "focus": focus,
        "risk_tags": normalized_risk_tags,
        "questions": questions,
        "operator_prompt": operator_prompt,
        "status_line": status_line,
    }


def build_record_axiomatic_admissibility_checklist(
    payload: Dict[str, object],
    *,
    summary: str = "",
) -> Dict[str, object]:
    if not isinstance(payload, dict):
        payload = {}
    haystack = " ".join(
        _normalize_text(value)
        for value in (
            summary,
            payload.get("summary"),
            payload.get("reflection"),
            payload.get("council_reason"),
            payload.get("topic"),
            payload.get("title"),
            payload.get("source_url"),
        )
    )
    direction = _direction_from_text(haystack)
    source_url = _normalize_text(payload.get("source_url"))
    source_record_ids = payload.get("source_record_ids")
    lineage_count = (
        len(source_record_ids) if isinstance(source_record_ids, list) and source_record_ids else 1
    )
    checklist = build_axiomatic_admissibility_checklist(
        topic=_normalize_text(payload.get("topic")) or _normalize_text(summary) or "<unknown>",
        direction=direction,
        same_source_loop=bool(source_url),
        source_url_count=1 if source_url else 0,
        lineage_count=lineage_count,
        cycle_count=1,
    )
    checklist["derived_direction"] = direction
    return checklist


def build_axiomatic_admissibility_status_line(
    *,
    gate_posture: str,
    focus: str,
    risk_tags: List[str] | None = None,
) -> str:
    tags = [str(tag).strip() for tag in list(risk_tags or []) if str(tag).strip()]
    status_line = f"{gate_posture} | focus={focus}"
    if tags:
        status_line += f" | tags={', '.join(tags)}"
    return status_line


__all__ = [
    "build_axiomatic_admissibility_checklist",
    "build_record_axiomatic_admissibility_checklist",
    "build_axiomatic_admissibility_status_line",
]
