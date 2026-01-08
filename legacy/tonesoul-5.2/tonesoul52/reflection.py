import json
from typing import Dict, List, Optional

from .ystm.schema import utc_now


def _issue_suggestion(issue: str) -> str:
    if issue.startswith("missing_context_field:"):
        field = issue.split(":", 1)[1]
        return f"Provide context.{field} in the seed or CLI overrides."
    if issue.startswith("missing_section:"):
        section = issue.split(":", 1)[1]
        return f"Ensure constraints template includes {section}."
    if issue.startswith("missing_files:"):
        files = issue.split(":", 1)[1]
        return f"Ensure required files exist: {files}."
    suggestions = {
        "missing_assumptions": "Provide an assumptions list (can be empty).",
        "missing_constraints": "Provide a constraints list (can be empty).",
        "assumptions_not_list": "Assumptions must be a list.",
        "constraints_not_list": "Constraints must be a list.",
        "time_island_missing": "Include time_island with chronos/kairos/trace sections.",
        "time_island_chronos_missing": "Include time_island.chronos with required fields.",
        "time_island_kairos_missing": "Include time_island.kairos with required fields.",
        "time_island_trace_missing": "Include time_island.trace with required fields.",
        "time_island_chronos_time_stamp_missing": "Set chronos.time_stamp.",
        "time_island_chronos_dependency_basis_missing": "Set chronos.dependency_basis (list).",
        "time_island_chronos_change_log_missing": "Set chronos.change_log (list).",
        "time_island_kairos_trigger_missing": "Set kairos.trigger.",
        "time_island_kairos_decision_mode_missing": "Set kairos.decision_mode.",
        "time_island_trace_residual_risk_missing": "Set trace.residual_risk.",
        "time_island_trace_rollback_condition_missing": "Set trace.rollback_condition.",
        "frame_selection_mismatch": "Rebuild frame_plan from the same context input.",
        "input_hash_mismatch": "Ensure frame_plan uses the same context hash.",
        "missing_context_constraints": "Merge context constraints into constraints.md.",
        "constraints_empty": "Ensure constraint template is loaded and non-empty.",
        "ystm_acceptance_failed": "Run YSTM acceptance and resolve failures.",
        "evidence_empty": "Run evidence collector and include context/execution report paths.",
        "context_not_listed": "Add context.yaml path to evidence summary.",
        "execution_report_not_listed": "Add execution_report.md path to evidence summary.",
    }
    return suggestions.get(issue, "Review the gate issue and address the underlying cause.")


def build_reflection(
    gate_report: Dict[str, object],
    directives: Optional[Dict[str, bool]] = None,
) -> Optional[Dict[str, object]]:
    directives = directives or {}
    results = gate_report.get("results", []) if isinstance(gate_report.get("results"), list) else []
    issues = []
    for result in results:
        gate = result.get("gate")
        for issue in result.get("issues", []) or []:
            issues.append(
                {
                    "gate": gate,
                    "issue": issue,
                    "suggestion": _issue_suggestion(issue),
                }
            )

    if not issues:
        return None

    return {
        "generated_at": utc_now(),
        "overall": gate_report.get("overall"),
        "directives": directives,
        "issues": issues,
        "status": "open",
        "note": "Reflection captures improvements when gates raise issues.",
    }


def write_reflection(path: str, reflection: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(reflection, handle, indent=2)
