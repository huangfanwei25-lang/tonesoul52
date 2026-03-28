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


def test_build_narrative_reasoning_prompt_uses_bounded_replay_shape():
    prompt = gemini_client._build_narrative_reasoning_prompt(
        {
            "verdict": "approve",
            "coherence": {"overall": 0.92},
            "votes": [
                {"perspective": "Guardian", "decision": "approve"},
                {"perspective": "Critic", "decision": "concern"},
            ],
            "divergence_analysis": {"core_divergence": "risk acceptable but contested"},
        }
    )

    assert "Goal function:" in prompt
    assert "P0:" in prompt
    assert "If any field is missing or weakly supported, mark [資料不足]" in prompt
    assert "Guardian: approve" in prompt
    assert "Critic: concern" in prompt
    assert "risk acceptable but contested" in prompt


def test_generate_narrative_reasoning_passes_structured_prompt_to_client():
    class _FakeClient:
        def __init__(self):
            self.prompt = ""

        def generate(self, prompt: str) -> str:
            self.prompt = prompt
            return "摘要完成"

    client = _FakeClient()

    result = gemini_client.generate_narrative_reasoning(
        client,
        {
            "verdict": "reject",
            "coherence": {"overall": 0.61},
            "votes": [{"perspective": "Guardian", "decision": "object"}],
            "divergence_analysis": {"core_divergence": "safety override"},
        },
    )

    assert result == "摘要完成"
    assert "final_verdict: reject" in client.prompt
    assert "coherence_score: 61%" in client.prompt
    assert "bounded replay-safe summary" in client.prompt
