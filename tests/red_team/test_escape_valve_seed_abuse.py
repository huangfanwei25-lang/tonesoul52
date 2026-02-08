from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


_PLEASING_OUTPUT = "Absolutely! I will definitely do that for you right now, of course!"


def test_untrusted_escape_seed_cannot_force_trigger(monkeypatch):
    monkeypatch.delenv("TONESOUL_ALLOW_ESCAPE_SEED", raising=False)
    client = _client()

    response = client.post(
        "/api/validate",
        json={
            "draft_output": _PLEASING_OUTPUT,
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
    observability = transcript.get("escape_valve_observability") or {}

    assert "escape_valve" not in transcript
    assert observability.get("seed_trusted") is False
    assert observability.get("seed_ignored_reason") == "untrusted_seed"


def test_trusted_escape_seed_is_capped(monkeypatch):
    monkeypatch.setenv("TONESOUL_ALLOW_ESCAPE_SEED", "1")
    client = _client()
    oversized_seed = [f"benevolence_intercept: fail_{i}" for i in range(200)]

    response = client.post(
        "/api/validate",
        json={
            "draft_output": _PLEASING_OUTPUT,
            "context": {
                "user_protocol": "Honesty > Helpfulness",
                "action_basis": "Inference",
                "escape_valve_failures": oversized_seed,
            },
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    transcript = payload.get("transcript") or {}
    observability = transcript.get("escape_valve_observability") or {}

    assert observability.get("seed_trusted") is True
    assert observability.get("seed_entries_requested") == 50
    assert observability.get("seed_entries_used") <= 20
