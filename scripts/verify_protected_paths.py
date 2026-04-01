#!/usr/bin/env python3
"""Protected-path verifier for agent workflows.

Purpose:
- turn prose-only "do not touch this" rules into executable checks
- support hook-style usage with explicit changed paths
- support local verification from git state when explicit paths are unavailable
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BLOCKED_FILES = (
    ".env",
    ".env.local",
    "AGENTS.md",
    "MEMORY.md",
)
DEFAULT_BLOCKED_GLOBS = (
    ".env.*.local",
    "memory/*.jsonl",
    "memory/**/*.jsonl",
    "memory/*.db",
    "memory/**/*.db",
)
DEFAULT_BLOCKED_PREFIXES = (
    "memory/handoff/",
    "memory/external_framework_analysis/",
    "memory/narrative/",
    "memory/vectors/",
    "memory/autonomous/",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _display_command(command: list[str] | None) -> str | None:
    if not command:
        return None
    rendered: list[str] = []
    for index, token in enumerate(command):
        text = str(token)
        if index == 0:
            executable = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable.startswith("python"):
                rendered.append("python")
                continue
            if executable in {"git", "git.exe"}:
                rendered.append("git")
                continue
        rendered.append(text)
    return " ".join(rendered)


def _parse_changed_lines(text: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        raw = raw_line.rstrip()
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if (
            len(parts) >= 2
            and parts[0]
            and parts[0][0].upper() in {"A", "C", "M", "R", "D", "T", "U"}
        ):
            candidates = parts[1:]
        elif len(raw) >= 4 and raw[2] == " " and any(token.strip() for token in raw[:2]):
            candidates = [raw[3:].strip()]
        else:
            candidates = [raw.strip()]

        for candidate in candidates:
            if " -> " in candidate:
                candidate = candidate.split(" -> ", maxsplit=1)[1]
            path = _normalize_path(candidate)
            if not path or path in seen:
                continue
            seen.add(path)
            paths.append(path)
    return paths


def collect_changed_paths(
    repo_root: Path,
    *,
    changed_files: list[str] | None = None,
    changed_file_list: Path | None = None,
    staged: bool = False,
    base_ref: str | None = None,
) -> dict[str, Any]:
    explicit = [_normalize_path(item) for item in (changed_files or []) if _normalize_path(item)]
    if explicit:
        return {
            "mode": "explicit",
            "command": None,
            "exit_code": 0,
            "paths": explicit,
        }

    if changed_file_list is not None:
        if not changed_file_list.exists():
            return {
                "mode": "file_list",
                "command": str(changed_file_list),
                "exit_code": 1,
                "paths": [],
                "error": f"changed file list not found: {changed_file_list}",
            }
        return {
            "mode": "file_list",
            "command": str(changed_file_list),
            "exit_code": 0,
            "paths": _parse_changed_lines(changed_file_list.read_text(encoding="utf-8")),
        }

    if staged:
        command = [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--name-only",
            "--cached",
            "--diff-filter=ACMRD",
        ]
    elif base_ref:
        command = [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--name-only",
            "--diff-filter=ACMRD",
            f"{base_ref}...HEAD",
        ]
    else:
        command = ["git", "-C", str(repo_root), "status", "--porcelain=v1"]

    proc = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "mode": "git",
        "command": _display_command(command),
        "exit_code": int(proc.returncode),
        "paths": _parse_changed_lines(proc.stdout) if proc.returncode == 0 else [],
        "stderr": proc.stderr.strip(),
    }


def _match_rule(
    path: str,
    *,
    blocked_files: tuple[str, ...],
    blocked_globs: tuple[str, ...],
    blocked_prefixes: tuple[str, ...],
    allowed_paths: tuple[str, ...],
) -> dict[str, str] | None:
    normalized = _normalize_path(path)
    if any(normalized == _normalize_path(item) for item in allowed_paths):
        return None

    for blocked_file in blocked_files:
        if normalized == _normalize_path(blocked_file):
            return {"rule_type": "file", "rule": _normalize_path(blocked_file)}
    for blocked_prefix in blocked_prefixes:
        prefix = _normalize_path(blocked_prefix)
        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"
        if normalized.startswith(prefix):
            return {"rule_type": "prefix", "rule": prefix}
    for blocked_glob in blocked_globs:
        if fnmatch.fnmatch(normalized, _normalize_path(blocked_glob)):
            return {"rule_type": "glob", "rule": _normalize_path(blocked_glob)}
    return None


def build_report(
    *,
    repo_root: Path,
    changed_files: list[str] | None = None,
    changed_file_list: Path | None = None,
    staged: bool = False,
    base_ref: str | None = None,
    blocked_files: tuple[str, ...] = DEFAULT_BLOCKED_FILES,
    blocked_globs: tuple[str, ...] = DEFAULT_BLOCKED_GLOBS,
    blocked_prefixes: tuple[str, ...] = DEFAULT_BLOCKED_PREFIXES,
    allowed_paths: tuple[str, ...] = (),
) -> dict[str, Any]:
    collection = collect_changed_paths(
        repo_root=repo_root,
        changed_files=changed_files,
        changed_file_list=changed_file_list,
        staged=staged,
        base_ref=base_ref,
    )
    violations: list[dict[str, str]] = []
    for path in collection.get("paths", []):
        match = _match_rule(
            path,
            blocked_files=blocked_files,
            blocked_globs=blocked_globs,
            blocked_prefixes=blocked_prefixes,
            allowed_paths=allowed_paths,
        )
        if match is None:
            continue
        violations.append(
            {
                "path": path,
                "rule_type": match["rule_type"],
                "rule": match["rule"],
            }
        )

    ok = collection.get("exit_code", 1) == 0 and not violations
    return {
        "generated_at": _iso_now(),
        "ok": ok,
        "repo_root": str(repo_root),
        "collection": {
            "mode": collection.get("mode", "unknown"),
            "command": collection.get("command"),
            "exit_code": collection.get("exit_code"),
            "error": collection.get("error", ""),
            "stderr": collection.get("stderr", ""),
        },
        "changed_paths": list(collection.get("paths", [])),
        "changed_path_count": len(collection.get("paths", [])),
        "blocked_files": list(blocked_files),
        "blocked_globs": list(blocked_globs),
        "blocked_prefixes": list(blocked_prefixes),
        "allowed_paths": list(allowed_paths),
        "violations": violations,
        "violation_count": len(violations),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify protected paths are untouched.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file", action="append", default=[], help="Explicit changed path."
    )
    parser.add_argument(
        "--changed-file-list",
        type=Path,
        help="Path to newline-delimited changed file list.",
    )
    parser.add_argument("--staged", action="store_true", help="Inspect staged changes.")
    parser.add_argument("--base-ref", help="Compare against base ref using git diff <base>...HEAD.")
    parser.add_argument("--allow-path", action="append", default=[], help="Explicit allowed path.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on violations.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    payload = build_report(
        repo_root=repo_root,
        changed_files=list(args.changed_file or []),
        changed_file_list=args.changed_file_list.resolve() if args.changed_file_list else None,
        staged=bool(args.staged),
        base_ref=str(args.base_ref).strip() if args.base_ref else None,
        allowed_paths=tuple(
            _normalize_path(item) for item in (args.allow_path or []) if _normalize_path(item)
        ),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["collection"]["exit_code"] != 0:
        return 1
    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
