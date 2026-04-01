from __future__ import annotations

import pytest

from tonesoul.gates.compute import RoutingPath
from tonesoul.unified_pipeline import (
    UnifiedPipeline,
    UnifiedResponse,
    _read_bool_env,
    _read_positive_int_env,
)


def test_unified_pipeline_initializes() -> None:
    pipeline = UnifiedPipeline()
    assert pipeline is not None


def test_read_bool_env_parses_truthy_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TONESOUL_TEST_BOOL", "YeS")

    assert _read_bool_env("TONESOUL_TEST_BOOL") is True


def test_read_bool_env_uses_default_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TONESOUL_TEST_BOOL", raising=False)

    assert _read_bool_env("TONESOUL_TEST_BOOL", default=True) is True
    assert _read_bool_env("TONESOUL_TEST_BOOL", default=False) is False


def test_read_positive_int_env_clamps_invalid_and_non_positive_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TONESOUL_TEST_INT", "0")
    assert _read_positive_int_env("TONESOUL_TEST_INT", 3) == 1

    monkeypatch.setenv("TONESOUL_TEST_INT", "bad")
    assert _read_positive_int_env("TONESOUL_TEST_INT", 3) == 3


def test_fast_route_dispatch_trace_marks_bypassed_council(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("tonesoul.local_llm.ask_local_llm", lambda message: "[Local Model] ok")

    result = UnifiedPipeline().process(
        user_message="hello",
        user_tier="free",
        user_id="dispatch-test-user",
    )

    assert result.dispatch_trace.get("route") == RoutingPath.PASS_LOCAL.value
    assert result.council_verdict.get("verdict") == "bypassed"
    metadata = result.council_verdict.get("metadata")
    assert metadata is None or isinstance(metadata, dict)


def test_unified_response_to_dict_preserves_dispatch_trace() -> None:
    payload = UnifiedResponse(
        response="ok",
        council_verdict={"verdict": "approve"},
        tonebridge_analysis={},
        inner_narrative="trace",
        dispatch_trace={"route": "pass_local"},
    ).to_dict()

    assert payload["dispatch_trace"] == {"route": "pass_local"}
