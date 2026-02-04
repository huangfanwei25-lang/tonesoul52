from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Tuple

from .base import IPerspective
from .pre_output_council import PreOutputCouncil
from .types import CouncilVerdict, PerspectiveType
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
        )

        if role_result:
            verdict.transcript = self._attach_role_summary(verdict.transcript, role_result)
        try:
            provenance = ProvenanceManager()
            provenance.add_record(
                event_type="council_verdict",
                content=verdict.to_structured_output(),
                metadata={
                    "verdict": verdict.verdict.value,
                    "summary": verdict.summary,
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
