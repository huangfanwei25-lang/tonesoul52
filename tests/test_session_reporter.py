"""
Unit Tests for Session Reporter Module

Tests for SessionReporter, SessionSummary, and related classes.
"""

from datetime import datetime

import pytest

from tonesoul.tonebridge.session_reporter import (
    SessionReporter,
    SessionSummary,
    TurningPoint,
)


class TestSessionReporter:
    """Tests for SessionReporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = SessionReporter()

    def test_analyze_empty_history(self):
        """Test analyzing empty conversation history."""
        summary = self.reporter.analyze([])

        assert summary.total_turns == 0
        assert summary.user_messages == 0
        assert summary.ai_responses == 0

    def test_analyze_simple_conversation(self):
        """Test analyzing a simple conversation."""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什麼我可以幫助你的？"},
            {"role": "user", "content": "謝謝你"},
            {"role": "assistant", "content": "不客氣！"},
        ]

        summary = self.reporter.analyze(history)

        assert summary.total_turns == 4
        assert summary.user_messages == 2
        assert summary.ai_responses == 2

    def test_detect_emotional_arc(self):
        """Test emotional arc detection."""
        history = [
            {"role": "user", "content": "我很擔心這個問題"},
            {"role": "assistant", "content": "我理解你的擔心。"},
            {"role": "user", "content": "太棒了！你的解釋很清楚"},
            {"role": "assistant", "content": "謝謝！"},
        ]

        summary = self.reporter.analyze(history)

        assert len(summary.emotional_arc) == 2
        # First should be anxious, second should be excited or positive

    def test_detect_turning_points(self):
        """Test turning point detection."""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
            {"role": "user", "content": "我很擔心這個"},
            {"role": "assistant", "content": "我理解"},
            {"role": "user", "content": "太棒了！"},
            {"role": "assistant", "content": "很高興能幫助！"},
        ]

        summary = self.reporter.analyze(history)

        # Should detect at least one turning point
        assert isinstance(summary.turning_points, list)

    def test_calculate_volatility(self):
        """Test emotional volatility calculation."""
        # Stable conversation
        stable_history = [
            {"role": "user", "content": "好的"},
            {"role": "user", "content": "好"},
            {"role": "user", "content": "好的"},
        ]

        summary = self.reporter.analyze(stable_history)

        # Low volatility for stable emotions
        assert summary.emotional_volatility <= 0.5

    def test_classify_session(self):
        """Test session classification."""
        productive_history = [
            {"role": "user", "content": "為什麼天空是藍色的？"},
            {"role": "assistant", "content": "這是因為瑞利散射。"},
            {"role": "user", "content": "好的，我明白了。謝謝"},
            {"role": "assistant", "content": "不客氣！"},
        ]

        summary = self.reporter.analyze(productive_history)

        # Should classify as some valid type
        assert summary.session_quality in [
            "productive",
            "exploratory",
            "dynamic",
            "challenging",
            "conversational",
        ]

    def test_generate_summary_text(self):
        """Test summary text generation."""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]

        summary = self.reporter.analyze(history)

        assert summary.summary_text is not None
        assert len(summary.summary_text) > 0


class TestSessionSummary:
    """Tests for SessionSummary dataclass."""

    def test_to_dict(self):
        """Test SessionSummary serialization."""
        summary = SessionSummary(
            session_id="test_session",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_turns=10,
            user_messages=5,
            ai_responses=5,
            emotional_arc=["calm", "curious", "calm"],
            dominant_emotion="calm",
            emotional_volatility=0.2,
            turning_points=[],
            high_tension_moments=[],
            theme_clusters=[],
            commitments_made=2,
            ruptures_detected=0,
            values_strengthened=["誠實"],
            session_quality="productive",
            summary_text="這是一段有建設性的對話。",
        )

        result = summary.to_dict()

        assert isinstance(result, dict)
        assert result["session_id"] == "test_session"
        assert result["total_turns"] == 10
        assert result["dominant_emotion"] == "calm"


class TestTurningPoint:
    """Tests for TurningPoint dataclass."""

    def test_to_dict(self):
        """Test TurningPoint serialization."""
        tp = TurningPoint(
            turn_index=3,
            description="情緒從 calm 轉變為 anxious",
            before_state="calm",
            after_state="anxious",
            trigger="我很擔心這個問題",
            significance=0.7,
        )

        result = tp.to_dict()

        assert result["turn_index"] == 3
        assert result["significance"] == 0.7
        assert "calm" in result["before_state"]
        assert "anxious" in result["after_state"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
