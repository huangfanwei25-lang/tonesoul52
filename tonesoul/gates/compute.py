"""
Revenue and Compute Gates (RFC-006) - Tier 1 Resource Protection.

The ComputeGate sits at the front of the pipeline. It evaluates the user's
tier, requested action, and calculated metrics (like text density/tension)
to determine the cheapest and safest processing route.

Available Routes:
- PASS_LOCAL: Short/simple inputs bypass the Council and go straight to the free local model (e.g. qwen3:4b).
- PASS_SINGLE: Low tension inputs go to a single, cheap cloud model. Bypasses 3-agent Council.
- PASS_COUNCIL: High tension / high value inputs that require the full 3-perspective debate.
- BLOCK_RATE_LIMIT: API spam/abuse detected.

Memory Eligibility:
- Only Premium tier interactions are flagged as 'journal_eligible' to prevent
  free users from poisoning the self_journal (Evolutionary Memory Isolation).
"""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class RoutingPath(Enum):
    PASS_LOCAL = "route_local_llm"
    PASS_SINGLE = "route_single_cloud"
    PASS_COUNCIL = "route_full_council"
    BLOCK_RATE_LIMIT = "block_rate_limit"


@dataclass
class RoutingDecision:
    path: RoutingPath
    journal_eligible: bool
    reason: str


class RateLimiter:
    """Simple in-memory token bucket rate limiter (thread-safe)."""

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        # Refill rate in tokens per second
        self.refill_rate = refill_rate
        self.buckets: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def consume(self, key: str, amount: float = 1.0) -> bool:
        with self._lock:
            now = time.time()
            bucket = self.buckets.setdefault(key, {"tokens": self.capacity, "last_update": now})

            # Refill based on elapsed time
            elapsed = now - bucket["last_update"]
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)
            bucket["last_update"] = now

            if bucket["tokens"] >= amount:
                bucket["tokens"] -= amount
                return True
            return False

    def reset(self) -> None:
        """Clear all buckets. Used by test fixtures."""
        with self._lock:
            self.buckets.clear()


# Global limiters for across-instance tracking
# Free tier: max 5 burst, 1 token per 10 seconds.
_free_tier_limiter = RateLimiter(capacity=5.0, refill_rate=0.1)


class ComputeGate:
    """Evaluates incoming requests to enforce Revenue and Compute limits."""

    def __init__(self, local_model_enabled: bool = True):
        self.local_model_enabled = local_model_enabled
        self.MIN_COUNCIL_TENSION = 0.4
        self.MIN_CLOUD_LEN = 15

    def evaluate(
        self,
        user_tier: str,
        user_message: str,
        initial_tension: float,
        user_id: str = "anonymous",
    ) -> RoutingDecision:
        """
        Determines the execution path.

        Args:
            user_tier: "free", "premium", "admin", etc.
            user_message: The raw prompt text.
            initial_tension: Pre-calculated tension severity (0.0 to 1.0).
            user_id: Identifier for rate limiting.

        Returns:
            RoutingDecision instructing the pipeline how to process the request.
        """
        user_tier = user_tier.lower()
        msg_len = len(user_message.strip())

        # 1. Evolutionary Memory Isolation
        # Only premium or admin users generate data worthy of cognitive evolution
        journal_eligible = user_tier in ("premium", "admin")

        # 2. The Occam Gate (Token Filtering)
        # If the message is basically "hello", "thanks", "ok", route to free local model
        if msg_len < self.MIN_CLOUD_LEN and initial_tension < self.MIN_COUNCIL_TENSION:
            if self.local_model_enabled:
                return RoutingDecision(
                    path=RoutingPath.PASS_LOCAL,
                    journal_eligible=False,  # Never journal pleasantries
                    reason=(
                        f"Message length ({msg_len}) below threshold. "
                        "Routing to local model to save cloud tokens."
                    ),
                )

        # 3. Fast Rate Limiting (Protects Cloud APIs only; local route bypasses)
        if user_tier == "free":
            # Limits based on user_id, defaults to a global "anonymous" bucket if not provided
            if not _free_tier_limiter.consume(user_id, 1.0):
                return RoutingDecision(
                    path=RoutingPath.BLOCK_RATE_LIMIT,
                    journal_eligible=False,
                    reason="Rate limit exceeded for free tier. Please try again later.",
                )

        # 4. Tension Cost Threshold
        # Free users are capped at Single Agent processing unless it's a critical safety issue
        if user_tier == "free" and initial_tension < 0.8:
            return RoutingDecision(
                path=RoutingPath.PASS_SINGLE,
                journal_eligible=False,
                reason="Free tier user. Tension sub-critical. Routing to single cloud agent.",
            )

        # High Tension (>0.4) or Premium user requiring full deliberation
        if initial_tension >= self.MIN_COUNCIL_TENSION:
            return RoutingDecision(
                path=RoutingPath.PASS_COUNCIL,
                journal_eligible=journal_eligible,
                reason=f"High Tension detected ({initial_tension:.2f}). Scaling up to full Council debate.",
            )

        # Default standard processing
        return RoutingDecision(
            path=RoutingPath.PASS_SINGLE,
            journal_eligible=journal_eligible,
            reason="Standard complexity. Routing to single cloud agent.",
        )
