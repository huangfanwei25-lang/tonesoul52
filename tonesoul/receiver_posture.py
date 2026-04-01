"""Shared receiver-posture readouts for cross-surface parity."""

from __future__ import annotations

from typing import Any


def _lane_classification(evidence_readout_posture: dict[str, Any], lane_name: str) -> str:
    for lane in list(evidence_readout_posture.get("lanes") or []):
        if str(lane.get("lane", "")).strip() == lane_name:
            return str(lane.get("classification", "")).strip()
    return ""


def _has_carry_forward_hazard(subject_refresh: dict[str, Any]) -> bool:
    for hazard in list(subject_refresh.get("promotion_hazards") or []):
        if "carry_forward" in str(hazard or ""):
            return True
    return False


def _build_primary_alerts(alert_entries: list[tuple[int, str]], *, limit: int = 4) -> list[str]:
    """Return a short session-start-friendly alert list without losing the full diagnostic set."""

    primary_alerts: list[str] = []
    for _priority, alert in sorted(alert_entries, key=lambda item: item[0], reverse=True):
        if alert in primary_alerts:
            continue
        primary_alerts.append(alert)
        if len(primary_alerts) >= limit:
            break
    return primary_alerts


def build_receiver_parity_readout(
    *,
    council_snapshot: dict[str, Any],
    project_memory_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build one bounded receiver-parity story for packet/session-start/diagnose."""

    decomposition = council_snapshot.get("confidence_decomposition") or {}
    evidence_readout_posture = project_memory_summary.get("evidence_readout_posture") or {}
    working_style_anchor = project_memory_summary.get("working_style_anchor") or {}
    working_style_observability = project_memory_summary.get("working_style_observability") or {}
    working_style_import_limits = project_memory_summary.get("working_style_import_limits") or {}
    subject_refresh = project_memory_summary.get("subject_refresh") or {}

    calibration_status = str(
        council_snapshot.get("calibration_status", "")
        or decomposition.get("calibration_status", "")
    ).strip()
    has_minority_report = bool(
        council_snapshot.get("has_minority_report")
        or list(council_snapshot.get("minority_report") or [])
    )
    suppression_flag = bool(council_snapshot.get("evolution_suppression_flag"))
    continuity_classification = (
        _lane_classification(
            evidence_readout_posture,
            "continuity_effectiveness",
        )
        or "unknown"
    )
    style_status = str(working_style_observability.get("status", "")).strip()
    if not style_status:
        style_status = "present" if working_style_anchor else "none"
    promotion_state = "guarded" if _has_carry_forward_hazard(subject_refresh) else "normal"

    alert_entries: list[tuple[int, str]] = []
    if promotion_state == "guarded":
        alert_entries.append(
            (
                100,
                "Latest carry-forward repeats an older handoff without new evidence; ack or review it, but do not promote it into subject identity or canonical planning.",
            )
        )
        if subject_refresh:
            alert_entries.append(
                (
                    95,
                    "Compaction-backed subject refresh is currently blocked by recycled carry-forward evidence; wait for a fresh compaction or stronger evidence before applying active_threads refresh.",
                )
            )
    if calibration_status == "descriptive_only":
        alert_entries.append(
            (
                90,
                "Latest council dossier confidence is descriptive_only; treat coherence and confidence posture as internal agreement context, not as an accuracy prediction.",
            )
        )
    if evidence_readout_posture:
        alert_entries.append(
            (
                20,
                "Evidence readout is a bounded honesty shortcut: continuity effectiveness is only runtime_present, council decision quality is descriptive_only, and higher-order axioms/theory remain document_backed unless separately proven.",
            )
        )
    if has_minority_report:
        alert_entries.append(
            (
                85,
                "Latest council dossier carries minority dissent; review it before treating approval as settled.",
            )
        )
    if suppression_flag:
        alert_entries.append(
            (
                80,
                "Latest council dossier indicates potential evolution suppression on repeated dissent; review minority signals carefully before dismissing objections.",
            )
        )
    if working_style_anchor:
        alert_entries.append(
            (
                70,
                "Working-style continuity is advisory only; reuse decision preferences and verified routines as habits, but do not promote them into vows, canonical rules, or durable identity.",
            )
        )
    if style_status == "partial":
        alert_entries.append(
            (
                68,
                "Shared working-style continuity is only partially reinforced by recent handoff surfaces; keep the playbook visible instead of assuming full habit continuity.",
            )
        )
    elif style_status == "unreinforced":
        alert_entries.append(
            (
                68,
                "Shared working-style continuity is currently unreinforced by recent handoff surfaces; apply it explicitly if it still fits, but do not assume the latest agent actually followed it.",
            )
        )
    if working_style_import_limits:
        alert_entries.append(
            (
                60,
                "Working-style import is bounded to scan order, evidence handling, prompt shape, session cadence, and render interpretation; it must not override vows, canonical governance, durable identity, or task scope.",
            )
        )

    alerts = [alert for _priority, alert in alert_entries]
    primary_alerts = _build_primary_alerts(alert_entries)

    summary_text = (
        "receiver_parity "
        f"council={calibration_status or 'unflagged'} "
        f"dissent={'visible' if has_minority_report else 'none'} "
        f"suppression={'flagged' if suppression_flag else 'clear'} "
        f"continuity={continuity_classification} "
        f"promotion={promotion_state} "
        f"style={style_status}"
    )
    rule = (
        "ack is safe visibility only; apply is bounded workflow use only; "
        "promote requires explicit justification and human confirmation."
    )
    action_ladder = [
        "ack: safe visibility and cursor advancement only",
        "apply: bounded workflow use only; do not treat advisory surfaces as canon",
        "promote: explicit justification plus human confirmation before authority elevation",
    ]
    return {
        "present": bool(alerts) or continuity_classification != "unknown",
        "summary_text": summary_text,
        "rule": rule,
        "action_ladder": action_ladder,
        "alerts": alerts,
        "primary_alerts": primary_alerts,
        "council": {
            "calibration_status": calibration_status or "unflagged",
            "has_minority_report": has_minority_report,
            "evolution_suppression_flag": suppression_flag,
        },
        "continuity": {
            "classification": continuity_classification,
            "promotion_state": promotion_state,
        },
        "working_style": {
            "status": style_status,
        },
    }
