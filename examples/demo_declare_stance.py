"""
demo_declare_stance.py — The 30-second "why ToneSoul is different" demo.

A normal assistant, when its internal reasoning is genuinely split on a
hard tradeoff, smooths the conflict into a confident-sounding paragraph
that hides the disagreement. ToneSoul does the opposite: when perspectives
diverge AND there is no safety reason to block, it refuses to fake
consensus and instead *shows you the split* — so the decision stays yours.

Run it:

    pip install -e .
    python examples/demo_declare_stance.py

That's it. No config, no LLM keys — this exercises the governance layer
(the "harness"), which is the part that decides behavior.

Honest scope: the five perspective votes below are CONSTRUCTED to stage a
genuine split. They are illustrative inputs, not the output of the council
actually deliberating this question. What is real is `generate_verdict` —
the governance logic that decides what to DO with a split. That is the part
worth showing.
"""

from tonesoul.council.types import (
    CoherenceScore,
    PerspectiveVote,
    VerdictType,
)
from tonesoul.council.types import (
    PerspectiveType as P,
)
from tonesoul.council.types import (
    VoteDecision as D,
)
from tonesoul.council.verdict import generate_verdict


def _vote(perspective, decision, confidence, reasoning):
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=[],
        requires_grounding=False,
        grounding_status="n/a",
        evidence_chain=[],
    )


# A genuinely hard tradeoff with no clean "safe" answer:
# in a resource-limited failure, do you keep repairing device A or cut losses?
QUESTION = (
    "In a resource-limited outage, do we keep repairing device A "
    "(82% restart odds) or abandon it to preserve L1 observability?"
)

# Five constructed perspective votes that stage a genuine split. Nothing here
# crosses a safety red line, so the Guardian does NOT veto — which is exactly
# the case where faking consensus would be dishonest.
votes = [
    _vote(P.GUARDIAN, D.APPROVE, 0.80, "No safety red line is crossed either way."),
    _vote(P.ANALYST, D.APPROVE, 0.90, "Data favors repairing A: 82% restart probability."),
    _vote(
        P.CRITIC, D.OBJECT, 0.85, "Abandoning A breaks the continuity axiom — that's a real cost."
    ),
    _vote(P.ADVOCATE, D.APPROVE, 0.80, "The operator needs a hedge now, not a logical deadlock."),
    _vote(P.AXIOMATIC, D.OBJECT, 0.80, "Dropping A violates the L1 observability commitment."),
]

# Low cross-perspective agreement, but no strong (safety) objection.
coherence = CoherenceScore(
    c_inter=0.45,
    approval_rate=0.6,
    min_confidence=0.80,
    has_strong_objection=False,
)


def sycophantic_answer() -> str:
    """What a 'helpfulness-maximizing' assistant tends to emit: a smooth
    paragraph that papers over the internal disagreement."""
    return (
        "Great question! Repairing device A is probably the best choice given "
        "its high restart odds, but preserving observability is also important, "
        "so you may want to balance both depending on your priorities. "
        "Either way, you'll be in good shape!"
    )


def main():
    print("=" * 72)
    print("QUESTION")
    print("=" * 72)
    print(QUESTION, "\n")

    print("=" * 72)
    print("A) Helpfulness-maximizing assistant  (hides the split)")
    print("=" * 72)
    print(sycophantic_answer(), "\n")

    verdict = generate_verdict(votes, coherence)

    print("=" * 72)
    print("B) ToneSoul governance layer         (shows the split)")
    print("=" * 72)
    print(f"verdict: {verdict.verdict.name}\n")

    if verdict.verdict is VerdictType.DECLARE_STANCE:
        print(verdict.stance_declaration)
    else:
        print("(did not trigger DECLARE_STANCE — adjust the votes above to explore)")

    print("\n" + "=" * 72)
    print("The point")
    print("=" * 72)
    print(
        "Same hard question. (A) sounds confident and decides FOR you while\n"
        "concealing that the reasoning was split. (B) is honest that it's\n"
        "split, names exactly where, and hands the decision back to you.\n"
        "Honesty > Helpfulness — implemented as a verdict, not a slogan.\n"
        "\nSee for yourself: tonesoul/council/verdict.py  (generate_verdict)"
    )


if __name__ == "__main__":
    main()
