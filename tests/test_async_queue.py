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


# ─── Extended coverage ────────────────────────────────────────────────────────


class TestAsyncQueueBuffer:
    def test_default_buffer_size_is_100(self):
        queue = AsyncQueue()
        for i in range(100):
            assert queue.push(i) is True
        assert queue.push(101) is False

    def test_size_decreases_after_consume(self):
        async def _run():
            queue = AsyncQueue[int](buffer_size=3)
            queue.push(1)
            queue.push(2)
            assert queue.size == 2
            await queue.__anext__()
            assert queue.size == 1

        asyncio.run(_run())

    def test_push_to_closed_raises(self):
        queue = AsyncQueue[int]()
        queue.close()
        with pytest.raises(RuntimeError, match="queue is closed"):
            queue.push(42)

    def test_anext_on_closed_empty_raises_stop(self):
        async def _run():
            queue = AsyncQueue[int]()
            queue.close()
            with pytest.raises(StopAsyncIteration):
                await queue.__anext__()

        asyncio.run(_run())

    def test_aiter_returns_self(self):
        queue = AsyncQueue[int]()
        assert queue.__aiter__() is queue

    def test_fifo_order_preserved(self):
        async def _run():
            queue = AsyncQueue[int](buffer_size=5)
            for i in range(3):
                queue.push(i)
            results = []
            for _ in range(3):
                results.append(await queue.__anext__())
            assert results == [0, 1, 2]

        asyncio.run(_run())

    def test_multiple_waiters_all_served(self):
        async def _run():
            queue = AsyncQueue[int]()
            t1 = asyncio.create_task(queue.__anext__())
            t2 = asyncio.create_task(queue.__anext__())
            await asyncio.sleep(0)
            queue.push(10)
            queue.push(20)
            r1 = await t1
            r2 = await t2
            assert sorted([r1, r2]) == [10, 20]

        asyncio.run(_run())

    def test_direct_delivery_bypasses_buffer(self):
        async def _run():
            queue = AsyncQueue[int](buffer_size=0)
            waiter = asyncio.create_task(queue.__anext__())
            await asyncio.sleep(0)
            # With a waiter, push should deliver directly
            result = queue.push(99)
            assert result is True
            assert await waiter == 99

        asyncio.run(_run())

    def test_close_while_items_in_buffer_drains_buffer(self):
        async def _run():
            queue = AsyncQueue[int](buffer_size=5)
            queue.push(1)
            queue.push(2)
            queue.close()
            # Items already buffered should still be drainable
            assert await queue.__anext__() == 1
            assert await queue.__anext__() == 2
            with pytest.raises(StopAsyncIteration):
                await queue.__anext__()

        asyncio.run(_run())

    def test_async_for_loop(self):
        async def _run():
            queue = AsyncQueue[int](buffer_size=10)
            for i in range(3):
                queue.push(i)
            queue.close()
            results = []
            async for item in queue:
                results.append(item)
            assert results == [0, 1, 2]

        asyncio.run(_run())
