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
