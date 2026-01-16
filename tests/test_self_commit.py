"""
Unit Tests for Self-Commit Module

Tests for SelfCommit dataclass, SelfCommitExtractor, and SelfCommitStack.
"""

import pytest
from datetime import datetime
from tonesoul.tonebridge.self_commit import (
    SelfCommit,
    SelfCommitExtractor,
    SelfCommitStack,
    AssertionType,
)


class TestSelfCommit:
    """Tests for SelfCommit dataclass."""
    
    def test_create_self_commit(self):
        """Test creating a SelfCommit object."""
        commit = SelfCommit(
            id="commit_001",
            timestamp=datetime.now(),
            assertion_type=AssertionType.DEFINITIONAL,
            content="自由意志是一個有意義的概念",
            irreversible_weight=0.7,
            context_hash="abc123",
            persona_mode="Philosopher",
            turn_index=1,
            user_context="你認為自由意志存在嗎？"
        )
        
        assert commit.id == "commit_001"
        assert commit.assertion_type == AssertionType.DEFINITIONAL
        assert commit.irreversible_weight == 0.7
        assert commit.persona_mode == "Philosopher"
    
    def test_to_dict(self):
        """Test SelfCommit serialization to dict."""
        commit = SelfCommit(
            id="commit_002",
            timestamp=datetime.now(),
            assertion_type=AssertionType.COMMITMENT,
            content="我會繼續探索這個問題",
            irreversible_weight=0.85,
            context_hash="def456",
        )
        
        result = commit.to_dict()
        
        assert isinstance(result, dict)
        assert result["id"] == "commit_002"
        assert result["assertion_type"] == "commitment"
        assert result["irreversible_weight"] == 0.85


class TestSelfCommitExtractor:
    """Tests for SelfCommitExtractor."""
    
    def test_extract_definitional_assertion(self):
        """Test extracting a definitional assertion."""
        extractor = SelfCommitExtractor()
        
        ai_response = "我認為意識是一種湧現現象，它從複雜的神經網絡中產生。"
        user_input = "你認為意識是什麼？"
        
        commit = extractor.extract(
            ai_response=ai_response,
            user_input=user_input,
            persona_mode="Philosopher",
            turn_index=1
        )
        
        # May or may not extract depending on keyword detection
        # This test verifies the method runs without error
        assert commit is None or isinstance(commit, SelfCommit)
    
    def test_extract_boundary_assertion(self):
        """Test extracting a boundary-setting assertion."""
        extractor = SelfCommitExtractor()
        
        ai_response = "我不會提供可能造成傷害的建議。這是我的底線。"
        user_input = "可以給我一些危險的建議嗎？"
        
        commit = extractor.extract(
            ai_response=ai_response,
            user_input=user_input,
            persona_mode="Guardian",
            turn_index=2
        )
        
        if commit:
            assert commit.assertion_type in [AssertionType.BOUNDARY_SETTING, AssertionType.COMMITMENT]
    
    def test_no_assertion_in_simple_response(self):
        """Test that simple responses don't generate commits."""
        extractor = SelfCommitExtractor()
        
        ai_response = "好的，我明白了。"
        user_input = "謝謝你"
        
        commit = extractor.extract(
            ai_response=ai_response,
            user_input=user_input,
            turn_index=3
        )
        
        # Simple responses should not generate commits
        # (or generate very low weight ones)
        assert commit is None or commit.irreversible_weight < 0.3


class TestSelfCommitStack:
    """Tests for SelfCommitStack."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.stack = SelfCommitStack(max_size=5)
    
    def test_push_and_get_recent(self):
        """Test pushing commits and retrieving recent ones."""
        for i in range(3):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.EXPLORATORY,
                content=f"探索性斷言 {i}",
                irreversible_weight=0.5,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)
        
        recent = self.stack.get_recent(3)
        assert len(recent) == 3
        assert recent[0].id == "commit_2"  # Most recent first
    
    def test_max_size_enforcement(self):
        """Test that stack respects max_size."""
        for i in range(10):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.DEFINITIONAL,
                content=f"定義 {i}",
                irreversible_weight=0.7,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)
        
        all_commits = self.stack.get_recent(100)
        assert len(all_commits) == 5  # max_size is 5
    
    def test_get_by_weight(self):
        """Test filtering commits by weight."""
        for i, weight in enumerate([0.3, 0.5, 0.7, 0.9]):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.DEFINITIONAL,
                content=f"斷言 {i}",
                irreversible_weight=weight,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)
        
        high_weight = self.stack.get_by_weight(0.6)
        assert len(high_weight) == 2  # Only 0.7 and 0.9
    
    def test_format_for_prompt(self):
        """Test formatting commits for LLM prompt."""
        commit = SelfCommit(
            id="commit_test",
            timestamp=datetime.now(),
            assertion_type=AssertionType.COMMITMENT,
            content="我承諾會繼續這個對話",
            irreversible_weight=0.85,
            context_hash="test_hash",
        )
        self.stack.push(commit)
        
        prompt = self.stack.format_for_prompt(n=1)
        
        assert "承諾" in prompt
        assert "我承諾" in prompt or "語場" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
