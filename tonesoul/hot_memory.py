"""Helpers for successor-facing canonical center and hot-memory layering."""

from __future__ import annotations

import re
from typing import Any

_SHORT_BOARD_HEADER = "- Current short board:"
_SHORT_BOARD_SOURCE = "task.md > Water-Bucket Snapshot > Current short board"
_PARENT_SURFACES = ["task.md", "DESIGN.md"]


def extract_current_short_board_items(task_text: str) -> list[str]:
    """Extract the current short-board bullets from task.md-like text."""
    items: list[str] = []
    collecting = False

    for raw_line in str(task_text or "").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(_SHORT_BOARD_HEADER):
            collecting = True
            continue

        if not collecting:
            continue

        if re.match(r"^\s{2,}-\s+", raw_line):
            item = re.sub(r"^\s*-\s+", "", raw_line).strip()
            if item:
                items.append(item)
            continue

        if not stripped:
            continue

        break

    return items


def build_canonical_center(*, task_text: str) -> dict[str, Any]:
    """Build a bounded canonical-center summary from task.md text."""
    short_board_items = extract_current_short_board_items(task_text)
    short_board_present = bool(short_board_items)
    short_board_summary = (
        short_board_items[0]
        if short_board_present
        else "current short board is not visible in task.md"
    )

    return {
        "present": True,
        "parent_surfaces": list(_PARENT_SURFACES),
        "receiver_rule": (
            "Treat the canonical center as parent planning truth. "
            "Observer/readout children may orient continuation, but they do not override task.md or DESIGN.md."
        ),
        "successor_correction": {
            "highest_risk_misread": "observer_stable_is_execution_permission",
            "correction_rule": (
                "Stable observer output is shell-order orientation only. "
                "Before shared edits, confirm live_coordination directly: check readiness status, visible claims, "
                "and bounded_handoff receiver obligation."
            ),
            "required_checks": [
                "readiness.status",
                "claim_view.claims",
                "import_posture.surfaces.compactions.receiver_obligation",
            ],
            "summary_text": "observer stable != execution permission; confirm live_coordination first",
        },
        "current_short_board": {
            "present": short_board_present,
            "status": "visible" if short_board_present else "not_visible",
            "items": short_board_items[:4],
            "source": _SHORT_BOARD_SOURCE,
            "summary_text": short_board_summary,
        },
        "summary_text": (
            f"canonical_center short_board_items={len(short_board_items)} "
            f"source={_SHORT_BOARD_SOURCE}"
        ),
    }


def _build_layer(
    *,
    layer: str,
    status: str,
    primary_sources: list[str],
    receiver_rule: str,
    note: str,
) -> dict[str, Any]:
    return {
        "layer": layer,
        "status": status,
        "primary_sources": primary_sources,
        "receiver_rule": receiver_rule,
        "note": note,
    }


def build_hot_memory_ladder(
    *,
    canonical_center: dict[str, Any],
    import_posture: dict[str, Any],
    readiness: dict[str, Any],
    stable_count: int,
    contested_count: int,
    stale_count: int,
) -> dict[str, Any]:
    """Summarize the successor-facing hot-memory layers in one bounded ladder."""
    compactions = import_posture.get("compactions") or {}
    subject_snapshot = import_posture.get("subject_snapshot") or {}
    working_style = import_posture.get("working_style") or {}
    council_dossier = import_posture.get("council_dossier") or {}
    traces = import_posture.get("recent_traces") or {}
    short_board_present = bool(
        (canonical_center.get("current_short_board") or {}).get("present")
    )
    live_coordination_present = bool(
        (import_posture.get("posture") or {}).get("present")
        and (import_posture.get("readiness") or {}).get("present")
    )
    live_coordination_stable = live_coordination_present and str(
        (readiness or {}).get("status", "")
    ) == "pass"

    compaction_obligation = str(compactions.get("receiver_obligation", "")).strip()
    closeout_status = str(compactions.get("closeout_status", "")).strip()
    handoff_present = bool(compactions.get("present")) or bool(traces.get("present"))
    handoff_contested = compaction_obligation in {
        "must_not_promote",
        "must_review",
        "review_before_apply",
    } or closeout_status in {"partial", "blocked", "underdetermined"}

    working_identity_present = bool(subject_snapshot.get("present")) or bool(
        working_style.get("present")
    )
    working_style_status = str(
        ((working_style.get("working_style_observability") or {}).get("status", "") or "")
    ).strip()
    working_identity_contested = working_style_status not in {"", "reinforced"}

    replay_present = bool(council_dossier.get("present")) or bool(traces.get("present"))
    replay_contested = bool(
        (council_dossier.get("dossier_interpretation") or {}).get("calibration_status")
        == "descriptive_only"
    )

    layers = [
        _build_layer(
            layer="canonical_center",
            status="stable" if short_board_present else "contested",
            primary_sources=["task.md.current_short_board", "DESIGN.md"],
            receiver_rule="treat_as_parent_truth",
            note=(
                "Current short board is visible."
                if short_board_present
                else "Canonical parent surfaces exist, but the current short board is not visible."
            ),
        ),
        _build_layer(
            layer="low_drift_anchor",
            status="stale" if stale_count else ("contested" if contested_count else "stable"),
            primary_sources=[
                "import_posture.posture",
                "packet.launch_claim_posture",
                "packet.coordination_mode",
                "import_posture.readiness",
            ],
            receiver_rule="apply_when_stable_review_when_contested",
            note=(
                f"observer_window counts: stable={stable_count} contested={contested_count} stale={stale_count}"
            ),
        ),
        _build_layer(
            layer="live_coordination",
            status=(
                "stable" if live_coordination_stable else "contested" if live_coordination_present else "stale"
            ),
            primary_sources=["readiness", "claims", "task_track_hint", "deliberation_mode_hint"],
            receiver_rule="must_read_before_shared_edits",
            note=(
                f"readiness={str((readiness or {}).get('status', 'unknown') or 'unknown')}"
                if live_coordination_present
                else "No live coordination posture is visible."
            ),
        ),
        _build_layer(
            layer="bounded_handoff",
            status=(
                "stale"
                if not handoff_present
                else "contested" if handoff_contested else "stable"
            ),
            primary_sources=["compactions", "checkpoints", "delta_feed", "recent_traces"],
            receiver_rule="ack_or_review_never_self_promote",
            note=(
                f"receiver_obligation={compaction_obligation or 'none'} closeout={closeout_status or 'complete'}"
                if handoff_present
                else "No fresh handoff surface is visible."
            ),
        ),
        _build_layer(
            layer="working_identity",
            status=(
                "stale"
                if not working_identity_present
                else "contested" if working_identity_contested else "stable"
            ),
            primary_sources=["subject_snapshot", "working_style_anchor", "working_style_playbook"],
            receiver_rule="advisory_only_do_not_promote",
            note=(
                f"working_style_status={working_style_status or 'reinforced'}"
                if working_identity_present
                else "No working-identity surface is visible."
            ),
        ),
        _build_layer(
            layer="replay_review",
            status=(
                "stale" if not replay_present else "contested" if replay_contested else "stable"
            ),
            primary_sources=["recent_traces", "council_dossier", "validation_artifacts"],
            receiver_rule="review_for_context_not_for_authority",
            note=(
                "Council replay remains descriptive_only."
                if replay_contested
                else "Replay surfaces are available without current descriptive-only flags."
            ),
        ),
    ]

    return {
        "layers": layers,
        "summary_text": " | ".join(
            f"{entry['layer']}={entry['status']}" for entry in layers
        ),
        "receiver_note": (
            "Read the ladder from canonical_center downward. Parent layers orient or constrain child layers. "
            "Child summaries do not outrank parent truth."
        ),
    }
