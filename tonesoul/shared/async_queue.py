"""
AsyncQueue - Event Streaming Queue with Backpressure

Ported from Copilot Ralph's async-queue.ts with Python adaptations.

Features:
- Async-iterable interface (for async for)
- Buffer size limit for backpressure
- Clean close() semantics
- Thread-safe waiting

Usage:
    queue = AsyncQueue[MyEvent](buffer_size=100)

    # Producer
    queue.push(event)

    # Consumer
    async for event in queue:
        handle(event)

    # Cleanup
    queue.close()
"""

import asyncio
from typing import Generic, List, TypeVar

T = TypeVar("T")


class AsyncQueue(Generic[T]):
    """
    Async-iterable queue with buffer size limit.

    Provides backpressure when buffer is full and clean
    shutdown semantics when closed.
    """

    def __init__(self, buffer_size: int = 100):
        """
        Initialize queue with buffer size limit.

        Args:
            buffer_size: Maximum items to buffer before backpressure
        """
        self._buffer: List[T] = []
        self._buffer_size = buffer_size
        self._waiters: List[asyncio.Future[T]] = []
        self._closed = False

    def push(self, item: T) -> bool:
        """
        Push item to queue.

        Args:
            item: Item to push

        Returns:
            True if item was accepted, False if buffer full (backpressure)

        Raises:
            RuntimeError: If queue is closed
        """
        if self._closed:
            raise RuntimeError("queue is closed")

        # If someone is waiting, deliver directly
        if self._waiters:
            waiter = self._waiters.pop(0)
            if not waiter.done():
                waiter.set_result(item)
                return True

        # Otherwise buffer if space available
        if len(self._buffer) < self._buffer_size:
            self._buffer.append(item)
            return True

        return False  # Backpressure signal

    def close(self) -> None:
        """
        Close the queue and release all waiters.

        After closing:
        - push() will raise RuntimeError
        - Iteration will complete gracefully
        """
        if self._closed:
            return

        self._closed = True
        for waiter in self._waiters:
            if not waiter.done():
                waiter.cancel()
        self._waiters.clear()

    @property
    def is_closed(self) -> bool:
        """Check if queue is closed"""
        return self._closed

    @property
    def size(self) -> int:
        """Current number of buffered items"""
        return len(self._buffer)

    def __aiter__(self) -> "AsyncQueue[T]":
        """Return self as async iterator"""
        return self

    async def __anext__(self) -> T:
        """
        Get next item from queue.

        Returns:
            Next item from buffer or waits for push

        Raises:
            StopAsyncIteration: When queue is closed and empty
        """
        # Check buffer first
        if self._buffer:
            return self._buffer.pop(0)

        # Check if closed
        if self._closed:
            raise StopAsyncIteration

        # Wait for next item
        loop = asyncio.get_running_loop()
        waiter: asyncio.Future[T] = loop.create_future()
        self._waiters.append(waiter)

        try:
            return await waiter
        except asyncio.CancelledError:
            raise StopAsyncIteration
