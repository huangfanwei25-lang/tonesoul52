"""
Run monthly consolidation checks and publish status artifacts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
        rendered.append(text)
    return " ".join(rendered)


def _run_json(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload: dict[str, Any]
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": proc.stdout.strip(), "raw_stderr": proc.stderr.strip()}
    return {
        "command": _display_command(cmd),
        "exit_code": int(proc.returncode),
        "ok": proc.returncode == 0,
        "payload": payload,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run monthly consolidation checks.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if any consolidation check fails.",
    )
    parser.add_argument(
        "--allow-missing-discussion",
        action="store_true",
        help="Allow missing discussion files for memory hygiene checks (CI-friendly).",
    )
    return parser


def _build_check_commands(allow_missing_discussion: bool) -> dict[str, list[str]]:
    memory_hygiene_cmd = [
        sys.executable,
        "scripts/verify_memory_hygiene.py",
        "--tail-lines",
        "200",
        "--discussion-path",
        "memory/agent_discussion_curated.jsonl",
    ]
    if allow_missing_discussion:
        memory_hygiene_cmd.append("--allow-missing-discussion")

    return {
        "7d": [sys.executable, "scripts/verify_7d.py"],
        "memory_hygiene": memory_hygiene_cmd,
        "memory_quality": [sys.executable, "scripts/run_memory_quality_report.py", "--strict"],
        "layer_boundaries": [sys.executable, "scripts/verify_layer_boundaries.py"],
        "docs_consistency": [sys.executable, "scripts/verify_docs_consistency.py"],
        "persona_swarm": [sys.executable, "scripts/run_persona_swarm_framework.py", "--strict"],
    }


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()

    check_commands = _build_check_commands(allow_missing_discussion=args.allow_missing_discussion)
    checks = {name: _run_json(cmd, repo_root) for name, cmd in check_commands.items()}

    overall_ok = all(item.get("ok", False) for item in checks.values())
    generated_at = _iso_now()

    snapshot_7d = {
        "generated_at": generated_at,
        "source": "scripts/verify_7d.py",
        "result": checks["7d"],
    }
    consolidation_report = {
        "generated_at": generated_at,
        "config": {
            "allow_missing_discussion": bool(args.allow_missing_discussion),
        },
        "overall_ok": overall_ok,
        "checks": checks,
    }

    _write_json(out_dir / "7d_snapshot.json", snapshot_7d)
    _write_json(out_dir / "monthly_consolidation_report.json", consolidation_report)

    _emit(consolidation_report)
    if args.strict and not overall_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
