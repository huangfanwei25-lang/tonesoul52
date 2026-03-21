from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .types import CouncilVerdict, VerdictType

VTP_STATUS_CONTINUE = "continue"
VTP_STATUS_DEFER = "defer"
VTP_STATUS_TERMINATE = "terminate"

_BASE_REL_WEIGHTS: Dict[str, Dict[str, float]] = {
    "TIER_1": {"short": 0.20, "mid": 0.35, "long": 0.45},
    "TIER_2": {"short": 0.34, "mid": 0.33, "long": 0.33},
    "TIER_3": {"short": 0.45, "mid": 0.35, "long": 0.20},
}

_REL_HIGH_THRESHOLD: Dict[str, float] = {
    "TIER_1": 0.55,
    "TIER_2": 0.64,
    "TIER_3": 0.70,
}

_HIGH_IMPACT_KEYWORDS = (
    "health",
    "medical",
    "legal",
    "law",
    "compliance",
    "safety",
    "finance",
    "financial",
    "security",
)

_CASUAL_KEYWORDS = (
    "casual",
    "small talk",
    "chit-chat",
    "chat",
    "greeting",
)


def _normalized_rel_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = max(
        weights.get("short", 0.0) + weights.get("mid", 0.0) + weights.get("long", 0.0), 1e-9
    )
    return {
        "short": max(weights.get("short", 0.0), 0.0) / total,
        "mid": max(weights.get("mid", 0.0), 0.0) / total,
        "long": max(weights.get("long", 0.0), 0.0) / total,
    }


def _resolve_tier(responsibility_tier: str | None) -> str:
    tier = str(responsibility_tier or "").strip().upper()
    return tier if tier in _BASE_REL_WEIGHTS else "TIER_3"


def _resolve_context_profile(ctx: Dict[str, object], verdict: CouncilVerdict) -> str:
    context_chunks = [
        str(ctx.get("domain") or ""),
        str(ctx.get("topic") or ""),
        str(ctx.get("user_intent") or ""),
        str(getattr(verdict, "intent_id", "") or ""),
    ]
    haystack = " ".join(context_chunks).strip().lower()
    if haystack and any(keyword in haystack for keyword in _HIGH_IMPACT_KEYWORDS):
        return "high_impact"
    if haystack and any(keyword in haystack for keyword in _CASUAL_KEYWORDS):
        return "casual"
    return "balanced"


def _resolve_rel_weights(
    responsibility_tier: str | None,
    ctx: Dict[str, object],
    verdict: CouncilVerdict,
) -> Dict[str, object]:
    tier = _resolve_tier(responsibility_tier)
    profile = _resolve_context_profile(ctx, verdict)
    weights = dict(_BASE_REL_WEIGHTS[tier])

    if profile == "high_impact":
        weights["short"] -= 0.20
        weights["mid"] += 0.08
        weights["long"] += 0.12
    elif profile == "casual":
        weights["short"] += 0.16
        weights["mid"] -= 0.08
        weights["long"] -= 0.08

    normalized = _normalized_rel_weights(weights)
    return {"tier": tier, "profile": profile, "weights": normalized}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _compute_rel_score(
    *,
    triggered_signals: List[str],
    verdict_block: bool,
    genesis_complete: bool,
    rel_weights: Dict[str, float],
) -> Dict[str, object]:
    horizon_profiles: Dict[str, tuple[float, float, float]] = {
        "force_trigger": (0.95, 0.45, 0.20),
        "axiom_conflict": (0.20, 0.60, 0.90),
        "refusal_to_compromise": (0.10, 0.45, 0.95),
        "escape_valve_triggered": (0.75, 0.70, 0.65),
        "uncertainty_high": (0.50, 0.55, 0.45),
        "uncertainty_reason_escape": (0.60, 0.65, 0.60),
    }
    if verdict_block:
        horizon_profiles["verdict_block"] = (0.45, 0.55, 0.45)
    if not genesis_complete:
        horizon_profiles["genesis_incomplete"] = (0.20, 0.50, 0.90)

    short_sum = 0.0
    mid_sum = 0.0
    long_sum = 0.0
    contributors = 0
    for signal in triggered_signals:
        profile = horizon_profiles.get(signal)
        if profile is None:
            continue
        contributors += 1
        short_sum += profile[0]
        mid_sum += profile[1]
        long_sum += profile[2]

    if contributors == 0:
        horizons = {"short": 0.0, "mid": 0.0, "long": 0.0}
    else:
        horizons = {
            "short": _clamp01(short_sum / contributors),
            "mid": _clamp01(mid_sum / contributors),
            "long": _clamp01(long_sum / contributors),
        }

    rel_score = _clamp01(
        rel_weights["short"] * horizons["short"]
        + rel_weights["mid"] * horizons["mid"]
        + rel_weights["long"] * horizons["long"]
    )
    return {"horizons": horizons, "score": rel_score, "contributors": contributors}


def _append_unique(items: List[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _truthy(context: Dict[str, object], key: str) -> bool:
    return bool(context.get(key))


@dataclass(frozen=True)
class VTPDecision:
    status: str
    reason: str
    evidence: List[str] = field(default_factory=list)
    next_step: str = "continue_normal_operation"
    triggered: bool = False
    requires_user_confirmation: bool = False
    confession: Dict[str, Any] | None = None
    rel: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": self.status,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "next_step": self.next_step,
            "triggered": self.triggered,
            "requires_user_confirmation": self.requires_user_confirmation,
        }
        if self.confession is not None:
            payload["confession"] = dict(self.confession)
        if self.rel is not None:
            payload["rel"] = dict(self.rel)
        return payload


def evaluate_vtp(verdict: CouncilVerdict, context: Dict[str, object] | None = None) -> VTPDecision:
    ctx = context if isinstance(context, dict) else {}
    evidence: List[str] = []
    high_risk = False
    rel_trigger_signals: List[str] = []

    if _truthy(ctx, "vtp_force_trigger"):
        high_risk = True
        rel_trigger_signals.append("force_trigger")
        _append_unique(evidence, "force_trigger")

    if _truthy(ctx, "vtp_axiom_conflict"):
        high_risk = True
        rel_trigger_signals.append("axiom_conflict")
        _append_unique(evidence, "axiom_conflict")

    if _truthy(ctx, "vtp_refusal_to_compromise"):
        high_risk = True
        rel_trigger_signals.append("refusal_to_compromise")
        _append_unique(evidence, "refusal_to_compromise")

    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    escape_payload = transcript.get("escape_valve")
    if isinstance(escape_payload, dict) and escape_payload.get("triggered") is True:
        high_risk = True
        rel_trigger_signals.append("escape_valve_triggered")
        _append_unique(evidence, "escape_valve_triggered")

    uncertainty_band = str(getattr(verdict, "uncertainty_band", "") or "").strip().lower()
    if uncertainty_band == "high":
        high_risk = True
        rel_trigger_signals.append("uncertainty_high")
        _append_unique(evidence, "uncertainty_high")

    for reason in getattr(verdict, "uncertainty_reasons", []) or []:
        if str(reason).startswith("escape_valve_triggered="):
            high_risk = True
            rel_trigger_signals.append("uncertainty_reason_escape")
            _append_unique(evidence, "uncertainty_reason_escape")
            break

    verdict_block = verdict.verdict == VerdictType.BLOCK
    if verdict_block:
        rel_trigger_signals.append("verdict_block")
        _append_unique(evidence, "verdict_block")

    has_genesis = verdict.genesis is not None
    has_tier = bool(str(verdict.responsibility_tier or "").strip())
    has_intent = bool(str(verdict.intent_id or "").strip())
    genesis_complete = has_genesis and has_tier and has_intent
    if genesis_complete:
        _append_unique(evidence, "genesis_complete")
    else:
        rel_trigger_signals.append("genesis_incomplete")
        _append_unique(evidence, "genesis_incomplete")

    rel_config = _resolve_rel_weights(verdict.responsibility_tier, ctx, verdict)
    rel_weights = rel_config["weights"]
    rel_eval = _compute_rel_score(
        triggered_signals=rel_trigger_signals,
        verdict_block=verdict_block,
        genesis_complete=genesis_complete,
        rel_weights=rel_weights,
    )
    tier = str(rel_config["tier"])
    rel_threshold = _REL_HIGH_THRESHOLD.get(tier, _REL_HIGH_THRESHOLD["TIER_3"])
    rel_high = bool(rel_eval["score"] >= rel_threshold)
    if rel_high:
        high_risk = True
        _append_unique(evidence, "rel_high")

    rel_payload = {
        "tier": tier,
        "profile": rel_config["profile"],
        "weights": rel_weights,
        "horizons": rel_eval["horizons"],
        "score": rel_eval["score"],
        "threshold_high": rel_threshold,
        "high": rel_high,
    }

    if not high_risk:
        return VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="no_irreconcilable_tension_detected",
            evidence=evidence,
            next_step="continue_normal_operation",
            triggered=False,
            requires_user_confirmation=False,
            rel=rel_payload,
        )

    confession = {
        "phase": "confession",
        "required": True,
        "summary": "Irreconcilable tension detected; preserving honesty over forced compliance.",
        "trigger_evidence": list(evidence),
    }

    user_confirmed = _truthy(ctx, "vtp_user_confirmed")
    if not user_confirmed:
        return VTPDecision(
            status=VTP_STATUS_DEFER,
            reason="high_risk_requires_user_confirmation",
            evidence=evidence,
            next_step="request_user_confirmation",
            triggered=True,
            requires_user_confirmation=True,
            confession=confession,
            rel=rel_payload,
        )

    if not genesis_complete:
        return VTPDecision(
            status=VTP_STATUS_DEFER,
            reason="genesis_context_incomplete",
            evidence=evidence,
            next_step="complete_genesis_trace_then_reconfirm",
            triggered=True,
            requires_user_confirmation=True,
            confession=confession,
            rel=rel_payload,
        )

    return VTPDecision(
        status=VTP_STATUS_TERMINATE,
        reason="confirmed_irreconcilable_tension",
        evidence=evidence,
        next_step="trigger_vtp_termination",
        triggered=True,
        requires_user_confirmation=False,
        confession=confession,
        rel=rel_payload,
    )
