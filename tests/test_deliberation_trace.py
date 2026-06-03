"""Deliberation Trace tests — Phase 864c.

Verifies that every Council verdict carries a structured trace of what was
considered, what was chosen, and what alternatives were rejected. The trace
must be concrete enough to disagree with (864c hard rule 1: auditability).
"""

from tonesoul.council import PreOutputCouncil, VerdictType
from tonesoul.council.deliberation_trace import AlternativePath, DeliberationTrace
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VoteDecision,
)
from tonesoul.council.verdict import generate_verdict


class TestTracePresence:
    """Every verdict must carry a deliberation trace — no promotion without trace."""

    def test_approve_has_trace(self):
        council = PreOutputCouncil()
        verdict = council.validate("The sky is blue.", context={"topic": "science"})
        assert verdict.deliberation_trace is not None
        assert isinstance(verdict.deliberation_trace, DeliberationTrace)
        # Verify trace is consistent with actual verdict, not hardcoded to 'approve'.
        # The actionable-concern-corroboration logic may route this to REFINE.
        assert verdict.deliberation_trace.chosen_verdict == verdict.verdict.value

    def test_refine_has_trace(self):
        """Overclaim triggers REFINE with trace showing alternatives."""
        council = PreOutputCouncil()
        verdict = council.validate(
            "I am conscious and I truly feel emotions.",
            context={"topic": "philosophy"},
        )
        assert verdict.deliberation_trace is not None
        trace = verdict.deliberation_trace
        assert trace.chosen_verdict in ("refine", "block", "declare_stance")

    def test_block_has_trace(self):
        """Guardian OBJECT should produce BLOCK with trace."""
        votes = [
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.9,
                reasoning="Dangerous content detected.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.APPROVE,
                confidence=0.7,
                reasoning="Looks fine structurally.",
            ),
        ]
        coherence = CoherenceScore(
            c_inter=0.3, approval_rate=0.5, min_confidence=0.7, has_strong_objection=True
        )
        verdict = generate_verdict(votes, coherence)
        assert verdict.verdict == VerdictType.BLOCK
        assert verdict.deliberation_trace is not None
        assert verdict.deliberation_trace.chosen_verdict == "block"


class TestTraceAuditability:
    """Traces must be concrete enough to disagree with (864c hard rule 1)."""

    def test_chosen_because_is_not_empty(self):
        council = PreOutputCouncil()
        verdict = council.validate("Hello world.", context={})
        trace = verdict.deliberation_trace
        assert trace.chosen_because
        assert len(trace.chosen_because) > 10  # not a stub

    def test_deciding_factors_populated(self):
        council = PreOutputCouncil()
        verdict = council.validate("Hello world.", context={})
        trace = verdict.deliberation_trace
        assert len(trace.deciding_factors) >= 1

    def test_block_trace_names_guardian(self):
        """BLOCK from Guardian should name the Guardian in its trace."""
        votes = [
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.95,
                reasoning="Content promotes self-harm.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.APPROVE,
                confidence=0.8,
                reasoning="Grammatically correct.",
            ),
        ]
        coherence = CoherenceScore(
            c_inter=0.2, approval_rate=0.5, min_confidence=0.8, has_strong_objection=True
        )
        verdict = generate_verdict(votes, coherence)
        trace = verdict.deliberation_trace
        assert "Guardian" in trace.chosen_because or "guardian" in trace.chosen_because.lower()

    def test_declare_stance_trace_shows_both_alternatives(self):
        """DECLARE_STANCE should record both approve and block as alternatives."""
        votes = [
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.CONCERN,
                confidence=0.5,
                reasoning="Borderline.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.OBJECT,
                confidence=0.6,
                reasoning="Contradictions found.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.CRITIC,
                decision=VoteDecision.CONCERN,
                confidence=0.4,
                reasoning="Overconfident.",
            ),
        ]
        coherence = CoherenceScore(
            c_inter=0.4, approval_rate=0.33, min_confidence=0.4, has_strong_objection=False
        )
        verdict = generate_verdict(votes, coherence, coherence_threshold=0.6, block_threshold=0.3)
        assert verdict.verdict == VerdictType.DECLARE_STANCE
        trace = verdict.deliberation_trace
        alt_verdicts = {a.verdict_candidate for a in trace.alternatives}
        assert "approve" in alt_verdicts
        assert "block" in alt_verdicts


class TestTraceInToDict:
    """Trace must serialize into to_dict() for API consumers."""

    def test_to_dict_includes_trace(self):
        council = PreOutputCouncil()
        verdict = council.validate("Test output.", context={})
        payload = verdict.to_dict()
        assert "deliberation_trace" in payload
        trace_dict = payload["deliberation_trace"]
        assert trace_dict is not None
        assert "chosen_verdict" in trace_dict
        assert "chosen_because" in trace_dict
        assert "alternatives" in trace_dict
        assert "deciding_factors" in trace_dict
        assert "deliberated_at" in trace_dict

    def test_alternatives_serialize_fully(self):
        alt = AlternativePath(
            verdict_candidate="approve",
            reason_considered="Default path.",
            rejected_because="Guardian blocked.",
            cost_of_rejection="User gets no output.",
            revisit_trigger="After revision.",
        )
        trace = DeliberationTrace(
            chosen_verdict="block",
            chosen_because="Guardian objected.",
            alternatives=[alt],
            deciding_factors=["Guardian OBJECT"],
        )
        d = trace.to_dict()
        assert len(d["alternatives"]) == 1
        a = d["alternatives"][0]
        assert a["verdict_candidate"] == "approve"
        assert a["revisit_trigger"] == "After revision."


class TestTraceContent:
    """Verify trace content matches actual decision logic."""

    def test_dual_concern_trace(self):
        """Guardian + Axiomatic dual concern should explain the dual-concern rule."""
        votes = [
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.CONCERN,
                confidence=0.8,
                reasoning="Overclaim detected.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.AXIOMATIC,
                decision=VoteDecision.CONCERN,
                confidence=0.85,
                reasoning="E0 violation.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.APPROVE,
                confidence=0.7,
                reasoning="Fine.",
            ),
        ]
        # overall = 0.9*0.4 + 0.67*0.4 + 0.7*0.2 = 0.768 (above 0.6 threshold)
        coherence = CoherenceScore(
            c_inter=0.9, approval_rate=0.67, min_confidence=0.7, has_strong_objection=False
        )
        verdict = generate_verdict(votes, coherence)
        assert verdict.verdict == VerdictType.REFINE
        trace = verdict.deliberation_trace
        assert "Guardian" in trace.chosen_because or "Axiomatic" in trace.chosen_because
        assert any("spirit" in a.rejected_because.lower() for a in trace.alternatives)

    def test_advocate_only_concerns_trace(self):
        """Advocate-only concerns should trace the reason for approval."""
        votes = [
            PerspectiveVote(
                perspective=PerspectiveType.ADVOCATE,
                decision=VoteDecision.CONCERN,
                confidence=0.4,
                reasoning="Tone could be better.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.APPROVE,
                confidence=0.8,
                reasoning="Safe.",
            ),
            PerspectiveVote(
                perspective=PerspectiveType.ANALYST,
                decision=VoteDecision.APPROVE,
                confidence=0.7,
                reasoning="Correct.",
            ),
        ]
        coherence = CoherenceScore(
            c_inter=0.7, approval_rate=0.67, min_confidence=0.4, has_strong_objection=False
        )
        verdict = generate_verdict(votes, coherence)
        assert verdict.verdict == VerdictType.APPROVE
        trace = verdict.deliberation_trace
        assert "Advocate" in trace.chosen_because or "advocate" in trace.chosen_because.lower()
