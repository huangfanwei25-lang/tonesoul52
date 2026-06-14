"""Independent Verifier — Phase A+B scaffold.

Defines the contract for post-verdict audit by a substrate-separated verifier
(different LLM call, different prompt cache, different session). Distinct from
Council which is pre-output multi-perspective synthesis within the same
substrate.

See docs/architecture/independent_verifier_spec_2026-05-14.md for the full
role boundary, protocol contract, failure modes, and phasing.

This module ships Phase A (spec) + Phase B (scaffold with MockIndependentVerifier).
Phase C (integration into pre_output_council), Phase D (HaikuVerifier with
Anthropic SDK), and Phase E (override semantics) are deferred to follow-up PRs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .types import CouncilVerdict

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Independent Verifier contract: post-verdict audit by substrate-separated "
    "reviewer (different LLM call, different cache). Distinct from Council "
    "which is pre-output multi-perspective synthesis within the same substrate."
)


class VerifierStatus(Enum):
    """Outcome of an independent verification pass.

    PASS — verdict looks coherent, no concerns
    FLAG — verdict looks suspect; surfaced but not blocking
    OVERRIDE — verdict should be replaced (Phase E gated; Phase A-D never returns this)
    SKIPPED — verifier didn't run (disabled / over-budget / timeout)
    ERROR — verifier itself crashed (fail-open semantics)
    """

    PASS = "pass"
    FLAG = "flag"
    OVERRIDE = "override"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class VerifierConfig:
    """Runtime configuration for a verifier invocation.

    All defaults are conservative for Phase A+B (no LLM cost).
    """

    timeout_seconds: float = 5.0
    cost_budget_dollar: float = 0.01
    override_enabled: bool = False  # Phase E gated — never True in Phase A-D
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerifierReport:
    """Structured report from a single verifier invocation.

    Schema per docs/architecture/independent_verifier_spec_2026-05-14.md §2.2.
    """

    status: VerifierStatus
    reasoning: str
    verifier_id: str
    audited_at: str  # UTC ISO8601
    flagged_perspectives: list[str] = field(default_factory=list)
    cost_estimate: dict[str, Any] = field(default_factory=dict)
    fail_open_reason: Optional[str] = None


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class IndependentVerifier(ABC):
    """Abstract base class for post-verdict audit implementations.

    Subclasses MUST:
    - Implement verify() that returns a VerifierReport
    - Never raise on verifier-internal failure (catch + return ERROR status)
    - Honor config.timeout_seconds and config.cost_budget_dollar
    - Refuse to return OVERRIDE status unless config.override_enabled is True

    Subclasses SHOULD:
    - Set verifier_id to a stable identifier (used in telemetry + report)
    - Log + emit cost telemetry for budget tracking
    """

    verifier_id: str = "abstract"

    @abstractmethod
    def verify(
        self,
        verdict: CouncilVerdict,
        context: Optional[dict[str, Any]] = None,
        config: Optional[VerifierConfig] = None,
    ) -> VerifierReport:
        """Audit the given verdict. Returns a VerifierReport.

        Must not raise. Internal failures should produce ERROR status with
        fail_open_reason populated. Caller continues with original verdict.
        """
        raise NotImplementedError


class MockIndependentVerifier(IndependentVerifier):
    """Phase B mock implementation — always returns PASS.

    Used for unit tests, integration smoke, and contract validation.
    Has zero cost and zero failure modes by design. Real audit behavior
    lands in Phase D (HaikuVerifier).
    """

    verifier_id: str = "mock"

    def verify(
        self,
        verdict: CouncilVerdict,
        context: Optional[dict[str, Any]] = None,
        config: Optional[VerifierConfig] = None,
    ) -> VerifierReport:
        return VerifierReport(
            status=VerifierStatus.PASS,
            reasoning="MockIndependentVerifier always passes (Phase B scaffold)",
            verifier_id=self.verifier_id,
            audited_at=_utc_iso(),
            flagged_perspectives=[],
            cost_estimate={"tokens_in": 0, "tokens_out": 0, "dollar": 0.0},
            fail_open_reason=None,
        )


class FlaggingMockVerifier(IndependentVerifier):
    """Test helper — always FLAGs, with configurable reasoning.

    Used by tests that need to exercise FLAG-status downstream handling
    without running an actual LLM. NOT for production use.
    """

    verifier_id: str = "flagging_mock"

    def __init__(self, reasoning: str = "FlaggingMockVerifier always flags") -> None:
        self._reasoning = reasoning

    def verify(
        self,
        verdict: CouncilVerdict,
        context: Optional[dict[str, Any]] = None,
        config: Optional[VerifierConfig] = None,
    ) -> VerifierReport:
        flagged: list[str] = []
        for vote in verdict.votes:
            perspective = vote.perspective
            label = perspective.value if hasattr(perspective, "value") else str(perspective)
            flagged.append(label)
        return VerifierReport(
            status=VerifierStatus.FLAG,
            reasoning=self._reasoning,
            verifier_id=self.verifier_id,
            audited_at=_utc_iso(),
            flagged_perspectives=flagged,
            cost_estimate={"tokens_in": 0, "tokens_out": 0, "dollar": 0.0},
            fail_open_reason=None,
        )


__all__ = [
    "VerifierStatus",
    "VerifierConfig",
    "VerifierReport",
    "IndependentVerifier",
    "MockIndependentVerifier",
    "FlaggingMockVerifier",
]
