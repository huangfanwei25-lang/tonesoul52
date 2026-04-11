#!/usr/bin/env python3
"""Run the default ToneSoul session-end bundle in one command."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
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


def _build_store(args):
    if args.state_path is None and args.traces_path is None and not _force_file_store_requested():
        return None

    from tonesoul.backends.file_store import FileStore

    if args.state_path is None and args.traces_path is None:
        return FileStore()

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
        "mode": args.mode,
        "checkpoint_id": args.checkpoint_id,
        "agent": args.agent,
        "session_id": args.session_id,
        "summary": args.summary,
        "pending_paths": list(args.pending_paths or []),
        "next_action": args.next_action,
        "carry_forward": list(args.carry_forward or []),
        "evidence_refs": list(args.evidence_refs or []),
        "release_task_ids": list(args.release_task_ids or []),
        "source": args.source,
    }


def _release_claims(*, task_ids: list[str], agent_id: str, store=None) -> dict:
    from tonesoul.runtime_adapter import list_active_claims, release_task_claim

    current_claims = list_active_claims(store=store)
    owned_claims = [claim for claim in current_claims if claim.get("agent") == agent_id]

    requested = list(task_ids)
    strategy = "explicit"
    if not requested:
        requested = [
            str(claim.get("task_id", "")).strip()
            for claim in owned_claims
            if str(claim.get("task_id", "")).strip()
        ]
        strategy = "all_for_agent"

    released_task_ids: list[str] = []
    not_released_task_ids: list[str] = []
    for task_id in requested:
        result = release_task_claim(task_id, agent_id=agent_id, store=store)
        if result.get("ok"):
            released_task_ids.append(task_id)
        else:
            not_released_task_ids.append(task_id)

    remaining_claims = list_active_claims(store=store)
    return {
        "strategy": strategy,
        "released_task_ids": released_task_ids,
        "not_released_task_ids": not_released_task_ids,
        "remaining_claims": remaining_claims,
    }


def _apply_subject_refresh_bundle(
    *,
    enabled: bool,
    agent_id: str,
    summary: str,
    session_id: str,
    source: str,
    store=None,
) -> dict | None:
    if not enabled:
        return None
    from tonesoul.runtime_adapter import apply_subject_refresh

    return apply_subject_refresh(
        agent_id=agent_id,
        field="active_threads",
        summary=summary,
        session_id=session_id,
        source=f"{source}-subject-refresh",
        refresh_signals=["session-end active_threads refresh requested"],
        store=store,
    )


def main() -> None:
    _ensure_repo_root_on_path()

    parser = argparse.ArgumentParser(description="Run the ToneSoul session-end bundle")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--agent", required=True)
    parser.add_argument(
        "--mode", choices=("checkpoint", "compaction", "both"), default="compaction"
    )
    parser.add_argument("--checkpoint-id", default="")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--path", action="append", dest="pending_paths", default=[])
    parser.add_argument("--next-action", default="")
    parser.add_argument("--carry-forward", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", dest="evidence_refs", default=[])
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
    parser.add_argument("--release-task", action="append", dest="release_task_ids", default=[])
    parser.add_argument("--no-release", action="store_true")
    parser.add_argument("--refresh-active-threads", action="store_true")
    parser.add_argument("--source", default="cli")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--checkpoint-ttl-seconds", type=int, default=86400)
    parser.add_argument("--compaction-ttl-seconds", type=int, default=604800)
    parser.add_argument("--compaction-limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    payload = _load_payload(args)
    agent_id = str(payload.get("agent", args.agent or "")).strip()
    if not agent_id:
        parser.error("--agent is required")

    mode = str(payload.get("mode", args.mode or "compaction")).strip() or "compaction"
    if mode not in {"checkpoint", "compaction", "both"}:
        parser.error("--mode must be one of checkpoint, compaction, both")

    summary = str(payload.get("summary", args.summary or "")).strip()
    if not summary:
        parser.error("summary is required")

    session_id = str(payload.get("session_id", args.session_id or "")).strip()
    pending_paths = list(payload.get("pending_paths") or [])
    next_action = str(payload.get("next_action", args.next_action or "")).strip()
    carry_forward = list(payload.get("carry_forward") or [])
    evidence_refs = list(payload.get("evidence_refs") or [])
    council_dossier = (
        dict(payload.get("council_dossier"))
        if isinstance(payload.get("council_dossier"), dict)
        else None
    )
    release_task_ids = [
        str(value).strip()
        for value in (payload.get("release_task_ids") or [])
        if str(value).strip()
    ]
    source = str(payload.get("source", args.source or "cli"))
    unresolved_items = [
        str(value).strip()
        for value in (payload.get("unresolved_items") or args.unresolved_items or [])
        if str(value).strip()
    ]

    from tonesoul.runtime_adapter import (
        normalize_closeout_payload,
        write_checkpoint,
        write_compaction,
    )

    closeout = normalize_closeout_payload(
        status=str(payload.get("closeout_status", args.closeout_status or "")).strip(),
        stop_reason=str(payload.get("stop_reason", args.stop_reason or "")).strip(),
        unresolved_items=unresolved_items,
        human_input_required=bool(payload.get("human_input_required", args.human_input_required)),
        note=str(payload.get("closeout_note", args.closeout_note or "")).strip(),
        pending_paths=pending_paths,
        next_action=next_action,
        closeout=(
            dict(payload.get("closeout")) if isinstance(payload.get("closeout"), dict) else None
        ),
    )

    store = _build_store(args)
    checkpoint = None
    compaction = None
    subject_refresh_application = None

    if mode in {"checkpoint", "both"}:
        checkpoint_id = str(payload.get("checkpoint_id", args.checkpoint_id or "")).strip() or str(
            uuid.uuid4()
        )
        checkpoint = write_checkpoint(
            checkpoint_id,
            agent_id=agent_id,
            session_id=session_id,
            summary=summary,
            pending_paths=pending_paths,
            next_action=next_action,
            source=source,
            ttl_seconds=args.checkpoint_ttl_seconds,
            store=store,
        )

    if mode in {"compaction", "both"}:
        compaction = write_compaction(
            agent_id=agent_id,
            session_id=session_id,
            summary=summary,
            carry_forward=carry_forward,
            pending_paths=pending_paths,
            evidence_refs=evidence_refs,
            council_dossier=council_dossier,
            closeout=closeout,
            next_action=next_action,
            source=source,
            ttl_seconds=args.compaction_ttl_seconds,
            limit=args.compaction_limit,
            store=store,
        )
        subject_refresh_application = _apply_subject_refresh_bundle(
            enabled=bool(args.refresh_active_threads),
            agent_id=agent_id,
            summary=summary,
            session_id=session_id,
            source=source,
            store=store,
        )

        # Governance Retro — entropy discharge valve
        try:
            from tonesoul.governance.retro import should_run_retro, run_retro, persist_retro_result
            from tonesoul.runtime_adapter import load as load_posture

            posture = load_posture()
            si = float(getattr(posture, "soul_integral", 0.0) or 0.0)
            sessions = int(getattr(posture, "session_count", 0) or 0)
            should, retro_reason = should_run_retro(
                soul_integral=si, sessions_since_last_retro=sessions % 10
            )
            if should:
                retro_result = run_retro(posture=posture)
                persist_retro_result(retro_result)
                payload_out_retro = retro_result.to_dict()
                payload_out_retro["trigger_reason"] = retro_reason
        except Exception:
            pass  # Retro is best-effort, never blocks session end

    release_summary = {
        "strategy": "none",
        "released_task_ids": [],
        "not_released_task_ids": [],
        "remaining_claims": [],
    }
    if not args.no_release:
        release_summary = _release_claims(task_ids=release_task_ids, agent_id=agent_id, store=store)

    shared_args = [f'--summary "{summary}"']
    for path in pending_paths:
        shared_args.append(f'--path "{path}"')
    if next_action:
        shared_args.append(f'--next-action "{next_action}"')
    closeout_args = [f"--closeout-status {closeout['status']}"]
    if closeout.get("stop_reason"):
        closeout_args.append(f"--stop-reason {closeout['stop_reason']}")
    for item in list(closeout.get("unresolved_items") or []):
        closeout_args.append(f'--unresolved-item "{item}"')
    if closeout.get("human_input_required"):
        closeout_args.append("--human-input-required")
    if str(closeout.get("note", "")).strip():
        closeout_args.append(f'--closeout-note "{closeout["note"]}"')
    shared_args_text = " ".join(shared_args)
    closeout_args_text = " ".join(closeout_args)

    # Collect retro result if it ran
    retro_output = None
    try:
        retro_output = payload_out_retro  # noqa: F821 — set in retro block above
    except NameError:
        pass

    payload_out = {
        "contract_version": "v1",
        "bundle": "session_end",
        "agent": agent_id,
        "mode": mode,
        "closeout": closeout,
        "checkpoint": checkpoint,
        "compaction": compaction,
        "subject_refresh_application": subject_refresh_application,
        "governance_retro": retro_output,
        "released_claims": release_summary,
        "underlying_commands": [],
    }
    if checkpoint is not None:
        payload_out["underlying_commands"].append(
            "python scripts/save_checkpoint.py "
            f"--checkpoint-id {checkpoint['checkpoint_id']} --agent {agent_id} {shared_args_text}"
        )
    if compaction is not None:
        payload_out["underlying_commands"].append(
            f"python scripts/save_compaction.py --agent {agent_id} {shared_args_text} {closeout_args_text}".strip()
        )
    if subject_refresh_application is not None:
        payload_out["underlying_commands"].append(
            f'python scripts/apply_subject_refresh.py --agent {agent_id} --field active_threads --summary "{summary}"'
        )
    if not args.no_release:
        payload_out["underlying_commands"].append(
            f"python scripts/run_task_claim.py release <task_id> --agent {agent_id}"
        )

    text = json.dumps(payload_out, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
