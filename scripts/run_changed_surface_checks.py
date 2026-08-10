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
import re
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
)
DOCUMENT_EXTENSIONS = {".md", ".rst", ".txt"}
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
CORE_CONTROL_PREFIXES = (
    ".github/workflows/",
    ".github/actions/",
    "skills/",
    ".agent/",
    ".agents/",
)
CORE_CONTROL_FILES = {
    "AGENTS.md",
    "HANDOFF.md",
    "AXIOMS.json",
    "pyproject.toml",
    "pytest.ini",
    "scripts/run_changed_surface_checks.py",
    "scripts/verify_protected_paths.py",
    "scripts/run_publish_push_preflight.py",
    "tonesoul/mutation_preflight.py",
    "tonesoul/publish_push_preflight.py",
}
CORE_CONTROL_TESTS = {
    "tests/test_run_changed_surface_checks.py",
    "tests/test_verify_protected_paths.py",
    "tests/test_publish_push_preflight.py",
}
RISK_LEVELS = ("documentation", "local_code", "core_boundary")
RISK_RANK = {name: index for index, name in enumerate(RISK_LEVELS)}
EXTERNAL_ACTIONS = {"push", "deploy", "publish", "submit", "remote_write"}

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


def _is_documentation_path(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized in CORE_CONTROL_FILES:
        return False
    if any(normalized.startswith(prefix) for prefix in CORE_CONTROL_PREFIXES):
        return False
    return (
        _is_doc_governance_path(normalized)
        and Path(normalized).suffix.lower() in DOCUMENT_EXTENSIONS
    )


def _path_risk(path: str) -> tuple[str, str]:
    normalized = _normalize_path(path)
    if normalized in CORE_CONTROL_FILES:
        return "core_boundary", f"core_file:{normalized}"
    if normalized in CORE_CONTROL_TESTS:
        return "core_boundary", f"core_test:{normalized}"
    for prefix in (*CORE_RUNTIME_PREFIXES, *CORE_CONTROL_PREFIXES):
        if normalized.startswith(prefix):
            return "core_boundary", f"core_prefix:{prefix}"
    if _is_documentation_path(normalized):
        return "documentation", "documentation_path"
    return "local_code", "default_local_code"


def derive_routing(
    changed_paths: list[str],
    *,
    action: str | None = None,
    requested_level: str | None = None,
    external_target: str | None = None,
    allowed_targets: tuple[str, ...] = (),
    grant_ref: str | None = None,
    owner_review_ref: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Derive content risk and external-effect posture without accepting downgrades."""
    normalized_paths = [_normalize_path(path) for path in changed_paths if _normalize_path(path)]
    path_results = [_path_risk(path) for path in normalized_paths]
    derived_level = max(
        (level for level, _rule in path_results),
        key=lambda level: RISK_RANK[level],
        default="local_code",
    )
    matched_rules = sorted({rule for _level, rule in path_results})
    issues: list[str] = []
    effective_level = derived_level
    requested = str(requested_level or "").strip()
    if requested:
        if requested not in RISK_RANK:
            issues.append("unknown_requested_level")
        elif RISK_RANK[requested] < RISK_RANK[derived_level]:
            issues.append("requested_level_would_downgrade")
        elif RISK_RANK[requested] > RISK_RANK[derived_level]:
            effective_level = requested
            matched_rules.append(f"explicit_escalation:{requested}")

    normalized_action = str(action or "").strip().lower()
    if not normalized_action:
        external_status = "not_assessed"
        missing_external: list[str] = []
    elif normalized_action not in EXTERNAL_ACTIONS:
        external_status = "not_external"
        missing_external = []
    else:
        missing_external = []
        target = str(external_target or "").strip()
        allowlist = {str(item).strip() for item in allowed_targets if str(item).strip()}
        if not target:
            missing_external.append("external_target")
        if not allowlist or (target and target not in allowlist):
            missing_external.append("target_allowlist")
        if not str(grant_ref or "").strip():
            missing_external.append("grant_ref")
        if not str(owner_review_ref or "").strip():
            missing_external.append("owner_review_ref")
        external_status = "owner_gate" if missing_external else "preflight_pending"

    return (
        {
            "protocol_version": "proportional-validation-v0.1",
            "adoption_status": "experimental_shadow",
            "derived_level": derived_level,
            "effective_level": effective_level,
            "requested_level": requested or None,
            "matched_rules": matched_rules,
            "action": normalized_action or None,
            "external_effect": normalized_action in EXTERNAL_ACTIONS,
            "external_effect_status": external_status,
            "external_target": str(external_target or "").strip() or None,
            "grant_ref": str(grant_ref or "").strip() or None,
            "owner_review_ref": str(owner_review_ref or "").strip() or None,
            "missing_external_requirements": missing_external,
            "publish_ready": False,
            "shadow_rule": "Current AGENTS.md full pre-push gate remains authoritative.",
        },
        issues,
    )


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
    role: str = "proportional",
) -> dict[str, Any]:
    return {
        "name": name,
        "argv": list(argv),
        "command": _display_command(argv),
        "reason": reason,
        "surface_ids": sorted({surface_id for surface_id in surface_ids if surface_id}),
        "blocking": bool(blocking),
        "role": role,
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
    routing: dict[str, Any],
    shadow_full: bool = False,
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
    effective_level = str(routing.get("effective_level", "local_code"))
    is_core = effective_level == "core_boundary"
    is_external = bool(routing.get("external_effect"))

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

    if is_core:
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

        add(
            _planned_check(
                name="doc_links",
                argv=[
                    python_executable,
                    "scripts/verify_doc_links.py",
                    "--strict",
                    "--no-write",
                ],
                reason="Documentation changes must not introduce unresolved repository links.",
                surface_ids=["docs_governance"],
                blocking=True,
            )
        )

    if normalized_paths:
        add(
            _planned_check(
                name="diff_check",
                argv=["git", "diff", "--check"],
                reason="All change classes reject whitespace and patch-format errors.",
                surface_ids=surface_ids or ["all_changes"],
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
    elif normalized_paths and effective_level == "local_code":
        add(
            _planned_check(
                name="smoke_tests",
                argv=[python_executable, "scripts/run_test_tier.py", "--tier", "smoke"],
                reason="Local code without reliable direct test inference falls back to the curated smoke tier.",
                surface_ids=surface_ids or ["local_code"],
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

    if normalized_paths and is_core:
        add(
            _planned_check(
                name="python_lint_full",
                argv=[python_executable, "-m", "ruff", "check", "tonesoul", "tests", "scripts"],
                reason="Core-boundary changes require repository-wide Python lint coverage.",
                surface_ids=["core_runtime"],
                blocking=True,
            )
        )
        add(
            _planned_check(
                name="boundary_tests",
                argv=[python_executable, "scripts/run_test_tier.py", "--tier", "blocking"],
                reason="Core-boundary changes must preserve public, privacy, and responsibility contracts.",
                surface_ids=["core_runtime"],
                blocking=True,
            )
        )
        add(
            _planned_check(
                name="core_tests",
                argv=[python_executable, "scripts/run_test_tier.py", "--tier", "core"],
                reason="Core-boundary changes require the curated blocking regression tier.",
                surface_ids=["core_runtime"],
                blocking=True,
            )
        )
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
                role="proportional_and_legacy",
            )
        )

    if normalized_paths and (is_core or is_external):
        add(
            _planned_check(
                name="pii_secret_scan",
                argv=[
                    python_executable,
                    "scripts/scan_changed_content.py",
                    "--repo-root",
                    ".",
                    "--strict",
                    *changed_args,
                ],
                reason="High-risk content receives a bounded lexical PII and credential-shape scan.",
                surface_ids=surface_ids or ["all_changes"],
                blocking=True,
            )
        )

    if normalized_paths and is_external:
        add(
            _planned_check(
                name="publish_push_preflight",
                argv=[
                    python_executable,
                    "scripts/run_publish_push_preflight.py",
                    "--agent",
                    "proportional-validation-v01",
                    "--grant-ref",
                    str(routing.get("grant_ref") or ""),
                    "--owner-review-ref",
                    str(routing.get("owner_review_ref") or ""),
                    "--strict",
                ],
                reason="External effects must pass the existing publish/push posture preflight.",
                surface_ids=surface_ids or ["all_changes"],
                blocking=True,
            )
        )

    if normalized_paths and shadow_full and not is_core:
        add(
            _planned_check(
                name="legacy_full_regression",
                argv=[python_executable, "-m", "pytest", "tests", "-x", "--tb=short", "-q"],
                reason="Shadow-only legacy baseline used to measure false negatives and validation cost.",
                surface_ids=surface_ids or ["all_changes"],
                blocking=True,
                role="legacy_baseline",
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
    routing = payload.get("routing") or {}
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
        f"- derived_level: {routing.get('derived_level', 'unknown')}",
        f"- effective_level: {routing.get('effective_level', 'unknown')}",
        f"- external_effect_status: {routing.get('external_effect_status', 'unknown')}",
        f"- publish_ready: {str(bool(routing.get('publish_ready'))).lower()}",
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
    action: str | None = None,
    requested_level: str | None = None,
    external_target: str | None = None,
    allowed_targets: tuple[str, ...] = (),
    grant_ref: str | None = None,
    owner_review_ref: str | None = None,
    shadow_full: bool = False,
    pilot_case_id: str | None = None,
    format_repair_count: int = 0,
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
    routing, routing_issues = derive_routing(
        changed_paths,
        action=action,
        requested_level=requested_level,
        external_target=external_target,
        allowed_targets=allowed_targets,
        grant_ref=grant_ref,
        owner_review_ref=owner_review_ref,
    )
    _targeted_preview, targeted_preview_warnings = infer_targeted_tests(repo_root, changed_paths)
    if targeted_preview_warnings and routing["effective_level"] != "core_boundary":
        routing["effective_level"] = "core_boundary"
        routing["matched_rules"].append("automatic_escalation:targeted_test_limit")
    plan, planning_warnings = build_check_plan(
        repo_root=repo_root,
        changed_paths=changed_paths,
        routing=routing,
        shadow_full=shadow_full,
        allow_paths=allow_paths,
        python_executable=python_executable,
    )
    routing["required_checks"] = [check["name"] for check in plan]

    preexecution_issues: list[str] = list(routing_issues)
    if collection.get("exit_code", 1) == 0 and not changed_paths:
        preexecution_issues.append("no_changed_paths")
    if routing["external_effect"] and routing["missing_external_requirements"]:
        preexecution_issues.append("external_requirements_incomplete")
    if shadow_full and not str(pilot_case_id or "").strip():
        preexecution_issues.append("shadow_case_id_required")

    checks_ok: bool | None = None
    if execute and collection.get("exit_code", 1) == 0 and not preexecution_issues:
        checks, checks_ok = execute_plan(repo_root=repo_root, plan=plan, runner=runner)
    else:
        checks = [dict(item) for item in plan]

    issues: list[str] = list(preexecution_issues)
    warnings: list[str] = list(planning_warnings)
    if collection.get("exit_code", 1) != 0:
        error = str(collection.get("error") or collection.get("stderr") or "").strip()
        issues.append(f"failed to collect changed paths: {error or 'unknown git error'}")
    if collection.get("exit_code", 0) == 0 and not changed_paths:
        warnings.append("no changed paths detected; no checks were planned")

    failed_check_count = sum(1 for check in checks if check.get("status") == "fail")
    blocking_check_count = sum(1 for check in checks if check.get("blocking"))
    executed_check_count = sum(1 for check in checks if check.get("status") in {"pass", "fail"})
    total_duration = round(
        sum(float(check.get("duration_seconds", 0.0) or 0.0) for check in checks), 2
    )
    proportional_checks = [check for check in checks if check.get("role") != "legacy_baseline"]
    legacy_checks = [
        check
        for check in checks
        if check.get("role") in {"legacy_baseline", "proportional_and_legacy"}
    ]

    def test_count(items: list[dict[str, Any]]) -> int:
        total = 0
        for item in items:
            text = f"{item.get('stdout_tail', '')}\n{item.get('stderr_tail', '')}"
            total += sum(
                int(value) for value in re.findall(r"(\d+)\s+(?:passed|failed|error)", text)
            )
        return total

    pilot_observation: dict[str, Any] | None = None
    if shadow_full and execute and checks_ok is not None:
        routed_ok = all(check.get("status") == "pass" for check in proportional_checks)
        legacy_ok = bool(legacy_checks) and all(
            check.get("status") == "pass" for check in legacy_checks
        )
        pilot_observation = {
            "case_id": str(pilot_case_id or "").strip() or None,
            "content_level": routing["effective_level"],
            "external_effect": routing["external_effect"],
            "routed": {
                "ok": routed_ok,
                "duration_seconds": round(
                    sum(
                        float(check.get("duration_seconds", 0.0) or 0.0)
                        for check in proportional_checks
                    ),
                    2,
                ),
                "test_count": test_count(proportional_checks),
            },
            "legacy": {
                "ok": legacy_ok,
                "duration_seconds": round(
                    sum(
                        float(check.get("duration_seconds", 0.0) or 0.0) for check in legacy_checks
                    ),
                    2,
                ),
                "test_count": test_count(legacy_checks),
            },
            "false_negative": routed_ok and not legacy_ok,
            "pii_or_owner_gate_miss": False,
            "format_repair_count": max(0, int(format_repair_count)),
        }
    plan_ok = collection.get("exit_code", 1) == 0 and not issues
    overall_ok = plan_ok and (checks_ok is not False)
    if (
        routing["external_effect"]
        and routing["external_effect_status"] == "preflight_pending"
        and execute
        and overall_ok
    ):
        routing["external_effect_status"] = "preflight_passed"
        routing["publish_ready"] = True

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
        "routing": routing,
        "surfaces": surfaces,
        "checks": checks,
        "metrics": {
            "changed_path_count": len(changed_paths),
            "surface_count": len(surfaces),
            "planned_check_count": len(plan),
            "blocking_check_count": blocking_check_count,
            "executed_check_count": executed_check_count,
            "failed_check_count": failed_check_count,
            "duration_seconds_total": total_duration,
            "pytest_test_count_observed": test_count(checks),
        },
        "pilot_observation": pilot_observation,
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
    parser.add_argument(
        "--action",
        default=None,
        choices=sorted(EXTERNAL_ACTIONS | {"local"}),
        help="Planned action. External actions add authority and publish preflight requirements.",
    )
    parser.add_argument(
        "--requested-level",
        default=None,
        choices=list(RISK_LEVELS),
        help="Optional escalation request. Requests below the derived level fail closed.",
    )
    parser.add_argument("--external-target", default=None, help="Exact external action target.")
    parser.add_argument(
        "--allowed-target", action="append", default=[], help="Allowed external target token."
    )
    parser.add_argument("--grant-ref", default=None, help="Scoped owner grant source reference.")
    parser.add_argument(
        "--owner-review-ref",
        default=None,
        help="Source reference for bounded owner review; not identity verification.",
    )
    parser.add_argument(
        "--shadow-full",
        action="store_true",
        help="Also run the legacy full gate and emit one pilot observation.",
    )
    parser.add_argument("--pilot-case-id", default=None, help="De-identified shadow case ID.")
    parser.add_argument("--format-repair-count", type=int, default=0)
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
        action=getattr(args, "action", None),
        requested_level=getattr(args, "requested_level", None),
        external_target=getattr(args, "external_target", None),
        allowed_targets=tuple(getattr(args, "allowed_target", []) or []),
        grant_ref=getattr(args, "grant_ref", None),
        owner_review_ref=getattr(args, "owner_review_ref", None),
        shadow_full=bool(getattr(args, "shadow_full", False)),
        pilot_case_id=getattr(args, "pilot_case_id", None),
        format_repair_count=int(getattr(args, "format_repair_count", 0) or 0),
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
