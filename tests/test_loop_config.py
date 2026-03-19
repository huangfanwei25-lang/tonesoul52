from tonesoul.loop.config import LoopConfig, LoopResult, default_loop_config


def test_default_loop_config_returns_expected_defaults():
    config = default_loop_config()

    assert config == LoopConfig()
    assert config.max_iterations == 10
    assert config.timeout_ms == 30 * 60 * 1000
    assert config.working_dir == "."
    assert config.dry_run is False
    assert isinstance(config.promise_phrase, str)
    assert config.promise_phrase


def test_loop_config_and_result_accept_custom_values():
    config = LoopConfig(
        prompt="Ship the patch",
        max_iterations=3,
        timeout_ms=1500,
        promise_phrase="done",
        working_dir="/tmp/run",
        dry_run=True,
    )
    result = LoopResult(state="failed", iterations=2, duration_ms=33, error=RuntimeError("boom"))

    assert config.prompt == "Ship the patch"
    assert config.max_iterations == 3
    assert config.timeout_ms == 1500
    assert config.promise_phrase == "done"
    assert config.working_dir == "/tmp/run"
    assert config.dry_run is True
    assert result.state == "failed"
    assert result.iterations == 2
    assert result.duration_ms == 33
    assert str(result.error) == "boom"
