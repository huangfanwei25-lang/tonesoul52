#!/usr/bin/env python3
"""Apply a bounded ToneSoul subject-refresh heuristic to shared R-memory."""

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
        subject_snapshots_path=_resolve_sidecar(root, "subject_snapshots.json"),
    )


def main() -> None:
    _ensure_repo_root_on_path()
    parser = argparse.ArgumentParser(
        description="Apply a bounded ToneSoul subject-refresh heuristic"
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--field", choices=("active_threads",), default="active_threads")
    parser.add_argument("--summary", default="")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--refresh-signal", action="append", dest="refresh_signals", default=[])
    parser.add_argument("--source", default="cli")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    args = parser.parse_args()

    store = _build_store(args)

    from tonesoul.runtime_adapter import apply_subject_refresh

    result = apply_subject_refresh(
        agent_id=args.agent,
        field=args.field,
        summary=args.summary,
        session_id=args.session_id,
        source=args.source,
        refresh_signals=list(args.refresh_signals or []),
        store=store,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
