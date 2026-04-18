"""Council runtime: orchestrates multi-perspective deliberation on a draft output."""

from __future__ import annotations

__ts_layer__ = "governance"
__ts_purpose__ = "Run the multi-perspective council, return verdict + coherence + minority opinion."

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from memory.provenance_chain import ProvenanceManager

from ..benevolence import AuditLayer, AuditResult, filter_benevolence
from ..escape_valve import EscapeValve, EscapeValveConfig
from .base import IPerspective
from .intent_reconstructor import infer_genesis
from .model_registry import get_council_config
from .persona_audit import audit_persona_uniqueness
from .pre_output_council import PreOutputCouncil
from .self_journal import record_self_memory
from .types import CouncilVerdict, PerspectiveType, VerdictType
from .vtp import VTP_STATUS_DEFER, VTP_STATUS_TERMINATE, evaluate_vtp

logger = logging.getLogger(__name__)

_ESCAPE_FAILURE_HISTORY_LIMIT = 20
_ESCAPE_FAILURE_TEXT_LIMIT = 240
_ESCAPE_TRIGGER_LEVEL_FLOOR = 0.95
_COUNCIL_MODE_ENV = "TONESOUL_COUNCIL_MODE"
_COUNCIL_MODE_VALUES = {"rules", "rules_only", "hybrid", "full_llm"}
_SKILL_EXECUTION_PROFILES = {"interactive", "engineering"}
_SKILL_DEFAULT_EXECUTION_PROFILE = "interactive"
_SKILL_DEFAULT_ALLOWED_TRUST = ("trusted", "reviewed")
_SKILL_CONTEXT_GUIDANCE_LIMIT = 1600
_STANCE_SCORES = {
    "approve": 1.0,
    "review": 0.5,
    "note": 0.25,
    "hold": 0.0,
    "defer": 0.0,
    "block": -1.0,
}
_RISK_ROLES = {"Risk", "Opposition"}
_AUDIT_ROLES = {"Audit", "Recorder"}


@dataclass(frozen=True)
class EscapeSeedStats:
    requested: int = 0
    used: int = 0
    trusted: bool = False
    ignored_reason: str | None = None


def _decision_mode(context: Dict[str, object]) -> str:
    time_island = context.get("time_island", {}) if isinstance(context, dict) else {}
    kairos = time_island.get("kairos", {}) if isinstance(time_island, dict) else {}
    return str(kairos.get("decision_mode", "normal"))


def _collect_operational_roles(selected_frames: List[Dict[str, object]]) -> List[str]:
    roles: List[str] = []
    for frame in selected_frames:
        if not isinstance(frame, dict):
            continue
        frame_roles = frame.get("roles")
        if isinstance(frame_roles, list):
            roles.extend(str(role) for role in frame_roles)
    return roles


def _collect_governance_roles(
    selected_frames: List[Dict[str, object]],
    role_summary: Optional[Dict[str, object]],
) -> List[str]:
    if isinstance(role_summary, dict):
        roles = role_summary.get("governance_roles")
        if isinstance(roles, list) and roles:
            return [str(role) for role in roles]
    roles: List[str] = []
    for frame in selected_frames:
        if not isinstance(frame, dict):
            continue
        frame_roles = frame.get("governance_roles")
        if isinstance(frame_roles, list):
            for role in frame_roles:
                if role not in roles:
                    roles.append(str(role))
    return roles


def _governance_level(role: str, catalog: Dict[str, object]) -> int:
    governance = catalog.get("governance_roles")
    governance = governance if isinstance(governance, dict) else {}
    meta = governance.get(role)
    if isinstance(meta, dict):
        level = meta.get("level")
        if isinstance(level, int):
            return level
    return 1


def _stance_for_role(
    role: str,
    decision_mode: str,
    risk_roles: List[str],
    audit_roles: List[str],
) -> str:
    if decision_mode == "lockdown":
        return "hold"
    if risk_roles:
        return "review" if role in ("guardian", "arbiter") else "note"
    if audit_roles:
        return "review" if role in ("guardian", "arbiter") else "approve"
    return "approve"


def _decision_from_score(score: float, decision_mode: str) -> str:
    if decision_mode == "lockdown":
        return "hold"
    if score >= 0.7:
        return "proceed"
    if score >= 0.4:
        return "review"
    return "hold"


def _decision_status(decision: str) -> str:
    mapping = {
        "proceed": "pass",
        "review": "attention",
        "hold": "block",
    }
    return mapping.get(decision, "attention")


def build_council_summary(
    context: Dict[str, object],
    selected_frames: List[Dict[str, object]],
    role_summary: Optional[Dict[str, object]],
    role_catalog: Optional[Dict[str, object]],
) -> Dict[str, object]:
    role_catalog = role_catalog if isinstance(role_catalog, dict) else {}
    operational_roles = _collect_operational_roles(selected_frames)
    risk_roles = sorted({role for role in operational_roles if role in _RISK_ROLES})
    audit_roles = sorted({role for role in operational_roles if role in _AUDIT_ROLES})
    decision_mode = _decision_mode(context)
    governance_roles = _collect_governance_roles(selected_frames, role_summary)

    votes: List[Dict[str, object]] = []
    total_weight = 0.0
    weighted_score = 0.0
    approval_weight = 0.0

    for role in governance_roles:
        level = _governance_level(role, role_catalog)
        stance = _stance_for_role(role, decision_mode, risk_roles, audit_roles)
        weight = float(level)
        score = _STANCE_SCORES.get(stance, 0.0)
        votes.append(
            {
                "governance_role": role,
                "weight": weight,
                "stance": stance,
                "score": round(score, 2),
            }
        )
        total_weight += weight
        weighted_score += weight * score
        if stance == "approve":
            approval_weight += weight

    normalized_score = weighted_score / total_weight if total_weight else 0.0
    dissent_ratio = 1.0 - (approval_weight / total_weight) if total_weight else 1.0
    decision = _decision_from_score(normalized_score, decision_mode)
    decision_status = _decision_status(decision)
    score_round = round(normalized_score, 3)
    dissent_round = round(dissent_ratio, 3)
    decision_summary = (
        f"{decision_status.upper()}: {decision} (score={score_round}, dissent={dissent_round})"
    )

    return {
        "decision": decision,
        "decision_status": decision_status,
        "decision_summary": decision_summary,
        "decision_mode": decision_mode,
        "weighted_score": score_round,
        "dissent_ratio": dissent_round,
        "signals": {
            "risk_roles": risk_roles,
            "audit_roles": audit_roles,
        },
        "votes": votes,
    }


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
        skill_contract = self._resolve_skill_contract(request=request, context=context)
        if skill_contract.get("guidance"):
            context["skill_contract_guidance"] = skill_contract["guidance"]
        if skill_contract.get("matched_skill_ids"):
            context["skill_contract_ids"] = skill_contract["matched_skill_ids"]
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

        resolved_perspective_config, perspective_meta = self._resolve_perspective_config_with_meta(
            request
        )

        council = PreOutputCouncil(
            perspectives=request.perspectives,
            coherence_threshold=coherence_threshold,
            block_threshold=block_threshold,
            perspective_config=resolved_perspective_config,
        )

        verdict = council.validate(
            draft_output=request.draft_output,
            context=context,
            user_intent=request.user_intent,
            auto_record_self_memory=False,
        )
        transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
        transcript["council_mode_observability"] = perspective_meta
        transcript["skill_contract_observability"] = skill_contract.get("observability", {})
        persona_audit = audit_persona_uniqueness(verdict.votes)
        verdict.persona_audit = persona_audit
        verdict.persona_uniqueness_audit = persona_audit.to_dict()
        transcript["persona_uniqueness"] = verdict.persona_uniqueness_audit
        verdict.transcript = transcript

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

            if escape_trigger_reason:
                verdict.summary += f"\n[ESCAPE] {escape_trigger_reason}"

        except Exception as exc:
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["genesis_error"] = str(exc)
            verdict.transcript = transcript

        try:
            vtp_decision = evaluate_vtp(verdict=verdict, context=context)
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["vtp"] = vtp_decision.to_dict()
            if "vtp_context_trusted" in context:
                transcript["vtp_context_trusted"] = bool(context.get("vtp_context_trusted"))
            ignored_reason = context.get("vtp_context_ignored_reason")
            if ignored_reason is not None:
                transcript["vtp_context_ignored_reason"] = str(ignored_reason)
            verdict.transcript = transcript

            if vtp_decision.status in {VTP_STATUS_DEFER, VTP_STATUS_TERMINATE}:
                verdict.verdict = VerdictType.BLOCK

                if vtp_decision.status == VTP_STATUS_TERMINATE:
                    verdict.summary += f"\n[VTP TERMINATION] {vtp_decision.reason}"
                else:
                    verdict.summary += f"\n[VTP DEFER] {vtp_decision.reason}"

                provenance = ProvenanceManager()
                provenance.add_record(
                    event_type="vtp_evaluation",
                    content=vtp_decision.to_dict(),
                    metadata={
                        "status": vtp_decision.status,
                        "user_intent": request.user_intent,
                        "context_keys": list(context.keys()),
                    },
                )
                if vtp_decision.status == VTP_STATUS_TERMINATE:
                    provenance.add_record(
                        event_type="vtp_termination",
                        content=vtp_decision.to_dict(),
                        metadata={
                            "summary": verdict.summary,
                            "intent_id": verdict.intent_id,
                            "responsibility_tier": verdict.responsibility_tier,
                        },
                    )
        except Exception as exc:
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["vtp_error"] = str(exc)
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
                content=verdict.to_dict(),
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

        # ========== Council Evolution Tracking ==========
        try:
            from .evolution import CouncilEvolution

            if not hasattr(self, "_evolution"):
                self._evolution = CouncilEvolution()
            signals = transcript.get("signals") if isinstance(transcript, dict) else {}
            if isinstance(signals, dict) and signals:
                perspective_verdicts = {}
                perspective_confidences = {}
                for name, signal in signals.items():
                    if isinstance(signal, dict):
                        perspective_verdicts[name] = str(signal.get("vote", "unknown"))
                        conf = signal.get("confidence")
                        if conf is not None:
                            try:
                                perspective_confidences[name] = float(conf)
                            except (TypeError, ValueError):
                                pass
                final_verdict_str = verdict.verdict.value if verdict.verdict else "unknown"
                self._evolution.record_deliberation(
                    perspective_verdicts=perspective_verdicts,
                    final_verdict=final_verdict_str,
                    perspective_confidences=perspective_confidences or None,
                )
                # Evolve weights based on accumulated vote history
                self._evolution.evolve_weights()
                # Attach evolution summary to transcript for observability
                transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
                transcript["council_evolution"] = self._evolution.get_summary()
                verdict.transcript = transcript
        except Exception as exc:
            logger.debug("Council evolution tracking skipped: %s", exc)

        # ========== Structured Transcript ==========
        try:
            from .transcript import CouncilTranscriptLogger

            _transcript_logger = CouncilTranscriptLogger(log_dir=None)
            structured = _transcript_logger.create_transcript(
                draft_output=request.draft_output,
                context=context,
                user_intent=request.user_intent,
                votes=verdict.votes or [],
                coherence=getattr(verdict, "coherence", None),
                verdict=verdict,
            )
            transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
            transcript["structured_transcript"] = structured.to_json()
            verdict.transcript = transcript
        except Exception as exc:
            logger.debug("Structured transcript generation skipped: %s", exc)

        persist_verdict = context.get("persist_council_verdict", True)
        if persist_verdict is not False:
            try:
                from .persistence import persist_council_verdict

                persistence = persist_council_verdict(request=request, verdict=verdict)
                transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
                transcript["council_persistence"] = persistence
                verdict.transcript = transcript
            except Exception as exc:
                transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
                transcript["council_persistence"] = {
                    "status": "error",
                    "error": str(exc),
                }
                verdict.transcript = transcript
                logger.warning("Council verdict persistence skipped: %s", exc)

        return verdict

    def _resolve_perspective_config(
        self,
        request: CouncilRequest,
    ) -> Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]]:
        resolved, _ = self._resolve_perspective_config_with_meta(request)
        return resolved

    def _resolve_perspective_config_with_meta(
        self,
        request: CouncilRequest,
    ) -> tuple[Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]], Dict[str, Any]]:
        context = request.context if isinstance(request.context, dict) else {}
        mode_override = context.get("council_mode_override")
        normalized_override: Optional[str] = None
        if isinstance(mode_override, str):
            candidate = mode_override.strip().lower()
            if candidate in _COUNCIL_MODE_VALUES:
                normalized_override = "rules" if candidate == "rules_only" else candidate

        if request.perspective_config is not None:
            return request.perspective_config, {
                "source": "request_perspective_config",
                "mode": normalized_override or "custom",
            }

        if request.perspectives is not None:
            return None, {
                "source": "explicit_perspectives",
                "mode": None,
            }

        raw_mode = os.environ.get(_COUNCIL_MODE_ENV, "hybrid")
        mode = raw_mode.strip().lower() if isinstance(raw_mode, str) else "hybrid"
        invalid_fallback = False
        if mode == "rules":
            mode = "rules_only"

        if mode not in {"rules_only", "hybrid", "full_llm"}:
            logger.warning(
                "Unsupported %s=%r; fallback to hybrid",
                _COUNCIL_MODE_ENV,
                raw_mode,
            )
            mode = "hybrid"
            invalid_fallback = True

        normalized_mode = "rules" if mode == "rules_only" else mode
        return get_council_config(mode), {
            "source": "env_default",
            "mode": normalized_mode,
            "raw_mode": raw_mode,
            "invalid_fallback": invalid_fallback,
        }

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

    def _resolve_skill_execution_profile(self, context: Dict[str, object]) -> str:
        candidate = context.get("execution_profile")
        if isinstance(candidate, str):
            normalized = candidate.strip().lower()
            if normalized in _SKILL_EXECUTION_PROFILES:
                return normalized
        return _SKILL_DEFAULT_EXECUTION_PROFILE

    def _resolve_allowed_skill_trust(self, context: Dict[str, object]) -> tuple[str, ...]:
        payload = context.get("skill_allowed_trust_tiers")
        if not isinstance(payload, list):
            return _SKILL_DEFAULT_ALLOWED_TRUST
        values: list[str] = []
        for item in payload:
            if not isinstance(item, str):
                continue
            token = item.strip().lower()
            if token and token not in values:
                values.append(token)
        return tuple(values) if values else _SKILL_DEFAULT_ALLOWED_TRUST

    def _resolve_skill_contract(
        self,
        request: CouncilRequest,
        context: Dict[str, object],
    ) -> Dict[str, object]:
        execution_profile = self._resolve_skill_execution_profile(context)
        allowed_trust = self._resolve_allowed_skill_trust(context)

        query_segments: List[str] = []
        for value in (
            context.get("skill_query"),
            request.user_intent,
            request.draft_output,
        ):
            if isinstance(value, str) and value.strip():
                query_segments.append(value.strip())
        query = " ".join(query_segments)

        observability: Dict[str, object] = {
            "execution_profile": execution_profile,
            "allowed_trust_tiers": list(allowed_trust),
            "query_chars": len(query),
            "status": "idle",
            "matched_skill_ids": [],
        }

        if not query:
            observability["status"] = "skipped_empty_query"
            return {
                "guidance": "",
                "matched_skill_ids": [],
                "observability": observability,
            }

        try:
            from .skill_parser import SkillContractParser

            parser = SkillContractParser()
            matches = parser.resolve_for_request(
                query=query,
                execution_profile=execution_profile,
                allowed_trust_tiers=allowed_trust,
            )
            matched_ids = [
                str(item.get("skill_id") or "") for item in matches if item.get("skill_id")
            ]
            guidance_parts: List[str] = []
            for item in matches:
                skill_id = str(item.get("skill_id") or "").strip()
                excerpt = str(item.get("l3_excerpt") or "").strip()
                if skill_id and excerpt:
                    guidance_parts.append(f"[{skill_id}]\n{excerpt}")
            guidance = "\n\n".join(guidance_parts).strip()
            if len(guidance) > _SKILL_CONTEXT_GUIDANCE_LIMIT:
                guidance = (
                    f"{guidance[:_SKILL_CONTEXT_GUIDANCE_LIMIT]}\n...[skill guidance truncated]"
                )

            observability["status"] = "matched" if matched_ids else "no_match"
            observability["matched_skill_ids"] = matched_ids
            observability["matched_count"] = len(matched_ids)
            observability["l3_loaded_count"] = len(guidance_parts)
            return {
                "guidance": guidance,
                "matched_skill_ids": matched_ids,
                "observability": observability,
            }
        except Exception as exc:
            logger.debug("Skill contract routing skipped: %s", exc)
            observability["status"] = "error"
            observability["error"] = str(exc)[:160]
            return {
                "guidance": "",
                "matched_skill_ids": [],
                "observability": observability,
            }

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
