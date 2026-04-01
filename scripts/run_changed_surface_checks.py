#!/usr/bin/env python3
"""Plan and optionally execute verification checks for the current change surface.

Purpose:
- convert changed files into explicit verification surfaces
- reduce hidden cross-file joins that agents currently do implicitly
- provide one hook-friendly artifact showing which checks should run
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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.verify_protected_paths as protected_paths  # noqa: E402

JSON_FILENAME = "changed_surface_checks_latest.json"
MARKDOWN_FILENAME = "changed_surface_checks_latest.md"
MAX_TARGETED_TESTS = 12
ROOT_DOC_FILES = {
    "README.md",
    "AI_ONBOARDING.md",
    "task.md",
    "CODEX_TASK.md",
    "CODEX_HANDBACK.md",
    "PHILOSOPHY.md",
}
DOC_PREFIXES = (
    "docs/",
    "語魂系統GPTs_v1.1/",
    ".github/workflows/",
)
WEB_PREFIX = "apps/web/"
CORE_RUNTIME_PREFIXES = (
    "tonesoul/governance/",
    "tonesoul/council/",
    "tonesoul/memory/",
    "tonesoul/llm/",
    "tonesoul/deliberation/",
    "tonesoul/unified_pipeline.py",
    "tonesoul/tension_engine.py",
    "tonesoul/dream_engine.py",
    "tonesoul/wakeup_loop.py",
    "apps/api/",
    "apps/web/src/app/api/chat/",
)

CheckRunner = Callable[[str, list[str], Path], dict[str, Any]]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _display_command(command: list[str]) -> str:
    rendered: list[str] = []
    for index, token in enumerate(command):
        text = str(token)
        if index == 0:
            executable = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable.startswith("python"):
                rendered.append("python")
                continue
            if executable in {"npm", "npm.cmd"}:
                rendered.append("npm")
                continue
            if executable in {"git", "git.exe"}:
                rendered.append("git")
                continue
        rendered.append(text)
    return " ".join(rendered)


def _tail(text: str, limit: int = 1200) -> str:
    payload = text.strip()
    if len(payload) <= limit:
        return payload
    return payload[-limit:]


def _npm_executable() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def _resolve_optional_path(repo_root: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def _is_doc_governance_path(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized in ROOT_DOC_FILES:
        return True
    return any(normalized.startswith(prefix) for prefix in DOC_PREFIXES)


def _matches_any_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    normalized = _normalize_path(path)
    return any(normalized.startswith(prefix) for prefix in prefixes)


def classify_surfaces(changed_paths: list[str]) -> list[dict[str, Any]]:
    unique_paths = []
    seen: set[str] = set()
    for raw_path in changed_paths:
        normalized = _normalize_path(raw_path)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_paths.append(normalized)

    python_paths = [path for path in unique_paths if path.endswith(".py")]
    core_runtime_paths = [
        path for path in unique_paths if _matches_any_prefix(path, CORE_RUNTIME_PREFIXES)
    ]
    web_paths = [path for path in unique_paths if path.startswith(WEB_PREFIX)]
    docs_paths = [path for path in unique_paths if _is_doc_governance_path(path)]

    surfaces: list[dict[str, Any]] = []
    if python_paths:
        surfaces.append(
            {
                "id": "python_runtime",
                "label": "Python Runtime",
                "summary": "Python modules, scripts, or tests changed and need code-level verification.",
                "paths": python_paths,
                "path_count": len(python_paths),
            }
        )
    if core_runtime_paths:
        surfaces.append(
            {
                "id": "core_runtime",
                "label": "Core Runtime",
                "summary": "Governance, memory, council, or pipeline surfaces changed and need deeper regression coverage.",
                "paths": core_runtime_paths,
                "path_count": len(core_runtime_paths),
            }
        )
    if web_paths:
        surfaces.append(
            {
                "id": "web_surface",
                "label": "Web Surface",
                "summary": "Frontend or web entrypoint files changed and need web lint/test coverage.",
                "paths": web_paths,
                "path_count": len(web_paths),
            }
        )
    if docs_paths:
        surfaces.append(
            {
                "id": "docs_governance",
                "label": "Docs and Governance",
                "summary": "Docs, workflow, or authority files changed and need consistency verification.",
                "paths": docs_paths,
                "path_count": len(docs_paths),
            }
        )
    return surfaces


def infer_targeted_tests(repo_root: Path, changed_paths: list[str]) -> tuple[list[str], list[str]]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        normalized = _normalize_path(path)
        if not normalized or normalized in seen:
            return
        if not (repo_root / normalized).exists():
            return
        seen.add(normalized)
        candidates.append(normalized)

    def add_matches(pattern: str) -> None:
        for match in sorted(repo_root.glob(pattern)):
            if match.is_file():
                add(match.relative_to(repo_root).as_posix())

    for raw_path in changed_paths:
        path = _normalize_path(raw_path)
        if not path:
            continue
        path_obj = Path(path)
        stem = path_obj.stem
        parent = path_obj.parent.name

        if path.startswith("tests/") and path.endswith(".py"):
            add(path)
            continue

        if not path.endswith(".py"):
            continue

        add_matches(f"tests/test_{stem}.py")
        add_matches(f"tests/test_{stem}*.py")
        if parent and parent not in {".", "tonesoul", "scripts", "tests", "apps"}:
            add_matches(f"tests/test_{parent}_{stem}.py")
            add_matches(f"tests/test_{parent}_{stem}*.py")

    warnings: list[str] = []
    if len(candidates) > MAX_TARGETED_TESTS:
        warnings.append(
            "targeted pytest candidate count exceeded limit; using full regression instead"
        )
        return [], warnings
    return candidates, warnings


def requires_full_regression(changed_paths: list[str]) -> bool:
    if len(changed_paths) >= 16:
        return True
    return any(_matches_any_prefix(path, CORE_RUNTIME_PREFIXES) for path in changed_paths)


def _planned_check(
    *,
    name: str,
    argv: list[str],
    reason: str,
    surface_ids: list[str],
    blocking: bool,
) -> dict[str, Any]:
    return {
        "name": name,
        "argv": list(argv),
        "command": _display_command(argv),
        "reason": reason,
        "surface_ids": sorted({surface_id for surface_id in surface_ids if surface_id}),
        "blocking": bool(blocking),
        "status": "planned",
        "ok": None,
        "exit_code": None,
        "duration_seconds": 0.0,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def build_check_plan(
    *,
    repo_root: Path,
    changed_paths: list[str],
    allow_paths: tuple[str, ...] = (),
    python_executable: str = sys.executable,
) -> tuple[list[dict[str, Any]], list[str]]:
    normalized_paths = [_normalize_path(path) for path in changed_paths if _normalize_path(path)]
    surfaces = classify_surfaces(normalized_paths)
    surface_ids = [surface["id"] for surface in surfaces]
    python_paths = [path for path in normalized_paths if path.endswith(".py")]
    web_paths = [path for path in normalized_paths if path.startswith(WEB_PREFIX)]
    docs_paths = [path for path in normalized_paths if _is_doc_governance_path(path)]
    targeted_tests, warnings = infer_targeted_tests(repo_root, normalized_paths)
    full_regression = requires_full_regression(normalized_paths) or not targeted_tests

    changed_args: list[str] = []
    for path in normalized_paths:
        changed_args.extend(["--changed-file", path])
    allow_args: list[str] = []
    for path in allow_paths:
        normalized = _normalize_path(path)
        if normalized:
            allow_args.extend(["--allow-path", normalized])

    plan: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    def add(item: dict[str, Any]) -> None:
        if item["name"] in seen_names:
            return
        seen_names.add(item["name"])
        plan.append(item)

    if normalized_paths:
        add(
            _planned_check(
                name="protected_paths",
                argv=[
                    python_executable,
                    "scripts/verify_protected_paths.py",
                    "--repo-root",
                    ".",
                    "--strict",
                    *changed_args,
                    *allow_args,
                ],
                reason="Fail closed when protected files or private memory paths are touched.",
                surface_ids=surface_ids or ["all_changes"],
                blocking=True,
            )
        )

    if python_paths:
        add(
            _planned_check(
                name="python_lint_changed",
                argv=[python_executable, "-m", "ruff", "check", *python_paths],
                reason="Lint only the changed Python surface before wider validation.",
                surface_ids=["python_runtime"],
                blocking=True,
            )
        )

    if any(_matches_any_prefix(path, CORE_RUNTIME_PREFIXES) for path in normalized_paths):
        add(
            _planned_check(
                name="layer_boundaries",
                argv=[
                    python_executable,
                    "scripts/verify_layer_boundaries.py",
                    "--project-root",
                    ".",
                ],
                reason="Core runtime edits must preserve explicit architecture boundaries.",
                surface_ids=["core_runtime"],
                blocking=True,
            )
        )

    if docs_paths:
        add(
            _planned_check(
                name="docs_consistency",
                argv=[python_executable, "scripts/verify_docs_consistency.py", "--repo-root", "."],
                reason="Authority and workflow docs must remain consistent with runtime enforcement.",
                surface_ids=["docs_governance"],
                blocking=True,
            )
        )

    if targeted_tests:
        add(
            _planned_check(
                name="targeted_pytest",
                argv=[python_executable, "-m", "pytest", *targeted_tests, "-q"],
                reason="Run focused pytest coverage inferred from the changed Python files.",
                surface_ids=["python_runtime"],
                blocking=True,
            )
        )

    if web_paths:
        add(
            _planned_check(
                name="web_lint",
                argv=[_npm_executable(), "--prefix", "apps/web", "run", "lint"],
                reason="Frontend changes need lint coverage at the app boundary.",
                surface_ids=["web_surface"],
                blocking=True,
            )
        )
        add(
            _planned_check(
                name="web_test",
                argv=[_npm_executable(), "--prefix", "apps/web", "run", "test"],
                reason="Frontend changes need test coverage at the app boundary.",
                surface_ids=["web_surface"],
                blocking=True,
            )
        )

    if normalized_paths and full_regression:
        add(
            _planned_check(
                name="python_full_regression",
                argv=[python_executable, "-m", "pytest", "tests", "-x", "--tb=short", "-q"],
                reason="The change surface is broad or critical enough to require full Python regression.",
                surface_ids=(
                    ["core_runtime"]
                    if any(
                        _matches_any_prefix(path, CORE_RUNTIME_PREFIXES)
                        for path in normalized_paths
                    )
                    else surface_ids or ["all_changes"]
                ),
                blocking=True,
            )
        )

    return plan, warnings


def _run_check(name: str, command: list[str], cwd: Path) -> dict[str, Any]:
    started = time.perf_counter()
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
    duration = round(time.perf_counter() - started, 2)
    ok = proc.returncode == 0
    return {
        "name": name,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "exit_code": int(proc.returncode),
        "duration_seconds": duration,
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
    }


def execute_plan(
    *,
    repo_root: Path,
    plan: list[dict[str, Any]],
    runner: CheckRunner | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    check_runner = runner or _run_check
    executed: list[dict[str, Any]] = []
    blocking_failures = 0

    for item in plan:
        result = dict(item)
        execution = check_runner(item["name"], list(item["argv"]), repo_root)
        result.update(execution)
        if result.get("blocking") and result.get("status") == "fail":
            blocking_failures += 1
        executed.append(result)

    return executed, blocking_failures == 0


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Changed Surface Checks Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- plan_ok: {str(payload['plan_ok']).lower()}",
        f"- checks_ok: {payload['checks_ok'] if payload['checks_ok'] is not None else 'null'}",
        f"- execution_mode: {payload['execution_mode']}",
        f"- changed_path_count: {payload['metrics']['changed_path_count']}",
        f"- surface_count: {payload['metrics']['surface_count']}",
        f"- planned_check_count: {payload['metrics']['planned_check_count']}",
        f"- blocking_check_count: {payload['metrics']['blocking_check_count']}",
        f"- failed_check_count: {payload['metrics']['failed_check_count']}",
        "",
        "## Surfaces",
    ]

    surfaces = payload.get("surfaces") or []
    if isinstance(surfaces, list) and surfaces:
        for surface in surfaces:
            lines.append(f"- `{surface['id']}` ({surface['path_count']}): {surface['summary']}")
            for path in surface.get("paths", [])[:8]:
                lines.append(f"  - `{path}`")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Checks")
    checks = payload.get("checks") or []
    if isinstance(checks, list) and checks:
        for check in checks:
            lines.append(f"- `{check['name']}` [{check['status']}]: `{check['command']}`")
            lines.append(f"  - reason: {check['reason']}")
            lines.append(f"  - blocking: {str(check['blocking']).lower()}")
            if check.get("surface_ids"):
                lines.append(
                    "  - surfaces: " + ", ".join(f"`{item}`" for item in check["surface_ids"])
                )
            if check.get("status") in {"pass", "fail"}:
                lines.append(f"  - exit_code: {check['exit_code']}")
    else:
        lines.append("- (none)")

    issues = payload.get("issues") or []
    if issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues:
            lines.append(f"- {issue}")

    warnings = payload.get("warnings") or []
    if warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def build_report(
    *,
    repo_root: Path,
    changed_files: list[str] | None = None,
    changed_file_list: Path | None = None,
    staged: bool = False,
    base_ref: str | None = None,
    allow_paths: tuple[str, ...] = (),
    execute: bool = False,
    runner: CheckRunner | None = None,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    collection = protected_paths.collect_changed_paths(
        repo_root=repo_root,
        changed_files=changed_files,
        changed_file_list=changed_file_list,
        staged=staged,
        base_ref=base_ref,
    )
    changed_paths = list(collection.get("paths", []))
    surfaces = classify_surfaces(changed_paths)
    plan, planning_warnings = build_check_plan(
        repo_root=repo_root,
        changed_paths=changed_paths,
        allow_paths=allow_paths,
        python_executable=python_executable,
    )

    checks_ok: bool | None = None
    if execute and collection.get("exit_code", 1) == 0:
        checks, checks_ok = execute_plan(repo_root=repo_root, plan=plan, runner=runner)
    else:
        checks = [dict(item) for item in plan]

    issues: list[str] = []
    warnings: list[str] = list(planning_warnings)
    if collection.get("exit_code", 1) != 0:
        error = str(collection.get("error") or collection.get("stderr") or "").strip()
        issues.append(f"failed to collect changed paths: {error or 'unknown git error'}")
    if collection.get("exit_code", 0) == 0 and not changed_paths:
        warnings.append("no changed paths detected; no checks were planned")

    failed_check_count = sum(1 for check in checks if check.get("status") == "fail")
    blocking_check_count = sum(1 for check in checks if check.get("blocking"))
    executed_check_count = sum(1 for check in checks if check.get("status") in {"pass", "fail"})
    plan_ok = collection.get("exit_code", 1) == 0
    overall_ok = plan_ok and (checks_ok is not False)

    return {
        "generated_at": _iso_now(),
        "plan_ok": plan_ok,
        "checks_ok": checks_ok,
        "overall_ok": overall_ok,
        "execution_mode": "execute" if execute else "plan",
        "repo_root": str(repo_root),
        "collection": {
            "mode": collection.get("mode", "unknown"),
            "command": collection.get("command"),
            "exit_code": collection.get("exit_code"),
            "error": collection.get("error", ""),
            "stderr": collection.get("stderr", ""),
        },
        "changed_paths": changed_paths,
        "surfaces": surfaces,
        "checks": checks,
        "metrics": {
            "changed_path_count": len(changed_paths),
            "surface_count": len(surfaces),
            "planned_check_count": len(plan),
            "blocking_check_count": blocking_check_count,
            "executed_check_count": executed_check_count,
            "failed_check_count": failed_check_count,
        },
        "issues": issues,
        "warnings": warnings,
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan and optionally execute change-surface verification checks."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--changed-file", action="append", default=[], help="Explicit changed path."
    )
    parser.add_argument(
        "--changed-file-list",
        default=None,
        help="Path to newline-delimited changed file list.",
    )
    parser.add_argument("--staged", action="store_true", help="Inspect staged changes.")
    parser.add_argument("--base-ref", default=None, help="Compare against git base ref.")
    parser.add_argument(
        "--allow-path", action="append", default=[], help="Protected-path allowlist."
    )
    parser.add_argument("--execute", action="store_true", help="Run the planned checks.")
    parser.add_argument(
        "--strict", action="store_true", help="Exit non-zero when planning or checks fail."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    changed_file_list = _resolve_optional_path(repo_root, args.changed_file_list)
    allow_paths = tuple(
        _normalize_path(path) for path in (args.allow_path or []) if _normalize_path(path)
    )

    payload = build_report(
        repo_root=repo_root,
        changed_files=list(args.changed_file or []),
        changed_file_list=changed_file_list,
        staged=bool(args.staged),
        base_ref=str(args.base_ref).strip() if args.base_ref else None,
        allow_paths=allow_paths,
        execute=bool(args.execute),
        python_executable=sys.executable,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _emit(payload)

    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
