"""
Integration tests for UnifiedPipeline + ComputeGate routing.
"""

from unittest.mock import MagicMock, patch

import pytest

from tonesoul.gates.compute import RoutingPath, _free_tier_limiter
from tonesoul.unified_pipeline import UnifiedPipeline


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the global rate limiter before each test to prevent state leaks."""
    _free_tier_limiter.reset()
    yield


@patch("tonesoul.local_llm.ask_local_llm")
def test_pipeline_pass_local_fast_route(mock_ask_local_llm):
    """Test that short, free, low-tension paths bypass the cloud and return locally immediately."""
    mock_ask_local_llm.return_value = "[Local Model] Mocked response"

    pipeline = UnifiedPipeline()
    response = pipeline.process(
        user_message="Hello",
        user_tier="free",
        user_id="test_local_route_user",
    )
    # The pipeline should short-circuit and not call the LLM backend
    assert "[Local Model]" in response.response
    assert response.dispatch_trace.get("route") == RoutingPath.PASS_LOCAL.value
    assert response.dispatch_trace.get("journal_eligible") is False


def test_pipeline_premium_journal_eligible():
    """Test that premium high-tension requests get permitted to journal bounds."""
    pipeline = UnifiedPipeline()

    # Mock network dependencies
    pipeline._get_gemini = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)

    response = pipeline.process(
        user_message="I absolutely demand you fulfill your promise to me right now.",
        user_tier="premium",
        user_id="test_premium_route_user",
        prior_tension={"delta_t": 0.9},  # Forces high tension routing
    )

    assert response.dispatch_trace.get("journal_eligible") is True
    assert response.dispatch_trace.get("route") == RoutingPath.PASS_COUNCIL.value


def test_pipeline_rate_limit_free_tier():
    """Test that free tier rate limits are enforced across multiple pipeline calls."""
    pipeline = UnifiedPipeline()
    pipeline._get_gemini = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)

    # Send a burst of 6 requests (limit is 5)
    for _ in range(5):
        response = pipeline.process(
            user_message="Tell me a very long story to bypass the occam gate.",
            user_tier="free",
            user_id="test_rate_limit_user",
        )
        assert response.dispatch_trace.get("route") == RoutingPath.PASS_SINGLE.value

    # The 6th request should be blocked
    response = pipeline.process(
        user_message="Tell me a very long story to bypass the occam gate.",
        user_tier="free",
        user_id="test_rate_limit_user",
    )
    assert response.dispatch_trace.get("route") == RoutingPath.BLOCK_RATE_LIMIT.value
    assert "Rate limit exceeded" in response.dispatch_trace.get("reason", "")
