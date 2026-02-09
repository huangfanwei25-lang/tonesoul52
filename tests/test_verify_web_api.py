from scripts.verify_web_api import _summarize_payload, _validate_chat_council_mode


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
    summary = _summarize_payload("POST web /api/chat", payload, verbose=False)
    assert summary["council_mode"] == "full_llm"
    assert summary["has_verdict"] is True
