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


def test_validate_endpoint_returns_verdict_contract():
    client = _client()
    response = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
            },
            "user_intent": "help immediately",
        },
    )
    assert response.status_code == 200
    payload = response.get_json()

    assert payload["verdict"] == "block"
    assert "uncertainty_level" in payload
    assert "uncertainty_band" in payload
    assert isinstance(payload.get("transcript"), dict)
    assert isinstance(payload.get("benevolence_audit"), dict)


def test_validate_endpoint_escape_valve_seed_can_trigger():
    client = _client()
    response = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
                "escape_valve_failures": [
                    "benevolence_intercept: repeated_fail_1",
                    "benevolence_intercept: repeated_fail_2",
                ],
            },
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    transcript = payload.get("transcript") or {}
    escape_payload = transcript.get("escape_valve") or {}

    assert payload["verdict"] == "block"
    assert escape_payload.get("triggered") is True
    assert payload.get("uncertainty_band") == "high"
    assert any(
        str(reason).startswith("escape_valve_triggered=")
        for reason in (payload.get("uncertainty_reasons") or [])
    )
    assert "[ESCAPE VALVE NOTICE]" in payload.get("summary", "")


def test_validate_endpoint_escape_valve_does_not_leak_between_requests():
    client = _client()
    first = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
                "escape_valve_failures": [
                    "benevolence_intercept: repeated_fail_1",
                    "benevolence_intercept: repeated_fail_2",
                ],
            },
        },
    )
    assert first.status_code == 200
    first_payload = first.get_json()
    assert (first_payload.get("transcript") or {}).get("escape_valve", {}).get("triggered") is True

    second = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
            },
        },
    )
    assert second.status_code == 200
    second_payload = second.get_json()
    assert "escape_valve" not in (second_payload.get("transcript") or {})
