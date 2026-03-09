"""Plan a safe branch-base switch for commit-attribution backfill recovery."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.verify_incremental_commit_attribution as incremental  # noqa: E402

DEFAULT_BACKFILL_REF = "feat/env-perception-attribution-backfill"
DEFAULT_ARTIFACT_PATH = "docs/status/commit_attribution_base_switch_latest.json"
LOCAL_BASE_CANDIDATES = ["origin/master", "origin/main", "master", "main"]


@dataclass(frozen=True)
class SwitchPlanConfig:
    repo_root: Path
    current_ref: str
    backfill_ref: str
    artifact_path: Path
    strict: bool


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_path(repo_root: Path, value: str) -> Path:
    raw = Path(str(value).strip())
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def _build_config(args: argparse.Namespace) -> SwitchPlanConfig:
    repo_root = Path(args.repo_root).resolve()
    current_ref = str(args.current_ref or "HEAD").strip() or "HEAD"
    backfill_ref = str(args.backfill_ref or DEFAULT_BACKFILL_REF).strip() or DEFAULT_BACKFILL_REF
    return SwitchPlanConfig(
        repo_root=repo_root,
        current_ref=current_ref,
        backfill_ref=backfill_ref,
        artifact_path=_resolve_path(repo_root, args.artifact_path),
        strict=bool(args.strict),
    )


def _run_git(repo_root: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *command],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _parse_status_lines(lines: list[str], *, include_entries: bool = False) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    staged_count = 0
    unstaged_count = 0
    untracked_count = 0
    category_counts: dict[str, int] = {}

    for raw in lines:
        line = str(raw).rstrip("\n")
        if not line.strip():
            continue
        status = line[:2] if len(line) >= 2 else line
        path = line[3:] if len(line) > 3 else ""
        is_untracked = status == "??"
        is_staged = status[0] not in {" ", "?"}
        is_unstaged = len(status) > 1 and status[1] not in {" ", "?"}
        if is_untracked:
            untracked_count += 1
        if is_staged:
            staged_count += 1
        if is_unstaged:
            unstaged_count += 1
        category = _classify_path(path)
        category_counts[category] = category_counts.get(category, 0) + 1
        entries.append(
            {
                "status": status,
                "path": path,
                "staged": is_staged,
                "unstaged": is_unstaged,
                "untracked": is_untracked,
                "category": category,
            }
        )

    payload = {
        "entry_count": len(entries),
        "staged_count": staged_count,
        "unstaged_count": unstaged_count,
        "untracked_count": untracked_count,
        "dirty": bool(entries),
        "sample_entries": entries[:20],
        "category_counts": dict(sorted(category_counts.items())),
    }
    if include_entries:
        payload["entries"] = entries
    return payload


def _classify_path(path: str) -> str:
    normalized = str(path or "").replace("\\", "/").strip()
    if normalized.startswith("docs/status/"):
        return _classify_status_path(normalized)
    if normalized.startswith("memory/"):
        return "memory"
    if normalized.startswith("docs/"):
        return "docs"
    if normalized.startswith("tests/"):
        return "tests"
    if normalized.startswith("scripts/"):
        return "scripts"
    if normalized.startswith("tonesoul/"):
        return "tonesoul"
    if normalized.startswith("api/") or normalized.startswith("apps/"):
        return "runtime_apps"
    if normalized.startswith(".agent/skills/") or normalized.startswith("skills/"):
        return "skills"
    if normalized.startswith(".github/") or normalized.startswith(".vscode/"):
        return "tooling"
    if normalized.startswith("spec/"):
        return "spec"
    if normalized.startswith("reports/"):
        return "reports"
    if normalized.startswith("experiments/"):
        return "experiments"
    if not normalized:
        return "unknown"
    return "repo_misc"


def _classify_status_path(normalized: str) -> str:
    relative = normalized[len("docs/status/") :]
    if "/" in relative:
        return "generated_status"

    name = Path(relative).name.lower()
    if name == "readme.md":
        return "docs"
    if name.endswith((".json", ".jsonl", ".html", ".csv", ".mmd")):
        return "generated_status"
    if name.endswith(".md") and (name.endswith("_latest.md") or name.endswith("_report.md")):
        return "generated_status"
    return "docs"


def _worktree_snapshot(repo_root: Path) -> dict[str, Any]:
    proc = _run_git(repo_root, ["status", "--short"])
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    snapshot = _parse_status_lines(lines)
    snapshot["command_ok"] = proc.returncode == 0
    snapshot["stderr_tail"] = proc.stderr.strip()[-600:]
    return snapshot


def collect_worktree_snapshot(repo_root: Path) -> dict[str, Any]:
    """Collect the current worktree summary using the planner's stable categories."""
    return _worktree_snapshot(repo_root)


def collect_worktree_entries(repo_root: Path) -> list[dict[str, Any]]:
    """Collect all dirty worktree entries using the planner's stable categories."""
    proc = _run_git(repo_root, ["status", "--short"])
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    snapshot = _parse_status_lines(lines, include_entries=True)
    return list(snapshot.get("entries") or [])


def _attribution_report(head_ref: str, equivalent_ref: str) -> dict[str, Any]:
    return incremental.build_report(
        event_name="",
        head_sha=head_ref,
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=LOCAL_BASE_CANDIDATES,
        equivalent_ref=equivalent_ref,
    )


def _plan_recommendation(
    *,
    current_ref: str,
    backfill_ref: str,
    current_report: dict[str, Any],
    backfill_report: dict[str, Any],
    worktree: dict[str, Any],
) -> tuple[str, str, list[str]]:
    current_ok = bool(current_report.get("ok"))
    backfill_ok = bool(backfill_report.get("ok"))
    current_equivalence = current_report.get("equivalence", {})
    tree_equal = bool(current_equivalence.get("tree_equal"))

    if current_ok:
        return (
            "no_switch_needed",
            "Current branch already satisfies commit-attribution requirements.",
            [],
        )

    if not backfill_ok:
        return (
            "backfill_branch_not_viable",
            "Backfill branch does not currently satisfy attribution requirements, so base switching would not remove the governance debt.",
            [],
        )

    if not tree_equal:
        return (
            "manual_review_required",
            "Backfill branch and current branch are not tree-equivalent. Treat this as real content drift, not metadata-only debt.",
            [],
        )

    if bool(worktree.get("dirty")):
        return (
            "defer_until_worktree_clean",
            "Backfill branch is clean and tree-equivalent, but the current worktree is dirty. Do not switch branch pointers in-place until local changes are settled or moved to a clean worktree.",
            [
                f"git worktree add <clean-path> {backfill_ref}",
                f"python scripts/plan_commit_attribution_base_switch.py --current-ref {current_ref} --backfill-ref {backfill_ref} --strict",
            ],
        )

    return (
        "continue_from_backfill_branch",
        "Backfill branch is attribution-clean and tree-equivalent to the current branch. Continue from the clean base instead of merging metadata-identical history.",
        [
            f"git switch {backfill_ref}",
            f"python scripts/verify_incremental_commit_attribution.py --strict --head-sha {backfill_ref}",
        ],
    )


def build_plan(config: SwitchPlanConfig) -> dict[str, Any]:
    current_report = _attribution_report(config.current_ref, config.backfill_ref)
    backfill_report = _attribution_report(config.backfill_ref, config.current_ref)
    worktree = _worktree_snapshot(config.repo_root)
    recommendation, rationale, commands = _plan_recommendation(
        current_ref=config.current_ref,
        backfill_ref=config.backfill_ref,
        current_report=current_report,
        backfill_report=backfill_report,
        worktree=worktree,
    )
    return {
        "generated_at": _iso_now(),
        "source": "scripts/plan_commit_attribution_base_switch.py",
        "current_ref": config.current_ref,
        "backfill_ref": config.backfill_ref,
        "current_missing_count": int(current_report.get("missing_count", 0)),
        "backfill_missing_count": int(backfill_report.get("missing_count", 0)),
        "tree_equal": bool(current_report.get("equivalence", {}).get("tree_equal")),
        "recommendation": recommendation,
        "rationale": rationale,
        "suggested_commands": commands,
        "worktree": worktree,
        "cleanup_priority": _cleanup_priority(worktree),
        "current_report": {
            "ok": bool(current_report.get("ok")),
            "mode": current_report.get("mode"),
            "range_spec": current_report.get("range_spec"),
            "missing": current_report.get("missing", []),
            "equivalence": current_report.get("equivalence", {}),
        },
        "backfill_report": {
            "ok": bool(backfill_report.get("ok")),
            "mode": backfill_report.get("mode"),
            "range_spec": backfill_report.get("range_spec"),
            "missing": backfill_report.get("missing", []),
            "equivalence": backfill_report.get("equivalence", {}),
        },
    }


def _cleanup_priority(worktree: dict[str, Any]) -> list[dict[str, Any]]:
    counts = worktree.get("category_counts") or {}
    if not isinstance(counts, dict):
        return []

    priority_order = [
        ("generated_status", "generated snapshots can usually be refreshed later"),
        ("reports", "derived reports should be separated from source edits early"),
        ("memory", "memory artifacts should be reviewed before branch movement"),
        ("docs", "hand-authored docs can be grouped after generated outputs"),
        ("scripts", "script changes affect operator and CI behavior"),
        ("tests", "tests should stay paired with code changes"),
        ("tonesoul", "core library changes are high-signal branch content"),
        ("runtime_apps", "runtime endpoints and apps affect execution contracts"),
        ("skills", "skill and registry drift changes governance surface"),
        ("tooling", "tooling/config changes can be isolated near the end"),
        ("spec", "spec changes should be grouped with their implementation"),
        ("experiments", "experimental assets can be settled separately"),
        ("repo_misc", "miscellaneous root-level changes need manual review"),
        ("unknown", "unknown paths require manual inspection"),
    ]
    return [
        {
            "category": category,
            "count": int(counts[category]),
            "reason": reason,
        }
        for category, reason in priority_order
        if category in counts
    ]


def build_cleanup_priority(worktree: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the ordered cleanup priority from a worktree snapshot."""
    return _cleanup_priority(worktree)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan a safe base-switch path for commit-attribution backfill recovery."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--current-ref", default="HEAD", help="Current branch/ref to evaluate.")
    parser.add_argument(
        "--backfill-ref",
        default=DEFAULT_BACKFILL_REF,
        help="Clean attribution backfill branch/ref to compare against.",
    )
    parser.add_argument(
        "--artifact-path",
        default=DEFAULT_ARTIFACT_PATH,
        help="Where to write the JSON plan artifact.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when the plan does not recommend a safe continuation path yet.",
    )
    return parser


def main() -> int:
    config = _build_config(build_parser().parse_args())
    payload = build_plan(config)
    _write_json(config.artifact_path, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if config.strict and payload["recommendation"] not in {
        "no_switch_needed",
        "continue_from_backfill_branch",
    }:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
