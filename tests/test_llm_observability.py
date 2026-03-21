from __future__ import annotations

from unittest.mock import MagicMock, patch


def test_ollama_client_records_usage_metrics_and_token_meter(tmp_path) -> None:
    from tonesoul.llm.ollama_client import OllamaClient
    from tonesoul.observability.token_meter import TokenMeter

    meter = TokenMeter(log_dir=tmp_path)
    client = OllamaClient(model="test-model", meter=meter)
    client._available_models = ["test-model"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "hello world",
        "prompt_eval_count": 120,
        "eval_count": 30,
    }

    with patch("tonesoul.llm.ollama_client.requests.post", return_value=mock_response):
        result = client.generate("hello")

    assert result == "hello world"
    assert client.last_metrics is not None
    assert client.last_metrics.prompt_tokens == 120
    assert client.last_metrics.completion_tokens == 30
    assert client.last_metrics.total_tokens == 150
    totals = meter.get_session_totals()
    assert totals["calls"] == 1
    assert totals["total_tokens"] == 150


def test_ollama_client_leaves_metrics_empty_when_usage_is_missing() -> None:
    from tonesoul.llm.ollama_client import OllamaClient

    client = OllamaClient(model="test-model")
    client._available_models = ["test-model"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "hello world"}

    with patch("tonesoul.llm.ollama_client.requests.post", return_value=mock_response):
        result = client.generate("hello")

    assert result == "hello world"
    assert client.last_metrics is None


def test_lmstudio_client_records_usage_metrics_and_token_meter(tmp_path) -> None:
    from tonesoul.llm.lmstudio_client import LMStudioClient
    from tonesoul.observability.token_meter import TokenMeter

    meter = TokenMeter(log_dir=tmp_path)
    client = LMStudioClient(model="test-model", meter=meter)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "hi from lmstudio"}}],
        "usage": {
            "prompt_tokens": 44,
            "completion_tokens": 11,
            "total_tokens": 55,
        },
    }

    with patch("tonesoul.llm.lmstudio_client.requests.post", return_value=mock_response):
        result = client.chat([{"role": "user", "content": "hello"}])

    assert result == "hi from lmstudio"
    assert client.last_metrics is not None
    assert client.last_metrics.prompt_tokens == 44
    assert client.last_metrics.completion_tokens == 11
    assert client.last_metrics.total_tokens == 55
    totals = meter.get_session_totals()
    assert totals["calls"] == 1
    assert totals["total_tokens"] == 55


def test_lmstudio_client_leaves_metrics_empty_when_usage_is_missing() -> None:
    from tonesoul.llm.lmstudio_client import LMStudioClient

    client = LMStudioClient(model="test-model")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "hi from lmstudio"}}],
    }

    with patch("tonesoul.llm.lmstudio_client.requests.post", return_value=mock_response):
        result = client.chat([{"role": "user", "content": "hello"}])

    assert result == "hi from lmstudio"
    assert client.last_metrics is None
