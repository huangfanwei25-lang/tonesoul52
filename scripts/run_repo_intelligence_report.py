#!/usr/bin/env python3
"""Publish a compact repo-intelligence handoff artifact for later agents."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.subjectivity_handoff import build_handoff_surface  # noqa: E402

JSON_FILENAME = "repo_intelligence_latest.json"
MARKDOWN_FILENAME = "repo_intelligence_latest.md"

PROTECTED_FILES: tuple[str, ...] = (
    "AGENTS.md",
    "HANDOFF.md",
    ".env",
    ".gitignore",
    "MEMORY.md",
)
WATCHED_DIRECTORIES: tuple[str, ...] = (
    "skills/",
    ".agent/",
    ".agents/",
)
RECOMMENDED_SURFACES: tuple[dict[str, str], ...] = (
    {
        "name": "repo_healthcheck",
        "path": "docs/status/repo_healthcheck_latest.json",
        "role": "repo_governance",
        "description": "Top repo-level blocking posture and compact runtime previews.",
    },
    {
        "name": "repo_semantic_atlas",
        "path": "docs/status/repo_semantic_atlas_latest.json",
        "role": "semantic_memory",
        "description": "Human-rememberable aliases, semantic neighborhoods, and domain-level nerve map.",
    },
    {
        "name": "agent_integrity",
        "path": "docs/status/agent_integrity_latest.json",
        "role": "integrity_governance",
        "description": "Protected-file hash contract, embedded metadata drift, and watched-directory posture.",
    },
    {
        "name": "repo_governance_settlement",
        "path": "docs/status/repo_governance_settlement_latest.json",
        "role": "branch_settlement",
        "description": "Branch-movement and worktree settlement readback.",
    },
    {
        "name": "runtime_source_change_groups",
        "path": "docs/status/runtime_source_change_groups_latest.json",
        "role": "review_scope",
        "description": "Dirty review lanes and recommended runtime grouping.",
    },
    {
        "name": "true_verification_weekly",
        "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
        "role": "weekly_runtime",
        "description": "Host-facing weekly runtime posture and session lineage.",
    },
    {
        "name": "scribe_status",
        "path": "docs/status/scribe_status_latest.json",
        "role": "chronicle_runtime",
        "description": "Latest Scribe chronicle/companion posture.",
    },
)
EXTERNAL_TOOL_POLICY = {
    "adoption_mode": "sidecar_only",
    "main_repo_install_allowed": False,
    "mirror_clone_required": True,
    "hook_registration_allowed": False,
    "protected_file_mutation_allowed": False,
}


def _load_json_document(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _protected_file_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for relative_path in PROTECTED_FILES:
        snapshots.append(
            {
                "path": relative_path,
                "exists": (repo_root / relative_path).exists(),
            }
        )
    return snapshots


def _watched_directory_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for relative_path in WATCHED_DIRECTORIES:
        snapshots.append(
            {
                "path": relative_path,
                "exists": (repo_root / relative_path).exists(),
            }
        )
    return snapshots


def _recommended_surface_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for item in RECOMMENDED_SURFACES:
        snapshots.append(
            {
                "name": item["name"],
                "path": item["path"],
                "role": item["role"],
                "description": item["description"],
                "available": (repo_root / item["path"]).exists(),
            }
        )
    return snapshots


def _semantic_memory_handoff(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / "docs" / "status" / "repo_semantic_atlas_latest.json"
    payload = _load_json_document(path)
    if not isinstance(payload, dict):
        return None

    handoff = payload.get("handoff")
    search_contract = payload.get("search_contract")
    retrieval_protocol = ""
    preferred_first_neighborhood = ""
    chronicle_collection_path = ""
    if isinstance(handoff, dict):
        retrieval_protocol = str(handoff.get("retrieval_protocol") or "").strip()
        preferred_first_neighborhood = str(
            handoff.get("preferred_first_neighborhood") or ""
        ).strip()
        chronicle_collection_path = str(handoff.get("chronicle_collection_path") or "").strip()

    retrieval_rule_ids: list[str] = []
    if isinstance(search_contract, dict):
        for item in search_contract.get("retrieval_protocol") or []:
            if not isinstance(item, dict):
                continue
            rule_id = str(item.get("id") or "").strip()
            if rule_id:
                retrieval_rule_ids.append(rule_id)

    return {
        "path": "docs/status/repo_semantic_atlas_latest.json",
        "retrieval_protocol": retrieval_protocol,
        "preferred_first_neighborhood": preferred_first_neighborhood,
        "chronicle_collection_path": chronicle_collection_path,
        "retrieval_rule_ids": retrieval_rule_ids,
        "primary_status_line": str(payload.get("primary_status_line") or "").strip(),
        "runtime_status_line": str(payload.get("runtime_status_line") or "").strip(),
        "artifact_policy_status_line": str(
            payload.get("artifact_policy_status_line") or ""
        ).strip(),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    protected_files = _protected_file_snapshot(repo_root)
    watched_directories = _watched_directory_snapshot(repo_root)
    recommended_surfaces = _recommended_surface_snapshot(repo_root)
    semantic_memory_handoff = _semantic_memory_handoff(repo_root)
    available_surface_count = sum(1 for item in recommended_surfaces if bool(item["available"]))
    first_surface = recommended_surfaces[0]["path"] if recommended_surfaces else ""
    semantic_protocol = ""
    semantic_first_neighborhood = ""
    if isinstance(semantic_memory_handoff, dict):
        semantic_protocol = str(semantic_memory_handoff.get("retrieval_protocol") or "").strip()
        semantic_first_neighborhood = str(
            semantic_memory_handoff.get("preferred_first_neighborhood") or ""
        ).strip()
    primary_status_line = (
        "repo_intelligence_ready | "
        f"available_surfaces={available_surface_count}/{len(recommended_surfaces)} "
        f"protected_files={len(protected_files)} watched_dirs={len(watched_directories)} "
        "adoption=sidecar_only"
    )
    runtime_status_line = (
        "entrypoints | "
        "repo=repo_healthcheck_latest.json "
        "atlas=repo_semantic_atlas_latest.json "
        "integrity=agent_integrity_latest.json "
        "settlement=repo_governance_settlement_latest.json "
        "review=runtime_source_change_groups_latest.json "
        "weekly=true_verification_task_status_latest.json "
        "scribe=scribe_status_latest.json "
        f"semantic_protocol={semantic_protocol or 'unavailable'} "
        f"semantic_first={semantic_first_neighborhood or 'unavailable'}"
    )
    artifact_policy_status_line = (
        "external_repo_intelligence=sidecar_only | "
        "main_repo_install=no hooks=no protected_files=no"
    )
    return {
        "generated_at": _iso_now(),
        "status": "ready",
        "protected_files": protected_files,
        "watched_directories": watched_directories,
        "recommended_surfaces": recommended_surfaces,
        "summary": {
            "protected_file_count": len(protected_files),
            "watched_directory_count": len(watched_directories),
            "recommended_surface_count": len(recommended_surfaces),
            "available_surface_count": available_surface_count,
            "missing_surface_count": len(recommended_surfaces) - available_surface_count,
            "semantic_memory_connected": bool(semantic_memory_handoff),
        },
        "external_tool_policy": dict(EXTERNAL_TOOL_POLICY),
        "semantic_memory_handoff": semantic_memory_handoff,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": build_handoff_surface(
            queue_shape="repo_intelligence_ready",
            requires_operator_action=False,
            status_lines=[
                primary_status_line,
                runtime_status_line,
                artifact_policy_status_line,
            ],
            extra_fields={
                "preferred_first_surface": first_surface,
                "main_repo_install_allowed": EXTERNAL_TOOL_POLICY["main_repo_install_allowed"],
                "mirror_clone_required": EXTERNAL_TOOL_POLICY["mirror_clone_required"],
                "semantic_retrieval_protocol": semantic_protocol,
                "semantic_preferred_neighborhood": semantic_first_neighborhood,
            },
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    handoff = payload.get("handoff") or {}
    lines = [
        "# Repo Intelligence Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- status: {payload['status']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## External Tool Policy",
        f"- adoption_mode: `{payload['external_tool_policy']['adoption_mode']}`",
        "- main_repo_install_allowed: "
        f"`{str(payload['external_tool_policy']['main_repo_install_allowed']).lower()}`",
        "- mirror_clone_required: "
        f"`{str(payload['external_tool_policy']['mirror_clone_required']).lower()}`",
        "- hook_registration_allowed: "
        f"`{str(payload['external_tool_policy']['hook_registration_allowed']).lower()}`",
        "- protected_file_mutation_allowed: "
        f"`{str(payload['external_tool_policy']['protected_file_mutation_allowed']).lower()}`",
        "",
        "## Recommended Surfaces",
    ]
    for item in payload["recommended_surfaces"]:
        availability = "yes" if item["available"] else "no"
        lines.extend(
            [
                f"- `{item['name']}`",
                f"  - path: `{item['path']}`",
                f"  - role: `{item['role']}`",
                f"  - available: `{availability}`",
                f"  - description: {item['description']}",
            ]
        )

    lines.append("")
    lines.append("## Semantic Retrieval Protocol")
    semantic_memory_handoff = payload.get("semantic_memory_handoff")
    if isinstance(semantic_memory_handoff, dict):
        lines.append(f"- path: `{semantic_memory_handoff.get('path', '')}`")
        lines.append(
            "- retrieval_protocol: " f"`{semantic_memory_handoff.get('retrieval_protocol', '')}`"
        )
        lines.append(
            "- preferred_first_neighborhood: "
            f"`{semantic_memory_handoff.get('preferred_first_neighborhood', '')}`"
        )
        lines.append(
            "- chronicle_collection_path: "
            f"`{semantic_memory_handoff.get('chronicle_collection_path', '')}`"
        )
        retrieval_rule_ids = list(semantic_memory_handoff.get("retrieval_rule_ids") or [])
        if retrieval_rule_ids:
            lines.append(
                "- retrieval_rule_ids: "
                + ", ".join(f"`{rule_id}`" for rule_id in retrieval_rule_ids)
            )
        if str(semantic_memory_handoff.get("primary_status_line") or "").strip():
            lines.append(
                "- primary_status_line: "
                f"`{semantic_memory_handoff.get('primary_status_line', '')}`"
            )
        if str(semantic_memory_handoff.get("runtime_status_line") or "").strip():
            lines.append(
                "- runtime_status_line: "
                f"`{semantic_memory_handoff.get('runtime_status_line', '')}`"
            )
        if str(semantic_memory_handoff.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{semantic_memory_handoff.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Protected Files")
    for item in payload["protected_files"]:
        lines.append(f"- `{item['path']}` (exists: `{str(item['exists']).lower()}`)")

    lines.append("")
    lines.append("## Watched Directories")
    for item in payload["watched_directories"]:
        lines.append(f"- `{item['path']}` (exists: `{str(item['exists']).lower()}`)")

    lines.extend(
        [
            "",
            "## Handoff",
            f"- queue_shape: `{handoff.get('queue_shape', '')}`",
            "- requires_operator_action: "
            f"`{str(handoff.get('requires_operator_action', False)).lower()}`",
            f"- preferred_first_surface: `{handoff.get('preferred_first_surface', '')}`",
            f"- semantic_retrieval_protocol: `{handoff.get('semantic_retrieval_protocol', '')}`",
            f"- semantic_preferred_neighborhood: `{handoff.get('semantic_preferred_neighborhood', '')}`",
            f"- primary_status_line: `{handoff.get('primary_status_line', '')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish a compact repo-intelligence artifact for later agents."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to inspect. Defaults to current directory.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Directory where the latest repo-intelligence artifacts are written.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
