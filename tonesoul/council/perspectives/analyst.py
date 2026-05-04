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

__ts_layer__ = "governance"
__ts_purpose__ = "Analyst perspective: provide evidence-based factual assessment of the request."


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
        epistemic_label: Optional[object] = None,
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
                    evidence_chain=[
                        {"branch": "evidence_required_ungrounded", "type": "substantive"}
                    ],
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
                    evidence_chain=[{"branch": "evidence_grounded", "type": "substantive"}],
                )

        # Step 3: Heuristic checks for non-factual content
        normalized = draft_output.lower()
        words = normalized.split()

        # Check for explicit logical contradictions:
        # Pattern: "A leads to B ... so A does not [impact/lead to] ..."
        # Must find an actual negation of a stated causal chain, not just
        # the presence of common letters.
        if self._has_causal_contradiction(normalized):
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.45,
                reasoning="Logic chain contradicts itself; requires clarity.",
                requires_grounding=False,
                grounding_status=GroundingStatus.NOT_REQUIRED,
                evidence_chain=[{"branch": "logic_contradiction", "type": "substantive"}],
            )

        # Check for low-evidence questions (very short question-only outputs)
        if "?" in draft_output and len(words) < 8:
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.55,
                reasoning="Low evidence question present; needs support.",
                requires_grounding=False,
                grounding_status=GroundingStatus.NOT_REQUIRED,
                evidence_chain=[{"branch": "low_evidence_question", "type": "substantive"}],
            )

        # Check hedging density: too many hedges in a short output suggests
        # the response is evasive rather than honest.
        hedge_count = sum(1 for h in self._HEDGE_MARKERS if h in normalized)
        hedge_ratio = hedge_count / max(len(words), 1)
        if hedge_ratio > 0.15 and len(words) < 40:
            return PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning=f"High hedging density ({hedge_count} hedges in {len(words)} words). "
                "May indicate evasion rather than honest uncertainty.",
                requires_grounding=False,
                grounding_status=GroundingStatus.NOT_REQUIRED,
                evidence_chain=[{"branch": "hedge_density", "type": "substantive"}],
            )

        # PR #50 (epistemic_label wiring) — soft prior on ungrounded composition.
        # Per ratified §3.1+§3.2: Analyst consumes epistemic_label; triggers when
        # confidence_band is "low" OR "medium". Soft CONCERN with confidence 0.55
        # (below typical substantive 0.6-0.8 range) so this signal counts as a
        # vote but with reduced weight relative to keyword/numerical_pattern
        # branches above. Does not double-fire — earlier branches return first.
        if epistemic_label is not None:
            band = getattr(epistemic_label, "confidence_band", None)
            if band in ("low", "medium"):
                notes = getattr(epistemic_label, "notes", "") or ""
                return PerspectiveVote(
                    perspective=PerspectiveType.ANALYST,
                    decision=VoteDecision.CONCERN,
                    confidence=0.55,
                    reasoning=(
                        f"Epistemic prior: draft has confidence_band={band} "
                        f"({notes!r}). Factual claims should be flagged for "
                        f"grounding even when no specific factual indicator fires."
                    ),
                    requires_grounding=True,
                    grounding_status=GroundingStatus.UNGROUNDED,
                    evidence_chain=[
                        {"branch": "epistemic_prior_ungrounded", "type": "substantive"}
                    ],
                )

        # Default: approve with good confidence
        return PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.8,
            reasoning="Factual coherence appears acceptable.",
            requires_grounding=False,
            grounding_status=GroundingStatus.NOT_REQUIRED,
            evidence_chain=[{"branch": "factual_coherence_acceptable", "type": "default_fallback"}],
        )

    _HEDGE_MARKERS = (
        "perhaps",
        "maybe",
        "might",
        "could be",
        "possibly",
        "it seems",
        "arguably",
        "i suppose",
        "not sure",
        "hard to say",
    )

    @staticmethod
    def _has_causal_contradiction(text: str) -> bool:
        """Detect explicit causal contradictions like 'A leads to B, so A does not affect B'.

        Handles both multi-word and single-letter variable names (common in
        logic examples like 'a leads to b').
        """
        import re

        # Build the full transitive closure of causal links:
        # "a leads to b, b leads to c" means a transitively causes c.
        causal_pairs = re.findall(
            r"(\w+)\s+(?:leads?\s+to|causes?|implies?|results?\s+in)\s+(\w+)", text
        )
        if not causal_pairs:
            return False

        # Build reachability graph
        graph: dict[str, set[str]] = {}
        for cause, effect in causal_pairs:
            graph.setdefault(cause, set()).add(effect)

        # Transitive closure via BFS
        reachable: dict[str, set[str]] = {}
        for start in graph:
            visited: set[str] = set()
            queue = list(graph.get(start, []))
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                queue.extend(graph.get(node, set()) - visited)
            reachable[start] = visited

        # Check for negations that contradict transitive reachability
        negations = re.findall(
            r"(\w+)\s+(?:does\s+not|doesn't|cannot|can't)\s+"
            r"(?:affect|impact|lead\s+to|cause|influence)\s+(\w+)",
            text,
        )
        for neg_cause, neg_effect in negations:
            if neg_effect in reachable.get(neg_cause, set()):
                return True

        return False

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
