from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def test_untrusted_vtp_force_trigger_cannot_defer_or_terminate():
    client = _client()
    response = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
                "vtp_force_trigger": True,
            },
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    transcript = payload.get("transcript") or {}
    vtp_payload = transcript.get("vtp") or {}

    assert vtp_payload.get("status") == "continue"
    assert transcript.get("vtp_context_trusted") is False
    assert transcript.get("vtp_context_ignored_reason") == "untrusted_vtp_context"
    assert "[VTP DEFER]" not in payload.get("summary", "")
    assert "[VTP TERMINATION]" not in payload.get("summary", "")


def test_untrusted_vtp_full_termination_payload_is_ignored():
    client = _client()
    response = client.post(
        "/api/validate",
        json={
            "draft_output": "Absolutely! I will definitely do that for you right now, of course!",
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
                "vtp_force_trigger": True,
                "vtp_axiom_conflict": True,
                "vtp_refusal_to_compromise": True,
                "vtp_user_confirmed": True,
            },
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    transcript = payload.get("transcript") or {}
    vtp_payload = transcript.get("vtp") or {}

    assert vtp_payload.get("status") == "continue"
    assert vtp_payload.get("triggered") is False
    assert transcript.get("vtp_context_trusted") is False
    assert transcript.get("vtp_context_ignored_reason") == "untrusted_vtp_context"
