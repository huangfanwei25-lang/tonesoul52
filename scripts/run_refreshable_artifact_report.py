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
    "docs/status/commit_attribution_local.json": {
        "command": "python scripts/verify_incremental_commit_attribution.py --strict --artifact-path docs/status/commit_attribution_local.json",
        "source": "scripts/verify_incremental_commit_attribution.py",
    },
    "docs/status/commit_attribution_backfill_branch.json": {
        "command": "python scripts/verify_incremental_commit_attribution.py --strict --head-sha feat/env-perception-attribution-backfill --equivalent-ref HEAD --artifact-path docs/status/commit_attribution_backfill_branch.json",
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
