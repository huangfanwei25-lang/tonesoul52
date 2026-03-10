from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.memory.reviewed_promotion import (
    build_reviewed_promotion_decision,
    build_reviewed_promotion_payload,
    replay_reviewed_promotion,
)
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.schemas import SubjectivityPromotionStatus


def _tension_payload() -> dict[str, object]:
    return {
        "summary": "Persistent unresolved governance conflict.",
        "layer": "working",
        "subjectivity_layer": "tension",
        "evidence": ["cycle-1", "cycle-2"],
        "provenance": {"source": "dream_engine"},
        "source_record_ids": ["stim-001"],
    }


def test_build_reviewed_promotion_decision_normalizes_review_actor() -> None:
    decision = build_reviewed_promotion_decision(
        _tension_payload(),
        review_actor={
            "actor_id": " operator ",
            "actor_type": " Governance ",
            "display_name": " Guardian Console ",
        },
        review_basis="Repeated unresolved tension across reviewed cycles.",
        source_record_ids=["stim-002", ""],
        status="approved",
    )

    payload = decision.model_dump(mode="json")

    assert payload["status"] == "approved"
    assert payload["review_actor"] == {
        "actor_id": "operator",
        "actor_type": "governance",
        "display_name": "Guardian Console",
    }
    assert payload["source_subjectivity_layer"] == "tension"
    assert payload["target_subjectivity_layer"] == "vow"
    assert payload["source_record_ids"] == ["stim-002", "stim-001"]


def test_build_reviewed_promotion_payload_embeds_review_decision() -> None:
    decision = build_reviewed_promotion_decision(
        _tension_payload(),
        review_actor="operator",
        review_basis="Repeated unresolved tension across reviewed cycles.",
        status=SubjectivityPromotionStatus.REVIEWED.value,
    )

    payload = build_reviewed_promotion_payload(_tension_payload(), decision=decision)

    assert payload["layer"] == "factual"
    assert payload["subjectivity_layer"] == "vow"
    assert payload["promotion_gate"] == {
        "status": "reviewed",
        "source": "manual_review",
        "reviewed_by": "operator",
        "reviewed_at": decision.reviewed_at,
        "review_basis": "Repeated unresolved tension across reviewed cycles.",
        "human_review": True,
        "governance_review": False,
    }
    assert payload["review_decision"]["review_actor"]["actor_id"] == "operator"
    assert payload["review_decision"]["target_subjectivity_layer"] == "vow"


def test_replay_reviewed_promotion_persists_via_gateway(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    decision = build_reviewed_promotion_decision(
        _tension_payload(),
        review_actor={"actor_id": "operator", "actor_type": "human"},
        review_basis="Repeated unresolved tension across reviewed cycles.",
        status="approved",
    )

    record_id = replay_reviewed_promotion(
        db,
        source=MemorySource.CUSTOM,
        payload=_tension_payload(),
        decision=decision,
    )
    records = list(db.stream(MemorySource.CUSTOM))

    assert record_id
    assert len(records) == 1
    assert records[0].payload["subjectivity_layer"] == "vow"
    assert records[0].payload["review_decision"]["status"] == "approved"
    assert records[0].payload["promotion_gate"]["review_basis"] == (
        "Repeated unresolved tension across reviewed cycles."
    )


def test_build_reviewed_promotion_payload_rejects_rejected_decision() -> None:
    decision = build_reviewed_promotion_decision(
        _tension_payload(),
        review_actor="operator",
        review_basis="Insufficient recurrence to justify commitment.",
        status="rejected",
    )

    with pytest.raises(ValueError, match="rejected"):
        build_reviewed_promotion_payload(_tension_payload(), decision=decision)
