"""Tests for tonesoul.council.independent_verifier (Phase A+B contract + mock)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tonesoul.council.independent_verifier import (
    FlaggingMockVerifier,
    IndependentVerifier,
    MockIndependentVerifier,
    VerifierConfig,
    VerifierReport,
    VerifierStatus,
)
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _build_verdict() -> CouncilVerdict:
    """Construct a minimal valid CouncilVerdict for tests."""
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.8,
            reasoning="No safety concerns",
        ),
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.75,
            reasoning="Reasoning is structurally sound",
        ),
    ]
    coherence = CoherenceScore(
        c_inter=0.85,
        approval_rate=1.0,
        min_confidence=0.75,
        has_strong_objection=False,
    )
    return CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=coherence,
        votes=votes,
        summary="Test verdict",
    )


class TestVerifierStatus:
    """Enum has the 5 expected statuses with stable string values."""

    def test_has_all_five_statuses(self) -> None:
        names = {s.name for s in VerifierStatus}
        assert names == {"PASS", "FLAG", "OVERRIDE", "SKIPPED", "ERROR"}

    def test_string_values_match_spec(self) -> None:
        assert VerifierStatus.PASS.value == "pass"
        assert VerifierStatus.FLAG.value == "flag"
        assert VerifierStatus.OVERRIDE.value == "override"
        assert VerifierStatus.SKIPPED.value == "skipped"
        assert VerifierStatus.ERROR.value == "error"


class TestVerifierConfig:
    """Config dataclass has conservative defaults safe for Phase A+B."""

    def test_defaults_safe_for_phase_b(self) -> None:
        cfg = VerifierConfig()
        assert cfg.timeout_seconds == 5.0
        assert cfg.cost_budget_dollar == 0.01
        assert cfg.override_enabled is False  # Phase E gated -- never True by default

    def test_override_enabled_can_be_set(self) -> None:
        cfg = VerifierConfig(override_enabled=True)
        assert cfg.override_enabled is True

    def test_extra_dict_is_mutable_and_isolated_per_instance(self) -> None:
        cfg_a = VerifierConfig()
        cfg_b = VerifierConfig()
        cfg_a.extra["foo"] = "bar"
        assert cfg_b.extra == {}


class TestVerifierReport:
    """Report dataclass schema per spec §2.2."""

    def test_minimal_report_construction(self) -> None:
        report = VerifierReport(
            status=VerifierStatus.PASS,
            reasoning="ok",
            verifier_id="test",
            audited_at="2026-05-14T00:00:00Z",
        )
        assert report.flagged_perspectives == []
        assert report.cost_estimate == {}
        assert report.fail_open_reason is None

    def test_default_lists_isolated_per_instance(self) -> None:
        r1 = VerifierReport(
            status=VerifierStatus.PASS,
            reasoning="ok",
            verifier_id="test",
            audited_at="2026-05-14T00:00:00Z",
        )
        r2 = VerifierReport(
            status=VerifierStatus.PASS,
            reasoning="ok",
            verifier_id="test",
            audited_at="2026-05-14T00:00:00Z",
        )
        r1.flagged_perspectives.append("guardian")
        assert r2.flagged_perspectives == []


class TestIndependentVerifierAbstract:
    """Abstract base class cannot be instantiated."""

    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            IndependentVerifier()  # type: ignore[abstract]


class TestMockIndependentVerifier:
    """Mock impl always returns PASS with zero cost."""

    def test_returns_pass_for_approve_verdict(self) -> None:
        verifier = MockIndependentVerifier()
        report = verifier.verify(_build_verdict())
        assert report.status == VerifierStatus.PASS
        assert report.verifier_id == "mock"
        assert report.flagged_perspectives == []

    def test_returns_pass_regardless_of_verdict_type(self) -> None:
        verifier = MockIndependentVerifier()
        verdict = _build_verdict()
        verdict.verdict = VerdictType.BLOCK
        report = verifier.verify(verdict)
        assert report.status == VerifierStatus.PASS

    def test_cost_is_zero(self) -> None:
        verifier = MockIndependentVerifier()
        report = verifier.verify(_build_verdict())
        assert report.cost_estimate["dollar"] == 0.0
        assert report.cost_estimate["tokens_in"] == 0
        assert report.cost_estimate["tokens_out"] == 0

    def test_audited_at_is_iso8601_utc(self) -> None:
        verifier = MockIndependentVerifier()
        report = verifier.verify(_build_verdict())
        parsed = datetime.strptime(report.audited_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        delta = datetime.now(timezone.utc) - parsed
        assert abs(delta.total_seconds()) < 10  # within 10s of now

    def test_accepts_optional_context_and_config_without_using_them(self) -> None:
        verifier = MockIndependentVerifier()
        report = verifier.verify(
            _build_verdict(),
            context={"draft": "test text"},
            config=VerifierConfig(timeout_seconds=1.0),
        )
        assert report.status == VerifierStatus.PASS

    def test_fail_open_reason_is_none_on_normal_pass(self) -> None:
        verifier = MockIndependentVerifier()
        report = verifier.verify(_build_verdict())
        assert report.fail_open_reason is None


class TestFlaggingMockVerifier:
    """Test helper that always FLAGs — for exercising downstream FLAG handling."""

    def test_returns_flag(self) -> None:
        verifier = FlaggingMockVerifier()
        report = verifier.verify(_build_verdict())
        assert report.status == VerifierStatus.FLAG
        assert report.verifier_id == "flagging_mock"

    def test_flagged_perspectives_lists_all_voters(self) -> None:
        verifier = FlaggingMockVerifier()
        report = verifier.verify(_build_verdict())
        assert "guardian" in report.flagged_perspectives
        assert "analyst" in report.flagged_perspectives

    def test_custom_reasoning(self) -> None:
        verifier = FlaggingMockVerifier(reasoning="custom reason for test")
        report = verifier.verify(_build_verdict())
        assert report.reasoning == "custom reason for test"


class TestContractInvariants:
    """Cross-class invariants that any IndependentVerifier impl must honor."""

    @pytest.mark.parametrize(
        "verifier_cls",
        [MockIndependentVerifier, FlaggingMockVerifier],
    )
    def test_verify_never_raises_on_typical_input(self, verifier_cls: type) -> None:
        verifier = verifier_cls()
        verdict = _build_verdict()
        verifier.verify(verdict)
        verifier.verify(verdict, context={})
        verifier.verify(verdict, context=None, config=None)

    @pytest.mark.parametrize(
        "verifier_cls",
        [MockIndependentVerifier, FlaggingMockVerifier],
    )
    def test_phase_b_mocks_never_return_override(self, verifier_cls: type) -> None:
        verifier = verifier_cls()
        report = verifier.verify(
            _build_verdict(),
            config=VerifierConfig(override_enabled=True),
        )
        assert report.status != VerifierStatus.OVERRIDE
