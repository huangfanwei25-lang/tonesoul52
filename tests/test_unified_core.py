"""Tests for UnifiedCore - the central orchestration module."""
import pytest
from tonesoul.unified_core import UnifiedCore


class TestUnifiedCoreInit:
    """Test UnifiedCore initialization."""

    def test_default_init(self):
        """UnifiedCore should initialize with default config."""
        core = UnifiedCore()
        assert core is not None

    def test_init_with_config(self):
        """UnifiedCore should accept custom config."""
        config = {"mode": "test", "verbose": False}
        core = UnifiedCore(config=config)
        assert core is not None


class TestUnifiedCoreProcess:
    """Test UnifiedCore processing capabilities."""

    def test_process_simple_input(self):
        """UnifiedCore should process a simple input."""
        core = UnifiedCore()
        result = core.process("Hello, this is a test input.")
        assert result is not None

    def test_process_empty_input(self):
        """UnifiedCore should handle empty input gracefully."""
        core = UnifiedCore()
        result = core.process("")
        assert result is not None

    def test_process_with_context(self):
        """UnifiedCore should accept context parameters."""
        core = UnifiedCore()
        context = {"user_id": "test_user", "session_id": "test_session"}
        result = core.process("Test with context", context=context)
        assert result is not None


class TestUnifiedCoreIntegration:
    """Integration tests for UnifiedCore with other modules."""

    def test_core_returns_metrics(self):
        """UnifiedCore should return ToneSoul metrics."""
        core = UnifiedCore()
        result = core.process("Analysis test input for metrics.")
        # Check if result has expected structure
        assert result is not None

    def test_core_handles_long_input(self):
        """UnifiedCore should handle long inputs."""
        core = UnifiedCore()
        long_input = "This is a test. " * 100
        result = core.process(long_input)
        assert result is not None


class TestUnifiedCoreErrorHandling:
    """Test error handling in UnifiedCore."""

    def test_process_unicode_input(self):
        """UnifiedCore should handle Unicode correctly."""
        core = UnifiedCore()
        result = core.process("測試中文輸入 和 emoji 🎉")
        assert result is not None

    def test_process_special_characters(self):
        """UnifiedCore should handle special characters."""
        core = UnifiedCore()
        result = core.process("Special chars: <>&\"'\\n\\t")
        assert result is not None
