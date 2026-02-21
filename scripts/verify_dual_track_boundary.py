"""
Dual-track boundary verifier.

Blocks public-repo changes that touch private-track paths.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

JSON_FILENAME = "dual_track_boundary_latest.json"
MARKDOWN_FILENAME = "dual_track_boundary_latest.md"
DEFAULT_BLOCKED_PREFIXES = (
    "tonesoul_evolution/",
    "memory/handoff/",
    "memory/external_framework_analysis/",
    "memory/narrative/",
    "memory/vectors/",
    "memory/.semantic_index/",
    "memory/.hierarchical_index/",
    ".moltbook/",
)
DEFAULT_BLOCKED_FILES = (
    "memory/self_journal.jsonl",
    "memory/agent_discussion.jsonl",
    "memory/agent_discussion_curated.jsonl",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _tail(text: str, limit: int = 1200) -> str:
    payload = text.strip()
    if len(payload) <= limit:
        return payload
    return payload[-limit:]


def _display_command(cmd: list[str]) -> str:
    rendered: list[str] = []
    for index, token in enumerate(cmd):
        text = str(token)
        if index == 0:
            executable = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable in {"git", "git.exe"}:
                rendered.append("git")
                continue
        rendered.append(text)
    return " ".join(rendered)


def _run_command(command: list[str], cwd: Path) -> tuple[int, str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return int(proc.returncode), proc.stdout, proc.stderr


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _normalize_prefix(prefix: str) -> str:
    normalized = _normalize_path(prefix)
    if normalized and not normalized.endswith("/"):
        normalized = normalized + "/"
    return normalized


def _parse_paths(text: str) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for raw in text.splitlines():
        path = _normalize_path(raw)
        if not path or path in seen:
            continue
        seen.add(path)
        results.append(path)
    return results


def _load_changed_file_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    return _parse_paths(path.read_text(encoding="utf-8", errors="replace"))


def _collect_changed_paths(
    repo_root: Path,
    *,
    staged: bool,
    base_ref: str | None,
    changed_file_list: Path | None,
    changed_files: list[str],
    runner: Callable[[list[str], Path], tuple[int, str, str]] = _run_command,
) -> dict[str, Any]:
    if changed_files:
        parsed = _parse_paths("\n".join(changed_files))
        return {
            "ok": True,
            "mode": "explicit",
            "command": None,
            "exit_code": 0,
            "stdout_tail": "",
            "stderr_tail": "",
            "paths": parsed,
        }

    if changed_file_list is not None:
        parsed = _load_changed_file_list(changed_file_list)
        return {
            "ok": True,
            "mode": "file_list",
            "command": str(changed_file_list.as_posix()),
            "exit_code": 0,
            "stdout_tail": "",
            "stderr_tail": "",
            "paths": parsed,
        }

    if staged:
        command = ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMRD"]
    elif base_ref:
        command = ["git", "diff", "--name-only", "--diff-filter=ACMRD", f"{base_ref}...HEAD"]
    else:
        command = ["git", "show", "--pretty=format:", "--name-only", "--diff-filter=ACMRD", "HEAD"]

    started = time.perf_counter()
    exit_code, stdout, stderr = runner(command, repo_root)
    duration = round(time.perf_counter() - started, 2)
    return {
        "ok": exit_code == 0,
        "mode": "git",
        "command": _display_command(command),
        "exit_code": exit_code,
        "duration_seconds": duration,
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
        "paths": _parse_paths(stdout),
    }


def _match_block_rule(
    path: str,
    *,
    blocked_prefixes: list[str],
    blocked_files: list[str],
) -> dict[str, str] | None:
    normalized = _normalize_path(path)
    for blocked_file in blocked_files:
        if normalized == blocked_file:
            return {"rule_type": "file", "rule": blocked_file}
    for blocked_prefix in blocked_prefixes:
        if normalized.startswith(blocked_prefix):
            return {"rule_type": "prefix", "rule": blocked_prefix}
    return None


def build_report(
    repo_root: Path,
    *,
    collection: dict[str, Any],
    blocked_prefixes: list[str],
    blocked_files: list[str],
    allow_private_paths: bool,
) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    for path in collection.get("paths", []):
        matched = _match_block_rule(
            path,
            blocked_prefixes=blocked_prefixes,
            blocked_files=blocked_files,
        )
        if matched is None:
            continue
        violations.append({"path": path, **matched})

    issues: list[str] = []
    warnings: list[str] = []
    if not collection.get("ok", False):
        issues.append("failed to collect changed files from git")

    if violations:
        if allow_private_paths:
            warnings.append(
                "private-path changes detected but bypassed via --allow-private-paths "
                "(break-glass mode)"
            )
        else:
            issues.append(
                f"detected {len(violations)} changed paths that violate dual-track boundary policy"
            )

    overall_ok = collection.get("ok", False) and (allow_private_paths or len(violations) == 0)
    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "repo_root": str(repo_root),
        "config": {
            "allow_private_paths": allow_private_paths,
            "blocked_prefixes": blocked_prefixes,
            "blocked_files": blocked_files,
        },
        "collection": collection,
        "metrics": {
            "changed_path_count": len(collection.get("paths", [])),
            "violation_count": len(violations),
        },
        "violations": violations,
        "issues": issues,
        "warnings": warnings,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Dual-Track Boundary Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- changed_path_count: {payload['metrics']['changed_path_count']}",
        f"- violation_count: {payload['metrics']['violation_count']}",
        f"- allow_private_paths: {str(payload['config']['allow_private_paths']).lower()}",
        "",
        "## Collection",
        f"- mode: {payload['collection'].get('mode')}",
    ]

    command = payload["collection"].get("command")
    if command:
        lines.append(f"- command: `{command}`")

    exit_code = payload["collection"].get("exit_code")
    if exit_code is not None:
        lines.append(f"- exit_code: {exit_code}")

    if payload["violations"]:
        lines.append("")
        lines.append("## Violations")
        lines.append("| path | rule_type | rule |")
        lines.append("| --- | --- | --- |")
        for item in payload["violations"]:
            lines.append(f"| `{item['path']}` | {item['rule_type']} | `{item['rule']}` |")

    if payload["issues"]:
        lines.append("")
        lines.append("## Issues")
        for issue in payload["issues"]:
            lines.append(f"- {issue}")

    if payload["warnings"]:
        lines.append("")
        lines.append("## Warnings")
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify dual-track public/private path boundaries."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use staged files (`git diff --cached`) as change source.",
    )
    parser.add_argument(
        "--base-ref",
        default=None,
        help="Compare against base ref (uses `git diff <base-ref>...HEAD`).",
    )
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Explicit changed file path (repeatable).",
    )
    parser.add_argument(
        "--changed-file-list",
        default=None,
        help="Path to newline-delimited changed files list.",
    )
    parser.add_argument(
        "--blocked-prefixes",
        nargs="+",
        default=list(DEFAULT_BLOCKED_PREFIXES),
        help="Blocked directory prefixes.",
    )
    parser.add_argument(
        "--blocked-files",
        nargs="+",
        default=list(DEFAULT_BLOCKED_FILES),
        help="Blocked exact file paths.",
    )
    parser.add_argument(
        "--allow-private-paths",
        action="store_true",
        help="Break-glass bypass for temporary emergency runs.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when checks fail.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    changed_file_list = Path(args.changed_file_list) if args.changed_file_list else None

    collection = _collect_changed_paths(
        repo_root,
        staged=bool(args.staged),
        base_ref=args.base_ref,
        changed_file_list=changed_file_list,
        changed_files=list(args.changed_file),
    )
    blocked_prefixes = sorted(
        {
            normalized
            for normalized in (_normalize_prefix(token) for token in args.blocked_prefixes)
            if normalized
        }
    )
    blocked_files = sorted(
        {_normalize_path(token) for token in args.blocked_files if _normalize_path(token)}
    )

    payload = build_report(
        repo_root,
        collection=collection,
        blocked_prefixes=blocked_prefixes,
        blocked_files=blocked_files,
        allow_private_paths=bool(args.allow_private_paths),
    )
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
