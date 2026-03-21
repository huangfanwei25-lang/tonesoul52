from __future__ import annotations

from tonesoul.alert_escalation import AlertLevel
from tonesoul.llm.router import LLMRouter, ThinkingTier, resolve_thinking_tier


class _FakeChatClient:
    def __init__(self, label: str) -> None:
        self.label = label
        self.history_calls: list[list[dict]] = []
        self.prompts: list[str] = []

    def start_chat(self, history):
        self.history_calls.append(list(history or []))
        return self

    def send_message(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"{self.label}:{prompt}"


def test_resolve_thinking_tier_none_defaults_to_local() -> None:
    assert resolve_thinking_tier(None) is ThinkingTier.LOCAL


def test_resolve_thinking_tier_l1_uses_local() -> None:
    assert resolve_thinking_tier(AlertLevel.L1) is ThinkingTier.LOCAL


def test_resolve_thinking_tier_l2_uses_cloud() -> None:
    assert resolve_thinking_tier(AlertLevel.L2) is ThinkingTier.CLOUD


def test_resolve_thinking_tier_l3_uses_cloud() -> None:
    assert resolve_thinking_tier(AlertLevel.L3) is ThinkingTier.CLOUD


def test_chat_with_tier_local_prefers_lmstudio(monkeypatch) -> None:
    router = LLMRouter()
    client = _FakeChatClient("local")
    monkeypatch.setattr(router, "_try_lmstudio", lambda: client)
    monkeypatch.setattr(router, "_try_gemini", lambda: None)

    response = router.chat_with_tier(
        history=[{"role": "user", "content": "hi"}],
        prompt="Draft safely.",
        tier="local",
    )

    assert response == "local:Draft safely."
    assert client.history_calls == [[{"role": "user", "content": "hi"}]]
    assert router.active_backend == "lmstudio"
    assert router.last_thinking_tier == "local"


def test_chat_with_tier_cloud_prefers_gemini(monkeypatch) -> None:
    router = LLMRouter()
    client = _FakeChatClient("cloud")
    monkeypatch.setattr(router, "_try_lmstudio", lambda: None)
    monkeypatch.setattr(router, "_try_gemini", lambda: client)

    response = router.chat_with_tier(
        history=[],
        prompt="Draft carefully.",
        tier="cloud",
    )

    assert response == "cloud:Draft carefully."
    assert client.history_calls == [[]]
    assert router.active_backend == "gemini"
    assert router.last_thinking_tier == "cloud"


def test_chat_with_tier_auto_uses_local_when_alert_is_clear(monkeypatch) -> None:
    router = LLMRouter()
    client = _FakeChatClient("local")
    monkeypatch.setattr(router, "_try_lmstudio", lambda: client)
    monkeypatch.setattr(router, "_try_gemini", lambda: None)

    response = router.chat_with_tier(
        history=[],
        prompt="Stay practical.",
        tier="auto",
        alert_level=None,
    )

    assert response == "local:Stay practical."
    assert router.active_backend == "lmstudio"
    assert router.last_thinking_tier == "local"


def test_chat_with_tier_falls_back_without_crashing_when_requested_tier_is_unavailable(
    monkeypatch,
) -> None:
    router = LLMRouter()
    fallback = _FakeChatClient("fallback")
    router._cached_backend = "ollama"
    monkeypatch.setattr(router, "_try_lmstudio", lambda: None)
    monkeypatch.setattr(router, "_try_gemini", lambda: None)
    monkeypatch.setattr(router, "get_client", lambda: fallback)

    response = router.chat_with_tier(
        history=[],
        prompt="Use any available backend.",
        tier="local",
    )

    assert response == "fallback:Use any available backend."
    assert router.last_thinking_tier == "local"
