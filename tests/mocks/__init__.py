"""
Mock classes for testing - Following Ralph patterns

Provides:
- MockLLMClient: Basic mock for LLM responses
- SlowMockLLMClient: Mock with configurable delay for timeout testing
"""

from .mock_llm_client import MockLLMClient, SlowMockLLMClient

__all__ = ["MockLLMClient", "SlowMockLLMClient"]
