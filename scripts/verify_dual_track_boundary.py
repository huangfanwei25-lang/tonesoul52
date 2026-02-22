"""
Dual-track boundary verifier.

Blocks public-repo changes that touch private-track paths.
"""

from __future__ import annotations

import argparse
import codecs
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
    "memory/memory/.semantic_index/",
    "memory/memory/.hierarchical_index/",
    ".agent/",
    "obsidian-vault/",
    "simulation_logs/",
    "reports/ystm_demo/",
    "generated_prompts/",
    ".moltbook/",
)
DEFAULT_BLOCKED_FILES = (
    "memory/self_journal.jsonl",
    "memory/agent_discussion.jsonl",
    "memory/agent_discussion_curated.jsonl",
    "memory/agent_discussion.jsonl.bak.20260206T145513Z",
    "memory/agent_discussion_antigravity_response.jsonl",
    "memory/summary_balls.jsonl",
    "memory/ANTIGRAVITY_SYNC.md",
    "memory/BOOTSTRAP.md",
    "memory/antigravity_journal.md",
    "memory/antigravity_memory_20260129.md",
    "memory/dawn_protocol_v10.md",
    "memory/guild_recruitment_post.md",
    "memory/moltbook_exploration.md",
    "memory/persona_synthesis_v5.md",
    "memory/persona_synthesis_v8.md",
    "memory/resonance_drafts.md",
    "memory/resonance_report_v1.md",
    "memory/silence_of_xiaozhua_v7.md",
    "memory/web_chat_debug.md",
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
    normalized = path.strip()
    if len(normalized) >= 2 and normalized.startswith('"') and normalized.endswith('"'):
        unquoted = normalized[1:-1]
        try:
            # Git may quote non-ascii paths as C-style octal escapes when core.quotepath=true.
            decoded = codecs.decode(unquoted, "unicode_escape")
            try:
                decoded = decoded.encode("latin-1").decode("utf-8")
            except UnicodeError:
                # Keep partially decoded output if utf-8 roundtrip is unavailable.
                pass
            normalized = decoded
        except Exception:
            normalized = unquoted
    normalized = normalized.replace("\\", "/").strip()
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
        path = _normalize_path(raw.lstrip("\ufeff"))
        if not path or path in seen:
            continue
        seen.add(path)
        results.append(path)
    return results


def _is_status_token(token: str) -> bool:
    if not token:
        return False
    return token[0].upper() in {"A", "C", "M", "R", "D", "T", "U", "X", "B"}


def _parse_changed_entries(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for raw_line in text.splitlines():
        line = raw_line.lstrip("\ufeff").strip()
        if not line:
            continue

        status_code = "UNSPECIFIED"
        status = "UNSPECIFIED"
        raw_paths: list[str] = [line]

        parts = line.split("\t")
        if len(parts) >= 2 and _is_status_token(parts[0].strip()):
            status_code = parts[0].strip().upper()
            status = status_code[0]
            raw_paths = parts[1:]

        paths: list[str] = []
        seen_path: set[str] = set()
        for raw_path in raw_paths:
            normalized = _normalize_path(raw_path)
            if not normalized or normalized in seen_path:
                continue
            seen_path.add(normalized)
            paths.append(normalized)

        if not paths:
            continue

        dedupe_key = (status_code, tuple(paths))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        entries.append({"status_code": status_code, "status": status, "paths": paths})

    return entries


def _collect_paths_from_entries(entries: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        for path in entry.get("paths", []):
            normalized = _normalize_path(str(path))
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            paths.append(normalized)
    return paths


def _read_text_with_fallback(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data:
        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _load_changed_file_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return _parse_changed_entries(_read_text_with_fallback(path))


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
        parsed_entries = _parse_changed_entries("\n".join(changed_files))
        return {
            "ok": True,
            "mode": "explicit",
            "command": None,
            "exit_code": 0,
            "stdout_tail": "",
            "stderr_tail": "",
            "entries": parsed_entries,
            "paths": _collect_paths_from_entries(parsed_entries),
        }

    if changed_file_list is not None:
        parsed_entries = _load_changed_file_list(changed_file_list)
        return {
            "ok": True,
            "mode": "file_list",
            "command": str(changed_file_list.as_posix()),
            "exit_code": 0,
            "stdout_tail": "",
            "stderr_tail": "",
            "entries": parsed_entries,
            "paths": _collect_paths_from_entries(parsed_entries),
        }

    if staged:
        command = [
            "git",
            "-c",
            "core.quotepath=off",
            "diff",
            "--name-status",
            "--cached",
            "--diff-filter=ACMRD",
        ]
    elif base_ref:
        command = [
            "git",
            "-c",
            "core.quotepath=off",
            "diff",
            "--name-status",
            "--diff-filter=ACMRD",
            f"{base_ref}...HEAD",
        ]
    else:
        command = [
            "git",
            "-c",
            "core.quotepath=off",
            "show",
            "--pretty=format:",
            "--name-status",
            "--diff-filter=ACMRD",
            "HEAD",
        ]

    started = time.perf_counter()
    exit_code, stdout, stderr = runner(command, repo_root)
    duration = round(time.perf_counter() - started, 2)
    parsed_entries = _parse_changed_entries(stdout)
    return {
        "ok": exit_code == 0,
        "mode": "git",
        "command": _display_command(command),
        "exit_code": exit_code,
        "duration_seconds": duration,
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
        "entries": parsed_entries,
        "paths": _collect_paths_from_entries(parsed_entries),
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
    private_deletion_count = 0

    entries = collection.get("entries")
    if not isinstance(entries, list):
        legacy_paths = collection.get("paths", [])
        if isinstance(legacy_paths, list):
            entries = [
                {"status_code": "UNSPECIFIED", "status": "UNSPECIFIED", "paths": [str(path)]}
                for path in legacy_paths
            ]
        else:
            entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("status") or "UNSPECIFIED").strip().upper()
        paths = entry.get("paths", [])
        if not isinstance(paths, list):
            continue

        matched_blocked_paths: list[dict[str, str]] = []
        for raw_path in paths:
            path = _normalize_path(str(raw_path))
            if not path:
                continue
            matched = _match_block_rule(
                path,
                blocked_prefixes=blocked_prefixes,
                blocked_files=blocked_files,
            )
            if matched is None:
                continue
            matched_blocked_paths.append({"path": path, **matched})

        if not matched_blocked_paths:
            continue

        if status == "D":
            private_deletion_count += len(matched_blocked_paths)
            continue

        for item in matched_blocked_paths:
            violations.append({**item, "status": status})

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
    if private_deletion_count:
        warnings.append(
            f"detected {private_deletion_count} deletions under blocked private paths "
            "(allowed cleanup)"
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
            "private_deletion_count": private_deletion_count,
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
        f"- private_deletion_count: {payload['metrics'].get('private_deletion_count', 0)}",
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
        lines.append("| path | status | rule_type | rule |")
        lines.append("| --- | --- | --- | --- |")
        for item in payload["violations"]:
            lines.append(
                f"| `{item['path']}` | {item.get('status', 'UNSPECIFIED')} | "
                f"{item['rule_type']} | `{item['rule']}` |"
            )

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
