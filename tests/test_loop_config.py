from __future__ import annotations

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


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestLoopConfig:
    def test_default_prompt_is_empty_string(self):
        assert LoopConfig().prompt == ""

    def test_equality_by_value(self):
        a = LoopConfig(max_iterations=5)
        b = LoopConfig(max_iterations=5)
        assert a == b

    def test_inequality_on_different_value(self):
        assert LoopConfig(max_iterations=5) != LoopConfig(max_iterations=6)

    def test_two_default_configs_are_equal(self):
        assert default_loop_config() == default_loop_config()


class TestLoopResult:
    def test_error_defaults_to_none(self):
        result = LoopResult(state="complete", iterations=1, duration_ms=100)
        assert result.error is None

    def test_cancelled_state_accepted(self):
        result = LoopResult(state="cancelled", iterations=0, duration_ms=0)
        assert result.state == "cancelled"

    def test_idle_state_accepted(self):
        result = LoopResult(state="idle", iterations=0, duration_ms=0)
        assert result.state == "idle"
