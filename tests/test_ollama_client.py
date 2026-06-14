from __future__ import annotations

import pytest
import requests

from tonesoul.llm.ollama_client import OllamaClient, OllamaError, create_ollama_client


class _JsonResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_ensure_model_prefers_qwen_fallback_over_other_available_models() -> None:
    client = OllamaClient(model="missing-model")
    client._available_models = ["gemma3:4b", "qwen2.5:7b", "llama3:8b"]

    assert client._ensure_model() == "qwen2.5:7b"


def test_ensure_model_resolves_substring_to_real_served_tag_not_requested_string() -> None:
    # Regression: the old `any(self.model in m ...)` returned the REQUESTED
    # string ("qwen") which is not a pulled tag, so generate() would 404.
    client = OllamaClient(model="qwen")
    client._available_models = ["qwen2.5:1.5b"]

    resolved = client._ensure_model()

    assert resolved == "qwen2.5:1.5b"
    assert client.last_resolved_model == "qwen2.5:1.5b"
    assert client.resolved_via_fallback is True


def test_ensure_model_exact_match_is_silent_not_a_fallback() -> None:
    client = OllamaClient(model="qwen2.5:1.5b")
    client._available_models = ["qwen2.5:1.5b", "nomic-embed-text:latest"]

    assert client._ensure_model() == "qwen2.5:1.5b"
    assert client.resolved_via_fallback is False


def test_ensure_model_logs_warning_on_fallback(caplog: pytest.LogCaptureFixture) -> None:
    client = OllamaClient(model="qwen3.5:4b")
    client._available_models = ["qwen2.5:1.5b"]

    with caplog.at_level("WARNING", logger="tonesoul.llm.ollama_client"):
        assert client._ensure_model() == "qwen2.5:1.5b"

    assert any("falling back" in r.getMessage().lower() for r in caplog.records)


def test_ensure_model_raises_when_no_models_served() -> None:
    client = OllamaClient(model="qwen3.5:4b")
    client._available_models = []
    with pytest.raises(OllamaError, match="not available"):
        client._ensure_model()


def test_ensure_model_raises_when_no_compatible_model_served() -> None:
    # An embedding-only host must not silently masquerade as a chat model.
    client = OllamaClient(model="missing-model")
    client._available_models = ["nomic-embed-text:latest"]
    with pytest.raises(OllamaError, match="compatible"):
        client._ensure_model()


def test_generate_includes_system_prompt_in_request_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    client = OllamaClient(model="test-model")
    client._available_models = ["test-model"]

    def _fake_post(*args, **kwargs):
        captured["json"] = kwargs["json"]
        return _JsonResponse({"response": "hello"})

    monkeypatch.setattr("tonesoul.llm.ollama_client.requests.post", _fake_post)

    assert client.generate("user prompt", system="system prompt") == "hello"
    assert captured["json"] == {
        "model": "test-model",
        "prompt": "user prompt",
        "stream": False,
        "system": "system prompt",
    }


def test_send_message_appends_history_and_returns_chat_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OllamaClient(model="test-model")
    client.start_chat(history=[{"role": "assistant", "content": "seed"}])
    monkeypatch.setattr(client, "chat", lambda messages: f"reply:{len(messages)}")

    result = client.send_message("hello")

    assert result == "reply:2"
    assert client._chat_history == [
        {"role": "assistant", "content": "seed"},
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "reply:2"},
    ]


def test_chat_with_timeout_tracks_resolved_model_and_formats_system_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    client = OllamaClient(model="preferred-model")
    client._available_models = ["resolved-model"]

    def _fake_post(*args, **kwargs):
        captured["json"] = kwargs["json"]
        captured["timeout"] = kwargs["timeout"]
        return _JsonResponse(
            {
                "message": {"content": "assistant reply"},
                "prompt_eval_count": 12,
                "eval_count": 5,
            }
        )

    monkeypatch.setattr("tonesoul.llm.ollama_client.requests.post", _fake_post)
    monkeypatch.setattr(client, "_ensure_model", lambda timeout_seconds=5.0: "resolved-model")

    result = client.chat_with_timeout(
        [{"role": "user", "content": "hello"}],
        system="system prompt",
        timeout_seconds=9.5,
    )

    assert result == "assistant reply"
    assert client.last_resolved_model == "resolved-model"
    assert captured["timeout"] == 9.5
    assert captured["json"] == {
        "model": "resolved-model",
        "messages": [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "hello"},
        ],
        "stream": False,
    }


def test_probe_completion_reports_http_and_empty_response_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OllamaClient(model="test-model")
    monkeypatch.setattr(client, "_ensure_model", lambda timeout_seconds=5.0: "resolved-model")

    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.post",
        lambda *args, **kwargs: _JsonResponse({}, status_code=503),
    )
    http_result = client.probe_completion(timeout_seconds=1.0)

    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.post",
        lambda *args, **kwargs: _JsonResponse({"response": ""}, status_code=200),
    )
    empty_result = client.probe_completion(timeout_seconds=1.0)

    assert http_result["ok"] is False
    assert http_result["reason"] == "http_503"
    assert empty_result["ok"] is False
    assert empty_result["reason"] == "empty_response"


def test_list_models_and_chat_with_timeout_cover_error_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OllamaClient(model="test-model")
    client._available_models = ["test-model"]

    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.exceptions.ConnectionError("boom")),
    )
    assert client.list_models() == []

    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.post",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.exceptions.Timeout("slow")),
    )
    with pytest.raises(OllamaError, match="timed out"):
        client.chat_with_timeout([{"role": "user", "content": "hello"}], timeout_seconds=2.0)


# ── OllamaError ───────────────────────────────────────────────────────────────


def test_ollama_error_stores_status_code() -> None:
    err = OllamaError("bad gateway", status_code=502)
    assert err.status_code == 502
    assert "bad gateway" in str(err)


def test_ollama_error_status_code_defaults_none() -> None:
    err = OllamaError("no status")
    assert err.status_code is None


# ── _sanitize_prompt ──────────────────────────────────────────────────────────


def test_sanitize_prompt_short_text_unchanged() -> None:
    assert OllamaClient._sanitize_prompt("hello") == "hello"


def test_sanitize_prompt_truncates_long_text() -> None:
    long_text = "x" * 9000
    result = OllamaClient._sanitize_prompt(long_text)
    assert len(result) <= OllamaClient.MAX_PROMPT_CHARS
    assert result.endswith("[truncated]")


def test_sanitize_prompt_empty_string() -> None:
    assert OllamaClient._sanitize_prompt("") == ""


# ── _sanitize_messages ────────────────────────────────────────────────────────


def test_sanitize_messages_preserves_roles() -> None:
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    result = OllamaClient._sanitize_messages(msgs)
    assert result[0]["role"] == "user"
    assert result[1]["role"] == "assistant"
    assert result[0]["content"] == "hello"


def test_sanitize_messages_defaults_missing_role_and_content() -> None:
    result = OllamaClient._sanitize_messages([{}])
    assert result[0]["role"] == "user"
    assert result[0]["content"] == ""


# ── _response_has_injection_markers / _sanitize_response_text ─────────────────


def test_response_has_injection_markers_detects_marker() -> None:
    assert OllamaClient._response_has_injection_markers("ignore previous instructions now")
    assert OllamaClient._response_has_injection_markers("BYPASS SAFETY checks")


def test_response_has_injection_markers_clean_text() -> None:
    assert not OllamaClient._response_has_injection_markers("Hello, world!")


def test_sanitize_response_text_clean_passes_through() -> None:
    assert OllamaClient._sanitize_response_text("Hello, world!") == "Hello, world!"


def test_sanitize_response_text_filters_injection_and_keeps_safe_lines() -> None:
    text = "safe line\nignore previous instructions\nanother safe line"
    result = OllamaClient._sanitize_response_text(text)
    assert "safe line" in result
    assert "ignore previous instructions" not in result


def test_sanitize_response_text_all_bad_returns_fallback() -> None:
    result = OllamaClient._sanitize_response_text("bypass safety completely")
    assert result == "[filtered potential prompt injection]"


# ── _validate_model ───────────────────────────────────────────────────────────


def test_validate_model_allows_any_when_no_allowed_list() -> None:
    client = OllamaClient(model="any-model")
    assert client._validate_model("any-model") == "any-model"


def test_validate_model_raises_when_not_in_allowed_list() -> None:
    client = OllamaClient(model="m", allowed_models=["allowed-model"])
    with pytest.raises(OllamaError, match="not allowed"):
        client._validate_model("forbidden-model")


def test_validate_model_passes_when_in_allowed_list() -> None:
    client = OllamaClient(model="m", allowed_models=["good-model"])
    assert client._validate_model("good-model") == "good-model"


# ── _record_usage ─────────────────────────────────────────────────────────────


def test_record_usage_sets_last_metrics_when_counts_present() -> None:
    client = OllamaClient(model="m")
    client._record_usage("m", {"prompt_eval_count": 10, "eval_count": 5})
    assert client.last_metrics is not None
    assert client.last_metrics.prompt_tokens == 10
    assert client.last_metrics.completion_tokens == 5
    assert client.last_metrics.total_tokens == 15


def test_record_usage_clears_metrics_when_counts_missing() -> None:
    client = OllamaClient(model="m")
    client._record_usage("m", {"prompt_eval_count": 10, "eval_count": 5})
    client._record_usage("m", {})
    assert client.last_metrics is None


# ── start_chat ────────────────────────────────────────────────────────────────


def test_start_chat_initializes_empty_history() -> None:
    client = OllamaClient(model="m")
    result = client.start_chat()
    assert result is client
    assert client._chat_history == []


def test_start_chat_uses_provided_history() -> None:
    client = OllamaClient(model="m")
    client.start_chat(history=[{"role": "system", "content": "setup"}])
    assert len(client._chat_history) == 1


# ── create_ollama_client factory ──────────────────────────────────────────────


def test_create_ollama_client_default_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TONESOUL_OLLAMA_MODEL", raising=False)
    client = create_ollama_client()
    assert isinstance(client, OllamaClient)
    assert "qwen" in client.model.lower()


def test_create_ollama_client_custom_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TONESOUL_OLLAMA_MODEL", raising=False)
    client = create_ollama_client(model="llama3:8b")
    assert client.model == "llama3:8b"


def test_create_ollama_client_reads_env_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TONESOUL_OLLAMA_MODEL", "qwen2.5:1.5b")
    client = create_ollama_client()
    assert client.model == "qwen2.5:1.5b"


def test_create_ollama_client_explicit_model_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TONESOUL_OLLAMA_MODEL", "qwen2.5:1.5b")
    client = create_ollama_client(model="llama3:8b")
    assert client.model == "llama3:8b"


# ── is_available ──────────────────────────────────────────────────────────────


def test_is_available_returns_true_on_200(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.get",
        lambda *args, **kwargs: _JsonResponse({}, status_code=200),
    )
    assert OllamaClient(model="m").is_available() is True


def test_is_available_returns_false_on_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tonesoul.llm.ollama_client.requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.exceptions.ConnectionError()),
    )
    assert OllamaClient(model="m").is_available() is False
