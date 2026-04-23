from __future__ import annotations

import pytest

from tonesoul.shared import errors as errors_mod


def test_error_hierarchy_and_singletons_have_expected_types():
    assert isinstance(errors_mod.ERR_LOOP_TIMEOUT, errors_mod.LoopError)
    assert isinstance(errors_mod.ERR_INVALID_INPUT, errors_mod.ValidationError)
    assert isinstance(errors_mod.ERR_ALREADY_RUNNING, errors_mod.StateError)
    assert isinstance(errors_mod.ERR_VOW_BLOCKED, errors_mod.VowError)
    assert issubclass(errors_mod.LoopError, errors_mod.ToneSoulError)


def test_singleton_errors_preserve_identity_and_messages():
    assert errors_mod.ERR_LOOP_TIMEOUT is errors_mod.ERR_LOOP_TIMEOUT
    assert str(errors_mod.ERR_LOOP_CANCELLED) == "loop cancelled"
    assert str(errors_mod.ERR_EMPTY_OUTPUT) == "output must be non-empty string"
    assert str(errors_mod.ERR_VOW_VIOLATION) == "vow violation detected"


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestErrorHierarchy:
    def test_all_subclasses_inherit_from_tonesoul_error(self):
        for cls in (
            errors_mod.LoopError,
            errors_mod.ValidationError,
            errors_mod.StateError,
            errors_mod.VowError,
        ):
            assert issubclass(cls, errors_mod.ToneSoulError)

    def test_tonesoul_error_is_exception(self):
        assert issubclass(errors_mod.ToneSoulError, Exception)

    def test_subclasses_are_distinct(self):
        classes = [
            errors_mod.LoopError,
            errors_mod.ValidationError,
            errors_mod.StateError,
            errors_mod.VowError,
        ]
        assert len(set(classes)) == 4


class TestSingletonMessages:
    def test_loop_timeout_message(self):
        assert str(errors_mod.ERR_LOOP_TIMEOUT) == "loop timeout exceeded"

    def test_max_iterations_message(self):
        assert str(errors_mod.ERR_MAX_ITERATIONS) == "maximum iterations reached"

    def test_invalid_input_message(self):
        assert str(errors_mod.ERR_INVALID_INPUT) == "invalid input"

    def test_state_violation_message(self):
        assert str(errors_mod.ERR_STATE_VIOLATION) == "invalid state transition"

    def test_already_running_message(self):
        assert str(errors_mod.ERR_ALREADY_RUNNING) == "loop already running"

    def test_vow_blocked_message(self):
        assert str(errors_mod.ERR_VOW_BLOCKED) == "output blocked by vow"


class TestSingletonRaiseAndCatch:
    def test_can_raise_and_catch_as_parent_class(self):
        with pytest.raises(errors_mod.LoopError):
            raise errors_mod.ERR_LOOP_TIMEOUT

    def test_raised_singleton_is_same_object(self):
        try:
            raise errors_mod.ERR_VOW_VIOLATION
        except errors_mod.VowError as e:
            assert e is errors_mod.ERR_VOW_VIOLATION

    def test_loop_error_catchable_as_tonesoul_error(self):
        with pytest.raises(errors_mod.ToneSoulError):
            raise errors_mod.ERR_MAX_ITERATIONS

    def test_validation_error_catchable_as_tonesoul_error(self):
        with pytest.raises(errors_mod.ToneSoulError):
            raise errors_mod.ERR_INVALID_INPUT
