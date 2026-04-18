"""Pre-output council: convene perspectives before a draft reaches the user."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from tonesoul.soul_config import SOUL

from .base import IPerspective
from .coherence import compute_coherence
from .self_journal import record_self_memory
from .summary_generator import (
    build_divergence_analysis,
    build_transcript,
    generate_human_summary,
    resolve_language,
)
from .types import CouncilVerdict, PerspectiveType
from .verdict import generate_verdict

__ts_layer__ = "governance"
__ts_purpose__ = "Convene the pre-output council: run perspectives, compute coherence, emit verdict and transcript."


class PreOutputCouncil:
    def __init__(
        self,
        perspectives: Optional[
            Union[
                IPerspective,
                List[Union[IPerspective, PerspectiveType, str]],
                Dict[Union[PerspectiveType, str], Dict[str, Any]],
                PerspectiveType,
                str,
            ]
        ] = None,
        coherence_threshold: float = SOUL.council.coherence_threshold,
        block_threshold: float = SOUL.council.block_threshold,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
    ):
        self.perspectives = self._normalize_perspectives(
            perspectives,
            perspective_config,
        )
        self.coherence_threshold = coherence_threshold
        self.block_threshold = block_threshold

    def validate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        auto_record_self_memory: bool = True,
    ) -> CouncilVerdict:
        votes = [
            perspective.evaluate(draft_output, context, user_intent)
            for perspective in self.perspectives
        ]

        # Apply evolved voting weights if available
        weights = None
        try:
            from tonesoul.council.evolution import CouncilEvolution

            if not hasattr(self, "_evolution"):
                self._evolution = CouncilEvolution()
            weights = self._evolution.get_weights()
        except Exception:
            pass

        coherence = compute_coherence(votes, weights=weights)
        verdict = generate_verdict(
            votes=votes,
            coherence=coherence,
            coherence_threshold=self.coherence_threshold,
            block_threshold=self.block_threshold,
        )
        language = resolve_language(context)
        divergence = build_divergence_analysis(votes, context=context)
        verdict.divergence_analysis = divergence
        verdict.human_summary = generate_human_summary(verdict, language=language)
        verdict.transcript = build_transcript(
            draft_output=draft_output,
            context=context,
            user_intent=user_intent,
            votes=votes,
            coherence=coherence,
            verdict=verdict,
            divergence=divergence,
        )
        # Selective self-memory: auto-record for meaningful decisions
        from .types import VerdictType

        record_option = context.get("record_self_memory")
        should_auto_record = verdict.verdict in (
            VerdictType.BLOCK,
            VerdictType.DECLARE_STANCE,
        )

        if auto_record_self_memory and (record_option or should_auto_record):
            path = record_option if isinstance(record_option, (str, bytes)) else None
            try:
                context["user_intent"] = user_intent
                record_self_memory(verdict, context=context, path=path)
            except OSError:
                pass
        return verdict

    def _default_perspectives(
        self,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        from .perspective_factory import PerspectiveFactory

        config = perspective_config or {}
        return PerspectiveFactory.create_council(config)

    def _normalize_perspectives(
        self,
        perspectives: Optional[
            Union[
                IPerspective,
                List[Union[IPerspective, PerspectiveType, str]],
                Dict[Union[PerspectiveType, str], Dict[str, Any]],
                PerspectiveType,
                str,
            ]
        ],
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]],
    ) -> List[IPerspective]:
        from .perspective_factory import PerspectiveFactory

        if perspectives is None:
            return self._default_perspectives(perspective_config)

        if not perspectives:
            return self._default_perspectives(perspective_config)

        if isinstance(perspectives, dict):
            return self._default_perspectives(perspectives)

        if isinstance(perspectives, IPerspective):
            return [perspectives]

        if isinstance(perspectives, (PerspectiveType, str)):
            return [PerspectiveFactory.create(name=perspectives)]

        resolved: List[IPerspective] = []
        for perspective in perspectives:
            if isinstance(perspective, IPerspective):
                resolved.append(perspective)
            else:
                resolved.append(PerspectiveFactory.create(name=perspective))
        return resolved
