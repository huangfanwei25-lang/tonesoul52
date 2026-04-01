#!/usr/bin/env python3
"""Commit a session trace summary to OpenClaw-Memory as a ToneSoul memory.

Usage:
    python scripts/commit_session_to_memory.py \
        --trace session_trace.json \
        --openclaw-dir ./OpenClaw-Memory

    # Or pipe from stdin:
    echo '{"session_id":"..."}' | python scripts/commit_session_to_memory.py \
        --stdin --openclaw-dir ./OpenClaw-Memory

This script:
  1. Reads a session_trace record
  2. Builds a safe, public-safe summary string
  3. Calls ask_my_brain.py --profile tonesoul --learn [summary] with
     appropriate tension, kind, tags, and wave parameters
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def build_summary(trace: dict) -> str:
    """Build a public-safe one-line summary from the trace."""
    agent = trace.get("agent", "unknown")
    decisions = trace.get("key_decisions", [])
    tensions = trace.get("tension_events", [])

    parts = [f"[{agent}]"]

    if decisions:
        parts.append("Decisions: " + "; ".join(decisions[:3]))

    if tensions:
        top = max(tensions, key=lambda t: t.get("severity", 0))
        parts.append(f"Top tension: {top['topic']} ({top.get('severity', 0):.2f})")

    shift = trace.get("stance_shift")
    if shift:
        parts.append(f"Shift: {shift.get('from', '?')} -> {shift.get('to', '?')}")

    return " | ".join(parts)


def compute_wave_args(trace: dict) -> dict[str, float]:
    """Infer wave vector from trace signals."""
    tensions = trace.get("tension_events", [])
    vetoes = trace.get("aegis_vetoes", [])

    max_tension = max((t.get("severity", 0) for t in tensions), default=0.0)
    has_shift = bool(trace.get("stance_shift"))
    has_vetoes = bool(vetoes)

    return {
        "uncertainty": round(max_tension * 0.8, 2),
        "divergence": round(max_tension * 0.9, 2) if has_shift else round(max_tension * 0.5, 2),
        "risk": 0.90 if has_vetoes else round(max_tension * 0.3, 2),
        "revision": round(max_tension * 0.7, 2) if has_shift else round(max_tension * 0.4, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Commit session trace to OpenClaw-Memory")
    parser.add_argument("--trace", type=Path, default=None)
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument(
        "--openclaw-dir",
        type=Path,
        default=Path("OpenClaw-Memory"),
        help="Path to OpenClaw-Memory directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the command without executing",
    )
    args = parser.parse_args()

    # Load trace
    if args.stdin:
        trace = json.loads(sys.stdin.read())
    elif args.trace:
        trace = json.loads(args.trace.read_text(encoding="utf-8"))
    else:
        print("ERROR: Provide --trace or --stdin")
        sys.exit(1)

    ask_brain = args.openclaw_dir / "ask_my_brain.py"
    if not ask_brain.exists() and not args.dry_run:
        print(f"ERROR: ask_my_brain.py not found at {ask_brain}")
        print("Make sure --openclaw-dir points to the OpenClaw-Memory directory.")
        sys.exit(1)

    summary = build_summary(trace)
    tensions = trace.get("tension_events", [])
    max_tension = max((t.get("severity", 0) for t in tensions), default=0.0)
    waves = compute_wave_args(trace)

    # Build tags
    tags = ["governance", "session-trace"]
    for t in tensions:
        if t.get("type"):
            tags.append(t["type"])

    cmd = [
        sys.executable,
        str(ask_brain),
        "--profile",
        "tonesoul",
        "--learn",
        summary,
        "--kind",
        "session_trace",
        "--tension",
        f"{max_tension:.2f}",
        "--tag",
        ",".join(tags[:5]),
        f"--wave-uncertainty",
        f"{waves['uncertainty']:.2f}",
        f"--wave-divergence",
        f"{waves['divergence']:.2f}",
        f"--wave-risk",
        f"{waves['risk']:.2f}",
        f"--wave-revision",
        f"{waves['revision']:.2f}",
    ]

    if args.dry_run:
        print("DRY RUN — would execute:")
        print(" ".join(cmd))
        return

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(args.openclaw_dir))
    if result.returncode == 0:
        print(f"Session committed to OpenClaw-Memory: {summary[:80]}...")
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        print(f"ERROR: ask_my_brain.py failed (exit {result.returncode})")
        if result.stderr.strip():
            print(result.stderr.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()
