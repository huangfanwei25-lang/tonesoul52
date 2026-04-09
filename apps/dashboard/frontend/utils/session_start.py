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
    next_focus = subsystem_parity.get("next_focus") or {}
    observer_shell = bundle.get("observer_shell") or {}
    closeout_attention = bundle.get("closeout_attention") or {}
    hot_memory_ladder = observer_shell.get("hot_memory_ladder") or {}
    current_pull_boundary = hot_memory_ladder.get("current_pull_boundary") or {}

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
        "next_focus": {
            "resolved_to": str(next_focus.get("resolved_to", "")).strip(),
            "source_family": str(next_focus.get("source_family", "")).strip(),
            "operator_action": str(next_focus.get("operator_action", "")).strip(),
            "focus_pressures": list(next_focus.get("focus_pressures") or []),
        },
        "family_cards": family_cards,
        "closeout_attention": {
            "present": bool(closeout_attention.get("present")),
            "status": str(closeout_attention.get("status", "")).strip(),
            "source_family": str(closeout_attention.get("source_family", "")).strip(),
            "operator_action": str(closeout_attention.get("operator_action", "")).strip(),
            "attention_pressures": list(closeout_attention.get("attention_pressures") or []),
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
        "hot_memory_boundary": {
            "pull_posture": str(current_pull_boundary.get("pull_posture", "")).strip(),
            "preferred_stop_at": str(current_pull_boundary.get("preferred_stop_at", "")).strip(),
            "operator_action": str(current_pull_boundary.get("operator_action", "")).strip(),
            "why_now": str(current_pull_boundary.get("why_now", "")).strip(),
            "receiver_rule": str(current_pull_boundary.get("receiver_rule", "")).strip(),
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


def build_operator_walkthrough_pack(
    *,
    tier0_shell: dict[str, Any] | None,
    tier1_shell: dict[str, Any] | None,
    tier2_drawer: dict[str, Any] | None,
) -> dict[str, Any]:
    tier0_shell = tier0_shell or {}
    tier1_shell = tier1_shell or {}
    tier2_drawer = tier2_drawer or {}

    next_followup = tier0_shell.get("next_followup") or {}
    tier1_cards = tier1_shell.get("canonical_cards") or {}
    closeout_attention = tier1_shell.get("closeout_attention") or {}
    parity_counts = tier1_shell.get("parity_counts") or {}

    walkthrough = [
        {
            "name": "Quick bounded change",
            "default_tier": "Tier 0",
            "use_when": (
                "Readiness is pass, the task is still narrow, and one bounded follow-up is already visible."
            ),
            "stop_here_rule": (
                "Stay in Tier 0 when the next move is clear and you do not need short-board archaeology or contested continuity review."
            ),
            "next_move": str(next_followup.get("command", "")).strip() or "No bounded follow-up command is currently visible.",
            "escalate_when": (
                "Pull Tier 1 if the short board is unclear, if the next step touches broader subsystem context, or if the bounded move no longer fits the task."
            ),
        },
        {
            "name": "Feature continuation",
            "default_tier": "Tier 1",
            "use_when": (
                "The task needs short-board recovery, subsystem parity, or closeout interpretation before acting."
            ),
            "stop_here_rule": (
                "Stay in Tier 1 when the short board, parity gaps, and observer shell are enough to orient bounded work."
            ),
            "next_move": str(tier1_cards.get("short_board", "")).strip() or "Current short board not visible.",
            "escalate_when": (
                "Open Tier 2 only if closeout attention is present, subsystem gaps imply risky mutation, or the observer shell shows contested continuity that affects action."
            ),
        },
        {
            "name": "Contested or risky work",
            "default_tier": "Tier 2",
            "use_when": (
                "Mutation, closeout, publish/push, or contested continuity now materially changes what may be done next."
            ),
            "stop_here_rule": (
                "Do not auto-open Tier 2 for every task; use it only when explicit triggers are active."
            ),
            "next_move": (
                ", ".join(tier2_drawer.get("next_pull_commands") or [])
                or "No deep-pull command is currently required."
            ),
            "escalate_when": (
                "Tier 2 is already the escalation lane. If no trigger is active, close it again and return to Tier 0 or Tier 1."
            ),
        },
    ]

    return {
        "present": True,
        "summary_text": (
            "walkthrough=Tier0_if_bounded "
            f"Tier1_if_orientation_needed Tier2_if_triggers={len(tier2_drawer.get('trigger_reasons') or [])}"
        ),
        "public_boundary": (
            "This pack is dashboard/operator-facing. Public/demo surfaces should explain the tier model, not run this walkthrough as a control surface."
        ),
        "operator_rule": (
            "Use the smallest tier that keeps the next move honest. Tier 0 is the default start, Tier 1 recovers orientation, and Tier 2 is explicit escalation."
        ),
        "current_signals": {
            "tier0_readiness": str(tier0_shell.get("readiness_status", "")).strip() or "unknown",
            "tier1_short_board_visible": bool(str(tier1_cards.get("short_board", "")).strip()),
            "tier1_closeout_attention_present": bool(closeout_attention.get("present")),
            "tier1_partial_count": int(parity_counts.get("partial", 0) or 0),
            "tier2_recommended_open": bool(tier2_drawer.get("recommended_open")),
        },
        "scenarios": walkthrough,
    }


def build_dashboard_command_shelf(
    *,
    agent_id: str,
    tier0_shell: dict[str, Any] | None,
    tier2_drawer: dict[str, Any] | None,
) -> dict[str, Any]:
    tier0_shell = tier0_shell or {}
    tier2_drawer = tier2_drawer or {}
    next_followup = tier0_shell.get("next_followup") or {}
    deeper_pulls = list(tier2_drawer.get("next_pull_commands") or [])
    tier2_trigger_reasons = [
        str(item).strip() for item in list(tier2_drawer.get("trigger_reasons") or []) if str(item).strip()
    ]

    commands = [
        {
            "label": "Start gate",
            "command": f"python scripts/start_agent_session.py --agent {agent_id} --tier 0 --no-ack",
            "tier": "Tier 0",
            "purpose": "Recover the smallest honest start posture before work begins.",
            "source_surface": "session_start.tier0",
            "activation_reason": "Always available as the smallest honest entry command.",
            "return_rule": "If Tier 0 already exposes a bounded next move, use that before pulling broader context.",
        },
        {
            "label": "Orientation shell",
            "command": f"python scripts/start_agent_session.py --agent {agent_id} --tier 1 --no-ack",
            "tier": "Tier 1",
            "purpose": "Pull short-board and observer orientation when Tier 0 is no longer enough.",
            "source_surface": "session_start.tier1",
            "activation_reason": "Use when the short board or observer orientation must be recovered before acting.",
            "return_rule": "Return to Tier 0 once the next bounded move is visible again.",
        },
        {
            "label": "Ack + packet",
            "command": f"python scripts/run_r_memory_packet.py --agent {agent_id} --ack",
            "tier": "Tier 1+",
            "purpose": "Advance observer state and re-read bounded shared surfaces.",
            "source_surface": "r_memory_packet.ack",
            "activation_reason": "Use when bounded shared surfaces need a fresh observer refresh after orientation work.",
            "return_rule": "If packet refresh does not change the next bounded move, go back to Tier 0 or Tier 1 instead of pulling deeper.",
        },
    ]

    if str(next_followup.get("command", "")).strip():
        commands.append(
            {
                "label": "Next bounded move",
                "command": str(next_followup.get("command", "")).strip(),
                "tier": "Tier 0",
                "purpose": "Use the already-visible bounded next move before inventing a broader workflow.",
                "source_surface": str(next_followup.get("target", "")).strip()
                or "mutation_preflight.next_followup",
                "activation_reason": str(next_followup.get("reason", "")).strip()
                or "Visible because Tier 0 already exposes one bounded follow-up.",
                "return_rule": "If this move broadens scope or loses fit, reopen Tier 1 before choosing a broader command.",
            }
        )

    if deeper_pulls:
        trigger_story = (
            "Visible because Tier 2 trigger(s) are active: " + ", ".join(tier2_trigger_reasons)
            if tier2_trigger_reasons
            else "Visible only when mutation, closeout, or contested continuity requires deeper review."
        )
        commands.append(
            {
                "label": "Deep pull",
                "command": deeper_pulls[0],
                "tier": "Tier 2",
                "purpose": "Only use when mutation, closeout, or contested continuity explicitly requires deeper review.",
                "source_surface": "tier2_deep_governance_drawer.next_pull_commands",
                "activation_reason": trigger_story,
                "return_rule": "When Tier 2 trigger reasons clear, close the drawer and return to the smallest tier that keeps the next move honest.",
            }
        )

    return {
        "present": True,
        "summary_text": f"command_shelf={len(commands)} tier-aware commands",
        "operator_rule": (
            "Use the dashboard as a thin operator shell over CLI/runtime truth. Commands here point back to the real entry surfaces; read each item's source, activation, and return cues before treating it as the next move."
        ),
        "commands": commands[:5],
    }
