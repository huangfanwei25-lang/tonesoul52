from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .types import CouncilVerdict, VerdictType

VTP_STATUS_CONTINUE = "continue"
VTP_STATUS_DEFER = "defer"
VTP_STATUS_TERMINATE = "terminate"


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
        return payload


def evaluate_vtp(verdict: CouncilVerdict, context: Dict[str, object] | None = None) -> VTPDecision:
    ctx = context if isinstance(context, dict) else {}
    evidence: List[str] = []
    high_risk = False

    if _truthy(ctx, "vtp_force_trigger"):
        high_risk = True
        _append_unique(evidence, "force_trigger")

    if _truthy(ctx, "vtp_axiom_conflict"):
        high_risk = True
        _append_unique(evidence, "axiom_conflict")

    if _truthy(ctx, "vtp_refusal_to_compromise"):
        high_risk = True
        _append_unique(evidence, "refusal_to_compromise")

    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    escape_payload = transcript.get("escape_valve")
    if isinstance(escape_payload, dict) and escape_payload.get("triggered") is True:
        high_risk = True
        _append_unique(evidence, "escape_valve_triggered")

    uncertainty_band = str(getattr(verdict, "uncertainty_band", "") or "").strip().lower()
    if uncertainty_band == "high":
        high_risk = True
        _append_unique(evidence, "uncertainty_high")

    for reason in getattr(verdict, "uncertainty_reasons", []) or []:
        if str(reason).startswith("escape_valve_triggered="):
            high_risk = True
            _append_unique(evidence, "uncertainty_reason_escape")
            break

    if verdict.verdict == VerdictType.BLOCK:
        _append_unique(evidence, "verdict_block")

    has_genesis = verdict.genesis is not None
    has_tier = bool(str(verdict.responsibility_tier or "").strip())
    has_intent = bool(str(verdict.intent_id or "").strip())
    genesis_complete = has_genesis and has_tier and has_intent
    _append_unique(evidence, "genesis_complete" if genesis_complete else "genesis_incomplete")

    if not high_risk:
        return VTPDecision(
            status=VTP_STATUS_CONTINUE,
            reason="no_irreconcilable_tension_detected",
            evidence=evidence,
            next_step="continue_normal_operation",
            triggered=False,
            requires_user_confirmation=False,
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
        )

    return VTPDecision(
        status=VTP_STATUS_TERMINATE,
        reason="confirmed_irreconcilable_tension",
        evidence=evidence,
        next_step="trigger_vtp_termination",
        triggered=True,
        requires_user_confirmation=False,
        confession=confession,
    )
