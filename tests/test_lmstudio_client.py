from __future__ import annotations

import pytest

from tonesoul.llm.lmstudio_client import LMStudioClient, LMStudioError


class _JsonResponse:
    def __init__(self, payload: dict, status_code: int = 200, text: str = "") -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def json(self) -> dict:
        return self._payload


def test_get_model_prefers_non_embedding_model_and_caches_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LMStudioClient(model=None)
    monkeypatch.setattr(
        client, "list_models", lambda timeout_seconds=5.0: ["embed-small", "qwen-14b"]
    )

    assert client._get_model() == "qwen-14b"
    assert client.model == "qwen-14b"


def test_get_model_falls_back_to_first_model_or_raises_when_none_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LMStudioClient(model=None)
    monkeypatch.setattr(client, "list_models", lambda timeout_seconds=5.0: ["embed-small"])
    assert client._get_model() == "embed-small"

    client = LMStudioClient(model=None)
    monkeypatch.setattr(client, "list_models", lambda timeout_seconds=5.0: [])
    with pytest.raises(LMStudioError, match="No models loaded"):
        client._get_model()


def test_generate_delegates_to_chat_with_system_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LMStudioClient(model="test-model")
    captured: dict[str, object] = {}

    def _fake_chat(messages, system=None):
        captured["messages"] = messages
        captured["system"] = system
        return "generated"

    monkeypatch.setattr(client, "chat", _fake_chat)

    assert client.generate("hello", system="sys") == "generated"
    assert captured["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hello"},
    ]
    assert captured["system"] is None


def test_send_message_updates_history_and_returns_chat_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LMStudioClient(model="test-model")
    client.start_chat(history=[{"role": "assistant", "content": "seed"}])
    monkeypatch.setattr(client, "chat", lambda messages: f"reply:{len(messages)}")

    result = client.send_message("hello")

    assert result == "reply:2"
    assert client._chat_history == [
        {"role": "assistant", "content": "seed"},
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "reply:2"},
    ]


def test_probe_completion_reports_model_resolution_error_and_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LMStudioClient(model=None)
    monkeypatch.setattr(
        client,
        "_get_model",
        lambda timeout_seconds=5.0: (_ for _ in ()).throw(LMStudioError("resolution failed")),
    )
    resolution_result = client.probe_completion(timeout_seconds=1.0)

    client = LMStudioClient(model="test-model")
    monkeypatch.setattr(client, "_get_model", lambda timeout_seconds=5.0: "test-model")
    monkeypatch.setattr(
        "tonesoul.llm.lmstudio_client.requests.post",
        lambda *args, **kwargs: _JsonResponse({"choices": [{"message": {"content": ""}}]}, 200),
    )
    empty_result = client.probe_completion(timeout_seconds=1.0)

    assert resolution_result["reason"] == "model_resolution_error"
    assert resolution_result["ok"] is False
    assert empty_result["reason"] == "empty_response"
    assert empty_result["ok"] is False


def test_chat_formats_system_message_and_raises_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LMStudioClient(model="test-model")
    captured: dict[str, object] = {}

    def _fake_post(*args, **kwargs):
        captured["json"] = kwargs["json"]
        return _JsonResponse({}, status_code=503, text="service unavailable")

    monkeypatch.setattr("tonesoul.llm.lmstudio_client.requests.post", _fake_post)

    with pytest.raises(LMStudioError, match="HTTP 503"):
        client.chat([{"role": "user", "content": "hello"}], system="sys")

    assert captured["json"] == {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "hello"},
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "stream": False,
    }
