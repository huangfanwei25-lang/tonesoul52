#!/usr/bin/env python3
"""Run the default ToneSoul session-start bundle in one command."""

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
        observer_cursors_path=_resolve_sidecar(root, "observer_cursors.json"),
    )


def _build_compact_line(*, agent_id: str, backend_name: str, packet: dict, posture) -> str:
    risk_posture = ((packet.get("posture") or {}).get("risk_posture") or {})
    repo_progress = ((packet.get("project_memory_summary") or {}).get("repo_progress") or {})
    return (
        f"[ToneSoul] {backend_name} | SI={float(getattr(posture, 'soul_integral', 0.0)):.2f} | "
        f"vows={len(getattr(posture, 'active_vows', []) or [])} "
        f"tensions={len(getattr(posture, 'tension_history', []) or [])} | "
        f"R={float(risk_posture.get('score', 0.0)):.2f}/{risk_posture.get('level', 'unknown')} | "
        f"claims={len(packet.get('active_claims', []))} "
        f"checkpoints={len(packet.get('recent_checkpoints', []))} "
        f"compactions={len(packet.get('recent_compactions', []))} "
        f"subjects={len(packet.get('recent_subject_snapshots', []))} | "
        f"git={repo_progress.get('head', 'unknown')}/dirty={int(repo_progress.get('dirty_count', 0) or 0)} | "
        f"agent={agent_id}"
    )


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Run the ToneSoul session-start bundle")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--trace-limit", type=int, default=5)
    parser.add_argument("--visitor-limit", type=int, default=5)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-ack", action="store_true")
    args = parser.parse_args()

    agent_id = str(args.agent or "").strip()
    if not agent_id:
        parser.error("--agent is required")

    from tonesoul.runtime_adapter import (
        acknowledge_observer_cursor,
        list_active_claims,
        load,
        r_memory_packet,
    )
    from tonesoul.store import get_store

    store = _build_store(args)
    if store is None:
        posture = load(agent_id=agent_id, source="start_agent_session")
        backend_name = getattr(get_store(), "backend_name", "unknown")
    else:
        posture = load(
            state_path=args.state_path,
            agent_id=agent_id,
            source="start_agent_session",
        )
        backend_name = getattr(store, "backend_name", "file")

    packet = r_memory_packet(
        posture=posture,
        store=store,
        observer_id=agent_id,
        trace_limit=args.trace_limit,
        visitor_limit=args.visitor_limit,
    )
    if not args.no_ack:
        acknowledge_observer_cursor(agent_id, packet=packet, store=store)

    claims = list_active_claims(store=store)
    payload = {
        "contract_version": "v1",
        "bundle": "session_start",
        "agent": agent_id,
        "acknowledged_observer_cursor": not args.no_ack,
        "backend_mode": backend_name,
        "compact_diagnostic": _build_compact_line(
            agent_id=agent_id,
            backend_name=backend_name,
            packet=packet,
            posture=posture,
        ),
        "claim_view": {
            "count": len(claims),
            "claims": claims,
        },
        "underlying_commands": [
            f"python -m tonesoul.diagnose --agent {agent_id}",
            f"python scripts/run_r_memory_packet.py --agent {agent_id}{'' if args.no_ack else ' --ack'}",
            "python scripts/run_task_claim.py list",
        ],
        "packet": packet,
    }

    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
