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


def test_write_auth_fail_closed_when_production_without_token(monkeypatch):
    monkeypatch.setenv("TONESOUL_ENV", "production")
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    monkeypatch.delenv("TONESOUL_WRITE_API_TOKEN", raising=False)
    monkeypatch.delenv("TONESOUL_AUTH_FAIL_CLOSED", raising=False)

    client = _client()
    response = client.post("/api/conversation", json={})
    payload = response.get_json()

    assert response.status_code == 503
    assert payload["error"] == "Write API token not configured"


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


def test_write_routes_require_token_when_configured(monkeypatch):
    monkeypatch.setenv("TONESOUL_WRITE_API_TOKEN", "secret-write-token")

    client = _client()
    chat = client.post("/api/chat", json={"message": "hello"})
    validate = client.post("/api/validate", json={})
    conversation = client.post("/api/conversation", json={})
    consent = client.post("/api/consent", json={})
    withdraw = client.delete("/api/consent/session_demo")
    report = client.post("/api/session-report", json={"history": []})
    switch = client.post("/api/llm/switch", json={"mode": "ollama"})
    consolidate = client.get("/api/consolidate")

    assert chat.status_code == 401
    assert validate.status_code == 401
    assert conversation.status_code == 401
    assert consent.status_code == 401
    assert withdraw.status_code == 401
    assert report.status_code == 401
    assert switch.status_code == 401
    assert consolidate.status_code == 401
    assert chat.get_json()["error"] == "Unauthorized write access"


def test_write_routes_accept_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("TONESOUL_WRITE_API_TOKEN", "secret-write-token")
    monkeypatch.setattr(
        server,
        "consolidate",
        lambda: SimpleNamespace(patterns={"status": "ok"}, meta_reflection="stable"),
    )

    client = _client()
    headers = {"Authorization": "Bearer secret-write-token"}

    validate = client.post("/api/validate", json={}, headers=headers)
    conversation = client.post("/api/conversation", json={}, headers=headers)
    consent = client.post(
        "/api/consent",
        json={"session_id": "session_demo", "consent_type": "standard"},
        headers=headers,
    )
    withdraw = client.delete("/api/consent/session_demo", headers=headers)
    consolidate = client.get("/api/consolidate", headers=headers)

    assert validate.status_code == 200
    assert conversation.status_code == 200
    assert consent.status_code == 200
    assert withdraw.status_code == 200
    assert consolidate.status_code == 200


def test_serverless_write_auth_requires_token_when_configured(monkeypatch):
    import api._shared.core as shared_core

    monkeypatch.setenv("TONESOUL_WRITE_API_TOKEN", "secret-write-token")

    payload, status = shared_core._require_write_api_auth({})

    assert status == 401
    assert payload == {"error": "Unauthorized write access"}


def test_serverless_write_auth_accepts_valid_bearer_token(monkeypatch):
    import api._shared.core as shared_core

    monkeypatch.setenv("TONESOUL_WRITE_API_TOKEN", "secret-write-token")

    payload, status = shared_core._require_write_api_auth(
        {"Authorization": "Bearer secret-write-token"}
    )

    assert status == 200
    assert payload is None
