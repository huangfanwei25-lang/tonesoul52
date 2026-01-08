import argparse
import json
import os
from typing import Dict, Optional

from .escalation import load_drift_metrics
from .yss_gates import (
    build_gate_report,
    build_test_gate,
    context_lint,
    constraint_consistency,
    dcs_gate,
    escalation_gate,
    evidence_completeness,
    guardian_gate,
    intent_achievement_gate,
    mercy_gate,
    p0_gate,
    poav_gate,
    role_alignment,
    router_replay,
    seed_schema_gate,
    tech_trace_gate,
    update_execution_report,
)
from .yss_gates import _load_json as load_json
from .yss_gates import _load_yaml as load_yaml


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run YSS gate validators.")
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Execution run directory (5.2/run/execution/<run_id>).",
    )
    parser.add_argument("--context", help="Path to context.yaml.")
    parser.add_argument("--frame-plan", help="Path to frame_plan.json.")
    parser.add_argument("--constraints", help="Path to constraints.md.")
    parser.add_argument("--execution-report", help="Path to execution_report.md.")
    parser.add_argument("--action-set", help="Path to action_set.json.")
    parser.add_argument("--mercy-objective", help="Path to mercy_objective.json.")
    parser.add_argument("--council-summary", help="Path to council_summary.json.")
    parser.add_argument("--tsr-metrics", help="Path to tsr_metrics.json.")
    parser.add_argument("--seed", help="Path to memory seed JSON.")
    parser.add_argument("--registry", help="Path to frame_registry.json.")
    parser.add_argument("--evidence-summary", help="Path to evidence/summary.md.")
    parser.add_argument("--ystm-nodes", help="Path to YSTM nodes.json.")
    parser.add_argument("--ystm-audit", help="Path to YSTM audit_log.json.")
    parser.add_argument("--ystm-diff", help="Path to YSTM semantic_diff.json.")
    parser.add_argument("--ystm-terrain", help="Path to YSTM terrain.html.")
    parser.add_argument("--ystm-terrain-json", help="Path to YSTM terrain.json.")
    parser.add_argument("--ystm-terrain-svg", help="Path to YSTM terrain.svg.")
    parser.add_argument("--ystm-terrain-png", help="Path to YSTM terrain.png.")
    parser.add_argument("--ystm-terrain-p2", help="Path to YSTM terrain_p2.html.")
    parser.add_argument("--ystm-terrain-p2-json", help="Path to YSTM terrain_p2.json.")
    parser.add_argument("--ystm-terrain-p2-svg", help="Path to YSTM terrain_p2.svg.")
    parser.add_argument("--ystm-terrain-p2-png", help="Path to YSTM terrain_p2.png.")
    parser.add_argument("--tech-trace-capture", help="Path to tech_trace capture JSON.")
    parser.add_argument("--tech-trace-normalize", help="Path to tech_trace normalized JSON.")
    parser.add_argument("--skills-applied", help="Path to skills_applied.json.")
    parser.add_argument("--intent-verification", help="Path to intent_verification.json.")
    parser.add_argument(
        "--poav-threshold",
        type=float,
        default=0.7,
        help="POAV threshold for gate decision.",
    )
    parser.add_argument(
        "--mercy-threshold",
        type=float,
        default=0.1,
        help="Mercy objective threshold for gate decision.",
    )
    parser.add_argument(
        "--drift-threshold",
        type=float,
        default=4.0,
        help="Drift threshold for escalation decisions.",
    )
    parser.add_argument(
        "--enforce-poav",
        action="store_true",
        help="Fail the gate if POAV falls below the threshold.",
    )
    parser.add_argument(
        "--enforce-mercy",
        action="store_true",
        help="Fail the gate if Mercy objective falls below the threshold.",
    )
    parser.add_argument(
        "--enforce-guardian",
        action="store_true",
        help="Fail the gate if guardian roles are missing.",
    )
    parser.add_argument(
        "--require-seed",
        action="store_true",
        help="Fail the gate if seed schema is missing or invalid.",
    )
    parser.add_argument(
        "--require-tech-trace",
        action="store_true",
        help="Fail the gate if tech-trace normalize is missing or invalid.",
    )
    parser.add_argument(
        "--require-intent",
        action="store_true",
        help="Fail the gate if intent verification is missing or inconclusive.",
    )
    parser.add_argument(
        "--tech-trace-strict",
        action="store_true",
        help="Require attributions to reference claim ids when validating tech-trace.",
    )
    parser.add_argument("--error-ledger", help="Optional error_ledger.jsonl path.")
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Require evidence summary to list all required files.",
    )
    parser.add_argument("--output", help="Path for gate_report.json.")
    parser.add_argument(
        "--no-update-report",
        action="store_true",
        help="Do not update execution_report.md.",
    )
    return parser


def _resolve_paths(args: argparse.Namespace) -> Dict[str, Optional[str]]:
    run_dir = args.run_dir
    if run_dir:
        run_dir = os.path.abspath(run_dir)
    resolved = {
        "run_dir": run_dir,
        "context": args.context,
        "frame_plan": args.frame_plan,
        "constraints": args.constraints,
        "execution_report": args.execution_report,
        "action_set": args.action_set,
        "mercy_objective": args.mercy_objective,
        "council_summary": args.council_summary,
        "tsr_metrics": args.tsr_metrics,
        "seed": args.seed,
        "registry": args.registry,
        "evidence_summary": args.evidence_summary,
        "ystm_nodes": args.ystm_nodes,
        "ystm_audit": args.ystm_audit,
        "ystm_diff": args.ystm_diff,
        "ystm_terrain": args.ystm_terrain,
        "ystm_terrain_json": args.ystm_terrain_json,
        "ystm_terrain_svg": args.ystm_terrain_svg,
        "ystm_terrain_png": args.ystm_terrain_png,
        "ystm_terrain_p2": args.ystm_terrain_p2,
        "ystm_terrain_p2_json": args.ystm_terrain_p2_json,
        "ystm_terrain_p2_svg": args.ystm_terrain_p2_svg,
        "ystm_terrain_p2_png": args.ystm_terrain_p2_png,
        "tech_trace_capture": args.tech_trace_capture,
        "tech_trace_normalize": args.tech_trace_normalize,
        "skills_applied": args.skills_applied,
        "intent_verification": args.intent_verification,
        "output": args.output,
        "error_ledger": args.error_ledger,
    }
    if not run_dir:
        return resolved

    defaults = {
        "context": os.path.join(run_dir, "context.yaml"),
        "frame_plan": os.path.join(run_dir, "frame_plan.json"),
        "constraints": os.path.join(run_dir, "constraints.md"),
        "execution_report": os.path.join(run_dir, "execution_report.md"),
        "action_set": os.path.join(run_dir, "action_set.json"),
        "mercy_objective": os.path.join(run_dir, "mercy_objective.json"),
        "council_summary": os.path.join(run_dir, "council_summary.json"),
        "tsr_metrics": os.path.join(run_dir, "tsr_metrics.json"),
        "output": os.path.join(run_dir, "gate_report.json"),
        "skills_applied": os.path.join(run_dir, "skills_applied.json"),
        "error_ledger": os.path.join(run_dir, "error_ledger.jsonl"),
        "intent_verification": os.path.join(run_dir, "intent_verification.json"),
    }
    for key, value in defaults.items():
        if not resolved.get(key):
            resolved[key] = value

    workspace_root = os.path.abspath(os.path.join(run_dir, "..", "..", ".."))
    workspace_defaults = {
        "registry": os.path.join(workspace_root, "spec", "frames", "frame_registry.json"),
        "evidence_summary": os.path.join(workspace_root, "evidence", "summary.md"),
        "ystm_nodes": os.path.join(workspace_root, "reports", "ystm_demo", "nodes.json"),
        "ystm_audit": os.path.join(workspace_root, "reports", "ystm_demo", "audit_log.json"),
        "ystm_diff": os.path.join(workspace_root, "reports", "ystm_demo", "semantic_diff.json"),
        "ystm_terrain": os.path.join(workspace_root, "reports", "ystm_demo", "terrain.html"),
        "ystm_terrain_json": os.path.join(workspace_root, "reports", "ystm_demo", "terrain.json"),
        "ystm_terrain_svg": os.path.join(workspace_root, "reports", "ystm_demo", "terrain.svg"),
        "ystm_terrain_png": os.path.join(workspace_root, "reports", "ystm_demo", "terrain.png"),
        "ystm_terrain_p2": os.path.join(workspace_root, "reports", "ystm_demo", "terrain_p2.html"),
        "ystm_terrain_p2_json": os.path.join(workspace_root, "reports", "ystm_demo", "terrain_p2.json"),
        "ystm_terrain_p2_svg": os.path.join(workspace_root, "reports", "ystm_demo", "terrain_p2.svg"),
        "ystm_terrain_p2_png": os.path.join(workspace_root, "reports", "ystm_demo", "terrain_p2.png"),
    }
    for key, value in workspace_defaults.items():
        if not resolved.get(key):
            resolved[key] = value
    resolved.setdefault("workspace_root", workspace_root)
    if run_dir and not resolved.get("seed"):
        run_id = os.path.basename(run_dir)
        resolved["seed"] = os.path.join(workspace_root, "memory", "seeds", f"{run_id}.json")

    _apply_audit_inputs(resolved)

    optional_keys = (
        "action_set",
        "mercy_objective",
        "council_summary",
        "tsr_metrics",
        "seed",
        "ystm_terrain",
        "ystm_terrain_json",
        "ystm_terrain_svg",
        "ystm_terrain_png",
        "ystm_terrain_p2",
        "ystm_terrain_p2_json",
        "ystm_terrain_p2_svg",
        "ystm_terrain_p2_png",
        "ystm_diff",
        "tech_trace_capture",
        "tech_trace_normalize",
        "skills_applied",
        "intent_verification",
    )
    for key in optional_keys:
        provided = getattr(args, key, None)
        path = resolved.get(key)
        if provided is None and path and not os.path.exists(path):
            resolved[key] = None
    return resolved


def _apply_audit_inputs(resolved: Dict[str, Optional[str]]) -> None:
    run_dir = resolved.get("run_dir")
    if not run_dir:
        return
    audit_path = os.path.join(run_dir, "audit_request.json")
    if not os.path.exists(audit_path):
        return
    try:
        payload = load_json(audit_path)
    except Exception:
        return
    inputs = payload.get("inputs") if isinstance(payload, dict) else None
    if not isinstance(inputs, dict):
        return
    for key in ("ystm_diff", "tech_trace_capture", "tech_trace_normalize", "intent_verification"):
        if resolved.get(key):
            continue
        value = inputs.get(key)
        if isinstance(value, str):
            resolved[key] = value


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    paths = _resolve_paths(args)

    if not paths.get("context") or not os.path.exists(paths["context"]):
        parser.error("context.yaml is required.")
    if not paths.get("frame_plan") or not os.path.exists(paths["frame_plan"]):
        parser.error("frame_plan.json is required.")
    if not paths.get("constraints") or not os.path.exists(paths["constraints"]):
        parser.error("constraints.md is required.")
    if not paths.get("registry") or not os.path.exists(paths["registry"]):
        parser.error("frame_registry.json is required.")

    context = load_yaml(paths["context"])
    frame_plan = load_json(paths["frame_plan"])
    with open(paths["constraints"], "r", encoding="utf-8") as handle:
        constraints_text = handle.read()
    with open(paths["registry"], "r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, list):
        raise ValueError("frame_registry.json must be a list.")

    poav_text = constraints_text
    poav_source = "constraints"
    if paths.get("execution_report") and os.path.exists(paths["execution_report"]):
        with open(paths["execution_report"], "r", encoding="utf-8") as handle:
            poav_text = handle.read()
        poav_source = "execution_report"

    mercy_objective = None
    if paths.get("mercy_objective") and os.path.exists(paths["mercy_objective"]):
        mercy_objective = load_json(paths["mercy_objective"])

    poav_result = poav_gate(
        poav_text,
        threshold=args.poav_threshold,
        enforce=args.enforce_poav,
        source=poav_source,
    )
    mercy_result = mercy_gate(
        mercy_objective,
        threshold=args.mercy_threshold,
        enforce=args.enforce_mercy,
    )
    drift_metrics = load_drift_metrics(paths.get("ystm_nodes"))
    tsr_delta_norm = None
    if paths.get("tsr_metrics") and os.path.exists(paths["tsr_metrics"]):
        try:
            tsr_payload = load_json(paths["tsr_metrics"])
            delta = tsr_payload.get("delta") if isinstance(tsr_payload, dict) else None
            if isinstance(delta, dict):
                value = delta.get("delta_norm")
                if isinstance(value, (int, float)):
                    tsr_delta_norm = float(value)
        except Exception:
            tsr_delta_norm = None
    run_id = os.path.basename(paths["run_dir"]) if paths.get("run_dir") else None
    escalation_result = escalation_gate(
        context,
        poav_result,
        drift_metrics,
        poav_threshold=args.poav_threshold,
        drift_threshold=args.drift_threshold,
        ledger_path=paths.get("error_ledger"),
        run_id=run_id,
    )
    p0_result = p0_gate(constraints_text)

    results = [
        context_lint(context),
        router_replay(context, registry, frame_plan),
        role_alignment(frame_plan),
        guardian_gate(frame_plan, enforce=args.enforce_guardian),
        constraint_consistency(constraints_text),
        p0_result,
        poav_result,
        mercy_result,
        seed_schema_gate(paths.get("seed"), require=args.require_seed),
        tech_trace_gate(
            paths.get("tech_trace_normalize"),
            require=args.require_tech_trace,
            strict=args.tech_trace_strict,
        ),
        intent_achievement_gate(
            paths.get("intent_verification"),
            require=args.require_intent,
        ),
        escalation_result,
        dcs_gate(
            context,
            p0_result,
            poav_result,
            mercy_result,
            escalation_result,
            drift_metrics,
            tsr_delta_norm,
            poav_threshold=args.poav_threshold,
            mercy_threshold=args.mercy_threshold,
            drift_threshold=args.drift_threshold,
        ),
    ]

    workspace_root = paths.get("workspace_root")
    if workspace_root:
        results.append(build_test_gate(workspace_root))

    evidence_text = ""
    if paths.get("evidence_summary") and os.path.exists(paths["evidence_summary"]):
        with open(paths["evidence_summary"], "r", encoding="utf-8") as handle:
            evidence_text = handle.read()
    required_files = {
        "context": paths.get("context"),
        "execution_report": paths.get("execution_report"),
        "action_set": paths.get("action_set"),
        "mercy_objective": paths.get("mercy_objective"),
        "council_summary": paths.get("council_summary"),
        "ystm_nodes": paths.get("ystm_nodes"),
        "ystm_audit": paths.get("ystm_audit"),
    }
    optional_required = {
        "tsr_metrics": paths.get("tsr_metrics"),
        "ystm_diff": paths.get("ystm_diff"),
        "ystm_terrain": paths.get("ystm_terrain"),
        "ystm_terrain_json": paths.get("ystm_terrain_json"),
        "ystm_terrain_svg": paths.get("ystm_terrain_svg"),
        "ystm_terrain_png": paths.get("ystm_terrain_png"),
        "ystm_terrain_p2": paths.get("ystm_terrain_p2"),
        "ystm_terrain_p2_json": paths.get("ystm_terrain_p2_json"),
        "ystm_terrain_p2_svg": paths.get("ystm_terrain_p2_svg"),
        "ystm_terrain_p2_png": paths.get("ystm_terrain_p2_png"),
        "tech_trace_capture": paths.get("tech_trace_capture"),
        "tech_trace_normalize": paths.get("tech_trace_normalize"),
        "skills_applied": paths.get("skills_applied"),
        "intent_verification": paths.get("intent_verification"),
    }
    for key, value in optional_required.items():
        if value:
            required_files[key] = value
    if paths.get("seed") and os.path.exists(paths["seed"]):
        required_files["seed"] = paths.get("seed")
    results.append(
        evidence_completeness(
            evidence_text,
            paths.get("context"),
            paths.get("execution_report"),
            required_files,
            require_listed=bool(args.require_evidence),
        )
    )

    gate_report = build_gate_report(results)
    output_path = paths.get("output") or os.path.join(os.getcwd(), "gate_report.json")
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(gate_report, handle, indent=2)

    dcs_result = next(
        (result for result in gate_report.get("results", []) if result.get("gate") == "dcs_gate"),
        None,
    )
    if dcs_result and paths.get("run_dir"):
        details = dcs_result.get("details")
        if isinstance(details, dict) and details:
            payload = dict(details)
            payload["gate"] = dcs_result.get("gate", "dcs_gate")
            payload["passed"] = dcs_result.get("passed")
            payload["issues"] = dcs_result.get("issues", [])
            dcs_path = os.path.join(paths["run_dir"], "dcs_result.json")
            with open(dcs_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)

    if not args.no_update_report and paths.get("execution_report"):
        update_execution_report(paths["execution_report"], gate_report)

    return {"gate_report": output_path}


if __name__ == "__main__":
    output = main()
    print(f"gate_report.json: {output['gate_report']}")
