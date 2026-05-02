"""Tests for tonesoul.tonebridge.self_commit — pure helpers and SelfCommitStack."""

from __future__ import annotations

import pytest

from tonesoul.tonebridge.self_commit import (
    AssertionType,
    SelfCommit,
    SelfCommitExtractor,
    SelfCommitStack,
)

# ── SelfCommit.to_dict / from_dict ────────────────────────────────────────────


class TestSelfCommitRoundtrip:
    def _make(self, **kw):
        from datetime import datetime

        defaults = dict(
            id="c1",
            timestamp=datetime(2026, 1, 1, 0, 0, 0),
            assertion_type=AssertionType.DEFINITIONAL,
            content="X 是 Y",
            irreversible_weight=0.7,
            context_hash="abc123",
        )
        defaults.update(kw)
        return SelfCommit(**defaults)

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        for key in (
            "id",
            "timestamp",
            "assertion_type",
            "content",
            "irreversible_weight",
            "context_hash",
            "persona_mode",
            "turn_index",
            "user_context",
            "reasoning",
        ):
            assert key in d

    def test_assertion_type_is_string(self):
        d = self._make().to_dict()
        assert d["assertion_type"] == "definitional"

    def test_roundtrip_preserves_data(self):
        original = self._make(
            assertion_type=AssertionType.COMMITMENT,
            content="我會持續",
            irreversible_weight=0.85,
            turn_index=3,
            user_context="user asked",
        )
        recovered = SelfCommit.from_dict(original.to_dict())
        assert recovered.id == original.id
        assert recovered.assertion_type == AssertionType.COMMITMENT
        assert recovered.irreversible_weight == pytest.approx(0.85)
        assert recovered.turn_index == 3

    def test_from_dict_optional_fields_default(self):
        from datetime import datetime

        d = dict(
            id="c1",
            timestamp=datetime(2026, 1, 1).isoformat(),
            assertion_type="boundary",
            content="我不會",
            irreversible_weight=0.9,
            context_hash="xyz",
        )
        commit = SelfCommit.from_dict(d)
        assert commit.persona_mode is None
        assert commit.turn_index == 0
        assert commit.user_context == ""


# ── SelfCommitExtractor._compute_context_hash ─────────────────────────────────


class TestComputeContextHash:
    def setup_method(self):
        self.ex = SelfCommitExtractor()

    def test_same_inputs_same_hash(self):
        h1 = self.ex._compute_context_hash("user", "ai")
        h2 = self.ex._compute_context_hash("user", "ai")
        assert h1 == h2

    def test_different_inputs_different_hash(self):
        h1 = self.ex._compute_context_hash("a", "b")
        h2 = self.ex._compute_context_hash("c", "d")
        assert h1 != h2

    def test_hash_is_16_chars(self):
        h = self.ex._compute_context_hash("user", "ai")
        assert len(h) == 16


# ── SelfCommitExtractor._detect_assertion_type ────────────────────────────────


class TestDetectAssertionType:
    def setup_method(self):
        self.ex = SelfCommitExtractor()

    def test_boundary_marker(self):
        atype, weight = self.ex._detect_assertion_type("我不會做這件事")
        assert atype == AssertionType.BOUNDARY_SETTING
        assert weight == pytest.approx(0.9)

    def test_commitment_marker(self):
        atype, weight = self.ex._detect_assertion_type("我會持續改進")
        assert atype == AssertionType.COMMITMENT
        assert weight == pytest.approx(0.85)

    def test_definitional_marker(self):
        atype, weight = self.ex._detect_assertion_type("這就是真理")
        assert atype == AssertionType.DEFINITIONAL
        assert weight == pytest.approx(0.7)

    def test_exploratory_marker(self):
        atype, weight = self.ex._detect_assertion_type("或許可以先假設一下")
        assert atype == AssertionType.EXPLORATORY
        assert weight == pytest.approx(0.3)

    def test_no_marker_default_exploratory(self):
        atype, weight = self.ex._detect_assertion_type("一個普通的句子")
        assert atype == AssertionType.EXPLORATORY
        assert weight == pytest.approx(0.2)

    def test_relational_marker(self):
        atype, weight = self.ex._detect_assertion_type("我們一起合作")
        assert atype == AssertionType.RELATIONAL
        assert weight == pytest.approx(0.75)

    def test_boundary_wins_over_commitment(self):
        # Text has both boundary and commitment markers; boundary checked first
        atype, _ = self.ex._detect_assertion_type("我不會，我會")
        assert atype == AssertionType.BOUNDARY_SETTING


# ── SelfCommitExtractor._calculate_irreversibility ────────────────────────────


class TestCalculateIrreversibility:
    def setup_method(self):
        self.ex = SelfCommitExtractor()

    def test_no_persona_unchanged(self):
        w = self.ex._calculate_irreversibility(AssertionType.COMMITMENT, 0.85, None)
        assert w == pytest.approx(0.85)

    def test_guardian_increases_weight(self):
        w = self.ex._calculate_irreversibility(AssertionType.COMMITMENT, 0.85, "guardian")
        assert w > 0.85

    def test_philosopher_decreases_weight(self):
        w = self.ex._calculate_irreversibility(AssertionType.DEFINITIONAL, 0.7, "philosopher")
        assert w < 0.7

    def test_capped_at_one(self):
        w = self.ex._calculate_irreversibility(AssertionType.BOUNDARY_SETTING, 0.95, "guardian")
        assert w <= 1.0

    def test_floored_at_0_1(self):
        w = self.ex._calculate_irreversibility(AssertionType.EXPLORATORY, 0.15, "philosopher")
        assert w >= 0.1


# ── SelfCommitExtractor._extract_core_assertion ───────────────────────────────


class TestExtractCoreAssertion:
    def setup_method(self):
        self.ex = SelfCommitExtractor()

    def test_returns_first_long_sentence(self):
        text = "這是一個足夠長的句子。短。另一句。"
        result = self.ex._extract_core_assertion(text)
        assert "這是一個足夠長的句子" in result

    def test_truncates_at_200(self):
        text = "X" * 300
        result = self.ex._extract_core_assertion(text)
        assert len(result) <= 200

    def test_empty_text(self):
        result = self.ex._extract_core_assertion("")
        assert result == ""


# ── SelfCommitExtractor.extract ───────────────────────────────────────────────


class TestSelfCommitExtractorExtract:
    def setup_method(self):
        self.ex = SelfCommitExtractor()

    def test_short_response_returns_none(self):
        result = self.ex.extract("短", "user input")
        assert result is None

    def test_empty_response_returns_none(self):
        assert self.ex.extract("", "user") is None

    def test_boundary_creates_commit(self):
        result = self.ex.extract("我不會做任何對使用者有害的事情，這是我的核心原則與底線。", "user")
        assert result is not None
        assert result.assertion_type == AssertionType.BOUNDARY_SETTING

    def test_exploratory_low_weight_returns_none(self):
        # No markers at all → default exploratory weight 0.2 < threshold 0.25
        result = self.ex.extract("Hello world this is a long enough sentence for testing!", "user")
        assert result is None

    def test_turn_index_preserved(self):
        result = self.ex.extract(
            "我不會做任何對使用者有害的事情，這是我的核心原則。", "user", turn_index=5
        )
        assert result is not None
        assert result.turn_index == 5

    def test_persona_mode_preserved(self):
        result = self.ex.extract(
            "我不會做任何對使用者有害的事情，這是我的核心原則。", "user", persona_mode="guardian"
        )
        assert result is not None
        assert result.persona_mode == "guardian"

    def test_user_context_truncated(self):
        long_user = "U" * 200
        result = self.ex.extract("我不會做任何對使用者有害的事情，這是我的核心原則。", long_user)
        if result:
            assert len(result.user_context) <= 100


# ── SelfCommitStack ───────────────────────────────────────────────────────────


class TestSelfCommitStack:
    def _make_commit(self, weight=0.7, turn=0):
        from datetime import datetime

        return SelfCommit(
            id=f"c{turn}",
            timestamp=datetime(2026, 1, 1),
            assertion_type=AssertionType.DEFINITIONAL,
            content="test",
            irreversible_weight=weight,
            context_hash="abc",
            turn_index=turn,
        )

    def test_push_adds_commit(self):
        stack = SelfCommitStack()
        stack.push(self._make_commit())
        assert len(stack.commits) == 1

    def test_push_trims_to_max_size(self):
        stack = SelfCommitStack(max_size=3)
        for i in range(5):
            stack.push(self._make_commit(turn=i))
        assert len(stack.commits) == 3

    def test_push_keeps_most_recent(self):
        stack = SelfCommitStack(max_size=2)
        for i in range(5):
            stack.push(self._make_commit(turn=i))
        assert stack.commits[0].turn_index == 3
        assert stack.commits[1].turn_index == 4

    def test_get_recent_reversed(self):
        stack = SelfCommitStack()
        for i in range(3):
            stack.push(self._make_commit(turn=i))
        recent = stack.get_recent(2)
        # Most recent first
        assert recent[0].turn_index == 2

    def test_get_high_weight_filtered(self):
        stack = SelfCommitStack()
        stack.push(self._make_commit(weight=0.3))
        stack.push(self._make_commit(weight=0.8))
        high = stack.get_high_weight(0.6)
        assert len(high) == 1
        assert high[0].irreversible_weight == pytest.approx(0.8)

    def test_get_high_weight_empty(self):
        stack = SelfCommitStack()
        assert stack.get_high_weight() == []

    def test_format_for_prompt_empty(self):
        assert SelfCommitStack().format_for_prompt() == ""

    def test_format_for_prompt_contains_content(self):
        stack = SelfCommitStack()
        stack.push(self._make_commit(weight=0.8))
        prompt = stack.format_for_prompt()
        assert "test" in prompt

    def test_to_dict_roundtrip(self):
        stack = SelfCommitStack()
        stack.push(self._make_commit(weight=0.7))
        d = stack.to_dict()
        recovered = SelfCommitStack.from_dict(d)
        assert len(recovered.commits) == 1
        assert recovered.commits[0].irreversible_weight == pytest.approx(0.7)
