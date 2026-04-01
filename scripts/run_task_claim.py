#!/usr/bin/env python3
"""Manage ToneSoul task claims for multi-terminal coordination."""

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


def _resolve_sidecar(root: Path, name: str) -> Path:
    canonical = root / ".aegis" / name
    legacy = root / name
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return canonical


def _build_store(args):
    if args.state_path is None and args.traces_path is None:
        return None

    from tonesoul.backends.file_store import FileStore

    if args.traces_path is not None:
        root = args.traces_path.parent
        zones_path = root / "zone_registry.json"
    elif args.state_path is not None:
        root = args.state_path.parent
        zones_path = root / "zone_registry.json"
    else:
        root = Path(".")
        zones_path = None

    return FileStore(
        gov_path=args.state_path,
        traces_path=args.traces_path,
        zones_path=zones_path,
        claims_path=_resolve_sidecar(root, "task_claims.json"),
        perspectives_path=_resolve_sidecar(root, "perspectives.json"),
        checkpoints_path=_resolve_sidecar(root, "checkpoints.json"),
        compactions_path=_resolve_sidecar(root, "compacted.json"),
    )


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Manage ToneSoul task claims")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
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

    store = _build_store(args)

    if args.command == "claim":
        if store is None:
            payload = claim_task(
                args.task_id,
                agent_id=args.agent,
                summary=args.summary,
                paths=args.paths,
                source="cli",
                ttl_seconds=args.ttl_seconds,
            )
        else:
            payload = claim_task(
                args.task_id,
                agent_id=args.agent,
                summary=args.summary,
                paths=args.paths,
                source="cli",
                ttl_seconds=args.ttl_seconds,
                store=store,
            )
    elif args.command == "release":
        if store is None:
            payload = release_task_claim(args.task_id, agent_id=args.agent)
        else:
            payload = release_task_claim(args.task_id, agent_id=args.agent, store=store)
    else:
        if store is None:
            payload = {"claims": list_active_claims()}
        else:
            payload = {"claims": list_active_claims(store=store)}

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
