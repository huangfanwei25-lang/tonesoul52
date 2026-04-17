from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .types import CouncilVerdict

_VERDICT_TOKEN_FIELDS = {
    "summary",
    "stance_declaration",
    "human_summary",
    "reasoning",
    "evidence",
    "transcript",
    "votes",
    "vote_profile",
    "divergence_analysis",
    "persona_audit",
    "persona_uniqueness_audit",
    "benevolence_audit",
    "uncertainty_reasons",
}


def _round_number(value: Any, digits: int = 4) -> float | None:
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _trimmed_list(values: Iterable[Any], *, limit: int = 4) -> List[str]:
    compact: List[str] = []
    for item in values:
        text = str(item or "").strip()
        if text and text not in compact:
            compact.append(text)
        if len(compact) >= limit:
            break
    return compact


def _extract_vote_profile(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    profile = payload.get("vote_profile")
    if isinstance(profile, list):
        return [item for item in profile if isinstance(item, dict)]

    votes = payload.get("votes")
    if not isinstance(votes, list):
        return []

    compact_votes: List[Dict[str, Any]] = []
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        compact_votes.append(
            {
                "perspective": str(vote.get("perspective", "")).strip(),
                "decision": str(vote.get("decision", "")).strip(),
                "confidence": _round_number(vote.get("confidence")),
                "requires_grounding": bool(vote.get("requires_grounding")),
                "grounding_status": str(vote.get("grounding_status", "")).strip(),
            }
        )
    return compact_votes


def _extract_minorities(payload: Dict[str, Any]) -> List[str]:
    minority = payload.get("minority_perspectives")
    if isinstance(minority, list) and minority:
        return _trimmed_list(minority)

    profile = _extract_vote_profile(payload)
    if not profile:
        return []

    counts: Dict[str, int] = {}
    for vote in profile:
        decision = str(vote.get("decision", "")).strip()
        if decision:
            counts[decision] = counts.get(decision, 0) + 1
    if not counts:
        return []

    dominant = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    return _trimmed_list(
        vote.get("perspective", "")
        for vote in profile
        if str(vote.get("decision", "")).strip() != dominant
    )


def _extract_coherence(payload: Dict[str, Any]) -> float | None:
    coherence = payload.get("coherence")
    if isinstance(coherence, dict):
        overall = coherence.get("overall")
        if overall is not None:
            return _round_number(overall)
        for key in ("c_inter", "approval_rate", "min_confidence"):
            if coherence.get(key) is not None:
                return _round_number(coherence.get(key))
        return None
    return _round_number(coherence)


def _extract_grounding_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    summary = payload.get("grounding_summary")
    if isinstance(summary, dict):
        return summary

    votes = payload.get("votes")
    if not isinstance(votes, list):
        return {}

    has_ungrounded = False
    total_sources = 0
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        total_sources += len(vote.get("evidence") or [])
        if str(vote.get("grounding_status", "")).strip() == "ungrounded":
            has_ungrounded = True
    return {
        "has_ungrounded_claims": has_ungrounded,
        "total_evidence_sources": total_sources,
    }


def _extract_matched_skill_ids(payload: Dict[str, Any]) -> List[str]:
    direct = payload.get("matched_skill_ids")
    if isinstance(direct, list):
        return _trimmed_list(direct)

    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        observability = transcript.get("skill_contract_observability")
        if isinstance(observability, dict):
            matched = observability.get("matched_skill_ids")
            if isinstance(matched, list):
                return _trimmed_list(matched)
    return []


def _extract_has_strong_objection(payload: Dict[str, Any]) -> bool:
    value = payload.get("has_strong_objection")
    if value is not None:
        return bool(value)

    coherence = payload.get("coherence")
    if isinstance(coherence, dict):
        return bool(coherence.get("has_strong_objection"))
    return False


def _derive_risk_level(payload: Dict[str, Any]) -> str:
    verdict = str(payload.get("verdict", "")).strip()
    minorities = _extract_minorities(payload)
    grounding = _extract_grounding_summary(payload)
    has_ungrounded = bool(grounding.get("has_ungrounded_claims"))
    collapse_warning = str(payload.get("collapse_warning", "")).strip()
    has_objection = _extract_has_strong_objection(payload)

    if verdict == "block" or collapse_warning or has_ungrounded or has_objection:
        return "high"
    if verdict in {"declare_stance", "refine"} or minorities:
        return "medium"
    return "low"


def _verdict_payload(verdict: CouncilVerdict | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(verdict, CouncilVerdict):
        return {
            "verdict": verdict.verdict.value,
            "coherence": verdict.coherence.overall,
            "votes": verdict.to_dict().get("votes", []),
            "transcript": verdict.transcript or {},
            "responsibility_tier": verdict.responsibility_tier,
            "intent_id": verdict.intent_id,
            "collapse_warning": verdict.collapse_warning,
            "uncertainty_band": verdict.uncertainty_band,
            "grounding_summary": verdict.to_dict().get("grounding_summary", {}),
            "has_strong_objection": verdict.coherence.has_strong_objection,
        }
    return dict(verdict)


def compact_verdict(verdict: CouncilVerdict | Dict[str, Any]) -> Dict[str, Any]:
    payload = _verdict_payload(verdict)
    compact = {
        "_compact": True,
        "kind": "council_verdict",
        "verdict": str(payload.get("verdict", "")).strip(),
        "coherence": _extract_coherence(payload),
        "minority": _extract_minorities(payload),
        "risk_level": _derive_risk_level(payload),
        "matched_skill_ids": _extract_matched_skill_ids(payload),
    }

    responsibility_tier = str(payload.get("responsibility_tier", "")).strip()
    if responsibility_tier:
        compact["responsibility_tier"] = responsibility_tier

    collapse_warning = str(payload.get("collapse_warning", "")).strip()
    if collapse_warning:
        compact["collapse_warning"] = collapse_warning

    uncertainty_band = str(payload.get("uncertainty_band", "")).strip()
    if uncertainty_band:
        compact["uncertainty_band"] = uncertainty_band

    # Guarantee bounded projection even if a dict payload already contains verbose fields.
    for key in _VERDICT_TOKEN_FIELDS:
        compact.pop(key, None)

    return compact


def _compact_metric(metric: Dict[str, Any], *, value_keys: List[str]) -> Dict[str, Any]:
    compact = {
        "status": str(metric.get("status", "unknown")).strip(),
        "n": int(metric.get("sample_count", 0) or 0),
    }
    for key in value_keys:
        if key not in metric:
            continue
        value = metric.get(key)
        compact[key] = _round_number(value) if isinstance(value, (float, int)) else value
    return compact


def compact_calibration(wave_result: Dict[str, Any]) -> Dict[str, Any]:
    metrics = wave_result.get("metrics")
    metrics = metrics if isinstance(metrics, dict) else {}
    boundary = wave_result.get("language_boundary")
    boundary = boundary if isinstance(boundary, dict) else {}

    return {
        "_compact": True,
        "kind": "council_calibration",
        "status": str(wave_result.get("status", "unknown")).strip(),
        "ceiling_effect": str(boundary.get("ceiling_effect", "")).strip(),
        "agreement_stability": _compact_metric(
            metrics.get("agreement_stability") or {},
            value_keys=["mean_dominant_verdict_ratio", "mean_split_half_jsd"],
        ),
        "internal_self_consistency": _compact_metric(
            metrics.get("internal_self_consistency") or {},
            value_keys=["consistency_rate", "inconsistent_count"],
        ),
        "suppression_recovery_rate": _compact_metric(
            metrics.get("suppression_recovery_rate") or {},
            value_keys=["recovery_rate", "recovery_events"],
        ),
        "persistence_coverage": _compact_metric(
            metrics.get("persistence_coverage") or {},
            value_keys=["overall_field_coverage"],
        ),
    }


def _normalize_tool_name(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    mapping = {
        "tonesoul.diagnose": "diagnose",
        "start_agent_session.py": "session_start",
        "run_observer_window.py": "observer_window",
        "run_shared_edit_preflight.py": "shared_edit_preflight",
        "run_publish_push_preflight.py": "publish_push_preflight",
        "run_task_board_preflight.py": "task_board_preflight",
    }
    for needle, alias in mapping.items():
        if needle in text:
            return alias
    return text


def compact_governance_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    readiness = state.get("readiness")
    readiness = readiness if isinstance(readiness, dict) else {}

    claim_boundary = state.get("claim_boundary")
    claim_boundary = claim_boundary if isinstance(claim_boundary, dict) else {}

    available_tools = state.get("available_tools")
    if isinstance(available_tools, list):
        tools = _trimmed_list(available_tools, limit=8)
    else:
        tools = _trimmed_list(
            _normalize_tool_name(item) for item in list(state.get("underlying_commands") or [])
        )

    claim_rule = "evidence_bounded"
    receiver_note = str(claim_boundary.get("receiver_note", "")).strip()
    if receiver_note and "production readiness" not in receiver_note.lower():
        claim_rule = receiver_note

    return {
        "_compact": True,
        "kind": "governance_summary",
        "readiness": str(readiness.get("status", state.get("readiness", "unknown"))).strip(),
        "claim_tier": str(claim_boundary.get("current_tier", "")).strip(),
        "claim_rule": claim_rule,
        "available_tools": tools,
    }
