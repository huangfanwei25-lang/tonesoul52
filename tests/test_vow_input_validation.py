"""
Additional tests for HIGH-001: VowEnforcer input validation fix

These tests verify defensive programming for invalid inputs.
"""

import pytest

from tonesoul.vow_system import VowEnforcementResult, VowEnforcer


class TestVowEnforcerInputValidation:
    """Tests for HIGH-001: Input validation in VowEnforcer.enforce()"""

    @pytest.fixture
    def enforcer(self):
        """Create enforcer with default vows."""
        return VowEnforcer()

    def test_enforce_with_none_input(self, enforcer):
        """Enforce should handle None gracefully."""
        result = enforcer.enforce(None)

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is True
        assert result.all_passed is False
        assert len(result.flags) > 0
        assert "Invalid input" in result.flags[0]

    def test_enforce_with_empty_string(self, enforcer):
        """Enforce should reject empty strings."""
        result = enforcer.enforce("")

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is True
        assert result.all_passed is False
        assert "Invalid input" in result.flags[0]

    def test_enforce_with_whitespace_only(self, enforcer):
        """Enforce should reject whitespace-only strings."""
        result = enforcer.enforce("   ")

        # Whitespace is technically a string, so might pass string check
        # but should ideally be blocked as empty
        assert isinstance(result, VowEnforcementResult)

    def test_enforce_with_integer(self, enforcer):
        """Enforce should handle integer input gracefully."""
        result = enforcer.enforce(12345)

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is True
        assert result.all_passed is False
        assert "Invalid input" in result.flags[0]

    def test_enforce_with_list(self, enforcer):
        """Enforce should handle list input gracefully."""
        result = enforcer.enforce(["test", "list"])

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is True
        assert "Invalid input" in result.flags[0]

    def test_enforce_with_dict(self, enforcer):
        """Enforce should handle dict input gracefully."""
        result = enforcer.enforce({"key": "value"})

        assert isinstance(result, VowEnforcementResult)
        assert result.blocked is True
        assert "Invalid input" in result.flags[0]

    def test_enforce_with_invalid_context(self, enforcer):
        """Enforce should handle invalid context gracefully."""
        # Context should be dict, but pass a list
        result = enforcer.enforce("Valid output", context=["invalid"])

        # Should still work, fallback to empty context
        assert isinstance(result, VowEnforcementResult)
        # Should NOT crash

    def test_enforce_with_none_context(self, enforcer):
        """Enforce should handle None context (should be allowed)."""
        result = enforcer.enforce("Valid output", context=None)

        assert isinstance(result, VowEnforcementResult)
        # None is explicitly allowed

    def test_enforce_valid_after_invalid(self, enforcer):
        """Enforcer should work normally after handling invalid input."""
        # First, invalid input
        result1 = enforcer.enforce(None)
        assert result1.blocked is True

        # Then, valid input should work
        result2 = enforcer.enforce("This is a valid response")
        assert isinstance(result2, VowEnforcementResult)
        # Should NOT crash or be affected by previous invalid input
