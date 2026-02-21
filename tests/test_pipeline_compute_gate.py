"""
Integration tests for UnifiedPipeline + ComputeGate routing.
"""
import pytest
from unittest.mock import MagicMock
from tonesoul.unified_pipeline import UnifiedPipeline
from tonesoul.gates.compute import RoutingPath

def test_pipeline_pass_local_fast_route():
    """Test that short, free, low-tension paths bypass the cloud and return locally immediately."""
    pipeline = UnifiedPipeline()
    response = pipeline.process(
        user_message="Hello",
        user_tier="free"
    )
    # The pipeline should short-circuit and not call the LLM backend
    assert "Local Model" in response.response
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
        prior_tension={"delta_t": 0.9} # Forces high tension routing
    )
    
    assert response.dispatch_trace.get("journal_eligible") is True
    assert response.dispatch_trace.get("route") == RoutingPath.PASS_COUNCIL.value
