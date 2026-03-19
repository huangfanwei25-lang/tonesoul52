"""
Run repository health checks and publish latest status artifacts.
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

from tonesoul.status_alignment import build_dream_weekly_alignment_line

DISCUSSION_CURATED_PATH = Path("memory/agent_discussion_curated.jsonl")
JSON_FILENAME = "repo_healthcheck_latest.json"
MARKDOWN_FILENAME = "repo_healthcheck_latest.md"
DEFAULT_MAX_TRACKED_IGNORED = 28
COMMIT_ATTRIBUTION_BASE_SWITCH_ARTIFACT = "docs/status/commit_attribution_base_switch_latest.json"
PASSIVE_STATUS_PREVIEW_SPECS: list[dict[str, str]] = [
    {
        "name": "agent_integrity",
        "path": "docs/status/agent_integrity_latest.json",
    },
    {
        "name": "repo_semantic_atlas",
        "path": "docs/status/repo_semantic_atlas_latest.json",
    },
    {
        "name": "subjectivity_review_batch",
        "path": "docs/status/subjectivity_review_batch_latest.json",
    },
    {
        "name": "dream_observability",
        "path": "docs/status/dream_observability_latest.json",
    },
    {
        "name": "scribe_status",
        "path": "docs/status/scribe_status_latest.json",
    },
]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _display_command(cmd: list[str]) -> str:
    rendered: list[str] = []
    for index, token in enumerate(cmd):
        text = str(token)
        if index == 0:
            executable = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if executable.startswith("python"):
                rendered.append("python")
                continue
            if executable in {"npm", "npm.cmd"}:
                rendered.append("npm")
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


def _is_ci_environment() -> bool:
    raw = str(os.environ.get("CI", "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _is_windows_environment() -> bool:
    return os.name == "nt"


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
        "command": _display_command(command),
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
    }


def _skip_check(name: str, command: list[str], reason: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": "skip",
        "ok": True,
        "exit_code": None,
        "duration_seconds": 0.0,
        "command": _display_command(command),
        "stdout_tail": "",
        "stderr_tail": "",
        "skip_reason": reason,
    }


def _run_json_command(
    name: str, command: list[str], cwd: Path
) -> tuple[dict[str, Any], dict[str, Any] | None]:
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
    payload: dict[str, Any] | None = None
    parse_error = ""
    stdout_text = proc.stdout.strip()
    if stdout_text:
        try:
            parsed = json.loads(stdout_text)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
        else:
            if isinstance(parsed, dict):
                payload = parsed
            else:
                parse_error = "JSON root is not an object"

    result = {
        "name": name,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "exit_code": int(proc.returncode),
        "duration_seconds": duration,
        "command": _display_command(command),
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
    }
    if parse_error:
        result["parse_error"] = parse_error
    return result, payload


def _load_json_document(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _extract_handoff_surface(document: dict[str, Any] | None) -> dict[str, str] | None:
    if not isinstance(document, dict):
        return None

    candidates: list[dict[str, Any]] = [document]
    for key in ("batch", "grouping", "report"):
        nested = document.get(key)
        if isinstance(nested, dict):
            candidates.append(nested)

    for candidate in candidates:
        handoff = candidate.get("handoff")
        primary_status_line = str(candidate.get("primary_status_line") or "").strip()
        runtime_status_line = str(candidate.get("runtime_status_line") or "").strip()
        anchor_status_line = str(candidate.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(candidate.get("problem_route_status_line") or "").strip()
        problem_route_secondary_labels = str(
            candidate.get("problem_route_secondary_labels") or ""
        ).strip()
        dream_weekly_alignment_line = str(
            candidate.get("dream_weekly_alignment_line") or ""
        ).strip()
        artifact_policy_status_line = str(
            candidate.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            candidate.get("admissibility_primary_status_line") or ""
        ).strip()
        scribe_status_line = str(candidate.get("scribe_status_line") or "").strip()
        semantic_retrieval_protocol = str(
            candidate.get("semantic_retrieval_protocol") or ""
        ).strip()
        semantic_preferred_neighborhood = str(
            candidate.get("semantic_preferred_neighborhood") or ""
        ).strip()
        queue_shape = ""
        requires_operator_action = False
        if isinstance(handoff, dict):
            queue_shape = str(handoff.get("queue_shape") or "").strip()
            requires_operator_action = bool(handoff.get("requires_operator_action"))
            if not primary_status_line:
                primary_status_line = str(handoff.get("primary_status_line") or "").strip()
            if not runtime_status_line:
                runtime_status_line = str(handoff.get("runtime_status_line") or "").strip()
            if not scribe_status_line:
                scribe_status_line = str(handoff.get("scribe_status_line") or "").strip()
            if not anchor_status_line:
                anchor_status_line = str(handoff.get("anchor_status_line") or "").strip()
            if not problem_route_status_line:
                problem_route_status_line = str(
                    handoff.get("problem_route_status_line") or ""
                ).strip()
            if not problem_route_secondary_labels:
                problem_route_secondary_labels = str(
                    handoff.get("problem_route_secondary_labels") or ""
                ).strip()
            if not dream_weekly_alignment_line:
                dream_weekly_alignment_line = str(
                    handoff.get("dream_weekly_alignment_line") or ""
                ).strip()
            if not artifact_policy_status_line:
                artifact_policy_status_line = str(
                    handoff.get("artifact_policy_status_line") or ""
                ).strip()
            if not admissibility_primary_status_line:
                admissibility_primary_status_line = str(
                    handoff.get("admissibility_primary_status_line") or ""
                ).strip()
            if not semantic_retrieval_protocol:
                semantic_retrieval_protocol = str(
                    handoff.get("semantic_retrieval_protocol") or ""
                ).strip()
            if not semantic_preferred_neighborhood:
                semantic_preferred_neighborhood = str(
                    handoff.get("semantic_preferred_neighborhood") or ""
                ).strip()
        if (
            queue_shape
            or primary_status_line
            or runtime_status_line
            or anchor_status_line
            or problem_route_status_line
            or problem_route_secondary_labels
            or dream_weekly_alignment_line
            or artifact_policy_status_line
            or scribe_status_line
            or semantic_retrieval_protocol
            or semantic_preferred_neighborhood
        ):
            preview = {
                "queue_shape": queue_shape,
                "primary_status_line": primary_status_line,
                "runtime_status_line": runtime_status_line,
                "anchor_status_line": anchor_status_line,
                "artifact_policy_status_line": artifact_policy_status_line,
                "scribe_status_line": scribe_status_line,
                "requires_operator_action": str(requires_operator_action).lower(),
            }
            if admissibility_primary_status_line:
                preview["admissibility_primary_status_line"] = admissibility_primary_status_line
            if problem_route_status_line:
                preview["problem_route_status_line"] = problem_route_status_line
            if problem_route_secondary_labels:
                preview["problem_route_secondary_labels"] = problem_route_secondary_labels
            if dream_weekly_alignment_line:
                preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
            if semantic_retrieval_protocol:
                preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
            if semantic_preferred_neighborhood:
                preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
            return preview
    return None


def _check_handoff_preview(
    name: str,
    payload: dict[str, Any] | None,
) -> dict[str, str] | None:
    surface = _extract_handoff_surface(payload)
    if surface is None:
        return None
    preview = {
        "name": name,
        "queue_shape": surface.get("queue_shape", ""),
        "primary_status_line": surface.get("primary_status_line", ""),
        "runtime_status_line": surface.get("runtime_status_line", ""),
        "anchor_status_line": surface.get("anchor_status_line", ""),
        "artifact_policy_status_line": surface.get("artifact_policy_status_line", ""),
        "requires_operator_action": surface.get("requires_operator_action", "false"),
    }
    admissibility_primary_status_line = str(
        surface.get("admissibility_primary_status_line") or ""
    ).strip()
    if admissibility_primary_status_line:
        preview["admissibility_primary_status_line"] = admissibility_primary_status_line
    problem_route_status_line = str(surface.get("problem_route_status_line") or "").strip()
    if problem_route_status_line:
        preview["problem_route_status_line"] = problem_route_status_line
    problem_route_secondary_labels = str(
        surface.get("problem_route_secondary_labels") or ""
    ).strip()
    if problem_route_secondary_labels:
        preview["problem_route_secondary_labels"] = problem_route_secondary_labels
    dream_weekly_alignment_line = str(surface.get("dream_weekly_alignment_line") or "").strip()
    if dream_weekly_alignment_line:
        preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
    scribe_status_line = str(surface.get("scribe_status_line") or "").strip()
    if scribe_status_line:
        preview["scribe_status_line"] = scribe_status_line
    semantic_retrieval_protocol = str(surface.get("semantic_retrieval_protocol") or "").strip()
    if semantic_retrieval_protocol:
        preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
    semantic_preferred_neighborhood = str(
        surface.get("semantic_preferred_neighborhood") or ""
    ).strip()
    if semantic_preferred_neighborhood:
        preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
    return preview


def _load_status_artifact_preview(
    repo_root: Path,
    *,
    name: str,
    path: str,
) -> dict[str, str] | None:
    artifact_path = Path(path)
    resolved_path = artifact_path if artifact_path.is_absolute() else repo_root / artifact_path
    document = _load_json_document(resolved_path)
    surface = _extract_handoff_surface(document)
    if surface is None:
        return None
    preview = {
        "name": name,
        "path": path,
        "queue_shape": surface.get("queue_shape", ""),
        "primary_status_line": surface.get("primary_status_line", ""),
        "runtime_status_line": surface.get("runtime_status_line", ""),
        "anchor_status_line": surface.get("anchor_status_line", ""),
        "artifact_policy_status_line": surface.get("artifact_policy_status_line", ""),
        "requires_operator_action": surface.get("requires_operator_action", "false"),
    }
    admissibility_primary_status_line = str(
        surface.get("admissibility_primary_status_line") or ""
    ).strip()
    if admissibility_primary_status_line:
        preview["admissibility_primary_status_line"] = admissibility_primary_status_line
    problem_route_status_line = str(surface.get("problem_route_status_line") or "").strip()
    if problem_route_status_line:
        preview["problem_route_status_line"] = problem_route_status_line
    problem_route_secondary_labels = str(
        surface.get("problem_route_secondary_labels") or ""
    ).strip()
    if problem_route_secondary_labels:
        preview["problem_route_secondary_labels"] = problem_route_secondary_labels
    dream_weekly_alignment_line = str(surface.get("dream_weekly_alignment_line") or "").strip()
    if dream_weekly_alignment_line:
        preview["dream_weekly_alignment_line"] = dream_weekly_alignment_line
    scribe_status_line = str(surface.get("scribe_status_line") or "").strip()
    if scribe_status_line:
        preview["scribe_status_line"] = scribe_status_line
    semantic_retrieval_protocol = str(surface.get("semantic_retrieval_protocol") or "").strip()
    if semantic_retrieval_protocol:
        preview["semantic_retrieval_protocol"] = semantic_retrieval_protocol
    semantic_preferred_neighborhood = str(
        surface.get("semantic_preferred_neighborhood") or ""
    ).strip()
    if semantic_preferred_neighborhood:
        preview["semantic_preferred_neighborhood"] = semantic_preferred_neighborhood
    return preview


def _select_handoff_preview(
    previews: list[dict[str, str]],
    *,
    queue_shape: str,
) -> dict[str, str] | None:
    target = queue_shape.strip()
    if not target:
        return None
    for preview in previews:
        if str(preview.get("queue_shape") or "").strip() != target:
            continue
        if (
            str(preview.get("primary_status_line") or "").strip()
            or str(preview.get("runtime_status_line") or "").strip()
        ):
            return dict(preview)
    return None


def _select_named_preview(
    previews: list[dict[str, str]],
    *,
    name: str,
) -> dict[str, str] | None:
    target = name.strip()
    if not target:
        return None
    for preview in previews:
        if str(preview.get("name") or "").strip() != target:
            continue
        if (
            str(preview.get("primary_status_line") or "").strip()
            or str(preview.get("runtime_status_line") or "").strip()
        ):
            return dict(preview)
    return None


def _select_subjectivity_focus_preview(
    previews: list[dict[str, str]],
) -> dict[str, str] | None:
    for preview in previews:
        if not str(preview.get("admissibility_primary_status_line") or "").strip():
            continue
        if (
            str(preview.get("primary_status_line") or "").strip()
            or str(preview.get("runtime_status_line") or "").strip()
        ):
            return dict(preview)
    return None


def _build_check_specs(
    python_executable: str,
    include_sdh: bool,
    check_council_modes: bool,
    strict_soft_fail: bool,
    web_base: str | None,
    api_base: str | None,
    sdh_timeout: int | None,
    allow_missing_discussion: bool,
    discussion_path: Path,
) -> list[dict[str, Any]]:
    verify_7d_cmd = [python_executable, "scripts/verify_7d.py"]
    if include_sdh:
        verify_7d_cmd.append("--include-sdh")
        if web_base:
            verify_7d_cmd.extend(["--web-base", web_base])
        if api_base:
            verify_7d_cmd.extend(["--api-base", api_base])
        if sdh_timeout is not None:
            verify_7d_cmd.extend(["--timeout", str(max(1, sdh_timeout))])
        if check_council_modes:
            verify_7d_cmd.append("--check-council-modes")
        else:
            verify_7d_cmd.append("--no-check-council-modes")
    if strict_soft_fail:
        verify_7d_cmd.append("--strict-soft-fail")

    specs: list[dict[str, Any]] = [
        {
            "name": "python_lint",
            "command": [python_executable, "-m", "ruff", "check", "tonesoul", "tests", "scripts"],
        },
        {
            "name": "python_format",
            "command": [
                python_executable,
                "-m",
                "black",
                "--check",
                "tonesoul",
                "tests",
                "scripts",
            ],
        },
        {
            "name": "python_tests",
            "command": [python_executable, "-m", "pytest", "tests", "-q"],
        },
        {
            "name": "web_lint",
            "command": [_npm_executable(), "--prefix", "apps/web", "run", "lint"],
        },
        {
            "name": "web_test",
            "command": [_npm_executable(), "--prefix", "apps/web", "run", "test"],
        },
        {
            "name": "git_hygiene",
            "command": [
                python_executable,
                "scripts/verify_git_hygiene.py",
                "--strict",
                "--max-tracked-ignored",
                str(DEFAULT_MAX_TRACKED_IGNORED),
            ],
        },
        {
            "name": "commit_attribution",
            "command": [
                python_executable,
                "scripts/verify_incremental_commit_attribution.py",
                "--strict",
                "--artifact-path",
                "docs/status/commit_attribution_local.json",
            ],
        },
        {
            "name": "dual_track_boundary",
            "command": [
                python_executable,
                "scripts/verify_dual_track_boundary.py",
                "--strict",
                "--staged",
            ],
        },
        {
            "name": "persona_swarm",
            "command": [python_executable, "scripts/run_persona_swarm_framework.py", "--strict"],
        },
        {
            "name": "external_source_registry",
            "command": [
                python_executable,
                "scripts/verify_external_source_registry.py",
                "--strict",
            ],
        },
        {
            "name": "skill_registry",
            "command": [
                python_executable,
                "scripts/verify_skill_registry.py",
                "--strict",
            ],
        },
        {
            "name": "multi_agent_divergence",
            "command": [
                python_executable,
                "scripts/run_multi_agent_divergence_report.py",
                "--strict",
            ],
        },
        {
            "name": "memory_quality",
            "command": [
                python_executable,
                "scripts/run_memory_quality_report.py",
                "--strict",
            ],
        },
        {
            "name": "memory_governance_contract",
            "command": [
                python_executable,
                "scripts/run_memory_governance_contract_check.py",
                "--strict",
            ],
        },
        {
            "name": "friction_shadow_replay_export",
            "command": [
                python_executable,
                "scripts/run_friction_shadow_replay_export.py",
                "--strict",
            ],
        },
        {
            "name": "friction_shadow_calibration",
            "command": [
                python_executable,
                "scripts/run_friction_shadow_calibration_report.py",
                "--strict",
            ],
        },
        {
            "name": "philosophical_reflection",
            "command": [
                python_executable,
                "scripts/run_philosophical_reflection_report.py",
                "--strict",
            ],
        },
        {
            "name": "memory_topology_fit",
            "command": [
                python_executable,
                "scripts/run_memory_topology_fit_report.py",
                "--strict",
            ],
        },
        {
            "name": "repo_intelligence",
            "command": [
                python_executable,
                "scripts/run_repo_intelligence_report.py",
            ],
            "structured_output": "json",
        },
        {
            "name": "true_verification_weekly",
            "command": [
                python_executable,
                "scripts/report_true_verification_task_status.py",
                "--strict",
            ],
            "structured_output": "json",
        },
        {
            "name": "audit_7d",
            "command": verify_7d_cmd,
        },
    ]

    if not _is_windows_environment():
        for spec in specs:
            if spec["name"] == "true_verification_weekly":
                spec["skip_reason"] = "requires Windows Task Scheduler host"
                break

    if allow_missing_discussion and not discussion_path.exists():
        for spec in specs:
            if spec["name"] == "audit_7d":
                spec["skip_reason"] = f"missing discussion file: {discussion_path}"
                break
    return specs


def _render_markdown(payload: dict[str, Any]) -> str:
    handoff_previews = list(payload.get("handoff_previews") or [])
    repo_intelligence_preview = payload.get("repo_intelligence_preview")
    weekly_host_status_preview = payload.get("weekly_host_status_preview")
    subjectivity_focus_preview = payload.get("subjectivity_focus_preview")
    dream_observability_preview = payload.get("dream_observability_preview")
    scribe_status_preview = payload.get("scribe_status_preview")
    agent_integrity_preview = payload.get("agent_integrity_preview")
    repo_semantic_atlas_preview = payload.get("repo_semantic_atlas_preview")
    dream_weekly_alignment_line = str(payload.get("dream_weekly_alignment_line") or "").strip()
    summary_lines = [
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- handoff_preview_count: {len(handoff_previews)}",
    ]

    if isinstance(repo_intelligence_preview, dict):
        primary_status_line = str(
            repo_intelligence_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            repo_intelligence_preview.get("runtime_status_line") or ""
        ).strip()
        semantic_retrieval_protocol = str(
            repo_intelligence_preview.get("semantic_retrieval_protocol") or ""
        ).strip()
        semantic_preferred_neighborhood = str(
            repo_intelligence_preview.get("semantic_preferred_neighborhood") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- repo_intelligence: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- repo_intelligence_entrypoints: `{runtime_status_line}`")
        if semantic_retrieval_protocol:
            summary_lines.append(
                f"- repo_intelligence_semantic_protocol: `{semantic_retrieval_protocol}`"
            )
        if semantic_preferred_neighborhood:
            summary_lines.append(
                f"- repo_intelligence_first_neighborhood: `{semantic_preferred_neighborhood}`"
            )

    if isinstance(repo_semantic_atlas_preview, dict):
        primary_status_line = str(
            repo_semantic_atlas_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            repo_semantic_atlas_preview.get("runtime_status_line") or ""
        ).strip()
        artifact_policy_status_line = str(
            repo_semantic_atlas_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- repo_semantic_atlas: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- repo_semantic_protocol: `{runtime_status_line}`")
        if artifact_policy_status_line:
            summary_lines.append(
                f"- repo_semantic_artifact_policy: `{artifact_policy_status_line}`"
            )

    if isinstance(weekly_host_status_preview, dict):
        primary_status_line = str(
            weekly_host_status_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            weekly_host_status_preview.get("runtime_status_line") or ""
        ).strip()
        anchor_status_line = str(weekly_host_status_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            weekly_host_status_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            weekly_host_status_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        scribe_status_line = str(weekly_host_status_preview.get("scribe_status_line") or "").strip()
        artifact_policy_status_line = str(
            weekly_host_status_preview.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            weekly_host_status_preview.get("admissibility_primary_status_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- weekly_host_status: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- weekly_runtime_posture: `{runtime_status_line}`")
        if anchor_status_line:
            summary_lines.append(f"- weekly_anchor_posture: `{anchor_status_line}`")
        if problem_route_status_line:
            summary_lines.append(f"- weekly_problem_route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            summary_lines.append(
                f"- weekly_problem_route_secondary: `{problem_route_secondary_labels}`"
            )
        if scribe_status_line:
            summary_lines.append(f"- weekly_scribe_posture: `{scribe_status_line}`")
        if artifact_policy_status_line:
            summary_lines.append(f"- weekly_artifact_policy: `{artifact_policy_status_line}`")
        if admissibility_primary_status_line:
            summary_lines.append(f"- weekly_admissibility: `{admissibility_primary_status_line}`")

    if isinstance(subjectivity_focus_preview, dict):
        primary_status_line = str(
            subjectivity_focus_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            subjectivity_focus_preview.get("runtime_status_line") or ""
        ).strip()
        scribe_status_line = str(subjectivity_focus_preview.get("scribe_status_line") or "").strip()
        anchor_status_line = str(subjectivity_focus_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            subjectivity_focus_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            subjectivity_focus_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        artifact_policy_status_line = str(
            subjectivity_focus_preview.get("artifact_policy_status_line") or ""
        ).strip()
        admissibility_primary_status_line = str(
            subjectivity_focus_preview.get("admissibility_primary_status_line") or ""
        ).strip()
        focus_alignment_line = str(
            subjectivity_focus_preview.get("dream_weekly_alignment_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- subjectivity_focus: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- subjectivity_runtime_posture: `{runtime_status_line}`")
        if scribe_status_line:
            summary_lines.append(f"- subjectivity_scribe_posture: `{scribe_status_line}`")
        if anchor_status_line:
            summary_lines.append(f"- subjectivity_anchor_posture: `{anchor_status_line}`")
        if problem_route_status_line:
            summary_lines.append(f"- subjectivity_problem_route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            summary_lines.append(
                f"- subjectivity_problem_route_secondary: `{problem_route_secondary_labels}`"
            )
        if focus_alignment_line:
            summary_lines.append(f"- subjectivity_alignment: `{focus_alignment_line}`")
        if artifact_policy_status_line:
            summary_lines.append(f"- subjectivity_artifact_policy: `{artifact_policy_status_line}`")
        if admissibility_primary_status_line:
            summary_lines.append(
                f"- subjectivity_admissibility: `{admissibility_primary_status_line}`"
            )

    if isinstance(dream_observability_preview, dict):
        primary_status_line = str(
            dream_observability_preview.get("primary_status_line") or ""
        ).strip()
        runtime_status_line = str(
            dream_observability_preview.get("runtime_status_line") or ""
        ).strip()
        anchor_status_line = str(
            dream_observability_preview.get("anchor_status_line") or ""
        ).strip()
        problem_route_status_line = str(
            dream_observability_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            dream_observability_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        artifact_policy_status_line = str(
            dream_observability_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- dream_observability: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- dream_runtime_posture: `{runtime_status_line}`")
        if anchor_status_line:
            summary_lines.append(f"- dream_anchor_posture: `{anchor_status_line}`")
        if problem_route_status_line:
            summary_lines.append(f"- dream_problem_route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            summary_lines.append(
                f"- dream_problem_route_secondary: `{problem_route_secondary_labels}`"
            )
        if artifact_policy_status_line:
            summary_lines.append(f"- dream_artifact_policy: `{artifact_policy_status_line}`")
    if dream_weekly_alignment_line:
        summary_lines.append(f"- dream_weekly_alignment: `{dream_weekly_alignment_line}`")

    if isinstance(scribe_status_preview, dict):
        primary_status_line = str(scribe_status_preview.get("primary_status_line") or "").strip()
        runtime_status_line = str(scribe_status_preview.get("runtime_status_line") or "").strip()
        anchor_status_line = str(scribe_status_preview.get("anchor_status_line") or "").strip()
        problem_route_status_line = str(
            scribe_status_preview.get("problem_route_status_line") or ""
        ).strip()
        problem_route_secondary_labels = str(
            scribe_status_preview.get("problem_route_secondary_labels") or ""
        ).strip()
        artifact_policy_status_line = str(
            scribe_status_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- scribe_state_document: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- scribe_state_posture: `{runtime_status_line}`")
        if anchor_status_line:
            summary_lines.append(f"- scribe_lead_anchor: `{anchor_status_line}`")
        if problem_route_status_line:
            summary_lines.append(f"- scribe_problem_route: `{problem_route_status_line}`")
        if problem_route_secondary_labels:
            summary_lines.append(
                f"- scribe_problem_route_secondary: `{problem_route_secondary_labels}`"
            )
        if artifact_policy_status_line:
            summary_lines.append(f"- scribe_artifact_policy: `{artifact_policy_status_line}`")

    if isinstance(agent_integrity_preview, dict):
        primary_status_line = str(agent_integrity_preview.get("primary_status_line") or "").strip()
        runtime_status_line = str(agent_integrity_preview.get("runtime_status_line") or "").strip()
        problem_route_status_line = str(
            agent_integrity_preview.get("problem_route_status_line") or ""
        ).strip()
        artifact_policy_status_line = str(
            agent_integrity_preview.get("artifact_policy_status_line") or ""
        ).strip()
        if primary_status_line:
            summary_lines.append(f"- agent_integrity: `{primary_status_line}`")
        if runtime_status_line:
            summary_lines.append(f"- agent_integrity_runtime: `{runtime_status_line}`")
        if problem_route_status_line:
            summary_lines.append(f"- agent_integrity_problem_route: `{problem_route_status_line}`")
        if artifact_policy_status_line:
            summary_lines.append(
                f"- agent_integrity_artifact_policy: `{artifact_policy_status_line}`"
            )

    lines = [
        "# Repo Healthcheck Latest",
        "",
        *summary_lines,
        "",
        "| check | status | exit | duration_s | command |",
        "| --- | --- | ---: | ---: | --- |",
    ]

    for check in payload["checks"]:
        exit_code = "-" if check.get("exit_code") is None else str(check["exit_code"])
        lines.append(
            f"| {check['name']} | {check['status'].upper()} | {exit_code} | "
            f"{float(check['duration_seconds']):.2f} | `{check['command']}` |"
        )

    failed = [item for item in payload["checks"] if item["status"] == "fail"]
    skipped = [item for item in payload["checks"] if item["status"] == "skip"]

    if handoff_previews:
        lines.append("")
        lines.append("## Handoff Previews")
        for item in handoff_previews:
            name = str(item.get("name") or "").strip()
            queue_shape = str(item.get("queue_shape") or "").strip()
            primary_status_line = str(item.get("primary_status_line") or "").strip()
            runtime_status_line = str(item.get("runtime_status_line") or "").strip()
            anchor_status_line = str(item.get("anchor_status_line") or "").strip()
            problem_route_status_line = str(item.get("problem_route_status_line") or "").strip()
            problem_route_secondary_labels = str(
                item.get("problem_route_secondary_labels") or ""
            ).strip()
            artifact_policy_status_line = str(item.get("artifact_policy_status_line") or "").strip()
            scribe_status_line = str(item.get("scribe_status_line") or "").strip()
            heading = f"`{name}`" if name else "`check`"
            line = f"- {heading}"
            if queue_shape:
                line += f" (`{queue_shape}`)"
            if primary_status_line:
                line += f": `{primary_status_line}`"
            lines.append(line)
            if runtime_status_line:
                lines.append(f"  - runtime_status_line: `{runtime_status_line}`")
            if anchor_status_line:
                lines.append(f"  - anchor_status_line: `{anchor_status_line}`")
            if problem_route_status_line:
                lines.append(f"  - problem_route_status_line: `{problem_route_status_line}`")
            if problem_route_secondary_labels:
                lines.append(
                    f"  - problem_route_secondary_labels: `{problem_route_secondary_labels}`"
                )
            if str(item.get("dream_weekly_alignment_line") or "").strip():
                lines.append(
                    f"  - dream_weekly_alignment_line: `{item['dream_weekly_alignment_line']}`"
                )
            if artifact_policy_status_line:
                lines.append(f"  - artifact_policy_status_line: `{artifact_policy_status_line}`")
            if str(item.get("semantic_retrieval_protocol") or "").strip():
                lines.append(
                    "  - semantic_retrieval_protocol: " f"`{item['semantic_retrieval_protocol']}`"
                )
            if str(item.get("semantic_preferred_neighborhood") or "").strip():
                lines.append(
                    "  - semantic_preferred_neighborhood: "
                    f"`{item['semantic_preferred_neighborhood']}`"
                )
            if scribe_status_line:
                lines.append(f"  - scribe_status_line: `{scribe_status_line}`")
            if str(item.get("admissibility_primary_status_line") or "").strip():
                lines.append(
                    "  - admissibility_primary_status_line: "
                    f"`{item['admissibility_primary_status_line']}`"
                )
            lines.append(
                "  - requires_operator_action: "
                f"`{item.get('requires_operator_action', 'false')}`"
            )

    lines.append("")
    lines.append("## Repo Intelligence Mirror")
    if isinstance(repo_intelligence_preview, dict):
        if str(repo_intelligence_preview.get("path") or "").strip():
            lines.append(f"- path: `{repo_intelligence_preview.get('path', '')}`")
        if str(repo_intelligence_preview.get("name") or "").strip():
            lines.append(f"- name: `{repo_intelligence_preview.get('name', '')}`")
        lines.append(f"- queue_shape: `{repo_intelligence_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{repo_intelligence_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{repo_intelligence_preview.get('primary_status_line', '')}`"
        )
        if str(repo_intelligence_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{repo_intelligence_preview.get('runtime_status_line', '')}`"
            )
        if str(repo_intelligence_preview.get("semantic_retrieval_protocol") or "").strip():
            lines.append(
                "- semantic_retrieval_protocol: "
                f"`{repo_intelligence_preview.get('semantic_retrieval_protocol', '')}`"
            )
        if str(repo_intelligence_preview.get("semantic_preferred_neighborhood") or "").strip():
            lines.append(
                "- semantic_preferred_neighborhood: "
                f"`{repo_intelligence_preview.get('semantic_preferred_neighborhood', '')}`"
            )
        if str(repo_intelligence_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{repo_intelligence_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Repo Semantic Atlas Mirror")
    repo_semantic_atlas_preview = payload.get("repo_semantic_atlas_preview")
    if isinstance(repo_semantic_atlas_preview, dict):
        if str(repo_semantic_atlas_preview.get("path") or "").strip():
            lines.append(f"- path: `{repo_semantic_atlas_preview.get('path', '')}`")
        if str(repo_semantic_atlas_preview.get("name") or "").strip():
            lines.append(f"- name: `{repo_semantic_atlas_preview.get('name', '')}`")
        lines.append(f"- queue_shape: `{repo_semantic_atlas_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{repo_semantic_atlas_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{repo_semantic_atlas_preview.get('primary_status_line', '')}`"
        )
        if str(repo_semantic_atlas_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{repo_semantic_atlas_preview.get('runtime_status_line', '')}`"
            )
        if str(repo_semantic_atlas_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{repo_semantic_atlas_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Weekly Host Status Mirror")
    weekly_host_status_preview = payload.get("weekly_host_status_preview")
    if isinstance(weekly_host_status_preview, dict):
        if str(weekly_host_status_preview.get("path") or "").strip():
            lines.append(f"- path: `{weekly_host_status_preview.get('path', '')}`")
        if str(weekly_host_status_preview.get("name") or "").strip():
            lines.append(f"- name: `{weekly_host_status_preview.get('name', '')}`")
        lines.append(f"- queue_shape: `{weekly_host_status_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{weekly_host_status_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{weekly_host_status_preview.get('primary_status_line', '')}`"
        )
        if str(weekly_host_status_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{weekly_host_status_preview.get('runtime_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("anchor_status_line") or "").strip():
            lines.append(
                f"- anchor_status_line: `{weekly_host_status_preview.get('anchor_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{weekly_host_status_preview.get('problem_route_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{weekly_host_status_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(weekly_host_status_preview.get("dream_weekly_alignment_line") or "").strip():
            lines.append(
                "- dream_weekly_alignment_line: "
                f"`{weekly_host_status_preview.get('dream_weekly_alignment_line', '')}`"
            )
        if str(weekly_host_status_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{weekly_host_status_preview.get('artifact_policy_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("admissibility_primary_status_line") or "").strip():
            lines.append(
                "- admissibility_primary_status_line: "
                f"`{weekly_host_status_preview.get('admissibility_primary_status_line', '')}`"
            )
        if str(weekly_host_status_preview.get("scribe_status_line") or "").strip():
            lines.append(
                f"- scribe_status_line: `{weekly_host_status_preview.get('scribe_status_line', '')}`"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Subjectivity Focus Mirror")
    focus_preview = payload.get("subjectivity_focus_preview")
    if isinstance(focus_preview, dict):
        if str(focus_preview.get("path") or "").strip():
            lines.append(f"- path: `{focus_preview.get('path', '')}`")
        lines.append(f"- name: `{focus_preview.get('name', '')}`")
        lines.append(f"- queue_shape: `{focus_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{focus_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(f"- primary_status_line: `{focus_preview.get('primary_status_line', '')}`")
        if str(focus_preview.get("runtime_status_line") or "").strip():
            lines.append(f"- runtime_status_line: `{focus_preview.get('runtime_status_line', '')}`")
        if str(focus_preview.get("scribe_status_line") or "").strip():
            lines.append(f"- scribe_status_line: `{focus_preview.get('scribe_status_line', '')}`")
        if str(focus_preview.get("anchor_status_line") or "").strip():
            lines.append(f"- anchor_status_line: `{focus_preview.get('anchor_status_line', '')}`")
        if str(focus_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{focus_preview.get('problem_route_status_line', '')}`"
            )
        if str(focus_preview.get("problem_route_secondary_labels") or "").strip():
            lines.append(
                "- problem_route_secondary_labels: "
                f"`{focus_preview.get('problem_route_secondary_labels', '')}`"
            )
        if str(focus_preview.get("dream_weekly_alignment_line") or "").strip():
            lines.append(
                "- dream_weekly_alignment_line: "
                f"`{focus_preview.get('dream_weekly_alignment_line', '')}`"
            )
        if str(focus_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{focus_preview.get('artifact_policy_status_line', '')}`"
            )
        if str(focus_preview.get("admissibility_primary_status_line") or "").strip():
            lines.append(
                "- admissibility_primary_status_line: "
                f"`{focus_preview.get('admissibility_primary_status_line', '')}`"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Agent Integrity Mirror")
    if isinstance(agent_integrity_preview, dict):
        if str(agent_integrity_preview.get("path") or "").strip():
            lines.append(f"- path: `{agent_integrity_preview.get('path', '')}`")
        if str(agent_integrity_preview.get("name") or "").strip():
            lines.append(f"- name: `{agent_integrity_preview.get('name', '')}`")
        lines.append(f"- queue_shape: `{agent_integrity_preview.get('queue_shape', '')}`")
        lines.append(
            "- requires_operator_action: "
            f"`{agent_integrity_preview.get('requires_operator_action', 'false')}`"
        )
        lines.append(
            f"- primary_status_line: `{agent_integrity_preview.get('primary_status_line', '')}`"
        )
        if str(agent_integrity_preview.get("runtime_status_line") or "").strip():
            lines.append(
                f"- runtime_status_line: `{agent_integrity_preview.get('runtime_status_line', '')}`"
            )
        if str(agent_integrity_preview.get("problem_route_status_line") or "").strip():
            lines.append(
                "- problem_route_status_line: "
                f"`{agent_integrity_preview.get('problem_route_status_line', '')}`"
            )
        if str(agent_integrity_preview.get("artifact_policy_status_line") or "").strip():
            lines.append(
                "- artifact_policy_status_line: "
                f"`{agent_integrity_preview.get('artifact_policy_status_line', '')}`"
            )
    else:
        lines.append("- None")

    if failed:
        lines.append("")
        lines.append("## Failures")
        for item in failed:
            detail = item.get("stderr_tail") or item.get("stdout_tail") or "no output"
            lines.append(f"- `{item['name']}`: {detail}")

    if skipped:
        lines.append("")
        lines.append("## Skipped")
        for item in skipped:
            lines.append(f"- `{item['name']}`: {item.get('skip_reason', 'skipped')}")

    recovery_advice = payload.get("recovery_advice", [])
    if recovery_advice:
        lines.append("")
        lines.append("## Recovery Advice")
        for item in recovery_advice:
            detail = item.get("detail") or {}
            recommendation = detail.get("recommendation") or item.get("status")
            rationale = detail.get("rationale") or item.get("stderr_tail") or "no detail"
            lines.append(f"- `{item['name']}`: {recommendation}")
            lines.append(f"  - rationale: {rationale}")
            if detail.get("suggested_commands"):
                lines.append("  - suggested_commands:")
                for command in detail["suggested_commands"]:
                    lines.append(f"    - `{command}`")

    return "\n".join(lines) + "\n"


def _collect_recovery_advice(
    *,
    checks: list[dict[str, Any]],
    repo_root: Path,
    python_executable: str,
) -> list[dict[str, Any]]:
    commit_attribution = next(
        (item for item in checks if item["name"] == "commit_attribution"), None
    )
    if commit_attribution is None or commit_attribution["status"] != "fail":
        return []

    command = [
        python_executable,
        "scripts/plan_commit_attribution_base_switch.py",
        "--artifact-path",
        COMMIT_ATTRIBUTION_BASE_SWITCH_ARTIFACT,
    ]
    result, payload = _run_json_command("commit_attribution_recovery", command, repo_root)
    detail = {}
    if payload is not None:
        detail = {
            "recommendation": payload.get("recommendation"),
            "rationale": payload.get("rationale"),
            "tree_equal": payload.get("tree_equal"),
            "current_missing_count": payload.get("current_missing_count"),
            "backfill_missing_count": payload.get("backfill_missing_count"),
            "suggested_commands": payload.get("suggested_commands", []),
        }
    result["artifact_path"] = COMMIT_ATTRIBUTION_BASE_SWITCH_ARTIFACT
    result["detail"] = detail
    return [result]


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
    parser = argparse.ArgumentParser(description="Run repository health checks.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--discussion-path",
        default=str(DISCUSSION_CURATED_PATH),
        help="Discussion channel path used by verify_7d precheck.",
    )
    parser.add_argument(
        "--allow-missing-discussion",
        action="store_true",
        help="Skip verify_7d when discussion file is absent.",
    )
    parser.add_argument(
        "--include-sdh",
        action="store_true",
        help="Pass --include-sdh to verify_7d (requires web/backend services).",
    )
    parser.add_argument(
        "--web-base",
        default=None,
        help="Optional web base passed to verify_7d when --include-sdh is enabled.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Optional api base passed to verify_7d when --include-sdh is enabled.",
    )
    parser.add_argument(
        "--sdh-timeout",
        type=int,
        default=None,
        help="Optional timeout seconds passed to verify_7d when --include-sdh is enabled.",
    )
    parser.add_argument(
        "--check-council-modes",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Pass council mode switch checks to verify_7d SDH smoke.",
    )
    parser.add_argument(
        "--strict-soft-fail",
        action="store_true",
        help="Pass --strict-soft-fail to verify_7d.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any blocking check fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    discussion_path = (repo_root / args.discussion_path).resolve()
    allow_missing_discussion = bool(args.allow_missing_discussion) or _is_ci_environment()

    specs = _build_check_specs(
        python_executable=sys.executable,
        include_sdh=bool(args.include_sdh),
        check_council_modes=bool(args.check_council_modes),
        strict_soft_fail=bool(args.strict_soft_fail),
        web_base=args.web_base,
        api_base=args.api_base,
        sdh_timeout=args.sdh_timeout,
        allow_missing_discussion=allow_missing_discussion,
        discussion_path=discussion_path,
    )

    checks: list[dict[str, Any]] = []
    handoff_previews: list[dict[str, str]] = []
    for spec in specs:
        skip_reason = spec.get("skip_reason")
        if skip_reason:
            checks.append(_skip_check(spec["name"], spec["command"], skip_reason))
            continue
        if spec.get("structured_output") == "json":
            result, structured_payload = _run_json_command(spec["name"], spec["command"], repo_root)
            preview = _check_handoff_preview(spec["name"], structured_payload)
            if preview is not None:
                handoff_previews.append(preview)
            checks.append(result)
            continue
        checks.append(_run_check(spec["name"], spec["command"], repo_root))

    passive_status_previews: list[dict[str, str]] = []
    for spec in PASSIVE_STATUS_PREVIEW_SPECS:
        preview = _load_status_artifact_preview(
            repo_root,
            name=str(spec.get("name") or ""),
            path=str(spec.get("path") or ""),
        )
        if preview is not None:
            passive_status_previews.append(preview)

    overall_ok = all(item["status"] in {"pass", "skip"} for item in checks)
    recovery_advice = _collect_recovery_advice(
        checks=checks,
        repo_root=repo_root,
        python_executable=sys.executable,
    )
    repo_intelligence_preview = _select_handoff_preview(
        handoff_previews,
        queue_shape="repo_intelligence_ready",
    )
    weekly_host_status_preview = _select_handoff_preview(
        handoff_previews,
        queue_shape="weekly_host_status",
    )
    subjectivity_focus_preview = _select_subjectivity_focus_preview(handoff_previews)
    if subjectivity_focus_preview is None:
        subjectivity_focus_preview = _select_named_preview(
            passive_status_previews,
            name="subjectivity_review_batch",
        )
    repo_semantic_atlas_preview = _select_named_preview(
        passive_status_previews,
        name="repo_semantic_atlas",
    )
    agent_integrity_preview = _select_named_preview(
        passive_status_previews,
        name="agent_integrity",
    )
    dream_observability_preview = _select_named_preview(
        passive_status_previews,
        name="dream_observability",
    )
    scribe_status_preview = _select_named_preview(
        passive_status_previews,
        name="scribe_status",
    )
    dream_weekly_alignment_line = str(
        (weekly_host_status_preview or {}).get("dream_weekly_alignment_line") or ""
    ).strip() or build_dream_weekly_alignment_line(
        weekly_host_status_preview,
        dream_observability_preview,
    )
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "config": {
            "include_sdh": bool(args.include_sdh),
            "web_base": args.web_base,
            "api_base": args.api_base,
            "sdh_timeout": args.sdh_timeout,
            "check_council_modes": bool(args.check_council_modes),
            "strict_soft_fail": bool(args.strict_soft_fail),
            "allow_missing_discussion": allow_missing_discussion,
        },
        "checks": checks,
        "handoff_previews": handoff_previews,
        "passive_status_previews": passive_status_previews,
        "repo_intelligence_preview": repo_intelligence_preview,
        "weekly_host_status_preview": weekly_host_status_preview,
        "subjectivity_focus_preview": subjectivity_focus_preview,
        "repo_semantic_atlas_preview": repo_semantic_atlas_preview,
        "agent_integrity_preview": agent_integrity_preview,
        "dream_observability_preview": dream_observability_preview,
        "scribe_status_preview": scribe_status_preview,
        "dream_weekly_alignment_line": dream_weekly_alignment_line,
        "recovery_advice": recovery_advice,
    }

    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not overall_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
