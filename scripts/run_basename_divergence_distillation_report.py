#!/usr/bin/env python3
"""Report curated handling rules for same-basename divergent files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

REGISTRY_PATH = Path("spec/governance/basename_divergence_registry_v1.json")
JSON_FILENAME = "basename_divergence_distillation_latest.json"
MARKDOWN_FILENAME = "basename_divergence_distillation_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(repo_root: Path) -> dict[str, Any]:
    registry = _read_json(repo_root / REGISTRY_PATH)
    entries = list(registry.get("entries", []))
    issues: list[str] = []
    basenames = []
    status_counts: Counter[str] = Counter()
    strategy_counts: Counter[str] = Counter()

    inventory_path = repo_root / "docs/status/doc_convergence_inventory_latest.json"
    inventory_manual_review: list[str] = []
    if inventory_path.exists():
        inventory = _read_json(inventory_path)
        inventory_manual_review = sorted(
            item["basename"]
            for item in inventory.get("collisions", [])
            if item.get("family") == "manual_review"
        )

    for entry in entries:
        basename = str(entry["basename"])
        basenames.append(basename)
        status_counts[str(entry["status"])] += 1
        strategy_counts[str(entry["strategy"])] += 1

        seen_basenames = set()
        for rel_path in entry.get("paths", []):
            path = repo_root / rel_path
            if not path.exists():
                issues.append(f"missing_path:{rel_path}")
                continue
            seen_basenames.add(path.name)
        if seen_basenames and seen_basenames != {basename}:
            issues.append(f"basename_mismatch:{basename}")

    missing_from_registry = sorted(set(inventory_manual_review) - set(basenames))
    if missing_from_registry:
        issues.extend(f"uncovered_manual_review:{item}" for item in missing_from_registry)

    primary_status_line = (
        "basename_divergence_distilled | "
        f"entries={len(entries)} covered_manual_review={len(inventory_manual_review) - len(missing_from_registry)} "
        f"unresolved={status_counts.get('unresolved_private_shadow', 0)} issues={len(issues)}"
    )
    runtime_status_line = (
        "distillation_registry | "
        f"strategies={len(strategy_counts)} manual_review_baselines={len(inventory_manual_review)}"
    )
    artifact_policy_status_line = (
        "registry_mode=curated | semantics=boundary_plus_namespace_plus_private_shadow"
    )

    return {
        "generated_at": _iso_now(),
        "registry_path": REGISTRY_PATH.as_posix(),
        "metrics": {
            "entry_count": len(entries),
            "manual_review_collision_count": len(inventory_manual_review),
            "covered_manual_review_count": len(inventory_manual_review)
            - len(missing_from_registry),
            "unresolved_count": status_counts.get("unresolved_private_shadow", 0),
            "issue_count": len(issues),
        },
        "status_counts": dict(sorted(status_counts.items())),
        "strategy_counts": dict(sorted(strategy_counts.items())),
        "missing_from_registry": missing_from_registry,
        "issues": issues,
        "entries": entries,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Basename Divergence Distillation Latest",
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

    lines.extend(["", "## Status Counts"])
    for key, value in payload["status_counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Strategy Counts"])
    for key, value in payload["strategy_counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Entries"])
    for entry in payload["entries"]:
        lines.append(
            f"- `{entry['basename']}` status=`{entry['status']}` strategy=`{entry['strategy']}`"
        )
        lines.append(f"  - authority_rule: {entry['authority_rule']}")
        lines.append(f"  - editing_rule: {entry['editing_rule']}")
        for rel_path in entry["paths"]:
            lines.append(f"  - path: `{rel_path}`")

    lines.extend(["", "## Missing From Registry"])
    for item in payload["missing_from_registry"]:
        lines.append(f"- `{item}`")

    lines.extend(["", "## Issues"])
    for item in payload["issues"]:
        lines.append(f"- `{item}`")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render the curated same-basename divergence distillation report."
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
    print(
        json.dumps(
            {
                "ok": True,
                "artifacts": {
                    "json": f"{args.out_dir}/{JSON_FILENAME}",
                    "markdown": f"{args.out_dir}/{MARKDOWN_FILENAME}",
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
