#!/usr/bin/env python3
"""Run the bounded ToneSoul task-board parking preflight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the ToneSoul task-board parking preflight.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--proposal-kind", default="unspecified")
    parser.add_argument("--target-path", default="task.md")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    return parser


def run_task_board_preflight(
    *,
    agent: str,
    proposal_kind: str,
    target_path: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, object]:
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.task_board_preflight import build_task_board_preflight

    payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
    )

    readiness = payload.get("readiness") or {}
    canonical_center = payload.get("canonical_center") or {}
    task_track_hint = payload.get("task_track_hint") or {}
    preflight = build_task_board_preflight(
        readiness=readiness,
        canonical_center=canonical_center,
        task_track_hint=task_track_hint,
        proposal_kind=proposal_kind,
        target_path=target_path,
    )

    return {
        "contract_version": "v1",
        "bundle": "task_board_preflight",
        "agent": agent,
        "proposal_kind": proposal_kind,
        "target_path": target_path,
        "readiness": str(readiness.get("status", "unknown") or "unknown"),
        "task_track": str(task_track_hint.get("suggested_track", "unclassified") or "unclassified"),
        "preflight": preflight,
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent} --no-ack",
            (
                f"python scripts/run_task_board_preflight.py --agent {agent} "
                f"--proposal-kind {proposal_kind} --target-path {target_path}"
            ),
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_task_board_preflight(
        agent=str(args.agent).strip(),
        proposal_kind=str(args.proposal_kind).strip(),
        target_path=str(args.target_path).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
