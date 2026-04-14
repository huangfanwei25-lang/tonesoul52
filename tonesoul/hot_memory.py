"""Helpers for successor-facing canonical center and hot-memory layering."""

from __future__ import annotations

import re
from typing import Any

_SHORT_BOARD_HEADERS = [
    "- Current short board:",
    "**Current short board:**",
]
_SHORT_BOARD_SOURCE = "task.md > Water-Bucket Snapshot > Current short board"
_PARENT_SURFACES = ["task.md", "DESIGN.md"]
_CANONICAL_ANCHOR_REFERENCES = [
    "AXIOMS.json",
    "DESIGN.md",
    "canonical architecture contracts",
    "task.md.current_short_board",
]
_SOURCE_PRECEDENCE = [
    {
        "layer": "canonical_anchors",
        "receiver_rule": "highest_parent_truth",
        "surfaces": [
            "AXIOMS.json",
            "DESIGN.md",
            "canonical architecture contracts",
            "task.md.current_short_board",
        ],
    },
    {
        "layer": "live_coordination_truth",
        "receiver_rule": "authoritative_for_current_session",
        "surfaces": [
            "packet.posture",
            "packet.project_memory_summary.launch_claim_posture",
            "packet.coordination_mode",
            "readiness",
        ],
    },
    {
        "layer": "derived_orientation_shells",
        "receiver_rule": "advisory_children_of_parents",
        "surfaces": [
            "session_start.import_posture",
            "canonical_center",
            "observer_window",
            "hot_memory_ladder",
            "subsystem_parity",
        ],
    },
    {
        "layer": "bounded_handoff",
        "receiver_rule": "review_before_apply_never_self_promote",
        "surfaces": [
            "compactions",
            "checkpoints",
            "delta_feed",
            "recent_traces",
        ],
    },
    {
        "layer": "working_identity_and_replay",
        "receiver_rule": "context_only_not_authority",
        "surfaces": [
            "subject_snapshot",
            "working_style_anchor",
            "working_style_playbook",
            "council_dossier",
        ],
    },
]
_HOT_MEMORY_DECAY_RULES = {
    "canonical_center": {
        "stable_use_posture": "operational",
        "nonstable_use_posture": "quarantine",
        "decay_posture": "human_refresh_only",
        "compression_posture": "never_compress",
        "base_note": "Parent truth; successors should re-read when the short board is not visible.",
    },
    "low_drift_anchor": {
        "stable_use_posture": "operational",
        "nonstable_use_posture": "review_only",
        "decay_posture": "recompute_each_session",
        "compression_posture": "already_compact_do_not_recompress",
        "base_note": "Observer summary should be rebuilt, not carried forward as its own authority.",
    },
    "live_coordination": {
        "stable_use_posture": "operational",
        "nonstable_use_posture": "review_only",
        "decay_posture": "expire_fast",
        "compression_posture": "do_not_compress_live_signals",
        "base_note": "Claims, readiness, and mode hints are only valid for the current coordination moment.",
    },
    "bounded_handoff": {
        "stable_use_posture": "review_only",
        "nonstable_use_posture": "quarantine",
        "decay_posture": "ttl_then_compress",
        "compression_posture": "compress_with_closeout_guards",
        "base_note": "Compactions may orient resumability, but incomplete closeout or promotion hazards require quarantine.",
    },
    "working_identity": {
        "stable_use_posture": "review_only",
        "nonstable_use_posture": "quarantine",
        "decay_posture": "slow_decay_with_refresh",
        "compression_posture": "do_not_compress_snapshot",
        "base_note": "Working identity is inheritable but non-canonical; stale or contested identity should not be leaned on.",
    },
    "replay_review": {
        "stable_use_posture": "review_only",
        "nonstable_use_posture": "review_only",
        "decay_posture": "prune_by_cardinality",
        "compression_posture": "preserve_dissent_then_prune_oldest",
        "base_note": "Replay helps context and audit, not authority or execution permission.",
    },
}


def extract_current_short_board_items(task_text: str) -> list[str]:
    """Extract the current short-board bullets from task.md-like text."""
    items: list[str] = []
    collecting = False
    nested = False  # True when header is a list item (items must be indented)

    for raw_line in str(task_text or "").splitlines():
        stripped = raw_line.strip()
        if not collecting:
            for h in _SHORT_BOARD_HEADERS:
                if stripped.startswith(h):
                    collecting = True
                    nested = h.startswith("- ")
                    break
            continue

        item_pattern = r"^\s{2,}-\s+" if nested else r"^-\s+"
        if re.match(item_pattern, raw_line):
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
        "canonical_anchor_references": list(_CANONICAL_ANCHOR_REFERENCES),
        "source_precedence": list(_SOURCE_PRECEDENCE),
        "source_precedence_summary": (
            "canonical_anchors > live_coordination_truth > derived_orientation_shells > "
            "bounded_handoff > working_identity_and_replay"
        ),
        "receiver_rule": (
            "Treat the canonical center as parent planning truth. "
            "Observer/readout children may orient continuation, but they do not override AXIOMS.json, DESIGN.md, canonical contracts, or the accepted short board."
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


def _build_current_pull_boundary(*, layers: list[dict[str, Any]]) -> dict[str, Any]:
    by_layer = {
        str(entry.get("layer", "")).strip(): str(entry.get("status", "")).strip() or "unknown"
        for entry in layers
    }
    canonical_status = by_layer.get("canonical_center", "unknown")
    anchor_status = by_layer.get("low_drift_anchor", "unknown")
    live_status = by_layer.get("live_coordination", "unknown")
    handoff_status = by_layer.get("bounded_handoff", "unknown")

    if canonical_status != "stable":
        return {
            "present": True,
            "pull_posture": "recover_parent_truth_first",
            "preferred_stop_at": "canonical_center",
            "why_now": "canonical_center is not currently stable enough to trust child shells by default.",
            "operator_action": "Stop at canonical_center and recover the accepted short board before trusting child shells or deeper replay.",
            "receiver_rule": "Recover parent truth first; do not keep pulling downward when canonical_center is contested.",
        }
    if live_status != "stable":
        return {
            "present": True,
            "pull_posture": "resolve_live_coordination_first",
            "preferred_stop_at": "live_coordination",
            "why_now": "live_coordination is not stable, so readiness and current coordination truth still need direct handling.",
            "operator_action": "Stop at live_coordination and resolve readiness, claim, or escalation pressure before deeper pulls.",
            "receiver_rule": "When live_coordination is not stable, treat deeper pulls as secondary until current coordination truth is handled.",
        }
    if handoff_status == "contested":
        return {
            "present": True,
            "pull_posture": "review_handoff_before_deeper_pull",
            "preferred_stop_at": "bounded_handoff",
            "why_now": "bounded_handoff is still contested, so closeout or receiver-obligation pressure remains active.",
            "operator_action": "Stop at bounded_handoff and review closeout plus receiver obligation before replay or working-identity surfaces.",
            "receiver_rule": "Read contested handoff state before deeper replay; smooth summaries do not remove closeout pressure.",
        }
    if anchor_status == "stale":
        return {
            "present": True,
            "pull_posture": "refresh_anchor_before_deeper_pull",
            "preferred_stop_at": "low_drift_anchor",
            "why_now": "the low-drift anchor is stale, so deeper context should wait until the orientation shell is refreshed.",
            "operator_action": "Refresh the low-drift anchor before trusting deeper replay or working-identity surfaces.",
            "receiver_rule": "Refresh stale orientation first; deeper pulls should not compensate for a stale anchor shell.",
        }
    return {
        "present": True,
        "pull_posture": "tier1_enough",
        "preferred_stop_at": "low_drift_anchor",
        "why_now": "canonical_center, live_coordination, and bounded_handoff are stable enough for a bounded orientation-first start.",
        "operator_action": "Tier-1 orientation is currently enough; do not deep-pull unless mutation, ambiguity, or conflict increases.",
        "receiver_rule": "Prefer the current bounded shell and stop at low_drift_anchor unless a later signal justifies deeper pull.",
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
    short_board_present = bool((canonical_center.get("current_short_board") or {}).get("present"))
    live_coordination_present = bool(
        (import_posture.get("posture") or {}).get("present")
        and (import_posture.get("readiness") or {}).get("present")
    )
    live_coordination_stable = (
        live_coordination_present and str((readiness or {}).get("status", "")) == "pass"
    )

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
                "stable"
                if live_coordination_stable
                else "contested" if live_coordination_present else "stale"
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
                "stale" if not handoff_present else "contested" if handoff_contested else "stable"
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

    current_pull_boundary = _build_current_pull_boundary(layers=layers)
    return {
        "layers": layers,
        "current_pull_boundary": current_pull_boundary,
        "summary_text": " | ".join(f"{entry['layer']}={entry['status']}" for entry in layers),
        "receiver_note": (
            "Read the ladder from canonical_center downward. Parent layers orient or constrain child layers. "
            "Child summaries do not outrank parent truth."
        ),
    }


def build_hot_memory_decay_map(*, hot_memory_ladder: dict[str, Any]) -> dict[str, Any]:
    """Classify which hot-memory layers are operational, review-only, or quarantined."""
    entries = list(hot_memory_ladder.get("layers") or [])
    mapped_layers: list[dict[str, Any]] = []
    operational_layers: list[str] = []
    review_only_layers: list[str] = []
    quarantine_layers: list[str] = []

    for entry in entries:
        layer_name = str(entry.get("layer", "")).strip()
        status = str(entry.get("status", "")).strip() or "unknown"
        rules = _HOT_MEMORY_DECAY_RULES.get(layer_name)
        if not rules:
            continue

        use_posture = (
            rules["stable_use_posture"] if status == "stable" else rules["nonstable_use_posture"]
        )
        if use_posture == "operational":
            operational_layers.append(layer_name)
        elif use_posture == "review_only":
            review_only_layers.append(layer_name)
        else:
            quarantine_layers.append(layer_name)

        mapped_layers.append(
            {
                "layer": layer_name,
                "status": status,
                "use_posture": use_posture,
                "decay_posture": rules["decay_posture"],
                "compression_posture": rules["compression_posture"],
                "quarantine_reason": (
                    str(entry.get("note", "")).strip() if use_posture == "quarantine" else ""
                ),
                "note": rules["base_note"],
            }
        )

    return {
        "layers": mapped_layers,
        "summary_text": (
            f"operational={','.join(operational_layers) or 'none'} "
            f"review_only={','.join(review_only_layers) or 'none'} "
            f"quarantine={','.join(quarantine_layers) or 'none'}"
        ),
        "receiver_note": (
            "Operational layers may orient immediate work. Review-only layers may inform resumability or context "
            "but should not be leaned on as authority. Quarantined layers should be refreshed or resolved before "
            "they influence edits."
        ),
    }
