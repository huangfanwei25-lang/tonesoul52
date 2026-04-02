#!/usr/bin/env python3
"""Run the bounded shared-edit path-overlap preflight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_repo_root_on_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check shared edit path overlap against visible claims.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--path", action="append", dest="paths", default=[])
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main() -> None:
    _ensure_repo_root_on_path()

    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.shared_edit_preflight import build_shared_edit_preflight

    args = build_parser().parse_args()
    agent_id = str(args.agent or "").strip()
    if not agent_id:
        raise SystemExit("--agent is required")
    if not args.paths:
        raise SystemExit("At least one --path is required.")

    session_start = run_session_start_bundle(
        agent_id=agent_id,
        state_path=args.state_path,
        traces_path=args.traces_path,
        no_ack=True,
    )
    preflight = build_shared_edit_preflight(
        agent_id=agent_id,
        candidate_paths=args.paths,
        readiness=session_start.get("readiness") or {},
        claims=list((session_start.get("claim_view") or {}).get("claims") or []),
        task_track_hint=session_start.get("task_track_hint") or {},
        mutation_preflight=session_start.get("mutation_preflight") or {},
        working_style_playbook=session_start.get("working_style_playbook") or {},
    )
    payload = {
        "contract_version": "v1",
        "bundle": "shared_edit_preflight",
        "agent": agent_id,
        "readiness": (session_start.get("readiness") or {}).get("status", "unknown"),
        "task_track": (session_start.get("task_track_hint") or {}).get(
            "suggested_track",
            "unclassified",
        ),
        "preflight": preflight,
        "underlying_commands": [
            "python scripts/run_task_claim.py list",
            preflight.get("recommended_command") or "",
        ],
    }

    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
