#!/usr/bin/env python3
"""Read-only bootstrap doctor for fresh ToneSoul environments."""

from __future__ import annotations

import argparse
import configparser
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

__ts_layer__ = "surface"
__ts_purpose__ = "Read-only bootstrap doctor for fresh ToneSoul environments"

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_MIN_VERSION = (3, 10)
DEFAULT_TIMEOUT_SECONDS = 8
# xdist added 2026-07-04: doctor's day-one incident — audit_7d's TDD tier failed
# with "unrecognized arguments: -n" because THIS list didn't probe pytest-xdist,
# so doctor said PASS while the test tier could not run. Probe what the tiers use.
DEV_MODULES = ("pytest", "hypothesis", "freezegun", "flask", "black", "ruff", "xdist")
OPTIONAL_TOOLS = {
    "codex": ("codex", "--version"),
    "gh": ("gh", "--version"),
    "ollama": ("ollama", "--version"),
}


def result(
    check: str,
    status: str,
    detail: str,
    *,
    repair: str | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"check": check, "status": status, "detail": detail}
    if repair:
        item["repair"] = repair
    if data:
        item["data"] = data
    return item


def _run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            cwd=str(cwd) if cwd else None,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        return 127, "", f"command not found: {exc}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    return proc.returncode, proc.stdout.rstrip(), proc.stderr.rstrip()


def _first_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if clean:
            return clean
    return ""


def _module_available(module: str, *, repo_root: Path | None = None) -> bool:
    inserted = False
    root = str(repo_root) if repo_root else None
    if root and root not in sys.path:
        sys.path.insert(0, root)
        inserted = True
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False
    finally:
        if inserted:
            try:
                sys.path.remove(root)
            except ValueError:
                pass


def check_python_version(version_info: tuple[int, int, int] | None = None) -> dict[str, Any]:
    version = version_info or sys.version_info[:3]
    version_text = ".".join(str(part) for part in version)
    min_text = ".".join(str(part) for part in PYTHON_MIN_VERSION)
    if version >= PYTHON_MIN_VERSION:
        return result(
            "python.version",
            "PASS",
            f"Python {version_text} satisfies >= {min_text}",
            data={"version": version_text},
        )
    return result(
        "python.version",
        "GAP",
        f"Python {version_text} is below required >= {min_text}",
        repair="Install Python 3.10+ and recreate the virtualenv",
        data={"version": version_text},
    )


def check_module(
    module: str,
    check: str,
    *,
    repo_root: Path | None = None,
    repair: str = 'pip install -e ".[dev]"',
) -> dict[str, Any]:
    if _module_available(module, repo_root=repo_root):
        return result(check, "PASS", f"module {module!r} is import-discoverable")
    return result(
        check,
        "GAP",
        f"module {module!r} is missing",
        repair=repair,
    )


def _git_metadata_exists(repo_root: Path) -> bool:
    return (repo_root / ".git").exists()


def check_git(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    git_path = shutil.which("git")
    if not git_path:
        return result(
            "git.executable",
            "GAP",
            "git is not on PATH; zip/source users cannot inspect checkout state",
            repair="Install Git, then use a git clone of the repository",
        )

    if not _git_metadata_exists(repo_root):
        return result(
            "git.checkout",
            "GAP",
            "no .git metadata found; this looks like a source zip, not a git checkout",
            repair="Use a git clone instead of a source zip",
        )

    rc, stdout, stderr = _run_command(
        [git_path, "rev-parse", "--is-inside-work-tree"],
        cwd=repo_root,
    )
    if rc == 0 and stdout == "true":
        version_rc, version_out, version_err = _run_command([git_path, "--version"], cwd=repo_root)
        version = _first_line(version_out or version_err)
        detail = "git checkout detected"
        if version_rc == 0 and version:
            detail = f"{detail}; {version}"
        return result("git.checkout", "PASS", detail)

    reason = _first_line(stderr or stdout) or f"git rev-parse exited {rc}"
    return result(
        "git.checkout",
        "GAP",
        f"git metadata exists but checkout validation failed: {reason}",
        repair="Run doctor from a valid git checkout of the repository",
    )


def _gitmodule_paths(repo_root: Path) -> list[str]:
    gitmodules_path = repo_root / ".gitmodules"
    if not gitmodules_path.exists():
        return []

    parser = configparser.ConfigParser()
    parser.read(gitmodules_path, encoding="utf-8")
    paths: list[str] = []
    for section in parser.sections():
        if section.startswith("submodule ") and parser.has_option(section, "path"):
            paths.append(parser.get(section, "path"))
    return paths


def _empty_or_missing_submodule_paths(repo_root: Path, paths: list[str]) -> list[str]:
    empty_or_missing: list[str] = []
    for rel_path in paths:
        submodule_path = repo_root / rel_path
        if not submodule_path.exists():
            empty_or_missing.append(rel_path)
        elif submodule_path.is_dir() and not any(submodule_path.iterdir()):
            empty_or_missing.append(rel_path)
    return empty_or_missing


def check_submodules(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    paths = _gitmodule_paths(repo_root)
    if not paths:
        return result("git.submodules", "SKIP", "no .gitmodules file or no declared submodules")

    missing = _empty_or_missing_submodule_paths(repo_root, paths)
    if missing:
        return result(
            "git.submodules",
            "GAP",
            "submodule path empty or missing: " + ", ".join(missing),
            repair="git submodule update --init",
            data={"paths": paths, "empty_or_missing": missing},
        )

    git_path = shutil.which("git")
    if not git_path:
        return result(
            "git.submodules",
            "GAP",
            "git is not on PATH; cannot inspect declared submodules",
            repair="Install Git, then run git submodule update --init",
            data={"paths": paths},
        )

    if not _git_metadata_exists(repo_root):
        return result(
            "git.submodules",
            "GAP",
            "declared submodules exist, but .git metadata is absent; source zip cannot verify status",
            repair="Use a git clone, then run git submodule update --init",
            data={"paths": paths},
        )

    rc, stdout, stderr = _run_command(
        [git_path, "submodule", "status", "--recursive"],
        cwd=repo_root,
    )
    if rc != 0:
        reason = _first_line(stderr or stdout) or f"git submodule status exited {rc}"
        return result(
            "git.submodules",
            "GAP",
            f"could not inspect submodules: {reason}",
            repair="git submodule update --init",
            data={"paths": paths},
        )

    if not stdout.strip():
        return result(
            "git.submodules",
            "GAP",
            "git submodule status returned no rows for declared submodules",
            repair="git submodule update --init",
            data={"paths": paths},
        )

    uninitialized: list[str] = []
    drifted: list[str] = []
    conflicted: list[str] = []
    unknown: list[str] = []
    for line in stdout.splitlines():
        if not line:
            continue
        marker = line[0]
        rel_path = (
            line[1:].strip().split(maxsplit=1)[1].split()[0] if len(line.split()) > 1 else line
        )
        if marker == "-":
            uninitialized.append(rel_path)
        elif marker == "+":
            drifted.append(rel_path)
        elif marker == "U":
            conflicted.append(rel_path)
        elif marker != " ":
            unknown.append(line.strip())

    if uninitialized or drifted or conflicted or unknown:
        problems: list[str] = []
        if uninitialized:
            problems.append("uninitialized: " + ", ".join(uninitialized))
        if drifted:
            problems.append("drifted: " + ", ".join(drifted))
        if conflicted:
            problems.append("conflicted: " + ", ".join(conflicted))
        if unknown:
            problems.append("unknown: " + ", ".join(unknown))
        return result(
            "git.submodules",
            "GAP",
            "; ".join(problems),
            repair="git submodule update --init",
            data={
                "paths": paths,
                "uninitialized": uninitialized,
                "drifted": drifted,
                "conflicted": conflicted,
                "unknown": unknown,
            },
        )

    return result(
        "git.submodules",
        "PASS",
        "all declared submodules are initialized and match the recorded commits",
        data={"paths": paths},
    )


def check_required_tool(tool: str, repair: str) -> dict[str, Any]:
    tool_path = shutil.which(tool)
    if not tool_path:
        return result(
            f"{tool}.executable",
            "GAP",
            f"{tool} is not on PATH",
            repair=repair,
        )

    rc, stdout, stderr = _run_command([tool_path, "--version"])
    version = _first_line(stdout or stderr)
    if rc == 0 and version:
        return result(f"{tool}.executable", "PASS", version)
    return result(
        f"{tool}.executable",
        "PASS",
        f"{tool} found at {tool_path}; version probe unavailable",
    )


def check_node_modules(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    web_app = repo_root / "apps" / "web"
    if not web_app.exists():
        return result("node.modules", "SKIP", "apps/web does not exist in this checkout")

    node_modules = web_app / "node_modules"
    if node_modules.exists():
        return result("node.modules", "PASS", "apps/web/node_modules exists")

    return result(
        "node.modules",
        "GAP",
        "apps/web/node_modules is missing",
        repair="npm --prefix apps/web install",
    )


def check_optional_tool(tool: str, command: tuple[str, ...]) -> dict[str, Any]:
    tool_path = shutil.which(tool)
    if not tool_path:
        return result(f"optional.{tool}", "SKIP", f"{tool} is not installed; optional tool")

    rc, stdout, stderr = _run_command([tool_path, *command[1:]])
    version = _first_line(stdout or stderr)
    if rc == 0 and version:
        return result(f"optional.{tool}", "PASS", version)
    return result(
        f"optional.{tool}",
        "PASS",
        f"{tool} found at {tool_path}; version probe unavailable",
    )


def run_all_checks(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = [
        check_python_version(),
        check_module("tonesoul", "python.import.tonesoul", repo_root=repo_root),
    ]
    for module in DEV_MODULES:
        checks.append(check_module(module, f"python.import.{module}"))

    checks.extend(
        [
            check_git(repo_root),
            check_submodules(repo_root),
            check_required_tool("node", "Install Node.js, then rerun doctor"),
            check_required_tool("npm", "Install npm with Node.js, then rerun doctor"),
            check_node_modules(repo_root),
        ]
    )
    for tool, command in OPTIONAL_TOOLS.items():
        checks.append(check_optional_tool(tool, command))
    return checks


def summarize(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "pass": sum(1 for item in checks if item["status"] == "PASS"),
        "gap": sum(1 for item in checks if item["status"] == "GAP"),
        "skip": sum(1 for item in checks if item["status"] == "SKIP"),
    }


def exit_code_for(checks: list[dict[str, Any]]) -> int:
    return 1 if any(item["status"] == "GAP" for item in checks) else 0


def manifest_for(checks: list[dict[str, Any]]) -> dict[str, Any]:
    counts = summarize(checks)
    return {
        "tool": "scripts/doctor.py",
        "schema_version": 1,
        "platform": {
            "python": platform.python_version(),
            "system": platform.system(),
            "release": platform.release(),
        },
        "summary": {**counts, "exit_code": exit_code_for(checks)},
        "checks": checks,
    }


def _unique_repairs(checks: list[dict[str, Any]]) -> list[str]:
    repairs: list[str] = []
    for item in checks:
        repair = item.get("repair")
        if item["status"] == "GAP" and repair and repair not in repairs:
            repairs.append(repair)
    return repairs


def render_text(checks: list[dict[str, Any]]) -> str:
    counts = summarize(checks)
    lines = ["[ToneSoul doctor] read-only environment diagnostic"]
    for item in checks:
        lines.append(f"[{item['status']}] {item['check']}: {item['detail']}")
        if item["status"] == "GAP" and item.get("repair"):
            lines.append(f"        fix: {item['repair']}")

    lines.append("")
    lines.append(
        "Summary: "
        f"PASS={counts['pass']} GAP={counts['gap']} SKIP={counts['skip']} "
        f"exit={exit_code_for(checks)}"
    )

    repairs = _unique_repairs(checks)
    if repairs:
        lines.append("")
        lines.append("Copyable repair commands:")
        for repair in repairs:
            lines.append(f"  - {repair}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit structured JSON only")
    args = parser.parse_args(argv)

    checks = run_all_checks()
    if args.json:
        print(json.dumps(manifest_for(checks), indent=2, ensure_ascii=False))
    else:
        print(render_text(checks))
    return exit_code_for(checks)


if __name__ == "__main__":
    sys.exit(main())
