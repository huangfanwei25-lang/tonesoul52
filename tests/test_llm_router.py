import pytest

from tonesoul.llm.router import LLMRouter, ThinkingTier, resolve_thinking_tier
from tonesoul.schemas import LLMCallMetrics


class _FakeClient:
    def __init__(self, metrics=None) -> None:
        self.last_metrics = metrics


class _FakeProbedClient:
    def __init__(self, probe_result) -> None:
        self.model = "qwen3.5:8b"
        self._probe_result = probe_result
        self.calls: list[float] = []

    def probe_completion(self, *, timeout_seconds: float = 10.0):
        self.calls.append(timeout_seconds)
        return dict(self._probe_result, timeout_seconds=timeout_seconds)


class _FakeClientWithoutProbe:
    def __init__(self, model="qwen3.5:8b") -> None:
        self.model = model


class _FakeExplodingClient:
    def __init__(self, error: Exception, model="qwen3.5:8b") -> None:
        self.model = model
        self._error = error
        self.calls: list[float] = []

    def probe_completion(self, *, timeout_seconds: float = 10.0):
        self.calls.append(timeout_seconds)
        raise self._error


def test_router_exposes_last_metrics_from_cached_client() -> None:
    router = LLMRouter()
    metrics = LLMCallMetrics(
        model="qwen3.5:8b",
        prompt_tokens=9,
        completion_tokens=4,
        total_tokens=13,
    )
    router._cached_client = _FakeClient(metrics=metrics)
    router._cached_backend = "ollama"

    assert router.last_metrics == metrics
    assert router.active_backend == "ollama"


def test_router_last_metrics_is_none_without_cached_client() -> None:
    router = LLMRouter()

    assert router.last_metrics is None


def test_router_inference_check_uses_client_probe() -> None:
    router = LLMRouter()
    client = _FakeProbedClient(
        {
            "ok": True,
            "supported": True,
            "backend": "lmstudio",
            "model": "qwen3.5:8b",
            "reason": "ready",
            "latency_ms": 800,
        }
    )
    router._cached_client = client
    router._cached_backend = "lmstudio"

    payload = router.inference_check(timeout_seconds=4.0)

    assert payload["ok"] is True
    assert payload["supported"] is True
    assert payload["backend"] == "lmstudio"
    assert payload["model"] == "qwen3.5:8b"
    assert payload["probe_latency_ms"] == 800
    assert payload["timeout_seconds"] == 4.0
    assert client.calls == [pytest.approx(4.0, rel=0.0, abs=0.01)]


def test_router_inference_check_spends_budget_on_selection(monkeypatch) -> None:
    router = LLMRouter()
    client = _FakeProbedClient(
        {
            "ok": False,
            "supported": True,
            "backend": "lmstudio",
            "model": "qwen3.5:8b",
            "reason": "timeout",
            "latency_ms": 1200,
        }
    )
    router._cached_client = client
    router._cached_backend = "lmstudio"
    perf = iter([100.0, 100.0, 101.5, 101.5])
    monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: next(perf))

    payload = router.inference_check(timeout_seconds=4.0)

    assert client.calls == [pytest.approx(2.5, rel=0.0, abs=0.01)]
    assert payload["selection_latency_ms"] == 1500
    assert payload["probe_latency_ms"] == 1200
    assert payload["latency_ms"] == 2700
    assert payload["timeout_seconds"] == 4.0


def test_router_inference_check_times_out_when_selection_exhausts_budget(monkeypatch) -> None:
    router = LLMRouter()
    client = _FakeProbedClient(
        {
            "ok": True,
            "supported": True,
            "backend": "lmstudio",
            "model": "qwen3.5:8b",
            "reason": "ready",
        }
    )
    router._cached_client = client
    router._cached_backend = "lmstudio"
    perf = iter([200.0, 200.0, 202.2, 202.2])
    monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: next(perf))

    payload = router.inference_check(timeout_seconds=2.0)

    assert payload["ok"] is False
    assert payload["reason"] == "timeout"
    assert payload["selection_latency_ms"] == 2200
    assert payload["latency_ms"] == 2200
    assert client.calls == []


def test_router_inference_check_returns_no_client_when_resolution_fails(monkeypatch) -> None:
    router = LLMRouter()
    monkeypatch.setattr(router, "get_client", lambda: None)

    payload = router.inference_check(timeout_seconds=3.0)

    assert payload["ok"] is False
    assert payload["supported"] is False
    assert payload["backend"] is None
    assert payload["reason"] == "no_client"
    assert payload["timeout_seconds"] == 3.0


def test_router_inference_check_reports_probe_unsupported() -> None:
    router = LLMRouter()
    router._cached_client = _FakeClientWithoutProbe()
    router._cached_backend = "lmstudio"

    payload = router.inference_check(timeout_seconds=2.5)

    assert payload["ok"] is True
    assert payload["supported"] is False
    assert payload["backend"] == "lmstudio"
    assert payload["model"] == "qwen3.5:8b"
    assert payload["reason"] == "probe_unsupported"
    assert payload["timeout_seconds"] == 2.5


def test_router_inference_check_reports_probe_exception() -> None:
    router = LLMRouter()
    client = _FakeExplodingClient(RuntimeError("backend exploded"))
    router._cached_client = client
    router._cached_backend = "ollama"

    payload = router.inference_check(timeout_seconds=5.0)

    assert payload["ok"] is False
    assert payload["supported"] is True
    assert payload["backend"] == "ollama"
    assert payload["model"] == "qwen3.5:8b"
    assert payload["reason"] == "probe_exception:RuntimeError"
    assert payload["detail"] == "backend exploded"
    assert payload["timeout_seconds"] == 5.0
    assert len(client.calls) == 1


def test_router_inference_check_normalizes_non_dict_probe_result() -> None:
    router = LLMRouter()
    client = _FakeProbedClient(probe_result={"ok": True})
    client._probe_result = "not-a-dict"
    router._cached_client = client
    router._cached_backend = "lmstudio"

    payload = router.inference_check(timeout_seconds=1.5)

    assert payload["ok"] is False
    assert payload["supported"] is True
    assert payload["backend"] == "lmstudio"
    assert payload["model"] == "qwen3.5:8b"
    assert payload["timeout_seconds"] == 1.5
    assert "probe_latency_ms" not in payload


def test_router_inference_check_normalizes_non_primitive_model() -> None:
    router = LLMRouter()

    class _ModelObject:
        model_name = "custom-model"

    client = _FakeClientWithoutProbe(model=_ModelObject())
    router._cached_client = client
    router._cached_backend = "lmstudio"

    payload = router.inference_check(timeout_seconds=2.0)

    assert payload["model"] == "custom-model"
    assert payload["reason"] == "probe_unsupported"


# ── ThinkingTier ──────────────────────────────────────────────────────────────

class TestThinkingTier:
    def test_enum_values(self):
        assert ThinkingTier.LOCAL.value == "local"
        assert ThinkingTier.CLOUD.value == "cloud"
        assert ThinkingTier.AUTO.value == "auto"

    def test_str_comparison(self):
        assert ThinkingTier.LOCAL == "local"
        assert ThinkingTier.CLOUD == "cloud"


# ── resolve_thinking_tier ─────────────────────────────────────────────────────

class TestResolveThinkingTier:
    def test_l2_gives_cloud(self):
        assert resolve_thinking_tier("L2") is ThinkingTier.CLOUD

    def test_l3_gives_cloud(self):
        assert resolve_thinking_tier("L3") is ThinkingTier.CLOUD

    def test_l2_lowercase_gives_cloud(self):
        assert resolve_thinking_tier("l2") is ThinkingTier.CLOUD

    def test_other_string_gives_local(self):
        assert resolve_thinking_tier("L1") is ThinkingTier.LOCAL
        assert resolve_thinking_tier("unknown") is ThinkingTier.LOCAL

    def test_none_gives_local(self):
        assert resolve_thinking_tier(None) is ThinkingTier.LOCAL

    def test_thinking_tier_local_passthrough(self):
        assert resolve_thinking_tier(ThinkingTier.LOCAL) is ThinkingTier.LOCAL

    def test_thinking_tier_cloud_passthrough(self):
        assert resolve_thinking_tier(ThinkingTier.CLOUD) is ThinkingTier.CLOUD

    def test_thinking_tier_auto_resolves_to_local(self):
        assert resolve_thinking_tier(ThinkingTier.AUTO) is ThinkingTier.LOCAL

    def test_object_with_value_attr(self):
        class _Obj:
            value = "L2"
        assert resolve_thinking_tier(_Obj()) is ThinkingTier.CLOUD


# ── LLMRouter.__init__ ────────────────────────────────────────────────────────

class TestLLMRouterInit:
    def test_default_preferred_is_auto(self):
        router = LLMRouter()
        assert router._preferred == "auto"

    def test_custom_preferred_backend(self):
        router = LLMRouter(preferred_backend="ollama")
        assert router._preferred == "ollama"

    def test_env_var_overrides_preferred(self, monkeypatch):
        monkeypatch.setenv("TONESOUL_LLM_BACKEND", "gemini")
        router = LLMRouter(preferred_backend="ollama")
        assert router._preferred == "gemini"

    def test_env_var_stripped(self, monkeypatch):
        monkeypatch.setenv("TONESOUL_LLM_BACKEND", "  lmstudio  ")
        router = LLMRouter()
        assert router._preferred == "lmstudio"

    def test_empty_env_var_uses_preferred(self, monkeypatch):
        monkeypatch.setenv("TONESOUL_LLM_BACKEND", "")
        router = LLMRouter(preferred_backend="ollama")
        assert router._preferred == "ollama"

    def test_initial_state_all_none(self):
        router = LLMRouter()
        assert router._cached_client is None
        assert router._cached_backend is None
        assert router._local_client is None
        assert router._cloud_client is None
        assert router._last_thinking_tier is None


# ── Static helpers ────────────────────────────────────────────────────────────

class TestNormalizeBackendName:
    def test_strips_and_lowercases(self):
        assert LLMRouter._normalize_backend_name("  OLLAMA  ") == "ollama"

    def test_empty_returns_none(self):
        assert LLMRouter._normalize_backend_name("   ") is None

    def test_none_returns_none(self):
        assert LLMRouter._normalize_backend_name(None) is None

    def test_non_string_returns_none(self):
        assert LLMRouter._normalize_backend_name(42) is None

    def test_valid_backend_name(self):
        assert LLMRouter._normalize_backend_name("gemini") == "gemini"


class TestTierFromBackend:
    def test_lmstudio_is_local(self):
        assert LLMRouter._tier_from_backend("lmstudio") is ThinkingTier.LOCAL

    def test_ollama_is_local(self):
        assert LLMRouter._tier_from_backend("ollama") is ThinkingTier.LOCAL

    def test_gemini_is_cloud(self):
        assert LLMRouter._tier_from_backend("gemini") is ThinkingTier.CLOUD

    def test_unknown_returns_none(self):
        assert LLMRouter._tier_from_backend("custom") is None

    def test_none_returns_none(self):
        assert LLMRouter._tier_from_backend(None) is None

    def test_mixed_case_lmstudio(self):
        assert LLMRouter._tier_from_backend("LMStudio") is ThinkingTier.LOCAL


class TestDeadlineAndRemaining:
    def test_deadline_adds_timeout(self, monkeypatch):
        monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: 100.0)
        assert LLMRouter._deadline(5.0) == pytest.approx(105.0)

    def test_deadline_clamps_small_timeout(self, monkeypatch):
        monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: 100.0)
        assert LLMRouter._deadline(0.0) == pytest.approx(100.1)

    def test_remaining_seconds_positive(self, monkeypatch):
        monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: 100.0)
        assert LLMRouter._remaining_seconds(105.0) == pytest.approx(5.0)

    def test_remaining_seconds_clamps_to_zero(self, monkeypatch):
        monkeypatch.setattr("tonesoul.llm.router.time.perf_counter", lambda: 110.0)
        assert LLMRouter._remaining_seconds(105.0) == 0.0


# ── LLMRouter.prime ───────────────────────────────────────────────────────────

class TestPrime:
    def test_prime_returns_client(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        result = router.prime(client, backend="ollama")
        assert result is client

    def test_prime_sets_cached_client(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="ollama")
        assert router._cached_client is client
        assert router._cached_backend == "ollama"

    def test_prime_none_returns_none(self):
        router = LLMRouter()
        assert router.prime(None) is None
        assert router._cached_client is None

    def test_prime_local_backend_sets_local(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="lmstudio")
        assert router._local_client is client
        assert router._local_backend == "lmstudio"

    def test_prime_cloud_backend_sets_cloud(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="gemini")
        assert router._cloud_client is client
        assert router._cloud_backend == "gemini"

    def test_prime_unknown_backend_no_tier_stored(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="custom")
        assert router._local_client is None
        assert router._cloud_client is None

    def test_prime_no_backend_does_not_set_cached_backend(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client)
        assert router._cached_backend is None


# ── LLMRouter._coerce_tier ────────────────────────────────────────────────────

class TestCoerceTier:
    def test_local_enum_passthrough(self):
        assert LLMRouter._coerce_tier(ThinkingTier.LOCAL) is ThinkingTier.LOCAL

    def test_cloud_enum_passthrough(self):
        assert LLMRouter._coerce_tier(ThinkingTier.CLOUD) is ThinkingTier.CLOUD

    def test_auto_resolves_via_alert_level(self):
        result = LLMRouter._coerce_tier(ThinkingTier.AUTO, alert_level="L2")
        assert result is ThinkingTier.CLOUD

    def test_string_local_gives_local(self):
        assert LLMRouter._coerce_tier("local") is ThinkingTier.LOCAL

    def test_string_cloud_gives_cloud(self):
        assert LLMRouter._coerce_tier("cloud") is ThinkingTier.CLOUD

    def test_unknown_string_falls_back_to_alert_level(self):
        result = LLMRouter._coerce_tier("unknown", alert_level="L3")
        assert result is ThinkingTier.CLOUD

    def test_none_falls_back_to_local(self):
        result = LLMRouter._coerce_tier(None)
        assert result is ThinkingTier.LOCAL


# ── LLMRouter._activate_client ────────────────────────────────────────────────

class TestActivateClient:
    def test_sets_cached_client(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._activate_client(client, backend="ollama", requested_tier=ThinkingTier.LOCAL)
        assert router._cached_client is client

    def test_sets_last_thinking_tier_from_backend(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._activate_client(client, backend="gemini", requested_tier=ThinkingTier.LOCAL)
        assert router._last_thinking_tier == "cloud"

    def test_falls_back_to_requested_tier_when_backend_unknown(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._activate_client(client, backend=None, requested_tier=ThinkingTier.LOCAL)
        assert router._last_thinking_tier == "local"

    def test_last_thinking_tier_property(self):
        router = LLMRouter()
        assert router.last_thinking_tier is None
        router._activate_client(_FakeClientWithoutProbe(), backend="ollama", requested_tier=ThinkingTier.LOCAL)
        assert router.last_thinking_tier == "local"


# ── LLMRouter.reset ───────────────────────────────────────────────────────────

class TestReset:
    def test_reset_clears_all_cached_state(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="ollama")
        router._last_thinking_tier = "local"
        router.reset()
        assert router._cached_client is None
        assert router._cached_backend is None
        assert router._local_client is None
        assert router._local_backend is None
        assert router._cloud_client is None
        assert router._cloud_backend is None
        assert router._last_thinking_tier is None

    def test_reset_allows_re_resolution(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router.prime(client, backend="ollama")
        router.reset()
        # After reset, get_client tries live backends — just verify it returns None when none available
        # by patching _direct_resolve
        router._direct_resolve = lambda: None
        assert router.get_client() is None


# ── LLMRouter.get_client ──────────────────────────────────────────────────────

class TestGetClient:
    def test_returns_cached_when_set(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._cached_client = client
        assert router.get_client() is client

    def test_backend_resolver_used(self):
        class _Decision:
            client = _FakeClientWithoutProbe()
            backend = "lmstudio"

        router = LLMRouter(backend_resolver=lambda preferred_backend: _Decision())
        result = router.get_client()
        assert result is _Decision.client
        assert router._cached_backend == "lmstudio"

    def test_backend_resolver_returning_none_falls_through(self, monkeypatch):
        router = LLMRouter(backend_resolver=lambda preferred_backend: None)
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_direct_resolve", lambda: client)
        result = router.get_client()
        assert result is client

    def test_backend_resolver_exception_falls_through(self, monkeypatch):
        def _bad_resolver(**_kw):
            raise RuntimeError("resolver exploded")

        router = LLMRouter(backend_resolver=_bad_resolver)
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_direct_resolve", lambda: client)
        result = router.get_client()
        assert result is client

    def test_direct_resolve_used_when_no_resolver(self, monkeypatch):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_direct_resolve", lambda: client)
        result = router.get_client()
        assert result is client


# ── LLMRouter._direct_resolve ─────────────────────────────────────────────────

class TestDirectResolve:
    def test_preferred_backend_tried_first(self, monkeypatch):
        router = LLMRouter(preferred_backend="ollama")
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_try_ollama", lambda: client)
        result = router._direct_resolve()
        assert result is client
        assert router._cached_backend == "ollama"

    def test_preferred_backend_miss_falls_to_waterfall(self, monkeypatch):
        router = LLMRouter(preferred_backend="ollama")
        lmstudio_client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_try_ollama", lambda: None)
        monkeypatch.setattr(router, "_try_lmstudio", lambda: lmstudio_client)
        monkeypatch.setattr(router, "_try_gemini", lambda: None)
        result = router._direct_resolve()
        assert result is lmstudio_client
        assert router._cached_backend == "lmstudio"

    def test_all_backends_fail_returns_none(self, monkeypatch):
        router = LLMRouter()
        monkeypatch.setattr(router, "_try_ollama", lambda: None)
        monkeypatch.setattr(router, "_try_lmstudio", lambda: None)
        monkeypatch.setattr(router, "_try_gemini", lambda: None)
        result = router._direct_resolve()
        assert result is None

    def test_auto_uses_waterfall_order(self, monkeypatch):
        router = LLMRouter(preferred_backend="auto")
        gemini_client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_try_ollama", lambda: None)
        monkeypatch.setattr(router, "_try_lmstudio", lambda: None)
        monkeypatch.setattr(router, "_try_gemini", lambda: gemini_client)
        result = router._direct_resolve()
        assert result is gemini_client
        assert router._cached_backend == "gemini"


# ── LLMRouter.health_check ────────────────────────────────────────────────────

class TestHealthCheck:
    def test_all_unavailable(self, monkeypatch):
        router = LLMRouter()
        monkeypatch.setattr(LLMRouter, "_try_ollama", staticmethod(lambda: None))
        monkeypatch.setattr(LLMRouter, "_try_lmstudio", staticmethod(lambda: None))
        monkeypatch.setattr(LLMRouter, "_try_gemini", staticmethod(lambda: None))
        result = router.health_check()
        assert result == {"ollama": False, "lmstudio": False, "gemini": False}

    def test_partial_availability(self, monkeypatch):
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(LLMRouter, "_try_ollama", staticmethod(lambda: client))
        monkeypatch.setattr(LLMRouter, "_try_lmstudio", staticmethod(lambda: None))
        monkeypatch.setattr(LLMRouter, "_try_gemini", staticmethod(lambda: None))
        router = LLMRouter()
        result = router.health_check()
        assert result == {"ollama": True, "lmstudio": False, "gemini": False}

    def test_all_available(self, monkeypatch):
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(LLMRouter, "_try_ollama", staticmethod(lambda: client))
        monkeypatch.setattr(LLMRouter, "_try_lmstudio", staticmethod(lambda: client))
        monkeypatch.setattr(LLMRouter, "_try_gemini", staticmethod(lambda: client))
        router = LLMRouter()
        result = router.health_check()
        assert result == {"ollama": True, "lmstudio": True, "gemini": True}


# ── LLMRouter.chat ────────────────────────────────────────────────────────────

class _ChatClient:
    def __init__(self):
        self.history_received = None
        self.prompt_received = None

    def start_chat(self, history):
        self.history_received = history

    def send_message(self, prompt):
        self.prompt_received = prompt
        return "response-text"


class _NoChatClient:
    """Has no send_message."""
    pass


class _NoHistoryClient:
    """Has send_message but no start_chat."""
    def send_message(self, prompt):
        return "ok"


class TestChat:
    def test_basic_chat_returns_response(self):
        router = LLMRouter()
        client = _ChatClient()
        router._cached_client = client
        result = router.chat(prompt="hello")
        assert result == "response-text"
        assert client.prompt_received == "hello"

    def test_chat_passes_history(self):
        router = LLMRouter()
        client = _ChatClient()
        router._cached_client = client
        history = [{"role": "user", "content": "prior"}]
        router.chat(history=history, prompt="follow-up")
        assert client.history_received == history

    def test_chat_empty_history_defaults_to_empty_list(self):
        router = LLMRouter()
        client = _ChatClient()
        router._cached_client = client
        router.chat(prompt="hi")
        assert client.history_received == []

    def test_chat_raises_when_no_client(self):
        router = LLMRouter()
        router._direct_resolve = lambda: None
        with pytest.raises(RuntimeError, match="No active LLM client"):
            router.chat(prompt="hi")

    def test_chat_raises_when_no_send_message(self):
        router = LLMRouter()
        router._cached_client = _NoChatClient()
        with pytest.raises(RuntimeError, match="send_message"):
            router.chat(prompt="hi")

    def test_chat_raises_when_history_but_no_start_chat(self):
        router = LLMRouter()
        router._cached_client = _NoHistoryClient()
        with pytest.raises(RuntimeError, match="history-aware"):
            router.chat(history=[{"role": "user", "content": "hi"}], prompt="follow-up")

    def test_chat_no_history_no_start_chat_ok(self):
        router = LLMRouter()
        router._cached_client = _NoHistoryClient()
        result = router.chat(prompt="hi")
        assert result == "ok"


# ── LLMRouter.chat_with_tier ──────────────────────────────────────────────────

class TestChatWithTier:
    def _router_with_client(self, client) -> LLMRouter:
        router = LLMRouter()
        router._cached_client = client
        router._cached_backend = "lmstudio"
        return router

    def test_basic_chat_with_tier_local(self):
        client = _ChatClient()
        router = self._router_with_client(client)
        result = router.chat_with_tier(prompt="hi", tier=ThinkingTier.LOCAL)
        assert result == "response-text"

    def test_chat_with_tier_sets_last_thinking_tier(self):
        client = _ChatClient()
        router = self._router_with_client(client)
        router.chat_with_tier(prompt="hi", tier=ThinkingTier.LOCAL)
        assert router.last_thinking_tier == "local"

    def test_chat_with_tier_raises_no_client(self):
        router = LLMRouter()
        router._resolve_client_for_tier = lambda tier: (None, None)
        with pytest.raises(RuntimeError, match="No active LLM client"):
            router.chat_with_tier(prompt="hi", tier=ThinkingTier.LOCAL)

    def test_chat_with_tier_auto_resolves(self):
        client = _ChatClient()
        router = LLMRouter()
        router._cached_client = client
        router._cached_backend = None  # unnamed → returned as-is by _resolve_client_for_tier
        result = router.chat_with_tier(prompt="hi", tier="auto")
        assert result == "response-text"

    def test_chat_with_tier_cloud_alert(self):
        client = _ChatClient()
        router = LLMRouter()
        router._cloud_client = client
        router._cloud_backend = "gemini"
        result = router.chat_with_tier(prompt="analyze", tier=ThinkingTier.CLOUD, alert_level="L2")
        assert result == "response-text"
        assert router.last_thinking_tier == "cloud"


# ── LLMRouter._resolve_client_for_tier ────────────────────────────────────────

class TestResolveClientForTier:
    def test_unnamed_cached_client_returned_directly(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._cached_client = client
        # no _cached_backend set → returns (client, None) without trying live backends
        result_client, result_backend = router._resolve_client_for_tier(ThinkingTier.LOCAL)
        assert result_client is client
        assert result_backend is None

    def test_local_tier_uses_local_client(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._local_client = client
        router._local_backend = "lmstudio"
        result_client, result_backend = router._resolve_client_for_tier(ThinkingTier.LOCAL)
        assert result_client is client
        assert result_backend == "lmstudio"

    def test_cloud_tier_uses_cloud_client(self):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        router._cloud_client = client
        router._cloud_backend = "gemini"
        result_client, result_backend = router._resolve_client_for_tier(ThinkingTier.CLOUD)
        assert result_client is client
        assert result_backend == "gemini"

    def test_local_tier_falls_back_to_lmstudio(self, monkeypatch):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_try_lmstudio", lambda: client)
        result_client, result_backend = router._resolve_client_for_tier(ThinkingTier.LOCAL)
        assert result_client is client
        assert result_backend == "lmstudio"

    def test_cloud_tier_falls_back_to_gemini(self, monkeypatch):
        router = LLMRouter()
        client = _FakeClientWithoutProbe()
        monkeypatch.setattr(router, "_try_gemini", lambda: client)
        result_client, result_backend = router._resolve_client_for_tier(ThinkingTier.CLOUD)
