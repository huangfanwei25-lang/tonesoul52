import argparse
import json
import os
from typing import Dict, List, Optional

from .ystm.schema import stable_hash, utc_now


def _load_frame_role_meta(frame_plan_path: Optional[str]) -> Dict[str, object]:
    if not frame_plan_path or not os.path.exists(frame_plan_path):
        return {}
    with open(frame_plan_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {}
    meta: Dict[str, object] = {}
    role_catalog = payload.get("role_catalog")
    if role_catalog:
        meta["role_catalog"] = role_catalog
    role_summary = payload.get("role_summary")
    if role_summary:
        meta["role_summary"] = role_summary
    return meta


def _load_poav_result(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return None
    if payload.get("gate") == "poav_gate":
        return payload
    results = payload.get("results")
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and item.get("gate") == "poav_gate":
                return item
    if isinstance(payload.get("poav_result"), dict):
        return payload["poav_result"]
    return payload


def _load_escalation_result(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return None
    if payload.get("gate") == "escalation_gate":
        return payload
    results = payload.get("results")
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and item.get("gate") == "escalation_gate":
                return item
    if isinstance(payload.get("escalation_result"), dict):
        return payload["escalation_result"]
    return payload


def _load_mercy_result(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return None
    if payload.get("gate") == "mercy_gate":
        return payload
    results = payload.get("results")
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and item.get("gate") == "mercy_gate":
                return item
    if isinstance(payload.get("mercy_result"), dict):
        return payload["mercy_result"]
    return payload


def _load_json(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _truncate(text: str, limit: int = 120) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: max(0, limit - 3)] + "..."


def _count_entries(items: object, key: Optional[str] = None) -> int:
    if not isinstance(items, list):
        return 0
    count = 0
    for item in items:
        if isinstance(item, dict):
            if key is None or item.get(key):
                count += 1
        elif isinstance(item, str):
            if item.strip():
                count += 1
    return count


def _claim_preview(claims: object) -> Dict[str, object]:
    if not isinstance(claims, list):
        return {"count": 0, "preview": []}
    count = 0
    preview: List[str] = []
    for item in claims:
        text = None
        if isinstance(item, dict):
            text = item.get("text") or item.get("claim") or item.get("statement")
        elif isinstance(item, str):
            text = item
        if text:
            count += 1
            if len(preview) < 3:
                preview.append(_truncate(text, 80))
    return {"count": count, "preview": preview}


def _tech_trace_digest(normalize_path: Optional[str]) -> Optional[Dict[str, object]]:
    payload = _load_json(normalize_path)
    if not payload:
        return None
    claims_info = _claim_preview(payload.get("claims"))
    return {
        "normalize_path": normalize_path,
        "summary": _truncate(payload.get("summary", "")) if payload.get("summary") else None,
        "claim_count": claims_info.get("count", 0),
        "claims_preview": claims_info.get("preview", []),
        "link_count": _count_entries(payload.get("links"), key="uri"),
        "attribution_count": _count_entries(payload.get("attributions"), key="source_ref"),
    }


def _intent_verification_digest(intent_path: Optional[str]) -> Optional[Dict[str, object]]:
    payload = _load_json(intent_path)
    if not payload:
        return None
    audit = payload.get("audit") if isinstance(payload.get("audit"), dict) else {}
    intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    return {
        "status": audit.get("status"),
        "confidence": audit.get("confidence"),
        "reason": audit.get("reason"),
        "surface": intent.get("surface"),
        "deep": intent.get("deep"),
        "evidence_path": source.get("evidence_path"),
    }


def build_audit_request(
    context_path: str,
    frame_plan_path: Optional[str],
    constraints_path: Optional[str],
    execution_report_path: Optional[str],
    evidence_summary_path: Optional[str],
    gate_report_path: Optional[str],
    error_ledger_path: Optional[str],
    action_set_path: Optional[str],
    mercy_objective_path: Optional[str],
    council_summary_path: Optional[str],
    tsr_metrics_path: Optional[str],
    dcs_result_path: Optional[str],
    ystm_nodes_path: Optional[str],
    ystm_audit_path: Optional[str],
    ystm_diff_path: Optional[str] = None,
    ystm_terrain_path: Optional[str] = None,
    ystm_terrain_json_path: Optional[str] = None,
    ystm_terrain_svg_path: Optional[str] = None,
    ystm_terrain_png_path: Optional[str] = None,
    ystm_terrain_p2_path: Optional[str] = None,
    ystm_terrain_p2_json_path: Optional[str] = None,
    ystm_terrain_p2_svg_path: Optional[str] = None,
    ystm_terrain_p2_png_path: Optional[str] = None,
    tech_trace_capture_path: Optional[str] = None,
    tech_trace_normalize_path: Optional[str] = None,
    intent_verification_path: Optional[str] = None,
    skills_applied_path: Optional[str] = None,
    reflection_path: Optional[str] = None,
    poav_result: Optional[Dict[str, object]] = None,
    escalation_result: Optional[Dict[str, object]] = None,
    mercy_result: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    payload = {
        "generated_at": utc_now(),
        "request_id": stable_hash(context_path + utc_now()),
        "scope": "External audit request (interface only).",
        "inputs": {
            "context": context_path,
            "frame_plan": frame_plan_path,
            "constraints": constraints_path,
            "execution_report": execution_report_path,
            "evidence_summary": evidence_summary_path,
            "gate_report": gate_report_path,
            "error_ledger": error_ledger_path,
            "action_set": action_set_path,
            "mercy_objective": mercy_objective_path,
            "council_summary": council_summary_path,
            "tsr_metrics": tsr_metrics_path,
            "dcs_result": dcs_result_path,
            "ystm_nodes": ystm_nodes_path,
            "ystm_audit_log": ystm_audit_path,
            "ystm_diff": ystm_diff_path,
            "ystm_terrain": ystm_terrain_path,
            "ystm_terrain_json": ystm_terrain_json_path,
            "ystm_terrain_svg": ystm_terrain_svg_path,
            "ystm_terrain_png": ystm_terrain_png_path,
            "ystm_terrain_p2": ystm_terrain_p2_path,
            "ystm_terrain_p2_json": ystm_terrain_p2_json_path,
            "ystm_terrain_p2_svg": ystm_terrain_p2_svg_path,
            "ystm_terrain_p2_png": ystm_terrain_p2_png_path,
            "tech_trace_capture": tech_trace_capture_path,
            "tech_trace_normalize": tech_trace_normalize_path,
            "intent_verification": intent_verification_path,
            "skills_applied": skills_applied_path,
            "reflection": reflection_path,
        },
        "principles": [
            "System records without judging.",
            "Audit authority is external.",
        ],
        "notes": "This request is an interface placeholder; no decision is made here.",
    }
    role_meta = _load_frame_role_meta(frame_plan_path)
    if role_meta:
        payload["responsibility_roles"] = role_meta
    if poav_result:
        payload["poav_result"] = poav_result
    if escalation_result:
        payload["escalation_result"] = escalation_result
    if mercy_result:
        payload["mercy_result"] = mercy_result
    tech_trace_digest = _tech_trace_digest(tech_trace_normalize_path)
    if tech_trace_digest:
        payload["tech_trace_digest"] = tech_trace_digest
    intent_digest = _intent_verification_digest(intent_verification_path)
    if intent_digest:
        payload["intent_verification_digest"] = intent_digest
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate audit request interface for YSS M5.")
    parser.add_argument("--context", required=True, help="Path to context.yaml.")
    parser.add_argument("--frame-plan", help="Optional path to frame_plan.json.")
    parser.add_argument("--constraints", help="Optional path to constraints.md.")
    parser.add_argument("--execution-report", help="Optional path to execution_report.md.")
    parser.add_argument("--evidence-summary", help="Optional path to evidence/summary.md.")
    parser.add_argument("--gate-report", help="Optional path to gate_report.json.")
    parser.add_argument("--error-ledger", help="Optional path to error_ledger.jsonl.")
    parser.add_argument("--action-set", help="Optional path to action_set.json.")
    parser.add_argument("--mercy-objective", help="Optional path to mercy_objective.json.")
    parser.add_argument("--council-summary", help="Optional path to council_summary.json.")
    parser.add_argument("--tsr-metrics", help="Optional path to tsr_metrics.json.")
    parser.add_argument("--dcs-result", help="Optional path to dcs_result.json.")
    parser.add_argument("--ystm-nodes", help="Optional path to nodes.json.")
    parser.add_argument("--ystm-audit", help="Optional path to audit_log.json.")
    parser.add_argument("--ystm-diff", help="Optional path to semantic_diff.json.")
    parser.add_argument("--ystm-terrain", help="Optional path to terrain.html.")
    parser.add_argument("--ystm-terrain-json", help="Optional path to terrain.json.")
    parser.add_argument("--ystm-terrain-svg", help="Optional path to terrain.svg.")
    parser.add_argument("--ystm-terrain-png", help="Optional path to terrain.png.")
    parser.add_argument("--ystm-terrain-p2", help="Optional path to terrain_p2.html.")
    parser.add_argument("--ystm-terrain-p2-json", help="Optional path to terrain_p2.json.")
    parser.add_argument("--ystm-terrain-p2-svg", help="Optional path to terrain_p2.svg.")
    parser.add_argument("--ystm-terrain-p2-png", help="Optional path to terrain_p2.png.")
    parser.add_argument("--tech-trace-capture", help="Optional path to tech_trace capture JSON.")
    parser.add_argument(
        "--tech-trace-normalize", help="Optional path to tech_trace normalized JSON."
    )
    parser.add_argument("--intent-verification", help="Optional path to intent_verification.json.")
    parser.add_argument("--skills-applied", help="Optional path to skills_applied.json.")
    parser.add_argument("--reflection", help="Optional path to reflection.json.")
    parser.add_argument(
        "--poav-result",
        help="Optional path to poav_result or gate_report.json (extracts poav_gate).",
    )
    parser.add_argument(
        "--escalation-result",
        help="Optional path to escalation_result or gate_report.json (extracts escalation_gate).",
    )
    parser.add_argument(
        "--mercy-result",
        help="Optional path to mercy_result or gate_report.json (extracts mercy_gate).",
    )
    parser.add_argument("--output", help="Output path for audit_request.json.")
    return parser


def _resolve_output(path: Optional[str], context_path: str) -> str:
    if path:
        return os.path.abspath(path)
    context_dir = os.path.dirname(os.path.abspath(context_path))
    return os.path.join(context_dir, "audit_request.json")


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    payload = build_audit_request(
        context_path=args.context,
        frame_plan_path=args.frame_plan,
        constraints_path=args.constraints,
        execution_report_path=args.execution_report,
        evidence_summary_path=args.evidence_summary,
        gate_report_path=args.gate_report,
        error_ledger_path=args.error_ledger,
        action_set_path=args.action_set,
        mercy_objective_path=args.mercy_objective,
        council_summary_path=args.council_summary,
        tsr_metrics_path=args.tsr_metrics,
        dcs_result_path=args.dcs_result,
        ystm_nodes_path=args.ystm_nodes,
        ystm_audit_path=args.ystm_audit,
        ystm_diff_path=args.ystm_diff,
        ystm_terrain_path=args.ystm_terrain,
        ystm_terrain_json_path=args.ystm_terrain_json,
        ystm_terrain_svg_path=args.ystm_terrain_svg,
        ystm_terrain_png_path=args.ystm_terrain_png,
        ystm_terrain_p2_path=args.ystm_terrain_p2,
        ystm_terrain_p2_json_path=args.ystm_terrain_p2_json,
        ystm_terrain_p2_svg_path=args.ystm_terrain_p2_svg,
        ystm_terrain_p2_png_path=args.ystm_terrain_p2_png,
        tech_trace_capture_path=args.tech_trace_capture,
        tech_trace_normalize_path=args.tech_trace_normalize,
        intent_verification_path=args.intent_verification,
        skills_applied_path=args.skills_applied,
        reflection_path=args.reflection,
        poav_result=_load_poav_result(args.poav_result),
        escalation_result=_load_escalation_result(args.escalation_result),
        mercy_result=_load_mercy_result(args.mercy_result),
    )
    output_path = _resolve_output(args.output, args.context)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return {"audit_request": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"audit_request.json: {paths['audit_request']}")
