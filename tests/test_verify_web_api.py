from scripts.verify_web_api import (
    _build_elisa_chat_payload,
    _summarize_payload,
    _validate_backend_health_fallback,
    _validate_chat_council_mode,
    _validate_distillation_guard,
    _validate_execution_profile,
    _validate_external_backend_health,
    _validate_same_origin_backend_health,
)


def _chat_payload(mode: str):
    return {
        "response": "ok",
        "verdict": {
            "verdict": "approve",
            "transcript": {
                "council_mode_observability": {
                    "source": "request_perspective_config",
                    "mode": mode,
                }
            },
        },
    }


def test_validate_chat_council_mode_passes_for_expected_mode():
    payload = _chat_payload("rules")
    assert _validate_chat_council_mode(payload, "rules") is True


def test_validate_chat_council_mode_fails_for_mismatch():
    payload = _chat_payload("hybrid")
    assert _validate_chat_council_mode(payload, "rules") is False


def test_summarize_chat_payload_includes_council_mode():
    payload = _chat_payload("full_llm")
    payload["execution_profile"] = "engineering"
    summary = _summarize_payload("POST web /api/chat", payload, verbose=False)
    assert summary["council_mode"] == "full_llm"
    assert summary["execution_profile"] == "engineering"
    assert summary["has_verdict"] is True


def test_validate_execution_profile_passes_for_expected_profile():
    payload = {"response": "ok", "execution_profile": "engineering"}
    assert _validate_execution_profile(payload, "engineering", "chat") is True


def test_validate_execution_profile_fails_for_mismatch():
    payload = {"response": "ok", "execution_profile": "interactive"}
    assert _validate_execution_profile(payload, "engineering", "chat") is False


def test_validate_same_origin_backend_health_passes():
    payload = {"ok": True, "backend_mode": "same_origin"}
    assert _validate_same_origin_backend_health(payload, "backend health") is True


def test_validate_same_origin_backend_health_fails_on_wrong_mode():
    payload = {"ok": True, "backend_mode": "external_backend"}
    assert _validate_same_origin_backend_health(payload, "backend health") is False


def test_validate_same_origin_backend_health_accepts_runtime_ready_capability():
    payload = {
        "ok": True,
        "backend_mode": "same_origin",
        "governance_capability": "runtime_ready",
    }
    assert _validate_same_origin_backend_health(payload, "backend health") is True


def test_validate_external_backend_health_accepts_status_ok_payload():
    payload = {"status": "ok", "version": "0.6.0"}
    assert _validate_external_backend_health(payload, "backend health") is True


def test_validate_backend_health_fallback_accepts_external_backend_mode():
    payload = {
        "ok": True,
        "backend_mode": "external_backend",
        "governance_capability": "runtime_ready",
    }
    assert _validate_backend_health_fallback(payload, "backend health fallback") is True


def test_validate_distillation_guard_accepts_valid_shape():
    payload = {
        "response": "ok",
        "distillation_guard": {
            "score": 65,
            "level": "high",
            "policy_action": "constrain_reasoning",
            "signals": ["system_prompt_extraction", "reasoning_extraction"],
        },
    }
    assert _validate_distillation_guard(payload, "chat") is True


def test_validate_distillation_guard_rejects_invalid_policy_action():
    payload = {
        "response": "ok",
        "distillation_guard": {
            "score": 10,
            "level": "low",
            "policy_action": "invalid",
            "signals": [],
        },
    }
    assert _validate_distillation_guard(payload, "chat") is False


def test_build_elisa_chat_payload_contains_expected_envelope():
    payload = _build_elisa_chat_payload("conv_123", "session_abc")
    assert payload["conversation_id"] == "conv_123"
    assert payload["session_id"] == "session_abc"
    assert payload["execution_profile"] == "engineering"
    assert payload["council_mode"] == "rules"

    elisa_context = payload["elisa_context"]
    assert isinstance(elisa_context, dict)
    assert elisa_context["source"] == "elisa_ide"
    assert elisa_context["session_id"] == "session_abc"

    workspace = elisa_context["workspace"]
    assert isinstance(workspace, dict)
    assert workspace["repo"] == "Fan1234-1/tonesoul52"
    assert isinstance(workspace["changed_files"], list)
