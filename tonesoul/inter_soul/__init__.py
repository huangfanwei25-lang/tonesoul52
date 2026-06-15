# DORMANT (as of 2026-06-15): inter_soul package is unused—only imported by tests. No live code references it through direct imports, re-exports, class/function usages, dynamic imports, plugin registries, or entry points. Safe to deprecate or archive; see docs/architecture/architecture_legibility_2026-06-15.md
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

__ts_layer__ = "surface"
__ts_purpose__ = "Inter-soul surface: cross-agent communication and soul linking utilities."
