#!/usr/bin/env python3
"""Write a bounded non-canonical perspective to ToneSoul shared R-memory."""

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


def _parse_drift_pairs(values: list[str]) -> dict:
    result = {}
    for raw in values:
        key, separator, number = str(raw).partition("=")
        key = key.strip()
        number = number.strip()
        if not separator or not key:
            raise ValueError(f"invalid drift pair: {raw}")
        result[key] = float(number)
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
        "session_id": args.session_id,
        "summary": args.summary,
        "stance": args.stance,
        "tensions": list(args.tensions or []),
        "proposed_drift": _parse_drift_pairs(args.proposed_drift or []),
        "proposed_vows": list(args.proposed_vows or []),
        "evidence_refs": list(args.evidence_refs or []),
        "source": args.source,
    }


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Save a ToneSoul perspective")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--stance", default="")
    parser.add_argument("--tension", action="append", dest="tensions", default=[])
    parser.add_argument("--drift", action="append", dest="proposed_drift", default=[])
    parser.add_argument("--vow", action="append", dest="proposed_vows", default=[])
    parser.add_argument("--evidence-ref", action="append", dest="evidence_refs", default=[])
    parser.add_argument("--source", default="cli")
    parser.add_argument("--ttl-seconds", type=int, default=7200)
    args = parser.parse_args()

    try:
        payload = _load_payload(args)
    except ValueError as exc:
        parser.error(str(exc))

    agent_id = str(payload.get("agent", args.agent or "unknown")).strip()
    if not agent_id:
        parser.error("agent is required")

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
        )

    from tonesoul.runtime_adapter import write_perspective

    result = write_perspective(
        agent_id,
        session_id=str(payload.get("session_id", args.session_id)),
        summary=str(payload.get("summary", args.summary)),
        stance=str(payload.get("stance", args.stance)),
        tensions=list(payload.get("tensions") or []),
        proposed_drift=dict(payload.get("proposed_drift") or {}),
        proposed_vows=list(payload.get("proposed_vows") or []),
        evidence_refs=list(payload.get("evidence_refs") or []),
        source=str(payload.get("source", args.source)),
        ttl_seconds=args.ttl_seconds,
        store=store,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
