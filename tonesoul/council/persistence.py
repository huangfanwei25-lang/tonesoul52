from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from tonesoul.store import KEY_COUNCIL_VERDICTS, get_store

from .types import CouncilVerdict, PerspectiveType

_SCHEMA_VERSION = "1.0.0"
_DEFAULT_RETENTION_LIMIT = 1000
_DEFAULT_TTL_SECONDS = 7776000
_FILE_SURFACE = ".aegis/council_verdicts.json"


def _utc_now_trimmed() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_text(value: str) -> str:
    return " ".join(str(value or "").split())


def _fingerprint_text(value: str) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _vote_profile(verdict: CouncilVerdict) -> List[Dict[str, Any]]:
    profile: List[Dict[str, Any]] = []
    for vote in verdict.votes:
        perspective = vote.perspective
        perspective_name = (
            perspective.value if isinstance(perspective, PerspectiveType) else str(perspective)
        )
        profile.append(
            {
                "perspective": perspective_name,
                "decision": vote.decision.value,
                "confidence": round(float(vote.confidence), 4),
                "requires_grounding": bool(vote.requires_grounding),
                "grounding_status": vote.grounding_status.value,
            }
        )
    return profile


def _minority_perspectives(profile: List[Dict[str, Any]]) -> List[str]:
    counts: Dict[str, int] = {}
    for vote in profile:
        decision = str(vote.get("decision", "")).strip()
        if decision:
            counts[decision] = counts.get(decision, 0) + 1
    if not counts:
        return []
    dominant_decision = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    return [
        str(vote.get("perspective", ""))
        for vote in profile
        if str(vote.get("decision", "")) != dominant_decision
        and str(vote.get("perspective", "")).strip()
    ]


def _grounding_summary(verdict: CouncilVerdict) -> Dict[str, Any]:
    total_sources = 0
    has_ungrounded = False
    for vote in verdict.votes:
        total_sources += len(vote.evidence or [])
        if vote.grounding_status.value == "ungrounded":
            has_ungrounded = True
    return {
        "has_ungrounded_claims": has_ungrounded,
        "total_evidence_sources": total_sources,
    }


def build_council_verdict_record(request, verdict: CouncilVerdict) -> Dict[str, Any]:
    context = request.context if isinstance(request.context, dict) else {}
    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    role_council = transcript.get("role_council") if isinstance(transcript, dict) else {}
    role_council = role_council if isinstance(role_council, dict) else {}
    signals = role_council.get("signals") if isinstance(role_council, dict) else {}
    signals = signals if isinstance(signals, dict) else {}
    skill_observability = (
        transcript.get("skill_contract_observability") if isinstance(transcript, dict) else {}
    )
    skill_observability = skill_observability if isinstance(skill_observability, dict) else {}

    agent = str(context.get("agent_id") or context.get("agent") or "unknown")
    session_id = str(context.get("session_id") or "")
    source = str(context.get("source") or "council_runtime")
    user_intent = request.user_intent if isinstance(request.user_intent, str) else ""
    vote_profile = _vote_profile(verdict)

    return {
        "record_id": f"cv-{uuid.uuid4().hex}",
        "schema_version": _SCHEMA_VERSION,
        "recorded_at": _utc_now_trimmed(),
        "agent": agent,
        "session_id": session_id,
        "source": source,
        "input_fingerprint": _fingerprint_text(f"{user_intent}\n{request.draft_output}"),
        "user_intent_fingerprint": _fingerprint_text(user_intent),
        "draft_fingerprint": _fingerprint_text(request.draft_output),
        "verdict": verdict.verdict.value,
        "coherence": round(float(verdict.coherence.overall), 6),
        "approval_rate": round(float(verdict.coherence.approval_rate), 6),
        "min_confidence": round(float(verdict.coherence.min_confidence), 6),
        "has_strong_objection": bool(verdict.coherence.has_strong_objection),
        "vote_profile": vote_profile,
        "minority_perspectives": _minority_perspectives(vote_profile),
        "grounding_summary": _grounding_summary(verdict),
        "decision_mode": str(role_council.get("decision_mode", "") or ""),
        "risk_roles": list(signals.get("risk_roles") or []),
        "audit_roles": list(signals.get("audit_roles") or []),
        "matched_skill_ids": list(skill_observability.get("matched_skill_ids") or []),
        "intent_id": verdict.intent_id,
        "responsibility_tier": verdict.responsibility_tier,
        "collapse_warning": verdict.collapse_warning,
    }


def persist_council_verdict(
    request,
    verdict: CouncilVerdict,
    *,
    store=None,
    limit: int = _DEFAULT_RETENTION_LIMIT,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
) -> Dict[str, Any]:
    active_store = store or get_store()
    append = getattr(active_store, "append_council_verdict", None)
    if not callable(append):
        raise AttributeError("store backend does not support council verdict persistence")

    record = build_council_verdict_record(request, verdict)
    append(record, limit=int(limit), ttl_seconds=int(ttl_seconds))

    backend_name = str(getattr(active_store, "backend_name", "unknown"))
    surface = KEY_COUNCIL_VERDICTS if backend_name == "redis" else _FILE_SURFACE
    return {
        "status": "stored",
        "record_id": record["record_id"],
        "backend": backend_name,
        "surface": surface,
        "retention": {
            "policy": "capped_rotation",
            "max_items": int(limit),
            "ttl_seconds": int(ttl_seconds),
        },
    }
