#!/usr/bin/env python3
"""Write a bounded non-canonical checkpoint to ToneSoul shared R-memory."""

from __future__ import annotations

import argparse
import json
import os
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


def _force_file_store_requested() -> bool:
    value = str(os.environ.get("TONESOUL_FORCE_FILE_STORE", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _load_payload(args) -> dict:
    if args.input is not None:
        return json.loads(args.input.read_text(encoding="utf-8"))
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read().strip()
        except OSError:
            raw = ""
        if raw:
            return json.loads(raw)
    return {
        "checkpoint_id": args.checkpoint_id,
        "agent": args.agent,
        "session_id": args.session_id,
        "summary": args.summary,
        "pending_paths": list(args.pending_paths or []),
        "next_action": args.next_action,
        "source": args.source,
    }


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Save a ToneSoul checkpoint")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--checkpoint-id", default="")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--path", action="append", dest="pending_paths", default=[])
    parser.add_argument("--next-action", default="")
    parser.add_argument("--source", default="cli")
    parser.add_argument("--ttl-seconds", type=int, default=86400)
    args = parser.parse_args()

    payload = _load_payload(args)
    checkpoint_id = str(payload.get("checkpoint_id", args.checkpoint_id)).strip()
    if not checkpoint_id:
        parser.error("checkpoint_id is required")

    store = None
    if args.state_path is not None or args.traces_path is not None or _force_file_store_requested():
        from tonesoul.backends.file_store import FileStore

        if args.state_path is None and args.traces_path is None:
            store = FileStore()
        elif args.traces_path is not None:
            root = args.traces_path.parent
            zones_path = root / "zone_registry.json"
        elif args.state_path is not None:
            root = args.state_path.parent
            zones_path = root / "zone_registry.json"
        else:
            root = Path(".")
            zones_path = None

        if store is None:
            store = FileStore(
                gov_path=args.state_path,
                traces_path=args.traces_path,
                zones_path=zones_path,
                claims_path=_resolve_sidecar(root, "task_claims.json"),
                perspectives_path=_resolve_sidecar(root, "perspectives.json"),
                checkpoints_path=_resolve_sidecar(root, "checkpoints.json"),
                compactions_path=_resolve_sidecar(root, "compacted.json"),
            )

    from tonesoul.runtime_adapter import write_checkpoint

    result = write_checkpoint(
        checkpoint_id,
        agent_id=str(payload.get("agent", args.agent or "unknown")),
        session_id=str(payload.get("session_id", args.session_id)),
        summary=str(payload.get("summary", args.summary)),
        pending_paths=list(payload.get("pending_paths") or []),
        next_action=str(payload.get("next_action", args.next_action)),
        source=str(payload.get("source", args.source)),
        ttl_seconds=args.ttl_seconds,
        store=store,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
