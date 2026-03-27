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
        "id": "doc_governance",
        "label": "Documentation Governance",
        "description": "naming, zoning, and convergence planning surfaces",
        "authority_role": "doc_governance",
        "use_when": "when retrieval quality, metadata posture, or naming collisions are the problem",
        "read_order": 8,
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
        "read_order": 9,
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
        "read_order": 10,
        "files": [
            "docs/status/doc_convergence_inventory_latest.json",
            "docs/status/basename_divergence_distillation_latest.json",
            "docs/status/private_memory_shadow_latest.json",
            "docs/status/paradox_fixture_ownership_latest.json",
            "docs/status/engineering_mirror_ownership_latest.json",
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
        "doc_retrieval_order=entrypoint_to_operational_to_canonical_to_deep_map_to_interpretive | "
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
