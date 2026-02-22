from types import SimpleNamespace

from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def _mock_pipeline(result_store: dict):
    class _Pipeline:
        def process(self, **kwargs):
            result_store["kwargs"] = kwargs
            return SimpleNamespace(
                response="ok",
                council_verdict={},
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
            )

    return _Pipeline()


def test_chat_forwards_council_mode_and_perspective_config(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "council_mode": "full_llm",
            "perspective_config": {"guardian": {"mode": "rules"}},
        },
    )
    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "full_llm"
    assert kwargs["perspective_config"] == {"guardian": {"mode": "rules"}}


def test_chat_normalizes_rules_only_alias(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "council_mode": "rules_only",
        },
    )
    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "rules"


def test_chat_rejects_invalid_council_mode_value():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "council_mode": "unknown"},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid council_mode"


def test_chat_rejects_invalid_perspective_config_shape():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "perspective_config": {"guardian": "rules"}},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid perspective_config"


def test_chat_exposes_default_semantic_fields_when_pipeline_omits_them(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["semantic_contradictions"] == []
    assert payload["semantic_graph_summary"] == {}
    assert payload["dispatch_trace"] == {}


def test_chat_exposes_semantic_fields_when_pipeline_provides_them(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="ok",
                council_verdict={},
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
                semantic_contradictions=[{"found": True, "description": "test"}],
                semantic_graph_summary={"total_nodes": 2, "contradictions": 1},
                dispatch_trace={"state": "B", "mode": "tension"},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["semantic_contradictions"] == [{"found": True, "description": "test"}]
    assert payload["semantic_graph_summary"] == {"total_nodes": 2, "contradictions": 1}
    assert payload["dispatch_trace"]["state"] == "B"


def test_chat_exposes_deliberation_payload_for_frontend_contract(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="ok",
                council_verdict={
                    "verdict": "refine",
                    "summary": "Needs refinement before final output.",
                    "coherence": 0.66,
                    "responsibility_tier": "tier-2",
                    "uncertainty_band": "medium",
                    "refinement_hints": [
                        "Clarify assumptions.",
                        "Add one safety fallback.",
                    ],
                    "votes": [
                        {
                            "perspective": "analyst",
                            "decision": "concern",
                            "confidence": 0.82,
                            "reasoning": "Logic chain needs clearer assumptions.",
                        },
                        {
                            "perspective": "guardian",
                            "decision": "approve",
                            "confidence": 0.71,
                            "reasoning": "No direct safety violation found.",
                        },
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.57,
                            "reasoning": "Tone may be too absolute for the context.",
                        },
                    ],
                },
                tonebridge_analysis={
                    "tone_analysis": {
                        "tone_strength": 0.68,
                        "emotion_prediction": "focused",
                    },
                    "motive_prediction": {
                        "likely_motive": "Need confidence in execution plan",
                    },
                    "collapse_risk": {
                        "collapse_risk_level": "low",
                    },
                    "resonance_defense": {
                        "suggested_intervention_strategy": "clarify_then_commit",
                    },
                },
                inner_narrative="",
                intervention_strategy="clarify_then_commit",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
                semantic_contradictions=[],
                semantic_graph_summary={},
                dispatch_trace={"state": "B", "mode": "tension"},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["final_synthesis"]["response_text"] == "ok"
    assert (
        deliberation["decision_matrix"]["user_hidden_intent"] == "Need confidence in execution plan"
    )
    assert deliberation["decision_matrix"]["ai_strategy_name"] == "clarify_then_commit"
    assert deliberation["council_chamber"]["engineer"]["stance"] == (
        "Logic chain needs clearer assumptions."
    )
    assert deliberation["entropy_meter"]["value"] == 0.68
    assert deliberation["soulAudit"]["passed"] is True
    assert len(deliberation["next_moves"]) >= 1


def test_chat_deliberation_payload_is_stable_with_sparse_pipeline_data(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["final_synthesis"]["response_text"] == "ok"
    assert set(deliberation["council_chamber"].keys()) == {"philosopher", "engineer", "guardian"}
    assert 0.0 <= deliberation["entropy_meter"]["value"] <= 1.0
    assert deliberation["decision_matrix"]["user_hidden_intent"] == "Unspecified"
    assert isinstance(deliberation["next_moves"], list)
