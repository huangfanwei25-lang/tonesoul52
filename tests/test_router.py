from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.llm.router import LLMRouter, ThinkingTier, resolve_thinking_tier


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


# ── resolve_thinking_tier ────────────────────────────────────────────────────

def test_resolve_thinking_tier_maps_l2_and_l3_to_cloud() -> None:
    assert resolve_thinking_tier("L2") is ThinkingTier.CLOUD
    assert resolve_thinking_tier("L3") is ThinkingTier.CLOUD
    assert resolve_thinking_tier("l2") is ThinkingTier.CLOUD


def test_resolve_thinking_tier_defaults_to_local_for_other_values() -> None:
    assert resolve_thinking_tier("L1") is ThinkingTier.LOCAL
    assert resolve_thinking_tier("") is ThinkingTier.LOCAL
    assert resolve_thinking_tier(None) is ThinkingTier.LOCAL
    assert resolve_thinking_tier("unknown") is ThinkingTier.LOCAL


def test_resolve_thinking_tier_passthrough_for_non_auto_tier() -> None:
    assert resolve_thinking_tier(ThinkingTier.LOCAL) is ThinkingTier.LOCAL
    assert resolve_thinking_tier(ThinkingTier.CLOUD) is ThinkingTier.CLOUD


def test_resolve_thinking_tier_auto_tier_resolves_to_local_by_default() -> None:
    result = resolve_thinking_tier(ThinkingTier.AUTO)
    assert result is ThinkingTier.LOCAL


# ── LLMRouter static helpers ──────────────────────────────────────────────────

def test_normalize_backend_name_lowercases_and_strips() -> None:
    assert LLMRouter._normalize_backend_name("  Ollama  ") == "ollama"
    assert LLMRouter._normalize_backend_name("LMStudio") == "lmstudio"
    assert LLMRouter._normalize_backend_name("") is None
    assert LLMRouter._normalize_backend_name(None) is None


def test_tier_from_backend_maps_local_and_cloud() -> None:
    assert LLMRouter._tier_from_backend("ollama") is ThinkingTier.LOCAL
    assert LLMRouter._tier_from_backend("lmstudio") is ThinkingTier.LOCAL
    assert LLMRouter._tier_from_backend("gemini") is ThinkingTier.CLOUD
    assert LLMRouter._tier_from_backend("unknown") is None
    assert LLMRouter._tier_from_backend(None) is None


def test_coerce_tier_returns_tier_directly_for_non_auto() -> None:
    assert LLMRouter._coerce_tier(ThinkingTier.LOCAL) is ThinkingTier.LOCAL
    assert LLMRouter._coerce_tier(ThinkingTier.CLOUD) is ThinkingTier.CLOUD


def test_coerce_tier_auto_falls_through_to_resolve_thinking_tier() -> None:
    result = LLMRouter._coerce_tier(ThinkingTier.AUTO, alert_level="L2")
    assert result is ThinkingTier.CLOUD


def test_coerce_tier_string_values() -> None:
    assert LLMRouter._coerce_tier("local") is ThinkingTier.LOCAL
    assert LLMRouter._coerce_tier("cloud") is ThinkingTier.CLOUD


# ── LLMRouter.prime ───────────────────────────────────────────────────────────

def test_prime_seeds_cached_client_and_backend() -> None:
    router = LLMRouter()
    fake_client = SimpleNamespace(model="test")
    returned = router.prime(fake_client, backend="ollama")
    assert returned is fake_client
    assert router._cached_client is fake_client
    assert router._cached_backend == "ollama"
    assert router._local_client is fake_client
    assert router._local_backend == "ollama"


def test_prime_with_none_client_returns_none() -> None:
    router = LLMRouter()
    result = router.prime(None)
    assert result is None
    assert router._cached_client is None
