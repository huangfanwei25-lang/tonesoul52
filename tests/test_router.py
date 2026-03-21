from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.llm.router import LLMRouter


def test_inference_check_returns_success_payload() -> None:
    router = LLMRouter()
    client = SimpleNamespace(
        model="mock-model",
        probe_completion=MagicMock(
            return_value={
                "ok": True,
                "supported": True,
                "backend": "lmstudio",
                "model": "mock-model",
                "reason": "ready",
                "latency_ms": 40,
            }
        ),
    )
    router._cached_backend = "lmstudio"
    router.get_client = MagicMock(return_value=client)

    payload = router.inference_check(timeout_seconds=2.0)

    assert payload["ok"] is True
    assert payload["supported"] is True
    assert payload["backend"] == "lmstudio"
    assert payload["model"] == "mock-model"
    assert payload["probe_latency_ms"] == 40
    client.probe_completion.assert_called_once()


def test_inference_check_returns_timeout_when_selection_exhausts_budget(monkeypatch) -> None:
    router = LLMRouter()
    client = SimpleNamespace(
        model="mock-model",
        probe_completion=MagicMock(return_value={"ok": True, "latency_ms": 10}),
    )
    router._cached_backend = "lmstudio"
    router.get_client = MagicMock(return_value=client)

    perf = iter([10.0, 10.0, 12.1, 12.1])
    monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: next(perf))

    payload = router.inference_check(timeout_seconds=2.0)

    assert payload["ok"] is False
    assert payload["reason"] == "timeout"
    assert payload["backend"] == "lmstudio"
    assert payload["selection_latency_ms"] == 2100
    client.probe_completion.assert_not_called()
