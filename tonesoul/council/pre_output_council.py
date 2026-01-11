from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .base import IPerspective
from .coherence import compute_coherence
from .types import CouncilVerdict, PerspectiveType
from .verdict import generate_verdict


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
        coherence_threshold: float = 0.6,
        block_threshold: float = 0.3,
        perspective_config: Optional[
            Dict[Union[PerspectiveType, str], Dict[str, Any]]
        ] = None,
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
        perspective_config: Optional[
            Dict[Union[PerspectiveType, str], Dict[str, Any]]
        ] = None,
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
        perspective_config: Optional[
            Dict[Union[PerspectiveType, str], Dict[str, Any]]
        ],
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
