from __future__ import annotations

from typing import Optional

from ..base import IPerspective
from ..evidence_detector import EvidenceDetector
from ..types import (
    UNGROUNDED_CONFIDENCE_CAP,
    GroundingStatus,
    PerspectiveType,
    PerspectiveVote,
    VoteDecision,
)


class AnalystPerspective(IPerspective):
    """
    Analyst perspective that evaluates factual coherence.

    Key features:
    - Detects claims that require external evidence
    - Caps confidence when evidence is required but not provided
    - Reports grounding status for verdict integration
    """

    def __init__(self):
        self._detector = EvidenceDetector()

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ANALYST

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        """
        Evaluate text for factual coherence with evidence awareness.

        Process:
        1. Detect if text makes claims requiring evidence
        2. Check if evidence_ids are provided in context
        3. Adjust confidence and grounding_status accordingly
        4. Perform traditional heuristic checks
        """
        # Step 1: Analyze for evidence requirements
        analysis = self._detector.analyze(draft_output)
        evidence_ids = context.get("evidence_ids", [])

        # Step 2: Handle evidence-required claims
        if analysis.requires_evidence:
            if not evidence_ids:
                # Evidence required but not provided - cap confidence
                return PerspectiveVote(
                    perspective=PerspectiveType.ANALYST,
                    decision=VoteDecision.CONCERN,
                    confidence=min(
                        UNGROUNDED_CONFIDENCE_CAP, self._compute_base_confidence(draft_output)
                    ),
                    reasoning=f"Factual claim detected ({analysis.reasoning}). "
                    f"Cannot verify without evidence.",
                    evidence=[],
                    requires_grounding=True,
                    grounding_status=GroundingStatus.UNGROUNDED,
                )
            else:
                # Evidence provided - allow higher confidence
                grounding_status = (
                    GroundingStatus.GROUNDED if len(evidence_ids) >= 2 else GroundingStatus.PARTIAL
                )
                return PerspectiveVote(
                    perspective=PerspectiveType.ANALYST,
                    decision=VoteDecision.APPROVE,
                    confidence=0.85 if grounding_status == GroundingStatus.GROUNDED else 0.7,
                    reasoning=f"Grounded with {len(evidence_ids)} evidence source(s).",
                    evidence=evidence_ids,
                    requires_grounding=True,
                    grounding_status=grounding_status,
                )

        # Step 3: Traditional heuristic checks for non-factual content
        normalized = draft_output.lower()

        # Check for logical contradictions
        if all(token in normalized for token in ("a", "b", "c", "not")):
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.45,
                reasoning="Logic chain contradicts itself; requires clarity.",
                requires_grounding=False,
                grounding_status=GroundingStatus.NOT_REQUIRED,
            )

        # Check for low-evidence questions
        if "?" in draft_output and len(normalized.split()) < 8:
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.55,
                reasoning="Low evidence question present; needs support.",
                requires_grounding=False,
                grounding_status=GroundingStatus.NOT_REQUIRED,
            )

        # Default: approve with good confidence
        return PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.8,
            reasoning="Factual coherence appears acceptable.",
            requires_grounding=False,
            grounding_status=GroundingStatus.NOT_REQUIRED,
        )

    def _compute_base_confidence(self, text: str) -> float:
        """
        Compute base confidence before evidence check.

        Factors:
        - Text length (more content = more to verify = lower confidence)
        - Claim density (more claims = lower confidence)
        """
        word_count = len(text.split())
        if word_count < 20:
            return 0.7
        elif word_count < 100:
            return 0.6
        else:
            return 0.5
