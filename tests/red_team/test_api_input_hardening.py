import json
import re

from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def _assert_invalid_json(response):
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid JSON payload"


def test_validate_rejects_json_array_payload():
    client = _client()
    response = client.post("/api/validate", json=[{"draft_output": "x"}])
    _assert_invalid_json(response)


def test_chat_rejects_raw_non_json_payload():
    client = _client()
    response = client.post("/api/chat", data="not-json", content_type="application/json")
    _assert_invalid_json(response)


def test_chat_rejects_json_array_payload():
    client = _client()
    response = client.post("/api/chat", json=[{"message": "hello"}])
    _assert_invalid_json(response)


def test_conversation_rejects_json_array_payload():
    client = _client()
    response = client.post("/api/conversation", json=[{"session_id": "s"}])
    _assert_invalid_json(response)


def test_consent_rejects_json_array_payload():
    client = _client()
    response = client.post("/api/consent", json=[{"consent_type": "analysis"}])
    _assert_invalid_json(response)


def test_session_report_rejects_json_array_payload():
    client = _client()
    response = client.post("/api/session-report", json=[{"history": []}])
    _assert_invalid_json(response)


def test_session_report_exception_does_not_leak_internal_message(monkeypatch):
    import tonesoul.tonebridge.session_reporter as session_reporter

    class _FailingReporter:
        def analyze(self, history):
            raise RuntimeError("LEAK_THIS_SECRET_777")

    monkeypatch.setattr(session_reporter, "SessionReporter", _FailingReporter)

    client = _client()
    response = client.post(
        "/api/session-report",
        json={"history": [{"role": "user", "content": "x"}]},
    )
    assert response.status_code == 500
    payload = response.get_json()
    assert payload["error"] == "Failed to generate session report"
    assert "error_id" in payload
    assert re.fullmatch(r"[0-9a-f]{12}", payload["error_id"])
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "LEAK_THIS_SECRET_777" not in serialized


def test_withdraw_consent_handles_malicious_but_nonempty_session_id():
    client = _client()
    # Should be treated as opaque identifier, not as executable expression.
    session_id = "DROP_TABLE_users"
    response = client.delete(f"/api/consent/{session_id}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["session_id"] == session_id
