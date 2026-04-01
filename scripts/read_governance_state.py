#!/usr/bin/env python3
"""Read and display current governance state for any AI agent.

This is the universal "session start" script.
Any AI agent (Antigravity, Codex, VS Code assistant) should run this
at the beginning of a session to inherit governance posture.

Usage:
    python scripts/read_governance_state.py
    python scripts/read_governance_state.py --state /path/to/governance_state.json
    python scripts/read_governance_state.py --json  # machine-readable output

If no --state is given, searches these locations in order:
    1. ./governance_state.json  (repo-local, for testing)
    2. ~/.gemini/tonesoul/governance_state.json  (Antigravity)
    3. ~/.codex/memories/governance_state.json   (Codex)
    4. ~/.tonesoul/governance_state.json         (generic)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TENSION_DECAY_ALPHA = 0.05

SEARCH_PATHS = [
    Path("governance_state.json"),
    Path.home() / ".gemini" / "tonesoul" / "governance_state.json",
    Path.home() / ".codex" / "memories" / "governance_state.json",
    Path.home() / ".tonesoul" / "governance_state.json",
]


def find_state_file() -> Path | None:
    """Search known locations for governance_state.json."""
    for p in SEARCH_PATHS:
        if p.exists():
            return p
    return None


def severity_bar(severity: float) -> str:
    """Visual bar for severity 0-1."""
    filled = int(severity * 10)
    return "█" * filled + "░" * (10 - filled)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read governance state")
    parser.add_argument("--state", type=Path, default=None)
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON for machine consumption",
    )
    args = parser.parse_args()

    state_path = args.state or find_state_file()
    if state_path is None or not state_path.exists():
        print("No governance_state.json found.")
        print("Searched:", ", ".join(str(p) for p in SEARCH_PATHS))
        print("\nRun: python scripts/init_governance_state.py --output <path>")
        sys.exit(1)

    assert state_path is not None  # type guard after sys.exit
    state = json.loads(state_path.read_text(encoding="utf-8"))

    if args.json_output:
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    # --- Human-readable report ---
    now = datetime.now(timezone.utc)
    last = datetime.fromisoformat(state["last_updated"])
    hours_ago = (now - last).total_seconds() / 3600.0

    print("=" * 60)
    print("  ToneSoul Governance State")
    print("=" * 60)
    print(f"  Source:         {state_path}")
    print(f"  Last updated:   {state['last_updated']} ({hours_ago:.1f}h ago)")
    print(f"  Session count:  {state['session_count']}")
    print(f"  Soul integral:  {state['soul_integral']:.4f}")
    print()

    # Baseline drift
    drift = state.get("baseline_drift", {})
    print("  Baseline Drift:")
    print(f"    Caution:     {drift.get('caution_bias', 0.5):.4f}  (0.5 = neutral)")
    print(f"    Innovation:  {drift.get('innovation_bias', 0.5):.4f}  (Fan prefers >0.5)")
    print(f"    Autonomy:    {drift.get('autonomy_level', 0.5):.4f}  (<0.5 = human-led)")
    print()

    # Active vows
    vows = state.get("active_vows", [])
    if vows:
        print(f"  Active Vows ({len(vows)}):")
        for v in vows:
            print(f"    [{v['id']}] {v['content']}")
        print()

    # Tension history (with decay preview)
    tensions = state.get("tension_history", [])
    if tensions:
        print(f"  Tension History ({len(tensions)} events):")
        for t in tensions:
            ts = datetime.fromisoformat(t["timestamp"])
            h = (now - ts).total_seconds() / 3600.0
            decayed = t["severity"] * math.exp(-TENSION_DECAY_ALPHA * h)
            bar = severity_bar(decayed)
            print(f"    {bar} {decayed:.2f}  {t['topic'][:50]}")
            if t.get("resolution"):
                print(f"              -> {t['resolution'][:50]}")
        print()

    # Aegis vetoes
    vetoes = state.get("aegis_vetoes", [])
    if vetoes:
        print(f"  Aegis Vetoes ({len(vetoes)}):")
        for v in vetoes:
            print(f"    [{v.get('timestamp', '?')}] {v['topic']}: {v['reason']}")
        print()

    print("=" * 60)
    print("  Ready. Governance posture loaded.")
    print("=" * 60)


if __name__ == "__main__":
    main()
