"""YSS semantic-field pipeline: route YSTM frames through gates, action set, and audit."""

__ts_layer__ = "pipeline"
__ts_purpose__ = "Compose YSS gates, action set, and audit into one semantic-field pipeline pass."

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import yaml

from .action_set import resolve_action_set
from .audit_interface import build_audit_request
from .constraint_stack import build_constraints_doc
from .context_compiler import compile_context
from .escalation import load_drift_metrics
from .evidence_collector import append_to_summary, build_evidence_summary
from .frame_router import build_frame_plan
from .generation_orch import build_execution_report, record_error_event
from .intent_verification import build_intent_verification
from .memory_manager import archive_runs, build_indexes, collect_run_dirs, list_run_dirs, record_run
from .mercy_objective import resolve_mercy_objective
from .reflection import build_reflection, write_reflection
from .skill_apply import apply_skills, format_skill_section
from .skill_gate import list_skill_paths, review_skills
from .skill_promoter import promote_skills
from .tech_trace.capture import capture_record
from .tech_trace.normalize import normalize_record
from .tsr_metrics import (
    build_tsr_metrics,
    latest_entry,
    load_index,
    update_index,
    write_tsr_metrics,
)
from .yss_gates import (
    GateResult,
    build_gate_report,
    build_test_gate,
    constraint_consistency,
    context_lint,
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
from .yss_unified_adapter import (
    build_multi_persona_eval_snapshot,
    build_unified_seed,
    write_multi_persona_eval_snapshot,
)
from .ystm.demo import DEFAULT_SEGMENTS, DemoConfig, write_demo_outputs
from .ystm.energy import EnergyConfig
from .ystm.ingest import load_segments, normalize_segments
from .ystm.representation import EmbeddingConfig
from .ystm.terrain import TerrainConfig


@dataclass
class PipelineConfig:
    run_dir: Optional[str] = None
    seed_path: Optional[str] = None
    task: Optional[str] = None
    objective: Optional[str] = None
    domain: Optional[str] = None
    decision_mode: Optional[str] = None
    run_ystm_demo: bool = True
    ystm_export_png: bool = False
    ystm_png_scale: float = 2.0
    ystm_input: Optional[str] = None
    ystm_diff_path: Optional[str] = None
    tech_trace_capture_path: Optional[str] = None
    tech_trace_normalize_path: Optional[str] = None
    tech_trace_auto: bool = False
    tech_trace_auto_claim_limit: int = 12
    tech_trace_auto_claim_min_chars: int = 24
    tech_trace_require: bool = False
    tech_trace_strict: bool = False
    intent_evidence_path: Optional[str] = None
    intent_require: bool = False
    error_event: Optional[str] = None
    error_ledger: Optional[str] = None
    skip_gates: bool = False
    poav_threshold: float = 0.7
    poav_enforce: bool = False
    drift_threshold: float = 4.0
    mercy_threshold: float = 0.1
    mercy_enforce: bool = False
    guardian_enforce: bool = False
    seed_gate_require: bool = False
    trace_level: str = "standard"
    mercy_weights: Optional[Dict[str, float]] = None
    mercy_signals: Optional[Dict[str, float]] = None
    record_memory: bool = True
    memory_root: Optional[str] = None
    archive_root: Optional[str] = None
    promote_skills: bool = True
    skill_policy_path: Optional[str] = None
    auto_compact: bool = True
    compact_max_runs: Optional[int] = None
    compact_keep_latest: Optional[int] = None
    auto_review_skills: bool = True
    energy: EnergyConfig = EnergyConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    terrain: TerrainConfig = TerrainConfig()


@dataclass
class ContextArtifacts:
    context_payload: Dict[str, object]
    context_path: str
    action_set: Dict[str, object]
    action_set_path: str
    mercy_objective: Dict[str, object]
    mercy_objective_path: str
    registry: List[Dict[str, object]]
    frame_plan: Dict[str, object]
    frame_plan_path: str
    council_summary_path: Optional[str]


@dataclass
class SkillArtifacts:
    constraints_doc: str
    constraints_path: str
    skills_path: Optional[str]
    applied_skills: List[Dict[str, object]]
    skill_directives: Dict[str, bool]


@dataclass
class GateArtifacts:
    gate_report: Dict[str, object]
    gate_results: List[GateResult]
    reflection_path: Optional[str]
    poav_result: Optional[Dict[str, object]]
    mercy_result: Optional[Dict[str, object]]
    escalation_result: Optional[Dict[str, object]]
    dcs_result: Optional[Dict[str, object]]
    dcs_result_path: Optional[str]


@dataclass
class PipelineContext:
    """Runtime state flowing through the gate pipeline.

    Encapsulates all paths, payloads, and computed values that
    previously required 25+ individual function parameters.
    """

    config: PipelineConfig
    workspace: str
    run_dir: str

    # --- payloads ---
    context_payload: Dict[str, object]
    registry: List[Dict[str, object]]
    frame_plan: Dict[str, object]
    constraints_doc: str
    execution_report: str
    mercy_objective: Dict[str, object]
    skill_directives: Dict[str, bool]
    ystm_outputs: Dict[str, str]

    # --- paths ---
    context_path: str
    action_set_path: str
    mercy_objective_path: str
    execution_report_path: str
    evidence_summary_path: str
    error_ledger_path: str
    gate_report_path: str
    council_summary_path: Optional[str] = None
    tsr_metrics_path: Optional[str] = None
    skills_path: Optional[str] = None
    ystm_diff_path: Optional[str] = None
    tech_trace_capture_path: Optional[str] = None
    tech_trace_normalize_path: Optional[str] = None
    intent_verification_path: Optional[str] = None


def _load_seed(path: str) -> Dict[str, object]:
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as handle:
        if ext in {".yaml", ".yml"}:
            payload = yaml.safe_load(handle)
        elif ext == ".json":
            payload = json.load(handle)
        else:
            raise ValueError("Seed file must be .json or .yaml/.yml")
    if not isinstance(payload, dict):
        raise ValueError("Seed payload must be an object.")
    return payload


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _resolve_run_dir(config: PipelineConfig) -> str:
    if config.run_dir:
        return os.path.abspath(config.run_dir)
    run_id = _generate_run_id()
    return os.path.join(_workspace_root(), "run", "execution", run_id)


def _generate_run_id() -> str:
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S")
    ms = f"{int(now.microsecond / 1000):03d}"
    suffix = uuid.uuid4().hex[:6]
    return f"{stamp}{ms}Z_{suffix}"


def _write_yaml(path: str, payload: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def _write_json(path: str, payload: object) -> None:
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _default_memory_policy_path() -> str:
    return os.path.join(_workspace_root(), "spec", "memory", "memory_policy.yaml")


def _apply_trace_level(config: PipelineConfig) -> None:
    level = (config.trace_level or "standard").strip().lower()
    if level not in {"standard", "full"}:
        raise ValueError("trace_level must be 'standard' or 'full'.")
    config.trace_level = level
    if level == "standard":
        config.record_memory = False
        config.promote_skills = False
        config.auto_review_skills = False
        config.auto_compact = False


def _load_policy(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _build_seed_from_config(config: PipelineConfig) -> Dict[str, object]:
    seed: Dict[str, object] = {}
    if config.seed_path:
        seed.update(_load_seed(config.seed_path))
    if config.task:
        seed["task"] = config.task
    if config.objective:
        seed["objective"] = config.objective
    if config.domain:
        seed["domain"] = config.domain
    if config.decision_mode:
        seed["decision_mode"] = config.decision_mode
    return seed


def _load_frame_registry(spec_root: str) -> List[Dict[str, object]]:
    registry_path = os.path.join(spec_root, "frames", "frame_registry.json")
    with open(registry_path, "r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, list):
        raise ValueError("frame_registry.json must be a list.")
    return registry


def _prepare_context_artifacts(
    seed: Dict[str, object],
    run_dir: str,
    spec_root: str,
    config: PipelineConfig,
) -> ContextArtifacts:
    context_payload = compile_context(seed)
    context_path = os.path.join(run_dir, "context.yaml")
    _write_yaml(context_path, context_payload)

    action_set = resolve_action_set(context_payload)
    action_set_path = os.path.join(run_dir, "action_set.json")
    _write_json(action_set_path, action_set)

    mercy_objective = resolve_mercy_objective(
        context_payload,
        signals=config.mercy_signals,
        weight_overrides=config.mercy_weights,
    )
    mercy_objective_path = os.path.join(run_dir, "mercy_objective.json")
    _write_json(mercy_objective_path, mercy_objective)

    registry = _load_frame_registry(spec_root)
    frame_plan = build_frame_plan(context_payload, registry)
    frame_plan_path = os.path.join(run_dir, "frame_plan.json")
    _write_json(frame_plan_path, frame_plan)

    council_summary_path = None
    council_summary = frame_plan.get("council_summary") if isinstance(frame_plan, dict) else None
    if isinstance(council_summary, dict) and council_summary:
        council_summary_path = os.path.join(run_dir, "council_summary.json")
        _write_json(council_summary_path, council_summary)

    return ContextArtifacts(
        context_payload=context_payload,
        context_path=context_path,
        action_set=action_set,
        action_set_path=action_set_path,
        mercy_objective=mercy_objective,
        mercy_objective_path=mercy_objective_path,
        registry=registry,
        frame_plan=frame_plan,
        frame_plan_path=frame_plan_path,
        council_summary_path=council_summary_path,
    )


def _build_constraints_and_skills(
    context_payload: Dict[str, object],
    frame_plan: Dict[str, object],
    mercy_objective: Dict[str, object],
    run_dir: str,
    spec_root: str,
    policy: Dict[str, object],
    memory_root: Optional[str],
) -> SkillArtifacts:
    template_path = os.path.join(spec_root, "constraints", "constraints_template.md")
    with open(template_path, "r", encoding="utf-8") as handle:
        template_text = handle.read()
    constraints_doc = build_constraints_doc(
        context_payload,
        template_text,
        frame_plan_path=os.path.join(run_dir, "frame_plan.json"),
        mercy_objective=mercy_objective,
    )
    skills_payload, applied_skills, skill_directives, skill_constraints = apply_skills(
        context_payload,
        frame_plan,
        memory_root=memory_root,
        matching_policy=policy.get("skill_matching", {}),
    )
    skills_path = None
    if applied_skills:
        skill_section = format_skill_section(applied_skills, skill_directives)
        if skill_constraints:
            skill_section = (
                f"{skill_section}## Skill Constraints\n" + "\n".join(skill_constraints) + "\n"
            )
        constraints_doc = f"{constraints_doc}\n{skill_section}"
        skills_path = os.path.join(run_dir, "skills_applied.json")
        _write_json(skills_path, skills_payload)

    constraints_path = os.path.join(run_dir, "constraints.md")
    with open(constraints_path, "w", encoding="utf-8") as handle:
        handle.write(constraints_doc)

    return SkillArtifacts(
        constraints_doc=constraints_doc,
        constraints_path=constraints_path,
        skills_path=skills_path,
        applied_skills=applied_skills,
        skill_directives=skill_directives,
    )


def _generate_ystm_outputs(config: PipelineConfig, workspace: str) -> Dict[str, str]:
    if not config.run_ystm_demo:
        return {}
    segments = DEFAULT_SEGMENTS
    if config.ystm_input:
        segments = load_segments(config.ystm_input)
    else:
        segments = normalize_segments(segments)
    demo_config = DemoConfig(
        embedding=config.embedding,
        energy=config.energy,
        terrain=config.terrain,
    )
    return write_demo_outputs(
        os.path.join(workspace, "reports", "ystm_demo"),
        segments,
        demo_config,
        export_png=config.ystm_export_png,
        png_scale=config.ystm_png_scale,
    )


def _resolve_optional_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return os.path.abspath(path)


def _record_error_event_id(config: PipelineConfig, error_ledger_path: str) -> Optional[str]:
    if config.error_event:
        return record_error_event(config.error_event, error_ledger_path)
    return None


def _write_execution_report(
    run_dir: str,
    context_payload: Dict[str, object],
    frame_plan: Dict[str, object],
    constraints_doc: str,
    error_event_id: Optional[str],
    applied_skills: List[Dict[str, object]],
) -> Tuple[str, str]:
    execution_report = build_execution_report(
        context_payload,
        frame_plan,
        constraints_doc,
        error_event_id=error_event_id,
        skills_applied=applied_skills if applied_skills else None,
    )
    execution_report_path = os.path.join(run_dir, "execution_report.md")
    with open(execution_report_path, "w", encoding="utf-8") as handle:
        handle.write(execution_report)
    return execution_report, execution_report_path


def _auto_generate_tech_trace(
    run_dir: str,
    execution_report: str,
    context_payload: Dict[str, object],
    claim_limit: int,
    claim_min_chars: int,
) -> Tuple[Optional[str], Optional[str]]:
    if not execution_report.strip():
        return None, None
    context = (
        context_payload.get("context", {})
        if isinstance(context_payload.get("context"), dict)
        else {}
    )
    title = context.get("task") or "YSS execution report"
    notes = "auto-generated from execution_report"
    tags = ["auto", "yss", "execution_report"]
    capture_payload = capture_record(
        raw_text=execution_report,
        source_type="execution_report",
        uri=None,
        title=title,
        grade="C",
        retrieved_at=None,
        verified_by=None,
        notes=notes,
        tags=tags,
    )
    source = capture_payload.get("source", {}) if isinstance(capture_payload, dict) else {}
    normalize_payload = normalize_record(
        raw_text=execution_report,
        capture_id=capture_payload.get("capture_id") if isinstance(capture_payload, dict) else None,
        source=source if isinstance(source, dict) else {},
        source_grade="C",
        summary=None,
        notes=notes,
        tags=tags,
        max_length=None,
        claims=None,
        links=None,
        attributions=None,
        auto_claims=True,
        auto_claim_limit=claim_limit,
        auto_claim_min_chars=claim_min_chars,
    )
    capture_id = capture_payload.get("capture_id") if isinstance(capture_payload, dict) else None
    normalize_id = (
        normalize_payload.get("normalize_id") if isinstance(normalize_payload, dict) else None
    )
    if not capture_id or not normalize_id:
        return None, None
    output_dir = os.path.join(run_dir, "tech_trace")
    os.makedirs(output_dir, exist_ok=True)
    capture_path = os.path.join(output_dir, f"{capture_id}.json")
    normalize_path = os.path.join(output_dir, f"{normalize_id}.json")
    with open(capture_path, "w", encoding="utf-8") as handle:
        json.dump(capture_payload, handle, indent=2)
    with open(normalize_path, "w", encoding="utf-8") as handle:
        json.dump(normalize_payload, handle, indent=2)
    return capture_path, normalize_path


def _build_evidence_artifacts(
    action_set_path: str,
    mercy_objective_path: str,
    council_summary_path: Optional[str],
    skills_path: Optional[str],
    applied_skills: List[Dict[str, object]],
    error_ledger_ref: Optional[str],
    tsr_metrics_path: Optional[str],
    dcs_result_path: Optional[str],
    ystm_outputs: Dict[str, str],
    ystm_diff_path: Optional[str],
    tech_trace_capture_path: Optional[str],
    tech_trace_normalize_path: Optional[str],
    intent_verification_path: Optional[str],
) -> Dict[str, Optional[str]]:
    return {
        "action_set": action_set_path,
        "mercy_objective": mercy_objective_path,
        "council_summary": council_summary_path,
        "skills_applied": skills_path if applied_skills else None,
        "error_ledger": error_ledger_ref,
        "tsr_metrics": tsr_metrics_path,
        "dcs_result": dcs_result_path,
        "ystm_audit": ystm_outputs.get("audit"),
        "ystm_diff": ystm_diff_path,
        "ystm_nodes": ystm_outputs.get("nodes"),
        "ystm_terrain": ystm_outputs.get("terrain"),
        "ystm_terrain_json": ystm_outputs.get("terrain_json"),
        "ystm_terrain_svg": ystm_outputs.get("terrain_svg"),
        "ystm_terrain_png": ystm_outputs.get("terrain_png"),
        "ystm_terrain_p2": ystm_outputs.get("terrain_p2"),
        "ystm_terrain_p2_json": ystm_outputs.get("terrain_p2_json"),
        "ystm_terrain_p2_svg": ystm_outputs.get("terrain_p2_svg"),
        "ystm_terrain_p2_png": ystm_outputs.get("terrain_p2_png"),
        "tech_trace_capture": tech_trace_capture_path,
        "tech_trace_normalize": tech_trace_normalize_path,
        "intent_verification": intent_verification_path,
    }


def _resolve_retention_config(
    policy: Dict[str, object], workspace: str
) -> Optional[Dict[str, object]]:
    retention = policy.get("retention", {}) if isinstance(policy, dict) else {}
    if not retention.get("enabled"):
        return None
    evidence_retention = retention.get("evidence", {}) if isinstance(retention, dict) else {}
    if not isinstance(evidence_retention, dict):
        return None
    if evidence_retention.get("max_entries") is None:
        return None
    archive_dir = evidence_retention.get("archive_dir")
    if archive_dir and not os.path.isabs(archive_dir):
        archive_dir = os.path.abspath(os.path.join(workspace, archive_dir))
    return {
        "max_entries": evidence_retention.get("max_entries"),
        "keep_latest": evidence_retention.get("keep_latest"),
        "archive_dir": archive_dir,
    }


def _append_evidence_summary(
    workspace: str,
    context_path: str,
    execution_report_path: str,
    evidence_artifacts: Dict[str, Optional[str]],
    policy: Dict[str, object],
) -> str:
    evidence_summary_path = os.path.join(workspace, "evidence", "summary.md")
    evidence_entry = build_evidence_summary(
        context_path,
        execution_report_path,
        artifacts=evidence_artifacts,
    )
    retention_config = _resolve_retention_config(policy, workspace)
    append_to_summary(evidence_summary_path, evidence_entry, retention=retention_config)
    return evidence_summary_path


def _extract_gate_result(
    gate_report: Dict[str, object],
    gate_name: str,
) -> Optional[Dict[str, object]]:
    for result in gate_report.get("results", []):
        if isinstance(result, dict) and result.get("gate") == gate_name:
            return result
    return None


def _build_required_files(ctx: PipelineContext) -> Dict[str, Optional[str]]:
    required_files = {
        "context": ctx.context_path,
        "execution_report": ctx.execution_report_path,
        "action_set": ctx.action_set_path,
        "mercy_objective": ctx.mercy_objective_path,
        "council_summary": ctx.council_summary_path,
        "tsr_metrics": ctx.tsr_metrics_path,
        "ystm_nodes": ctx.ystm_outputs.get("nodes"),
        "ystm_audit": ctx.ystm_outputs.get("audit"),
        "ystm_terrain": ctx.ystm_outputs.get("terrain"),
        "ystm_terrain_json": ctx.ystm_outputs.get("terrain_json"),
        "ystm_terrain_svg": ctx.ystm_outputs.get("terrain_svg"),
        "ystm_terrain_p2": ctx.ystm_outputs.get("terrain_p2"),
        "ystm_terrain_p2_json": ctx.ystm_outputs.get("terrain_p2_json"),
        "ystm_terrain_p2_svg": ctx.ystm_outputs.get("terrain_p2_svg"),
    }
    if ctx.skills_path:
        required_files["skills_applied"] = ctx.skills_path
    if ctx.ystm_diff_path:
        required_files["ystm_diff"] = ctx.ystm_diff_path
    if ctx.tech_trace_capture_path:
        required_files["tech_trace_capture"] = ctx.tech_trace_capture_path
    if ctx.tech_trace_normalize_path:
        required_files["tech_trace_normalize"] = ctx.tech_trace_normalize_path
    if ctx.intent_verification_path:
        required_files["intent_verification"] = ctx.intent_verification_path
    return required_files


def _collect_gate_results(ctx: PipelineContext) -> List[GateResult]:
    config = ctx.config
    skip_gates = config.skip_gates
    if ctx.skill_directives.get("force_gates") or ctx.skill_directives.get("require_evidence"):
        skip_gates = False

    p0_result_gate = p0_gate(ctx.constraints_doc)
    if skip_gates:
        return [p0_result_gate]

    poav_result_gate = poav_gate(
        ctx.execution_report,
        threshold=config.poav_threshold,
        enforce=config.poav_enforce,
        source="execution_report",
    )
    mercy_result_gate = mercy_gate(
        ctx.mercy_objective,
        threshold=config.mercy_threshold,
        enforce=config.mercy_enforce,
    )
    drift_metrics = load_drift_metrics(ctx.ystm_outputs.get("nodes"))
    tsr_delta_norm = None
    if ctx.tsr_metrics_path and os.path.exists(ctx.tsr_metrics_path):
        try:
            with open(ctx.tsr_metrics_path, "r", encoding="utf-8") as handle:
                tsr_payload = json.load(handle)
            delta = tsr_payload.get("delta") if isinstance(tsr_payload, dict) else None
            if isinstance(delta, dict):
                value = delta.get("delta_norm")
                if isinstance(value, (int, float)):
                    tsr_delta_norm = float(value)
        except (OSError, json.JSONDecodeError):
            tsr_delta_norm = None
    escalation_result_gate = escalation_gate(
        ctx.context_payload,
        poav_result_gate,
        drift_metrics,
        poav_threshold=config.poav_threshold,
        drift_threshold=config.drift_threshold,
        ledger_path=ctx.error_ledger_path,
        run_id=os.path.basename(ctx.run_dir),
    )
    results = [
        context_lint(ctx.context_payload),
        router_replay(ctx.context_payload, ctx.registry, ctx.frame_plan),
        role_alignment(ctx.frame_plan),
        guardian_gate(ctx.frame_plan, enforce=config.guardian_enforce),
        constraint_consistency(ctx.constraints_doc),
        p0_result_gate,
        poav_result_gate,
        mercy_result_gate,
        tech_trace_gate(
            ctx.tech_trace_normalize_path,
            require=config.tech_trace_require,
            strict=config.tech_trace_strict,
        ),
        intent_achievement_gate(
            ctx.intent_verification_path,
            require=config.intent_require,
        ),
        escalation_result_gate,
        dcs_gate(
            ctx.context_payload,
            p0_result_gate,
            poav_result_gate,
            mercy_result_gate,
            escalation_result_gate,
            drift_metrics,
            tsr_delta_norm,
            poav_threshold=config.poav_threshold,
            mercy_threshold=config.mercy_threshold,
            drift_threshold=config.drift_threshold,
        ),
        build_test_gate(ctx.workspace),
    ]
    evidence_text = ""
    if os.path.exists(ctx.evidence_summary_path):
        with open(ctx.evidence_summary_path, "r", encoding="utf-8") as handle:
            evidence_text = handle.read()
    required_files = _build_required_files(ctx)
    results.append(
        evidence_completeness(
            evidence_text,
            ctx.context_path,
            ctx.execution_report_path,
            required_files,
            require_listed=bool(ctx.skill_directives.get("require_evidence")),
        )
    )
    return results


def _write_gate_outputs(
    gate_report_path: str,
    execution_report_path: str,
    gate_results: List[GateResult],
    skill_directives: Dict[str, bool],
) -> Tuple[Dict[str, object], Optional[str]]:
    gate_report = build_gate_report(gate_results)
    with open(gate_report_path, "w", encoding="utf-8") as handle:
        json.dump(gate_report, handle, indent=2)
    update_execution_report(execution_report_path, gate_report)
    reflection = build_reflection(gate_report, directives=skill_directives)
    reflection_path = None
    if reflection:
        reflection_path = os.path.join(os.path.dirname(gate_report_path), "reflection.json")
        write_reflection(reflection_path, reflection)
    return gate_report, reflection_path


def _run_gates(ctx: PipelineContext) -> GateArtifacts:
    gate_results = _collect_gate_results(ctx)
    gate_report, reflection_path = _write_gate_outputs(
        ctx.gate_report_path,
        ctx.execution_report_path,
        gate_results,
        ctx.skill_directives,
    )
    dcs_result = _extract_gate_result(gate_report, "dcs_gate")
    dcs_result_path = None
    if isinstance(dcs_result, dict):
        details = dcs_result.get("details")
        if isinstance(details, dict) and details:
            payload = dict(details)
            payload["gate"] = dcs_result.get("gate", "dcs_gate")
            payload["passed"] = dcs_result.get("passed")
            payload["issues"] = dcs_result.get("issues", [])
            dcs_result_path = os.path.join(os.path.dirname(ctx.gate_report_path), "dcs_result.json")
            with open(dcs_result_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
    return GateArtifacts(
        gate_report=gate_report,
        gate_results=gate_results,
        reflection_path=reflection_path,
        poav_result=_extract_gate_result(gate_report, "poav_gate"),
        mercy_result=_extract_gate_result(gate_report, "mercy_gate"),
        escalation_result=_extract_gate_result(gate_report, "escalation_gate"),
        dcs_result=dcs_result if isinstance(dcs_result, dict) else None,
        dcs_result_path=dcs_result_path,
    )


def _extract_dispatch_trace_from_context(
    context_payload: Dict[str, object],
) -> Optional[Dict[str, object]]:
    inputs = context_payload.get("inputs") if isinstance(context_payload, dict) else None
    if not isinstance(inputs, dict):
        return None
    payload = inputs.get("payload")
    if not isinstance(payload, dict):
        return None
    dispatch_trace = payload.get("dispatch_trace")
    return dispatch_trace if isinstance(dispatch_trace, dict) else None


def run_pipeline_from_unified_request(
    unified_request: Dict[str, object],
    config: Optional[PipelineConfig] = None,
) -> Dict[str, object]:
    """Run YSS pipeline using UnifiedPipeline-style request schema."""
    seed = build_unified_seed(unified_request if isinstance(unified_request, dict) else {})
    cfg = config if config is not None else PipelineConfig()

    if not cfg.task:
        cfg.task = str(seed.get("task") or "")
    if not cfg.objective:
        cfg.objective = str(seed.get("objective") or "")
    if not cfg.domain:
        cfg.domain = str(seed.get("domain") or "")
    if not cfg.decision_mode:
        cfg.decision_mode = str(seed.get("decision_mode") or "normal")

    paths = run_pipeline(cfg)
    paths["unified_seed"] = seed
    return paths


def run_pipeline(config: PipelineConfig) -> Dict[str, object]:
    workspace = _workspace_root()
    _apply_trace_level(config)
    run_dir = _resolve_run_dir(config)
    error_ledger_path = config.error_ledger or os.path.join(run_dir, "error_ledger.jsonl")
    spec_root = os.path.join(workspace, "spec")
    policy_path = config.skill_policy_path or _default_memory_policy_path()
    policy = _load_policy(policy_path)

    seed = _build_seed_from_config(config)
    context_artifacts = _prepare_context_artifacts(seed, run_dir, spec_root, config)
    skill_artifacts = _build_constraints_and_skills(
        context_payload=context_artifacts.context_payload,
        frame_plan=context_artifacts.frame_plan,
        mercy_objective=context_artifacts.mercy_objective,
        run_dir=run_dir,
        spec_root=spec_root,
        policy=policy,
        memory_root=config.memory_root,
    )

    ystm_outputs = _generate_ystm_outputs(config, workspace)
    ystm_diff_path = _resolve_optional_path(config.ystm_diff_path)
    if ystm_diff_path:
        ystm_outputs["diff"] = ystm_diff_path
    tech_trace_capture_path = _resolve_optional_path(config.tech_trace_capture_path)
    tech_trace_normalize_path = _resolve_optional_path(config.tech_trace_normalize_path)
    intent_evidence_path = _resolve_optional_path(config.intent_evidence_path)
    if not intent_evidence_path:
        runtime_candidate = os.path.join(workspace, "runtime", "control_result.json")
        if os.path.exists(runtime_candidate):
            intent_evidence_path = runtime_candidate

    error_event_id = _record_error_event_id(config, error_ledger_path)
    error_ledger_ref = error_ledger_path if os.path.exists(error_ledger_path) else None

    execution_report, execution_report_path = _write_execution_report(
        run_dir,
        context_artifacts.context_payload,
        context_artifacts.frame_plan,
        skill_artifacts.constraints_doc,
        error_event_id,
        skill_artifacts.applied_skills,
    )
    intent_verification_path = os.path.join(run_dir, "intent_verification.json")
    intent_verification_payload = build_intent_verification(
        context_artifacts.context_payload,
        intent_evidence_path,
    )
    _write_json(intent_verification_path, intent_verification_payload)
    run_id = os.path.basename(run_dir)
    memory_root = os.path.abspath(config.memory_root or os.path.join(workspace, "memory"))
    tsr_index_path = os.path.join(memory_root, "tsr_index.json")
    tsr_index = load_index(tsr_index_path)
    tsr_baseline = latest_entry(tsr_index)
    tsr_metrics_payload = build_tsr_metrics(
        execution_report,
        run_id=run_id,
        source_path=execution_report_path,
        baseline_entry=tsr_baseline,
    )
    tsr_metrics_path = os.path.join(run_dir, "tsr_metrics.json")
    write_tsr_metrics(tsr_metrics_path, tsr_metrics_payload)
    if config.record_memory:
        update_index(tsr_index_path, run_id, tsr_metrics_path, tsr_metrics_payload)
    dcs_result_path = None
    if config.tech_trace_auto and not tech_trace_capture_path and not tech_trace_normalize_path:
        auto_capture_path, auto_normalize_path = _auto_generate_tech_trace(
            run_dir,
            execution_report,
            context_artifacts.context_payload,
            config.tech_trace_auto_claim_limit,
            config.tech_trace_auto_claim_min_chars,
        )
        if auto_capture_path:
            tech_trace_capture_path = auto_capture_path
        if auto_normalize_path:
            tech_trace_normalize_path = auto_normalize_path

    evidence_artifacts = _build_evidence_artifacts(
        action_set_path=context_artifacts.action_set_path,
        mercy_objective_path=context_artifacts.mercy_objective_path,
        council_summary_path=context_artifacts.council_summary_path,
        skills_path=skill_artifacts.skills_path,
        applied_skills=skill_artifacts.applied_skills,
        error_ledger_ref=error_ledger_ref,
        tsr_metrics_path=tsr_metrics_path,
        dcs_result_path=dcs_result_path,
        ystm_outputs=ystm_outputs,
        ystm_diff_path=ystm_diff_path,
        tech_trace_capture_path=tech_trace_capture_path,
        tech_trace_normalize_path=tech_trace_normalize_path,
        intent_verification_path=intent_verification_path,
    )
    evidence_summary_path = _append_evidence_summary(
        workspace,
        context_artifacts.context_path,
        execution_report_path,
        evidence_artifacts,
        policy,
    )

    gate_report_path = os.path.join(run_dir, "gate_report.json")
    pipeline_ctx = PipelineContext(
        config=config,
        workspace=workspace,
        run_dir=run_dir,
        context_payload=context_artifacts.context_payload,
        registry=context_artifacts.registry,
        frame_plan=context_artifacts.frame_plan,
        constraints_doc=skill_artifacts.constraints_doc,
        execution_report=execution_report,
        mercy_objective=context_artifacts.mercy_objective,
        skill_directives=skill_artifacts.skill_directives,
        ystm_outputs=ystm_outputs,
        context_path=context_artifacts.context_path,
        action_set_path=context_artifacts.action_set_path,
        mercy_objective_path=context_artifacts.mercy_objective_path,
        execution_report_path=execution_report_path,
        evidence_summary_path=evidence_summary_path,
        error_ledger_path=error_ledger_path,
        gate_report_path=gate_report_path,
        council_summary_path=context_artifacts.council_summary_path,
        tsr_metrics_path=tsr_metrics_path,
        skills_path=skill_artifacts.skills_path,
        ystm_diff_path=ystm_diff_path,
        tech_trace_capture_path=tech_trace_capture_path,
        tech_trace_normalize_path=tech_trace_normalize_path,
        intent_verification_path=intent_verification_path,
    )
    gate_artifacts = _run_gates(pipeline_ctx)
    dispatch_trace = _extract_dispatch_trace_from_context(context_artifacts.context_payload)
    multi_persona_eval_payload = build_multi_persona_eval_snapshot(
        gate_report=gate_artifacts.gate_report,
        dispatch_trace=dispatch_trace,
    )
    multi_persona_eval_path = write_multi_persona_eval_snapshot(
        os.path.join(run_dir, "multi_persona_eval.json"),
        multi_persona_eval_payload,
    )

    audit_request_path = os.path.join(run_dir, "audit_request.json")
    gate_report_ref = gate_report_path
    error_ledger_ref = error_ledger_path if os.path.exists(error_ledger_path) else None
    audit_request = build_audit_request(
        context_path=context_artifacts.context_path,
        frame_plan_path=context_artifacts.frame_plan_path,
        constraints_path=skill_artifacts.constraints_path,
        execution_report_path=execution_report_path,
        evidence_summary_path=evidence_summary_path,
        gate_report_path=gate_report_ref,
        error_ledger_path=error_ledger_ref,
        action_set_path=context_artifacts.action_set_path,
        mercy_objective_path=context_artifacts.mercy_objective_path,
        council_summary_path=context_artifacts.council_summary_path,
        tsr_metrics_path=tsr_metrics_path,
        dcs_result_path=gate_artifacts.dcs_result_path,
        ystm_nodes_path=ystm_outputs.get("nodes"),
        ystm_audit_path=ystm_outputs.get("audit"),
        ystm_diff_path=ystm_diff_path,
        ystm_terrain_path=ystm_outputs.get("terrain"),
        ystm_terrain_json_path=ystm_outputs.get("terrain_json"),
        ystm_terrain_svg_path=ystm_outputs.get("terrain_svg"),
        ystm_terrain_png_path=ystm_outputs.get("terrain_png"),
        ystm_terrain_p2_path=ystm_outputs.get("terrain_p2"),
        ystm_terrain_p2_json_path=ystm_outputs.get("terrain_p2_json"),
        ystm_terrain_p2_svg_path=ystm_outputs.get("terrain_p2_svg"),
        ystm_terrain_p2_png_path=ystm_outputs.get("terrain_p2_png"),
        tech_trace_capture_path=tech_trace_capture_path,
        tech_trace_normalize_path=tech_trace_normalize_path,
        intent_verification_path=intent_verification_path,
        skills_applied_path=skill_artifacts.skills_path if skill_artifacts.applied_skills else None,
        reflection_path=gate_artifacts.reflection_path,
        poav_result=gate_artifacts.poav_result,
        escalation_result=gate_artifacts.escalation_result,
        mercy_result=gate_artifacts.mercy_result,
    )
    with open(audit_request_path, "w", encoding="utf-8") as handle:
        json.dump(audit_request, handle, indent=2)

    memory_paths = {}
    if config.record_memory:
        memory_paths = record_run(
            run_dir,
            ystm_outputs=ystm_outputs,
            memory_root=config.memory_root,
            archive_root=config.archive_root,
        )
    if gate_artifacts.gate_results and config.seed_gate_require:
        seed_path = memory_paths.get("seed")
        seed_result = seed_schema_gate(seed_path, require=True)
        gate_artifacts.gate_results.append(seed_result)
        gate_report, reflection_path = _write_gate_outputs(
            gate_report_path,
            execution_report_path,
            gate_artifacts.gate_results,
            skill_artifacts.skill_directives,
        )
        gate_artifacts.gate_report = gate_report
        gate_artifacts.reflection_path = reflection_path
        gate_artifacts.poav_result = _extract_gate_result(gate_report, "poav_gate")
        gate_artifacts.mercy_result = _extract_gate_result(gate_report, "mercy_gate")
        gate_artifacts.escalation_result = _extract_gate_result(gate_report, "escalation_gate")

    skill_paths = {}
    if config.promote_skills:
        skill_paths = promote_skills(
            memory_root=config.memory_root,
            policy_path=policy_path,
        )

    review_paths = {}
    review_policy = policy.get("review", {}) if isinstance(policy.get("review"), dict) else {}
    if config.auto_review_skills and review_policy.get("auto_approve"):
        memory_root = os.path.abspath(config.memory_root or os.path.join(workspace, "memory"))
        review_paths = review_skills(
            list_skill_paths(memory_root),
            decision=None,
            reviewer=review_policy.get("default_reviewer"),
            reviewer_role=review_policy.get("default_role"),
            note="auto-review",
            memory_root=memory_root,
            policy_path=policy_path,
        )

    compaction_paths = {}
    if config.auto_compact:
        compaction = policy.get("compaction", {}) if isinstance(policy, dict) else {}
        enabled = compaction.get("enabled", False)
        if enabled:
            workspace_root = _workspace_root()
            run_root = os.path.join(workspace_root, "run", "execution")
            memory_root = os.path.abspath(
                config.memory_root or os.path.join(workspace_root, "memory")
            )
            archive_root = os.path.abspath(
                config.archive_root or os.path.join(workspace_root, "..", "archive", "runs")
            )
            max_runs = (
                config.compact_max_runs
                if config.compact_max_runs is not None
                else compaction.get("max_active_runs")
            )
            keep_latest = (
                config.compact_keep_latest
                if config.compact_keep_latest is not None
                else compaction.get("keep_latest")
            )
            include_archived = compaction.get("include_archived", True)
            run_dirs = list_run_dirs(run_root)
            if max_runs and keep_latest and len(run_dirs) > int(max_runs):
                archived_paths = archive_runs(run_root, archive_root, keep_latest=int(keep_latest))
                run_roots = [run_root]
                if include_archived:
                    run_roots.append(archive_root)
                indexed = build_indexes(
                    collect_run_dirs(run_roots),
                    memory_root=memory_root,
                    archive_root=archive_root,
                )
                compaction_paths = {
                    "archived_count": len(archived_paths),
                    "archived_paths": archived_paths,
                    **indexed,
                }
                memory_paths.update(indexed)

    return {
        "run_dir": run_dir,
        "context": context_artifacts.context_path,
        "frame_plan": context_artifacts.frame_plan_path,
        "action_set": context_artifacts.action_set_path,
        "mercy_objective": context_artifacts.mercy_objective_path,
        "council_summary": context_artifacts.council_summary_path,
        "constraints": skill_artifacts.constraints_path,
        "execution_report": execution_report_path,
        "tsr_metrics": tsr_metrics_path,
        "evidence_summary": evidence_summary_path,
        "audit_request": audit_request_path,
        "gate_report": gate_report_path,
        "dcs_result": gate_artifacts.dcs_result_path,
        "multi_persona_eval": multi_persona_eval_path,
        "skills_applied": skill_artifacts.skills_path if skill_artifacts.applied_skills else None,
        "skills_directives": (
            skill_artifacts.skill_directives if skill_artifacts.applied_skills else None
        ),
        "reflection": gate_artifacts.reflection_path,
        "memory_seed": memory_paths.get("seed"),
        "memory_graph": memory_paths.get("graph"),
        "memory_run_index": memory_paths.get("run_index"),
        "memory_episode_index": skill_paths.get("episode_index"),
        "memory_skill_index": skill_paths.get("skill_index"),
        "memory_skill_review": review_paths,
        "memory_compaction": compaction_paths,
        "tech_trace_capture": tech_trace_capture_path,
        "tech_trace_normalize": tech_trace_normalize_path,
        "intent_verification": intent_verification_path,
        **{f"ystm_{key}": value for key, value in ystm_outputs.items()},
    }
