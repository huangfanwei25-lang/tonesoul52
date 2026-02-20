"""
Git hygiene verifier.

Checks repository object-store hygiene and integrity signals:
- `git count-objects -vH` for loose object pressure.
- `git fsck --no-reflogs` for dangling/non-dangling object diagnostics.
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
from typing import Any

JSON_FILENAME = "git_hygiene_latest.json"
MARKDOWN_FILENAME = "git_hygiene_latest.md"
DEFAULT_MAX_DANGLING = 50
DEFAULT_MAX_LOOSE_COUNT = 5000
DEFAULT_MAX_TRACKED_IGNORED = 0


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


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_count_objects(stdout: str) -> dict[str, Any]:
    values: dict[str, str] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()

    return {
        "values": values,
        "loose_count": _parse_int(values.get("count")),
        "in_pack": _parse_int(values.get("in-pack")),
        "packs": _parse_int(values.get("packs")),
        "garbage": _parse_int(values.get("garbage")),
        "size": values.get("size"),
        "size_pack": values.get("size-pack"),
    }


def _summarize_fsck(stdout: str) -> dict[str, Any]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    prefix_counts: dict[str, int] = {}
    unexpected_lines: list[str] = []

    for line in lines:
        prefix = line.split(" ", 1)[0]
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        if prefix != "dangling":
            unexpected_lines.append(line)

    return {
        "line_count": len(lines),
        "prefix_counts": prefix_counts,
        "dangling_count": prefix_counts.get("dangling", 0),
        "unexpected_lines": unexpected_lines,
    }


def _parse_tracked_ignored(stdout: str) -> list[str]:
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def build_report(
    repo_root: Path,
    max_dangling: int = DEFAULT_MAX_DANGLING,
    max_loose_count: int = DEFAULT_MAX_LOOSE_COUNT,
    max_tracked_ignored: int = DEFAULT_MAX_TRACKED_IGNORED,
    runner=_run_command,
) -> dict[str, Any]:
    issues: list[str] = []
    checks: list[dict[str, Any]] = []

    count_cmd = ["git", "count-objects", "-vH"]
    started = time.perf_counter()
    count_exit, count_stdout, count_stderr = runner(count_cmd, repo_root)
    count_duration = round(time.perf_counter() - started, 2)
    count_parsed = _parse_count_objects(count_stdout)
    loose_count = count_parsed["loose_count"]
    count_ok = count_exit == 0

    if count_exit != 0:
        issues.append("git count-objects -vH failed")
    if loose_count is None:
        count_ok = False
        issues.append("unable to parse loose object count from git count-objects output")
    elif loose_count > max_loose_count:
        count_ok = False
        issues.append(f"loose object count {loose_count} exceeds threshold {max_loose_count}")

    checks.append(
        {
            "name": "count_objects",
            "status": "pass" if count_ok else "fail",
            "ok": count_ok,
            "exit_code": count_exit,
            "duration_seconds": count_duration,
            "command": _display_command(count_cmd),
            "stdout_tail": _tail(count_stdout),
            "stderr_tail": _tail(count_stderr),
        }
    )

    fsck_cmd = ["git", "fsck", "--no-reflogs"]
    started = time.perf_counter()
    fsck_exit, fsck_stdout, fsck_stderr = runner(fsck_cmd, repo_root)
    fsck_duration = round(time.perf_counter() - started, 2)
    fsck_summary = _summarize_fsck(fsck_stdout)
    dangling_count = fsck_summary["dangling_count"]
    fsck_ok = fsck_exit == 0

    if fsck_exit != 0:
        issues.append("git fsck --no-reflogs returned non-zero exit")
    if dangling_count > max_dangling:
        fsck_ok = False
        issues.append(f"dangling objects {dangling_count} exceeds threshold {max_dangling}")
    if fsck_summary["unexpected_lines"]:
        fsck_ok = False
        issues.append(
            f"git fsck reported non-dangling diagnostics ({len(fsck_summary['unexpected_lines'])})"
        )

    checks.append(
        {
            "name": "fsck",
            "status": "pass" if fsck_ok else "fail",
            "ok": fsck_ok,
            "exit_code": fsck_exit,
            "duration_seconds": fsck_duration,
            "command": _display_command(fsck_cmd),
            "stdout_tail": _tail(fsck_stdout),
            "stderr_tail": _tail(fsck_stderr),
        }
    )

    tracked_cmd = ["git", "ls-files", "-ci", "--exclude-standard"]
    started = time.perf_counter()
    tracked_exit, tracked_stdout, tracked_stderr = runner(tracked_cmd, repo_root)
    tracked_duration = round(time.perf_counter() - started, 2)
    tracked_ignored_paths = _parse_tracked_ignored(tracked_stdout)
    tracked_ignored_count = len(tracked_ignored_paths)
    tracked_ok = tracked_exit == 0

    if tracked_exit != 0:
        issues.append("git ls-files -ci --exclude-standard failed")
    if tracked_ignored_count > max_tracked_ignored:
        tracked_ok = False
        issues.append(
            f"tracked-ignored files {tracked_ignored_count} exceeds threshold {max_tracked_ignored}"
        )

    checks.append(
        {
            "name": "tracked_ignored",
            "status": "pass" if tracked_ok else "fail",
            "ok": tracked_ok,
            "exit_code": tracked_exit,
            "duration_seconds": tracked_duration,
            "command": _display_command(tracked_cmd),
            "stdout_tail": _tail(tracked_stdout),
            "stderr_tail": _tail(tracked_stderr),
        }
    )

    overall_ok = all(item["ok"] for item in checks)
    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "config": {
            "max_dangling": max_dangling,
            "max_loose_count": max_loose_count,
            "max_tracked_ignored": max_tracked_ignored,
        },
        "metrics": {
            "loose_count": loose_count,
            "in_pack": count_parsed["in_pack"],
            "packs": count_parsed["packs"],
            "size": count_parsed["size"],
            "size_pack": count_parsed["size_pack"],
            "dangling_count": dangling_count,
            "fsck_prefix_counts": fsck_summary["prefix_counts"],
            "fsck_unexpected_count": len(fsck_summary["unexpected_lines"]),
            "tracked_ignored_count": tracked_ignored_count,
        },
        "checks": checks,
        "issues": issues,
        "fsck_unexpected_lines": fsck_summary["unexpected_lines"],
        "tracked_ignored_paths": tracked_ignored_paths,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Git Hygiene Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- max_dangling: {payload['config']['max_dangling']}",
        f"- max_loose_count: {payload['config']['max_loose_count']}",
        f"- max_tracked_ignored: {payload['config']['max_tracked_ignored']}",
        "",
        "| check | status | exit | duration_s | command |",
        "| --- | --- | ---: | ---: | --- |",
    ]

    for check in payload["checks"]:
        lines.append(
            f"| {check['name']} | {check['status'].upper()} | {check['exit_code']} | "
            f"{float(check['duration_seconds']):.2f} | `{check['command']}` |"
        )

    metrics = payload["metrics"]
    lines.extend(
        [
            "",
            "## Metrics",
            f"- loose_count: {metrics['loose_count']}",
            f"- in_pack: {metrics['in_pack']}",
            f"- packs: {metrics['packs']}",
            f"- size: {metrics['size']}",
            f"- size_pack: {metrics['size_pack']}",
            f"- dangling_count: {metrics['dangling_count']}",
            f"- fsck_unexpected_count: {metrics['fsck_unexpected_count']}",
            f"- tracked_ignored_count: {metrics['tracked_ignored_count']}",
        ]
    )

    if payload["issues"]:
        lines.append("")
        lines.append("## Issues")
        for issue in payload["issues"]:
            lines.append(f"- {issue}")

    if payload["fsck_unexpected_lines"]:
        lines.append("")
        lines.append("## Unexpected Fsck Lines")
        for line in payload["fsck_unexpected_lines"][:20]:
            lines.append(f"- `{line}`")

    if payload["tracked_ignored_paths"]:
        lines.append("")
        lines.append("## Tracked Ignored Files")
        for path in payload["tracked_ignored_paths"][:20]:
            lines.append(f"- `{path}`")

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
    parser = argparse.ArgumentParser(description="Verify git object-store hygiene.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--max-dangling",
        type=int,
        default=DEFAULT_MAX_DANGLING,
        help="Maximum allowed dangling-object count.",
    )
    parser.add_argument(
        "--max-loose-count",
        type=int,
        default=DEFAULT_MAX_LOOSE_COUNT,
        help="Maximum allowed loose-object count.",
    )
    parser.add_argument(
        "--max-tracked-ignored",
        type=int,
        default=DEFAULT_MAX_TRACKED_IGNORED,
        help="Maximum allowed tracked files that match ignore rules.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when hygiene checks do not pass.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()

    payload = build_report(
        repo_root=repo_root,
        max_dangling=max(0, int(args.max_dangling)),
        max_loose_count=max(0, int(args.max_loose_count)),
        max_tracked_ignored=max(0, int(args.max_tracked_ignored)),
    )
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
