from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, Protocol

from .session import GatewaySession

DEFAULT_GATEWAY_URI = "ws://127.0.0.1:18789"
DEFAULT_CHANNEL_ROUTES: dict[str, str] = {
    "audit": "/audit",
    "council": "/council",
    "heartbeat": "/heartbeat",
}


class _WebSocketLike(Protocol):
    async def send(self, data: str) -> None: ...

    async def close(self) -> None: ...


ConnectFunc = Callable[[str], Awaitable[_WebSocketLike]]


class GatewayClientError(RuntimeError):
    """Gateway client failure."""


class GatewayClient:
    """Minimal OpenClaw gateway websocket client with channel routing."""

    def __init__(
        self,
        uri: str = DEFAULT_GATEWAY_URI,
        *,
        channel_routes: dict[str, str] | None = None,
        connect_func: ConnectFunc | None = None,
    ) -> None:
        self.uri = uri
        self._channel_routes = dict(DEFAULT_CHANNEL_ROUTES)
        if channel_routes:
            self._channel_routes.update(channel_routes)
        self._connect_func = connect_func
        self._ws: _WebSocketLike | None = None

    @property
    def connected(self) -> bool:
        return self._ws is not None

    @property
    def channel_routes(self) -> dict[str, str]:
        return dict(self._channel_routes)

    def resolve_route(self, channel: str) -> str:
        key = channel.strip().lower()
        if key in self._channel_routes:
            return self._channel_routes[key]
        return f"/{key}" if key else "/audit"

    async def connect(self) -> _WebSocketLike:
        if self._ws is not None:
            return self._ws
        connect_func = self._connect_func or _default_connect
        self._ws = await connect_func(self.uri)
        return self._ws

    async def close(self) -> None:
        if self._ws is None:
            return
        ws = self._ws
        self._ws = None
        await ws.close()

    async def send(self, channel: str, payload: dict[str, Any]) -> dict[str, Any]:
        ws = await self.connect()
        envelope = {
            "channel": channel,
            "route": self.resolve_route(channel),
            "payload": payload,
        }
        await ws.send(json.dumps(envelope, ensure_ascii=False))
        return envelope

    async def send_session(
        self, session: GatewaySession, event_type: str = "session_open"
    ) -> dict[str, Any]:
        return await self.send(session.channel, session.to_gateway_payload(event_type=event_type))


async def _default_connect(uri: str) -> _WebSocketLike:
    try:
        import websockets
    except ImportError as exc:
        raise GatewayClientError(
            "Missing dependency: websockets. Install with `pip install websockets`."
        ) from exc
    return await websockets.connect(uri)
