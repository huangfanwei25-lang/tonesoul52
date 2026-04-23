from .client import (
    DEFAULT_CHANNEL_ROUTES,
    DEFAULT_GATEWAY_URI,
    GatewayClient,
    GatewayClientError,
)
from .session import GatewaySession


__ts_layer__ = "infrastructure"
__ts_purpose__ = "Gateway package: HTTP gateway server for multi-agent coordination access."

__all__ = [
    "DEFAULT_CHANNEL_ROUTES",
    "DEFAULT_GATEWAY_URI",
    "GatewayClient",
    "GatewayClientError",
    "GatewaySession",
]
