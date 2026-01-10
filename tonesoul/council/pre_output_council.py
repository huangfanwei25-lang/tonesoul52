from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import IPerspective
from .coherence import compute_coherence
from .types import CouncilVerdict
from .verdict import generate_verdict


class PreOutputCouncil:
    def __init__(
        self,
        perspectives: Optional[List[IPerspective]] = None,
        coherence_threshold: float = 0.6,
        block_threshold: float = 0.3,
        perspective_config: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.perspectives = perspectives or self._default_perspectives(
            perspective_config
        )
        self.coherence_threshold = coherence_threshold
        self.block_threshold = block_threshold

    def validate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> CouncilVerdict:
        votes = [
            perspective.evaluate(draft_output, context, user_intent)
            for perspective in self.perspectives
        ]
        coherence = compute_coherence(votes)
        return generate_verdict(
            votes=votes,
            coherence=coherence,
            coherence_threshold=self.coherence_threshold,
            block_threshold=self.block_threshold,
        )

    def _default_perspectives(
        self,
        perspective_config: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        from .perspective_factory import PerspectiveFactory

        config = perspective_config or {}
        return PerspectiveFactory.create_council(config)
