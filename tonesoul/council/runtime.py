from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Tuple

from .base import IPerspective
from .pre_output_council import PreOutputCouncil
from .self_journal import record_self_memory
from .types import CouncilVerdict, PerspectiveType
from .verdict import apply_uncertainty
from .intent_reconstructor import infer_genesis
from ..role_council import build_council_summary
from memory.provenance_chain import ProvenanceManager


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

        from .types import VerdictType

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
            print(f"⚠️ Failed to append Isnād record: {exc}")
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
