"""
Verify git submodule metadata consistency.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

JSON_FILENAME = "submodule_integrity_latest.json"
MARKDOWN_FILENAME = "submodule_integrity_latest.md"


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


def _parse_gitlinks(ls_files_stdout: str) -> dict[str, str]:
    results: dict[str, str] = {}
    for raw_line in ls_files_stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        mode = parts[0]
        sha = parts[1]
        path = parts[3]
        if mode == "160000":
            results[path] = sha
    return results


def _parse_gitmodules(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    result: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        name = section.split('"', 2)[1] if '"' in section else section
        entry_path = parser.get(section, "path", fallback="").strip()
        url = parser.get(section, "url", fallback="").strip()
        result[name] = {"path": entry_path, "url": url}
    return result


def build_report(
    repo_root: Path,
    runner: Callable[[list[str], Path], tuple[int, str, str]] = _run_command,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    ls_code, ls_out, ls_err = runner(["git", "ls-files", "-s"], repo_root)
    gitlinks: dict[str, str] = {}
    if ls_code != 0:
        issues.append("failed to read git index entries via `git ls-files -s`")
    else:
        gitlinks = _parse_gitlinks(ls_out)

    gitmodules_path = repo_root / ".gitmodules"
    try:
        mappings = _parse_gitmodules(gitmodules_path)
    except (configparser.Error, UnicodeError) as exc:
        mappings = {}
        issues.append(f"failed to parse .gitmodules: {exc}")

    mapped_paths = {
        details["path"]: details["url"] for details in mappings.values() if details.get("path")
    }

    if gitlinks and not gitmodules_path.exists():
        issues.append("gitlinks present but .gitmodules is missing")

    for path in sorted(gitlinks):
        if path not in mapped_paths:
            issues.append(f"gitlink path missing in .gitmodules: {path}")
            continue
        if not mapped_paths[path]:
            issues.append(f"submodule url missing for path: {path}")

    for path in sorted(mapped_paths):
        if path not in gitlinks:
            warnings.append(f".gitmodules contains path not tracked as gitlink: {path}")

    status_code, status_out, status_err = runner(["git", "submodule", "status"], repo_root)
    if status_code != 0:
        issues.append("`git submodule status` returned non-zero")
    status_lines = [line.strip() for line in status_out.splitlines() if line.strip()]
    not_initialized = [line for line in status_lines if line.startswith("-")]
    if not_initialized:
        warnings.append(f"{len(not_initialized)} submodule(s) not initialized in current checkout")

    return {
        "overall_ok": len(issues) == 0,
        "repo_root": str(repo_root),
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "gitlinks": gitlinks,
        "gitmodules": mappings,
        "submodule_status_lines": status_lines,
        "issues": issues,
        "warnings": warnings,
        "commands": {
            "ls_files": {
                "exit_code": ls_code,
                "stderr_tail": ls_err.strip()[-1000:],
            },
            "submodule_status": {
                "exit_code": status_code,
                "stderr_tail": status_err.strip()[-1000:],
            },
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Submodule Integrity Latest",
        "",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- issue_count: {payload['issue_count']}",
        f"- warning_count: {payload['warning_count']}",
        f"- gitlink_count: {len(payload['gitlinks'])}",
        f"- gitmodules_count: {len(payload['gitmodules'])}",
        "",
        "## Gitlinks",
    ]
    if payload["gitlinks"]:
        for path, sha in sorted(payload["gitlinks"].items()):
            lines.append(f"- `{path}` @ `{sha}`")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Issues")
    if payload["issues"]:
        for issue in payload["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify submodule metadata integrity.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when submodule integrity issues are found.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root=repo_root)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
