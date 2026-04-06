"""
Session-start helpers for the dashboard workspace.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def run_session_start_bundle(
    *,
    agent_id: str,
    tier: int,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or get_repo_root()
    script_path = root / "scripts" / "start_agent_session.py"
    command = [
        sys.executable,
        str(script_path),
        "--agent",
        agent_id,
        "--tier",
        str(tier),
        "--no-ack",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {
            "present": False,
            "error": f"failed to run session-start: {exc}",
            "tier": tier,
        }

    if result.returncode != 0:
        return {
            "present": False,
            "error": (result.stderr or result.stdout or "session-start failed").strip(),
            "tier": tier,
        }

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "present": False,
            "error": f"invalid session-start json: {exc}",
            "tier": tier,
        }

    if isinstance(payload, dict):
        payload.setdefault("present", True)
    return payload


def build_tier0_start_strip(bundle: dict[str, Any]) -> dict[str, Any]:
    readiness = bundle.get("readiness") or {}
    task_track = bundle.get("task_track_hint") or {}
    deliberation = bundle.get("deliberation_mode_hint") or {}
    canonical_center = bundle.get("canonical_center") or {}
    hook_chain = bundle.get("hook_chain") or {}
    mutation_preflight = bundle.get("mutation_preflight") or {}
    next_followup = mutation_preflight.get("next_followup") or {}

    return {
        "present": bool(bundle.get("present", True)),
        "tier": int(bundle.get("tier", 0) or 0),
        "readiness_status": str(readiness.get("status", "")).strip(),
        "task_track": str(task_track.get("suggested_track", "")).strip(),
        "deliberation_mode": str(deliberation.get("suggested_mode", "")).strip(),
        "canonical_summary": str(canonical_center.get("summary_text", "")).strip(),
        "hook_badges": [
            {
                "name": str(item.get("name", "")).strip(),
                "status": str(item.get("status", "")).strip(),
            }
            for item in list(hook_chain.get("hooks") or [])
            if str(item.get("name", "")).strip()
        ],
        "next_followup": {
            "target": str(next_followup.get("target", "")).strip(),
            "classification": str(next_followup.get("classification", "")).strip(),
            "command": str(next_followup.get("command", "")).strip(),
            "reason": str(next_followup.get("reason", "")).strip(),
        },
        "receiver_rule": str(mutation_preflight.get("receiver_rule", "")).strip(),
    }


def build_tier1_orientation_shell(bundle: dict[str, Any]) -> dict[str, Any]:
    canonical_center = bundle.get("canonical_center") or {}
    current_short_board = canonical_center.get("current_short_board") or {}
    successor_correction = canonical_center.get("successor_correction") or {}
    subsystem_parity = bundle.get("subsystem_parity") or {}
    observer_shell = bundle.get("observer_shell") or {}
    closeout_attention = bundle.get("closeout_attention") or {}

    family_cards = []
    for family in list(subsystem_parity.get("families") or [])[:4]:
        family_cards.append(
            {
                "name": str(family.get("name", "")).strip(),
                "status": str(family.get("status", "")).strip(),
                "main_gap": str(family.get("main_gap", "")).strip(),
                "next_move": str(family.get("next_bounded_move", "")).strip(),
            }
        )

    return {
        "present": bool(bundle.get("present", True)),
        "tier": int(bundle.get("tier", 1) or 1),
        "canonical_cards": {
            "short_board": str(current_short_board.get("summary_text", "")).strip(),
            "successor_correction": str(successor_correction.get("summary_text", "")).strip(),
            "source_precedence": str(canonical_center.get("source_precedence_summary", "")).strip(),
        },
        "parity_counts": dict(subsystem_parity.get("counts") or {}),
        "family_cards": family_cards,
        "closeout_attention": {
            "present": bool(closeout_attention.get("present")),
            "status": str(closeout_attention.get("status", "")).strip(),
            "summary_text": str(closeout_attention.get("summary_text", "")).strip(),
            "receiver_rule": str(closeout_attention.get("receiver_rule", "")).strip(),
        },
        "observer_shell": {
            "summary_text": str(observer_shell.get("summary_text", "")).strip(),
            "receiver_note": str(observer_shell.get("receiver_note", "")).strip(),
            "counts": dict(observer_shell.get("counts") or {}),
            "stable_headlines": list(observer_shell.get("stable_headlines") or []),
            "contested_headlines": list(observer_shell.get("contested_headlines") or []),
            "stale_headlines": list(observer_shell.get("stale_headlines") or []),
        },
    }
