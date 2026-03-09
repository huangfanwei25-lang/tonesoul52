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

DISCUSSION_CURATED_PATH = Path("memory/agent_discussion_curated.jsonl")
JSON_FILENAME = "repo_healthcheck_latest.json"
MARKDOWN_FILENAME = "repo_healthcheck_latest.md"
DEFAULT_MAX_TRACKED_IGNORED = 28
COMMIT_ATTRIBUTION_BASE_SWITCH_ARTIFACT = "docs/status/commit_attribution_base_switch_latest.json"


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
            "name": "true_verification_weekly",
            "command": [
                python_executable,
                "scripts/report_true_verification_task_status.py",
                "--strict",
            ],
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
    lines = [
        "# Repo Healthcheck Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
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
    for spec in specs:
        skip_reason = spec.get("skip_reason")
        if skip_reason:
            checks.append(_skip_check(spec["name"], spec["command"], skip_reason))
            continue
        checks.append(_run_check(spec["name"], spec["command"], repo_root))

    overall_ok = all(item["status"] in {"pass", "skip"} for item in checks)
    recovery_advice = _collect_recovery_advice(
        checks=checks,
        repo_root=repo_root,
        python_executable=sys.executable,
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
