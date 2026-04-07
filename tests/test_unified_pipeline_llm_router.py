from __future__ import annotations

from unittest.mock import MagicMock

from tonesoul.alert_escalation import AlertLevel
from tonesoul.unified_pipeline import UnifiedPipeline


class _ExplodingClient:
    def __init__(self) -> None:
        self.model = "mock-model"
        self.last_metrics = None

    def start_chat(self, history):
        raise AssertionError("pipeline should use LLMRouter.chat instead of client.start_chat")

    def send_message(self, prompt: str) -> str:
        raise AssertionError("pipeline should use LLMRouter.chat instead of client.send_message")


class _FakeRouter:
    def __init__(self, client) -> None:
        self._client = client
        self.active_backend = "lmstudio"
        self.last_metrics = None
        self.last_thinking_tier = "local"
        self.chat = MagicMock(return_value="legacy-router-response")
        self.chat_with_tier = MagicMock(return_value="router-mediated response")

    def prime(self, client, *, backend=None):
        self._client = client
        if backend:
            self.active_backend = backend
        return client

    def get_client(self):
        return self._client


def test_pipeline_uses_llm_router_chat_for_generation() -> None:
    pipeline = UnifiedPipeline()
    client = _ExplodingClient()
    router = _FakeRouter(client)
    pipeline._llm_client = client
    pipeline._llm_router = router
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_tension_engine = MagicMock(return_value=None)

    result = pipeline.process(
        user_message="Please outline a practical engineering plan for this subsystem.",
        user_tier="premium",
        user_id="router-chat-test",
    )

    router.chat_with_tier.assert_called_once()
    router.chat.assert_not_called()
    _, kwargs = router.chat_with_tier.call_args
    assert kwargs["history"] == []
    assert "Please outline a practical engineering plan" in kwargs["prompt"]
    assert kwargs["alert_level"] == AlertLevel.CLEAR
    assert result.response.startswith("router-mediated response")
    assert result.dispatch_trace["thinking_tier"] == "local"
