"""Tests for Phase 852: Verification Over-Budget Fail-Stop."""

from tonesoul.reflection import (
    VERIFICATION_BUDGET,
    VERIFICATION_BUDGET_EXCEEDED_MSG,
)


class TestVerificationBudgetConstants:
    """Budget constants are sane."""

    def test_budget_is_positive(self):
        assert VERIFICATION_BUDGET > 0

    def test_budget_default_value(self):
        assert VERIFICATION_BUDGET == 4

    def test_exceeded_msg_is_nonempty(self):
        assert len(VERIFICATION_BUDGET_EXCEEDED_MSG) > 0

    def test_exceeded_msg_is_chinese(self):
        # Should contain at least some CJK characters
        assert any("\u4e00" <= c <= "\u9fff" for c in VERIFICATION_BUDGET_EXCEEDED_MSG)
