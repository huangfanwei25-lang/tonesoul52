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
