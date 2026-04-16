from __future__ import annotations

from typing import Any, Dict, List, Optional

_CLOSEOUT_STATUSES = {"complete", "partial", "blocked", "underdetermined"}
_CLOSEOUT_STOP_REASONS = {
    "external_blocked",
    "internal_unstable",
    "divergence_risk",
    "underdetermined",
}


def clean_text_list(values: Optional[List[Any]]) -> List[str]:
    result: List[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def looks_like_stop_action(text: str) -> bool:
    return str(text or "").strip().upper().startswith("STOP:")


def normalize_closeout_payload(
    closeout: Optional[Dict[str, Any]] = None,
    *,
    status: str = "",
    stop_reason: str = "",
    unresolved_items: Optional[List[str]] = None,
    human_input_required: bool = False,
    note: str = "",
    pending_paths: Optional[List[str]] = None,
    next_action: str = "",
) -> Dict[str, Any]:
    payload = dict(closeout or {})
    normalized_status = str(payload.get("status", status or "")).strip().lower()
    normalized_stop_reason = str(payload.get("stop_reason", stop_reason or "")).strip().lower()
    unresolved = clean_text_list(
        list(payload.get("unresolved_items") or []) + list(unresolved_items or [])
    )
    human_required = bool(payload.get("human_input_required", human_input_required))
    note_text = str(payload.get("note", note or "")).strip()
    pending = clean_text_list(list(payload.get("pending_paths") or []) + list(pending_paths or []))
    next_action_text = str(payload.get("next_action", next_action or "")).strip()

    if normalized_status not in _CLOSEOUT_STATUSES:
        normalized_status = ""
    if normalized_stop_reason not in _CLOSEOUT_STOP_REASONS:
        normalized_stop_reason = ""

    if not normalized_status:
        if normalized_stop_reason == "underdetermined":
            normalized_status = "underdetermined"
        elif normalized_stop_reason or human_required or looks_like_stop_action(next_action_text):
            normalized_status = "blocked"
        elif unresolved or pending or next_action_text:
            normalized_status = "partial"
        else:
            normalized_status = "complete"

    if normalized_status == "complete":
        if normalized_stop_reason == "underdetermined":
            normalized_status = "underdetermined"
        elif normalized_stop_reason or human_required or looks_like_stop_action(next_action_text):
            normalized_status = "blocked"
        elif unresolved or pending or next_action_text:
            normalized_status = "partial"

    if normalized_status == "underdetermined" and not normalized_stop_reason:
        normalized_stop_reason = "underdetermined"

    if not note_text:
        note_map = {
            "complete": "Closeout reports no unresolved handoff items.",
            "partial": "Closeout remains bounded but incomplete; review pending paths and next action before continuing.",
            "blocked": "Closeout is blocked; do not treat this handoff as completed work.",
            "underdetermined": "Closeout is underdetermined; gather stronger evidence or request human clarification before continuing.",
        }
        note_text = note_map[normalized_status]

    return {
        "status": normalized_status,
        "stop_reason": normalized_stop_reason,
        "unresolved_items": unresolved,
        "human_input_required": human_required,
        "note": note_text,
    }


def clean_string_list(values: Optional[List[Any]]) -> List[str]:
    cleaned: List[str] = []
    seen = set()
    for value in values or []:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def find_recycled_carry_forward_hazard(
    *,
    newer_compactions: List[Dict[str, Any]],
    all_compactions: List[Dict[str, Any]],
) -> str:
    if not newer_compactions:
        return ""

    latest = newer_compactions[0]
    latest_carry = clean_string_list(latest.get("carry_forward") or [])
    if not latest_carry:
        return ""

    latest_carry_key = tuple(latest_carry)
    latest_evidence = set(clean_string_list(latest.get("evidence_refs") or []))
    latest_id = str(latest.get("compaction_id", "")).strip()

    for previous in all_compactions[1:]:
        previous_id = str(previous.get("compaction_id", "")).strip()
        if previous_id and latest_id and previous_id == latest_id:
            continue

        previous_carry = clean_string_list(previous.get("carry_forward") or [])
        if tuple(previous_carry) != latest_carry_key:
            continue

        previous_evidence = set(clean_string_list(previous.get("evidence_refs") or []))
        if latest_evidence.issubset(previous_evidence):
            return (
                "Do not promote recycled carry_forward into durable identity when the latest "
                "compaction repeats the same handoff without any new evidence."
            )

    return ""


def normalize_council_dossier(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    normalized: Dict[str, Any] = {}
    dossier_version = str(payload.get("dossier_version", "")).strip()
    final_verdict = str(payload.get("final_verdict", "")).strip()
    confidence_posture = str(payload.get("confidence_posture", "")).strip()
    deliberation_mode = str(payload.get("deliberation_mode", "")).strip()
    opacity_declaration = str(payload.get("opacity_declaration", "")).strip()
    if dossier_version:
        normalized["dossier_version"] = dossier_version
    if final_verdict:
        normalized["final_verdict"] = final_verdict
    if confidence_posture:
        normalized["confidence_posture"] = confidence_posture
    if deliberation_mode:
        normalized["deliberation_mode"] = deliberation_mode
    if opacity_declaration:
        normalized["opacity_declaration"] = opacity_declaration

    for key in ("coherence_score", "dissent_ratio"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            normalized[key] = round(float(value), 3)
        except (TypeError, ValueError):
            continue

    minority_report: List[Dict[str, Any]] = []
    for item in payload.get("minority_report") or []:
        if not isinstance(item, dict):
            continue
        try:
            confidence = round(float(item.get("confidence", 0.0)), 3)
        except (TypeError, ValueError):
            confidence = 0.0
        entry = {
            "perspective": str(item.get("perspective", "")).strip(),
            "decision": str(item.get("decision", "")).strip(),
            "confidence": confidence,
            "reasoning": str(item.get("reasoning", "")).strip(),
            "evidence": clean_string_list(item.get("evidence")),
        }
        if entry["perspective"] and entry["decision"] and entry["reasoning"]:
            minority_report.append(entry)
    normalized["minority_report"] = minority_report

    vote_summary: List[Dict[str, Any]] = []
    for item in payload.get("vote_summary") or []:
        if not isinstance(item, dict):
            continue
        try:
            confidence = round(float(item.get("confidence", 0.0)), 3)
        except (TypeError, ValueError):
            confidence = 0.0
        entry = {
            "perspective": str(item.get("perspective", "")).strip(),
            "decision": str(item.get("decision", "")).strip(),
            "confidence": confidence,
        }
        reasoning = str(item.get("reasoning", "")).strip()
        evidence = clean_string_list(item.get("evidence"))
        if reasoning:
            entry["reasoning"] = reasoning
        if evidence:
            entry["evidence"] = evidence
        if entry["perspective"] and entry["decision"]:
            vote_summary.append(entry)
    normalized["vote_summary"] = vote_summary

    change_of_position: List[Dict[str, Any]] = []
    for item in payload.get("change_of_position") or []:
        if not isinstance(item, dict):
            continue
        entry = {str(key): value for key, value in item.items() if value is not None}
        if entry:
            change_of_position.append(entry)
    normalized["change_of_position"] = change_of_position

    normalized["evidence_refs"] = clean_string_list(payload.get("evidence_refs"))
    grounding = payload.get("grounding_summary")
    if isinstance(grounding, dict):
        normalized["grounding_summary"] = {
            "has_ungrounded_claims": bool(grounding.get("has_ungrounded_claims", False)),
            "total_evidence_sources": int(grounding.get("total_evidence_sources", 0) or 0),
        }
    decomposition = payload.get("confidence_decomposition")
    if isinstance(decomposition, dict):
        entry: Dict[str, Any] = {}
        calibration_status = str(decomposition.get("calibration_status", "")).strip()
        coverage_posture = str(decomposition.get("coverage_posture", "")).strip()
        evidence_posture = str(decomposition.get("evidence_posture", "")).strip()
        grounding_posture = str(decomposition.get("grounding_posture", "")).strip()
        adversarial_posture = str(decomposition.get("adversarial_posture", "")).strip()
        if calibration_status:
            entry["calibration_status"] = calibration_status
        if coverage_posture:
            entry["coverage_posture"] = coverage_posture
        if evidence_posture:
            entry["evidence_posture"] = evidence_posture
        if grounding_posture:
            entry["grounding_posture"] = grounding_posture
        if adversarial_posture:
            entry["adversarial_posture"] = adversarial_posture
        for key in ("agreement_score", "evidence_density"):
            value = decomposition.get(key)
            if value is None:
                continue
            try:
                entry[key] = round(float(value), 3)
            except (TypeError, ValueError):
                continue
        distinct_perspectives = decomposition.get("distinct_perspectives")
        if distinct_perspectives is not None:
            try:
                entry["distinct_perspectives"] = max(0, int(distinct_perspectives))
            except (TypeError, ValueError):
                pass
        if entry:
            normalized["confidence_decomposition"] = entry
    if "evolution_suppression_flag" in payload:
        normalized["evolution_suppression_flag"] = bool(payload.get("evolution_suppression_flag"))
    realism_note = str(payload.get("realism_note", "")).strip()
    if not realism_note:
        realism_note = derive_council_realism_note_from_normalized(normalized)
    if realism_note:
        normalized["realism_note"] = realism_note
    return normalized


def derive_council_realism_note_from_normalized(dossier: Dict[str, Any]) -> str:
    if not dossier:
        return ""

    decomposition = dossier.get("confidence_decomposition") or {}
    calibration_status = str(decomposition.get("calibration_status", "")).strip()
    has_minority_report = bool(dossier.get("minority_report"))
    adversarial_posture = str(decomposition.get("adversarial_posture", "")).strip()
    suppression_flag = bool(dossier.get("evolution_suppression_flag"))

    if calibration_status == "descriptive_only":
        if suppression_flag and has_minority_report:
            return (
                "Descriptive agreement record only; dissent is visible and suppression risk is flagged, "
                "so review minority signals before treating approval as settled."
            )
        if has_minority_report or adversarial_posture == "survived_dissent":
            return (
                "Descriptive agreement record only; visible dissent survived review, "
                "so approval is not equivalent to proven correctness."
            )
        return "Descriptive agreement record only; coherence and confidence posture are not calibrated accuracy signals."

    if suppression_flag and has_minority_report:
        return "Dissent and possible suppression are both visible; review minority signals before treating the verdict as settled."
    if has_minority_report:
        return "Minority dissent is visible; review it before treating approval as settled."
    return ""


def derive_council_realism_note(payload: Optional[Dict[str, Any]]) -> str:
    dossier = normalize_council_dossier(payload)
    return derive_council_realism_note_from_normalized(dossier)


def build_council_dossier_summary(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    dossier = normalize_council_dossier(payload)
    if not dossier:
        return {}
    minority_report = list(dossier.get("minority_report") or [])
    summary = {
        "final_verdict": str(dossier.get("final_verdict", "")),
        "confidence_posture": str(dossier.get("confidence_posture", "")),
        "coherence_score": float(dossier.get("coherence_score", 0.0) or 0.0),
        "dissent_ratio": float(dossier.get("dissent_ratio", 0.0) or 0.0),
        "has_minority_report": bool(minority_report),
    }
    deliberation_mode = str(dossier.get("deliberation_mode", "")).strip()
    opacity_declaration = str(dossier.get("opacity_declaration", "")).strip()
    if deliberation_mode:
        summary["deliberation_mode"] = deliberation_mode
    if opacity_declaration:
        summary["opacity_declaration"] = opacity_declaration
    decomposition = dossier.get("confidence_decomposition")
    if isinstance(decomposition, dict) and decomposition:
        summary["confidence_decomposition"] = decomposition
    if "evolution_suppression_flag" in dossier:
        summary["evolution_suppression_flag"] = bool(dossier.get("evolution_suppression_flag"))
    realism_note = derive_council_realism_note(dossier)
    if realism_note:
        summary["realism_note"] = realism_note
    return summary
