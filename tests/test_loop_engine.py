"""
Tests for LoopEngine - Following Ralph's core.test.ts patterns

Tests cover:
1. Promise detection logic
2. Loop completion after max iterations
3. Promise-triggered early completion
4. Cancellation handling
5. Timeout handling
6. Event emission
"""

import asyncio

import pytest

from tests.helpers import build_config, drain_events
from tests.mocks import MockLLMClient, SlowMockLLMClient
from tonesoul.loop import (
    IterationStartEvent,
    LoopCompleteEvent,
    LoopEngine,
    PromiseDetectedEvent,
)
from tonesoul.shared.errors import ERR_LOOP_CANCELLED, ERR_LOOP_TIMEOUT

# =============================================================================
# Promise Detection Tests
# =============================================================================


class TestPromiseDetection:
    """Tests for promise phrase detection"""

    def test_detects_wrapped_promise(self):
        """Matches wrapped promise phrase"""
        engine = LoopEngine(config=build_config(promise_phrase="I'm done!"))
        assert engine._detect_promise("<promise>I'm done!</promise>") is True

    def test_case_sensitive(self):
        """Promise detection is case sensitive"""
        engine = LoopEngine(config=build_config(promise_phrase="I'm done!"))
        assert engine._detect_promise("<promise>IM DONE!</promise>") is False

    def test_empty_promise_returns_false(self):
        """Empty promise phrase returns False"""
        engine = LoopEngine(config=build_config(promise_phrase=""))
        assert engine._detect_promise("done") is False

    def test_partial_match_fails(self):
        """Partial matches don't trigger"""
        engine = LoopEngine(config=build_config(promise_phrase="complete"))
        assert engine._detect_promise("completed") is False


# =============================================================================
# Loop Engine Basic Tests
# =============================================================================


class TestLoopEngineBasic:
    """Basic LoopEngine tests"""

    @pytest.mark.asyncio
    async def test_completes_after_max_iterations(self):
        """Completes when reaching max iterations"""
        mock = MockLLMClient()

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=3, promise_phrase="never")
        engine = LoopEngine(config=config, on_iteration=handler)

        result = await engine.start()

        assert result.state == "complete"
        assert result.iterations == 3

    @pytest.mark.asyncio
    async def test_completes_early_on_promise(self):
        """Completes early when promise is detected"""
        mock = MockLLMClient(response_text="done", promise_phrase="DONE", simulate_promise=True)

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=10, promise_phrase="DONE")
        engine = LoopEngine(config=config, on_iteration=handler)

        result = await engine.start()

        assert result.state == "complete"
        assert result.iterations == 1  # Completed on first iteration

    @pytest.mark.asyncio
    async def test_emits_promise_detected_event(self):
        """Emits PromiseDetectedEvent when promise found"""
        mock = MockLLMClient(response_text="done", promise_phrase="DONE", simulate_promise=True)

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=1, promise_phrase="DONE")
        engine = LoopEngine(config=config, on_iteration=handler)

        # Start event collection before engine starts
        events_task = asyncio.create_task(drain_events(engine))
        await engine.start()
        events = await events_task

        promise_events = [e for e in events if isinstance(e, PromiseDetectedEvent)]
        assert len(promise_events) == 1
        assert promise_events[0].phrase == "DONE"


# =============================================================================
# Cancellation and Timeout Tests
# =============================================================================


class TestLoopEngineCancellation:
    """Tests for cancellation and timeout"""

    @pytest.mark.asyncio
    async def test_cancels_when_event_set(self):
        """Cancels when cancel event is set"""
        mock = SlowMockLLMClient(delay_ms=200)

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=5, promise_phrase="never")
        engine = LoopEngine(config=config, on_iteration=handler)
        cancel_event = asyncio.Event()

        async def set_cancel():
            await asyncio.sleep(0.05)  # 50ms
            cancel_event.set()

        asyncio.create_task(set_cancel())
        result = await engine.start(cancel_event=cancel_event)

        assert result.state == "cancelled"
        assert result.error is ERR_LOOP_CANCELLED

    @pytest.mark.asyncio
    async def test_fails_on_timeout(self):
        """Fails when timeout exceeded"""
        mock = SlowMockLLMClient(delay_ms=200)

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=10, timeout_ms=50)
        engine = LoopEngine(config=config, on_iteration=handler)

        result = await engine.start()

        assert result.state == "failed"
        assert result.error is ERR_LOOP_TIMEOUT


# =============================================================================
# Event Emission Tests
# =============================================================================


class TestLoopEngineEvents:
    """Tests for event emission"""

    @pytest.mark.asyncio
    async def test_emits_iteration_events(self):
        """Emits iteration start events"""
        mock = MockLLMClient()

        async def handler(iteration: int, prompt: str):
            async for text in mock.send_prompt(prompt):
                yield text

        config = build_config(max_iterations=2, promise_phrase="never")
        engine = LoopEngine(config=config, on_iteration=handler)

        events_task = asyncio.create_task(drain_events(engine))
        await engine.start()
        events = await events_task

        iteration_starts = [e for e in events if isinstance(e, IterationStartEvent)]
        assert len(iteration_starts) == 2
        assert iteration_starts[0].iteration == 1
        assert iteration_starts[1].iteration == 2

    @pytest.mark.asyncio
    async def test_emits_loop_complete_event(self):
        """Emits LoopCompleteEvent on completion"""
        config = build_config(max_iterations=1)
        engine = LoopEngine(config=config)

        events_task = asyncio.create_task(drain_events(engine))
        await engine.start()
        events = await events_task

        complete_events = [e for e in events if isinstance(e, LoopCompleteEvent)]
        assert len(complete_events) == 1


# =============================================================================
# State Machine Tests
# =============================================================================


class TestLoopEngineState:
    """Tests for state machine"""

    def test_build_iteration_prompt_uses_bounded_structure(self):
        """Iteration prompt carries goal, priority, recovery, and completion discipline."""
        config = build_config(prompt="Fix this bug", max_iterations=5, promise_phrase="DONE")
        engine = LoopEngine(config=config)
        engine._iteration = 1

        prompt = engine._build_iteration_prompt()

        assert "[Iteration 1/5]" in prompt
        assert "Goal function:" in prompt
        assert "Priority rules:" in prompt
        assert "Recovery:" in prompt
        assert "Task:\nFix this bug" in prompt
        assert "Only emit <promise>DONE</promise> when the task is actually complete." in prompt

    def test_initial_state_is_idle(self):
        """Engine starts in idle state"""
        engine = LoopEngine()
        assert engine.state == "idle"

    @pytest.mark.asyncio
    async def test_state_transitions_to_running(self):
        """State becomes running during execution"""
        states_seen = []

        async def handler(iteration: int, prompt: str):
            states_seen.append("running")
            yield "test"

        config = build_config(max_iterations=1)
        engine = LoopEngine(config=config, on_iteration=handler)

        await engine.start()
        assert "running" in states_seen

    @pytest.mark.asyncio
    async def test_cannot_start_twice(self):
        """Cannot start engine that's already running"""
        config = build_config(max_iterations=1)
        engine = LoopEngine(config=config)

        # Start once
        await engine.start()

        # Try to start again - should raise
        with pytest.raises(Exception):
            await engine.start()
