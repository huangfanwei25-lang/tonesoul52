import pytest

from tonesoul.llm.router import LLMRouter
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
