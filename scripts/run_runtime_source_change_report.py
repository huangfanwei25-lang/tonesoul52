"""Group dirty runtime-source changes into reviewable change groups."""

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

JSON_FILENAME = "runtime_source_change_groups_latest.json"
MARKDOWN_FILENAME = "runtime_source_change_groups_latest.md"

RUNTIME_CATEGORIES = {
    "scripts",
    "tests",
    "tonesoul",
    "runtime_apps",
    "skills",
    "tooling",
}

GROUP_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "repo_governance_and_settlement",
        "title": "Repo Governance and Settlement",
        "goal": "Keep repo-level gates, settlement planners, and healthcheck contracts reviewable as one governance surface.",
        "status_surfaces": [
            "docs/status/repo_healthcheck_latest.json",
            "docs/status/repo_governance_settlement_latest.json",
            "docs/status/refreshable_artifact_report_latest.json",
        ],
        "recommended_actions": [
            "Review healthcheck and settlement scripts as one changeset, because they define what counts as safe branch movement.",
            "Keep their tests and CI wiring paired so gate semantics do not drift from enforcement.",
        ],
        "prefixes": [
            "scripts/healthcheck.py",
            "scripts/run_repo_healthcheck.py",
            "scripts/verify_7d.py",
            "scripts/verify_docs_consistency.py",
            "scripts/verify_command_registry.py",
            "scripts/verify_incremental_commit_attribution.py",
            "scripts/plan_commit_attribution_base_switch.py",
            "scripts/run_worktree_settlement_report.py",
            "scripts/run_refreshable_artifact_report.py",
            "scripts/run_private_memory_review_report.py",
            "scripts/run_runtime_source_change_report.py",
            "scripts/run_repo_governance_settlement_report.py",
            "tests/test_agent_discussion_tool.py",
            "tests/test_run_repo_healthcheck.py",
            "tests/test_verify_7d.py",
            "tests/test_verify_docs_consistency.py",
            "tests/test_verify_incremental_commit_attribution.py",
            "tests/test_plan_commit_attribution_base_switch.py",
            "tests/test_run_worktree_settlement_report.py",
            "tests/test_run_refreshable_artifact_report.py",
            "tests/test_run_private_memory_review_report.py",
            "tests/test_run_runtime_source_change_report.py",
            "tests/test_run_repo_governance_settlement_report.py",
            ".github/workflows/test.yml",
        ],
    },
    {
        "name": "skill_and_registry_contracts",
        "title": "Skill and Registry Contracts",
        "goal": "Keep agent-skill governance and machine-readable registries aligned.",
        "recommended_actions": [
            "Review skill docs, registry JSON, and validators together because they define the same contract surface.",
            "Settle this group before branch movement so agent-facing behavior does not drift from machine checks.",
        ],
        "prefixes": [
            "scripts/skill_gate.py",
            "scripts/verify_skill_registry.py",
            "skills/registry.json",
            ".agent/skills/",
            "tests/test_verify_skill_registry.py",
        ],
    },
    {
        "name": "governance_pipeline_and_llm",
        "title": "Governance Pipeline and LLM Runtime",
        "goal": "Keep governance, orchestration, council parsing, and LLM observability changes as one coupled runtime group.",
        "recommended_actions": [
            "Review kernel, unified pipeline, LLM clients, and council parsing together because they share runtime decision contracts.",
            "Keep pipeline, governance, and LLM tests in the same changeset as the runtime files they validate.",
        ],
        "prefixes": [
            "tonesoul/governance/",
            "tonesoul/unified_pipeline.py",
            "tonesoul/llm/",
            "tonesoul/local_llm.py",
            "tonesoul/observability/",
            "tonesoul/safe_parse.py",
            "tonesoul/schemas.py",
            "tonesoul/council/perspective_factory.py",
            "tonesoul/council/model_registry.py",
            "tonesoul/gates/compute.py",
            "tonesoul/deliberation/engine.py",
            "tonesoul/tension_engine.py",
            "tonesoul/nonlinear_predictor.py",
            "tests/test_governance_kernel.py",
            "tests/test_pipeline_compute_gate.py",
            "tests/test_unified_pipeline_v2_runtime.py",
            "tests/test_local_llm.py",
            "tests/test_perspective_factory.py",
            "tests/test_resistance.py",
            "tests/test_variance_compressor.py",
            "tests/test_work_classifier.py",
            "tests/test_schemas.py",
            "tests/test_deliberation_engine.py",
            "tests/test_llm_",
            "tests/test_ollama_fallback.py",
            "tests/test_observability.py",
        ],
    },
    {
        "name": "perception_and_memory_ingest",
        "title": "Perception and Memory Ingest",
        "goal": "Keep environment perception, source selection, and memory-write seams reviewable as one ingest pipeline.",
        "recommended_actions": [
            "Review perception, source registry, and memory write-gateway changes together because they form one ingest path.",
            "Keep registry checks and perception tests paired with the runtime modules they exercise.",
        ],
        "prefixes": [
            "tonesoul/perception/",
            "tonesoul/memory/",
            "scripts/verify_external_source_registry.py",
            "tests/test_perception.py",
            "tests/test_memory_write_gateway.py",
            "tests/test_verify_external_source_registry.py",
            "tests/test_source_registry.py",
        ],
    },
    {
        "name": "autonomous_verification_runtime",
        "title": "Autonomous Verification Runtime",
        "goal": "Keep autonomous schedule, wake-up, dashboard, and weekly true-verification runners reviewable as one runtime chain.",
        "status_surfaces": [
            "docs/status/repo_healthcheck_latest.json",
            "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
            "docs/status/dream_observability_latest.json",
            "docs/status/autonomous_registry_schedule_latest.json",
        ],
        "recommended_actions": [
            "Review autonomous runtime modules with their runners and tests as one stack, because they share artifacts and cadence contracts.",
            "Treat task-scheduler wiring and true-verification summaries as part of the same operational runtime, not as detached scripts.",
        ],
        "prefixes": [
            "tonesoul/autonomous_",
            "tonesoul/dream_",
            "tonesoul/wakeup_loop.py",
            "tonesoul/schedule_profile.py",
            "tonesoul/true_verification_summary.py",
            "scripts/run_autonomous_",
            "scripts/run_dream_",
            "scripts/run_runtime_probe_watch.py",
            "scripts/run_true_verification_",
            "scripts/render_true_verification_task_scheduler.py",
            "scripts/install_true_verification_task_scheduler.py",
            "scripts/report_true_verification_task_status.py",
            "tests/test_autonomous_",
            "tests/test_dream_",
            "tests/test_run_autonomous_",
            "tests/test_run_dream_",
            "tests/test_run_runtime_probe_watch.py",
            "tests/test_run_true_verification_",
            "tests/test_render_true_verification_task_scheduler.py",
            "tests/test_install_true_verification_task_scheduler.py",
            "tests/test_report_true_verification_task_status.py",
            "tests/test_schedule_profile.py",
            "tests/test_true_verification_",
            "tests/test_wakeup_loop.py",
        ],
    },
    {
        "name": "scribe_chronicle_runtime",
        "title": "Scribe Chronicle Runtime",
        "goal": "Keep chronicle generation, companion/status handoff, and focused Scribe tests reviewable as one reflective runtime lane.",
        "status_surfaces": [
            "docs/status/scribe_status_latest.json",
        ],
        "recommended_actions": [
            "Review Scribe engine, runner, and focused tests together because they define one chronicle-generation contract.",
            "Open the compact Scribe status artifact first before reading raw chronicles, so review starts from the latest truthful handoff surface.",
        ],
        "prefixes": [
            "tonesoul/scribe/",
            "scripts/run_scribe_cycle.py",
            "tests/test_scribe_engine.py",
            "tests/test_run_scribe_cycle.py",
        ],
    },
    {
        "name": "api_contract_surface",
        "title": "API Contract Surface",
        "goal": "Keep API entrypoints and server contract changes reviewable as one delivery surface.",
        "recommended_actions": [
            "Review shared API core, chat route, and server wiring together because they define one external contract.",
            "Keep API security and contract tests attached to these runtime entrypoints.",
        ],
        "prefixes": [
            "api/",
            "apps/api/",
            "tests/test_api_phase_a_security.py",
        ],
    },
    {
        "name": "supporting_runtime_and_math",
        "title": "Supporting Runtime and Math",
        "goal": "Isolate supporting scripts, model probes, and math/runtime helpers from the core governance and autonomous stacks.",
        "recommended_actions": [
            "Review support scripts and math helpers as one smaller follow-up set after the major runtime groups are stable.",
            "Do not let auxiliary probe or maintenance scripts blur the main governance/autonomy changesets.",
        ],
        "prefixes": [
            "scripts/deduplicate_crystals.py",
            "scripts/generate_stress_data.py",
            "scripts/memory_compact.py",
            "scripts/run_self_play_resonance.py",
            "scripts/run_swarm_resonance_roleplay.py",
            "scripts/test_delegation.py",
            "scripts/test_ollama.py",
            "scripts/tension_dashboard.py",
            "scripts/verify_ollama_mvp.py",
            "scripts/fetch_moltbook.py",
            "scripts/test_moltbook.py",
        ],
    },
    {
        "name": "tooling_and_editor_contract",
        "title": "Tooling and Editor Contract",
        "goal": "Keep local tooling drift explicit so it does not hide inside larger runtime groups.",
        "recommended_actions": [
            "Review editor/tooling drift separately from runtime changes so developer ergonomics do not piggyback on feature work.",
        ],
        "prefixes": [
            ".vscode/",
        ],
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


def _dirty_runtime_entries(repo_root: Path) -> list[dict[str, Any]]:
    return [
        entry
        for entry in planner.collect_worktree_entries(repo_root)
        if str(entry.get("category") or "") in RUNTIME_CATEGORIES
    ]


def _matches(path: str, prefixes: list[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _group_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    assigned: set[str] = set()

    for definition in GROUP_DEFINITIONS:
        matched = [
            entry
            for entry in entries
            if str(entry.get("path") or "").replace("\\", "/") not in assigned
            and _matches(str(entry.get("path") or "").replace("\\", "/"), definition["prefixes"])
        ]
        if not matched:
            continue
        for entry in matched:
            assigned.add(str(entry.get("path") or "").replace("\\", "/"))
        groups.append(
            {
                "name": definition["name"],
                "title": definition["title"],
                "goal": definition["goal"],
                "status_surfaces": list(definition.get("status_surfaces") or []),
                "recommended_actions": list(definition["recommended_actions"]),
                "entry_count": len(matched),
                "category_counts": _count_by_key(matched, "category"),
                "sample_paths": [
                    str(entry.get("path") or "").replace("\\", "/") for entry in matched[:8]
                ],
                "paths": [str(entry.get("path") or "").replace("\\", "/") for entry in matched],
            }
        )

    ungrouped = [
        entry
        for entry in entries
        if str(entry.get("path") or "").replace("\\", "/") not in assigned
    ]
    if ungrouped:
        groups.append(
            {
                "name": "ungrouped_runtime_drift",
                "title": "Ungrouped Runtime Drift",
                "goal": "Surface runtime-source files that still lack a review group.",
                "status_surfaces": [],
                "recommended_actions": [
                    "Do not settle these files until they are attached to an explicit runtime change group.",
                ],
                "entry_count": len(ungrouped),
                "category_counts": _count_by_key(ungrouped, "category"),
                "sample_paths": [
                    str(entry.get("path") or "").replace("\\", "/") for entry in ungrouped[:8]
                ],
                "paths": [str(entry.get("path") or "").replace("\\", "/") for entry in ungrouped],
            }
        )

    return groups


def _count_by_key(entries: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for entry in entries:
        name = str(entry.get(key) or "unknown")
        counts[name] = counts.get(name, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(counts.items())]


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Runtime Source Change Groups Latest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Overall OK: `{str(payload['overall_ok']).lower()}`")
    lines.append(f"- Dirty runtime-source entries: `{payload['summary']['entry_count']}`")
    lines.append(f"- Change groups: `{payload['summary']['group_count']}`")
    lines.append(f"- Ungrouped entries: `{payload['summary']['ungrouped_count']}`")
    lines.append("")
    lines.append("## Groups")
    lines.append("")
    for index, group in enumerate(payload["change_groups"], start=1):
        lines.append(f"{index}. **{group['title']}** (`entries={group['entry_count']}`)")
        lines.append(f"   - Goal: {group['goal']}")
        for surface in group.get("status_surfaces", []):
            lines.append(f"   - Status surface: `{surface}`")
        for action in group["recommended_actions"]:
            lines.append(f"   - Action: {action}")
        if group["category_counts"]:
            counts = ", ".join(
                f"`{item['name']}={item['count']}`" for item in group["category_counts"]
            )
            lines.append(f"   - Categories: {counts}")
        for path in group["sample_paths"]:
            lines.append(f"   - Sample: `{path}`")
        lines.append("")
    return "\n".join(lines)


def build_report(repo_root: Path) -> tuple[dict[str, Any], str]:
    entries = _dirty_runtime_entries(repo_root)
    groups = _group_entries(entries)
    ungrouped = next(
        (group["entry_count"] for group in groups if group["name"] == "ungrouped_runtime_drift"),
        0,
    )
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(entries) == 0,
        "source": "scripts/run_runtime_source_change_report.py",
        "summary": {
            "entry_count": len(entries),
            "group_count": len(groups),
            "ungrouped_count": int(ungrouped),
            "category_counts": _count_by_key(entries, "category"),
        },
        "change_groups": groups,
        "issues": [] if not entries else ["runtime_source_lane_still_dirty"],
        "warnings": [],
    }
    return payload, _render_markdown(payload)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Group dirty runtime-source changes into reviewable change groups."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Directory for status artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero while dirty runtime-source artifacts remain.",
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
