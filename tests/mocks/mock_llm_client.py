"""
Mock LLM Client following Ralph SDK patterns

These mocks enable testing of:
- Normal response flows
- Promise detection
- Timeout handling
- Cancellation
"""

import asyncio
from typing import AsyncIterator


class MockLLMClient:
    """
    Base mock for LLM client.

    Usage in tests:
        client = MockLLMClient(
            response_text="Hello",
            promise_phrase="DONE",
            simulate_promise=True
        )

        async for text in client.send_prompt("prompt"):
            print(text)  # "Hello <promise>DONE</promise>"
    """

    def __init__(
        self,
        response_text: str = "Mock response",
        promise_phrase: str = "",
        simulate_promise: bool = False,
    ):
        """
        Initialize mock client.

        Args:
            response_text: Text to return in response
            promise_phrase: Promise phrase to append if simulating
            simulate_promise: If True, append promise phrase to response
        """
        self._response_text = response_text
        self._promise_phrase = promise_phrase
        self._simulate_promise = simulate_promise

    async def send_prompt(self, prompt: str) -> AsyncIterator[str]:
        """
        Send prompt and get response stream.

        Args:
            prompt: The input prompt (ignored in mock)

        Yields:
            Response text, optionally with promise phrase
        """
        text = self._response_text
        if self._simulate_promise and self._promise_phrase:
            text = f"{text} <promise>{self._promise_phrase}</promise>"

        # Simulate minimal async delay
        await asyncio.sleep(0.001)
        yield text


class SlowMockLLMClient(MockLLMClient):
    """
    Mock with configurable delay for timeout testing.

    Usage in tests:
        client = SlowMockLLMClient(delay_ms=500)
        # Will take 500ms to respond
        async for text in client.send_prompt("prompt"):
            print(text)
    """

    def __init__(self, delay_ms: int):
        """
        Initialize slow mock.

        Args:
            delay_ms: Delay in milliseconds before responding
        """
        super().__init__(response_text="Slow response")
        self._delay_ms = delay_ms

    async def send_prompt(self, prompt: str) -> AsyncIterator[str]:
        """Send prompt with configured delay"""
        await asyncio.sleep(self._delay_ms / 1000)
        yield self._response_text
