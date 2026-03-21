#!/usr/bin/env python3
"""Publish a compact change-intent governance artifact.

This script creates a source-declared record answering three questions:
1) Why are we changing now?
2) Which scope/files are in-bound?
3) How will we validate the change?
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.subjectivity_handoff import build_handoff_surface  # noqa: E402

JSON_FILENAME = "change_intent_latest.json"
MARKDOWN_FILENAME = "change_intent_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _git_touched_paths(repo_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain=v1"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []

    if result.returncode != 0:
        return []

    touched: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            touched.append(path)
    return touched


def build_report(
    *,
    repo_root: Path,
    intent_id: str,
    summary: str,
    why: str,
    scope: str,
    invariants: list[str],
    planned_files: list[str],
    validation_commands: list[str],
) -> dict[str, Any]:
    touched_files = _git_touched_paths(repo_root)
    normalized_invariants = [item.strip() for item in invariants if item.strip()]
    normalized_planned_files = [item.strip() for item in planned_files if item.strip()]
    normalized_validation = [item.strip() for item in validation_commands if item.strip()]

    primary_status_line = (
        "change_intent_ready | "
        f"intent_id={intent_id} "
        f"planned_files={len(normalized_planned_files)} "
        f"touched_files={len(touched_files)}"
    )
    runtime_status_line = (
        "intent_scope | "
        f"scope={scope} "
        f"invariants={len(normalized_invariants)} "
        f"validations={len(normalized_validation)}"
    )
    artifact_policy_status_line = (
        "change_governance=explicit_intent | "
        "requires_intent_before_edit=yes "
        "requires_validation_evidence=yes"
    )

    return {
        "generated_at": _iso_now(),
        "status": "ready",
        "intent_id": intent_id,
        "summary": summary,
        "why": why,
        "scope": scope,
        "invariants": normalized_invariants,
        "planned_files": normalized_planned_files,
        "validation_commands": normalized_validation,
        "touched_files": touched_files,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": build_handoff_surface(
            queue_shape="change_intent_ready",
            requires_operator_action=False,
            status_lines=[
                primary_status_line,
                runtime_status_line,
                artifact_policy_status_line,
            ],
            extra_fields={
                "intent_id": intent_id,
                "scope": scope,
                "planned_file_count": len(normalized_planned_files),
                "touched_file_count": len(touched_files),
            },
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Change Intent Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- status: {payload['status']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Intent",
        f"- intent_id: `{payload['intent_id']}`",
        f"- summary: {payload['summary']}",
        f"- why: {payload['why']}",
        f"- scope: `{payload['scope']}`",
        "",
        "## Invariants",
    ]

    invariants = payload.get("invariants") or []
    if isinstance(invariants, list) and invariants:
        lines.extend(f"- {str(item)}" for item in invariants)
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Planned Files")
    planned_files = payload.get("planned_files") or []
    if isinstance(planned_files, list) and planned_files:
        lines.extend(f"- `{str(item)}`" for item in planned_files)
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Validation Commands")
    validation_commands = payload.get("validation_commands") or []
    if isinstance(validation_commands, list) and validation_commands:
        lines.extend(f"- `{str(item)}`" for item in validation_commands)
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Touched Files (Current Working Tree)")
    touched_files = payload.get("touched_files") or []
    if isinstance(touched_files, list) and touched_files:
        lines.extend(f"- `{str(item)}`" for item in touched_files)
    else:
        lines.append("- (none detected)")

    return "\n".join(lines) + "\n"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish change-intent governance artifact.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "docs" / "status")
    parser.add_argument("--intent-id", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--why", required=True)
    parser.add_argument("--scope", default="workspace")
    parser.add_argument("--invariant", action="append", default=[])
    parser.add_argument("--planned-file", action="append", default=[])
    parser.add_argument("--validation-cmd", action="append", default=[])
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if why, invariants, or validation_commands are empty.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if getattr(args, "strict", False):
        if not str(args.why).strip():
            print("[strict] --why must not be empty", flush=True)
            return 1
        if not [v for v in (args.invariant or []) if v.strip()]:
            print("[strict] at least one --invariant is required", flush=True)
            return 1
        if not [v for v in (args.validation_cmd or []) if v.strip()]:
            print("[strict] at least one --validation-cmd is required", flush=True)
            return 1

    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_report(
        repo_root=repo_root,
        intent_id=str(args.intent_id).strip(),
        summary=str(args.summary).strip(),
        why=str(args.why).strip(),
        scope=str(args.scope).strip(),
        invariants=list(args.invariant or []),
        planned_files=list(args.planned_file or []),
        validation_commands=list(args.validation_cmd or []),
    )
    (out_dir / JSON_FILENAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / MARKDOWN_FILENAME).write_text(render_markdown(payload), encoding="utf-8")

    if args.stdout:
        _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
