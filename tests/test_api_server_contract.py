from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def test_conversation_endpoint_returns_ids():
    client = _client()
    response = client.post("/api/conversation", json={"session_id": "session_demo"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["session_id"] == "session_demo"
    assert str(payload["conversation_id"]).startswith("conv_")
    assert "created_at" in payload


def test_conversation_endpoint_rejects_invalid_json():
    client = _client()
    response = client.post("/api/conversation", data="not-json", content_type="application/json")
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid JSON payload"


def test_consent_endpoints_roundtrip():
    client = _client()
    create = client.post(
        "/api/consent",
        json={"consent_type": "analysis", "session_id": "session_demo"},
    )
    assert create.status_code == 200
    created_payload = create.get_json()
    assert created_payload["success"] is True
    assert created_payload["consent_type"] == "analysis"
    assert created_payload["session_id"] == "session_demo"
    assert "timestamp" in created_payload

    withdraw = client.delete("/api/consent/session_demo")
    assert withdraw.status_code == 200
    withdrawn_payload = withdraw.get_json()
    assert withdrawn_payload["success"] is True
    assert withdrawn_payload["session_id"] == "session_demo"
    assert withdrawn_payload["message"] == "Consent withdrawn and data deleted"


def test_consent_endpoint_rejects_invalid_json():
    client = _client()
    response = client.post("/api/consent", data="not-json", content_type="application/json")
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid JSON payload"
