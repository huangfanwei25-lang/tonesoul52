#!/usr/bin/env python3
"""Write a bounded non-canonical subject snapshot to ToneSoul shared R-memory."""

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
        "agent": args.agent,
        "session_id": args.session_id,
        "summary": args.summary,
        "stable_vows": list(args.stable_vows or []),
        "durable_boundaries": list(args.durable_boundaries or []),
        "decision_preferences": list(args.decision_preferences or []),
        "verified_routines": list(args.verified_routines or []),
        "active_threads": list(args.active_threads or []),
        "evidence_refs": list(args.evidence_refs or []),
        "refresh_signals": list(args.refresh_signals or []),
        "source": args.source,
    }


def main() -> None:
    _ensure_repo_root_on_path()
    parser = argparse.ArgumentParser(description="Save a ToneSoul subject snapshot")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--vow", action="append", dest="stable_vows", default=[])
    parser.add_argument("--boundary", action="append", dest="durable_boundaries", default=[])
    parser.add_argument("--preference", action="append", dest="decision_preferences", default=[])
    parser.add_argument("--routine", action="append", dest="verified_routines", default=[])
    parser.add_argument("--thread", action="append", dest="active_threads", default=[])
    parser.add_argument("--evidence-ref", action="append", dest="evidence_refs", default=[])
    parser.add_argument("--refresh-signal", action="append", dest="refresh_signals", default=[])
    parser.add_argument("--source", default="cli")
    parser.add_argument("--ttl-seconds", type=int, default=2592000)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    payload = _load_payload(args)
    if not str(payload.get("summary", args.summary)).strip():
        parser.error("summary is required")

    store = None
    if args.state_path is not None or args.traces_path is not None:
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

        store = FileStore(
            gov_path=args.state_path,
            traces_path=args.traces_path,
            zones_path=zones_path,
            claims_path=_resolve_sidecar(root, "task_claims.json"),
            perspectives_path=_resolve_sidecar(root, "perspectives.json"),
            checkpoints_path=_resolve_sidecar(root, "checkpoints.json"),
            compactions_path=_resolve_sidecar(root, "compacted.json"),
            subject_snapshots_path=_resolve_sidecar(root, "subject_snapshots.json"),
        )

    from tonesoul.runtime_adapter import write_subject_snapshot

    result = write_subject_snapshot(
        agent_id=str(payload.get("agent", args.agent or "unknown")),
        session_id=str(payload.get("session_id", args.session_id)),
        summary=str(payload.get("summary", args.summary)),
        stable_vows=list(payload.get("stable_vows") or []),
        durable_boundaries=list(payload.get("durable_boundaries") or []),
        decision_preferences=list(payload.get("decision_preferences") or []),
        verified_routines=list(payload.get("verified_routines") or []),
        active_threads=list(payload.get("active_threads") or []),
        evidence_refs=list(payload.get("evidence_refs") or []),
        refresh_signals=list(payload.get("refresh_signals") or []),
        source=str(payload.get("source", args.source)),
        ttl_seconds=args.ttl_seconds,
        limit=args.limit,
        store=store,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
