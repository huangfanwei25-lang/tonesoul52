"""Bounded Claude-style entry adapter for ToneSoul session-start shells."""

from __future__ import annotations

from typing import Any


def _build_priority_correction(
    *,
    priority_misread_guard: dict[str, Any],
    first_hop_order: list[str],
    next_followup_target: str,
) -> dict[str, Any]:
    return {
        "name": str(priority_misread_guard.get("name", "")).strip(),
        "trigger_surface": str(priority_misread_guard.get("trigger_surface", "")).strip(),
        "blocked_assumption": str(priority_misread_guard.get("rule", "")).strip(),
        "operator_action": str(priority_misread_guard.get("operator_action", "")).strip(),
        "why_now": str(priority_misread_guard.get("why_now", "")).strip(),
        "re_read_now": [surface for surface in first_hop_order[:4] if surface],
        "bounded_next_step_target": str(next_followup_target).strip(),
        "receiver_rule": (
            "Recover the blocked assumption through the same first-hop order before widening context or acting."
        ),
    }


def build_claude_entry_adapter(*, session_start_payload: dict[str, Any]) -> dict[str, Any]:
    """Translate a Tier-1 session-start bundle into a Claude-style entry shell."""

    from tonesoul.surface_versioning import build_surface_versioning_readout

    payload = dict(session_start_payload or {})
    consumer_contract = dict(payload.get("consumer_contract") or {})
    surface_versioning = (
        dict(payload.get("surface_versioning") or {}) or build_surface_versioning_readout()
    )
    canonical_center = dict(payload.get("canonical_center") or {})
    closeout_attention = dict(payload.get("closeout_attention") or {})
    mutation_preflight = dict(payload.get("mutation_preflight") or {})
    deliberation_mode_hint = dict(payload.get("deliberation_mode_hint") or {})
    subsystem_parity = dict(payload.get("subsystem_parity") or {})
    next_pull = dict(payload.get("next_pull") or {})

    required_read_order = list(consumer_contract.get("required_read_order") or [])
    priority_misread_guard = dict(consumer_contract.get("priority_misread_guard") or {})
    first_hop_order = [str(item.get("surface", "")).strip() for item in required_read_order]
    must_read_now = [
        {
            "surface": str(item.get("surface", "")).strip(),
            "receiver_rule": str(item.get("receiver_rule", "")).strip(),
        }
        for item in required_read_order[:4]
    ]

    short_board = dict(canonical_center.get("current_short_board") or {})
    next_focus = dict(subsystem_parity.get("next_focus") or {})
    closeout_focus = {
        "status": str(closeout_attention.get("status", "") or "complete"),
        "source_family": str(closeout_attention.get("source_family", "")).strip(),
        "operator_action": str(closeout_attention.get("operator_action", "")).strip(),
        "attention_pressures": list(closeout_attention.get("attention_pressures") or []),
        "why_now": str(closeout_attention.get("why_now", "")).strip(),
    }
    current_context = {
        "readiness": str((payload.get("readiness") or {}).get("status", "") or "unknown"),
        "deliberation_mode": str(
            deliberation_mode_hint.get("suggested_mode", "") or "unclassified"
        ),
        "closeout_status": str(closeout_attention.get("status", "") or "complete"),
        "short_board": str(short_board.get("summary_text", "")).strip(),
        "next_followup_target": str(
            (mutation_preflight.get("next_followup") or {}).get("target", "")
        ).strip(),
    }
    priority_correction = _build_priority_correction(
        priority_misread_guard=priority_misread_guard,
        first_hop_order=first_hop_order,
        next_followup_target=current_context["next_followup_target"],
    )

    return {
        "present": True,
        "shell": "claude_style_shell",
        "source_bundle_tier": int(payload.get("tier", 1) or 1),
        "summary_text": (
            f"claude_entry_adapter readiness={current_context['readiness']} "
            f"closeout={current_context['closeout_status']} "
            f"short_board_visible={bool(short_board.get('present'))} "
            f"next_focus={str(next_focus.get('resolved_to', '') or 'none')}"
        ),
        "first_hop_order": first_hop_order,
        "must_read_now": must_read_now,
        "must_not_assume": list(consumer_contract.get("misread_guards") or []),
        "must_correct_first": {
            "name": str(priority_misread_guard.get("name", "")).strip(),
            "trigger_surface": str(priority_misread_guard.get("trigger_surface", "")).strip(),
            "operator_action": str(priority_misread_guard.get("operator_action", "")).strip(),
            "why_now": str(priority_misread_guard.get("why_now", "")).strip(),
        },
        "priority_correction": priority_correction,
        "receiver_rule": str(consumer_contract.get("receiver_rule", "")).strip(),
        "surface_versioning": surface_versioning,
        "shell_rule": (
            "Start from the bounded Tier-1 orientation shell. Do not skip directly to packet detail or smooth handoff prose."
        ),
        "current_context": current_context,
        "closeout_focus": closeout_focus,
        "bounded_pulls": {
            "observe_first": True,
            "deep_pull_only_when": str(next_pull.get("receiver_rule", "")).strip(),
            "recommended_commands": list(next_pull.get("recommended_commands") or []),
        },
        "next_focus": next_focus,
    }
