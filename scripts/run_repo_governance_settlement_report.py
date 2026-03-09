"""Summarize repo-governance settlement truth from healthcheck and attribution artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "repo_governance_settlement_latest.json"
MARKDOWN_FILENAME = "repo_governance_settlement_latest.md"


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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_governance_group(runtime_groups: dict[str, Any]) -> dict[str, Any] | None:
    groups = runtime_groups.get("change_groups")
    if not isinstance(groups, list):
        return None
    for group in groups:
        if isinstance(group, dict) and group.get("name") == "repo_governance_and_settlement":
            return group
    return None


def _check_counts(checks: list[dict[str, Any]]) -> tuple[int, int]:
    pass_count = sum(1 for check in checks if bool(check.get("ok")))
    fail_count = len(checks) - pass_count
    return pass_count, fail_count


def _status(
    failing_checks: list[str],
    *,
    metadata_only_blocker: bool,
) -> str:
    if not failing_checks:
        return "green"
    if metadata_only_blocker:
        return "runtime_green_metadata_blocked"
    return "runtime_blocked"


def _issues(
    failing_checks: list[str],
    *,
    metadata_only_blocker: bool,
) -> list[str]:
    if not failing_checks:
        return []
    if metadata_only_blocker:
        return ["metadata_only_commit_attribution_blocker"]
    return [f"blocking_check:{name}" for name in failing_checks]


def _next_actions(
    settlement_status: str,
    attribution: dict[str, Any],
) -> list[str]:
    if settlement_status == "green":
        return [
            "Repo governance gates are green. Branch-movement decisions may proceed using the normal worktree safety ritual.",
        ]
    if settlement_status == "runtime_green_metadata_blocked":
        actions = [
            "Do not reinterpret the remaining failure as runtime drift; current repo governance gates are green except for historical commit trailers.",
            "Keep branch movement deferred until the dirty worktree is settled, then prefer the tree-equivalent backfill branch as the clean attribution base.",
        ]
        recommendation = str(attribution.get("recommendation") or "").strip()
        if recommendation:
            actions.append(f"Current attribution planner recommendation: `{recommendation}`.")
        return actions
    return [
        "Resolve the non-attribution blocking checks before treating repo governance as converged.",
        "Use the healthcheck artifact as the source of truth for which blocking gates still fail.",
    ]


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Repo Governance Settlement Latest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Overall OK: `{str(payload['overall_ok']).lower()}`")
    lines.append(f"- Settlement status: `{payload['settlement']['status']}`")
    lines.append(f"- Healthcheck generated at: `{payload['healthcheck']['generated_at']}`")
    lines.append(
        f"- Healthcheck pass/fail: `{payload['healthcheck']['pass_count']}` / "
        f"`{payload['healthcheck']['fail_count']}`"
    )
    lines.append(
        f"- Failing checks: `{', '.join(payload['healthcheck']['failing_checks']) or 'none'}`"
    )
    lines.append(
        f"- Metadata-only blocker: `{str(payload['settlement']['metadata_only_blocker']).lower()}`"
    )
    lines.append(
        f"- Runtime green except attribution: `{str(payload['settlement']['runtime_green_except_metadata']).lower()}`"
    )
    lines.append("")
    lines.append("## Attribution")
    lines.append("")
    lines.append(f"- Planner recommendation: `{payload['attribution']['recommendation']}`")
    lines.append(f"- Tree equal: `{str(payload['attribution']['tree_equal']).lower()}`")
    lines.append(
        f"- Missing trailers: current=`{payload['attribution']['current_missing_count']}`, "
        f"backfill=`{payload['attribution']['backfill_missing_count']}`"
    )
    lines.append("")
    lines.append("## Repo Governance Group")
    lines.append("")
    lines.append(
        f"- Dirty entries in repo governance group: "
        f"`{payload['repo_governance_group']['entry_count']}`"
    )
    for path in payload["repo_governance_group"]["sample_paths"]:
        lines.append(f"- Sample: `{path}`")
    lines.append("")
    lines.append("## Next Actions")
    lines.append("")
    for action in payload["settlement"]["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def build_report(
    repo_root: Path,
    *,
    healthcheck_path: str = "docs/status/repo_healthcheck_latest.json",
    attribution_path: str = "docs/status/commit_attribution_base_switch_latest.json",
    runtime_groups_path: str = "docs/status/runtime_source_change_groups_latest.json",
) -> tuple[dict[str, Any], str]:
    healthcheck = _load_json(_resolve_path(repo_root, healthcheck_path))
    attribution = _load_json(_resolve_path(repo_root, attribution_path))
    runtime_groups = _load_json(_resolve_path(repo_root, runtime_groups_path))

    checks = [check for check in healthcheck.get("checks", []) if isinstance(check, dict)]
    failing_checks = [str(check.get("name") or "") for check in checks if not bool(check.get("ok"))]
    pass_count, fail_count = _check_counts(checks)
    repo_group = _repo_governance_group(runtime_groups)
    metadata_only_blocker = (
        failing_checks == ["commit_attribution"]
        and bool(attribution.get("tree_equal"))
        and int(attribution.get("current_missing_count", 0)) > 0
        and int(attribution.get("backfill_missing_count", 0)) == 0
    )
    settlement_status = _status(
        failing_checks,
        metadata_only_blocker=metadata_only_blocker,
    )

    payload = {
        "generated_at": _iso_now(),
        "overall_ok": settlement_status == "green",
        "source": "scripts/run_repo_governance_settlement_report.py",
        "healthcheck": {
            "generated_at": healthcheck.get("generated_at"),
            "overall_ok": bool(healthcheck.get("overall_ok")),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "failing_checks": failing_checks,
        },
        "attribution": {
            "recommendation": attribution.get("recommendation"),
            "tree_equal": bool(attribution.get("tree_equal")),
            "current_missing_count": int(attribution.get("current_missing_count", 0)),
            "backfill_missing_count": int(attribution.get("backfill_missing_count", 0)),
            "rationale": attribution.get("rationale"),
            "suggested_commands": list(attribution.get("suggested_commands") or []),
        },
        "repo_governance_group": {
            "entry_count": int((repo_group or {}).get("entry_count", 0)),
            "sample_paths": list((repo_group or {}).get("sample_paths") or []),
            "recommended_actions": list((repo_group or {}).get("recommended_actions") or []),
        },
        "settlement": {
            "status": settlement_status,
            "metadata_only_blocker": metadata_only_blocker,
            "runtime_green_except_metadata": (
                settlement_status == "runtime_green_metadata_blocked"
            ),
            "next_actions": _next_actions(settlement_status, attribution),
        },
        "issues": _issues(
            failing_checks,
            metadata_only_blocker=metadata_only_blocker,
        ),
        "warnings": [] if repo_group else ["missing_repo_governance_runtime_group"],
    }
    return payload, _render_markdown(payload)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize repo-governance settlement truth from healthcheck and attribution artifacts."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Directory for status artifacts.")
    parser.add_argument(
        "--healthcheck-path",
        default="docs/status/repo_healthcheck_latest.json",
        help="Path to the latest repo healthcheck artifact.",
    )
    parser.add_argument(
        "--attribution-path",
        default="docs/status/commit_attribution_base_switch_latest.json",
        help="Path to the latest commit-attribution planner artifact.",
    )
    parser.add_argument(
        "--runtime-groups-path",
        default="docs/status/runtime_source_change_groups_latest.json",
        help="Path to the latest runtime-source grouping artifact.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero unless repo governance settlement is fully green.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = _resolve_path(repo_root, args.out_dir)
    payload, markdown = build_report(
        repo_root,
        healthcheck_path=str(args.healthcheck_path),
        attribution_path=str(args.attribution_path),
        runtime_groups_path=str(args.runtime_groups_path),
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
