#!/usr/bin/env python3
"""Manage ToneSoul task claims for multi-terminal coordination."""

from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage ToneSoul task claims")
    sub = parser.add_subparsers(dest="command", required=True)

    claim_parser = sub.add_parser("claim")
    claim_parser.add_argument("task_id")
    claim_parser.add_argument("--agent", required=True)
    claim_parser.add_argument("--summary", default="")
    claim_parser.add_argument("--path", action="append", dest="paths", default=[])
    claim_parser.add_argument("--ttl-seconds", type=int, default=1800)

    release_parser = sub.add_parser("release")
    release_parser.add_argument("task_id")
    release_parser.add_argument("--agent", default=None)

    sub.add_parser("list")

    args = parser.parse_args()

    from tonesoul.runtime_adapter import claim_task, list_active_claims, release_task_claim

    if args.command == "claim":
        payload = claim_task(
            args.task_id,
            agent_id=args.agent,
            summary=args.summary,
            paths=args.paths,
            source="cli",
            ttl_seconds=args.ttl_seconds,
        )
    elif args.command == "release":
        payload = release_task_claim(args.task_id, agent_id=args.agent)
    else:
        payload = {"claims": list_active_claims()}

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
