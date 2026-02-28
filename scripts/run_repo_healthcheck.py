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
            "name": "philosophical_reflection",
            "command": [
                python_executable,
                "scripts/run_philosophical_reflection_report.py",
                "--strict",
            ],
        },
        {
            "name": "audit_7d",
            "command": verify_7d_cmd,
        },
    ]

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
    }

    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not overall_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
