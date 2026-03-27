#!/usr/bin/env python3
"""Emit a compact R-memory packet for agents and local operator tooling."""

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


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Emit ToneSoul R-memory packet")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--agent", type=str, default="")
    parser.add_argument("--ack", action="store_true")
    parser.add_argument("--trace-limit", type=int, default=5)
    parser.add_argument("--visitor-limit", type=int, default=5)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.ack and not str(args.agent or "").strip():
        parser.error("--ack requires --agent")

    from tonesoul.runtime_adapter import (
        acknowledge_observer_cursor,
        load,
        r_memory_packet,
    )

    store = None
    posture = None
    if args.state_path is not None or args.traces_path is not None:
        from tonesoul.backends.file_store import FileStore

        if args.traces_path is not None:
            claim_root = args.traces_path.parent
            zones_path = args.traces_path.parent / "zone_registry.json"
        elif args.state_path is not None:
            claim_root = args.state_path.parent
            zones_path = args.state_path.parent / "zone_registry.json"
        else:
            claim_root = Path(".")
            zones_path = None

        store = FileStore(
            gov_path=args.state_path,
            traces_path=args.traces_path,
            zones_path=zones_path,
            claims_path=_resolve_sidecar(claim_root, "task_claims.json"),
            perspectives_path=_resolve_sidecar(claim_root, "perspectives.json"),
            checkpoints_path=_resolve_sidecar(claim_root, "checkpoints.json"),
            compactions_path=_resolve_sidecar(claim_root, "compacted.json"),
            subject_snapshots_path=_resolve_sidecar(claim_root, "subject_snapshots.json"),
            observer_cursors_path=_resolve_sidecar(claim_root, "observer_cursors.json"),
        )
        posture = load(state_path=args.state_path)

    packet = r_memory_packet(
        posture=posture,
        store=store,
        observer_id=str(args.agent or "").strip(),
        trace_limit=args.trace_limit,
        visitor_limit=args.visitor_limit,
    )
    if args.ack:
        acknowledge_observer_cursor(str(args.agent or "").strip(), packet=packet, store=store)
    text = json.dumps(packet, indent=2, ensure_ascii=False) + "\n"

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print(text, end="")


if __name__ == "__main__":
    main()
