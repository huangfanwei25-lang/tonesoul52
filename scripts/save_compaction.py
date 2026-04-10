#!/usr/bin/env python3
"""Write a bounded non-canonical compaction summary to ToneSoul R-memory."""

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
            "agent": args.agent,
            "session_id": args.session_id,
            "summary": args.summary,
            "carry_forward": list(args.carry_forward or []),
            "pending_paths": list(args.pending_paths or []),
            "evidence_refs": list(args.evidence_refs or []),
            "next_action": args.next_action,
            "closeout_status": args.closeout_status,
            "stop_reason": args.stop_reason,
            "unresolved_items": list(args.unresolved_items or []),
            "human_input_required": bool(args.human_input_required),
            "closeout_note": args.closeout_note,
            "source": args.source,
        }
    return {
        "agent": args.agent,
        "session_id": args.session_id,
        "summary": args.summary,
        "carry_forward": list(args.carry_forward or []),
        "pending_paths": list(args.pending_paths or []),
        "evidence_refs": list(args.evidence_refs or []),
        "next_action": args.next_action,
        "closeout_status": args.closeout_status,
        "stop_reason": args.stop_reason,
        "unresolved_items": list(args.unresolved_items or []),
        "human_input_required": bool(args.human_input_required),
        "closeout_note": args.closeout_note,
        "source": args.source,
    }


def main() -> None:
    _ensure_repo_root_on_path()
    parser = argparse.ArgumentParser(description="Save a ToneSoul compaction summary")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--carry-forward", action="append", default=[])
    parser.add_argument("--path", action="append", dest="pending_paths", default=[])
    parser.add_argument("--evidence-ref", action="append", dest="evidence_refs", default=[])
    parser.add_argument("--next-action", default="")
    parser.add_argument(
        "--closeout-status",
        choices=("complete", "partial", "blocked", "underdetermined"),
        default="",
    )
    parser.add_argument(
        "--stop-reason",
        choices=("external_blocked", "internal_unstable", "divergence_risk", "underdetermined"),
        default="",
    )
    parser.add_argument("--unresolved-item", action="append", dest="unresolved_items", default=[])
    parser.add_argument("--human-input-required", action="store_true")
    parser.add_argument("--closeout-note", default="")
    parser.add_argument("--source", default="cli")
    parser.add_argument("--ttl-seconds", type=int, default=604800)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    payload = _load_payload(args)

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

    from tonesoul.runtime_adapter import normalize_closeout_payload, write_compaction

    closeout = normalize_closeout_payload(
        status=str(payload.get("closeout_status", args.closeout_status or "")).strip(),
        stop_reason=str(payload.get("stop_reason", args.stop_reason or "")).strip(),
        unresolved_items=list(payload.get("unresolved_items") or []),
        human_input_required=bool(payload.get("human_input_required", args.human_input_required)),
        note=str(payload.get("closeout_note", args.closeout_note or "")).strip(),
        pending_paths=list(payload.get("pending_paths") or []),
        next_action=str(payload.get("next_action", args.next_action)),
        closeout=(
            dict(payload.get("closeout")) if isinstance(payload.get("closeout"), dict) else None
        ),
    )

    result = write_compaction(
        agent_id=str(payload.get("agent", args.agent or "unknown")),
        session_id=str(payload.get("session_id", args.session_id)),
        summary=str(payload.get("summary", args.summary)),
        carry_forward=list(payload.get("carry_forward") or []),
        pending_paths=list(payload.get("pending_paths") or []),
        evidence_refs=list(payload.get("evidence_refs") or []),
        council_dossier=(
            dict(payload.get("council_dossier"))
            if isinstance(payload.get("council_dossier"), dict)
            else None
        ),
        closeout=closeout,
        next_action=str(payload.get("next_action", args.next_action)),
        source=str(payload.get("source", args.source)),
        ttl_seconds=args.ttl_seconds,
        limit=args.limit,
        store=store,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
