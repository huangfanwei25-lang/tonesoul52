#!/usr/bin/env python3
"""Initialize a fresh governance_state.json for a ToneSoul developer agent.

Usage:
    python scripts/init_governance_state.py --output ~/path/to/governance_state.json
    python scripts/init_governance_state.py  # defaults to ./governance_state.json

This script is safe to run multiple times; it will NOT overwrite an existing
file unless --force is passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

INITIAL_STATE = {
    "version": "0.1.0",
    "last_updated": "",  # filled at runtime
    "soul_integral": 0.0,
    "tension_history": [],
    "active_vows": [
        {
            "id": "vow-001",
            "content": "Do not commit personal memory data to the public repo",
            "created": "2026-02-21",
            "source": "AGENTS.md",
        },
        {
            "id": "vow-002",
            "content": "Do not modify protected human-managed files (AGENTS.md, MEMORY.md, .env)",
            "created": "2026-02-21",
            "source": "AGENTS.md",
        },
        {
            "id": "vow-003",
            "content": "Stop and reassess after 3 consecutive failures",
            "created": "2026-02-21",
            "source": "AGENTS.md",
        },
    ],
    "aegis_vetoes": [],
    "baseline_drift": {
        "caution_bias": 0.50,
        "innovation_bias": 0.60,
        "autonomy_level": 0.35,
    },
    "session_count": 0,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize governance state")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("governance_state.json"),
        help="Output file path (default: ./governance_state.json)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="Soul profile name (e.g. 'default', 'cautious-guardian', 'creative-explorer') or path to .soul.json",
    )
    args = parser.parse_args()

    if args.output.exists() and not args.force:
        print(f"ERROR: {args.output} already exists. Use --force to overwrite.")
        sys.exit(1)

    state = INITIAL_STATE.copy()
    state["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Load soul profile if specified
    if args.profile:
        profile_path = Path(args.profile)
        if not profile_path.exists():
            # Try looking in memory/profiles/
            repo_root = Path(__file__).resolve().parent.parent
            profile_path = repo_root / "memory" / "profiles" / f"{args.profile}.soul.json"
        if not profile_path.exists():
            print(f"ERROR: Soul profile not found: {args.profile}")
            print("Available profiles in memory/profiles/:")
            profiles_dir = Path(__file__).resolve().parent.parent / "memory" / "profiles"
            if profiles_dir.exists():
                for p in sorted(profiles_dir.glob("*.soul.json")):
                    print(f"  - {p.stem.replace('.soul', '')}")
            sys.exit(1)

        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        print(f"Loading soul profile: {profile.get('profile_name', 'unknown')}")
        if profile.get("description"):
            print(f"  {profile['description']}")

        # Apply profile overrides
        if "baseline_drift" in profile:
            state["baseline_drift"] = profile["baseline_drift"]
        if "initial_vows" in profile:
            state["active_vows"] = [
                {**v, "created": state["last_updated"][:10]} for v in profile["initial_vows"]
            ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Initialized governance state at: {args.output}")


if __name__ == "__main__":
    main()
