#!/usr/bin/env python3
"""Run the bounded ToneSoul publish/push posture preflight."""

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
        description="Run the ToneSoul publish/push posture preflight.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    return parser


def run_publish_push_preflight(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, object]:
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.publish_push_preflight import build_publish_push_preflight

    payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
    )

    readiness = payload.get("readiness") or {}
    import_posture = payload.get("import_posture") or {}
    repo_state_awareness = payload.get("repo_state_awareness") or {}
    preflight = build_publish_push_preflight(
        readiness=readiness,
        import_posture=import_posture,
        repo_state_awareness=repo_state_awareness,
    )

    return {
        "contract_version": "v1",
        "bundle": "publish_push_preflight",
        "agent": agent,
        "readiness": str(readiness.get("status", "unknown") or "unknown"),
        "repo_state": str(
            repo_state_awareness.get("classification", "unknown") or "unknown"
        ),
        "launch_tier": str(
            (
                ((import_posture.get("surfaces") or {}).get("launch_claims") or {}).get(
                    "launch_claim_posture"
                )
                or {}
            ).get("current_tier", "unknown")
            or "unknown"
        ),
        "preflight": preflight,
        "underlying_commands": [
            f"python scripts/start_agent_session.py --agent {agent} --no-ack",
            f"python scripts/run_publish_push_preflight.py --agent {agent}",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_publish_push_preflight(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
