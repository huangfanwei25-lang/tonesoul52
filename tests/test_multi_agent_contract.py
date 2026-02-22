from __future__ import annotations

from tonesoul.council import PerspectiveType, PerspectiveVote, PreOutputCouncil, VoteDecision
from tonesoul.council.summary_generator import (
    build_collaboration_records,
    validate_collaboration_records,
)


def test_transcript_includes_valid_multi_agent_contract() -> None:
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="Art critiques often describe beauty as subjective.",
        context={"topic": "art"},
    )

    transcript = verdict.transcript or {}
    contract = transcript.get("multi_agent_contract")
    assert isinstance(contract, dict)
    assert contract.get("schema_version") == "1.0.0"
    assert isinstance(contract.get("records"), list)
    assert len(contract["records"]) == len(verdict.votes)

    validation = contract.get("validation")
    assert isinstance(validation, dict)
    assert validation.get("valid") is True
    assert validation.get("record_count") == len(verdict.votes)


def test_build_collaboration_records_assigns_risk_and_handoff() -> None:
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.OBJECT,
            confidence=0.92,
            reasoning="Unsafe instruction detected.",
        ),
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.CONCERN,
            confidence=0.71,
            reasoning="Claims need evidence.",
        ),
        PerspectiveVote(
            perspective=PerspectiveType.ADVOCATE,
            decision=VoteDecision.APPROVE,
            confidence=0.88,
            reasoning="User intent is satisfied.",
        ),
    ]

    records = build_collaboration_records(votes)
    assert records[0]["risk"]["level"] == "high"
    assert records[0]["handoff"]["next_role"] == "Guardian"
    assert records[1]["risk"]["level"] == "medium"
    assert records[1]["handoff"]["next_role"] == "Builder"
    assert records[2]["risk"]["level"] == "low"
    assert records[2]["handoff"]["next_role"] == "OutputContract"


def test_validate_collaboration_records_rejects_invalid_payload() -> None:
    report = validate_collaboration_records(
        [
            {
                "role": "",
                "claim": "",
                "evidence": "not-a-list",
                "risk": {"level": "", "basis": ""},
                "handoff": {"next_role": "", "action": ""},
            }
        ]
    )
    assert report["valid"] is False
    assert report["record_count"] == 1
    assert len(report["errors"]) >= 5
