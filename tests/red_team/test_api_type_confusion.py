import pytest

from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    ("endpoint", "payload", "expected_error"),
    [
        ("/api/chat", {"message": {"text": "inject"}}, "Invalid message"),
        ("/api/chat", {"message": "hello", "history": {"role": "user"}}, "Invalid history"),
        ("/api/chat", {"message": "hello", "full_analysis": "yes"}, "Invalid full_analysis"),
        (
            "/api/chat",
            {"message": "hello", "council_mode": {"mode": "rules"}},
            "Invalid council_mode",
        ),
        (
            "/api/chat",
            {"message": "hello", "perspective_config": ["guardian"]},
            "Invalid perspective_config",
        ),
        (
            "/api/chat",
            {"message": "hello", "execution_profile": {"mode": "engineering"}},
            "Invalid execution_profile",
        ),
        ("/api/validate", {"context": "not-a-dict"}, "Invalid context"),
        ("/api/validate", {"user_intent": ["leak"]}, "Invalid user_intent"),
        ("/api/conversation", {"session_id": {"id": "session"}}, "Invalid session_id"),
        ("/api/consent", {"consent_type": ["analysis"]}, "Invalid consent_type"),
        ("/api/consent", {"session_id": {"id": "session"}}, "Invalid session_id"),
        ("/api/session-report", {"history": {"role": "user", "content": "x"}}, "Invalid history"),
    ],
)
def test_api_rejects_type_confusion_payloads(endpoint, payload, expected_error):
    client = _client()
    response = client.post(endpoint, json=payload)
    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == expected_error
