#!/usr/bin/env python3
"""Render a retrieval-oriented structure map for ToneSoul documentation authority."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

INVENTORY_PATH = Path("docs/status/doc_convergence_inventory_latest.json")
JSON_FILENAME = "doc_authority_structure_latest.json"
MARKDOWN_FILENAME = "doc_authority_structure_latest.md"
MERMAID_FILENAME = "doc_authority_structure_latest.mmd"

GROUPS = [
    {
        "id": "entrypoints",
        "label": "Entry Points",
        "description": "first surfaces for orientation and collaboration posture",
        "authority_role": "entrypoint",
        "use_when": "first repo contact, before choosing which deeper lane to open",
        "read_order": 1,
        "files": [
            "README.md",
            "README.zh-TW.md",
            "AI_ONBOARDING.md",
            "docs/INDEX.md",
            "docs/README.md",
        ],
    },
    {
        "id": "ai_operational_guides",
        "label": "AI Operational Guides",
        "description": "minimal working entry and lookup surfaces for later agents",
        "authority_role": "operational",
        "use_when": "after entrypoint routing, before or during daily work",
        "read_order": 2,
        "files": [
            "docs/AI_QUICKSTART.md",
            "docs/AI_REFERENCE.md",
        ],
    },
    {
        "id": "canonical_architecture",
        "label": "Canonical Architecture",
        "description": "canonical architectural north-star and layer maps",
        "authority_role": "canonical",
        "use_when": "before architecture claims, runtime authority claims, or boundary changes",
        "read_order": 3,
        "files": [
            "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md",
            "docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md",
            "docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md",
            "docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md",
        ],
    },
    {
        "id": "deep_system_maps",
        "label": "Deep System Maps",
        "description": "panoramic repository-wide maps that explain the whole system without becoming executable contracts",
        "authority_role": "deep_map",
        "use_when": "before repo-wide refactors or whole-system explanations",
        "read_order": 4,
        "files": [
            "docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md",
            "docs/narrative/TONESOUL_ANATOMY.md",
        ],
    },
    {
        "id": "interpretive_readings",
        "label": "Interpretive Readings",
        "description": "grounded narrative readings that help later agents inherit load-bearing meaning without outranking canonical contracts",
        "authority_role": "interpretive",
        "use_when": "when the architecture map is clear but the deeper load-bearing meaning is still not",
        "read_order": 5,
        "files": [
            "docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md",
            "docs/narrative/TONESOUL_CODEX_READING.md",
        ],
    },
    {
        "id": "governance_execution",
        "label": "Governance And Execution",
        "description": "runtime, audit, and API contracts",
        "authority_role": "contract",
        "use_when": "when moving from documentation into executable governance or API behavior",
        "read_order": 6,
        "files": [
            "docs/7D_AUDIT_FRAMEWORK.md",
            "docs/7D_EXECUTION_SPEC.md",
            "docs/AUDIT_CONTRACT.md",
            "docs/API_SPEC.md",
            "docs/COUNCIL_RUNTIME.md",
            "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md",
        ],
    },
    {
        "id": "claim_authority_distillation",
        "label": "Claim Authority Distillation",
        "description": "boundary aids that classify whether prominent repo terms are active runtime, vocabulary, theory, or projection",
        "authority_role": "boundary_contract",
        "use_when": "when a term sounds load-bearing but you need to know whether it is truly implemented before relying on it",
        "read_order": 7,
        "files": [
            "docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md",
            "docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md",
        ],
    },
    {
        "id": "evidence_topology_and_verifiability",
        "label": "Evidence And Verifiability",
        "description": "evidence ladders and topology aids that separate what is tested, structurally enforced, runtime-present, document-backed, philosophical, or currently blocked",
        "authority_role": "evidence_map",
        "use_when": "when a claim sounds important and you need to know whether it is regression-backed, schema-backed, thinly tested, or merely documented before repeating it",
        "read_order": 8,
        "files": [
            "docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md",
            "docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md",
            "docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md",
            "docs/plans/tonesoul_evidence_followup_candidates_2026-03-29.md",
        ],
    },
    {
        "id": "subject_refresh_boundaries",
        "label": "Subject Refresh Boundaries",
        "description": "boundary aids for deciding when hot-state evidence may refresh subject snapshots without inflating durable identity",
        "authority_role": "boundary_contract",
        "use_when": "when writing, reviewing, or proposing heuristics around subject_snapshot refresh and promotion limits",
        "read_order": 9,
        "files": [
            "docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md",
        ],
    },
    {
        "id": "control_plane_discipline",
        "label": "Control Plane Discipline",
        "description": "readiness, task-track, and plan-delta discipline surfaces for coordinating work before and during execution",
        "authority_role": "discipline_contract",
        "use_when": "when the question is whether a task is ready, what track it belongs to, or how plan changes should be recorded",
        "read_order": 10,
        "files": [
            "docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md",
            "docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md",
            "docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md",
            "docs/plans/tonesoul_control_plane_followup_candidates_2026-03-28.md",
        ],
    },
    {
        "id": "observable_shell_and_axiom_boundaries",
        "label": "Observable-Shell And Axiom Boundaries",
        "description": "boundary aids for epistemic honesty about opacity and for challenging axiom claims without silently rewriting the constitution",
        "authority_role": "boundary_contract",
        "use_when": "when an agent is about to overclaim auditability of hidden reasoning or repeat an axiom without checking what would weaken it",
        "read_order": 11,
        "files": [
            "docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md",
            "docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md",
            "docs/plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md",
        ],
    },
    {
        "id": "council_deliberation_discipline",
        "label": "Council Deliberation Discipline",
        "description": "discipline aids for preserving dissent, replaying verdicts honestly, and matching deliberation depth to task stakes",
        "authority_role": "discipline_contract",
        "use_when": "when a council result needs bounded dossier extraction, minority preservation, or mode-depth guidance without mutating runtime behavior from prose alone",
        "read_order": 12,
        "files": [
            "docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md",
            "docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md",
            "docs/plans/tonesoul_council_followup_candidates_2026-03-28.md",
        ],
    },
    {
        "id": "continuity_import_and_receiver_discipline",
        "label": "Continuity Import And Receiver Discipline",
        "description": "receiver-side continuity aids for deciding what may be acknowledged, applied, promoted, or discounted by decay across packet, handoff, and subject surfaces",
        "authority_role": "discipline_contract",
        "use_when": "when the question is not merely what should continue, but what a later agent may safely import from continuity surfaces and how long that import remains fresh",
        "read_order": 13,
        "files": [
            "docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md",
            "docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md",
            "docs/architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md",
            "docs/plans/tonesoul_continuity_followup_candidates_2026-03-29.md",
        ],
    },
    {
        "id": "council_realism_and_calibration",
        "label": "Council Realism And Calibration",
        "description": "honesty and adoption aids for separating perspective plurality from real independence, and descriptive confidence from calibrated confidence",
        "authority_role": "boundary_contract",
        "use_when": "when describing how real the current council is, what its confidence numbers actually mean, or which bounded adversarial upgrades are safe to consider next",
        "read_order": 14,
        "files": [
            "docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md",
            "docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md",
            "docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md",
            "docs/plans/tonesoul_council_realism_followup_candidates_2026-03-29.md",
        ],
    },
    {
        "id": "context_continuity_adoption",
        "label": "Context Continuity Adoption",
        "description": "adoption aid for deciding what structure should continue across sessions, tasks, agents, and models without turning handoff memory into hidden truth",
        "authority_role": "adoption_map",
        "use_when": "when the question is not merely how to hand off hot state, but what continuity discipline ToneSoul should adopt or defer",
        "read_order": 15,
        "files": [
            "docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md",
        ],
    },
    {
        "id": "prompt_discipline_skeleton",
        "label": "Prompt Discipline",
        "description": "prompt-side discipline aids for separating goal, priority, confidence, recovery, compression, receiver instructions, and practical task-shaped variants before building extraction or transfer prompts",
        "authority_role": "discipline_contract",
        "use_when": "when the question is not what should be transferred, but how the prompt that extracts or transfers it should be structured",
        "read_order": 16,
        "files": [
            "docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md",
            "docs/architecture/TONESOUL_PROMPT_VARIANTS.md",
            "docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md",
        ],
    },
    {
        "id": "prompt_surface_topology_and_adoption",
        "label": "Prompt Surface Topology And Adoption",
        "description": "topology and adoption aids that classify which live prompt families are already aligned, which are the next short board, and which should remain specialized",
        "authority_role": "adoption_map",
        "use_when": "when the question is not how prompt discipline works in theory, but which concrete prompt families should be adopted next and which should stay untouched",
        "read_order": 17,
        "files": [
            "docs/architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md",
            "docs/architecture/TONESOUL_PROMPT_SURFACE_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_PROMPT_SURFACE_TOPOLOGY_MAP.md",
            "docs/plans/tonesoul_prompt_adoption_followup_candidates_2026-03-29.md",
        ],
    },
    {
        "id": "reality_alignment_and_render_boundaries",
        "label": "Reality Alignment And Render Boundaries",
        "description": "doc-reality aids that distinguish live entry surfaces from stale assumptions, separate file-layer truth from terminal noise, and keep directory counts reproducible",
        "authority_role": "doc_reality_aid",
        "use_when": "when entry routing, document counts, or encoding reports may have drifted from the current repo state and you need a measured baseline before repeating them",
        "read_order": 18,
        "files": [
            "docs/architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md",
            "docs/architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md",
            "docs/architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md",
        ],
    },
    {
        "id": "successor_continuity_and_hot_memory",
        "label": "Successor Continuity And Hot Memory",
        "description": "successor-facing contracts and residue notes that keep hot-memory layering, source precedence, and sidecar retirement aligned with the live runtime/readout story",
        "authority_role": "successor_contract",
        "use_when": "when a later agent needs the active hot-memory and successor-collaboration story without reopening retired sidecar theories",
        "read_order": 19,
        "files": [
            "docs/architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md",
            "docs/architecture/TONESOUL_LOW_DRIFT_ANCHOR_SOURCE_PRECEDENCE_CONTRACT.md",
            "docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md",
            "docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md",
            "docs/plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md",
            "docs/plans/tonesoul_successor_sidecar_residue_triage_2026-04-02.md",
        ],
    },
    {
        "id": "research_driven_memory_interop_and_knowledge_layer",
        "label": "Research-Driven Memory Interop And Knowledge Layer",
        "description": "repo-native bridge contracts for cross-agent consumer parity, Claude-compatible first-hop entry, future knowledge-layer separation, bounded launch-health trend posture, and bounded internal-state observability",
        "authority_role": "interop_contract",
        "use_when": "when the question is how different agent shells should read the same memory surfaces, where future retrieval belongs, how launch-health readouts should stay descriptive without fake forecasting, or how internal-state pressure may be externalized without selfhood inflation",
        "read_order": 20,
        "files": [
            "docs/architecture/TONESOUL_CROSS_AGENT_MEMORY_CONSUMER_CONTRACT.md",
            "docs/architecture/TONESOUL_CLAUDE_COMPATIBLE_ENTRY_ADAPTER_CONTRACT.md",
            "docs/architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_LAUNCH_HEALTH_TREND_READOUT_CONTRACT.md",
            "docs/architecture/TONESOUL_INTERNAL_STATE_OBSERVABILITY_REALITY_CHECK_CONTRACT.md",
            "docs/architecture/TONESOUL_SURFACE_VERSIONING_AND_CONSUMER_LINEAGE_CONTRACT.md",
            "docs/architecture/TONESOUL_KNOWLEDGE_LAYER_SOURCE_TAXONOMY_AND_PARKING_CONTRACT.md",
            "docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md",
            "docs/architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md",
            "docs/plans/tonesoul_research_lines_and_memory_interop_program_2026-04-06.md",
        ],
    },
    {
        "id": "bounded_self_improvement_loop",
        "label": "Bounded Self-Improvement Loop",
        "description": "bounded improvement-loop surfaces that define how ToneSoul may propose, evaluate, and promote operator/runtime improvements without crossing governance, identity, or hot-memory transport boundaries",
        "authority_role": "improvement_contract",
        "use_when": "when the question is how ToneSoul may safely improve operator/runtime surfaces, where experiment lineage belongs, which mutation classes remain forbidden or human-gated in v0, or how trial outcomes may surface without becoming runtime truth",
        "read_order": 21,
        "files": [
            "docs/architecture/TONESOUL_SELF_IMPROVEMENT_LOOP_V0_SPEC.md",
            "docs/architecture/TONESOUL_SELF_IMPROVEMENT_EVALUATOR_HARNESS_CONTRACT.md",
            "docs/architecture/TONESOUL_EXPERIMENT_REGISTRY_AND_LINEAGE_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_BOUNDED_MUTATION_SPACE_CONTRACT.md",
            "docs/architecture/TONESOUL_ANALYZER_AND_PROMOTION_GATE_CONTRACT.md",
            "docs/architecture/TONESOUL_PROMOTION_READY_RESULT_SURFACE_CONTRACT.md",
            "docs/plans/tonesoul_self_improvement_loop_v0_program_2026-04-06.md",
        ],
    },
    {
        "id": "entry_simplification_and_lineage_routing",
        "label": "Entry Simplification And Lineage Routing",
        "description": "cleanup and routing aids for audience entry paths, historical-versus-current surface distinction, safe simplification moves, and bounded docs cleanup sequencing",
        "authority_role": "doc_cleanup_aid",
        "use_when": "when the problem is how a reader should enter, what should remain visible as lineage, or which cleanup moves are safe without flattening authority",
        "read_order": 22,
        "files": [
            "docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md",
            "docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md",
            "docs/architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md",
            "docs/plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md",
        ],
    },
    {
        "id": "doc_governance",
        "label": "Documentation Governance",
        "description": "naming, zoning, and convergence planning surfaces",
        "authority_role": "doc_governance",
        "use_when": "when retrieval quality, metadata posture, or naming collisions are the problem",
        "read_order": 23,
        "files": [
            "docs/DOCS_INFORMATION_ARCHITECTURE_v1.md",
            "docs/DOCS_CLASSIFICATION_LEDGER_v1.md",
            "docs/FILE_PURPOSE_MAP.md",
            "docs/status/doc_convergence_inventory_latest.json",
            "docs/plans/doc_convergence_cleanup_plan_2026-03-22.md",
        ],
    },
    {
        "id": "convergence_contracts",
        "label": "Convergence Contracts",
        "description": "ownership and divergence boundaries for duplicate-like surfaces",
        "authority_role": "boundary_contract",
        "use_when": "when two similar-looking lanes need explicit ownership or split-brain control",
        "read_order": 24,
        "files": [
            "docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md",
            "docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md",
            "docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md",
            "docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md",
        ],
    },
    {
        "id": "generated_status",
        "label": "Generated Status",
        "description": "machine-readable current posture for convergence-related lanes",
        "authority_role": "generated_status",
        "use_when": "when current machine-readable posture matters more than prose explanation",
        "read_order": 25,
        "files": [
            "docs/status/doc_convergence_inventory_latest.json",
            "docs/status/basename_divergence_distillation_latest.json",
            "docs/status/private_memory_shadow_latest.json",
            "docs/status/paradox_fixture_ownership_latest.json",
            "docs/status/engineering_mirror_ownership_latest.json",
            "docs/status/claim_authority_latest.json",
        ],
    },
]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_inventory(repo_root: Path) -> dict[str, Any]:
    inventory_path = repo_root / INVENTORY_PATH
    if not inventory_path.exists():
        return {"missing_metadata": {"purpose": [], "date_hint": []}}
    return json.loads(inventory_path.read_text(encoding="utf-8"))


def build_report(repo_root: Path) -> dict[str, Any]:
    inventory = _read_inventory(repo_root)
    missing_purpose = set(inventory.get("missing_metadata", {}).get("purpose", []))
    missing_date = set(inventory.get("missing_metadata", {}).get("date_hint", []))

    groups: list[dict[str, Any]] = []
    total_tracked = 0
    total_complete = 0
    missing_files: list[str] = []

    for group in GROUPS:
        file_rows = []
        for rel_path in group["files"]:
            total_tracked += 1
            exists = (repo_root / rel_path).exists()
            has_purpose = rel_path not in missing_purpose if exists else False
            has_date = rel_path not in missing_date if exists else False
            metadata_complete = exists and has_purpose and has_date
            if metadata_complete:
                total_complete += 1
            if exists and not metadata_complete:
                missing_files.append(rel_path)
            file_rows.append(
                {
                    "path": rel_path,
                    "exists": exists,
                    "has_purpose": has_purpose,
                    "has_date": has_date,
                    "metadata_complete": metadata_complete,
                }
            )

        groups.append(
            {
                "id": group["id"],
                "label": group["label"],
                "description": group["description"],
                "authority_role": group["authority_role"],
                "use_when": group["use_when"],
                "read_order": group["read_order"],
                "files": file_rows,
                "tracked_count": len(file_rows),
                "metadata_complete_count": sum(1 for row in file_rows if row["metadata_complete"]),
            }
        )

    generated_status_group = next(group for group in groups if group["id"] == "generated_status")
    primary_status_line = (
        "doc_authority_structure | "
        f"groups={len(groups)} tracked={total_tracked} metadata_complete={total_complete} "
        f"metadata_missing={len(missing_files)}"
    )
    runtime_status_line = (
        "doc_retrieval_order=entrypoint_to_operational_to_canonical_to_deep_map_to_interpretive_to_boundary_aids_to_control_plane | "
        f"generated_status_lane={len(generated_status_group['files'])}"
    )
    artifact_policy_status_line = "structure_mode=retrieval_oriented | authority_roles=explicit | generated_status_preferred_for_current_state"

    return {
        "generated_at": _iso_now(),
        "inventory_path": INVENTORY_PATH.as_posix(),
        "metrics": {
            "group_count": len(groups),
            "tracked_file_count": total_tracked,
            "metadata_complete_count": total_complete,
            "metadata_missing_count": len(missing_files),
        },
        "groups": groups,
        "missing_metadata_files": sorted(missing_files),
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Documentation Authority Structure Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Groups"])
    for group in payload["groups"]:
        lines.append(
            f"- `{group['label']}` tracked=`{group['tracked_count']}` "
            f"metadata_complete=`{group['metadata_complete_count']}`"
        )
        lines.append(f"  - description: {group['description']}")
        lines.append(f"  - authority_role: {group['authority_role']}")
        lines.append(f"  - use_when: {group['use_when']}")
        lines.append(f"  - read_order: {group['read_order']}")
        for row in group["files"]:
            lines.append(
                f"  - `{row['path']}` exists=`{str(row['exists']).lower()}` "
                f"purpose=`{str(row['has_purpose']).lower()}` "
                f"date=`{str(row['has_date']).lower()}`"
            )

    lines.extend(["", "## Missing Metadata Files"])
    for rel_path in payload["missing_metadata_files"]:
        lines.append(f"- `{rel_path}`")

    return "\n".join(lines) + "\n"


def render_mermaid(payload: dict[str, Any]) -> str:
    lines = ["graph TD", '    root["ToneSoul Documentation Authority"]']
    for group in payload["groups"]:
        group_id = group["id"]
        lines.append(f'    root --> {group_id}["{group["label"]}"]')
        for index, row in enumerate(group["files"], start=1):
            node_id = f"{group_id}_{index}"
            lines.append(f'    {group_id} --> {node_id}["{Path(row["path"]).name}"]')
    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render the documentation authority structure map."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _write(out_dir / MERMAID_FILENAME, render_mermaid(payload))
    print(
        json.dumps(
            {
                "ok": True,
                "artifacts": {
                    "json": f"{args.out_dir}/{JSON_FILENAME}",
                    "markdown": f"{args.out_dir}/{MARKDOWN_FILENAME}",
                    "mermaid": f"{args.out_dir}/{MERMAID_FILENAME}",
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
