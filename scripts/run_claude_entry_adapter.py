#!/usr/bin/env python3
"""Run the bounded Claude-compatible ToneSoul entry adapter."""

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
        description="Run the bounded Claude-compatible ToneSoul entry adapter.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    return parser


def run_claude_entry_adapter(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, object]:
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.claude_entry_adapter import build_claude_entry_adapter

    session_start = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=1,
    )
    adapter = build_claude_entry_adapter(session_start_payload=session_start)

    return {
        "contract_version": "v1",
        "bundle": "claude_entry_adapter",
        "agent": agent,
        "session_start_tier": int(session_start.get("tier", 1) or 1),
        "adapter": adapter,
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent} --tier 1 --no-ack",
            f"python scripts/run_claude_entry_adapter.py --agent {agent}",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_claude_entry_adapter(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
