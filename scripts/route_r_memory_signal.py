#!/usr/bin/env python3
"""Route a bounded runtime signal into the most plausible shared R-memory surface."""

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


def _parse_proposed_drift(values: list[str]) -> dict[str, float]:
    result: dict[str, float] = {}
    for value in values:
        text = str(value or "").strip()
        if not text or "=" not in text:
            raise ValueError(f"Invalid --proposed-drift entry: {value}")
        key, raw_score = text.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --proposed-drift entry: {value}")
        result[key] = float(raw_score.strip())
    return result


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
        "summary": args.summary,
        "task_id": args.task_id,
        "session_id": args.session_id,
        "paths": list(args.paths or []),
        "pending_paths": list(args.pending_paths or []),
        "next_action": args.next_action,
        "stance": args.stance,
        "tensions": list(args.tensions or []),
        "proposed_drift": _parse_proposed_drift(list(args.proposed_drift or [])),
        "proposed_vows": list(args.proposed_vows or []),
        "carry_forward": list(args.carry_forward or []),
        "evidence_refs": list(args.evidence_refs or []),
        "stable_vows": list(args.stable_vows or []),
        "durable_boundaries": list(args.durable_boundaries or []),
        "decision_preferences": list(args.decision_preferences or []),
        "verified_routines": list(args.verified_routines or []),
        "active_threads": list(args.active_threads or []),
        "refresh_signals": list(args.refresh_signals or []),
        "source": args.source,
        "prefer_surface": args.surface,
    }


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Route a ToneSoul runtime signal")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--surface", default="")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--summary", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--path", action="append", dest="paths", default=[])
    parser.add_argument("--pending-path", action="append", dest="pending_paths", default=[])
    parser.add_argument("--next-action", default="")
    parser.add_argument("--stance", default="")
    parser.add_argument("--tension", action="append", dest="tensions", default=[])
    parser.add_argument("--proposed-drift", action="append", default=[])
    parser.add_argument("--proposed-vow", action="append", dest="proposed_vows", default=[])
    parser.add_argument("--carry-forward", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", dest="evidence_refs", default=[])
    parser.add_argument("--stable-vow", action="append", dest="stable_vows", default=[])
    parser.add_argument("--boundary", action="append", dest="durable_boundaries", default=[])
    parser.add_argument("--preference", action="append", dest="decision_preferences", default=[])
    parser.add_argument("--routine", action="append", dest="verified_routines", default=[])
    parser.add_argument("--active-thread", action="append", dest="active_threads", default=[])
    parser.add_argument("--refresh-signal", action="append", dest="refresh_signals", default=[])
    parser.add_argument("--source", default="cli")
    parser.add_argument("--ttl-seconds", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    payload = _load_payload(args)

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

    from tonesoul.runtime_adapter import (
        record_routing_event,
        route_r_memory_signal,
        write_routed_signal,
    )

    route = route_r_memory_signal(
        agent_id=str(payload.get("agent", args.agent or "unknown")),
        summary=str(payload.get("summary", args.summary)),
        task_id=str(payload.get("task_id", args.task_id)),
        session_id=str(payload.get("session_id", args.session_id)),
        paths=list(payload.get("paths") or []),
        pending_paths=list(payload.get("pending_paths") or []),
        next_action=str(payload.get("next_action", args.next_action)),
        stance=str(payload.get("stance", args.stance)),
        tensions=list(payload.get("tensions") or []),
        proposed_drift=dict(payload.get("proposed_drift") or {}),
        proposed_vows=list(payload.get("proposed_vows") or []),
        carry_forward=list(payload.get("carry_forward") or []),
        evidence_refs=list(payload.get("evidence_refs") or []),
        stable_vows=list(payload.get("stable_vows") or []),
        durable_boundaries=list(payload.get("durable_boundaries") or []),
        decision_preferences=list(payload.get("decision_preferences") or []),
        verified_routines=list(payload.get("verified_routines") or []),
        active_threads=list(payload.get("active_threads") or []),
        refresh_signals=list(payload.get("refresh_signals") or []),
        source=str(payload.get("source", args.source)),
        prefer_surface=str(payload.get("prefer_surface", args.surface)),
    )

    output = {"route": route}
    if args.write:
        output["written"] = write_routed_signal(
            route,
            store=store,
            ttl_seconds=args.ttl_seconds,
            limit=args.limit,
        )
    output["routing_event"] = record_routing_event(
        route,
        action="write" if args.write else "preview",
        written=bool(args.write),
        store=store,
        ttl_seconds=int(args.ttl_seconds) if args.ttl_seconds is not None else 1209600,
        limit=int(args.limit) if args.limit is not None else 50,
    )

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
