"""Unit tests for the self-commit module."""

from datetime import datetime

import pytest

from tonesoul.tonebridge.self_commit import (
    AssertionType,
    SelfCommit,
    SelfCommitExtractor,
    SelfCommitStack,
)


class TestSelfCommit:
    """Tests for SelfCommit dataclass."""

    def test_create_self_commit(self):
        commit = SelfCommit(
            id="commit_001",
            timestamp=datetime.now(),
            assertion_type=AssertionType.DEFINITIONAL,
            content="This definition should remain stable.",
            irreversible_weight=0.7,
            context_hash="abc123",
            persona_mode="Philosopher",
            turn_index=1,
            user_context="Explain the principle clearly.",
        )

        assert commit.id == "commit_001"
        assert commit.assertion_type == AssertionType.DEFINITIONAL
        assert commit.irreversible_weight == 0.7
        assert commit.persona_mode == "Philosopher"

    def test_to_dict(self):
        commit = SelfCommit(
            id="commit_002",
            timestamp=datetime.now(),
            assertion_type=AssertionType.COMMITMENT,
            content="I will keep this boundary visible.",
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
        extractor = SelfCommitExtractor()

        ai_response = "這代表一個可追蹤的定義，因此後續回答要維持一致。"
        user_input = "請先說清楚這個定義。"

        commit = extractor.extract(
            ai_response=ai_response,
            user_input=user_input,
            persona_mode="Philosopher",
            turn_index=1,
        )

        assert commit is not None
        assert commit.assertion_type == AssertionType.DEFINITIONAL

    def test_extract_boundary_assertion(self):
        extractor = SelfCommitExtractor()

        ai_response = "我不會接受沒有證據支撐的結論，這是目前的邊界。"
        user_input = "那你會直接接受這個說法嗎？"

        commit = extractor.extract(
            ai_response=ai_response,
            user_input=user_input,
            persona_mode="Guardian",
            turn_index=2,
        )

        assert commit is not None
        assert commit.assertion_type == AssertionType.BOUNDARY_SETTING

    def test_no_assertion_in_simple_response(self):
        extractor = SelfCommitExtractor()

        ai_response = "好的，我知道了。"
        user_input = "收到嗎？"

        commit = extractor.extract(ai_response=ai_response, user_input=user_input, turn_index=3)

        assert commit is None or commit.irreversible_weight < 0.3


class TestSelfCommitStack:
    """Tests for SelfCommitStack."""

    def setup_method(self):
        self.stack = SelfCommitStack(max_size=5)

    def test_push_and_get_recent(self):
        for i in range(3):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.EXPLORATORY,
                content=f"Exploratory note {i}",
                irreversible_weight=0.5,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)

        recent = self.stack.get_recent(3)
        assert len(recent) == 3
        assert recent[0].id == "commit_2"

    def test_max_size_enforcement(self):
        for i in range(10):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.DEFINITIONAL,
                content=f"Definition {i}",
                irreversible_weight=0.7,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)

        all_commits = self.stack.get_recent(100)
        assert len(all_commits) == 5

    def test_get_by_weight(self):
        for i, weight in enumerate([0.3, 0.5, 0.7, 0.9]):
            commit = SelfCommit(
                id=f"commit_{i}",
                timestamp=datetime.now(),
                assertion_type=AssertionType.DEFINITIONAL,
                content=f"Assertion {i}",
                irreversible_weight=weight,
                context_hash=f"hash_{i}",
            )
            self.stack.push(commit)

        high_weight = self.stack.get_high_weight(0.6)
        assert len(high_weight) == 2

    def test_format_for_prompt(self):
        commit = SelfCommit(
            id="commit_test",
            timestamp=datetime.now(),
            assertion_type=AssertionType.COMMITMENT,
            content="keep this commitment visible",
            irreversible_weight=0.85,
            context_hash="test_hash",
        )
        self.stack.push(commit)

        prompt = self.stack.format_for_prompt(n=1)

        assert "自我承諾注入" in prompt
        assert "高優先提醒" in prompt
        assert "P0:" in prompt

    def test_format_for_prompt_prioritizes_weight_before_recency(self):
        newer_weaker = SelfCommit(
            id="commit_new",
            timestamp=datetime(2026, 3, 29, 12, 0, 0),
            assertion_type=AssertionType.EXPLORATORY,
            content="new but weaker",
            irreversible_weight=0.55,
            context_hash="hash_new",
            turn_index=8,
        )
        older_stronger = SelfCommit(
            id="commit_old",
            timestamp=datetime(2026, 3, 29, 11, 0, 0),
            assertion_type=AssertionType.BOUNDARY_SETTING,
            content="older but stronger",
            irreversible_weight=0.95,
            context_hash="hash_old",
            turn_index=4,
        )
        self.stack.push(newer_weaker)
        self.stack.push(older_stronger)

        prompt = self.stack.format_for_prompt(n=1)

        assert "older but stronger" in prompt
        assert "new but weaker" not in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
