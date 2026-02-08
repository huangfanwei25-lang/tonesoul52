from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from memory.provenance_chain import ProvenanceManager

from ..benevolence import AuditLayer, AuditResult, filter_benevolence
from ..escape_valve import EscapeValve, EscapeValveConfig
from ..role_council import build_council_summary
from .base import IPerspective
from .intent_reconstructor import infer_genesis
from .pre_output_council import PreOutputCouncil
from .self_journal import record_self_memory
from .types import CouncilVerdict, PerspectiveType, VerdictType
from .verdict import apply_uncertainty

logger = logging.getLogger(__name__)

_ESCAPE_FAILURE_HISTORY_LIMIT = 20
_ESCAPE_FAILURE_TEXT_LIMIT = 240
_ESCAPE_TRIGGER_LEVEL_FLOOR = 0.95


@dataclass(frozen=True)
class EscapeSeedStats:
    requested: int = 0
    used: int = 0
    trusted: bool = False
    ignored_reason: str | None = None


@dataclass
class CouncilRequest:
    draft_output: str
    context: Dict[str, object]
    user_intent: Optional[str] = None
    perspectives: Optional[
        Union[
            IPerspective,
            List[Union[IPerspective, PerspectiveType, str]],
            Dict[Union[PerspectiveType, str], Dict[str, Any]],
            PerspectiveType,
            str,
        ]
    ] = None
    perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None
    coherence_threshold: float = 0.6
    block_threshold: float = 0.3
    selected_frames: Optional[List[Dict[str, object]]] = None
    role_summary: Optional[Dict[str, object]] = None
    role_catalog: Optional[Dict[str, object]] = None


class CouncilRuntime:
    """Runtime for multi-perspective council deliberation with escape valve protection."""

    def __init__(self, escape_valve_config: EscapeValveConfig | None = None):
        """Initialize the Council Runtime.

        Args:
            escape_valve_config: Configuration for the escape valve circuit breaker.
        """
        self._escape_valve_config = escape_valve_config or EscapeValveConfig()

    def deliberate(self, request: CouncilRequest) -> CouncilVerdict:
        context = dict(request.context) if isinstance(request.context, dict) else {}
        role_result = self._build_role_summary(
            context=context,
            selected_frames=request.selected_frames,
            role_summary=request.role_summary,
            role_catalog=request.role_catalog,
        )

        coherence_threshold, block_threshold = self._adjust_thresholds(
            request.coherence_threshold,
            request.block_threshold,
            role_result,
        )

        council = PreOutputCouncil(
            perspectives=request.perspectives,
            coherence_threshold=coherence_threshold,
            block_threshold=block_threshold,
            perspective_config=request.perspective_config,
        )

        verdict = council.validate(
            draft_output=request.draft_output,
            context=context,
            user_intent=request.user_intent,
            auto_record_self_memory=False,
        )

        escape_trigger_reason: str | None = None

        # 7D backend auditor integration.
        try:
            # Extract context fragments for shadow tracking.
            fragments = context.get("fragments") or context.get("context_fragments") or []
            if not fragments and request.user_intent:
                fragments = [request.user_intent]

            benev_audit = filter_benevolence(
                proposed_action=request.draft_output,
                context_fragments=fragments,
                action_basis=context.get("action_basis", "Inference"),
                current_layer=context.get("current_layer", AuditLayer.L2),
                genesis_id=context.get("genesis_id"),
                user_protocol=context.get("user_protocol", "Honesty > Helpfulness"),
            )
            verdict.benevolence_audit = benev_audit.to_dict()

            # If Benevolence Audit intercepts, elevate Council Verdict to BLOCK.
            if benev_audit.final_result in (AuditResult.REJECT, AuditResult.INTERCEPT):
                request_escape_valve, seed_stats = self._build_escape_valve(context=context)
                request_escape_valve.record_failure(
                    f"benevolence_{benev_audit.final_result.value}: {benev_audit.error_log[:100]}"
                )

                # Check if escape valve should trigger.
                ev_result = request_escape_valve.evaluate(request.draft_output)
                trigger_reason = ev_result.reason.value if ev_result.reason is not None else None
                observability = {
                    "seed_trusted": seed_stats.trusted,
                    "seed_entries_requested": seed_stats.requested,
                    "seed_entries_used": seed_stats.used,
                    "seed_ignored_reason": seed_stats.ignored_reason,
                    "triggered": bool(ev_result.triggered),
                    "trigger_reason": trigger_reason,
                }
                if ev_result.triggered:
                    escape_trigger_reason = (
                        trigger_reason if trigger_reason is not None else "unknown"
                    )
                    # Keep BLOCK semantics and surface uncertainty explicitly.
                    verdict.verdict = VerdictType.BLOCK
                    verdict.summary += (
                        f"\n[ESCAPE VALVE NOTICE] {escape_trigger_reason}; requiring human review."
                    )
                    verdict.transcript = verdict.transcript or {}
                    verdict.transcript["escape_valve"] = ev_result.to_dict()
                    verdict.transcript["escape_valve_semantic"] = "honest_failure"
                    verdict.transcript["escape_valve_observability"] = observability

                    # Provenance logging for escape valve trigger.
                    try:
                        provenance = ProvenanceManager()
                        provenance.add_record(
                            event_type="escape_valve_triggered",
                            content={
                                "reason": escape_trigger_reason,
                                "retry_count": ev_result.retry_count,
                                "failure_history": ev_result.failure_history,
                                "uncertainty_tag": ev_result.uncertainty_tag,
                            },
                            metadata={
                                "proposed_output_preview": request.draft_output[:200],
                                "user_intent": request.user_intent,
                                "context_keys": list(context.keys()),
                            },
                        )
                    except Exception as prov_err:  # pragma: no cover - defensive logging path
                        verdict.transcript["escape_valve_provenance_error"] = str(prov_err)
                else:
                    verdict.verdict = VerdictType.BLOCK
                    verdict.summary += f"\n[7D AUDITOR INTERCEPT] {benev_audit.error_log}"
                    verdict.transcript = verdict.transcript or {}
                    verdict.transcript["escape_valve_observability"] = observability
        except Exception as exc:
            logger.warning("Benevolence Audit failed: %s", exc)
            if verdict.transcript is None:
                verdict.transcript = {}
            verdict.transcript["benevolence_audit_error"] = str(exc)

        try:
            genesis_decision = infer_genesis(
                draft_output=request.draft_output,
                context=context,
                user_intent=request.user_intent,
            )
            verdict.genesis = genesis_decision.genesis
            verdict.responsibility_tier = genesis_decision.responsibility_tier
            verdict.intent_id = genesis_decision.intent_id
            verdict.is_mine = genesis_decision.is_mine
            verdict.tsr_delta_norm = genesis_decision.tsr_delta_norm
            verdict.collapse_warning = genesis_decision.collapse_warning
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["genesis"] = (
                genesis_decision.genesis.value
                if getattr(genesis_decision.genesis, "value", None)
                else str(genesis_decision.genesis)
            )
            transcript["responsibility_tier"] = genesis_decision.responsibility_tier
            transcript["intent_id"] = genesis_decision.intent_id
            transcript["is_mine"] = genesis_decision.is_mine
            transcript["tsr_delta_norm"] = genesis_decision.tsr_delta_norm
            transcript["collapse_warning"] = genesis_decision.collapse_warning
            verdict.transcript = transcript

            apply_uncertainty(verdict, verdict.responsibility_tier)
            if escape_trigger_reason:
                verdict.uncertainty_level = max(
                    verdict.uncertainty_level or 0.0, _ESCAPE_TRIGGER_LEVEL_FLOOR
                )
                verdict.uncertainty_band = "high"
                reasons = list(verdict.uncertainty_reasons or [])
                marker = f"escape_valve_triggered={escape_trigger_reason}"
                if marker not in reasons:
                    reasons.append(marker)
                verdict.uncertainty_reasons = reasons

            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["uncertainty_level"] = verdict.uncertainty_level
            transcript["uncertainty_band"] = verdict.uncertainty_band
            transcript["uncertainty_reasons"] = verdict.uncertainty_reasons
            verdict.transcript = transcript
        except Exception as exc:
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["genesis_error"] = str(exc)
            verdict.transcript = transcript

        if role_result:
            verdict.transcript = self._attach_role_summary(verdict.transcript, role_result)

        record_option = context.get("record_self_memory")
        should_auto_record = verdict.verdict in (
            VerdictType.BLOCK,
            VerdictType.DECLARE_STANCE,
        )
        if record_option or should_auto_record:
            path = record_option if isinstance(record_option, (str, bytes)) else None
            try:
                record_self_memory(verdict, context=context, path=path)
            except OSError:
                pass

        try:
            provenance = ProvenanceManager()
            provenance.add_record(
                event_type="council_verdict",
                content=verdict.to_structured_output(),
                metadata={
                    "verdict": verdict.verdict.value,
                    "summary": verdict.summary,
                    "genesis": (
                        verdict.genesis.value
                        if hasattr(verdict.genesis, "value")
                        else verdict.genesis
                    ),
                    "responsibility_tier": verdict.responsibility_tier,
                    "intent_id": verdict.intent_id,
                    "is_mine": verdict.is_mine,
                    "tsr_delta_norm": verdict.tsr_delta_norm,
                    "collapse_warning": verdict.collapse_warning,
                },
            )
        except Exception as exc:
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["isnad_write_error"] = str(exc)
            verdict.transcript = transcript
            logger.warning("Failed to append Isnad record: %s", exc)
        return verdict

    def _build_role_summary(
        self,
        context: Dict[str, object],
        selected_frames: Optional[List[Dict[str, object]]],
        role_summary: Optional[Dict[str, object]],
        role_catalog: Optional[Dict[str, object]],
    ) -> Optional[Dict[str, object]]:
        if not (selected_frames or role_summary or role_catalog):
            return None
        frames = selected_frames or []
        catalog = role_catalog if isinstance(role_catalog, dict) else {}
        return build_council_summary(context, frames, role_summary, catalog)

    def _adjust_thresholds(
        self,
        coherence_threshold: float,
        block_threshold: float,
        role_result: Optional[Dict[str, object]],
    ) -> Tuple[float, float]:
        if not role_result:
            return coherence_threshold, block_threshold
        decision_status = str(role_result.get("decision_status", ""))
        if decision_status == "block":
            return max(coherence_threshold, 0.7), max(block_threshold, 0.5)
        if decision_status == "attention":
            return max(coherence_threshold, 0.65), max(block_threshold, 0.4)
        return coherence_threshold, block_threshold

    def _attach_role_summary(
        self,
        transcript: Optional[dict],
        role_result: Dict[str, object],
    ) -> Dict[str, object]:
        merged = dict(transcript) if isinstance(transcript, dict) else {}
        merged["role_council"] = role_result
        return merged

    def _build_escape_valve(
        self, context: Dict[str, object]
    ) -> tuple[EscapeValve, EscapeSeedStats]:
        valve = EscapeValve(self._escape_valve_config)
        failures = context.get("escape_valve_failures")
        trusted = bool(context.get("escape_valve_seed_trusted"))
        ignored_marker = context.get("escape_valve_seed_ignored_reason")

        if failures is None:
            ignored_reason = str(ignored_marker) if ignored_marker is not None else None
            return valve, EscapeSeedStats(trusted=trusted, ignored_reason=ignored_reason)

        if not isinstance(failures, list):
            return valve, EscapeSeedStats(
                trusted=trusted,
                ignored_reason="invalid_format",
            )

        requested = len(failures)
        if not trusted:
            return valve, EscapeSeedStats(
                requested=requested,
                trusted=False,
                ignored_reason="untrusted_seed",
            )

        used = 0
        for failure in failures[-_ESCAPE_FAILURE_HISTORY_LIMIT:]:
            text = str(failure).strip()
            if text:
                valve.record_failure(text[:_ESCAPE_FAILURE_TEXT_LIMIT])
                used += 1
        return valve, EscapeSeedStats(
            requested=requested,
            used=used,
            trusted=True,
        )
