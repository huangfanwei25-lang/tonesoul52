from __future__ import annotations

import pytest
import requests

from tonesoul.llm.ollama_client import OllamaClient, OllamaError


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


def test_ensure_model_returns_first_available_then_original_when_none_loaded() -> None:
    client = OllamaClient(model="missing-model")
    client._available_models = ["phi4:mini"]
    assert client._ensure_model() == "phi4:mini"

    client._available_models = []
    assert client._ensure_model() == "missing-model"


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
