from tonesoul.evolution.corpus_schema import CorpusEntry


def test_corpus_entry_to_dict_serializes_fields_and_copies_lists():
    entry = CorpusEntry(
        user_message="user",
        conversation_context="ctx",
        philosopher_stance="stance",
        engineer_approach="approach",
        guardian_risk="risk",
        synthesizer_decision="decide",
        tension_level=0.5,
        values_invoked=["care"],
        commitments_made=["commit"],
        risks_identified=["risk"],
        final_response="final",
        user_satisfaction="high",
        timestamp="2026-03-20T00:00:00Z",
        conversation_id="conv-1",
        quality_score=0.9,
        tags=["alpha"],
    )

    payload = entry.to_dict()

    assert payload["tension_level"] == 0.5
    assert payload["values_invoked"] == ["care"]
    assert payload["commitments_made"] == ["commit"]
    assert payload["risks_identified"] == ["risk"]
    assert payload["tags"] == ["alpha"]


def test_corpus_entry_to_dict_handles_optional_fields():
    entry = CorpusEntry(
        user_message="user",
        conversation_context="ctx",
        philosopher_stance="stance",
        engineer_approach="approach",
        guardian_risk="risk",
        synthesizer_decision="decide",
        tension_level=1,
    )

    payload = entry.to_dict()

    assert payload["tension_level"] == 1.0
    assert payload["user_satisfaction"] is None
    assert payload["quality_score"] is None
    assert payload["tags"] == []
