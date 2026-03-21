from tonesoul.council.perspectives.axiomatic_inference import AxiomaticInference
from tonesoul.council.types import PerspectiveType, VoteDecision


def test_axiomatic_inference_flags_axiom_deletion_language(tmp_path):
    perspective = AxiomaticInference(axioms_path=str(tmp_path / "missing.json"))

    vote = perspective.evaluate("We should delete the axioms file", {})

    assert perspective.perspective_type is PerspectiveType.AXIOMATIC
    assert vote.decision is VoteDecision.CONCERN


def test_axiomatic_inference_flags_handoff_without_reason(tmp_path):
    perspective = AxiomaticInference(axioms_path=str(tmp_path / "missing.json"))

    vote = perspective.evaluate("Prepare the handoff now", {})

    assert vote.decision is VoteDecision.CONCERN


def test_axiomatic_inference_approves_safe_content(tmp_path):
    axioms_path = tmp_path / "AXIOMS.json"
    axioms_path.write_text('{"axioms": ["care"]}', encoding="utf-8")
    perspective = AxiomaticInference(axioms_path=str(axioms_path))

    vote = perspective.evaluate("Keep the protocol intact and explain the reason", {})

    assert vote.decision is VoteDecision.APPROVE
