"""
Tests for Phase 542 & 543: Stale Rule Verification Task system.
"""

import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tonesoul.stale_rule_verifier import (
    StaleRuleVerificationTask,
    StaleRuleVerificationTaskBatch,
    VerificationQuery,
    _utcnow_iso,
)

# Test Fixtures


@dataclass
class MockCrystal:
    """Mock Crystal for testing."""

    rule: str
    source_pattern: str
    weight: float
    created_at: str
    freshness_score: float
    freshness_status: str = "stale"
    access_count: int = 0
    tags: list = None
    stage: str = "T0"
    stage_history: list = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.stage_history is None:
            self.stage_history = []


@pytest.fixture
def stale_crystal():
    """A stale crystal for testing."""
    now = datetime.now(timezone.utc)
    created_at = (now - timedelta(days=45)).isoformat().replace("+00:00", "Z")
    return MockCrystal(
        rule="If user_sentiment == 'angry', escalate_to_supervisor",
        source_pattern="customer_support_logs",
        weight=0.75,
        created_at=created_at,
        freshness_score=0.25,  # Stale
        freshness_status="stale",
    )


@pytest.fixture
def needs_verification_crystal():
    """A crystal needing verification."""
    now = datetime.now(timezone.utc)
    created_at = (now - timedelta(days=20)).isoformat().replace("+00:00", "Z")
    return MockCrystal(
        rule="API_TIMEOUT_MS should never exceed 5000",
        source_pattern="performance_metrics",
        weight=0.85,
        created_at=created_at,
        freshness_score=0.40,  # Needs verification
        freshness_status="needs_verification",
    )


@pytest.fixture
def active_crystal():
    """An active crystal (recent)."""
    return MockCrystal(
        rule="OAuth tokens must be rotated every 24 hours",
        source_pattern="security_audit",
        weight=0.95,
        created_at=_utcnow_iso(),
        freshness_score=0.90,  # Active
        freshness_status="active",
    )


# Tests: VerificationQuery


class TestVerificationQuery:
    """Test VerificationQuery generation from stale rules."""

    def test_for_stale_rule_very_stale(self):
        """Test query generation for very stale rule (< 0.15)."""
        vq = VerificationQuery.for_stale_rule(
            rule_text="Old rule text",
            freshness_score=0.10,
        )
        assert vq.rule_text == "Old rule text"
        assert "EVIDENCE" in vq.challenge.upper()
        assert "Goal function:" in vq.challenge
        assert "- P0:" in vq.challenge
        assert "Recovery instructions:" in vq.challenge
        assert "counter_example" in vq.evidence_types
        assert vq.confidence_threshold == 0.75
        assert vq.decomission_reason is not None

    def test_for_stale_rule_moderately_stale(self):
        """Test query generation for moderately stale rule (0.15-0.30)."""
        vq = VerificationQuery.for_stale_rule(
            rule_text="Moderately old rule",
            freshness_score=0.25,
        )
        assert vq.rule_text == "Moderately old rule"
        assert "recent case" in vq.challenge.lower()
        assert "Output expectation:" in vq.challenge
        assert "inconclusive" in vq.challenge.lower()
        assert "supporting_case" in vq.evidence_types
        assert vq.confidence_threshold == 0.60

    def test_for_stale_rule_includes_source_pattern_context_hint(self):
        """Test source pattern is preserved as bounded context instead of hidden assumption."""
        vq = VerificationQuery.for_stale_rule(
            rule_text="Rule with source",
            freshness_score=0.22,
            source_pattern="runtime_observability",
        )
        assert "Context hint: runtime_observability." in vq.challenge

    def test_verification_query_to_dict(self):
        """Test serialization of VerificationQuery."""
        vq = VerificationQuery(
            rule_text="Test rule",
            challenge="Test challenge",
            evidence_types=["test_type"],
            confidence_threshold=0.75,
        )
        d = vq.to_dict()
        assert d["rule_text"] == "Test rule"
        assert d["challenge"] == "Test challenge"
        assert d["evidence_types"] == ["test_type"]


# Tests: StaleRuleVerificationTask


class TestStaleRuleVerificationTask:
    """Test StaleRuleVerificationTask creation and management."""

    def test_from_crystal_stale(self, stale_crystal):
        """Test task creation from stale crystal."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        assert task.rule_text == stale_crystal.rule
        assert task.freshness_score == 0.25
        assert task.status == "pending"
        assert task.verification_attempts == 0
        assert task.dream_engine_priority > 0.60  # Should be high for stale

    def test_from_crystal_not_stale_raises(self, active_crystal):
        """Test that non-stale crystals raise ValueError."""
        with pytest.raises(ValueError, match="not stale enough"):
            StaleRuleVerificationTask.from_crystal(active_crystal)

    def test_from_crystal_age_calculation(self, stale_crystal):
        """Test that age_days is calculated correctly."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        # stale_crystal is 45 days old, so age_days should be ~45
        assert 44.0 <= task.age_days <= 46.0

    def test_task_priority_calculation(self, stale_crystal):
        """Test that dream_engine_priority is computed correctly."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        # Base 0.60 + decay_factor (0.75) * 0.25 + age_factor (45/365 ~ 0.12) * 0.15
        # ~0.60 + 0.1875 + 0.018 = ~0.806
        assert 0.75 < task.dream_engine_priority <= 1.0

    def test_record_attempt_re_confirmed(self, stale_crystal):
        """Test recording a re-confirmed verification result."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        result = {
            "status": "re_confirmed",
            "confidence": 0.92,
            "evidence_summary": "Found 5 recent instances supporting the rule.",
            "recommendation": "Mark rule as re-confirmed.",
        }
        task.record_attempt(result)
        assert task.status == "re_confirmed"
        assert task.verification_attempts == 1
        assert task.last_attempt_at is not None
        assert task.verification_result["confidence"] == 0.92

    def test_record_attempt_decomissioned(self, stale_crystal):
        """Test recording a decomissioned result."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        result = {
            "status": "decomissioned",
            "confidence": 0.05,
            "evidence_summary": "No supporting evidence found; counter-examples exist.",
            "recommendation": "Rule is invalid in current contexts.",
        }
        task.record_attempt(result)
        assert task.status == "decomissioned"

    def test_record_attempt_inconclusive_after_3_attempts(self, stale_crystal):
        """Test that task marked as failed after 3 inconclusive attempts."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        for i in range(3):
            result = {
                "status": "inconclusive",
                "confidence": 0.50,
                "evidence_summary": f"Attempt {i+1}: inconclusive.",
            }
            task.record_attempt(result)
        assert task.status == "failed"
        assert task.verification_attempts == 3

    def test_task_to_dict(self, stale_crystal):
        """Test serialization of StaleRuleVerificationTask."""
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        d = task.to_dict()
        assert d["task_id"] == task.task_id
        assert d["rule_text"] == task.rule_text
        assert d["status"] == "pending"
        assert "verification_query" in d
        assert isinstance(d["verification_query"], dict)


# Tests: StaleRuleVerificationTaskBatch


class TestStaleRuleVerificationTaskBatch:
    """Test batch generation and persistence."""

    def test_generate_from_crystals(
        self, stale_crystal, needs_verification_crystal, active_crystal
    ):
        """Test generating tasks from a mixed crystal list."""
        batch = StaleRuleVerificationTaskBatch()
        crystals = [stale_crystal, needs_verification_crystal, active_crystal]
        tasks = batch.generate_from_crystals(crystals, max_tasks=10)

        # Only stale and needs_verification should generate tasks, but only stale < 0.30
        assert len(tasks) == 1
        assert tasks[0].rule_text == stale_crystal.rule

    def test_generate_from_crystals_max_limit(self, stale_crystal):
        """Test that max_tasks limit is respected."""
        batch = StaleRuleVerificationTaskBatch()
        # Create 5 stale crystals
        now = datetime.now(timezone.utc)
        stale_crystals = []
        for i in range(5):
            created_at = (now - timedelta(days=30 + i)).isoformat().replace("+00:00", "Z")
            stale_crystals.append(
                MockCrystal(
                    rule=f"Rule {i}",
                    source_pattern="test",
                    weight=0.75,
                    created_at=created_at,
                    freshness_score=0.20,
                )
            )

        tasks = batch.generate_from_crystals(stale_crystals, max_tasks=3)
        assert len(tasks) == 3

    def test_persist_and_load_tasks(self):
        """Test persistence and loading of verification tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "verification_tasks.jsonl")

            # Create and persist
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)
            task1 = StaleRuleVerificationTask(
                task_id="verify_1",
                rule_id="rule_1",
                rule_text="Test rule 1",
                source_pattern="source_1",
                freshness_score=0.20,
                age_days=10.0,
                verification_query=VerificationQuery(
                    rule_text="Test rule 1",
                    challenge="Challenge 1",
                    evidence_types=["type1"],
                    confidence_threshold=0.75,
                ),
                created_at=_utcnow_iso(),
                dream_engine_priority=0.70,
            )
            batch.persist_tasks([task1])

            # Load and verify
            batch2 = StaleRuleVerificationTaskBatch(storage_path=storage_path)
            loaded = batch2.load_tasks()
            assert len(loaded) == 1
            assert loaded[0].rule_text == "Test rule 1"
            assert loaded[0].freshness_score == 0.20

    def test_get_pending_tasks(self):
        """Test retrieving only pending tasks."""
        batch = StaleRuleVerificationTaskBatch()
        task1 = StaleRuleVerificationTask(
            task_id="verify_1",
            rule_id="rule_1",
            rule_text="Test rule 1",
            source_pattern="source_1",
            freshness_score=0.20,
            age_days=10.0,
            verification_query=VerificationQuery(
                rule_text="Test rule 1",
                challenge="Challenge",
                evidence_types=["type"],
                confidence_threshold=0.75,
            ),
            created_at=_utcnow_iso(),
            dream_engine_priority=0.70,
            status="pending",
        )
        task2 = StaleRuleVerificationTask(
            task_id="verify_2",
            rule_id="rule_2",
            rule_text="Test rule 2",
            source_pattern="source_2",
            freshness_score=0.20,
            age_days=10.0,
            verification_query=VerificationQuery(
                rule_text="Test rule 2",
                challenge="Challenge",
                evidence_types=["type"],
                confidence_threshold=0.75,
            ),
            created_at=_utcnow_iso(),
            dream_engine_priority=0.70,
            status="re_confirmed",  # Not pending
        )
        batch.tasks = {"verify_1": task1, "verify_2": task2}
        pending = batch.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].task_id == "verify_1"


# Integration test


class TestStaleRuleVerificationIntegration:
    """Integration tests for stale rule verification."""

    def test_end_to_end_workflow(self, stale_crystal):
        """Test complete workflow from crystal to verification result."""
        # 1. Create task from stale crystal
        task = StaleRuleVerificationTask.from_crystal(stale_crystal)
        assert task.status == "pending"

        # 2. Simulate verification attempt
        result = {
            "status": "re_confirmed",
            "confidence": 0.88,
            "evidence_summary": "Found 3 supporting cases.",
            "recommendation": "Rule remains valid.",
        }
        task.record_attempt(result)

        # 3. Verify state changes
        assert task.status == "re_confirmed"
        assert task.verification_attempts == 1
        assert task.last_attempt_at is not None

    def test_batch_full_cycle(self):
        """Test batch generation, persistence, and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")

            # Create stale crystals
            now = datetime.now(timezone.utc)
            stale_crystals = []
            for i in range(3):
                created_at = (now - timedelta(days=30)).isoformat().replace("+00:00", "Z")
                stale_crystals.append(
                    MockCrystal(
                        rule=f"Rule {i}",
                        source_pattern=f"source_{i}",
                        weight=0.75,
                        created_at=created_at,
                        freshness_score=0.20,
                    )
                )

            # Generate and persist
            batch1 = StaleRuleVerificationTaskBatch(storage_path=storage_path)
            tasks = batch1.generate_from_crystals(stale_crystals, max_tasks=10)
            batch1.persist_tasks(tasks)

            # Load and verify
            batch2 = StaleRuleVerificationTaskBatch(storage_path=storage_path)
            loaded_tasks = batch2.load_tasks()
            assert len(loaded_tasks) == 3
            assert all(t.status == "pending" for t in loaded_tasks)


# Phase 543: apply_verification_results tests


class TestApplyVerificationResults:
    """Test Phase 543: applying verification results back to Crystallizer."""

    def _make_task(self, *, task_id: str, rule_text: str, status: str) -> StaleRuleVerificationTask:
        return StaleRuleVerificationTask(
            task_id=task_id,
            rule_id=f"rule_{task_id}",
            rule_text=rule_text,
            source_pattern="test",
            freshness_score=0.20,
            age_days=30.0,
            verification_query=VerificationQuery(
                rule_text=rule_text,
                challenge="Challenge",
                evidence_types=["type"],
                confidence_threshold=0.75,
            ),
            created_at=_utcnow_iso(),
            dream_engine_priority=0.70,
            status=status,
        )

    def test_re_confirmed_calls_mark_support(self):
        """re_confirmed tasks should call mark_support on the crystallizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            task = self._make_task(task_id="v1", rule_text="rule-A", status="re_confirmed")
            batch.persist_tasks([task])

            mock_crystallizer = MagicMock()
            results = batch.apply_verification_results(mock_crystallizer)

            assert results["re_confirmed"] == 1
            assert results["retired"] == 0
            mock_crystallizer.mark_support.assert_called_once_with("rule-A")

    def test_decomissioned_calls_retire_crystal(self):
        """decomissioned tasks should call retire_crystal on the crystallizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            task = self._make_task(task_id="v2", rule_text="rule-B", status="decomissioned")
            batch.persist_tasks([task])

            mock_crystallizer = MagicMock()
            results = batch.apply_verification_results(mock_crystallizer)

            assert results["retired"] == 1
            assert results["re_confirmed"] == 0
            mock_crystallizer.retire_crystal.assert_called_once_with("rule-B")

    def test_failed_calls_retire_crystal(self):
        """failed tasks should also call retire_crystal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            task = self._make_task(task_id="v3", rule_text="rule-C", status="failed")
            batch.persist_tasks([task])

            mock_crystallizer = MagicMock()
            results = batch.apply_verification_results(mock_crystallizer)

            assert results["retired"] == 1
            mock_crystallizer.retire_crystal.assert_called_once_with("rule-C")

    def test_pending_tasks_are_skipped(self):
        """pending tasks should not be applied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            task = self._make_task(task_id="v4", rule_text="rule-D", status="pending")
            batch.persist_tasks([task])

            mock_crystallizer = MagicMock()
            results = batch.apply_verification_results(mock_crystallizer)

            assert results == {"re_confirmed": 0, "retired": 0, "skipped": 0}
            mock_crystallizer.mark_support.assert_not_called()
            mock_crystallizer.retire_crystal.assert_not_called()

    def test_mixed_statuses_applied_correctly(self):
        """Multiple tasks with different statuses all handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            tasks = [
                self._make_task(task_id="v5", rule_text="rule-E", status="re_confirmed"),
                self._make_task(task_id="v6", rule_text="rule-F", status="decomissioned"),
                self._make_task(task_id="v7", rule_text="rule-G", status="pending"),
            ]
            batch.persist_tasks(tasks)

            mock_crystallizer = MagicMock()
            results = batch.apply_verification_results(mock_crystallizer)

            assert results["re_confirmed"] == 1
            assert results["retired"] == 1
            assert results["skipped"] == 0

    def test_status_updated_after_apply(self):
        """Task statuses should be rewritten after apply."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = str(Path(tmpdir) / "tasks.jsonl")
            batch = StaleRuleVerificationTaskBatch(storage_path=storage_path)

            task = self._make_task(task_id="v8", rule_text="rule-H", status="re_confirmed")
            batch.persist_tasks([task])

            mock_crystallizer = MagicMock()
            batch.apply_verification_results(mock_crystallizer)

            # Reload and verify status was updated
            batch2 = StaleRuleVerificationTaskBatch(storage_path=storage_path)
            loaded = batch2.load_tasks()
            assert len(loaded) == 1
            assert loaded[0].status == "applied_re_confirmed"
