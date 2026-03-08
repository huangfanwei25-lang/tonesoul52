"""Tests for Ollama -> Gemini runtime fallback."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# A1. OllamaClient raises OllamaError on failures
# ---------------------------------------------------------------------------


class TestOllamaClientRaisesOnFailure:
    """OllamaClient.generate() and .chat() must raise OllamaError on non-200."""

    def test_generate_raises_on_500(self):
        from tonesoul.llm.ollama_client import OllamaClient, OllamaError

        client = OllamaClient(model="test-model")
        client._available_models = ["test-model"]

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("tonesoul.llm.ollama_client.requests.post", return_value=mock_response):
            with pytest.raises(OllamaError) as exc_info:
                client.generate("hello")
            assert exc_info.value.status_code == 500
            assert "500" in str(exc_info.value)

    def test_chat_raises_on_500(self):
        from tonesoul.llm.ollama_client import OllamaClient, OllamaError

        client = OllamaClient(model="test-model")
        client._available_models = ["test-model"]

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("tonesoul.llm.ollama_client.requests.post", return_value=mock_response):
            with pytest.raises(OllamaError) as exc_info:
                client.chat([{"role": "user", "content": "hello"}])
            assert exc_info.value.status_code == 500

    def test_generate_raises_on_timeout(self):
        import requests as req_lib

        from tonesoul.llm.ollama_client import OllamaClient, OllamaError

        client = OllamaClient(model="test-model")
        client._available_models = ["test-model"]

        with patch(
            "tonesoul.llm.ollama_client.requests.post",
            side_effect=req_lib.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(OllamaError) as exc_info:
                client.generate("hello")
            assert "超時" in str(exc_info.value)

    def test_chat_raises_on_connection_error(self):
        import requests as req_lib

        from tonesoul.llm.ollama_client import OllamaClient, OllamaError

        client = OllamaClient(model="test-model")
        client._available_models = ["test-model"]

        with patch(
            "tonesoul.llm.ollama_client.requests.post",
            side_effect=req_lib.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(OllamaError) as exc_info:
                client.chat([{"role": "user", "content": "hello"}])
            assert "連接失敗" in str(exc_info.value)

    def test_generate_returns_on_200(self):
        from tonesoul.llm.ollama_client import OllamaClient

        client = OllamaClient(model="test-model")
        client._available_models = ["test-model"]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "hello world"}

        with patch("tonesoul.llm.ollama_client.requests.post", return_value=mock_response):
            result = client.generate("hello")
            assert result == "hello world"


# ---------------------------------------------------------------------------
# A3. local_llm falls back to Gemini
# ---------------------------------------------------------------------------


class TestLocalLlmFallback:
    """ask_local_llm should return error message when Ollama fails."""

    def test_returns_error_on_connection_error(self):
        import requests as req_lib

        from tonesoul.local_llm import ask_local_llm

        with patch(
            "tonesoul.local_llm.requests.post",
            side_effect=req_lib.exceptions.ConnectionError("refused"),
        ):
            result = ask_local_llm("hello")

        assert "無法服務" in result

    def test_returns_error_on_unexpected_exception(self):
        from tonesoul.local_llm import ask_local_llm

        with patch(
            "tonesoul.local_llm.requests.post",
            side_effect=RuntimeError("unexpected"),
        ):
            result = ask_local_llm("hello")

        assert "未知錯誤" in result
