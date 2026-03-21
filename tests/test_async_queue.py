import asyncio

import pytest

from tonesoul.shared.async_queue import AsyncQueue


def test_async_queue_buffers_and_delivers_waiting_consumers():
    async def _exercise():
        queue = AsyncQueue[int](buffer_size=1)

        assert queue.push(1) is True
        assert queue.push(2) is False
        assert queue.size == 1
        assert await queue.__anext__() == 1

        waiter = asyncio.create_task(queue.__anext__())
        await asyncio.sleep(0)
        assert queue.push(3) is True
        assert await waiter == 3

    asyncio.run(_exercise())


def test_async_queue_close_stops_iteration_and_push_after_close_raises():
    async def _exercise():
        queue = AsyncQueue[int]()
        waiter = asyncio.create_task(queue.__anext__())
        await asyncio.sleep(0)
        queue.close()

        with pytest.raises(StopAsyncIteration):
            await waiter
        with pytest.raises(StopAsyncIteration):
            await queue.__anext__()
        with pytest.raises(RuntimeError, match="queue is closed"):
            queue.push(1)

    asyncio.run(_exercise())


def test_async_queue_properties_and_idempotent_close():
    queue = AsyncQueue[str](buffer_size=2)

    assert queue.is_closed is False
    assert queue.push("a") is True
    assert queue.size == 1
    queue.close()
    queue.close()
    assert queue.is_closed is True
