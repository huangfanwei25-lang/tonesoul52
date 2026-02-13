from __future__ import annotations

from types import SimpleNamespace

import apps.api.server as server


def _client(testing: bool = True):
    server.app.config["TESTING"] = testing
    return server.app.test_client()


def test_read_auth_fail_closed_when_production_without_token(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENV", "production")
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    monkeypatch.delenv("TONESOUL_AUTH_FAIL_CLOSED", raising=False)

    client = _client()
    response = client.get("/api/conversations")
    payload = response.get_json()

    assert response.status_code == 503
    assert payload["error"] == "Read API token not configured"


def test_read_auth_can_opt_out_fail_closed(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENV", "production")
    monkeypatch.setenv("TONESOUL_AUTH_FAIL_CLOSED", "0")
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)

    client = _client()
    response = client.get("/api/conversations")

    assert response.status_code != 503


def test_debug_mode_locked_in_production(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENV", "production")
    monkeypatch.setenv("TONESOUL_API_DEBUG", "1")
    assert server._resolve_debug_mode() is False


def test_debug_mode_allowed_in_non_production(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENV", "development")
    monkeypatch.setenv("TONESOUL_API_DEBUG", "1")
    assert server._resolve_debug_mode() is True


def test_validate_rate_limit_returns_429(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENABLE_RATE_LIMIT", "1")
    monkeypatch.setenv("TONESOUL_RATE_LIMIT_VALIDATE_PER_MINUTE", "1")
    monkeypatch.setenv("TONESOUL_RATE_LIMIT_WINDOW_SECONDS", "60")
    server._reset_rate_limit_state()

    previous_testing = server.app.config.get("TESTING", False)
    client = _client(testing=False)
    try:
        first = client.post("/api/validate", json={})
        second = client.post("/api/validate", json={})
    finally:
        server.app.config["TESTING"] = previous_testing

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.get_json()["error"] == "Too Many Requests"


def test_chat_rate_limit_returns_429(monkeypatch):
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
                semantic_contradictions=[],
                semantic_graph_summary={},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())
    monkeypatch.setenv("TONESOUL_ENABLE_RATE_LIMIT", "1")
    monkeypatch.setenv("TONESOUL_RATE_LIMIT_CHAT_PER_MINUTE", "1")
    monkeypatch.setenv("TONESOUL_RATE_LIMIT_WINDOW_SECONDS", "60")
    server._reset_rate_limit_state()

    previous_testing = server.app.config.get("TESTING", False)
    client = _client(testing=False)
    try:
        first = client.post("/api/chat", json={"message": "hello"})
        second = client.post("/api/chat", json={"message": "hello again"})
    finally:
        server.app.config["TESTING"] = previous_testing

    assert first.status_code == 200
    assert second.status_code == 429
    payload = second.get_json()
    assert payload["error"] == "Too Many Requests"
    assert payload["endpoint"] == "chat"
