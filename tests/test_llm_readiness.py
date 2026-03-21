from __future__ import annotations

import requests

from tonesoul.llm.lmstudio_client import LMStudioClient
from tonesoul.llm.ollama_client import OllamaClient


class _FakeResponse:
    def __init__(self, payload, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def test_lmstudio_probe_completion_reports_readiness_without_mutating_metrics(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake_post(*args, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        return _FakeResponse(
            {
                "choices": [{"message": {"content": "READY"}}],
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 2,
                    "total_tokens": 6,
                },
            }
        )

    monkeypatch.setattr(
        requests,
        "post",
        _fake_post,
    )
    client = LMStudioClient(host="http://localhost:1234", model="qwen3.5-9b")

    result = client.probe_completion(timeout_seconds=3.0)

    assert result["ok"] is True
    assert result["backend"] == "lmstudio"
    assert result["model"] == "qwen3.5-9b"
    assert result["reason"] == "ready"
    assert result["usage_available"] is True
    connect_timeout, read_timeout = captured["timeout"]
    assert connect_timeout <= 0.75
    assert connect_timeout + read_timeout <= 3.0
    assert client.last_metrics is None


def test_ollama_probe_completion_handles_timeout_without_mutating_metrics(monkeypatch) -> None:
    def _raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("slow backend")

    monkeypatch.setattr(requests, "post", _raise_timeout)
    monkeypatch.setattr(
        OllamaClient, "_ensure_model", lambda self, timeout_seconds=5.0: "qwen3.5:4b"
    )
    client = OllamaClient(host="http://localhost:11434", model="qwen3.5:4b")

    result = client.probe_completion(timeout_seconds=1.5)

    assert result["ok"] is False
    assert result["backend"] == "ollama"
    assert result["model"] == "qwen3.5:4b"
    assert result["reason"] == "timeout"
    assert client.last_metrics is None


def test_lmstudio_probe_completion_shares_budget_with_model_resolution(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake_list_models(self, timeout_seconds: float = 5.0):
        captured["list_timeout"] = timeout_seconds
        return ["qwen3.5-9b"]

    def _fake_post(*args, **kwargs):
        captured["request_timeout"] = kwargs.get("timeout")
        return _FakeResponse({"choices": [{"message": {"content": "READY"}}]})

    monkeypatch.setattr(LMStudioClient, "list_models", _fake_list_models)
    monkeypatch.setattr(requests, "post", _fake_post)
    client = LMStudioClient(host="http://localhost:1234", model=None)

    result = client.probe_completion(timeout_seconds=2.0)

    assert result["ok"] is True
    assert captured["list_timeout"] <= 2.0
    connect_timeout, read_timeout = captured["request_timeout"]
    assert connect_timeout + read_timeout <= 2.0


def test_ollama_probe_completion_uses_bounded_request_timeout(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        OllamaClient, "_ensure_model", lambda self, timeout_seconds=5.0: "qwen3.5:4b"
    )

    def _fake_post(*args, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        return _FakeResponse({"response": "READY"})

    monkeypatch.setattr(requests, "post", _fake_post)
    client = OllamaClient(host="http://localhost:11434", model="qwen3.5:4b")

    result = client.probe_completion(timeout_seconds=2.0)

    assert result["ok"] is True
    connect_timeout, read_timeout = captured["timeout"]
    assert connect_timeout + read_timeout <= 2.0
