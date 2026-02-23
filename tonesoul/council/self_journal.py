from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from memory import self_memory as self_memory_store

from ..memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
from .summary_generator import resolve_language
from .types import CouncilVerdict

VERDICT_LABELS = {
    "approve": ("approved", "\u901a\u904e"),
    "refine": ("needs refinement", "\u9700\u8981\u6539\u9032"),
    "declare_stance": ("needs a declared stance", "\u9700\u8981\u7acb\u5834\u8868\u660e"),
    "block": ("blocked", "\u5df2\u5c01\u9396"),
}


def _resolve_soul_db(
    path: Optional[os.PathLike],
    soul_db: Optional[SoulDB],
) -> SoulDB:
    if soul_db:
        return soul_db
    if path:
        return JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: Path(path)})
    return JsonlSoulDB()


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _label_for_verdict(verdict_value: str, language: str) -> str:
    label = VERDICT_LABELS.get(verdict_value)
    if not label:
        return verdict_value
    return label[0] if language == "en" else label[1]


def _build_self_statement(
    verdict: CouncilVerdict,
    identity: str,
    language: str,
) -> str:
    verdict_value = verdict.verdict.value
    verdict_label = _label_for_verdict(verdict_value, language)
    reason = verdict.human_summary or verdict.summary or ""

    if language == "zh":
        statement = f"\u6211\u662f{identity}\u3002\u6211\u525b\u525b\u5b8c\u6210\u4e00\u6b21\u5224\u65b7\uff0c\u7d50\u8ad6\u662f{verdict_label}\u3002"
        if reason:
            statement += f"\u539f\u56e0\uff1a{reason}"
        return statement

    statement = f"I am {identity}. I just completed a review and decided {verdict_label}."
    if reason:
        statement += f" Reason: {reason}"
    return statement


def _compute_risk_level(verdict: CouncilVerdict, context: dict) -> str:
    """Compute basic risk level based on tension and output verdict."""
    try:
        tension = float(context.get("tension", 0) or 0)
    except (TypeError, ValueError):
        tension = 0.0

    is_contra = bool(context.get("is_contradiction", False))
    verdict_name = getattr(verdict, "verdict", None)

    if is_contra:
        return "critical"
    if verdict_name and getattr(verdict_name, "name", "") == "BLOCK":
        return "high"
    if tension >= 0.8:
        return "high"
    if tension >= 0.4:
        return "medium"
    return "low"


def _compute_intent_match(context: dict, verdict: CouncilVerdict) -> bool:
    """Flag if user intent was fulfilled."""
    intent = context.get("user_intent")
    if not intent:
        return True

    verdict_name = getattr(verdict, "verdict", None)
    if verdict_name and getattr(verdict_name, "name", "") in ("BLOCK", "DECLARE_STANCE"):
        return False
    return True


def record_self_memory(
    verdict: CouncilVerdict,
    context: Optional[dict] = None,
    path: Optional[os.PathLike] = None,
    include_transcript: bool = True,
    soul_db: Optional[SoulDB] = None,
) -> dict:
    context = context or {}
    language = resolve_language(context)
    identity = str(context.get("self_identity", "ToneSoul"))
    divergence = verdict.divergence_analysis or {}

    self_statement = _build_self_statement(verdict, identity, language)
    uncertainty_level = getattr(verdict, "uncertainty_level", None)
    uncertainty_band = getattr(verdict, "uncertainty_band", None)
    uncertainty_reasons = getattr(verdict, "uncertainty_reasons", None) or []
    uncertainty_note = None
    if uncertainty_level is not None:
        band_label = uncertainty_band or "unknown"
        uncertainty_note = f"level={uncertainty_level:.3f}, band={band_label}"

    actor_type = context.get("actor_type", "agent")
    event_source = context.get("event_source", "unknown")
    intent_outcome = {
        "intent": context.get("user_intent"),
        "outcome": verdict.verdict.value if verdict and verdict.verdict else "unknown",
        "matched": _compute_intent_match(context, verdict),
    }
    risk_level = _compute_risk_level(verdict, context)

    extras = {
        "timestamp": _iso_now(),
        "actor_type": actor_type,
        "event_source": event_source,
        "intent_outcome": intent_outcome,
        "risk_level": risk_level,
        "identity": identity,
        "human_summary": verdict.human_summary,
        "core_divergence": divergence.get("core_divergence"),
        "recommended_action": divergence.get("recommended_action"),
        "self_statement": self_statement,
        "uncertainty_level": uncertainty_level,
        "uncertainty_band": uncertainty_band,
        "uncertainty_reasons": uncertainty_reasons,
    }
    if include_transcript:
        extras["transcript"] = verdict.transcript or {}

    return self_memory_store.record_self_memory(
        reflection=self_statement,
        context=context,
        verdict=verdict.verdict.value,
        coherence=verdict.coherence.overall,
        key_decision=verdict.summary,
        uncertainty=uncertainty_note,
        genesis=getattr(verdict, "genesis", None),
        is_mine=getattr(verdict, "is_mine", None),
        intent_id=getattr(verdict, "intent_id", None),
        extras=extras,
        journal_path=Path(path) if path else None,
        soul_db=soul_db,
    )


def load_recent_memory(
    limit: int = 3,
    path: Optional[os.PathLike] = None,
    soul_db: Optional[SoulDB] = None,
) -> List[dict]:
    if limit <= 0:
        return []
    return self_memory_store.load_recent_memory(
        n=limit,
        journal_path=Path(path) if path else None,
        soul_db=soul_db,
    )
