"""Report dirty refreshable artifacts and whether they can be regenerated safely."""

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

import scripts.plan_commit_attribution_base_switch as planner  # noqa: E402

JSON_FILENAME = "refreshable_artifact_report_latest.json"
MARKDOWN_FILENAME = "refreshable_artifact_report_latest.md"

EXACT_PRODUCERS: dict[str, dict[str, str]] = {
    "docs/status/autonomous_registry_schedule_latest.json": {
        "command": "python scripts/run_autonomous_registry_schedule.py --strict",
        "source": "scripts/run_autonomous_registry_schedule.py",
    },
    "docs/status/dream_observability_latest.json": {
        "command": "python scripts/run_dream_observability_dashboard.py --strict",
        "source": "scripts/run_dream_observability_dashboard.py",
    },
    "docs/status/dream_observability_latest.html": {
        "command": "python scripts/run_dream_observability_dashboard.py --strict",
        "source": "scripts/run_dream_observability_dashboard.py",
    },
    "docs/status/dream_wakeup_snapshot_latest.json": {
        "command": "python scripts/run_autonomous_registry_schedule.py --strict",
        "source": "scripts/run_autonomous_registry_schedule.py",
    },
    "docs/status/repo_healthcheck_latest.json": {
        "command": "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion",
        "source": "scripts/run_repo_healthcheck.py",
    },
    "docs/status/repo_healthcheck_latest.md": {
        "command": "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion",
        "source": "scripts/run_repo_healthcheck.py",
    },
    "docs/status/repo_intelligence_latest.json": {
        "command": "python scripts/run_repo_intelligence_report.py",
        "source": "scripts/run_repo_intelligence_report.py",
    },
    "docs/status/repo_intelligence_latest.md": {
        "command": "python scripts/run_repo_intelligence_report.py",
        "source": "scripts/run_repo_intelligence_report.py",
    },
    "docs/status/repo_semantic_atlas_latest.json": {
        "command": "python scripts/run_repo_semantic_atlas.py",
        "source": "scripts/run_repo_semantic_atlas.py",
    },
    "docs/status/repo_semantic_atlas_latest.md": {
        "command": "python scripts/run_repo_semantic_atlas.py",
        "source": "scripts/run_repo_semantic_atlas.py",
    },
    "docs/status/repo_semantic_atlas_latest.mmd": {
        "command": "python scripts/run_repo_semantic_atlas.py",
        "source": "scripts/run_repo_semantic_atlas.py",
    },
    "docs/status/agent_integrity_latest.json": {
        "command": "python scripts/run_agent_integrity_report.py --strict",
        "source": "scripts/run_agent_integrity_report.py",
    },
    "docs/status/agent_integrity_latest.md": {
        "command": "python scripts/run_agent_integrity_report.py --strict",
        "source": "scripts/run_agent_integrity_report.py",
    },
    "docs/status/runtime_source_change_groups_latest.json": {
        "command": "python scripts/run_runtime_source_change_report.py",
        "source": "scripts/run_runtime_source_change_report.py",
    },
    "docs/status/runtime_source_change_groups_latest.md": {
        "command": "python scripts/run_runtime_source_change_report.py",
        "source": "scripts/run_runtime_source_change_report.py",
    },
    "docs/status/repo_governance_settlement_latest.json": {
        "command": "python scripts/run_repo_governance_settlement_report.py",
        "source": "scripts/run_repo_governance_settlement_report.py",
    },
    "docs/status/repo_governance_settlement_latest.md": {
        "command": "python scripts/run_repo_governance_settlement_report.py",
        "source": "scripts/run_repo_governance_settlement_report.py",
    },
    "docs/status/private_memory_review_latest.json": {
        "command": "python scripts/run_private_memory_review_report.py",
        "source": "scripts/run_private_memory_review_report.py",
    },
    "docs/status/private_memory_review_latest.md": {
        "command": "python scripts/run_private_memory_review_report.py",
        "source": "scripts/run_private_memory_review_report.py",
    },
    "docs/status/refreshable_artifact_report_latest.json": {
        "command": "python scripts/run_refreshable_artifact_report.py",
        "source": "scripts/run_refreshable_artifact_report.py",
    },
    "docs/status/refreshable_artifact_report_latest.md": {
        "command": "python scripts/run_refreshable_artifact_report.py",
        "source": "scripts/run_refreshable_artifact_report.py",
    },
    "docs/status/dual_track_boundary_latest.json": {
        "command": "python scripts/verify_dual_track_boundary.py --strict --staged",
        "source": "scripts/verify_dual_track_boundary.py",
    },
    "docs/status/dual_track_boundary_latest.md": {
        "command": "python scripts/verify_dual_track_boundary.py --strict --staged",
        "source": "scripts/verify_dual_track_boundary.py",
    },
    "docs/status/git_hygiene_latest.json": {
        "command": "python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28",
        "source": "scripts/verify_git_hygiene.py",
    },
    "docs/status/git_hygiene_latest.md": {
        "command": "python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28",
        "source": "scripts/verify_git_hygiene.py",
    },
    "docs/status/external_source_registry_latest.json": {
        "command": "python scripts/run_external_source_registry_check.py --strict",
        "source": "scripts/run_external_source_registry_check.py",
    },
    "docs/status/external_source_registry_latest.md": {
        "command": "python scripts/run_external_source_registry_check.py --strict",
        "source": "scripts/run_external_source_registry_check.py",
    },
    "docs/status/memory_governance_contract_latest.json": {
        "command": "python scripts/run_memory_governance_contract_check.py --strict",
        "source": "scripts/run_memory_governance_contract_check.py",
    },
    "docs/status/memory_governance_contract_latest.md": {
        "command": "python scripts/run_memory_governance_contract_check.py --strict",
        "source": "scripts/run_memory_governance_contract_check.py",
    },
    "docs/status/memory_quality_latest.json": {
        "command": "python scripts/run_memory_quality_report.py --strict",
        "source": "scripts/run_memory_quality_report.py",
    },
    "docs/status/memory_quality_latest.md": {
        "command": "python scripts/run_memory_quality_report.py --strict",
        "source": "scripts/run_memory_quality_report.py",
    },
    "docs/status/memory_learning_samples_latest.jsonl": {
        "command": "python scripts/run_memory_quality_report.py --strict",
        "source": "scripts/run_memory_quality_report.py",
    },
    "docs/status/subjectivity_report_latest.json": {
        "command": "python scripts/run_subjectivity_report.py --strict",
        "source": "scripts/run_subjectivity_report.py",
    },
    "docs/status/subjectivity_report_latest.md": {
        "command": "python scripts/run_subjectivity_report.py --strict",
        "source": "scripts/run_subjectivity_report.py",
    },
    "docs/status/subjectivity_shadow_pressure_latest.json": {
        "command": "python scripts/run_subjectivity_shadow_pressure_report.py",
        "source": "scripts/run_subjectivity_shadow_pressure_report.py",
    },
    "docs/status/subjectivity_shadow_pressure_latest.md": {
        "command": "python scripts/run_subjectivity_shadow_pressure_report.py",
        "source": "scripts/run_subjectivity_shadow_pressure_report.py",
    },
    "docs/status/subjectivity_tension_groups_latest.json": {
        "command": "python scripts/run_subjectivity_tension_grouping.py",
        "source": "scripts/run_subjectivity_tension_grouping.py",
    },
    "docs/status/subjectivity_tension_groups_latest.md": {
        "command": "python scripts/run_subjectivity_tension_grouping.py",
        "source": "scripts/run_subjectivity_tension_grouping.py",
    },
    "docs/status/subjectivity_review_batch_latest.json": {
        "command": "python scripts/run_subjectivity_review_batch.py",
        "source": "scripts/run_subjectivity_review_batch.py",
    },
    "docs/status/subjectivity_review_batch_latest.md": {
        "command": "python scripts/run_subjectivity_review_batch.py",
        "source": "scripts/run_subjectivity_review_batch.py",
    },
    "docs/status/memory_topology_fit_latest.json": {
        "command": "python scripts/run_memory_topology_fit_report.py --strict",
        "source": "scripts/run_memory_topology_fit_report.py",
    },
    "docs/status/memory_topology_fit_latest.md": {
        "command": "python scripts/run_memory_topology_fit_report.py --strict",
        "source": "scripts/run_memory_topology_fit_report.py",
    },
    "docs/status/multi_agent_divergence_latest.json": {
        "command": "python scripts/run_multi_agent_divergence_report.py --strict",
        "source": "scripts/run_multi_agent_divergence_report.py",
    },
    "docs/status/multi_agent_divergence_latest.md": {
        "command": "python scripts/run_multi_agent_divergence_report.py --strict",
        "source": "scripts/run_multi_agent_divergence_report.py",
    },
    "docs/status/persona_swarm_framework_latest.json": {
        "command": "python scripts/run_persona_swarm_framework.py --strict",
        "source": "scripts/run_persona_swarm_framework.py",
    },
    "docs/status/persona_swarm_long_task_latest.json": {
        "command": "python scripts/run_swarm_long_task_planning.py --strict",
        "source": "scripts/run_swarm_long_task_planning.py",
    },
    "docs/status/swarm_long_task_plan_latest.json": {
        "command": "python scripts/run_swarm_long_task_planning.py --strict",
        "source": "scripts/run_swarm_long_task_planning.py",
    },
    "docs/status/self_play_resonance_latest.json": {
        "command": "python scripts/run_self_play_resonance.py",
        "source": "scripts/run_self_play_resonance.py",
    },
    "docs/status/swarm_resonance_roleplay_latest.json": {
        "command": "python scripts/run_swarm_resonance_roleplay.py",
        "source": "scripts/run_swarm_resonance_roleplay.py",
    },
    "docs/status/philosophical_reflection_latest.json": {
        "command": "python scripts/run_philosophical_reflection_report.py --strict",
        "source": "scripts/run_philosophical_reflection_report.py",
    },
    "docs/status/philosophical_reflection_latest.md": {
        "command": "python scripts/run_philosophical_reflection_report.py --strict",
        "source": "scripts/run_philosophical_reflection_report.py",
    },
    "docs/status/command_registry_latest.json": {
        "command": "python scripts/verify_command_registry.py --strict",
        "source": "scripts/verify_command_registry.py",
    },
    "docs/status/command_registry_latest.md": {
        "command": "python scripts/verify_command_registry.py --strict",
        "source": "scripts/verify_command_registry.py",
    },
    "docs/status/submodule_integrity_latest.json": {
        "command": "python scripts/verify_submodule_integrity.py --strict",
        "source": "scripts/verify_submodule_integrity.py",
    },
    "docs/status/submodule_integrity_latest.md": {
        "command": "python scripts/verify_submodule_integrity.py --strict",
        "source": "scripts/verify_submodule_integrity.py",
    },
    "docs/status/stale_command_refs_latest.json": {
        "command": "python scripts/verify_stale_command_refs.py --strict",
        "source": "scripts/verify_stale_command_refs.py",
    },
    "docs/status/stale_command_refs_latest.md": {
        "command": "python scripts/verify_stale_command_refs.py --strict",
        "source": "scripts/verify_stale_command_refs.py",
    },
    "docs/status/friction_shadow_replay_latest.json": {
        "command": "python scripts/run_friction_shadow_replay_export.py --strict",
        "source": "scripts/run_friction_shadow_replay_export.py",
    },
    "docs/status/friction_shadow_replay_latest.md": {
        "command": "python scripts/run_friction_shadow_replay_export.py --strict",
        "source": "scripts/run_friction_shadow_replay_export.py",
    },
    "docs/status/friction_shadow_calibration_latest.json": {
        "command": "python scripts/run_friction_shadow_calibration_report.py --strict",
        "source": "scripts/run_friction_shadow_calibration_report.py",
    },
    "docs/status/friction_shadow_calibration_latest.md": {
        "command": "python scripts/run_friction_shadow_calibration_report.py --strict",
        "source": "scripts/run_friction_shadow_calibration_report.py",
    },
    "docs/status/worktree_settlement_latest.json": {
        "command": "python scripts/run_worktree_settlement_report.py",
        "source": "scripts/run_worktree_settlement_report.py",
    },
    "docs/status/worktree_settlement_latest.md": {
        "command": "python scripts/run_worktree_settlement_report.py",
        "source": "scripts/run_worktree_settlement_report.py",
    },
    "docs/status/scribe_status_latest.json": {
        "command": "python scripts/run_scribe_cycle.py",
        "source": "scripts/run_scribe_cycle.py",
    },
    "docs/status/true_verification_weekly/true_verification_task_status_latest.json": {
        "command": "python scripts/report_true_verification_task_status.py --strict",
        "source": "scripts/report_true_verification_task_status.py",
    },
    "docs/status/commit_attribution_local.json": {
        "command": "python scripts/verify_incremental_commit_attribution.py --strict --enforcement-anchor 3a0b48ae92f907b96b180558044aae6c8bf5cc92 --artifact-path docs/status/commit_attribution_local.json",
        "source": "scripts/verify_incremental_commit_attribution.py",
    },
    "docs/status/commit_attribution_backfill_branch.json": {
        "command": "python scripts/verify_incremental_commit_attribution.py --strict --head-sha feat/env-perception-attribution-backfill --equivalent-ref HEAD --require-tree-equivalence --artifact-path docs/status/commit_attribution_backfill_branch.json",
        "source": "scripts/verify_incremental_commit_attribution.py",
    },
    "docs/status/commit_attribution_base_switch_latest.json": {
        "command": "python scripts/plan_commit_attribution_base_switch.py",
        "source": "scripts/plan_commit_attribution_base_switch.py",
    },
    "reports/model_comparison_latest.json": {
        "command": "python experiments/compare_model_reports.py",
        "source": "experiments/compare_model_reports.py",
    },
    "reports/model_comparison_latest.md": {
        "command": "python experiments/compare_model_reports.py",
        "source": "experiments/compare_model_reports.py",
    },
}

MANUAL_REPORT_INPUTS = {
    "reports/analysis_gpt53.md",
    "reports/analysis_gpt54.md",
}

NAMESPACE_HANDLERS: list[dict[str, Any]] = [
    {
        "prefix": "docs/status/runtime_probe_watch/",
        "kind": "operational_namespace",
        "disposition": "namespace_regenerate",
        "namespace_commands": [
            "python scripts/run_runtime_probe_watch.py --strict",
        ],
        "producer_sources": [
            "scripts/run_runtime_probe_watch.py",
        ],
        "notes": "Runtime preflight namespace with refreshable schedule, wake-up, and dashboard artifacts.",
    },
    {
        "prefix": "docs/status/true_verification_weekly/",
        "kind": "operational_namespace",
        "disposition": "namespace_regenerate",
        "namespace_commands": [
            "python scripts/run_true_verification_host_tick.py --strict",
            "python scripts/report_true_verification_task_status.py --strict",
            "python scripts/render_true_verification_task_scheduler.py --strict",
            "python scripts/install_true_verification_task_scheduler.py --strict",
        ],
        "producer_sources": [
            "scripts/run_true_verification_host_tick.py",
            "scripts/report_true_verification_task_status.py",
            "scripts/render_true_verification_task_scheduler.py",
            "scripts/install_true_verification_task_scheduler.py",
        ],
        "notes": "Managed weekly experiment namespace; refresh with the host-tick and task-status entrypoints instead of treating the folder itself as an orphan artifact.",
    },
    {
        "prefix": "docs/status/probe_",
        "kind": "probe_namespace",
        "disposition": "archive_or_drop",
        "namespace_commands": [],
        "producer_sources": [],
        "notes": "Historical probe namespace. Safe to archive or drop once its evidence has been superseded by current latest artifacts.",
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


def _preview_json_path(path: str) -> str:
    normalized = str(path or "").replace("\\", "/").strip()
    if not normalized:
        return ""
    if normalized.endswith(".json"):
        return normalized
    if normalized.endswith(".md"):
        return f"{normalized[:-3]}.json"
    return ""


def _load_json_document(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _extract_handoff_surface(document: dict[str, Any]) -> dict[str, str] | None:
    candidates: list[dict[str, Any]] = [document]
    for key in ("batch", "grouping", "report"):
        nested = document.get(key)
        if isinstance(nested, dict):
            candidates.append(nested)

    for candidate in candidates:
        handoff = candidate.get("handoff")
        primary_status_line = str(candidate.get("primary_status_line") or "").strip()
        runtime_status_line = str(candidate.get("runtime_status_line") or "").strip()
        anchor_status_line = str(candidate.get("anchor_status_line") or "").strip()
        scribe_status_line = str(candidate.get("scribe_status_line") or "").strip()
        problem_route_status_line = str(candidate.get("problem_route_status_line") or "").strip()
        problem_route_secondary_labels = str(
            candidate.get("problem_route_secondary_labels") or ""
        ).strip()
        dream_weekly_alignment_line = str(
            candidate.get("dream_weekly_alignment_line") or ""
        ).strip()
        artifact_policy_status_line = str(
            candidate.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            candidate.get("admissibility_primary_status_line") or ""
        ).strip()
        semantic_retrieval_protocol = str(
            candidate.get("semantic_retrieval_protocol") or ""
        ).strip()
        semantic_preferred_neighborhood = str(
            candidate.get("semantic_preferred_neighborhood") or ""
        ).strip()
        queue_shape = ""
        requires_operator_action = False
        if isinstance(handoff, dict):
            queue_shape = str(handoff.get("queue_shape") or "").strip()
            requires_operator_action = bool(handoff.get("requires_operator_action"))
            if not primary_status_line:
                primary_status_line = str(handoff.get("primary_status_line") or "").strip()
            if not runtime_status_line:
                runtime_status_line = str(handoff.get("runtime_status_line") or "").strip()
            if not scribe_status_line:
                scribe_status_line = str(handoff.get("scribe_status_line") or "").strip()
            if not anchor_status_line:
                anchor_status_line = str(handoff.get("anchor_status_line") or "").strip()
            if not problem_route_status_line:
                problem_route_status_line = str(
                    handoff.get("problem_route_status_line") or ""
                ).strip()
            if not problem_route_secondary_labels:
                problem_route_secondary_labels = str(
                    handoff.get("problem_route_secondary_labels") or ""
                ).strip()
            if not dream_weekly_alignment_line:
                dream_weekly_alignment_line = str(
                    handoff.get("dream_weekly_alignment_line") or ""
                ).strip()
            if not artifact_policy_status_line:
                artifact_policy_status_line = str(
                    handoff.get("artifact_policy_status_line") or ""
                ).strip()
            if not admissibility_primary_status_line:
                admissibility_primary_status_line = str(
                    handoff.get("admissibility_primary_status_line") or ""
                ).strip()
            if not semantic_retrieval_protocol:
                semantic_retrieval_protocol = str(
                    handoff.get("semantic_retrieval_protocol") or ""
                ).strip()
            if not semantic_preferred_neighborhood:
                semantic_preferred_neighborhood = str(
                    handoff.get("semantic_preferred_neighborhood") or ""
                ).strip()
        if (
            queue_shape
            or primary_status_line
            or runtime_status_line
            or anchor_status_line
            or scribe_status_line
            or problem_route_status_line
            or problem_route_secondary_labels
            or dream_weekly_alignment_line
            or artifact_policy_status_line
            or admissibility_primary_status_line
            or semantic_retrieval_protocol
            or semantic_preferred_neighborhood
        ):
            preview = {
                "queue_shape": queue_shape,
                "primary_status_line": primary_status_line,
                "runtime_status_line": runtime_status_line,
                "anchor_status_line": anchor_status_line,
                "artifact_policy_status_line": artifact_policy_status_line,
                "admissibility_primary_status_line": admissibility_primary_status_line,
                "requires_operator_action": str(requires_operator_action).lower(),
            }
            if scribe_status_line:
                preview["scribe_status_line"] = scribe_status_line
            if problem_route_status_line:
                preview["problem_route_status_line"] = problem_route_status_line
            if problem_route_secondary_labels:
                preview["problem_route_secondary_labels"] = problem_route_secondary_labels
            if dream_weekly_alignment_line:
                preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
            if semantic_retrieval_protocol:
                preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
            if semantic_preferred_neighborhood:
                preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
            return preview
    return None


def _build_handoff_previews(
    repo_root: Path,
    items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    previews: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for item in items:
        preview_path = _preview_json_path(str(item.get("path") or ""))
        if not preview_path or preview_path in seen_paths:
            continue
        seen_paths.add(preview_path)
        document = _load_json_document(_resolve_path(repo_root, preview_path))
        if document is None:
            continue
        surface = _extract_handoff_surface(document)
        if surface is None:
            continue
        preview = {
            "path": preview_path,
            "queue_shape": surface["queue_shape"],
            "primary_status_line": surface["primary_status_line"],
            "runtime_status_line": surface.get("runtime_status_line", ""),
            "anchor_status_line": surface.get("anchor_status_line", ""),
            "artifact_policy_status_line": surface.get("artifact_policy_status_line", ""),
            "admissibility_primary_status_line": surface.get(
                "admissibility_primary_status_line", ""
            ),
            "requires_operator_action": surface.get("requires_operator_action", "false"),
        }
        semantic_retrieval_protocol = str(surface.get("semantic_retrieval_protocol") or "").strip()
        if semantic_retrieval_protocol:
            preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
        semantic_preferred_neighborhood = str(
            surface.get("semantic_preferred_neighborhood") or ""
        ).strip()
        if semantic_preferred_neighborhood:
            preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
        scribe_status_line = str(surface.get("scribe_status_line") or "").strip()
        if scribe_status_line:
            preview["scribe_status_line"] = scribe_status_line
        problem_route_status_line = str(surface.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            preview["problem_route_status_line"] = problem_route_status_line
        problem_route_secondary_labels = str(
            surface.get("problem_route_secondary_labels") or ""
        ).strip()
        if problem_route_secondary_labels:
            preview["problem_route_secondary_labels"] = problem_route_secondary_labels
        dream_weekly_alignment_line = str(surface.get("dream_weekly_alignment_line") or "").strip()
        if dream_weekly_alignment_line:
            preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
        previews.append(preview)
    return sorted(previews, key=lambda item: item["path"])


def _subjectivity_focus_preview(
    previews: list[dict[str, str]],
) -> dict[str, str] | None:
    def _normalize(item: dict[str, Any]) -> dict[str, str] | None:
        path = str(item.get("path") or "").strip()
        queue_shape = str(item.get("queue_shape") or "").strip()
        primary_status_line = str(item.get("primary_status_line") or "").strip()
        if not path or not primary_status_line:
            return None
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
        scribe_status_line = str(item.get("scribe_status_line") or "").strip()
        if scribe_status_line:
            preview["scribe_status_line"] = scribe_status_line
        problem_route_status_line = str(item.get("problem_route_status_line") or "").strip()
        if problem_route_status_line:
            preview["problem_route_status_line"] = problem_route_status_line
        problem_route_secondary_labels = str(
            item.get("problem_route_secondary_labels") or ""
        ).strip()
        if problem_route_secondary_labels:
            preview["problem_route_secondary_labels"] = problem_route_secondary_labels
        dream_weekly_alignment_line = str(item.get("dream_weekly_alignment_line") or "").strip()
        if dream_weekly_alignment_line:
            preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
        return preview

    prioritized = [
        item
        for item in previews
        if str(item.get("admissibility_primary_status_line") or "").strip()
    ]
    if prioritized:
        return _normalize(prioritized[0])

    batch_preview = next(
        (
            item
            for item in previews
            if str(item.get("path") or "").endswith("subjectivity_review_batch_latest.json")
        ),
        None,
    )
    if isinstance(batch_preview, dict):
        return _normalize(batch_preview)
    return None


def _dirty_refreshable_entries(repo_root: Path) -> list[dict[str, Any]]:
    entries = planner.collect_worktree_entries(repo_root)
    return [
        entry
        for entry in entries
        if str(entry.get("category") or "") in {"generated_status", "reports"}
    ]


def _classify_entry(entry: dict[str, Any]) -> dict[str, Any]:
    path = str(entry.get("path") or "").replace("\\", "/")
    producer = EXACT_PRODUCERS.get(path)
    if producer is not None:
        return {
            "path": path,
            "category": entry.get("category"),
            "kind": "known_generated",
            "disposition": "regenerate",
            "producer_command": producer["command"],
            "producer_source": producer["source"],
            "status": entry.get("status"),
            "staged": bool(entry.get("staged")),
            "unstaged": bool(entry.get("unstaged")),
            "untracked": bool(entry.get("untracked")),
        }

    for handler in NAMESPACE_HANDLERS:
        prefix = str(handler["prefix"])
        if path.startswith(prefix):
            return {
                "path": path,
                "category": entry.get("category"),
                "kind": handler["kind"],
                "disposition": handler["disposition"],
                "producer_command": None,
                "producer_source": None,
                "namespace_commands": list(handler.get("namespace_commands") or []),
                "producer_sources": list(handler.get("producer_sources") or []),
                "notes": str(handler.get("notes") or ""),
                "status": entry.get("status"),
                "staged": bool(entry.get("staged")),
                "unstaged": bool(entry.get("unstaged")),
                "untracked": bool(entry.get("untracked")),
            }

    if path in MANUAL_REPORT_INPUTS:
        return {
            "path": path,
            "category": entry.get("category"),
            "kind": "manual_report_input",
            "disposition": "manual_review",
            "producer_command": None,
            "producer_source": None,
            "namespace_commands": [],
            "producer_sources": [],
            "notes": "",
            "status": entry.get("status"),
            "staged": bool(entry.get("staged")),
            "unstaged": bool(entry.get("unstaged")),
            "untracked": bool(entry.get("untracked")),
        }

    kind = "unknown_refreshable"
    disposition = "inspect"
    if path.startswith("docs/status/") and path.endswith("/"):
        kind = "status_folder"
    elif path.startswith("docs/status/") and path.endswith(
        (".json", ".jsonl", ".html", ".csv", ".mmd", ".md")
    ):
        kind = "generated_status_artifact"
    elif path.startswith("reports/") and path.endswith((".json", ".md", ".xml")):
        kind = "report_artifact"

    return {
        "path": path,
        "category": entry.get("category"),
        "kind": kind,
        "disposition": disposition,
        "producer_command": None,
        "producer_source": None,
        "namespace_commands": [],
        "producer_sources": [],
        "notes": "",
        "status": entry.get("status"),
        "staged": bool(entry.get("staged")),
        "unstaged": bool(entry.get("unstaged")),
        "untracked": bool(entry.get("untracked")),
    }


def _group_counts(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(counts.items())]


def _group_by_command(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        command = item.get("producer_command")
        if not isinstance(command, str) or not command.strip():
            continue
        bucket = grouped.setdefault(
            command,
            {
                "command": command,
                "source": item.get("producer_source"),
                "count": 0,
                "paths": [],
            },
        )
        bucket["count"] += 1
        bucket["paths"].append(item["path"])
    return sorted(grouped.values(), key=lambda item: (-int(item["count"]), str(item["command"])))


def _namespace_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets = []
    for item in items:
        if item.get("disposition") != "namespace_regenerate":
            continue
        buckets.append(
            {
                "path": item["path"],
                "kind": item["kind"],
                "commands": list(item.get("namespace_commands") or []),
                "sources": list(item.get("producer_sources") or []),
                "notes": item.get("notes") or "",
            }
        )
    return buckets


def _archivable_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets = []
    for item in items:
        if item.get("disposition") != "archive_or_drop":
            continue
        buckets.append(
            {
                "path": item["path"],
                "kind": item["kind"],
                "notes": item.get("notes") or "",
            }
        )
    return buckets


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Refreshable Artifact Report Latest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Overall OK: `{str(payload['overall_ok']).lower()}`")
    lines.append(f"- Dirty refreshable entries: `{payload['summary']['entry_count']}`")
    lines.append(f"- Known regenerators: `{payload['summary']['regenerate_count']}`")
    lines.append(f"- Namespace regenerators: `{payload['summary']['namespace_regenerate_count']}`")
    lines.append(f"- Manual review items: `{payload['summary']['manual_review_count']}`")
    lines.append(
        f"- Archive-or-drop probe namespaces: `{payload['summary']['archive_or_drop_count']}`"
    )
    lines.append(f"- Inspect items: `{payload['summary']['inspect_count']}`")
    lines.append(f"- Handoff previews: `{payload['summary']['handoff_preview_count']}`")
    lines.append(f"- Admissibility previews: `{payload['summary']['admissibility_preview_count']}`")
    lines.append("")
    lines.append("## Subjectivity Focus")
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
    lines.append("## Handoff Previews")
    lines.append("")
    if payload["handoff_previews"]:
        for item in payload["handoff_previews"]:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - queue_shape: `{item['queue_shape']}`")
            lines.append(
                "  - requires_operator_action: "
                f"`{item.get('requires_operator_action', 'false')}`"
            )
            lines.append(f"  - primary_status_line: `{item['primary_status_line']}`")
            if str(item.get("runtime_status_line") or "").strip():
                lines.append(f"  - runtime_status_line: `{item['runtime_status_line']}`")
            if str(item.get("scribe_status_line") or "").strip():
                lines.append(f"  - scribe_status_line: `{item['scribe_status_line']}`")
            if str(item.get("anchor_status_line") or "").strip():
                lines.append(f"  - anchor_status_line: `{item['anchor_status_line']}`")
            if str(item.get("problem_route_status_line") or "").strip():
                lines.append(
                    "  - problem_route_status_line: " f"`{item['problem_route_status_line']}`"
                )
            if str(item.get("problem_route_secondary_labels") or "").strip():
                lines.append(
                    "  - problem_route_secondary_labels: "
                    f"`{item['problem_route_secondary_labels']}`"
                )
            if str(item.get("dream_weekly_alignment_line") or "").strip():
                lines.append(
                    "  - dream_weekly_alignment_line: " f"`{item['dream_weekly_alignment_line']}`"
                )
            if str(item.get("artifact_policy_status_line") or "").strip():
                lines.append(
                    "  - artifact_policy_status_line: " f"`{item['artifact_policy_status_line']}`"
                )
            if str(item.get("semantic_retrieval_protocol") or "").strip():
                lines.append(
                    "  - semantic_retrieval_protocol: " f"`{item['semantic_retrieval_protocol']}`"
                )
            if str(item.get("semantic_preferred_neighborhood") or "").strip():
                lines.append(
                    "  - semantic_preferred_neighborhood: "
                    f"`{item['semantic_preferred_neighborhood']}`"
                )
            if str(item.get("admissibility_primary_status_line") or "").strip():
                lines.append(
                    "  - admissibility_primary_status_line: "
                    f"`{item['admissibility_primary_status_line']}`"
                )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Regenerate")
    lines.append("")
    if payload["regenerate_groups"]:
        for group in payload["regenerate_groups"]:
            lines.append(f"- `{group['command']}`")
            lines.append(f"  - count: `{group['count']}`")
            if group.get("source"):
                lines.append(f"  - source: `{group['source']}`")
            for path in group["paths"][:6]:
                lines.append(f"  - path: `{path}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Namespace Regenerate")
    lines.append("")
    if payload["namespace_groups"]:
        for item in payload["namespace_groups"]:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
            if item["notes"]:
                lines.append(f"  - notes: `{item['notes']}`")
            for command in item["commands"]:
                lines.append(f"  - command: `{command}`")
            for source in item["sources"]:
                lines.append(f"  - source: `{source}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Manual Review")
    lines.append("")
    manual_items = [item for item in payload["entries"] if item["disposition"] == "manual_review"]
    if manual_items:
        for item in manual_items:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Archive Or Drop")
    lines.append("")
    if payload["archive_groups"]:
        for item in payload["archive_groups"]:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
            if item["notes"]:
                lines.append(f"  - notes: `{item['notes']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Inspect")
    lines.append("")
    inspect_items = [item for item in payload["entries"] if item["disposition"] == "inspect"]
    if inspect_items:
        for item in inspect_items[:20]:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def build_report(repo_root: Path) -> tuple[dict[str, Any], str]:
    entries = [_classify_entry(entry) for entry in _dirty_refreshable_entries(repo_root)]
    handoff_previews = _build_handoff_previews(repo_root, entries)
    subjectivity_focus_preview = _subjectivity_focus_preview(handoff_previews)
    admissibility_preview_count = sum(
        1
        for item in handoff_previews
        if str(item.get("admissibility_primary_status_line") or "").strip()
    )
    regenerate_groups = _group_by_command(entries)
    namespace_groups = _namespace_items(entries)
    archive_groups = _archivable_items(entries)
    summary = {
        "entry_count": len(entries),
        "regenerate_count": sum(1 for item in entries if item["disposition"] == "regenerate"),
        "namespace_regenerate_count": sum(
            1 for item in entries if item["disposition"] == "namespace_regenerate"
        ),
        "manual_review_count": sum(1 for item in entries if item["disposition"] == "manual_review"),
        "archive_or_drop_count": sum(
            1 for item in entries if item["disposition"] == "archive_or_drop"
        ),
        "inspect_count": sum(1 for item in entries if item["disposition"] == "inspect"),
        "handoff_preview_count": len(handoff_previews),
        "admissibility_preview_count": admissibility_preview_count,
        "kind_counts": _group_counts(entries, "kind"),
        "category_counts": _group_counts(entries, "category"),
        "disposition_counts": _group_counts(entries, "disposition"),
    }
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(entries) == 0,
        "source": "scripts/run_refreshable_artifact_report.py",
        "summary": summary,
        "regenerate_groups": regenerate_groups,
        "namespace_groups": namespace_groups,
        "archive_groups": archive_groups,
        "handoff_previews": handoff_previews,
        "subjectivity_focus_preview": subjectivity_focus_preview,
        "entries": entries,
        "issues": [] if not entries else ["refreshable_artifacts_lane_still_dirty"],
        "warnings": [],
    }
    return payload, _render_markdown(payload)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report dirty refreshable artifacts and whether they can be regenerated safely."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Directory for status artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero while dirty refreshable artifacts remain.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = _resolve_path(repo_root, args.out_dir)
    payload, markdown = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
