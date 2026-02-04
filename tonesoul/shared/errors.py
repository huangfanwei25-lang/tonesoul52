"""
ToneSoul Standard Errors - Singleton Pattern

Following Copilot Ralph's clean error design:
- Singleton errors for direct comparison in tests
- Hierarchical error classes
- Clear error messages

Usage:
    from tonesoul.shared.errors import ERR_LOOP_TIMEOUT

    if error is ERR_LOOP_TIMEOUT:
        handle_timeout()
"""


class ToneSoulError(Exception):
    """Base error for ToneSoul system"""

    pass


class LoopError(ToneSoulError):
    """Errors related to iteration loops"""

    pass


class ValidationError(ToneSoulError):
    """Errors related to input validation"""

    pass


class StateError(ToneSoulError):
    """Errors related to state machine violations"""

    pass


class VowError(ToneSoulError):
    """Errors related to vow system"""

    pass


# =============================================================================
# Singleton Errors - Can be compared with `is` operator
# =============================================================================

# Loop errors
ERR_LOOP_CANCELLED = LoopError("loop cancelled")
ERR_LOOP_TIMEOUT = LoopError("loop timeout exceeded")
ERR_MAX_ITERATIONS = LoopError("maximum iterations reached")

# Validation errors
ERR_INVALID_INPUT = ValidationError("invalid input")
ERR_EMPTY_OUTPUT = ValidationError("output must be non-empty string")

# State errors
ERR_STATE_VIOLATION = StateError("invalid state transition")
ERR_ALREADY_RUNNING = StateError("loop already running")

# Vow errors
ERR_VOW_VIOLATION = VowError("vow violation detected")
ERR_VOW_BLOCKED = VowError("output blocked by vow")
