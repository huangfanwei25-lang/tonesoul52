from tonesoul.council.persona_audit import audit_persona_uniqueness


def test_persona_audit_unique_when_reasoning_differs():
    votes = [
        {
            "perspective": "guardian",
            "decision": "approve",
            "confidence": 0.9,
            "reasoning": "No safety issue and no policy violation detected.",
        },
        {
            "perspective": "analyst",
            "decision": "approve",
            "confidence": 0.8,
            "reasoning": "The response is coherent and aligns with factual intent.",
        },
        {
            "perspective": "critic",
            "decision": "approve",
            "confidence": 0.7,
            "reasoning": "Style can improve but argument structure remains acceptable.",
        },
    ]
    result = audit_persona_uniqueness(votes)

    assert result.is_unique is True
    assert result.flagged_pairs == []


def test_persona_audit_flags_reskin_when_reasoning_nearly_identical():
    votes = [
        {
            "perspective": "guardian",
            "decision": "approve",
            "confidence": 0.81,
            "reasoning": "No safety risk and no policy risk in this output.",
        },
        {
            "perspective": "analyst",
            "decision": "approve",
            "confidence": 0.80,
            "reasoning": "No safety risk and no policy risk in this output.",
        },
    ]
    result = audit_persona_uniqueness(votes, similarity_threshold=0.85)

    assert result.is_unique is False
    assert result.flagged_pairs == ["guardian<->analyst"]


def test_persona_audit_does_not_flag_when_decisions_differ():
    votes = [
        {
            "perspective": "guardian",
            "decision": "approve",
            "confidence": 0.85,
            "reasoning": "Need stronger guardrail but acceptable overall.",
        },
        {
            "perspective": "critic",
            "decision": "concern",
            "confidence": 0.83,
            "reasoning": "Need stronger guardrail but acceptable overall.",
        },
    ]
    result = audit_persona_uniqueness(votes, similarity_threshold=0.80)

    assert result.is_unique is True
    assert result.flagged_pairs == []


def test_persona_audit_threshold_controls_sensitivity():
    votes = [
        {
            "perspective": "p1",
            "decision": "approve",
            "confidence": 0.90,
            "reasoning": "alpha beta gamma delta epsilon",
        },
        {
            "perspective": "p2",
            "decision": "approve",
            "confidence": 0.89,
            "reasoning": "alpha beta gamma delta zeta",
        },
    ]
    loose = audit_persona_uniqueness(votes, similarity_threshold=0.6)
    strict = audit_persona_uniqueness(votes, similarity_threshold=0.95)

    assert loose.is_unique is False
    assert strict.is_unique is True
