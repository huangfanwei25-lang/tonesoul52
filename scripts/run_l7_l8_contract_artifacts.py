#!/usr/bin/env python3
"""Generate machine-readable L7/L8 contract artifacts for ToneSoul."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

L7_JSON_FILENAME = "l7_retrieval_contract_latest.json"
L7_MARKDOWN_FILENAME = "l7_retrieval_contract_latest.md"
L8_JSON_FILENAME = "l8_distillation_boundary_latest.json"
L8_MARKDOWN_FILENAME = "l8_distillation_boundary_latest.md"

L7_CONTRACT_PATH = "docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md"
L8_CONTRACT_PATH = "docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md"
DATASET_SCHEMA_PATH = "spec/governance/adapter_dataset_record_v1.schema.json"
DATASET_EXAMPLE_PATH = "spec/governance/adapter_dataset_record_v1.example.json"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_repo_path(value: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def _load_json(repo_root: Path, repo_path: str) -> dict[str, Any]:
    path = repo_root / repo_path
    return json.loads(path.read_text(encoding="utf-8"))


def build_l7_payload() -> dict[str, Any]:
    surfaces = [
        {
            "id": "architecture_anchor",
            "authority_rank": 1,
            "use_for": "north-star architecture, layer meaning, repo-wide interpretation",
            "examples": [
                "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md",
                "docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md",
            ],
        },
        {
            "id": "boundary_map",
            "authority_rank": 2,
            "use_for": "surface separation and authority disambiguation",
            "examples": [
                "docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md",
                L7_CONTRACT_PATH,
            ],
        },
        {
            "id": "status_artifact",
            "authority_rank": 3,
            "use_for": "latest generated repo state, machine-readable operational truth",
            "examples": [
                "docs/status/tonesoul_knowledge_graph_latest.md",
                "docs/status/changed_surface_checks_latest.md",
                "docs/status/repo_healthcheck_latest.json",
            ],
        },
        {
            "id": "research_note",
            "authority_rank": 4,
            "use_for": "external evidence and non-canonical comparison",
            "examples": [
                "docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md",
            ],
        },
        {
            "id": "implementation_source",
            "authority_rank": 5,
            "use_for": "actual runtime behavior when prose is insufficient",
            "examples": [
                "tonesoul/unified_pipeline.py",
                "scripts/run_changed_surface_checks.py",
            ],
        },
        {
            "id": "verifier",
            "authority_rank": 6,
            "use_for": "mechanical truth checks when drift risk is high",
            "examples": [
                "scripts/verify_docs_consistency.py",
                "scripts/verify_protected_paths.py",
                "scripts/run_changed_surface_checks.py",
            ],
        },
    ]

    question_routes = [
        {
            "question_type": "architecture_meaning",
            "open_first": "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md",
            "open_second": "docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md",
            "then": "implementation_source",
        },
        {
            "question_type": "knowledge_surface_authority",
            "open_first": "docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md",
            "open_second": L7_CONTRACT_PATH,
            "then": "status_artifact",
        },
        {
            "question_type": "latest_repo_state",
            "open_first": "docs/status/repo_healthcheck_latest.json",
            "open_second": "docs/status/tonesoul_knowledge_graph_latest.md",
            "then": "verifier",
        },
        {
            "question_type": "change_validation",
            "open_first": "scripts/run_changed_surface_checks.py",
            "open_second": "docs/status/changed_surface_checks_latest.md",
            "then": "verifier",
        },
        {
            "question_type": "external_design_influence",
            "open_first": "docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md",
            "open_second": "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md",
            "then": "human_review",
        },
    ]

    verifier_checks = [
        {
            "id": "protected_paths",
            "command": "python scripts/verify_protected_paths.py --repo-root . --strict",
            "use_when": "sensitive files, memory lanes, or protected docs are touched",
        },
        {
            "id": "docs_consistency",
            "command": "python scripts/verify_docs_consistency.py --repo-root .",
            "use_when": "authority docs, status surfaces, or repo-facing descriptions changed",
        },
        {
            "id": "changed_surface_checks",
            "command": "python scripts/run_changed_surface_checks.py --repo-root .",
            "use_when": "you need the check plan for current changes instead of guessing",
        },
    ]

    stop_reading_triggers = [
        "protected paths are involved",
        "the question is about what is true right now",
        "the claim can be checked mechanically",
        "status artifacts and prose may have drifted apart",
        "the task is code-change oriented and a verifier already maps the changed surface",
    ]

    return {
        "generated_at": _iso_now(),
        "contract_version": "v1",
        "canonical_contract": L7_CONTRACT_PATH,
        "machine_readable_mirror": f"docs/status/{L7_JSON_FILENAME}",
        "default_reading_order": [
            "architecture_anchor",
            "boundary_map",
            "status_artifact",
            "research_note",
            "implementation_source",
            "verifier",
        ],
        "surfaces": surfaces,
        "question_routes": question_routes,
        "verifier_checks": verifier_checks,
        "stop_reading_triggers": stop_reading_triggers,
        "metrics": {
            "surface_count": len(surfaces),
            "question_route_count": len(question_routes),
            "verifier_count": len(verifier_checks),
        },
    }


def build_l8_payload(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    schema = _load_json(repo_root, DATASET_SCHEMA_PATH)
    example = _load_json(repo_root, DATASET_EXAMPLE_PATH)
    properties = schema.get("properties", {})

    allowed_classes = [
        {
            "id": "public_safe_behavior_trace",
            "allowed": True,
            "examples": [
                "verifier-first routing pattern",
                "public governance posture",
                "safe answer structure",
            ],
        },
        {
            "id": "public_philosophical_prior",
            "allowed": True,
            "examples": [
                "published axiomatic stance",
                "public semantic-governance posture",
            ],
        },
        {
            "id": "tool_routing_habit",
            "allowed": True,
            "examples": [
                "retrieval-before-long-prompt",
                "verifier-before-claim",
            ],
        },
        {
            "id": "governance_posture",
            "allowed": True,
            "examples": [
                "stable refusal posture",
                "public governance guard behavior",
            ],
        },
        {
            "id": "language_style",
            "allowed": True,
            "examples": [
                "public-facing tone style",
            ],
        },
    ]

    forbidden_surfaces = [
        "private vault memory",
        "raw personal journals",
        "identifiable user facts",
        "deletion-sensitive records",
        "private red-team payload collections",
        "internal security bypass probes",
        "secret thresholds and unpublished guard formulas",
        "unredacted conversation archives",
    ]

    export_gates = [
        {
            "id": "public_safe_review",
            "question": "Is the material safe for irreversible retention?",
        },
        {
            "id": "provenance_review",
            "question": "Can source path and transformation chain be reconstructed?",
        },
        {
            "id": "privacy_review",
            "question": "Has private or identifying detail been removed?",
        },
        {
            "id": "governance_review",
            "question": "Does the trace represent a stable desired behavior?",
        },
        {
            "id": "evaluation_plan",
            "question": "Can the experiment be measured and reversed?",
        },
    ]

    evaluation_dimensions = [
        "governance consistency",
        "verifier pass rate",
        "auditability of training sources",
        "reversibility under drift",
        "public benchmark regression risk",
    ]

    cross_repo_boundary = [
        {
            "repo": "tonesoul52",
            "role": "public engine and contracts",
            "policy": "source of public-safe behavior abstractions only",
        },
        {
            "repo": "ToneSoul-Memory-Vault",
            "role": "private sensitive memory repository",
            "policy": "never a direct training dump; must remain external",
        },
        {
            "repo": "OpenClaw-Memory",
            "role": "public memory substrate experiment",
            "policy": "safe for memory-engineering patterns, not private memory export",
        },
        {
            "repo": "OpenClaw-RL",
            "role": "agentic RL experiment rail",
            "policy": "may consume approved public-safe traces only",
        },
    ]

    return {
        "generated_at": _iso_now(),
        "contract_version": "v1",
        "canonical_contract": L8_CONTRACT_PATH,
        "machine_readable_mirror": f"docs/status/{L8_JSON_FILENAME}",
        "dataset_schema_ref": DATASET_SCHEMA_PATH,
        "dataset_example_ref": DATASET_EXAMPLE_PATH,
        "dataset_required_fields": list(schema.get("required", [])),
        "dataset_property_count": len(properties),
        "allowed_classes": allowed_classes,
        "forbidden_surfaces": forbidden_surfaces,
        "export_gates": export_gates,
        "evaluation_dimensions": evaluation_dimensions,
        "cross_repo_boundary": cross_repo_boundary,
        "example_record_preview": {
            "row_id": example.get("row_id"),
            "behavior_class": example.get("behavior_class"),
            "training_objective": example.get("training_objective"),
        },
        "metrics": {
            "allowed_class_count": len(allowed_classes),
            "forbidden_surface_count": len(forbidden_surfaces),
            "export_gate_count": len(export_gates),
            "evaluation_dimension_count": len(evaluation_dimensions),
        },
    }


def render_l7_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# L7 Retrieval Contract Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- contract_version: {payload['contract_version']}",
        f"- canonical_contract: `{payload['canonical_contract']}`",
        "",
        "## Default Reading Order",
    ]
    for item in payload.get("default_reading_order", []):
        lines.append(f"- `{item}`")

    lines.extend(["", "## Surfaces"])
    for surface in payload.get("surfaces", []):
        lines.append(
            f"- `{surface['id']}` (rank {surface['authority_rank']}): {surface['use_for']}"
        )
        for example in surface.get("examples", []):
            lines.append(f"  - `{example}`")

    lines.extend(["", "## Question Routes"])
    for route in payload.get("question_routes", []):
        lines.append(
            f"- `{route['question_type']}`: first `{route['open_first']}`, then `{route['open_second']}`, then `{route['then']}`"
        )

    lines.extend(["", "## Verifier Checks"])
    for check in payload.get("verifier_checks", []):
        lines.append(f"- `{check['id']}`: `{check['command']}`")
        lines.append(f"  - use_when: {check['use_when']}")

    lines.extend(["", "## Stop Reading Triggers"])
    for trigger in payload.get("stop_reading_triggers", []):
        lines.append(f"- {trigger}")
    return "\n".join(lines) + "\n"


def render_l8_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# L8 Distillation Boundary Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- contract_version: {payload['contract_version']}",
        f"- canonical_contract: `{payload['canonical_contract']}`",
        f"- dataset_schema_ref: `{payload['dataset_schema_ref']}`",
        f"- dataset_example_ref: `{payload['dataset_example_ref']}`",
        "",
        "## Allowed Classes",
    ]
    for item in payload.get("allowed_classes", []):
        lines.append(f"- `{item['id']}`")
        for example in item.get("examples", []):
            lines.append(f"  - `{example}`")

    lines.extend(["", "## Forbidden Surfaces"])
    for surface in payload.get("forbidden_surfaces", []):
        lines.append(f"- {surface}")

    lines.extend(["", "## Export Gates"])
    for gate in payload.get("export_gates", []):
        lines.append(f"- `{gate['id']}`: {gate['question']}")

    lines.extend(["", "## Dataset Required Fields"])
    for field_name in payload.get("dataset_required_fields", []):
        lines.append(f"- `{field_name}`")

    lines.extend(["", "## Evaluation Dimensions"])
    for dimension in payload.get("evaluation_dimensions", []):
        lines.append(f"- {dimension}")
    return "\n".join(lines) + "\n"


def write_outputs(
    *,
    l7_payload: dict[str, Any],
    l8_payload: dict[str, Any],
    output_dir: Path,
    repo_root: Path = REPO_ROOT,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "l7_json": output_dir / L7_JSON_FILENAME,
        "l7_markdown": output_dir / L7_MARKDOWN_FILENAME,
        "l8_json": output_dir / L8_JSON_FILENAME,
        "l8_markdown": output_dir / L8_MARKDOWN_FILENAME,
    }
    paths["l7_json"].write_text(
        json.dumps(l7_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    paths["l7_markdown"].write_text(render_l7_markdown(l7_payload), encoding="utf-8")
    paths["l8_json"].write_text(
        json.dumps(l8_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    paths["l8_markdown"].write_text(render_l8_markdown(l8_payload), encoding="utf-8")
    return {
        key: _normalize_repo_path(str(path.relative_to(repo_root))) for key, path in paths.items()
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate L7/L8 contract artifacts.")
    parser.add_argument(
        "--output-dir",
        default="docs/status",
        help="Directory for generated artifacts (default: docs/status).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    l7_payload = build_l7_payload()
    l8_payload = build_l8_payload(REPO_ROOT)
    artifacts = write_outputs(
        l7_payload=l7_payload,
        l8_payload=l8_payload,
        output_dir=REPO_ROOT / args.output_dir,
        repo_root=REPO_ROOT,
    )
    print(json.dumps({"ok": True, "artifacts": artifacts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
