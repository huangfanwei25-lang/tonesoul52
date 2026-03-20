"""
Inter-Soul Tension Protocol.

This package makes divergence visible instead of erasing it, preserves signed
tension snapshots as memory sediment, and treats each soul as a sovereign
entity with non-negotiable governance boundaries.
"""

from .bridge import InterSoulBridge, LocalInterSoulBridge
from .negotiation import NegotiationResult, TensionNegotiator
from .sovereignty import SovereigntyGuard
from .types import (
    NegotiationOutcome,
    RuptureNotice,
    SovereigntyBoundary,
    TensionPacket,
)

__all__ = [
    "InterSoulBridge",
    "LocalInterSoulBridge",
    "NegotiationOutcome",
    "NegotiationResult",
    "RuptureNotice",
    "SovereigntyBoundary",
    "SovereigntyGuard",
    "TensionNegotiator",
    "TensionPacket",
]
