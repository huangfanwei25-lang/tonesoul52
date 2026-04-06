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


def build_tier2_deep_governance_drawer(bundle: dict[str, Any]) -> dict[str, Any]:
    readiness = bundle.get("readiness") or {}
    import_posture = bundle.get("import_posture") or {}
    surfaces = import_posture.get("surfaces") or {}
    mutation_preflight = bundle.get("mutation_preflight") or {}
    publish_push_preflight = bundle.get("publish_push_preflight") or {}
    task_board_preflight = bundle.get("task_board_preflight") or {}
    closeout_attention = bundle.get("closeout_attention") or {}
    observer_shell = bundle.get("observer_shell") or {}

    trigger_reasons: list[str] = []
    if str(readiness.get("status", "")).strip() != "pass":
        trigger_reasons.append("readiness_not_pass")
    if int(readiness.get("claim_conflict_count", 0) or 0) > 0:
        trigger_reasons.append("claim_conflict_visible")
    if bool(closeout_attention.get("present")):
        trigger_reasons.append("closeout_attention_present")
    if str(publish_push_preflight.get("classification", "")).strip() not in {"", "clear"}:
        trigger_reasons.append("publish_push_requires_review")
    if str(task_board_preflight.get("classification", "")).strip() not in {"", "parking_clear"}:
        trigger_reasons.append("task_board_requires_parking_review")

    mutation_cards: list[dict[str, str]] = []
    for point in list(mutation_preflight.get("decision_points") or []):
        name = str(point.get("name", "")).strip()
        if name not in {"shared_code_edit", "compaction_write"}:
            continue
        mutation_cards.append(
            {
                "title": name.replace("_", " "),
                "status": str(point.get("posture", "")).strip(),
                "summary": str(point.get("receiver_note", "")).strip(),
                "guard": str(point.get("current_guard", "")).strip(),
            }
        )

    group_a_cards: list[dict[str, str]] = []
    if bool(closeout_attention.get("present")):
        group_a_cards.append(
            {
                "title": "closeout attention",
                "status": str(closeout_attention.get("status", "")).strip() or "contested",
                "summary": str(closeout_attention.get("summary_text", "")).strip(),
                "guard": str(closeout_attention.get("receiver_rule", "")).strip(),
            }
        )
    group_a_cards.extend(mutation_cards[:2])

    if publish_push_preflight:
        group_a_cards.append(
            {
                "title": "publish / push posture",
                "status": str(publish_push_preflight.get("classification", "")).strip(),
                "summary": str(publish_push_preflight.get("summary_text", "")).strip(),
                "guard": str(publish_push_preflight.get("receiver_note", "")).strip(),
            }
        )
    if task_board_preflight:
        group_a_cards.append(
            {
                "title": "task-board parking",
                "status": str(task_board_preflight.get("classification", "")).strip(),
                "summary": str(task_board_preflight.get("summary_text", "")).strip(),
                "guard": str(task_board_preflight.get("receiver_note", "")).strip(),
            }
        )

    compaction_surface = surfaces.get("compactions") or {}
    council_surface = surfaces.get("council_dossier") or {}
    subject_surface = surfaces.get("subject_snapshot") or {}
    style_surface = surfaces.get("working_style") or {}
    contested_headlines = list(observer_shell.get("contested_headlines") or [])

    group_b_cards: list[dict[str, str]] = []
    if compaction_surface:
        group_b_cards.append(
            {
                "title": "compaction carry-forward",
                "status": str(compaction_surface.get("receiver_obligation", "")).strip() or "advisory",
                "summary": (
                    f"closeout={str(compaction_surface.get('closeout_status', '')).strip() or 'complete'}"
                ),
                "guard": str(compaction_surface.get("note", "")).strip(),
            }
        )
    if contested_headlines:
        group_b_cards.append(
            {
                "title": "observer contested continuity",
                "status": "contested",
                "summary": contested_headlines[0],
                "guard": str(observer_shell.get("receiver_note", "")).strip(),
            }
        )
    if council_surface:
        interpretation = council_surface.get("dossier_interpretation") or {}
        group_b_cards.append(
            {
                "title": "council realism caution",
                "status": "descriptive_only",
                "summary": (
                    str(interpretation.get("calibration_status", "")).strip()
                    or "Treat council agreement as review context, not accuracy proof."
                ),
                "guard": str(council_surface.get("note", "")).strip(),
            }
        )
    if subject_surface or style_surface:
        group_b_cards.append(
            {
                "title": "working identity / style",
                "status": "advisory",
                "summary": "Subject snapshot and working style help orientation, but they must not promote into canonical identity.",
                "guard": "Keep working identity and style advisory-only; do not promote them into vows, durable identity, or governance truth.",
            }
        )

    groups: list[dict[str, Any]] = []
    if group_a_cards:
        groups.append(
            {
                "name": "Mutation And Closeout",
                "priority": 1,
                "cards": group_a_cards[:5],
            }
        )
    if group_b_cards:
        groups.append(
            {
                "name": "Contested Continuity",
                "priority": 2,
                "cards": group_b_cards[:5],
            }
        )

    next_pull_commands = []
    next_followup = mutation_preflight.get("next_followup") or {}
    if str(next_followup.get("command", "")).strip():
        next_pull_commands.append(str(next_followup.get("command", "")).strip())
    if str(publish_push_preflight.get("recommended_command", "")).strip():
        next_pull_commands.append(str(publish_push_preflight.get("recommended_command", "")).strip())
    if str(task_board_preflight.get("recommended_command", "")).strip():
        next_pull_commands.append(str(task_board_preflight.get("recommended_command", "")).strip())

    return {
        "present": bool(bundle.get("present", True)),
        "tier": int(bundle.get("tier", 2) or 2),
        "recommended_open": bool(trigger_reasons),
        "trigger_reasons": trigger_reasons,
        "active_group_names": [group["name"] for group in groups[:2]],
        "groups": groups[:2],
        "next_pull_commands": next_pull_commands[:3],
        "summary_text": (
            "tier2_drawer="
            + ("recommended" if trigger_reasons else "manual_only")
            + f" groups={len(groups[:2])} triggers={len(trigger_reasons)}"
        ),
        "receiver_rule": (
            "Use Tier 2 only when mutation, closeout, or contested continuity requires deeper review. Keep packet/detail payloads behind deeper pull."
        ),
    }
