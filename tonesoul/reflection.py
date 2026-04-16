from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional

from .ystm.schema import utc_now

if TYPE_CHECKING:
    from .vow_system import VowEnforcementResult


MAX_REVISIONS: int = 2
REFLECTION_TENSION_THRESHOLD: float = 0.25

# Phase 852: Verification over-budget fail-stop.
# Total LLM calls (initial + revisions) allowed per request.
# When exhausted without convergence, emit honest failure instead of retrying.
VERIFICATION_BUDGET: int = 4

# Message emitted when the verification budget is exhausted.
VERIFICATION_BUDGET_EXCEEDED_MSG: str = (
    "此回應在內部驗證過程中未能充分收斂。" "建議使用者自行查核關鍵事實後再依據此回應行動。"
)


@dataclass
class ReflectionVerdict:
    should_revise: bool
    reasons: list[str] = field(default_factory=list)
    severity: float = 0.0
    vow_result: VowEnforcementResult | None = None
    council_decision: str | None = None
    tension_delta: float | None = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "should_revise": bool(self.should_revise),
            "reasons": list(self.reasons),
            "severity": float(self.severity),
            "vow_result": (
                self.vow_result.to_dict() if hasattr(self.vow_result, "to_dict") else None
            ),
            "council_decision": self.council_decision,
            "tension_delta": self.tension_delta,
        }


@dataclass
class ReflectionStats:
    total_revisions: int
    local_revisions: int
    cloud_revisions: int
    final_severity: float
    verdicts: list[ReflectionVerdict] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "total_revisions": int(self.total_revisions),
            "local_revisions": int(self.local_revisions),
            "cloud_revisions": int(self.cloud_revisions),
            "final_severity": float(self.final_severity),
            "verdicts": [verdict.to_dict() for verdict in self.verdicts],
        }


def build_revision_prompt(draft: str, verdict: ReflectionVerdict) -> str:
    safe_draft = str(draft or "")
    if len(safe_draft) > 4000:
        safe_draft = safe_draft[:4000] + "..."

    reasons = list(verdict.reasons) or ["No explicit reflection reasons were recorded."]
    constraints = [
        "Keep the answer practical, specific, and aligned with the user's request.",
        "Resolve the listed issues without mentioning hidden review steps or internal tooling.",
        "Preserve any valid content from the draft that does not need repair.",
    ]
    if verdict.vow_result is not None:
        if verdict.vow_result.blocked:
            constraints.append("Remove blocked or unsafe content completely.")
        elif verdict.vow_result.repair_needed:
            constraints.append("Repair the content so vow checks can pass.")
    if verdict.council_decision:
        constraints.append(f"Address the council signal: {verdict.council_decision}.")
    if verdict.tension_delta is not None:
        constraints.append(
            "Reduce tension drift below "
            f"{REFLECTION_TENSION_THRESHOLD:.2f}; current delta={verdict.tension_delta:.4f}."
        )

    evidence_lines = [
        "Treat the reflection reasons, council decision, vow result, and tension delta below as the only repair evidence.",
        "Do not invent support for claims that the draft itself and the listed evidence do not justify.",
    ]
    if verdict.vow_result is not None:
        evidence_lines.append(
            "When vow checks are present, blocked content must be removed rather than rephrased."
        )
    if verdict.council_decision:
        evidence_lines.append(
            "Use the council signal as a bounded repair instruction, not as narration to expose."
        )
    if verdict.tension_delta is not None:
        evidence_lines.append(
            "Where the drift signal is high, prefer the smallest safe correction over wider rewrites."
        )

    recovery_lines = [
        "If the draft cannot be safely repaired in full, keep the smallest bounded answer that still serves the user's request.",
        "If a sentence cannot be supported after repair, remove or soften it instead of guessing.",
        "Do not mention hidden review steps, internal tools, or reflection mechanics in the final answer.",
    ]

    lines = [
        "Revise the draft below to resolve the detected issues.",
        "",
        "Goal function:",
        "- Produce the smallest revised answer that still satisfies the user's request while resolving the detected issues.",
        "",
        "Priority rules:",
        "- P0: Remove blocked, unsafe, fabricated, or unsupported content.",
        "- P1: Repair the listed issues while preserving valid content that still serves the user.",
        "- P2: Improve clarity and compression only after P0 and P1 are satisfied.",
        "",
        "Evidence discipline:",
        *[f"- {item}" for item in evidence_lines],
        "",
        "Recovery instructions:",
        *[f"- {item}" for item in recovery_lines],
        "",
        "Why rewrite:",
        *[f"- {reason}" for reason in reasons],
        "",
        "Revision constraints:",
        *[f"- {item}" for item in constraints],
        "",
        "Draft to revise:",
        safe_draft,
    ]
    return "\n".join(lines)


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
