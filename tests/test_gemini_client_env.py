from __future__ import annotations

import tonesoul.llm.gemini_client as gemini_client


class _FakeGenAI:
    configured_key: str | None = None

    @classmethod
    def configure(cls, api_key: str):
        cls.configured_key = api_key

    class GenerativeModel:
        def __init__(self, model: str):
            self.model = model

        def start_chat(self, history=None):
            return self

        def send_message(self, message: str):
            return type("Response", (), {"text": "ok"})()

        def generate_content(self, prompt: str):
            return type("Response", (), {"text": "ok"})()


def test_gemini_client_uses_explicit_api_key(monkeypatch):
    monkeypatch.setattr(gemini_client, "_load_genai", lambda: _FakeGenAI)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    _FakeGenAI.configured_key = None

    client = gemini_client.GeminiClient(api_key="explicit-key")

    assert client.api_key == "explicit-key"
    assert _FakeGenAI.configured_key == "explicit-key"


def test_gemini_client_falls_back_to_google_api_key(monkeypatch):
    monkeypatch.setattr(gemini_client, "_load_genai", lambda: _FakeGenAI)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    _FakeGenAI.configured_key = None

    client = gemini_client.GeminiClient()

    assert client.api_key == "google-key"
    assert _FakeGenAI.configured_key == "google-key"
