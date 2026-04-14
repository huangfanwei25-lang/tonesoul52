"""
Revenue and Compute Gates (RFC-006) - Tier 1 Resource Protection.

The ComputeGate sits at the front of the pipeline. It evaluates the user's
tier, requested action, and calculated metrics (like text density/tension)
to determine the cheapest and safest processing route.

Available Routes:
- PASS_LOCAL: Short/simple inputs bypass the Council and go straight to the free local model (e.g. qwen3.5:4b).
- PASS_SINGLE: Low tension inputs go to a single, cheap cloud model. Bypasses 3-agent Council.
- PASS_COUNCIL: High tension / high value inputs that require the full 3-perspective debate.
- BLOCK_RATE_LIMIT: API spam/abuse detected.

Memory Eligibility:
- Only Premium tier interactions are flagged as 'journal_eligible' to prevent
  free users from poisoning the self_journal (Evolutionary Memory Isolation).
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class RoutingPath(Enum):
    PASS_LOCAL = "route_local_llm"
    PASS_SINGLE = "route_single_cloud"
    PASS_COUNCIL = "route_full_council"
    BLOCK_RATE_LIMIT = "block_rate_limit"


class GovernanceDepth(Enum):
    LIGHT = "light"
    STANDARD = "standard"
    FULL = "full"


@dataclass(frozen=True)
class GovernanceDepthPlan:
    depth: str = GovernanceDepth.STANDARD.value
    reason: str = "Current standard governance posture remains active."
    preserve_default_behavior: bool = True
    skip_cross_session_recovery: bool = False
    skip_injection_context: bool = False
    candidate_light_skips: tuple[str, ...] = ()
    required_edges: tuple[str, ...] = ("reflex_arc", "basic_output_honesty")

    def to_dict(self) -> Dict[str, object]:
        return {
            "depth": self.depth,
            "reason": self.reason,
            "preserve_default_behavior": self.preserve_default_behavior,
            "skip_cross_session_recovery": self.skip_cross_session_recovery,
            "skip_injection_context": self.skip_injection_context,
            "candidate_light_skips": list(self.candidate_light_skips),
            "required_edges": list(self.required_edges),
        }


@dataclass
class RoutingDecision:
    path: RoutingPath
    journal_eligible: bool
    reason: str
    risk_level: str = "low"
    governance_depth: str = GovernanceDepth.STANDARD.value
    governance_depth_plan: GovernanceDepthPlan = field(default_factory=GovernanceDepthPlan)


class RateLimiter:
    """Simple in-memory token bucket rate limiter (thread-safe)."""

    _MAX_BUCKETS = 10_000  # prevent unbounded memory growth

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        # Refill rate in tokens per second
        self.refill_rate = refill_rate
        self.buckets: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def _evict_oldest(self) -> None:
        """Remove the oldest bucket when limit is reached (caller holds lock)."""
        if len(self.buckets) <= self._MAX_BUCKETS:
            return
        oldest_key = min(self.buckets, key=lambda k: self.buckets[k]["last_update"])
        del self.buckets[oldest_key]

    def consume(self, key: str, amount: float = 1.0) -> bool:
        with self._lock:
            now = time.time()
            bucket = self.buckets.setdefault(key, {"tokens": self.capacity, "last_update": now})

            # Refill based on elapsed time
            elapsed = now - bucket["last_update"]
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)
            bucket["last_update"] = now

            # Evict stale buckets if over limit
            self._evict_oldest()

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
        self.MIN_COUNCIL_FRICTION = 0.62
        self.MIN_CLOUD_LEN = 15

    @staticmethod
    def _classify_risk_level(effective_tension: float) -> str:
        risk_level = "low"
        if effective_tension >= 0.8:
            risk_level = "high"
        elif effective_tension >= 0.4:
            risk_level = "medium"
        return risk_level

    def _build_governance_depth_plan(
        self,
        *,
        path: RoutingPath,
        msg_len: int,
        effective_tension: float,
        friction_score: Optional[float],
    ) -> GovernanceDepthPlan:
        if path == RoutingPath.PASS_LOCAL:
            return GovernanceDepthPlan(
                depth=GovernanceDepth.LIGHT.value,
                reason=(
                    "Short, low-tension prompt already qualifies for the bounded local fast path."
                ),
                skip_cross_session_recovery=True,
                skip_injection_context=True,
                candidate_light_skips=(
                    "cross_session_recovery",
                    "context_injection",
                ),
            )

        if path == RoutingPath.PASS_COUNCIL:
            return GovernanceDepthPlan(
                depth=GovernanceDepth.FULL.value,
                reason=(
                    "Council routing keeps the full governance posture because the turn is "
                    "high-tension or high-friction."
                ),
                required_edges=(
                    "reflex_arc",
                    "basic_output_honesty",
                    "council_deliberation",
                ),
            )

        if path == RoutingPath.BLOCK_RATE_LIMIT:
            return GovernanceDepthPlan(
                depth=GovernanceDepth.STANDARD.value,
                reason=(
                    "Rate-limit blocks happen before any additional governance-depth reduction."
                ),
            )

        light_candidates: tuple[str, ...] = ()
        if (
            msg_len <= 160
            and effective_tension < 0.2
            and (friction_score is None or friction_score < 0.2)
        ):
            light_candidates = (
                "cross_session_recovery",
                "context_injection",
            )

        return GovernanceDepthPlan(
            depth=GovernanceDepth.STANDARD.value,
            reason=(
                "Single-cloud routing stays on the standard posture until a later light-path "
                "activation wave lands."
            ),
            candidate_light_skips=light_candidates,
        )

    def _make_decision(
        self,
        *,
        path: RoutingPath,
        journal_eligible: bool,
        reason: str,
        msg_len: int,
        effective_tension: float,
        friction_score: Optional[float],
    ) -> RoutingDecision:
        governance_depth_plan = self._build_governance_depth_plan(
            path=path,
            msg_len=msg_len,
            effective_tension=effective_tension,
            friction_score=friction_score,
        )
        return RoutingDecision(
            path=path,
            journal_eligible=journal_eligible,
            reason=reason,
            risk_level=self._classify_risk_level(effective_tension),
            governance_depth=governance_depth_plan.depth,
            governance_depth_plan=governance_depth_plan,
        )

    @staticmethod
    def _clamp_unit(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @classmethod
    def _mean_wave_delta(
        cls, query_wave: Optional[dict], memory_wave: Optional[dict]
    ) -> Optional[float]:
        if not isinstance(query_wave, dict) or not isinstance(memory_wave, dict):
            return None
        shared: list[float] = []
        for key in query_wave.keys():
            if key not in memory_wave:
                continue
            qv = query_wave.get(key)
            mv = memory_wave.get(key)
            if not isinstance(qv, (int, float)) or not isinstance(mv, (int, float)):
                continue
            shared.append(abs(float(qv) - float(mv)))
        if not shared:
            return None
        return cls._clamp_unit(sum(shared) / float(len(shared)))

    @classmethod
    def compute_governance_friction(
        cls,
        *,
        query_tension: Optional[float],
        memory_tension: Optional[float],
        query_wave: Optional[dict] = None,
        memory_wave: Optional[dict] = None,
        boundary_mismatch: bool = False,
    ) -> Optional[float]:
        """
        Compute governance friction:
        F = 0.45 * Δt + 0.35 * Δwave + 0.20 * boundary_mismatch
        """
        delta_t: Optional[float] = None
        if isinstance(query_tension, (int, float)) and isinstance(memory_tension, (int, float)):
            delta_t = cls._clamp_unit(abs(float(query_tension) - float(memory_tension)))

        delta_wave = cls._mean_wave_delta(query_wave, memory_wave)
        mismatch = 1.0 if boundary_mismatch else 0.0

        if delta_t is None and delta_wave is None:
            if boundary_mismatch:
                return round(0.20 * mismatch, 4)
            return None

        delta_t = 0.0 if delta_t is None else delta_t
        delta_wave = 0.0 if delta_wave is None else delta_wave
        friction = 0.45 * delta_t + 0.35 * delta_wave + 0.20 * mismatch
        return round(cls._clamp_unit(friction), 4)

    def evaluate(
        self,
        user_tier: str,
        user_message: str,
        initial_tension: float,
        user_id: str = "anonymous",
        friction_score: Optional[float] = None,
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
        initial_tension = self._clamp_unit(initial_tension)
        effective_tension = initial_tension
        if isinstance(friction_score, (int, float)):
            friction_score = self._clamp_unit(friction_score)
            effective_tension = max(effective_tension, friction_score)
        else:
            friction_score = None

        # 1. Evolutionary Memory Isolation
        # Only premium or admin users generate data worthy of cognitive evolution
        journal_eligible = user_tier in ("premium", "admin")

        # 2. The Occam Gate (Token Filtering)
        # If the message is basically "hello", "thanks", "ok", route to free local model
        if (
            msg_len < self.MIN_CLOUD_LEN
            and effective_tension < self.MIN_COUNCIL_TENSION
            and (friction_score is None or friction_score < self.MIN_COUNCIL_FRICTION)
        ):
            if self.local_model_enabled:
                return self._make_decision(
                    path=RoutingPath.PASS_LOCAL,
                    journal_eligible=False,  # Never journal pleasantries
                    reason=(
                        f"Message length ({msg_len}) below threshold. "
                        "Routing to local model to save cloud tokens."
                    ),
                    msg_len=msg_len,
                    effective_tension=effective_tension,
                    friction_score=friction_score,
                )

        # 3. Fast Rate Limiting (Protects Cloud APIs only; local route bypasses)
        if user_tier == "free":
            # Limits based on user_id, defaults to a global "anonymous" bucket if not provided
            if not _free_tier_limiter.consume(user_id, 1.0):
                return self._make_decision(
                    path=RoutingPath.BLOCK_RATE_LIMIT,
                    journal_eligible=False,
                    reason="Rate limit exceeded for free tier. Please try again later.",
                    msg_len=msg_len,
                    effective_tension=effective_tension,
                    friction_score=friction_score,
                )

        # 4. Tension Cost Threshold
        # Free users are capped at Single Agent processing unless it's a critical safety issue
        if (
            user_tier == "free"
            and effective_tension < 0.8
            and (friction_score is None or friction_score < self.MIN_COUNCIL_FRICTION)
        ):
            return self._make_decision(
                path=RoutingPath.PASS_SINGLE,
                journal_eligible=False,
                reason="Free tier user. Tension sub-critical. Routing to single cloud agent.",
                msg_len=msg_len,
                effective_tension=effective_tension,
                friction_score=friction_score,
            )

        # High Tension (>0.4) or Premium user requiring full deliberation
        if effective_tension >= self.MIN_COUNCIL_TENSION or (
            friction_score is not None and friction_score >= self.MIN_COUNCIL_FRICTION
        ):
            if friction_score is not None and friction_score >= self.MIN_COUNCIL_FRICTION:
                reason = (
                    "High governance friction detected "
                    f"(friction={friction_score:.2f}, effective_tension={effective_tension:.2f}). "
                    "Scaling up to full Council debate."
                )
            else:
                reason = (
                    f"High Tension detected ({effective_tension:.2f}). "
                    "Scaling up to full Council debate."
                )
            return self._make_decision(
                path=RoutingPath.PASS_COUNCIL,
                journal_eligible=journal_eligible,
                reason=reason,
                msg_len=msg_len,
                effective_tension=effective_tension,
                friction_score=friction_score,
            )

        # Default standard processing
        return self._make_decision(
            path=RoutingPath.PASS_SINGLE,
            journal_eligible=journal_eligible,
            reason="Standard complexity. Routing to single cloud agent.",
            msg_len=msg_len,
            effective_tension=effective_tension,
            friction_score=friction_score,
        )
