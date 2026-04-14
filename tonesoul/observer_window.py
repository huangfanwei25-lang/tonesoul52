"""
Observer Window — Low-Drift Anchor

Purpose: derive a compact, bounded observer-window readout that tells a later agent:
  - what is currently stable (posture, launch tier, file-backed mode)
  - what is contested (council calibration, claim collisions, compaction hazards)
  - what is stale (old traces, outdated compactions, missing surfaces)
  - what changed since last seen (delta_feed summary)

Authority: advisory only.  This module must not be promoted into canonical governance truth.
Last Updated: 2026-03-30
Status: Day-1 implementation — minimal, bounded, testable.

Design Rules:
  - Derives from packet / session-start surfaces that already exist.
  - Never invents new interpretation axes.
  - Outputs exactly three top-level buckets: stable / contested / stale.
  - Each item is a bounded, one-line claim with an evidence_source reference.
  - A delta_summary block summarises what is new since last seen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tonesoul.consumer_contract import build_memory_consumer_contract
from tonesoul.hot_memory import (
    build_canonical_center,
    build_hot_memory_decay_map,
    build_hot_memory_ladder,
)
from tonesoul.repo_state_awareness import build_repo_state_awareness
from tonesoul.surface_versioning import build_surface_versioning_readout

# ---------------------------------------------------------------------------
# Thresholds (tuned conservatively; only raise after repeated validation)
# ---------------------------------------------------------------------------

_STALE_TRACE_HOURS = 48.0  # traces older than this are stale
_STALE_COMPACTION_HOURS = 72.0  # compactions older than this are stale
_STALE_SNAPSHOT_HOURS = 96.0  # subject snapshots older than this are stale


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hours(freshness_hours: float | None) -> float | None:
    if freshness_hours is None:
        return None
    try:
        return float(freshness_hours)
    except (TypeError, ValueError):
        return None


def _item(claim: str, *, evidence_source: str, detail: str = "") -> dict[str, str]:
    result: dict[str, str] = {"claim": claim, "evidence_source": evidence_source}
    if detail:
        result["detail"] = detail
    return result


def _build_closeout_attention(*, import_posture: dict[str, Any]) -> dict[str, Any]:
    """Lift non-complete compaction closeout into a dedicated successor-facing alert."""

    compaction_surface = import_posture.get("compactions") or {}
    closeout_status = str(compaction_surface.get("closeout_status", "")).strip() or "complete"
    stop_reason = str(compaction_surface.get("stop_reason", "")).strip()
    unresolved_count = int(compaction_surface.get("unresolved_count", 0) or 0)
    human_input_required = bool(compaction_surface.get("human_input_required", False))

    if closeout_status not in {"partial", "blocked", "underdetermined"}:
        return {
            "present": False,
            "status": "complete",
            "source_family": "",
            "attention_pressures": [],
            "operator_action": "",
            "why_now": "",
            "summary_text": "latest compaction closeout is complete or not currently contested",
            "receiver_rule": "No extra observer-window closeout lift is needed when the latest closeout is complete.",
        }

    detail_parts = [f"status={closeout_status}", f"unresolved={unresolved_count}"]
    attention_pressures = [f"status={closeout_status}", f"unresolved={unresolved_count}"]
    if stop_reason:
        detail_parts.append(f"stop_reason={stop_reason}")
        attention_pressures.append(f"stop_reason={stop_reason}")
    if human_input_required:
        detail_parts.append("human_input_required=true")
        attention_pressures.append("human_input_required=true")

    if closeout_status == "partial":
        operator_action = "Review unresolved items, stop reason, and next-action prose before treating the handoff as resumable work."
    else:
        operator_action = "Do not continue shared mutation yet; resolve the blocked or underdetermined closeout before treating the handoff as resumable work."

    return {
        "present": True,
        "status": closeout_status,
        "source_family": "bounded_handoff_closeout",
        "attention_pressures": attention_pressures,
        "operator_action": operator_action,
        "why_now": f"latest compaction closeout is {closeout_status}",
        "stop_reason": stop_reason,
        "unresolved_count": unresolved_count,
        "human_input_required": human_input_required,
        "summary_text": (
            f"latest compaction closeout is {closeout_status}; do not treat the handoff summary as completed work"
        ),
        "detail": " ".join(detail_parts),
        "receiver_rule": (
            "Read the closeout before the summary. A smooth compaction summary does not imply the previous session finished cleanly."
        ),
    }


# ---------------------------------------------------------------------------
# Stable bucket
# ---------------------------------------------------------------------------


def _build_stable(
    *, packet: dict[str, Any], import_posture: dict[str, Any]
) -> list[dict[str, str]]:
    """Items we can honestly call stable right now."""
    items: list[dict[str, str]] = []

    # Posture is directly importable — most stable surface
    posture_surface = import_posture.get("posture") or {}
    if str(posture_surface.get("import_posture", "")) == "directly_importable":
        items.append(
            _item(
                "governance posture is directly importable",
                evidence_source="import_posture.posture",
            )
        )

    # Launch tier — if collaborator_beta is confirmed
    project_memory = packet.get("project_memory_summary") or {}
    launch_claim = project_memory.get("launch_claim_posture") or {}
    current_tier = str(launch_claim.get("current_tier", "")).strip()
    public_launch_ready = bool(launch_claim.get("public_launch_ready", False))
    if current_tier == "collaborator_beta" and not public_launch_ready:
        items.append(
            _item(
                "launch tier is collaborator_beta; public_launch_ready=false",
                evidence_source="packet.project_memory_summary.launch_claim_posture",
            )
        )

    # Coordination backend — file-backed is the stable default
    coord_mode = packet.get("coordination_mode") or {}
    launch_default = str(coord_mode.get("launch_default_mode", "")).strip()
    if launch_default == "file-backed":
        items.append(
            _item(
                "coordination backend is file-backed (launch default)",
                evidence_source="packet.coordination_mode.launch_default_mode",
            )
        )

    # Evidence readout posture — present = stable enough to use
    evidence_readout = project_memory.get("evidence_readout_posture") or {}
    if evidence_readout:
        items.append(
            _item(
                "evidence_readout_posture is present and bounded",
                evidence_source="packet.project_memory_summary.evidence_readout_posture",
            )
        )

    # Readiness — if pass
    readiness_surface = import_posture.get("readiness") or {}
    if str(readiness_surface.get("import_posture", "")) == "directly_importable":
        items.append(
            _item(
                "session readiness surface is computed and directly importable",
                evidence_source="import_posture.readiness",
            )
        )

    return items


# ---------------------------------------------------------------------------
# Contested bucket
# ---------------------------------------------------------------------------


def _build_contested(
    *, packet: dict[str, Any], import_posture: dict[str, Any], readiness: dict[str, Any]
) -> list[dict[str, str]]:
    """Items that are present but not yet settled or calibrated."""
    items: list[dict[str, str]] = []

    compaction_surface = import_posture.get("compactions") or {}
    hazards = list(compaction_surface.get("promotion_hazards") or [])
    obligation = str(compaction_surface.get("receiver_obligation", "")).strip()
    closeout_status = str(compaction_surface.get("closeout_status", "")).strip()
    unresolved_count = int(compaction_surface.get("unresolved_count", 0) or 0)
    stop_reason = str(compaction_surface.get("stop_reason", "")).strip()
    if closeout_status in {"partial", "blocked", "underdetermined"}:
        detail_parts = [f"status={closeout_status}", f"unresolved={unresolved_count}"]
        if stop_reason:
            detail_parts.append(f"stop_reason={stop_reason}")
        items.append(
            _item(
                f"latest compaction closeout is '{closeout_status}'; do not read the handoff as completed work",
                evidence_source="import_posture.compactions.closeout_status",
                detail=" ".join(detail_parts),
            )
        )
    if hazards or obligation == "must_not_promote":
        items.append(
            _item(
                "latest compaction has carry_forward promotion hazard; must_not_promote",
                evidence_source="import_posture.compactions.promotion_hazards",
                detail=f"hazards={len(hazards)}",
            )
        )

    # Council calibration - always contested until proven
    council_surface = import_posture.get("council_dossier") or {}
    dossier = council_surface.get("dossier_interpretation") or {}
    calibration = str(dossier.get("calibration_status", "")).strip()
    if calibration == "descriptive_only" or council_surface.get("present"):
        items.append(
            _item(
                "council confidence is descriptive_only; agreement does not equal calibrated accuracy",
                evidence_source="import_posture.council_dossier.dossier_interpretation",
                detail=(
                    f"calibration_status={calibration}"
                    if calibration
                    else "council dossier present but calibration_status not confirmed"
                ),
            )
        )

    # Council evolution suppression - flag when minority dissent may be getting conformity-biased
    if dossier.get("evolution_suppression_flag"):
        items.append(
            _item(
                "council evolution suppression risk flagged; review minority signals before treating verdict as settled",
                evidence_source="import_posture.council_dossier.dossier_interpretation",
                detail="evolution_suppression_flag=True",
            )
        )

    # Claim conflicts
    claim_conflicts = int((readiness or {}).get("claim_conflict_count", 0) or 0)
    if claim_conflicts > 0:
        items.append(
            _item(
                f"other-agent claim collision detected ({claim_conflicts} conflict(s))",
                evidence_source="readiness.other_agent_claims",
                detail=f"conflict_count={claim_conflicts}",
            )
        )

    # Subject snapshot advisory note
    snapshot_surface = import_posture.get("subject_snapshot") or {}
    if snapshot_surface.get("present"):
        items.append(
            _item(
                "subject snapshot is advisory; must not be promoted into canonical identity",
                evidence_source="import_posture.subject_snapshot",
            )
        )

    # Working-style drift risk
    ws_surface = import_posture.get("working_style") or {}
    observability = ws_surface.get("working_style_observability") or {}
    ws_status = str(observability.get("status", "")).strip()
    if ws_status and ws_status != "reinforced":
        items.append(
            _item(
                f"working_style observability status is '{ws_status}'; monitor for drift",
                evidence_source="import_posture.working_style.working_style_observability",
                detail=f"status={ws_status}",
            )
        )

    return items


# ---------------------------------------------------------------------------
# Stale bucket
# ---------------------------------------------------------------------------


def _build_stale(*, import_posture: dict[str, Any]) -> list[dict[str, str]]:
    """Items that may be outdated or missing."""
    items: list[dict[str, str]] = []

    # Recent traces
    traces_surface = import_posture.get("recent_traces") or {}
    trace_hours = _hours(traces_surface.get("freshness_hours"))
    if not traces_surface.get("present"):
        items.append(
            _item(
                "recent_traces surface is absent; no session trace available",
                evidence_source="import_posture.recent_traces",
            )
        )
    elif trace_hours is not None and trace_hours > _STALE_TRACE_HOURS:
        items.append(
            _item(
                f"recent_traces are {trace_hours:.1f}h old (threshold={_STALE_TRACE_HOURS}h)",
                evidence_source="import_posture.recent_traces.freshness_hours",
                detail=f"freshness_hours={trace_hours:.1f}",
            )
        )

    # Compaction freshness
    compaction_surface = import_posture.get("compactions") or {}
    compaction_hours = _hours(compaction_surface.get("freshness_hours"))
    if not compaction_surface.get("present"):
        items.append(
            _item(
                "compactions surface is absent; no resumability handoff available",
                evidence_source="import_posture.compactions",
            )
        )
    elif compaction_hours is not None and compaction_hours > _STALE_COMPACTION_HOURS:
        items.append(
            _item(
                f"latest compaction is {compaction_hours:.1f}h old (threshold={_STALE_COMPACTION_HOURS}h)",
                evidence_source="import_posture.compactions.freshness_hours",
                detail=f"freshness_hours={compaction_hours:.1f}",
            )
        )

    # Subject snapshot freshness
    snapshot_surface = import_posture.get("subject_snapshot") or {}
    snapshot_hours = _hours(snapshot_surface.get("freshness_hours"))
    if (
        snapshot_surface.get("present")
        and snapshot_hours is not None
        and snapshot_hours > _STALE_SNAPSHOT_HOURS
    ):
        items.append(
            _item(
                f"subject snapshot is {snapshot_hours:.1f}h old (threshold={_STALE_SNAPSHOT_HOURS}h)",
                evidence_source="import_posture.subject_snapshot.freshness_hours",
                detail=f"freshness_hours={snapshot_hours:.1f}",
            )
        )

    # Evidence readout absent
    evidence_surface = import_posture.get("evidence_readout") or {}
    if not evidence_surface.get("present"):
        items.append(
            _item(
                "evidence_readout_posture is absent; cannot verify claim-to-evidence boundaries",
                evidence_source="import_posture.evidence_readout",
            )
        )

    return items


# ---------------------------------------------------------------------------
# Delta summary
# ---------------------------------------------------------------------------


def _build_delta_summary(*, packet: dict[str, Any]) -> dict[str, Any]:
    """Compact summary of what changed since last agent observation."""
    delta_feed = packet.get("delta_feed") or {}
    new_compactions = list(delta_feed.get("new_compactions") or [])
    new_checkpoints = list(delta_feed.get("new_checkpoints") or [])
    new_traces = list(delta_feed.get("new_traces") or [])
    first_observation = bool(delta_feed.get("first_observation", False))

    total_new = len(new_compactions) + len(new_checkpoints) + len(new_traces)
    has_updates = total_new > 0

    return {
        "first_observation": first_observation,
        "has_updates": has_updates,
        "new_compaction_count": len(new_compactions),
        "new_checkpoint_count": len(new_checkpoints),
        "new_trace_count": len(new_traces),
        "summary_text": (
            f"first_observation={first_observation} "
            f"new=compactions:{len(new_compactions)} checkpoints:{len(new_checkpoints)} traces:{len(new_traces)}"
        ),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_low_drift_anchor(
    *,
    packet: dict[str, Any],
    import_posture: dict[str, Any],
    readiness: dict[str, Any],
    canonical_center: dict[str, Any] | None = None,
    subsystem_parity: dict[str, Any] | None = None,
    mutation_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Derive a bounded low_drift_anchor from visible packet/session-start surfaces.

    Returns a dict with:
      stable:    list of items the current agent may treat as settled
      contested: list of items present but not yet calibrated or settled
      stale:     list of items that are absent or older than thresholds
      delta_summary: what changed since last seen
      generated_at: ISO timestamp
      receiver_note: mandatory non-promotion reminder

    This function is pure — it does not write any files or mutate state.
    All inputs must come from already-loaded packet / import_posture / readiness dicts.
    """
    stable = _build_stable(packet=packet, import_posture=import_posture)
    contested = _build_contested(packet=packet, import_posture=import_posture, readiness=readiness)
    stale = _build_stale(import_posture=import_posture)
    delta_summary = _build_delta_summary(packet=packet)
    canonical_center = canonical_center or build_canonical_center(task_text="")
    subsystem_parity = subsystem_parity or {}

    stable_count = len(stable)
    contested_count = len(contested)
    stale_count = len(stale)
    hot_memory_ladder = build_hot_memory_ladder(
        canonical_center=canonical_center,
        import_posture=import_posture,
        readiness=readiness,
        stable_count=stable_count,
        contested_count=contested_count,
        stale_count=stale_count,
    )
    hot_memory_decay_map = build_hot_memory_decay_map(hot_memory_ladder=hot_memory_ladder)
    repo_state_awareness = build_repo_state_awareness(
        project_memory_summary=packet.get("project_memory_summary") or {},
        delta_feed=packet.get("delta_feed") or {},
    )
    closeout_attention = _build_closeout_attention(import_posture=import_posture)
    consumer_contract = build_memory_consumer_contract(
        readiness_status=str(readiness.get("status", "") or "unknown"),
        canonical_center=canonical_center,
        closeout_attention=closeout_attention,
        mutation_preflight=mutation_preflight,
        deep_surface_note=(
            "Observer shell is for orientation first. Pull full packet/import detail only if the task is contested, blocked, or about to mutate shared state."
        ),
    )
    surface_versioning = build_surface_versioning_readout()
    closeout_status = str(closeout_attention.get("status", "complete") or "complete")

    return {
        "generated_at": _iso_now(),
        "canonical_center": canonical_center,
        "subsystem_parity": subsystem_parity,
        "hot_memory_ladder": hot_memory_ladder,
        "hot_memory_decay_map": hot_memory_decay_map,
        "repo_state_awareness": repo_state_awareness,
        "closeout_attention": closeout_attention,
        "consumer_contract": consumer_contract,
        "surface_versioning": surface_versioning,
        "stable": stable,
        "contested": contested,
        "stale": stale,
        "delta_summary": delta_summary,
        "counts": {
            "stable": stable_count,
            "contested": contested_count,
            "stale": stale_count,
        },
        "summary_text": (
            f"observer_window stable={stable_count} contested={contested_count} stale={stale_count} "
            f"delta_has_updates={delta_summary['has_updates']} "
            f"repo_state={repo_state_awareness.get('classification', 'unknown')} "
            f"closeout_attention={closeout_status}"
        ),
        "receiver_note": (
            "This observer window is advisory only. "
            "Items in 'stable' reflect current bounded posture but do not outrank canonical contracts. "
            "Items in 'contested' must not be treated as confirmed. "
            "Items in 'stale' should trigger a re-read before leaning on them. "
            "Do not promote this readout into canonical governance truth."
        ),
    }
