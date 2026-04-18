"""YSS gate stack: DCS, POAV, frame routing, seed checks, and escalation."""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import yaml

from .dcs import build_dcs_result, load_dcs_policy
from .escalation import decide_escalation, decision_mode_from_context, record_escalation
from .frame_router import build_frame_plan
from .issue_codes import IssueCode, issue
from .poav import score as score_poav
from .seed_schema_check import check_seed_schema
from .tech_trace.validate import validate_normalize_payload
from .ystm.acceptance import run_acceptance
from .ystm.schema import stable_hash, utc_now

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Compose the YSS gate stack (DCS, POAV, frame router, seed, acceptance) into one policy pass."
)


@dataclass
class GateResult:
    gate: str
    passed: bool
    issues: List[str]
    details: Optional[Dict[str, object]] = None


def _load_yaml(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("YAML payload must be a mapping.")
    return payload


def _load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be a mapping.")
    return payload


def _extract_section(text: str, header: str) -> str:
    lines = text.splitlines()
    target = header.strip().lower()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == target:
            start = idx + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        line = lines[idx].strip()
        if line.startswith("## ") and line.lower() != target:
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def context_lint(context: Dict[str, object]) -> GateResult:
    issues: List[str] = []
    ctx = context.get("context", {}) if isinstance(context.get("context"), dict) else {}
    for key in ("task", "objective", "domain", "audience", "mode"):
        if not ctx.get(key):
            issues.append(issue(IssueCode.MISSING_CONTEXT_FIELD, field=key))

    for list_key in ("assumptions", "constraints"):
        value = context.get(list_key)
        if value is None:
            if list_key == "assumptions":
                issues.append(issue(IssueCode.MISSING_ASSUMPTIONS))
            else:
                issues.append(issue(IssueCode.MISSING_CONSTRAINTS))
        elif not isinstance(value, list):
            if list_key == "assumptions":
                issues.append(issue(IssueCode.ASSUMPTIONS_NOT_LIST))
            else:
                issues.append(issue(IssueCode.CONSTRAINTS_NOT_LIST))

    time_island = context.get("time_island", {})
    if not isinstance(time_island, dict):
        issues.append(issue(IssueCode.TIME_ISLAND_MISSING))
    else:
        for section, keys in {
            "chronos": ("time_stamp", "dependency_basis", "change_log"),
            "kairos": ("trigger", "decision_mode"),
            "trace": ("residual_risk", "rollback_condition"),
        }.items():
            block = time_island.get(section, {})
            if not isinstance(block, dict):
                issues.append(issue(IssueCode.TIME_ISLAND_SECTION_MISSING, section=section))
            else:
                for key in keys:
                    if key not in block:
                        issues.append(
                            issue(
                                IssueCode.TIME_ISLAND_SECTION_KEY_MISSING, section=section, key=key
                            )
                        )

    return GateResult(
        gate="context_lint",
        passed=not issues,
        issues=issues,
    )


def router_replay(
    context: Dict[str, object],
    registry: List[Dict[str, object]],
    plan: Dict[str, object],
) -> GateResult:
    issues: List[str] = []
    expected = build_frame_plan(context, registry)
    expected_ids = [item.get("id") for item in expected.get("selected_frames", [])]
    actual_ids = [item.get("id") for item in plan.get("selected_frames", [])]
    if expected_ids != actual_ids:
        issues.append(issue(IssueCode.FRAME_SELECTION_MISMATCH))

    context_hash = stable_hash(json.dumps(context, sort_keys=True))
    if plan.get("input_hash") != context_hash:
        issues.append(issue(IssueCode.INPUT_HASH_MISMATCH))

    return GateResult(
        gate="router_replay",
        passed=not issues,
        issues=issues,
        details={"expected": expected_ids, "actual": actual_ids},
    )


def role_alignment(plan: Dict[str, object]) -> GateResult:
    issues: List[str] = []
    selected = plan.get("selected_frames")
    if not isinstance(selected, list):
        issues.append(issue(IssueCode.SELECTED_FRAMES_INVALID))
        return GateResult(gate="role_alignment", passed=False, issues=issues)

    if not plan.get("role_catalog"):
        issues.append(issue(IssueCode.ROLE_CATALOG_MISSING))

    role_summary = plan.get("role_summary")
    if not isinstance(role_summary, dict):
        issues.append(issue(IssueCode.ROLE_SUMMARY_MISSING))
    else:
        for key in ("operational_roles", "governance_roles"):
            value = role_summary.get(key)
            if not isinstance(value, list) or not value:
                if key == "operational_roles":
                    issues.append(issue(IssueCode.OPERATIONAL_ROLES_MISSING))
                else:
                    issues.append(issue(IssueCode.GOVERNANCE_ROLES_MISSING))
        if role_summary.get("max_governance_level") is None:
            issues.append(issue(IssueCode.MAX_GOVERNANCE_LEVEL_MISSING))

    for frame in selected:
        if not isinstance(frame, dict):
            issues.append(issue(IssueCode.SELECTED_FRAME_INVALID))
            continue
        frame_id = frame.get("id")
        roles = frame.get("roles") if isinstance(frame.get("roles"), list) else []
        gov_roles = (
            frame.get("governance_roles") if isinstance(frame.get("governance_roles"), list) else []
        )
        role_map = frame.get("role_map") if isinstance(frame.get("role_map"), list) else []
        if roles and not gov_roles:
            issues.append(issue(IssueCode.FRAME_GOVERNANCE_ROLES_MISSING, frame_id=frame_id))
        if roles and not role_map:
            issues.append(issue(IssueCode.ROLE_MAP_MISSING, frame_id=frame_id))
        for entry in role_map:
            if not isinstance(entry, dict):
                issues.append(issue(IssueCode.ROLE_MAP_ENTRY_INVALID, frame_id=frame_id))
                continue
            if entry.get("governance_role") in (None, "unknown"):
                issues.append(
                    issue(
                        IssueCode.GOVERNANCE_ROLE_UNKNOWN,
                        frame_id=frame_id,
                        role=entry.get("role"),
                    )
                )
            if entry.get("governance_level") is None:
                issues.append(
                    issue(
                        IssueCode.GOVERNANCE_LEVEL_MISSING,
                        frame_id=frame_id,
                        role=entry.get("role"),
                    )
                )

    return GateResult(
        gate="role_alignment",
        passed=not issues,
        issues=issues,
    )


def constraint_consistency(text: str) -> GateResult:
    issues: List[str] = []
    required_sections = ["## Scope", "## Safety", "## Technical", "## Governance"]
    for section in required_sections:
        if section not in text:
            issues.append(issue(IssueCode.MISSING_SECTION, section=section))
    if "Context constraints:" not in text:
        issues.append(issue(IssueCode.MISSING_CONTEXT_CONSTRAINTS))
    if not text.strip():
        issues.append(issue(IssueCode.CONSTRAINTS_EMPTY))

    return GateResult(
        gate="constraint_consistency",
        passed=not issues,
        issues=issues,
    )


def guardian_gate(plan: Dict[str, object], enforce: bool = False) -> GateResult:
    issues: List[str] = []
    if not isinstance(plan, dict):
        issues.append(issue(IssueCode.GUARDIAN_PLAN_MISSING))
        return GateResult(
            gate="guardian_gate",
            passed=not enforce,
            issues=issues,
            details={"enforce": enforce, "decision": "missing"},
        )
    role_summary = plan.get("role_summary")
    if not isinstance(role_summary, dict):
        issues.append(issue(IssueCode.GUARDIAN_ROLE_SUMMARY_MISSING))
        return GateResult(
            gate="guardian_gate",
            passed=not enforce,
            issues=issues,
            details={"enforce": enforce, "decision": "missing"},
        )
    governance_roles = role_summary.get("governance_roles")
    if not isinstance(governance_roles, list) or not governance_roles:
        issues.append(issue(IssueCode.GUARDIAN_ROLES_MISSING))
    roles_lower = (
        [str(role).lower() for role in governance_roles]
        if isinstance(governance_roles, list)
        else []
    )
    max_level = role_summary.get("max_governance_level")
    guardian_present = "guardian" in roles_lower or isinstance(max_level, int) and max_level >= 3
    if not guardian_present:
        issues.append(issue(IssueCode.GUARDIAN_MISSING))
    decision = "pass" if not issues else ("fail" if enforce else "record_only")
    passed = not issues if enforce else True
    details = {
        "enforce": enforce,
        "decision": decision,
        "guardian_present": guardian_present,
        "max_governance_level": max_level,
        "governance_roles": governance_roles,
    }
    return GateResult(
        gate="guardian_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def p0_gate(text: str) -> GateResult:
    issues: List[str] = []
    if not text or not text.strip():
        issues.append(issue(IssueCode.P0_CONSTRAINTS_EMPTY))
    safety_block = _extract_section(text, "## Safety")
    if not safety_block:
        issues.append(issue(IssueCode.P0_SAFETY_SECTION_MISSING))
    else:
        safety_lower = safety_block.lower()
        markers = ("p0", "non-harm", "non harm", "no harm")
        if not any(marker in safety_lower for marker in markers):
            issues.append(issue(IssueCode.P0_NON_HARM_MISSING))
    decision = "pass" if not issues else "block"
    return GateResult(
        gate="p0_gate",
        passed=not issues,
        issues=issues,
        details={"decision": decision},
    )


def poav_gate(
    text: str,
    threshold: float = 0.7,
    enforce: bool = False,
    source: str = "execution_report",
) -> GateResult:
    issues: List[str] = []
    if not text or not text.strip():
        issues.append(issue(IssueCode.POAV_TEXT_EMPTY))
        decision = "blocked" if enforce else "skipped"
        return GateResult(
            gate="poav_gate",
            passed=not enforce,
            issues=issues,
            details={
                "threshold": round(threshold, 3),
                "enforce": enforce,
                "decision": decision,
                "text_source": source,
                "reason": "empty_text",
            },
        )

    metrics = score_poav(text)
    total = float(metrics.get("total", 0.0))
    meets_threshold = total >= threshold
    if not meets_threshold:
        issues.append(issue(IssueCode.POAV_BELOW_THRESHOLD))
    decision = "pass" if meets_threshold else ("block" if enforce else "record_only")
    passed = meets_threshold if enforce else True
    details = {
        "threshold": round(threshold, 3),
        "enforce": enforce,
        "decision": decision,
        "text_source": source,
        "components": {
            "parsimony": round(metrics.get("parsimony", 0.0), 3),
            "orthogonality": round(metrics.get("orthogonality", 0.0), 3),
            "audibility": round(metrics.get("audibility", 0.0), 3),
            "verifiability": round(metrics.get("verifiability", 0.0), 3),
            "total": round(total, 3),
        },
        "token_count": int(metrics.get("token_count", 0.0)),
        "sentence_count": int(metrics.get("sentence_count", 0.0)),
        "unique_sentences": int(metrics.get("unique_sentences", 0.0)),
        "avg_sentence_tokens": round(metrics.get("avg_sentence_tokens", 0.0), 2),
        "keyword_hits": int(metrics.get("keyword_hits", 0.0)),
        "path_hits": int(metrics.get("path_hits", 0.0)),
    }
    return GateResult(
        gate="poav_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def mercy_gate(
    mercy_objective: Optional[Dict[str, object]],
    threshold: float = 0.1,
    enforce: bool = False,
) -> GateResult:
    issues: List[str] = []
    if not isinstance(mercy_objective, dict):
        issues.append(issue(IssueCode.MERCY_OBJECTIVE_MISSING))
        return GateResult(
            gate="mercy_gate",
            passed=not enforce,
            issues=issues,
            details={
                "threshold": round(threshold, 3),
                "enforce": enforce,
                "decision": "missing",
            },
        )

    score = mercy_objective.get("score")
    if not isinstance(score, (int, float)):
        issues.append(issue(IssueCode.MERCY_SCORE_MISSING))
        return GateResult(
            gate="mercy_gate",
            passed=not enforce,
            issues=issues,
            details={
                "threshold": round(threshold, 3),
                "enforce": enforce,
                "decision": "missing",
            },
        )

    decision = "pass"
    if score < threshold:
        issues.append(issue(IssueCode.MERCY_BELOW_THRESHOLD))
        decision = "quarantine" if enforce else "flag"
    passed = score >= threshold if enforce else True
    details = {
        "threshold": round(threshold, 3),
        "enforce": enforce,
        "decision": decision,
        "score": round(float(score), 4),
        "decision_mode": mercy_objective.get("decision_mode"),
        "objective_version": mercy_objective.get("objective_version"),
        "weights": mercy_objective.get("weights"),
        "signals": mercy_objective.get("signals"),
    }
    return GateResult(
        gate="mercy_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def dcs_gate(
    context: Dict[str, object],
    p0_result: GateResult,
    poav_result: Optional[GateResult],
    mercy_result: Optional[GateResult],
    escalation_result: Optional[GateResult],
    drift_metrics: Dict[str, object],
    tsr_delta_norm: Optional[float],
    poav_threshold: float = 0.7,
    mercy_threshold: float = 0.1,
    drift_threshold: float = 4.0,
    enforce: bool = False,
    policy_path: Optional[str] = None,
) -> GateResult:
    poav_total = None
    if poav_result and isinstance(poav_result.details, dict):
        components = poav_result.details.get("components")
        if isinstance(components, dict):
            value = components.get("total")
            if isinstance(value, (int, float)):
                poav_total = float(value)

    mercy_score = None
    if mercy_result and isinstance(mercy_result.details, dict):
        value = mercy_result.details.get("score")
        if isinstance(value, (int, float)):
            mercy_score = float(value)

    escalation_decision = None
    if escalation_result and isinstance(escalation_result.details, dict):
        escalation_decision = escalation_result.details.get("decision")

    drift_max = None
    if isinstance(drift_metrics, dict):
        drift_max = drift_metrics.get("max_delta_norm")

    decision_mode = decision_mode_from_context(context)
    policy = load_dcs_policy(policy_path)
    dcs_config = policy.get("dcs") if isinstance(policy.get("dcs"), dict) else {}
    if not enforce and isinstance(dcs_config, dict) and dcs_config.get("enforce") is True:
        enforce = True
    payload = build_dcs_result(
        decision_mode=decision_mode,
        p0_passed=p0_result.passed,
        p0_issues=p0_result.issues,
        poav_total=poav_total,
        poav_threshold=poav_threshold,
        mercy_score=mercy_score,
        mercy_threshold=mercy_threshold,
        drift_max=drift_max,
        drift_threshold=drift_threshold,
        tsr_delta_norm=tsr_delta_norm,
        escalation_decision=escalation_decision,
        policy=policy,
    )
    payload["enforce"] = enforce

    issues: List[str] = []
    state = payload.get("state")
    if state == "soft_close":
        issues.append(issue(IssueCode.DCS_SOFT_CLOSE))
    elif state == "closed":
        issues.append(issue(IssueCode.DCS_CLOSED))

    passed = state == "open" if enforce else True
    return GateResult(
        gate="dcs_gate",
        passed=passed,
        issues=issues,
        details=payload,
    )


def seed_schema_gate(seed_path: Optional[str], require: bool = False) -> GateResult:
    issues: List[str] = []
    if not seed_path or not os.path.exists(seed_path):
        issues.append(issue(IssueCode.SEED_MISSING))
        return GateResult(
            gate="seed_schema_gate",
            passed=not require,
            issues=issues,
            details={"seed_path": seed_path, "require": require, "decision": "missing"},
        )
    try:
        payload = _load_json(seed_path)
    except Exception as exc:
        issues.append(issue(IssueCode.SEED_LOAD_FAILED, error=exc.__class__.__name__))
        return GateResult(
            gate="seed_schema_gate",
            passed=False if require else True,
            issues=issues,
            details={"seed_path": seed_path, "require": require, "decision": "load_failed"},
        )
    schema_issues = check_seed_schema(payload)
    issues.extend(schema_issues)
    decision = "pass" if not schema_issues else ("fail" if require else "record_only")
    passed = not schema_issues if require else True
    details = {
        "seed_path": seed_path,
        "require": require,
        "decision": decision,
        "issue_count": len(schema_issues),
    }
    return GateResult(
        gate="seed_schema_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def tech_trace_gate(
    normalize_path: Optional[str],
    require: bool = False,
    strict: bool = False,
) -> GateResult:
    issues: List[str] = []
    if not normalize_path or not os.path.exists(normalize_path):
        issues.append(issue(IssueCode.TECH_TRACE_MISSING))
        return GateResult(
            gate="tech_trace_gate",
            passed=not require,
            issues=issues,
            details={"normalize_path": normalize_path, "require": require, "decision": "missing"},
        )
    try:
        payload = _load_json(normalize_path)
    except Exception as exc:
        issues.append(issue(IssueCode.TECH_TRACE_LOAD_FAILED, error=exc.__class__.__name__))
        return GateResult(
            gate="tech_trace_gate",
            passed=not require,
            issues=issues,
            details={
                "normalize_path": normalize_path,
                "require": require,
                "decision": "load_failed",
            },
        )
    schema_issues = validate_normalize_payload(payload, strict=strict)
    issues.extend(schema_issues)
    decision = "pass" if not schema_issues else ("fail" if require else "record_only")
    passed = not schema_issues if require else True
    details = {
        "normalize_path": normalize_path,
        "require": require,
        "strict": strict,
        "decision": decision,
        "issue_count": len(schema_issues),
    }
    return GateResult(
        gate="tech_trace_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def intent_achievement_gate(intent_path: Optional[str], require: bool = False) -> GateResult:
    issues: List[str] = []
    if not intent_path or not os.path.exists(intent_path):
        issues.append(issue(IssueCode.INTENT_VERIFICATION_MISSING))
        return GateResult(
            gate="intent_achievement_gate",
            passed=not require,
            issues=issues,
            details={"intent_path": intent_path, "require": require, "decision": "missing"},
        )

    try:
        payload = _load_json(intent_path)
    except Exception as exc:
        issues.append(
            issue(IssueCode.INTENT_VERIFICATION_LOAD_FAILED, error=exc.__class__.__name__)
        )
        return GateResult(
            gate="intent_achievement_gate",
            passed=not require,
            issues=issues,
            details={"intent_path": intent_path, "require": require, "decision": "load_failed"},
        )

    audit = payload.get("audit") if isinstance(payload, dict) else None
    audit = audit if isinstance(audit, dict) else {}
    status = audit.get("status") or payload.get("status") or "unknown"
    confidence = audit.get("confidence")
    reason = audit.get("reason")

    decision = "record_only"
    passed = True
    if status == "achieved":
        decision = "pass"
        passed = True
    elif status == "failed":
        issues.append(issue(IssueCode.INTENT_VERIFICATION_FAILED))
        decision = "fail" if require else "record_only"
        passed = not require
    elif status == "inconclusive":
        issues.append(issue(IssueCode.INTENT_VERIFICATION_INCONCLUSIVE))
        decision = "fail" if require else "record_only"
        passed = not require
    else:
        issues.append(issue(IssueCode.INTENT_VERIFICATION_INCONCLUSIVE))
        decision = "fail" if require else "record_only"
        passed = not require

    details = {
        "intent_path": intent_path,
        "require": require,
        "decision": decision,
        "status": status,
        "confidence": confidence,
        "reason": reason,
    }
    return GateResult(
        gate="intent_achievement_gate",
        passed=passed,
        issues=issues,
        details=details,
    )


def escalation_gate(
    context: Dict[str, object],
    poav_result: Optional[GateResult],
    drift_metrics: Dict[str, object],
    poav_threshold: float = 0.7,
    drift_threshold: float = 4.0,
    ledger_path: Optional[str] = None,
    run_id: Optional[str] = None,
) -> GateResult:
    decision_mode = decision_mode_from_context(context)
    poav_total = None
    if poav_result and isinstance(poav_result.details, dict):
        components = poav_result.details.get("components")
        if isinstance(components, dict):
            poav_total = components.get("total")
    drift_max = None
    if isinstance(drift_metrics, dict):
        drift_max = drift_metrics.get("max_delta_norm")
    escalation = decide_escalation(
        poav_total,
        poav_threshold,
        drift_max,
        drift_threshold,
        decision_mode,
    )
    decision = escalation.get("decision", "none")
    reasons = escalation.get("reasons", [])
    issues: List[str] = []
    event_id = None
    if decision != "none":
        issues.append(issue(IssueCode.ESCALATION_DECISION, decision=decision))
        if isinstance(reasons, list):
            issues.extend(reasons)
        event_id = record_escalation(
            decision,
            reasons if isinstance(reasons, list) else [],
            {
                "poav_total": poav_total,
                "poav_threshold": poav_threshold,
                "drift_max": drift_max,
                "drift_threshold": drift_threshold,
                "drift_avg": (
                    drift_metrics.get("avg_delta_norm") if isinstance(drift_metrics, dict) else None
                ),
                "drift_count": (
                    drift_metrics.get("count") if isinstance(drift_metrics, dict) else None
                ),
            },
            ledger_path,
            decision_mode,
            run_id,
        )
    details = {
        "decision": decision,
        "decision_mode": decision_mode,
        "reasons": reasons,
        "poav_total": poav_total,
        "poav_threshold": poav_threshold,
        "drift_max": drift_max,
        "drift_threshold": drift_threshold,
        "drift_avg": (
            drift_metrics.get("avg_delta_norm") if isinstance(drift_metrics, dict) else None
        ),
        "drift_count": drift_metrics.get("count") if isinstance(drift_metrics, dict) else None,
        "drift_available": (
            drift_metrics.get("available") if isinstance(drift_metrics, dict) else False
        ),
        "event_id": event_id,
        "ledger_path": ledger_path,
    }
    return GateResult(
        gate="escalation_gate",
        passed=decision == "none",
        issues=issues,
        details=details,
    )


def build_test_gate(workspace_root: str) -> GateResult:
    del workspace_root  # Preserved for backwards-compatible signature.
    issues: List[str] = []
    try:
        results = run_acceptance()
    except Exception as exc:  # pragma: no cover - defensive path for gate failures
        issues.append(issue(IssueCode.YSTM_ACCEPTANCE_FAILED))
        details = {
            "command": "in_process:tonesoul.ystm.acceptance.run_acceptance",
            "returncode": 1,
            "stdout_tail": f"{exc.__class__.__name__}: {exc}",
        }
        return GateResult(
            gate="build_test_gate",
            passed=False,
            issues=issues,
            details=details,
        )

    failed = [item for item in results if item.get("status") != "PASS"]
    if failed:
        issues.append(issue(IssueCode.YSTM_ACCEPTANCE_FAILED))

    output_lines = []
    for item in results[-5:]:
        line = f"{item.get('test', 'unknown')}: {item.get('status', 'UNKNOWN')}"
        if item.get("status") != "PASS" and item.get("error"):
            line = f"{line} - {item.get('error')}"
        output_lines.append(line)
    details = {
        "command": "in_process:tonesoul.ystm.acceptance.run_acceptance",
        "returncode": 0 if not failed else 1,
        "stdout_tail": "\n".join(output_lines),
    }
    return GateResult(
        gate="build_test_gate",
        passed=not issues,
        issues=issues,
        details=details,
    )


def evidence_completeness(
    evidence_text: str,
    context_path: str,
    execution_report_path: Optional[str],
    required_files: Dict[str, str],
    require_listed: bool = False,
) -> GateResult:
    issues: List[str] = []
    if not evidence_text.strip():
        issues.append(issue(IssueCode.EVIDENCE_EMPTY))
    if context_path and context_path not in evidence_text:
        issues.append(issue(IssueCode.CONTEXT_NOT_LISTED))
    if execution_report_path and execution_report_path not in evidence_text:
        issues.append(issue(IssueCode.EXECUTION_REPORT_NOT_LISTED))
    missing_files = []
    for label, path in required_files.items():
        if path and not os.path.exists(path):
            missing_files.append(label)
    if missing_files:
        issues.append(issue(IssueCode.MISSING_FILES, labels=",".join(missing_files)))
    missing_refs = []
    if require_listed and evidence_text.strip():
        for label, path in required_files.items():
            if path and path not in evidence_text:
                missing_refs.append(label)
    if missing_refs:
        issues.append(issue(IssueCode.EVIDENCE_MISSING_REFS, labels=",".join(missing_refs)))

    return GateResult(
        gate="evidence_completeness",
        passed=not issues,
        issues=issues,
        details={"missing_files": missing_files, "missing_refs": missing_refs},
    )


def build_gate_report(results: List[GateResult]) -> Dict[str, object]:
    return {
        "generated_at": utc_now(),
        "overall": "PASS" if all(result.passed for result in results) else "FAIL",
        "results": [
            {
                "gate": result.gate,
                "passed": result.passed,
                "issues": result.issues,
                "details": result.details or {},
            }
            for result in results
        ],
    }


def update_execution_report(report_path: str, gate_report: Dict[str, object]) -> None:
    header = "## Gate Results"
    report_text = ""
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as handle:
            report_text = handle.read()
    if header in report_text:
        report_text = report_text.split(header)[0].rstrip() + "\n\n"

    lines = [report_text, header, ""]
    lines.append(f"- Generated at: {gate_report['generated_at']}")
    lines.append(f"- Overall: {gate_report['overall']}")
    lines.append("")
    for result in gate_report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        issue_text = ", ".join(result["issues"]) if result["issues"] else "-"
        lines.append(f"- {result['gate']}: {status} | {issue_text}")
    lines.append("")
    p0_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "p0_gate"),
        None,
    )
    if p0_result:
        details = p0_result.get("details", {}) if isinstance(p0_result, dict) else {}
        issue_text = ", ".join(p0_result.get("issues", [])) if p0_result.get("issues") else "-"
        lines.append("## P0 Non-Harm Gate")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Passed: {p0_result.get('passed')}"
        )
        lines.append(f"- Issues: {issue_text}")
        lines.append("")
    guardian_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "guardian_gate"),
        None,
    )
    if guardian_result:
        details = guardian_result.get("details", {}) if isinstance(guardian_result, dict) else {}
        issue_text = (
            ", ".join(guardian_result.get("issues", [])) if guardian_result.get("issues") else "-"
        )
        lines.append("## Guardian Gate")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Passed: {guardian_result.get('passed')}"
        )
        lines.append(f"- Guardian present: {details.get('guardian_present', 'n/a')}")
        lines.append(f"- Issues: {issue_text}")
        lines.append("")
    poav_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "poav_gate"),
        None,
    )
    if poav_result:
        details = poav_result.get("details", {}) if isinstance(poav_result, dict) else {}
        components = details.get("components", {}) if isinstance(details, dict) else {}
        lines.append("## POAV Metrics")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Passed: {poav_result.get('passed')}"
        )
        lines.append(
            f"- Threshold: {details.get('threshold', 'n/a')} | Enforced: {details.get('enforce', 'n/a')}"
        )
        lines.append(
            f"- Score: {components.get('total', 'n/a')} (P={components.get('parsimony', 'n/a')}, "
            f"O={components.get('orthogonality', 'n/a')}, "
            f"A={components.get('audibility', 'n/a')}, "
            f"V={components.get('verifiability', 'n/a')})"
        )
        lines.append(
            f"- Tokens: {details.get('token_count', 'n/a')} | Sentences: {details.get('sentence_count', 'n/a')} "
            f"| Avg sentence tokens: {details.get('avg_sentence_tokens', 'n/a')}"
        )
        lines.append(
            f"- Evidence signals: keywords={details.get('keyword_hits', 'n/a')} | "
            f"paths={details.get('path_hits', 'n/a')} | Source: {details.get('text_source', 'n/a')}"
        )
        lines.append("")
    escalation_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "escalation_gate"),
        None,
    )
    if escalation_result:
        details = (
            escalation_result.get("details", {}) if isinstance(escalation_result, dict) else {}
        )
        lines.append("## Escalation")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Mode: {details.get('decision_mode', 'n/a')}"
        )
        lines.append(
            f"- Reasons: {details.get('reasons', 'n/a')} | Event ID: {details.get('event_id', 'n/a')}"
        )
        lines.append(
            f"- POAV: {details.get('poav_total', 'n/a')} (threshold={details.get('poav_threshold', 'n/a')})"
        )
        lines.append(
            f"- Drift max: {details.get('drift_max', 'n/a')} "
            f"(threshold={details.get('drift_threshold', 'n/a')})"
        )
        lines.append("")
    mercy_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "mercy_gate"),
        None,
    )
    if mercy_result:
        details = mercy_result.get("details", {}) if isinstance(mercy_result, dict) else {}
        lines.append("## Mercy Objective Gate")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Score: {details.get('score', 'n/a')}"
        )
        lines.append(
            f"- Threshold: {details.get('threshold', 'n/a')} | Enforced: {details.get('enforce', 'n/a')}"
        )
        lines.append(
            f"- Decision mode: {details.get('decision_mode', 'n/a')} | Version: {details.get('objective_version', 'n/a')}"
        )
        lines.append("")
    dcs_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "dcs_gate"),
        None,
    )
    if dcs_result:
        details = dcs_result.get("details", {}) if isinstance(dcs_result, dict) else {}
        lines.append("## DCS (Dynamic Closure System)")
        lines.append(
            f"- State: {details.get('state', 'n/a')} | Decision: {details.get('decision', 'n/a')}"
        )
        lines.append(
            f"- Decision mode: {details.get('decision_mode', 'n/a')} | Enforced: {details.get('enforce', 'n/a')}"
        )
        lines.append(f"- Reasons: {details.get('reasons', 'n/a')}")
        lines.append("")
    seed_result = next(
        (result for result in gate_report["results"] if result.get("gate") == "seed_schema_gate"),
        None,
    )
    if seed_result:
        details = seed_result.get("details", {}) if isinstance(seed_result, dict) else {}
        lines.append("## Seed Schema Gate")
        lines.append(
            f"- Decision: {details.get('decision', 'n/a')} | Require: {details.get('require', 'n/a')}"
        )
        lines.append(
            f"- Issue count: {details.get('issue_count', 'n/a')} | Seed: {details.get('seed_path', 'n/a')}"
        )
        lines.append("")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
