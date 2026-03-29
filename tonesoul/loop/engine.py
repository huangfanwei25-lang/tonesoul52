"""
LoopEngine - Iterative AI Execution Engine

Ported from Copilot Ralph's loop-engine.ts with ToneSoul governance extensions.

Features:
- Iterative execution until completion or limit
- Timeout and cancellation support
- Event streaming via AsyncQueue
- Promise/Vow detection
- State machine: idle → running → complete/failed/cancelled

Usage:
    from tonesoul.loop import LoopEngine, LoopConfig

    config = LoopConfig(prompt="Fix this bug", max_iterations=5)
    engine = LoopEngine(config=config, on_iteration=my_handler)

    result = await engine.start()
    print(f"Completed in {result.iterations} iterations")
"""

import asyncio
import time
from typing import AsyncIterator, Callable, Optional

from ..shared.async_queue import AsyncQueue
from ..shared.errors import ERR_ALREADY_RUNNING, ERR_LOOP_CANCELLED, ERR_LOOP_TIMEOUT
from .config import LoopConfig, LoopResult, LoopState, default_loop_config
from .events import (
    ErrorEvent,
    IterationCompleteEvent,
    IterationStartEvent,
    LoopCancelledEvent,
    LoopCompleteEvent,
    LoopEvent,
    LoopFailedEvent,
    LoopStartEvent,
    PromiseDetectedEvent,
)

# Type for iteration handler
IterationHandler = Callable[[int, str], AsyncIterator[str]]


class LoopEngine:
    """
    Event-driven iteration engine with governance hooks.

    The engine runs an iteration loop, calling the provided handler
    for each iteration. It monitors for promise phrases and respects
    timeout/cancellation signals.

    State Machine:
        idle → running → complete | failed | cancelled

    Attributes:
        state: Current loop state
        iteration: Current iteration number
    """

    BUFFER_SIZE = 100

    def __init__(
        self,
        config: Optional[LoopConfig] = None,
        on_iteration: Optional[IterationHandler] = None,
    ):
        """
        Initialize loop engine.

        Args:
            config: Loop configuration (uses defaults if None)
            on_iteration: Async generator called for each iteration
        """
        self._config = config or default_loop_config()
        self._on_iteration = on_iteration

        # State
        self._state: LoopState = "idle"
        self._iteration = 0
        self._start_time_ms = 0
        self._promise_detected = False

        # Event streaming
        self._events: AsyncQueue[LoopEvent] = AsyncQueue(buffer_size=self.BUFFER_SIZE)
        self._events_closed = False

    @property
    def state(self) -> LoopState:
        """Current loop state"""
        return self._state

    @property
    def iteration(self) -> int:
        """Current iteration number"""
        return self._iteration

    @property
    def config(self) -> LoopConfig:
        """Loop configuration"""
        return self._config

    def events_stream(self) -> AsyncIterator[LoopEvent]:
        """
        Get async iterator for event stream.

        Usage:
            async for event in engine.events_stream():
                handle(event)
        """
        return self._events

    async def start(self, cancel_event: Optional[asyncio.Event] = None) -> LoopResult:
        """
        Start the iteration loop.

        Args:
            cancel_event: Optional event to signal cancellation

        Returns:
            LoopResult with final state and statistics

        Raises:
            RuntimeError: If loop is already running
        """
        if self._state != "idle":
            raise ERR_ALREADY_RUNNING

        self._state = "running"
        self._start_time_ms = int(time.time() * 1000)
        self._iteration = 0
        self._promise_detected = False

        try:
            self._emit(LoopStartEvent(config=self._config))
            result = await self._run_loop(cancel_event)
            return result
        except Exception as e:
            return self._fail(e)
        finally:
            self._events_closed = True
            self._events.close()

    async def _run_loop(self, cancel_event: Optional[asyncio.Event]) -> LoopResult:
        """Main iteration loop"""
        while True:
            # Pre-iteration checks
            result = self._pre_iteration_check(cancel_event)
            if result:
                return result

            # Execute iteration
            try:
                await self._execute_iteration()
            except Exception as e:
                if e is ERR_LOOP_TIMEOUT:
                    return self._fail(ERR_LOOP_TIMEOUT)
                if e is ERR_LOOP_CANCELLED:
                    return self._cancelled()

                # Emit error event but continue (recoverable)
                self._emit(ErrorEvent(error=e, iteration=self._iteration, recoverable=True))

            # Check for promise detection
            if self._promise_detected:
                return self._complete()

    def _pre_iteration_check(self, cancel_event: Optional[asyncio.Event]) -> Optional[LoopResult]:
        """Check conditions before iteration"""
        # Check cancellation
        if cancel_event and cancel_event.is_set():
            return self._cancelled()

        # Check timeout
        if self._config.timeout_ms > 0:
            elapsed = int(time.time() * 1000) - self._start_time_ms
            if elapsed > self._config.timeout_ms:
                return self._fail(ERR_LOOP_TIMEOUT)

        # Check max iterations
        if self._config.max_iterations > 0 and self._iteration >= self._config.max_iterations:
            return self._complete()

        return None

    async def _execute_iteration(self) -> None:
        """Execute single iteration"""
        self._iteration += 1
        iteration_start = int(time.time() * 1000)

        self._emit(
            IterationStartEvent(
                iteration=self._iteration, max_iterations=self._config.max_iterations
            )
        )

        if self._on_iteration:
            prompt = self._build_iteration_prompt()
            async for text in self._on_iteration(self._iteration, prompt):
                # Check for promise phrase
                if self._detect_promise(text):
                    self._promise_detected = True
                    self._emit(
                        PromiseDetectedEvent(
                            phrase=self._config.promise_phrase,
                            source="ai_response",
                            iteration=self._iteration,
                        )
                    )

        duration = int(time.time() * 1000) - iteration_start
        self._emit(IterationCompleteEvent(iteration=self._iteration, duration_ms=duration))

    def _build_iteration_prompt(self) -> str:
        """Build prompt for current iteration"""
        parts = [
            f"[Iteration {self._iteration}/{self._config.max_iterations}]",
            "",
            "Goal function:",
            "- Advance the current task toward one concrete next-step outcome.",
            "",
            "Priority rules:",
            "- P0: Stay grounded in the task below; do not invent scope or claim completion early.",
            "- P1: Prefer one clear next-step result over repeating the task prompt.",
            "- P2: Keep the response concise and iteration-aware.",
            "",
            "Recovery:",
            "- If task details are insufficient, state the missing information instead of guessing.",
        ]
        promise_phrase = str(self._config.promise_phrase or "").strip()
        if promise_phrase:
            parts.append(
                f"- Only emit <promise>{promise_phrase}</promise> when the task is actually complete."
            )
        parts.extend(
            [
                "",
                "Task:",
                self._config.prompt,
            ]
        )
        return "\n".join(parts)

    def _detect_promise(self, text: str) -> bool:
        """
        Detect promise phrase in text.

        Following Ralph's pattern: looks for <promise>phrase</promise>
        """
        if not self._config.promise_phrase:
            return False
        wrapped = f"<promise>{self._config.promise_phrase}</promise>"
        return wrapped in text

    def _complete(self) -> LoopResult:
        """Mark loop as complete"""
        self._state = "complete"
        result = self._build_result()
        self._emit(LoopCompleteEvent(result=result))
        return result

    def _fail(self, error: Exception) -> LoopResult:
        """Mark loop as failed"""
        self._state = "failed"
        result = self._build_result()
        result.error = error
        self._emit(LoopFailedEvent(error=error, result=result))
        return result

    def _cancelled(self) -> LoopResult:
        """Mark loop as cancelled"""
        self._state = "cancelled"
        result = self._build_result()
        result.error = ERR_LOOP_CANCELLED
        self._emit(LoopCancelledEvent(result=result))
        return result

    def _build_result(self) -> LoopResult:
        """Build result object"""
        return LoopResult(
            state=self._state,
            iterations=self._iteration,
            duration_ms=int(time.time() * 1000) - self._start_time_ms,
            error=None,
        )

    def _emit(self, event: LoopEvent) -> None:
        """Emit event to stream"""
        if self._events_closed:
            return
        try:
            self._events.push(event)
        except RuntimeError:
            pass  # Queue closed, ignore
