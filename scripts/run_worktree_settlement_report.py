"""Generate a non-destructive settlement plan for the current dirty worktree."""

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

import scripts.plan_commit_attribution_base_switch as base_switch_planner  # noqa: E402
import scripts.run_refreshable_artifact_report as refreshable_report  # noqa: E402
from tonesoul.status_alignment import build_dream_weekly_alignment_line  # noqa: E402

JSON_FILENAME = "worktree_settlement_latest.json"
MARKDOWN_FILENAME = "worktree_settlement_latest.md"

LANE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "refreshable_artifacts",
        "title": "Refreshable Artifacts",
        "categories": ["generated_status", "reports"],
        "goal": "Separate reproducible outputs from authored source edits before any branch movement.",
        "recommended_actions": [
            "Do not let generated status snapshots and derived reports drive branch-base decisions.",
            "Refresh, discard, or restage reproducible artifacts only after the authored source set is stable.",
        ],
        "exit_criteria": "No remaining dirty paths in generated outputs or reports, or an explicit decision to preserve them.",
    },
    {
        "name": "private_memory_review",
        "title": "Private Memory Review",
        "categories": ["memory"],
        "goal": "Review private memory artifacts outside the public-branch settlement path.",
        "recommended_actions": [
            "Treat raw memory artifacts as private-evolution evidence, not ordinary public repo edits.",
            "Mirror only public-safe learnings into task/reflection/status artifacts when needed.",
        ],
        "exit_criteria": "Private memory changes are either archived to the private path or consciously excluded from branch movement.",
    },
    {
        "name": "public_contract_docs",
        "title": "Public Contract Docs",
        "categories": ["docs", "spec"],
        "goal": "Group public documentation and spec edits by owning implementation phase.",
        "recommended_actions": [
            "Settle docs and specs after generated artifacts are separated, but before final branch movement.",
            "Keep public docs aligned with the actual runtime and governance artifacts they describe.",
        ],
        "exit_criteria": "Docs/spec edits are paired with their implementation or intentionally deferred.",
    },
    {
        "name": "runtime_source_changes",
        "title": "Runtime Source Changes",
        "categories": ["scripts", "tests", "tonesoul", "runtime_apps", "skills", "tooling"],
        "goal": "Review high-signal code and contract changes as cohesive change groups.",
        "recommended_actions": [
            "Keep tests paired with the code paths they validate instead of settling them independently.",
            "Treat scripts, runtime apps, and core `tonesoul` changes as the public source-of-truth lane.",
        ],
        "exit_criteria": "Core source edits are grouped into reviewable changesets with matching tests and docs.",
    },
    {
        "name": "experimental_misc_review",
        "title": "Experimental and Misc Review",
        "categories": ["experiments", "repo_misc", "unknown"],
        "goal": "Resolve root-level drift and experimental assets deliberately instead of letting them hitchhike.",
        "recommended_actions": [
            "Decide whether experimental files belong to the public repo, a follow-up branch, or should be dropped.",
            "Review uncategorized root-level files manually before any git history movement.",
        ],
        "exit_criteria": "Experimental and miscellaneous paths have an explicit keep/defer/drop decision.",
    },
]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _resolve_path(repo_root: Path, value: str) -> Path:
    raw = Path(str(value).strip())
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def _group_entries(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        category = str(entry.get("category") or "unknown")
        grouped.setdefault(category, []).append(entry)
    return grouped


def _category_summary(entries: list[dict[str, Any]], sample_limit: int) -> dict[str, Any]:
    return {
        "count": len(entries),
        "staged_count": sum(1 for entry in entries if entry.get("staged")),
        "unstaged_count": sum(1 for entry in entries if entry.get("unstaged")),
        "untracked_count": sum(1 for entry in entries if entry.get("untracked")),
        "sample_paths": [str(entry.get("path") or "") for entry in entries[:sample_limit]],
    }


def _build_lane(
    lane_definition: dict[str, Any],
    grouped_entries: dict[str, list[dict[str, Any]]],
    sample_limit: int,
) -> dict[str, Any]:
    category_payloads: list[dict[str, Any]] = []
    lane_entries: list[dict[str, Any]] = []
    for category in lane_definition["categories"]:
        entries = list(grouped_entries.get(category) or [])
        if not entries:
            continue
        category_payloads.append(
            {
                "category": category,
                **_category_summary(entries, sample_limit),
            }
        )
        lane_entries.extend(entries)

    return {
        "name": lane_definition["name"],
        "title": lane_definition["title"],
        "active": bool(category_payloads),
        "goal": lane_definition["goal"],
        "categories": category_payloads,
        "entry_count": len(lane_entries),
        "recommended_actions": list(lane_definition["recommended_actions"]),
        "exit_criteria": lane_definition["exit_criteria"],
    }


def _refreshable_handoff_previews(repo_root: Path) -> list[dict[str, str]]:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in previews:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "").strip()
        queue_shape = str(item.get("queue_shape") or "").strip()
        primary_status_line = str(item.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            continue
        preview = {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(item.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(item.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                item.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                item.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(item.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
        problem_route_status_line = str(item.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            preview["problem_route_status_line"] = problem_route_status_line
        problem_route_secondary_labels = str(
            item.get("problem_route_secondary_labels") or ""
        ).strip()
        if problem_route_secondary_labels:
            preview["problem_route_secondary_labels"] = problem_route_secondary_labels
        semantic_retrieval_protocol = str(item.get("semantic_retrieval_protocol") or "").strip()
        if semantic_retrieval_protocol:
            preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
        semantic_preferred_neighborhood = str(
            item.get("semantic_preferred_neighborhood") or ""
        ).strip()
        if semantic_preferred_neighborhood:
            preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
        dream_weekly_alignment_line = str(item.get("dream_weekly_alignment_line") or "").strip()
        if dream_weekly_alignment_line:
            preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
        scribe_status_line = str(item.get("scribe_status_line") or "").strip()
        if scribe_status_line:
            preview["scribe_status_line"] = scribe_status_line
        normalized.append(preview)
    return normalized


def _refreshable_subjectivity_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    preview = payload.get("subjectivity_focus_preview")
    if not isinstance(preview, dict):
        previews = payload.get("handoff_previews")
        if isinstance(previews, list):
            for item in previews:
                if not isinstance(item, dict):
                    continue
                if str(item.get("admissibility_primary_status_line") or "").strip():
                    preview = item
                    break
    if not isinstance(preview, dict):
        return None
    path = str(preview.get("path") or "").strip()
    queue_shape = str(preview.get("queue_shape") or "").strip()
    primary_status_line = str(preview.get("primary_status_line") or "").strip()
    if not path or not primary_status_line:
        return None
    normalized = {
        "path": path,
        "queue_shape": queue_shape,
        "primary_status_line": primary_status_line,
        "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
        "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
        "artifact_policy_status_line": str(
            preview.get("artifact_policy_status_line") or ""
        ).strip(),
        "admissibility_primary_status_line": str(
            preview.get("admissibility_primary_status_line") or ""
        ).strip(),
        "requires_operator_action": str(preview.get("requires_operator_action") or "false")
        .strip()
        .lower(),
    }
    scribe_status_line = str(preview.get("scribe_status_line") or "").strip()
    if scribe_status_line:
        normalized["scribe_status_line"] = scribe_status_line
    problem_route_status_line = str(preview.get("problem_route_status_line") or "").strip()
    if problem_route_status_line:
        normalized["problem_route_status_line"] = problem_route_status_line
    problem_route_secondary_labels = str(
        preview.get("problem_route_secondary_labels") or ""
    ).strip()
    if problem_route_secondary_labels:
        normalized["problem_route_secondary_labels"] = problem_route_secondary_labels
    dream_weekly_alignment_line = str(preview.get("dream_weekly_alignment_line") or "").strip()
    if dream_weekly_alignment_line:
        normalized["dream_weekly_alignment_line"] = dream_weekly_alignment_line
    return normalized


def _refreshable_scribe_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return None

    def _normalize(preview: dict[str, Any]) -> dict[str, str] | None:
        path = str(preview.get("path") or "").strip()
        queue_shape = str(preview.get("queue_shape") or "").strip()
        primary_status_line = str(preview.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            return None
        if not (
            path.endswith("docs/status/scribe_status_latest.json")
            or queue_shape.startswith("scribe_")
        ):
            return None
        normalized = {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                preview.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                preview.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(preview.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
        problem_route_status_line = str(preview.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            normalized["problem_route_status_line"] = problem_route_status_line
        problem_route_secondary_labels = str(
            preview.get("problem_route_secondary_labels") or ""
        ).strip()
        if problem_route_secondary_labels:
            normalized["problem_route_secondary_labels"] = problem_route_secondary_labels
        dream_weekly_alignment_line = str(preview.get("dream_weekly_alignment_line") or "").strip()
        if dream_weekly_alignment_line:
            normalized["dream_weekly_alignment_line"] = dream_weekly_alignment_line
        return normalized

    for item in previews:
        if isinstance(item, dict) and str(item.get("path") or "").strip().endswith(
            "docs/status/scribe_status_latest.json"
        ):
            normalized = _normalize(item)
            if normalized is not None:
                return normalized

    for item in previews:
        if not isinstance(item, dict):
            continue
        normalized = _normalize(item)
        if normalized is not None:
            return normalized
    return None


def _refreshable_dream_observability_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return None

    def _normalize(preview: dict[str, Any]) -> dict[str, str] | None:
        path = str(preview.get("path") or "").strip()
        queue_shape = str(preview.get("queue_shape") or "").strip()
        primary_status_line = str(preview.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            return None
        if not (
            path.endswith("docs/status/dream_observability_latest.json")
            or queue_shape == "dream_observability_ready"
        ):
            return None
        normalized = {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                preview.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                preview.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(preview.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
        problem_route_status_line = str(preview.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            normalized["problem_route_status_line"] = problem_route_status_line
        problem_route_secondary_labels = str(
            preview.get("problem_route_secondary_labels") or ""
        ).strip()
        if problem_route_secondary_labels:
            normalized["problem_route_secondary_labels"] = problem_route_secondary_labels
        dream_weekly_alignment_line = str(preview.get("dream_weekly_alignment_line") or "").strip()
        if dream_weekly_alignment_line:
            normalized["dream_weekly_alignment_line"] = dream_weekly_alignment_line
        return normalized

    for item in previews:
        if isinstance(item, dict) and str(item.get("path") or "").strip().endswith(
            "docs/status/dream_observability_latest.json"
        ):
            normalized = _normalize(item)
            if normalized is not None:
                return normalized

    for item in previews:
        if not isinstance(item, dict):
            continue
        normalized = _normalize(item)
        if normalized is not None:
            return normalized
    return None


def _refreshable_agent_integrity_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return None

    for preview in previews:
        if not isinstance(preview, dict):
            continue
        path = str(preview.get("path") or "").strip()
        queue_shape = str(preview.get("queue_shape") or "").strip()
        primary_status_line = str(preview.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            continue
        if not (
            path.endswith("docs/status/agent_integrity_latest.json")
            or queue_shape in {"agent_integrity_guarded", "agent_integrity_attention"}
        ):
            continue
        normalized = {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                preview.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                preview.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(preview.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
        problem_route_status_line = str(preview.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            normalized["problem_route_status_line"] = problem_route_status_line
        return normalized
    return None


def _refreshable_repo_semantic_atlas_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return None

    for preview in previews:
        if not isinstance(preview, dict):
            continue
        path = str(preview.get("path") or "").strip()
        queue_shape = str(preview.get("queue_shape") or "").strip()
        primary_status_line = str(preview.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            continue
        if not (
            path.endswith("docs/status/repo_semantic_atlas_latest.json")
            or queue_shape == "repo_semantic_atlas_ready"
        ):
            continue
        return {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                preview.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                preview.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(preview.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
    return None


def _refreshable_repo_intelligence_focus_preview(repo_root: Path) -> dict[str, str] | None:
    payload, _ = refreshable_report.build_report(repo_root)
    previews = payload.get("handoff_previews")
    if not isinstance(previews, list):
        return None

    for preview in previews:
        if not isinstance(preview, dict):
            continue
        path = str(preview.get("path") or "").strip()
        queue_shape = str(preview.get("queue_shape") or "").strip()
        primary_status_line = str(preview.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            continue
        if not (
            path.endswith("docs/status/repo_intelligence_latest.json")
            or queue_shape == "repo_intelligence_ready"
        ):
            continue
        normalized = {
            "path": path,
            "queue_shape": queue_shape,
            "primary_status_line": primary_status_line,
            "runtime_status_line": str(preview.get("runtime_status_line") or "").strip(),
            "anchor_status_line": str(preview.get("anchor_status_line") or "").strip(),
            "artifact_policy_status_line": str(
                preview.get("artifact_policy_status_line") or ""
            ).strip(),
            "admissibility_primary_status_line": str(
                preview.get("admissibility_primary_status_line") or ""
            ).strip(),
            "requires_operator_action": str(preview.get("requires_operator_action") or "false")
            .strip()
            .lower(),
        }
        semantic_retrieval_protocol = str(preview.get("semantic_retrieval_protocol") or "").strip()
        if semantic_retrieval_protocol:
            normalized["semantic_retrieval_protocol"] = semantic_retrieval_protocol
        semantic_preferred_neighborhood = str(
            preview.get("semantic_preferred_neighborhood") or ""
        ).strip()
        if semantic_preferred_neighborhood:
            normalized["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
        return normalized
    return None


def _select_refreshable_preview_by_queue_shape(
    previews: list[dict[str, str]],
    *,
    queue_shape: str,
) -> dict[str, str] | None:
    target = queue_shape.strip()
    if not target:
        return None
    for preview in previews:
        if str(preview.get("queue_shape") or "").strip() != target:
            continue
        if str(preview.get("primary_status_line") or "").strip():
            return dict(preview)
    return None


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Worktree Settlement Latest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Overall OK: `{str(payload['overall_ok']).lower()}`")
    lines.append(f"- Worktree dirty: `{str(payload['worktree']['dirty']).lower()}`")
    lines.append(
        f"- Planner recommendation: `{payload['planner']['recommendation']}`"
        f" (`tree_equal={str(payload['planner']['tree_equal']).lower()}`)"
    )
    lines.append(
        f"- Attribution debt: current=`{payload['planner']['current_missing_count']}`, "
        f"backfill=`{payload['planner']['backfill_missing_count']}`"
    )
    dream_weekly_alignment_line = str(payload.get("dream_weekly_alignment_line") or "").strip()
    weekly_host_status_preview = payload.get("weekly_host_status_preview")
    if isinstance(weekly_host_status_preview, dict):
        primary_status_line = str(
            weekly_host_status_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            weekly_host_status_preview.get("runtime_status_line") or ""
        ).strip()
        anchor_status_line = str(weekly_host_status_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            weekly_host_status_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            weekly_host_status_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        scribe_status_line = str(weekly_host_status_preview.get("scribe_status_line") or "").strip()
        artifact_policy_status_line = str(
            weekly_host_status_preview.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            weekly_host_status_preview.get("admissibility_primary_status_line") or ""
        ).strip()
        if primary_status_line:
            lines.append(f"- Weekly host status: `{primary_status_line}`")
        if runtime_status_line:
            lines.append(f"- Weekly runtime posture: `{runtime_status_line}`")
        if anchor_status_line:
            lines.append(f"- Weekly anchor posture: `{anchor_status_line}`")
        if problem_route_status_line:
            lines.append(f"- Weekly problem route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            lines.append(f"- Weekly problem route secondary: `{problem_route_secondary_labels}`")
        if scribe_status_line:
            lines.append(f"- Weekly Scribe posture: `{scribe_status_line}`")
        if artifact_policy_status_line:
            lines.append(f"- Weekly artifact policy: `{artifact_policy_status_line}`")
        if admissibility_primary_status_line:
            lines.append(f"- Weekly admissibility: `{admissibility_primary_status_line}`")
    focus_preview = payload.get("subjectivity_focus_preview")
    if isinstance(focus_preview, dict):
        primary_status_line = str(focus_preview.get("primary_status_line") or "").strip()
        runtime_status_line = str(focus_preview.get("runtime_status_line") or "").strip()
        scribe_status_line = str(focus_preview.get("scribe_status_line") or "").strip()
        anchor_status_line = str(focus_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            focus_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            focus_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        focus_alignment_line = str(focus_preview.get("dream_weekly_alignment_line") or "").strip()
        artifact_policy_status_line = str(
            focus_preview.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            focus_preview.get("admissibility_primary_status_line") or ""
        ).strip()
        if primary_status_line:
            lines.append(f"- Subjectivity focus: `{primary_status_line}`")
        if runtime_status_line:
            lines.append(f"- Subjectivity runtime posture: `{runtime_status_line}`")
        if scribe_status_line:
            lines.append(f"- Subjectivity Scribe posture: `{scribe_status_line}`")
        if anchor_status_line:
            lines.append(f"- Subjectivity anchor posture: `{anchor_status_line}`")
        if problem_route_status_line:
            lines.append(f"- Subjectivity problem route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            lines.append(
                f"- Subjectivity problem route secondary: `{problem_route_secondary_labels}`"
            )
        if focus_alignment_line:
            lines.append(f"- Subjectivity alignment: `{focus_alignment_line}`")
        if artifact_policy_status_line:
            lines.append(f"- Subjectivity artifact policy: `{artifact_policy_status_line}`")
        if admissibility_primary_status_line:
            lines.append(f"- Subjectivity admissibility: `{admissibility_primary_status_line}`")
    dream_focus_preview = payload.get("dream_observability_focus_preview")
    if isinstance(dream_focus_preview, dict):
        primary_status_line = str(dream_focus_preview.get("primary_status_line") or "").strip()
        runtime_status_line = str(dream_focus_preview.get("runtime_status_line") or "").strip()
        anchor_status_line = str(dream_focus_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            dream_focus_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            dream_focus_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        artifact_policy_status_line = str(
            dream_focus_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            lines.append(f"- Dream observability: `{primary_status_line}`")
        if runtime_status_line:
            lines.append(f"- Dream runtime posture: `{runtime_status_line}`")
        if anchor_status_line:
            lines.append(f"- Dream anchor posture: `{anchor_status_line}`")
        if problem_route_status_line:
            lines.append(f"- Dream problem route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            lines.append(f"- Dream problem route secondary: `{problem_route_secondary_labels}`")
        if artifact_policy_status_line:
            lines.append(f"- Dream artifact policy: `{artifact_policy_status_line}`")
    repo_semantic_atlas_focus_preview = payload.get("repo_semantic_atlas_focus_preview")
    if isinstance(repo_semantic_atlas_focus_preview, dict):
        primary_status_line = str(
            repo_semantic_atlas_focus_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            repo_semantic_atlas_focus_preview.get("runtime_status_line") or ""
        ).strip()
        artifact_policy_status_line = str(
            repo_semantic_atlas_focus_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            lines.append(f"- Repo semantic atlas: `{primary_status_line}`")
        if runtime_status_line:
            lines.append(f"- Repo semantic retrieval: `{runtime_status_line}`")
        if artifact_policy_status_line:
            lines.append(f"- Repo semantic artifact policy: `{artifact_policy_status_line}`")
    repo_intelligence_focus_preview = payload.get("repo_intelligence_focus_preview")
    if isinstance(repo_intelligence_focus_preview, dict):
        primary_status_line = str(
            repo_intelligence_focus_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            repo_intelligence_focus_preview.get("runtime_status_line") or ""
        ).strip()
        semantic_retrieval_protocol = str(
            repo_intelligence_focus_preview.get("semantic_retrieval_protocol") or ""
        ).strip()
        semantic_preferred_neighborhood = str(
            repo_intelligence_focus_preview.get("semantic_preferred_neighborhood") or ""
        ).strip()
        artifact_policy_status_line = str(
            repo_intelligence_focus_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            lines.append(f"- Repo intelligence: `{primary_status_line}`")
        if runtime_status_line:
            lines.append(f"- Repo intelligence runtime: `{runtime_status_line}`")
        if semantic_retrieval_protocol:
            lines.append(f"- Repo intelligence semantic protocol: `{semantic_retrieval_protocol}`")
        if semantic_preferred_neighborhood:
            lines.append(
                f"- Repo intelligence first neighborhood: `{semantic_preferred_neighborhood}`"
            )
        if artifact_policy_status_line:
            lines.append(f"- Repo intelligence artifact policy: `{artifact_policy_status_line}`")
    if dream_weekly_alignment_line:
        lines.append(f"- Dream weekly alignment: `{dream_weekly_alignment_line}`")
    lines.append("")
    lines.append("## Weekly Host Status Mirror")
    lines.append("")
    if isinstance(weekly_host_status_preview, dict):
        lines.append(f"- path: `{weekly_host_status_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{weekly_host_status_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{weekly_host_status_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{weekly_host_status_preview.get('primary_status_line', '')}`"
        )
        if str(weekly_host_status_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{weekly_host_status_preview.get('runtime_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("anchor_status_line") or "").strip():
            lines.append(
                f"- anchor_status_line: `{weekly_host_status_preview.get('anchor_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{weekly_host_status_preview.get('problem_route_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{weekly_host_status_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(weekly_host_status_preview.get("scribe_status_line") or "").strip():
            lines.append(
                f"- scribe_status_line: `{weekly_host_status_preview.get('scribe_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{weekly_host_status_preview.get('artifact_policy_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("admissibility_primary_status_line") or "").strip():
            lines.append(
                "- admissibility_primary_status_line: "
                f"`{weekly_host_status_preview.get('admissibility_primary_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("dream_weekly_alignment_line") or "").strip():
            lines.append(
                "- dream_weekly_alignment_line: "
                f"`{weekly_host_status_preview.get('dream_weekly_alignment_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Subjectivity Focus Mirror")
    lines.append("")
    focus_preview = payload.get("subjectivity_focus_preview")
    if isinstance(focus_preview, dict):
        lines.append(f"- path: `{focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(f"- primary_status_line: `{focus_preview.get('primary_status_line', '')}`")
        if str(focus_preview.get("runtime_status_line") or "").strip():
            lines.append(f"- runtime_status_line: `{focus_preview.get('runtime_status_line', '')}`")
        if str(focus_preview.get("scribe_status_line") or "").strip():
            lines.append(f"- scribe_status_line: `{focus_preview.get('scribe_status_line', '')}`")
        if str(focus_preview.get("anchor_status_line") or "").strip():
            lines.append(f"- anchor_status_line: `{focus_preview.get('anchor_status_line', '')}`")
        if str(focus_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{focus_preview.get('problem_route_status_line', '')}`"
            )
        if str(focus_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{focus_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(focus_preview.get("dream_weekly_alignment_line") or "").strip():
            lines.append(
                "- dream_weekly_alignment_line: "
                f"`{focus_preview.get('dream_weekly_alignment_line', '')}`"
            )
        if str(focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{focus_preview.get('artifact_policy_status_line', '')}`"
            )
        if str(focus_preview.get("admissibility_primary_status_line") or "").strip():
            lines.append(
                "- admissibility_primary_status_line: "
                f"`{focus_preview.get('admissibility_primary_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Dream Observability Focus Mirror")
    lines.append("")
    if isinstance(dream_focus_preview, dict):
        lines.append(f"- path: `{dream_focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{dream_focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{dream_focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{dream_focus_preview.get('primary_status_line', '')}`"
        )
        if str(dream_focus_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{dream_focus_preview.get('runtime_status_line', '')}`"
            )
        if str(dream_focus_preview.get("anchor_status_line") or "").strip():
            lines.append(
                f"- anchor_status_line: `{dream_focus_preview.get('anchor_status_line', '')}`"
            )
        if str(dream_focus_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{dream_focus_preview.get('problem_route_status_line', '')}`"
            )
        if str(dream_focus_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{dream_focus_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(dream_focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{dream_focus_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Repo Semantic Atlas Focus Mirror")
    lines.append("")
    if isinstance(repo_semantic_atlas_focus_preview, dict):
        lines.append(f"- path: `{repo_semantic_atlas_focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{repo_semantic_atlas_focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{repo_semantic_atlas_focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            "- primary_status_line: "
            f"`{repo_semantic_atlas_focus_preview.get('primary_status_line', '')}`"
        )
        if str(repo_semantic_atlas_focus_preview.get("runtime_status_line") or "").strip():
            lines.append(
                "- runtime_status_line: "
                f"`{repo_semantic_atlas_focus_preview.get('runtime_status_line', '')}`"
            )
        if str(repo_semantic_atlas_focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{repo_semantic_atlas_focus_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Repo Intelligence Focus Mirror")
    lines.append("")
    repo_intelligence_focus_preview = payload.get("repo_intelligence_focus_preview")
    if isinstance(repo_intelligence_focus_preview, dict):
        lines.append(f"- path: `{repo_intelligence_focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{repo_intelligence_focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{repo_intelligence_focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            "- primary_status_line: "
            f"`{repo_intelligence_focus_preview.get('primary_status_line', '')}`"
        )
        if str(repo_intelligence_focus_preview.get("runtime_status_line") or "").strip():
            lines.append(
                "- runtime_status_line: "
                f"`{repo_intelligence_focus_preview.get('runtime_status_line', '')}`"
            )
        if str(repo_intelligence_focus_preview.get("semantic_retrieval_protocol") or "").strip():
            lines.append(
                "- semantic_retrieval_protocol: "
                f"`{repo_intelligence_focus_preview.get('semantic_retrieval_protocol', '')}`"
            )
        if str(
            repo_intelligence_focus_preview.get("semantic_preferred_neighborhood") or ""
        ).strip():
            lines.append(
                "- semantic_preferred_neighborhood: "
                f"`{repo_intelligence_focus_preview.get('semantic_preferred_neighborhood', '')}`"
            )
        if str(repo_intelligence_focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{repo_intelligence_focus_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Scribe Focus Mirror")
    lines.append("")
    scribe_focus_preview = payload.get("scribe_focus_preview")
    if isinstance(scribe_focus_preview, dict):
        lines.append(f"- path: `{scribe_focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{scribe_focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{scribe_focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{scribe_focus_preview.get('primary_status_line', '')}`"
        )
        if str(scribe_focus_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{scribe_focus_preview.get('runtime_status_line', '')}`"
            )
        if str(scribe_focus_preview.get("anchor_status_line") or "").strip():
            lines.append(
                f"- anchor_status_line: `{scribe_focus_preview.get('anchor_status_line', '')}`"
            )
        if str(scribe_focus_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{scribe_focus_preview.get('problem_route_status_line', '')}`"
            )
        if str(scribe_focus_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{scribe_focus_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(scribe_focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{scribe_focus_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Agent Integrity Focus Mirror")
    lines.append("")
    agent_integrity_focus_preview = payload.get("agent_integrity_focus_preview")
    if isinstance(agent_integrity_focus_preview, dict):
        lines.append(f"- path: `{agent_integrity_focus_preview.get('path', '')}`")
        lines.append(f"- queue_shape: `{agent_integrity_focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{agent_integrity_focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            "- primary_status_line: "
            f"`{agent_integrity_focus_preview.get('primary_status_line', '')}`"
        )
        if str(agent_integrity_focus_preview.get("runtime_status_line") or "").strip():
            lines.append(
                "- runtime_status_line: "
                f"`{agent_integrity_focus_preview.get('runtime_status_line', '')}`"
            )
        if str(agent_integrity_focus_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{agent_integrity_focus_preview.get('problem_route_status_line', '')}`"
            )
        if str(agent_integrity_focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{agent_integrity_focus_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Settlement Order")
    lines.append("")
    for index, lane in enumerate(payload["settlement_lanes"], start=1):
        lines.append(
            f"{index}. **{lane['title']}**"
            f" (`entries={lane['entry_count']}`, `active={str(lane['active']).lower()}`)"
        )
        lines.append(f"   - Goal: {lane['goal']}")
        lines.append(f"   - Exit criteria: {lane['exit_criteria']}")
        for action in lane["recommended_actions"]:
            lines.append(f"   - Action: {action}")
        for category in lane["categories"]:
            samples = ", ".join(f"`{path}`" for path in category["sample_paths"])
            lines.append(
                f"   - `{category['category']}`: count=`{category['count']}`, "
                f"staged=`{category['staged_count']}`, unstaged=`{category['unstaged_count']}`, "
                f"untracked=`{category['untracked_count']}`"
            )
            if samples:
                lines.append(f"     samples: {samples}")
        previews = list(lane.get("handoff_previews") or [])
        if previews:
            lines.append(f"   - Handoff previews: `{len(previews)}`")
            for preview in previews:
                lines.append(
                    "     - "
                    f"`{preview.get('path', '')}` "
                    f"(`{preview.get('queue_shape', '')}`): "
                    f"`{preview.get('primary_status_line', '')}`"
                )
                if str(preview.get("runtime_status_line") or "").strip():
                    lines.append(
                        "       runtime_status_line: " f"`{preview.get('runtime_status_line', '')}`"
                    )
                if str(preview.get("anchor_status_line") or "").strip():
                    lines.append(
                        "       anchor_status_line: " f"`{preview.get('anchor_status_line', '')}`"
                    )
                if str(preview.get("problem_route_status_line") or "").strip():
                    lines.append(
                        "       problem_route_status_line: "
                        f"`{preview.get('problem_route_status_line', '')}`"
                    )
                if str(preview.get("problem_route_secondary_labels") or "").strip():
                    lines.append(
                        "       problem_route_secondary_labels: "
                        f"`{preview.get('problem_route_secondary_labels', '')}`"
                    )
                if str(preview.get("dream_weekly_alignment_line") or "").strip():
                    lines.append(
                        "       dream_weekly_alignment_line: "
                        f"`{preview.get('dream_weekly_alignment_line', '')}`"
                    )
                if str(preview.get("artifact_policy_status_line") or "").strip():
                    lines.append(
                        "       artifact_policy_status_line: "
                        f"`{preview.get('artifact_policy_status_line', '')}`"
                    )
                if str(preview.get("semantic_retrieval_protocol") or "").strip():
                    lines.append(
                        "       semantic_retrieval_protocol: "
                        f"`{preview.get('semantic_retrieval_protocol', '')}`"
                    )
                if str(preview.get("semantic_preferred_neighborhood") or "").strip():
                    lines.append(
                        "       semantic_preferred_neighborhood: "
                        f"`{preview.get('semantic_preferred_neighborhood', '')}`"
                    )
                if str(preview.get("scribe_status_line") or "").strip():
                    lines.append(
                        "       scribe_status_line: " f"`{preview.get('scribe_status_line', '')}`"
                    )
                lines.append(
                    "       requires_operator_action: "
                    f"`{preview.get('requires_operator_action', 'false')}`"
                )
                if str(preview.get("admissibility_primary_status_line") or "").strip():
                    lines.append(
                        "       admissibility_primary_status_line: "
                        f"`{preview.get('admissibility_primary_status_line', '')}`"
                    )
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- Private memory paths remain governed by the dual-track boundary; settle them as private evidence,"
        " not as ordinary public branch content."
    )
    lines.append(
        "- Generated status artifacts and derived reports should be refreshed only after the authored source set is stable."
    )
    lines.append(
        f"- Re-check branch movement readiness with `{payload['next_checkpoint']['command']}` after settlement."
    )
    lines.append("")
    return "\n".join(lines)


def build_report(
    repo_root: Path,
    *,
    sample_limit: int = 5,
    backfill_ref: str = base_switch_planner.DEFAULT_BACKFILL_REF,
) -> tuple[dict[str, Any], str]:
    plan_config = base_switch_planner.SwitchPlanConfig(
        repo_root=repo_root,
        current_ref="HEAD",
        backfill_ref=backfill_ref,
        artifact_path=repo_root / "_unused_worktree_settlement_plan.json",
        strict=False,
    )
    switch_plan = base_switch_planner.build_plan(plan_config)
    entries = base_switch_planner.collect_worktree_entries(repo_root)
    grouped_entries = _group_entries(entries)
    lanes = [
        _build_lane(definition, grouped_entries, sample_limit) for definition in LANE_DEFINITIONS
    ]
    refreshable_handoff_previews = _refreshable_handoff_previews(repo_root)
    refreshable_subjectivity_focus_preview = _refreshable_subjectivity_focus_preview(repo_root)
    refreshable_dream_observability_focus_preview = _refreshable_dream_observability_focus_preview(
        repo_root
    )
    refreshable_scribe_focus_preview = _refreshable_scribe_focus_preview(repo_root)
    refreshable_agent_integrity_focus_preview = _refreshable_agent_integrity_focus_preview(
        repo_root
    )
    refreshable_repo_semantic_atlas_focus_preview = _refreshable_repo_semantic_atlas_focus_preview(
        repo_root
    )
    refreshable_repo_intelligence_focus_preview = _refreshable_repo_intelligence_focus_preview(
        repo_root
    )
    refreshable_weekly_host_status_preview = _select_refreshable_preview_by_queue_shape(
        refreshable_handoff_previews,
        queue_shape="weekly_host_status",
    )
    refreshable_admissibility_preview_count = sum(
        1
        for item in refreshable_handoff_previews
        if str(item.get("admissibility_primary_status_line") or "").strip()
    )
    for lane in lanes:
        if lane["name"] != "refreshable_artifacts":
            continue
        lane["handoff_previews"] = refreshable_handoff_previews
        lane["handoff_preview_count"] = len(refreshable_handoff_previews)
        lane["admissibility_preview_count"] = refreshable_admissibility_preview_count
        break
    active_lane_count = sum(1 for lane in lanes if lane["active"])
    worktree = switch_plan["worktree"]
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": not bool(worktree.get("dirty")),
        "source": "scripts/run_worktree_settlement_report.py",
        "planner": {
            "recommendation": switch_plan["recommendation"],
            "rationale": switch_plan["rationale"],
            "tree_equal": switch_plan["tree_equal"],
            "current_missing_count": switch_plan["current_missing_count"],
            "backfill_missing_count": switch_plan["backfill_missing_count"],
            "cleanup_priority": switch_plan["cleanup_priority"],
        },
        "worktree": {
            "dirty": bool(worktree.get("dirty")),
            "entry_count": int(worktree.get("entry_count", 0)),
            "staged_count": int(worktree.get("staged_count", 0)),
            "unstaged_count": int(worktree.get("unstaged_count", 0)),
            "untracked_count": int(worktree.get("untracked_count", 0)),
            "category_counts": dict(worktree.get("category_counts") or {}),
        },
        "settlement_lanes": lanes,
        "summary": {
            "active_lane_count": active_lane_count,
            "largest_categories": switch_plan["cleanup_priority"][:5],
            "refreshable_handoff_preview_count": len(refreshable_handoff_previews),
            "refreshable_admissibility_preview_count": refreshable_admissibility_preview_count,
        },
        "weekly_host_status_preview": refreshable_weekly_host_status_preview,
        "subjectivity_focus_preview": refreshable_subjectivity_focus_preview,
        "dream_observability_focus_preview": refreshable_dream_observability_focus_preview,
        "scribe_focus_preview": refreshable_scribe_focus_preview,
        "agent_integrity_focus_preview": refreshable_agent_integrity_focus_preview,
        "repo_semantic_atlas_focus_preview": refreshable_repo_semantic_atlas_focus_preview,
        "repo_intelligence_focus_preview": refreshable_repo_intelligence_focus_preview,
        "dream_weekly_alignment_line": str(
            (refreshable_weekly_host_status_preview or {}).get("dream_weekly_alignment_line") or ""
        ).strip()
        or build_dream_weekly_alignment_line(
            refreshable_weekly_host_status_preview,
            refreshable_dream_observability_focus_preview,
        ),
        "next_checkpoint": {
            "command": (
                "python scripts/plan_commit_attribution_base_switch.py "
                f"--current-ref HEAD --backfill-ref {backfill_ref} --strict"
            ),
            "goal": "Re-check whether branch-base movement is safe after settlement.",
        },
        "boundary_notes": {
            "public_scope": ["tonesoul/", "tests/", "scripts/", "docs/status/"],
            "private_scope": [
                "memory/self_journal.jsonl",
                "memory/agent_discussion.jsonl",
                "memory/agent_discussion_curated.jsonl",
                "memory/vectors/",
                ".agent/",
                "obsidian-vault/",
            ],
        },
        "issues": [] if not worktree.get("dirty") else ["dirty_worktree_blocks_branch_movement"],
        "warnings": [],
    }
    markdown = _render_markdown(payload)
    return payload, markdown


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a non-destructive settlement plan for the current dirty worktree."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Directory for status artifacts.")
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=5,
        help="Number of sample paths to include per category.",
    )
    parser.add_argument(
        "--backfill-ref",
        default=base_switch_planner.DEFAULT_BACKFILL_REF,
        help="Attribution-clean branch used for planner context.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero while the worktree is still dirty.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = _resolve_path(repo_root, args.out_dir)
    sample_limit = max(1, int(args.sample_limit))
    payload, markdown = build_report(
        repo_root,
        sample_limit=sample_limit,
        backfill_ref=str(args.backfill_ref).strip() or base_switch_planner.DEFAULT_BACKFILL_REF,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
