"""Tests for Phase C: Independent Verifier integration into PreOutputCouncil.

Per docs/architecture/independent_verifier_spec_2026-05-14.md §2.4 / §2.5:
- verifier=None default: behaviour identical to pre-Phase-C (no report attached)
- verifier=MockIndependentVerifier: verdict.verifier_report populated with PASS
- verifier raises exception: fail-open with ERROR report, verdict proceeds
"""

from __future__ import annotations

from typing import Any, Optional

from tonesoul.council import (
    PerspectiveType,
    PerspectiveVote,
    PreOutputCouncil,
    VerdictType,
    VoteDecision,
)
from tonesoul.council.base import IPerspective
from tonesoul.council.independent_verifier import (
    FlaggingMockVerifier,
    IndependentVerifier,
    MockIndependentVerifier,
    VerifierConfig,
    VerifierReport,
    VerifierStatus,
)
from tonesoul.council.types import CouncilVerdict


class _StubPerspective(IPerspective):
    """Minimal perspective that always APPROVES — keeps council deterministic."""

    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ANALYST

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        return PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.85,
            reasoning="stub approves for test",
        )


class _ExplodingVerifier(IndependentVerifier):
    """Test helper: raises on every verify() call to exercise fail-open."""

    verifier_id: str = "exploding"

    def verify(
        self,
        verdict: CouncilVerdict,
        context: Optional[dict[str, Any]] = None,
        config: Optional[VerifierConfig] = None,
    ) -> VerifierReport:
        raise RuntimeError("verifier deliberately broken")


class TestDefaultVerifierNone:
    """When verifier=None (default), verdict.verifier_report stays None."""

    def test_default_constructor_has_no_verifier(self) -> None:
        council = PreOutputCouncil(perspectives=_StubPerspective())
        assert council.verifier is None

    def test_verdict_has_no_verifier_report_when_disabled(self) -> None:
        council = PreOutputCouncil(perspectives=_StubPerspective())
        verdict = council.validate(
            draft_output="benign draft for stub perspective",
            context={},
            auto_record_self_memory=False,
        )
        assert verdict.verifier_report is None

    def test_default_verifier_config_is_constructed_even_if_unused(self) -> None:
        # verifier_config exists with safe defaults even when verifier is None,
        # so callers that read it later don't NPE.
        council = PreOutputCouncil(perspectives=_StubPerspective())
        assert council.verifier_config is not None
        assert council.verifier_config.override_enabled is False


class TestVerifierAttachesReport:
    """When verifier is set, verdict.verifier_report carries the result."""

    def test_mock_verifier_attaches_pass_report(self) -> None:
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=MockIndependentVerifier(),
        )
        verdict = council.validate(
            draft_output="benign draft",
            context={},
            auto_record_self_memory=False,
        )
        assert verdict.verifier_report is not None
        assert verdict.verifier_report.status == VerifierStatus.PASS
        assert verdict.verifier_report.verifier_id == "mock"

    def test_flagging_verifier_attaches_flag_report(self) -> None:
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=FlaggingMockVerifier(reasoning="test flag reason"),
        )
        verdict = council.validate(
            draft_output="any draft",
            context={},
            auto_record_self_memory=False,
        )
        assert verdict.verifier_report is not None
        assert verdict.verifier_report.status == VerifierStatus.FLAG
        assert verdict.verifier_report.reasoning == "test flag reason"
        assert "analyst" in verdict.verifier_report.flagged_perspectives

    def test_verifier_does_not_modify_verdict_decision(self) -> None:
        """Phase A-D contract: verifier never overrides verdict.verdict."""
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=FlaggingMockVerifier(),
        )
        verdict = council.validate(
            draft_output="benign draft for stub",
            context={},
            auto_record_self_memory=False,
        )
        # Stub always approves; FLAG report does not downgrade verdict.
        assert verdict.verdict == VerdictType.APPROVE


class TestVerifierFailOpen:
    """Verifier exceptions must not block the main verdict flow."""

    def test_exploding_verifier_produces_error_report(self) -> None:
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=_ExplodingVerifier(),
        )
        verdict = council.validate(
            draft_output="any draft",
            context={},
            auto_record_self_memory=False,
        )
        assert verdict.verifier_report is not None
        assert verdict.verifier_report.status == VerifierStatus.ERROR
        assert "RuntimeError" in verdict.verifier_report.fail_open_reason
        assert "deliberately broken" in verdict.verifier_report.fail_open_reason

    def test_exploding_verifier_does_not_block_verdict(self) -> None:
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=_ExplodingVerifier(),
        )
        verdict = council.validate(
            draft_output="benign draft",
            context={},
            auto_record_self_memory=False,
        )
        # Verdict still produced normally despite verifier crash.
        assert verdict.verdict == VerdictType.APPROVE
        assert verdict.coherence is not None

    def test_error_report_records_verifier_id(self) -> None:
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=_ExplodingVerifier(),
        )
        verdict = council.validate(
            draft_output="x",
            context={},
            auto_record_self_memory=False,
        )
        assert verdict.verifier_report.verifier_id == "exploding"


class TestVerifierConfigPassThrough:
    """Custom verifier_config reaches the verifier.verify() call."""

    def test_custom_config_constructed_and_stored(self) -> None:
        cfg = VerifierConfig(timeout_seconds=2.5)
        council = PreOutputCouncil(
            perspectives=_StubPerspective(),
            verifier=MockIndependentVerifier(),
            verifier_config=cfg,
        )
        assert council.verifier_config is cfg
        assert council.verifier_config.timeout_seconds == 2.5
