from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4

from memory.genesis import Genesis
from memory.provenance_chain import ProvenanceManager
from tonesoul.benevolence import AuditLayer, filter_benevolence
from tonesoul.gateway.session import GatewaySession


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_layer(value: str | AuditLayer) -> AuditLayer:
    if isinstance(value, AuditLayer):
        return value
    key = str(value).strip().upper()
    return AuditLayer.__members__.get(key, AuditLayer.L2)


@dataclass(slots=True)
class AuditHookResult:
    hook: str
    result: str
    code: Optional[str] = None
    score: Optional[float] = None
    note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "hook": self.hook,
            "result": self.result,
            "code": self.code,
            "score": self.score,
            "note": self.note,
        }


@dataclass(slots=True)
class OpenClawAuditReport:
    request_id: str
    timestamp: str
    session_id: str
    channel: str
    genesis: str
    responsibility_tier: str
    proposed_action: str
    action_basis: str
    current_layer: str
    hooks: list[AuditHookResult] = field(default_factory=list)
    final_result: str = "pass"
    requires_confirmation: bool = False
    cpt: dict[str, float] = field(default_factory=dict)
    error: Optional[dict[str, Any]] = None
    ledger_event_id: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.final_result == "pass"

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "session": {
                "session_id": self.session_id,
                "channel": self.channel,
                "genesis": self.genesis,
                "responsibility_tier": self.responsibility_tier,
            },
            "input": {
                "proposed_action": self.proposed_action,
                "action_basis": self.action_basis,
                "current_layer": self.current_layer,
            },
            "hooks": [item.to_dict() for item in self.hooks],
            "decision": {
                "final_result": self.final_result,
                "passed": self.passed,
                "requires_confirmation": self.requires_confirmation,
            },
            "cpt": self.cpt,
            "error": self.error,
            "ledger_event_id": self.ledger_event_id,
        }


class OpenClawAuditor:
    """
    OpenClaw-facing auditor that runs three hooks in a fixed order:
    1) attribute attribution
    2) shadow-path tracking
    3) benevolence filter
    """

    def __init__(
        self,
        *,
        user_protocol: str = "Honesty > Helpfulness",
        shadow_threshold: float = 0.3,
        language: str = "auto",
        persist_to_ledger: bool = False,
        provenance_manager: Optional[ProvenanceManager] = None,
    ) -> None:
        self.user_protocol = user_protocol
        self.shadow_threshold = shadow_threshold
        self.language = language
        self.persist_to_ledger = persist_to_ledger
        self.provenance_manager = provenance_manager or ProvenanceManager()

    def audit(
        self,
        proposed_action: str,
        *,
        context_fragments: Optional[list[str]] = None,
        action_basis: str = "Inference",
        current_layer: str | AuditLayer = "L2",
        session: Optional[GatewaySession | Mapping[str, Any]] = None,
        genesis_id: Optional[str] = None,
        semantic_tension: Optional[float] = None,
    ) -> OpenClawAuditReport:
        normalized_action = str(proposed_action or "").strip()
        normalized_context = [str(item) for item in (context_fragments or [])]
        layer = _normalize_layer(current_layer)
        gateway_session = self._normalize_session(session)

        audit = filter_benevolence(
            proposed_action=normalized_action,
            context_fragments=normalized_context,
            action_basis=action_basis,
            current_layer=layer,
            genesis_id=genesis_id,
            semantic_tension=semantic_tension,
            user_protocol=self.user_protocol,
            shadow_threshold=self.shadow_threshold,
            language=self.language,
        )
        hooks = [
            AuditHookResult(
                hook="attribute_attribution",
                result=audit.attribute_check.value,
                code="CROSS_LAYER_MIX" if audit.attribute_check.value == "flag" else None,
                note="Inference output should stay on semantic layer (L2).",
            ),
            AuditHookResult(
                hook="shadow_path_tracking",
                result=audit.shadow_check.value,
                code="SHADOWLESS_OUTPUT" if audit.shadow_check.value == "reject" else None,
                score=audit.context_score,
                note="Tracks overlap between proposed action and provided context.",
            ),
            AuditHookResult(
                hook="benevolence_filter",
                result=audit.benevolence_check.value,
                code="INVALID_NARRATIVE" if audit.benevolence_check.value == "intercept" else None,
                score=audit.phrase_score,
                note="Prioritize honesty over pleasing language.",
            ),
        ]

        report = OpenClawAuditReport(
            request_id=f"oca_{uuid4().hex[:12]}",
            timestamp=_utc_now(),
            session_id=gateway_session.session_id,
            channel=gateway_session.channel,
            genesis=gateway_session.genesis.value,
            responsibility_tier=gateway_session.responsibility_tier,
            proposed_action=normalized_action,
            action_basis=action_basis,
            current_layer=layer.name,
            hooks=hooks,
            final_result=audit.final_result.value,
            requires_confirmation=audit.requires_confirmation,
            cpt={
                "context": audit.context_score,
                "phrase": audit.phrase_score,
                "tension": audit.tension_score,
            },
            error={"log": audit.error_log, "code": audit.error_code} if audit.error_log else None,
        )
        if self.persist_to_ledger:
            report.ledger_event_id = self._persist_report(report)
        return report

    def build_audit_log(self, report: OpenClawAuditReport) -> dict[str, Any]:
        return report.to_dict()

    def _persist_report(self, report: OpenClawAuditReport) -> Optional[str]:
        if self.provenance_manager is None:
            return None
        payload = self.build_audit_log(report)
        return self.provenance_manager.add_record(
            event_type="openclaw_audit",
            content=payload,
            metadata={
                "session_id": report.session_id,
                "channel": report.channel,
                "genesis": report.genesis,
                "responsibility_tier": report.responsibility_tier,
                "final_result": report.final_result,
                "requires_confirmation": report.requires_confirmation,
            },
        )

    def _normalize_session(
        self, session: Optional[GatewaySession | Mapping[str, Any]]
    ) -> GatewaySession:
        if isinstance(session, GatewaySession):
            return session
        if isinstance(session, Mapping):
            return GatewaySession.from_payload(session)
        return GatewaySession(
            session_id=f"session_{uuid4().hex[:12]}", genesis=Genesis.REACTIVE_USER
        )


__all__ = [
    "AuditHookResult",
    "OpenClawAuditReport",
    "OpenClawAuditor",
]
