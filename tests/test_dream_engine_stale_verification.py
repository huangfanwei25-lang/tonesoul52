"""
Tests for Phase 542: DreamEngine integration with stale rule verification.
"""

from unittest.mock import MagicMock, patch

import pytest

from tonesoul.dream_engine import DreamCycleResult, DreamEngine
from tonesoul.stale_rule_verifier import StaleRuleVerificationTask


@pytest.fixture
def mock_crystallizer():
    """Mock crystallizer with stale rules."""
    mock = MagicMock()

    # Mock stale crystal
    stale_crystal = MagicMock()
    stale_crystal.rule = "If status == 'urgent', auto_escalate"
    stale_crystal.source_pattern = "ticket_system"
    stale_crystal.weight = 0.75
    stale_crystal.created_at = "2025-12-18T10:00:00Z"
    stale_crystal.freshness_score = 0.25
    stale_crystal.freshness_status = "stale"

    mock.top_crystals.return_value = [stale_crystal]
    return mock


@pytest.fixture
def mock_write_gateway():
    """Mock write gateway."""
    mock = MagicMock()
    mock.stream_environment_stimuli.return_value = []
    return mock


@pytest.fixture
def mock_governance_kernel():
    """Mock governance kernel."""
    return MagicMock()


@pytest.fixture
def mock_router():
    """Mock LLM router."""
    mock = MagicMock()
    mock.get_client.return_value = None
    return mock


@pytest.fixture
def mock_soul_db():
    """Mock SoulDB."""
    return MagicMock()


@pytest.fixture
def dream_engine_with_mocks(
    mock_soul_db,
    mock_write_gateway,
    mock_governance_kernel,
    mock_router,
    mock_crystallizer,
):
    """Create a DreamEngine with all mocked dependencies."""
    engine = DreamEngine(
        soul_db=mock_soul_db,
        write_gateway=mock_write_gateway,
        governance_kernel=mock_governance_kernel,
        router=mock_router,
        crystallizer=mock_crystallizer,
    )
    return engine


class TestDreamEngineStaleRuleIntegration:
    """Test DreamEngine integration with stale rule verification."""

    def test_reflection_prompt_includes_bounded_prompt_discipline(
        self,
        dream_engine_with_mocks,
    ):
        prompt = dream_engine_with_mocks._reflection_prompt(
            payload={
                "topic": "memory drift",
                "summary": "Recent handoff feels thinner than expected.",
                "tags": ["continuity", "handoff"],
            },
            related_memories=[
                {"title": "Old continuity repair"},
                {"title": "Shared working-style anchor"},
            ],
            crystal_rules=[
                "Preserve continuity without promoting advisory memory into canon.",
                "Prefer bounded review when evidence is thin.",
            ],
            friction_score=0.42,
            council_reason="Review before promoting stale handoff guidance.",
            llm_backend="mock-backend",
        )

        assert "Goal function:" in prompt
        assert "Priority rules:" in prompt
        assert "- P0:" in prompt
        assert "- P1:" in prompt
        assert "- P2:" in prompt
        assert "Evidence discipline:" in prompt
        assert "Recovery instructions:" in prompt
        assert "Output spec:" in prompt
        assert "Exactly 2 concise sentences" in prompt

    def test_reflection_prompt_warns_against_invented_governance_support(
        self,
        dream_engine_with_mocks,
    ):
        prompt = dream_engine_with_mocks._reflection_prompt(
            payload={"topic": "stale rule", "summary": "A rule may no longer hold.", "tags": []},
            related_memories=[],
            crystal_rules=["Outdated heuristics need re-verification."],
            friction_score=0.15,
            council_reason="Seek evidence before changing governance posture.",
            llm_backend=None,
        )

        assert "Do not invent hidden memories" in prompt
        assert "If the evidence is thin or conflicting, say so directly" in prompt
        assert "smallest bounded review or follow-up step" in prompt

    def test_run_cycle_generates_verification_tasks(
        self,
        dream_engine_with_mocks,
    ):
        """Test that run_cycle generates verification tasks for stale rules."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            # Mock batch behavior
            mock_batch = MagicMock()
            mock_batch.generate_from_crystals.return_value = [
                MagicMock(spec=StaleRuleVerificationTask),
            ]
            MockBatch.return_value = mock_batch

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                result = dream_engine_with_mocks.run_cycle(
                    limit=1,
                    generate_verification_tasks=True,
                    max_verification_tasks=5,
                )

                # Verify batch was created (twice: apply + generate)
                assert MockBatch.call_count == 2
                mock_batch.generate_from_crystals.assert_called_once()
                mock_batch.persist_tasks.assert_called_once()

                # Verify result includes verification task count
                assert isinstance(result, DreamCycleResult)
                assert result.stale_rule_tasks_generated == 1

    def test_run_cycle_verification_tasks_disabled(
        self,
        dream_engine_with_mocks,
    ):
        """Test that verification tasks can be disabled."""
        with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
            mock_persist.return_value = {}

            result = dream_engine_with_mocks.run_cycle(
                limit=1,
                generate_verification_tasks=False,
            )

            # Verify no tasks generated when disabled
            assert result.stale_rule_tasks_generated == 0

    def test_run_cycle_verification_tasks_failure_graceful(
        self,
        dream_engine_with_mocks,
    ):
        """Test that verification task generation failure is handled gracefully."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            # Mock batch to raise an exception
            MockBatch.side_effect = Exception("Batch creation failed")

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                # Should not raise, should gracefully degrade
                result = dream_engine_with_mocks.run_cycle(
                    limit=1,
                    generate_verification_tasks=True,
                )

                # Verify task count is 0 due to failure
                assert result.stale_rule_tasks_generated == 0

    def test_dream_cycle_result_includes_verification_tasks(
        self,
        dream_engine_with_mocks,
    ):
        """Test that DreamCycleResult.to_dict includes verification task count."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            mock_batch = MagicMock()
            mock_batch.generate_from_crystals.return_value = [
                MagicMock(),
                MagicMock(),
            ]
            MockBatch.return_value = mock_batch

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                result = dream_engine_with_mocks.run_cycle(
                    generate_verification_tasks=True,
                    max_verification_tasks=10,
                )

                # Convert to dict and verify field is present
                result_dict = result.to_dict()
                assert "stale_rule_tasks_generated" in result_dict
                assert result_dict["stale_rule_tasks_generated"] == 2

    def test_run_cycle_with_max_verification_tasks(
        self,
        dream_engine_with_mocks,
    ):
        """Test that max_verification_tasks limit is respected."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            mock_batch = MagicMock()
            # Return 5 tasks
            mock_batch.generate_from_crystals.return_value = [MagicMock()] * 5
            MockBatch.return_value = mock_batch

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                result = dream_engine_with_mocks.run_cycle(
                    generate_verification_tasks=True,
                    max_verification_tasks=3,
                )

                # Verify max_tasks was passed to generate_from_crystals
                call_kwargs = mock_batch.generate_from_crystals.call_args[1]
                assert call_kwargs["max_tasks"] == 3
                # But result shows what was actually generated
                assert result.stale_rule_tasks_generated == 5

    def test_verification_tasks_persist_after_cycle(
        self,
        dream_engine_with_mocks,
    ):
        """Test that verification tasks are persisted to storage."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            mock_batch = MagicMock()
            mock_task = MagicMock(spec=StaleRuleVerificationTask)
            mock_batch.generate_from_crystals.return_value = [mock_task]
            MockBatch.return_value = mock_batch

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                dream_engine_with_mocks.run_cycle(
                    generate_verification_tasks=True,
                )

                # Verify persist_tasks was called with the generated tasks
                mock_batch.persist_tasks.assert_called_once()
                persisted = mock_batch.persist_tasks.call_args[0][0]
                assert len(persisted) == 1
                assert persisted[0] is mock_task


class TestDreamCycleResultWithVerification:
    """Test DreamCycleResult handles verification tasks correctly."""

    def test_dream_cycle_result_default_verification_count(self):
        """Test that default stale_rule_tasks_generated is 0."""
        from tonesoul.dream_engine import DreamCycleResult

        result = DreamCycleResult(
            generated_at="2026-01-01T00:00:00Z",
            dream_cycle_id="test-cycle-123",
            stimuli_considered=5,
            stimuli_selected=2,
            llm_backend="gpt4",
        )

        assert result.stale_rule_tasks_generated == 0

    def test_dream_cycle_result_with_verification_count(self):
        """Test that stale_rule_tasks_generated can be set."""
        from tonesoul.dream_engine import DreamCycleResult

        result = DreamCycleResult(
            generated_at="2026-01-01T00:00:00Z",
            dream_cycle_id="test-cycle-123",
            stimuli_considered=5,
            stimuli_selected=2,
            llm_backend="gpt4",
            stale_rule_tasks_generated=3,
        )

        assert result.stale_rule_tasks_generated == 3

    def test_dream_cycle_result_to_dict_includes_verification(self):
        """Test that to_dict() includes verification task count."""
        from tonesoul.dream_engine import DreamCycleResult

        result = DreamCycleResult(
            generated_at="2026-01-01T00:00:00Z",
            dream_cycle_id="test-cycle-123",
            stimuli_considered=5,
            stimuli_selected=2,
            llm_backend="gpt4",
            stale_rule_tasks_generated=2,
        )

        d = result.to_dict()
        assert d["stale_rule_tasks_generated"] == 2


# Phase 543: verification_applied tests


class TestDreamCycleResultVerificationApplied:
    """Test Phase 543: verification_applied field in DreamCycleResult."""

    def test_default_verification_applied_is_empty_dict(self):
        result = DreamCycleResult(
            generated_at="2026-01-01T00:00:00Z",
            dream_cycle_id="test-cycle",
            stimuli_considered=0,
            stimuli_selected=0,
            llm_backend=None,
        )
        assert result.verification_applied == {}

    def test_verification_applied_set_and_serialized(self):
        applied = {"re_confirmed": 2, "retired": 1, "skipped": 0}
        result = DreamCycleResult(
            generated_at="2026-01-01T00:00:00Z",
            dream_cycle_id="test-cycle",
            stimuli_considered=0,
            stimuli_selected=0,
            llm_backend=None,
            verification_applied=applied,
        )
        assert result.verification_applied == applied
        d = result.to_dict()
        assert d["verification_applied"] == applied


class TestDreamEngineApplyVerification:
    """Test Phase 543: DreamEngine.run_cycle applies verification results."""

    def test_run_cycle_applies_verification_results(
        self,
        dream_engine_with_mocks,
    ):
        """run_cycle should apply verification results before generating new tasks."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            mock_apply_batch = MagicMock()
            mock_apply_batch.apply_verification_results.return_value = {
                "re_confirmed": 1,
                "retired": 2,
                "skipped": 0,
            }
            mock_gen_batch = MagicMock()
            mock_gen_batch.generate_from_crystals.return_value = []

            # First call for apply, second for generate
            MockBatch.side_effect = [mock_apply_batch, mock_gen_batch]

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                result = dream_engine_with_mocks.run_cycle(
                    limit=1,
                    generate_verification_tasks=True,
                )

                assert result.verification_applied["re_confirmed"] == 1
                assert result.verification_applied["retired"] == 2

    def test_run_cycle_verification_applied_when_disabled(
        self,
        dream_engine_with_mocks,
    ):
        """When generate_verification_tasks=False, verification_applied is empty."""
        with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
            mock_persist.return_value = {}

            result = dream_engine_with_mocks.run_cycle(
                limit=1,
                generate_verification_tasks=False,
            )

            assert result.verification_applied == {"re_confirmed": 0, "retired": 0, "skipped": 0}

    def test_run_cycle_apply_failure_graceful(
        self,
        dream_engine_with_mocks,
    ):
        """If apply raises, run_cycle should continue without errors."""
        with patch("tonesoul.dream_engine.StaleRuleVerificationTaskBatch") as MockBatch:
            # First call (apply) raises, second call (generate) succeeds
            mock_gen_batch = MagicMock()
            mock_gen_batch.generate_from_crystals.return_value = []
            MockBatch.side_effect = [Exception("apply failed"), mock_gen_batch]

            with patch.object(dream_engine_with_mocks, "_persist_collisions") as mock_persist:
                mock_persist.return_value = {}

                result = dream_engine_with_mocks.run_cycle(
                    limit=1,
                    generate_verification_tasks=True,
                )

                # Should degrade gracefully
                assert result.verification_applied == {
                    "re_confirmed": 0,
                    "retired": 0,
                    "skipped": 0,
                }
