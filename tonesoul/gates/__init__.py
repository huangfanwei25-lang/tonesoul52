__ts_layer__ = "governance"
__ts_purpose__ = "Gates package: governance gate checks — adaptive, skill, and YSS gate exports."

"""Gate modules — compute gate and rate limiter."""

from .compute import ComputeGate, RateLimiter

__all__ = ["ComputeGate", "RateLimiter"]
