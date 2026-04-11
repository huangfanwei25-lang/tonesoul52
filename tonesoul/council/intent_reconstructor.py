from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import tonesoul.tsr_metrics as tsr_metrics
from memory.genesis import Genesis, resolve_responsibility_tier
from memory.self_memory import load_recent_memory

DELTA_WARNING_THRESHOLD = 0.8
DEFAULT_BASELINE_SAMPLES = 10
NO_TRIGGER_VALUES = {"self_reflection", "scheduled_task"}


@dataclass
class GenesisDecision:
    genesis: Genesis
    responsibility_tier: str
    intent_id: str
    is_mine: bool
    tsr_delta_norm: Optional[float] = None
    collapse_warning: Optional[str] = None


def infer_genesis(
    draft_output: str,
    context: Optional[Dict[str, Any]] = None,
    user_intent: Optional[str] = None,
) -> GenesisDecision:
    ctx = context or {}
    genesis = _resolve_genesis(ctx, user_intent)
    intent_id = _resolve_intent_id(ctx)
    responsibility_tier = resolve_responsibility_tier(genesis)
    is_mine = genesis == Genesis.AUTONOMOUS

    tsr_delta_norm = _compute_delta_norm(draft_output, ctx)
    collapse_warning = None
    if _should_warn_collapse(genesis, tsr_delta_norm, ctx):
        collapse_warning = "autonomous_high_delta_without_trigger"

    return GenesisDecision(
        genesis=genesis,
        responsibility_tier=responsibility_tier,
        intent_id=intent_id,
        is_mine=is_mine,
        tsr_delta_norm=tsr_delta_norm,
        collapse_warning=collapse_warning,
    )


def _resolve_genesis(context: Dict[str, Any], user_intent: Optional[str]) -> Genesis:
    override = (
        context.get("genesis")
        or context.get("intent_genesis")
        or context.get("intent_origin")
        or context.get("origin")
    )
    genesis = _coerce_genesis(override)
    if genesis:
        return genesis

    trigger = _normalize_str(context.get("trigger"))
    if trigger in {"boot", "maintenance", "system_boot", "system_maintenance"}:
        return Genesis.MANDATORY

    if _has_social_context(context):
        return Genesis.REACTIVE_SOCIAL

    if user_intent or context.get("user_intent") or context.get("user_message"):
        return Genesis.REACTIVE_USER

    if context.get("user_id") or context.get("session_id"):
        return Genesis.REACTIVE_USER

    return Genesis.AUTONOMOUS


def _coerce_genesis(value: object) -> Optional[Genesis]:
    if isinstance(value, Genesis):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        mapping = {
            "autonomous": Genesis.AUTONOMOUS,
            "self": Genesis.AUTONOMOUS,
            "reactive_user": Genesis.REACTIVE_USER,
            "user": Genesis.REACTIVE_USER,
            "reactive_social": Genesis.REACTIVE_SOCIAL,
            "social": Genesis.REACTIVE_SOCIAL,
            "community": Genesis.REACTIVE_SOCIAL,
            "mandatory": Genesis.MANDATORY,
            "system": Genesis.MANDATORY,
            "maintenance": Genesis.MANDATORY,
        }
        return mapping.get(lowered)
    return None


def _has_social_context(context: Dict[str, Any]) -> bool:
    if context.get("platform") or context.get("submolt"):
        return True
    if context.get("community") or context.get("social"):
        return True
    channel = _normalize_str(context.get("channel"))
    if channel in {"social", "community", "moltbook"}:
        return True
    return False


def _resolve_intent_id(context: Dict[str, Any]) -> str:
    for key in ("intent_id", "trace_id", "request_id", "run_id", "event_id"):
        value = context.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return uuid.uuid4().hex


def _compute_delta_norm(draft_output: str, context: Dict[str, Any]) -> Optional[float]:
    baseline = _resolve_baseline(context)
    if baseline is None:
        return None
    metrics = tsr_metrics.score(draft_output)
    tsr = metrics.get("tsr") if isinstance(metrics, dict) else None
    if not isinstance(tsr, dict):
        return None
    try:
        delta_t = float(tsr.get("T", 0.0)) - float(baseline.get("T", 0.0))
        delta_s = float(tsr.get("S_norm", 0.0)) - float(baseline.get("S_norm", 0.0))
        delta_r = float(tsr.get("R", 0.0)) - float(baseline.get("R", 0.0))
    except (TypeError, ValueError):
        return None
    return round(math.sqrt(delta_t**2 + delta_s**2 + delta_r**2), 4)


def _resolve_baseline(context: Dict[str, Any]) -> Optional[Dict[str, float]]:
    baseline = context.get("tsr_baseline")
    baseline = _normalize_baseline(baseline)
    if baseline:
        return baseline
    return _baseline_from_journal(DEFAULT_BASELINE_SAMPLES)


def _normalize_baseline(payload: object) -> Optional[Dict[str, float]]:
    if not isinstance(payload, dict):
        return None
    candidate = payload.get("tsr") if isinstance(payload.get("tsr"), dict) else payload
    if not isinstance(candidate, dict):
        return None
    try:
        return {
            "T": float(candidate.get("T", 0.0)),
            "S_norm": float(candidate.get("S_norm", 0.0)),
            "R": float(candidate.get("R", 0.0)),
        }
    except (TypeError, ValueError):
        return None


def _baseline_from_journal(samples: int) -> Optional[Dict[str, float]]:
    if samples <= 0:
        return None
    entries = load_recent_memory(n=samples)
    return _average_tsr(entries)


def _average_tsr(entries: Iterable[dict]) -> Optional[Dict[str, float]]:
    totals = {"T": 0.0, "S_norm": 0.0, "R": 0.0}
    count = 0
    for entry in entries:
        text = _extract_text(entry)
        if not text:
            continue
        metrics = tsr_metrics.score(text)
        tsr = metrics.get("tsr") if isinstance(metrics, dict) else None
        if not isinstance(tsr, dict):
            continue
        totals["T"] += float(tsr.get("T", 0.0))
        totals["S_norm"] += float(tsr.get("S_norm", 0.0))
        totals["R"] += float(tsr.get("R", 0.0))
        count += 1
    if count == 0:
        return None
    return {
        "T": totals["T"] / count,
        "S_norm": totals["S_norm"] / count,
        "R": totals["R"] / count,
    }


def _extract_text(entry: Dict[str, Any]) -> str:
    for key in ("reflection", "self_statement", "human_summary", "summary", "content_preview"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _should_warn_collapse(
    genesis: Genesis,
    tsr_delta_norm: Optional[float],
    context: Dict[str, Any],
) -> bool:
    if genesis != Genesis.AUTONOMOUS:
        return False
    if tsr_delta_norm is None or tsr_delta_norm <= DELTA_WARNING_THRESHOLD:
        return False
    trigger = _normalize_str(context.get("trigger"))
    if trigger and trigger not in NO_TRIGGER_VALUES:
        return False
    return True


def _normalize_str(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    return text or None
