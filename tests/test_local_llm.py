from unittest.mock import MagicMock, patch

import requests

from tonesoul.local_llm import ask_local_llm


@patch("tonesoul.local_llm.requests.post")
def test_ask_local_llm_success(mock_post):
    """Test successful generation from local LLM."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": "This is a local response."}}
    mock_post.return_value = mock_response

    result = ask_local_llm("Hello")
    assert result == "This is a local response."

    # Verify the structure forces think=False
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["json"]["think"] is False
    assert call_kwargs["json"]["model"] == "qwen3.5:4b"


@patch("tonesoul.local_llm.requests.post")
def test_ask_local_llm_connection_error(mock_post):
    """Test fallback when Ollama is not running."""
    mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect")

    result = ask_local_llm("Hello")
    assert "本機運算單元暫時無法服務" in result


@patch("tonesoul.local_llm.requests.post")
def test_ask_local_llm_timeout(mock_post):
    """Test fallback when Ollama hangs or times out."""
    mock_post.side_effect = requests.exceptions.Timeout("Read timeout")

    result = ask_local_llm("Hello")
    assert "本機運算單元暫時無法服務" in result
