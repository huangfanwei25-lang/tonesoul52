from __future__ import annotations

from types import SimpleNamespace

import apps.api.server as server


def _client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


def _pipeline_result(response_text: str = "ok"):
    return SimpleNamespace(
        response=response_text,
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
        semantic_contradictions=[],
        semantic_graph_summary={},
    )


def test_chat_cache_reuses_pipeline_result_for_same_request(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    calls = {"count": 0}

    class _Pipeline:
        def process(self, **kwargs):
            calls["count"] += 1
            return _pipeline_result(response_text="cached-demo")

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())
    monkeypatch.setenv("TONESOUL_CHAT_CACHE_ENABLED", "1")
    server._reset_chat_cache_state()

    client = _client()
    first = client.post(
        "/api/chat", json={"message": "hello", "history": [], "full_analysis": False}
    )
    second = client.post(
        "/api/chat", json={"message": "hello", "history": [], "full_analysis": False}
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()["response"] == "cached-demo"
    assert second.get_json()["response"] == "cached-demo"
    assert calls["count"] == 1


def test_chat_cache_miss_when_request_changes(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    calls = {"count": 0}

    class _Pipeline:
        def process(self, **kwargs):
            calls["count"] += 1
            return _pipeline_result(response_text=f"call-{calls['count']}")

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())
    monkeypatch.setenv("TONESOUL_CHAT_CACHE_ENABLED", "1")
    server._reset_chat_cache_state()

    client = _client()
    first = client.post("/api/chat", json={"message": "hello", "history": []})
    second = client.post("/api/chat", json={"message": "hello-2", "history": []})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json()["response"] == "call-1"
    assert second.get_json()["response"] == "call-2"
    assert calls["count"] == 2


def test_session_report_rejects_invalid_history_item_role():
    client = _client()
    response = client.post(
        "/api/session-report",
        json={"history": [{"role": "hacker", "content": "x"}]},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Invalid history item"


def test_chat_rejects_invalid_history_item_content_type():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "history": [{"role": "user", "content": 123}]},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Invalid history item"
