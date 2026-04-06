"""Cross-agent memory consumer contract helpers."""

from __future__ import annotations

from typing import Any

_DEFAULT_SOURCE_PRECEDENCE_SUMMARY = (
    "canonical_anchors > live_coordination_truth > derived_orientation_shells > "
    "bounded_handoff > working_identity_and_replay"
)
_COMPATIBLE_CONSUMERS = [
    "codex_cli",
    "claude_style_shell",
    "dashboard_operator_shell",
]


def _step(
    surface: str,
    *,
    step: int,
    role: str,
    when: str,
    receiver_rule: str,
    misread_to_avoid: str,
) -> dict[str, Any]:
    return {
        "step": step,
        "surface": surface,
        "role": role,
        "when": when,
        "receiver_rule": receiver_rule,
        "misread_to_avoid": misread_to_avoid,
    }


def _guard(name: str, rule: str) -> dict[str, str]:
    return {"name": name, "rule": rule}


def build_memory_consumer_contract(
    *,
    readiness_status: str = "unknown",
    canonical_center: dict[str, Any] | None = None,
    closeout_attention: dict[str, Any] | None = None,
    mutation_preflight: dict[str, Any] | None = None,
    deep_surface_note: str = "Pull deeper packet/import surfaces only if the task is not already local and clear.",
) -> dict[str, Any]:
    """Return one bounded read-order and non-promotion contract for all consumer shells."""

    canonical_center = dict(canonical_center or {})
    closeout_attention = dict(closeout_attention or {})
    mutation_preflight = dict(mutation_preflight or {})

    current_short_board = canonical_center.get("current_short_board") or {}
    source_precedence_summary = str(
        canonical_center.get("source_precedence_summary", "") or _DEFAULT_SOURCE_PRECEDENCE_SUMMARY
    ).strip()
    short_board_visible = bool(current_short_board.get("present"))
    closeout_status = str(closeout_attention.get("status", "") or "complete").strip() or "complete"
    next_followup = mutation_preflight.get("next_followup") or {}

    required_read_order = [
        _step(
            "readiness",
            step=1,
            role="gate",
            when="always",
            receiver_rule="Read session readiness before trusting any summary or orientation shell.",
            misread_to_avoid="observer_stable_or_smooth_handoff_is_not_start_permission",
        ),
        _step(
            "canonical_center",
            step=2,
            role="parent_truth",
            when="always",
            receiver_rule="Use canonical center to recover the accepted short board and source precedence before deeper interpretation.",
            misread_to_avoid="compaction_or_observer_children_do_not_outrank_task_md_or_design",
        ),
        _step(
            "closeout_attention",
            step=3,
            role="anti_fake_completion",
            when="whenever recent compaction or handoff exists",
            receiver_rule="Read closeout state before reusing any compaction summary or next-action prose.",
            misread_to_avoid="smooth_compaction_summary_is_not_completed_work",
        ),
        _step(
            "mutation_preflight",
            step=4,
            role="side_effect_gate",
            when="before shared edits, publish/push, or task-board promotion",
            receiver_rule="Use bounded preflight before side effects; hook posture is narrower than general shell confidence.",
            misread_to_avoid="orientation_surfaces_do_not_authorize_mutation",
        ),
        _step(
            "deep_packet_or_observer_pull",
            step=5,
            role="context_expansion",
            when="only if readiness is not pass or the task is ambiguous, contested, or system-track",
            receiver_rule=deep_surface_note,
            misread_to_avoid="every_turn_needs_full_packet_or_full_observer_dump",
        ),
    ]

    misread_guards = [
        _guard(
            "observer_stable_not_verified",
            "Observer-window `stable` means currently unchallenged bounded orientation, not verified truth.",
        ),
        _guard(
            "compaction_not_completion",
            "Compaction summaries remain subordinate to closeout status and unresolved items.",
        ),
        _guard(
            "working_style_not_identity",
            "Working-style continuity can shape workflow, but must not be promoted into durable identity or policy.",
        ),
        _guard(
            "council_agreement_not_accuracy",
            "Council agreement and coherence remain descriptive unless separately calibrated by outcome evidence.",
        ),
    ]

    summary_bits = [
        "readiness",
        "canonical_center",
        "closeout_attention",
        "mutation_preflight",
        "deep_pull_only",
    ]
    if closeout_status != "complete":
        summary_bits.append(f"closeout={closeout_status}")
    if not short_board_visible:
        summary_bits.append("short_board=not_visible")
    if readiness_status and readiness_status != "unknown":
        summary_bits.append(f"readiness={readiness_status}")

    return {
        "present": True,
        "summary_text": "consumer_order=" + " -> ".join(summary_bits[:5]) + (
            f" | closeout={closeout_status}" if closeout_status != "complete" else ""
        ) + (
            f" | readiness={readiness_status}" if readiness_status and readiness_status != "unknown" else ""
        ),
        "compatible_consumers": list(_COMPATIBLE_CONSUMERS),
        "shell_parity_goal": (
            "Different shells may render different panes, but they should preserve the same first-hop order and non-promotion rules."
        ),
        "source_precedence_summary": source_precedence_summary,
        "required_read_order": required_read_order,
        "misread_guards": misread_guards,
        "receiver_rule": (
            "All consumers should recover the same parent truth, the same closeout meaning, and the same mutation gates before they widen context or act."
        ),
        "current_context": {
            "readiness_status": readiness_status or "unknown",
            "closeout_status": closeout_status,
            "short_board_visible": short_board_visible,
            "next_followup_target": str(next_followup.get("target", "")).strip(),
        },
    }
