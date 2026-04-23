"""
session_pulse.py — minimal file-backed session heartbeat.

Reads current repo state (git, tests, open tasks) and writes a pulse record
to memory/session_pulse_latest.json. Works without Redis, gateway, or any
external service.

Usage:
    python scripts/session_pulse.py --agent claude-sonnet-4-6
    python scripts/session_pulse.py --agent claude-sonnet-4-6 --note "starting Day 2 work"

Purpose: give each AI session a tangible "beat" — a moment of taking stock
before acting. Addresses the memory fragmentation problem by making the current
state machine-readable and git-trackable.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PULSE_PATH = REPO_ROOT / "memory" / "session_pulse_latest.json"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _read_task_md_short_board() -> str:
    task_md = REPO_ROOT / "task.md"
    if not task_md.exists():
        return "task.md not found"
    lines = task_md.read_text(encoding="utf-8").splitlines()
    board: list[str] = []
    in_board = False
    for line in lines:
        if "Current short board" in line or "short board" in line.lower():
            in_board = True
        if in_board:
            board.append(line)
            if len(board) > 8:
                break
    return "\n".join(board[:8]) if board else "short board not found"


def _count_open_phases() -> list[str]:
    task_md = REPO_ROOT / "task.md"
    if not task_md.exists():
        return []
    text = task_md.read_text(encoding="utf-8")
    pending = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Phase") and "~~" not in stripped:
            pending.append(stripped[:80])
    return pending[:5]


def _git_status_summary() -> dict:
    branch = _git("branch", "--show-current")
    ahead_behind = _git("rev-list", "--count", "--left-right", "origin/master...HEAD")
    parts = ahead_behind.split("\t") if "\t" in ahead_behind else ["0", "0"]
    uncommitted = _git("status", "--short")
    last_commit = _git("log", "-1", "--format=%h %s")
    return {
        "branch": branch,
        "ahead_of_master": parts[1].strip() if len(parts) > 1 else "0",
        "behind_master": parts[0].strip(),
        "uncommitted_files": len([ln for ln in uncommitted.splitlines() if ln.strip()]),
        "last_commit": last_commit,
    }


def _run_test_count() -> str:
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(REPO_ROOT / "tests"),
                "--continue-on-collection-errors",
                "-q",
                "--co",
                "--tb=no",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        lines = result.stdout.splitlines() + result.stderr.splitlines()
        for line in reversed(lines):
            if "selected" in line or "collected" in line or "error" in line:
                return line.strip()
        return "count unavailable"
    except Exception as e:
        return f"error: {e}"


def build_pulse(agent: str, note: str = "") -> dict:
    git_state = _git_status_summary()
    pending_phases = _count_open_phases()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "note": note,
        "git": git_state,
        "pending_phases": pending_phases,
        "short_board": _read_task_md_short_board(),
        "pulse_schema": "v1",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a session pulse record.")
    parser.add_argument("--agent", default="unknown-agent")
    parser.add_argument("--note", default="")
    parser.add_argument(
        "--no-test-count", action="store_true", help="Skip slow test collection count"
    )
    args = parser.parse_args()

    pulse = build_pulse(args.agent, args.note)

    if not args.no_test_count:
        pulse["test_collection_summary"] = _run_test_count()

    PULSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PULSE_PATH.write_text(json.dumps(pulse, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(pulse, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
