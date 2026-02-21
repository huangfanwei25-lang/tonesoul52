"""
Organic 4D QA Auditor Tests

D3: Time Travel — deep coverage (concurrent writes, decay edge cases, extreme jumps)
D4: Environment — path isolation, missing env vars
"""

import threading

import pytest
from freezegun import freeze_time

from tonesoul.memory.decay import FORGET_THRESHOLD, HALF_LIFE_DAYS, calculate_decay
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB


@pytest.fixture
def isolated_db(qa_sandbox):
    """Provides an isolated SqliteSoulDB within the D4 sandbox."""
    db_path = qa_sandbox / "test_soul_db.db"
    return SqliteSoulDB(db_path=db_path)


# =====================================================================
# D3: Time Travel — Basic
# =====================================================================


class TestD3_TimeTravel_Basic:
    """Validate timestamp correctness across day boundaries."""

    @freeze_time("2026-02-21 23:55:00")
    def test_midnight_boundary_timestamps(self, isolated_db):
        """Records saved before and after midnight must have correct dates."""
        isolated_db.append(MemorySource.CUSTOM, {"msg": "before midnight"})

        with freeze_time("2026-02-22 00:05:00"):
            isolated_db.append(MemorySource.CUSTOM, {"msg": "after midnight"})

            memories = list(isolated_db.query(MemorySource.CUSTOM, limit=5))
            assert len(memories) == 2

            timestamps = [m.timestamp for m in memories]
            assert "2026-02-21" in timestamps[0]
            assert "2026-02-22" in timestamps[1]


# =====================================================================
# D3: Time Travel — Decay Edge Cases
# =====================================================================


class TestD3_TimeTravel_Decay:
    """
    The REAL 隔日 Bug tests.
    Decay uses HALF_LIFE_DAYS=7 and FORGET_THRESHOLD=0.1.
    We verify that the math holds under time jumps.
    """

    def test_decay_after_one_half_life(self):
        """After 7 days, relevance should drop to ~50% of initial."""
        score = calculate_decay(1.0, HALF_LIFE_DAYS, access_count=0)
        assert 0.45 <= score <= 0.55, f"Expected ~0.5 after one half-life, got {score}"

    def test_decay_after_two_half_lives(self):
        """After 14 days, relevance should drop to ~25%."""
        score = calculate_decay(1.0, HALF_LIFE_DAYS * 2, access_count=0)
        assert 0.20 <= score <= 0.30, f"Expected ~0.25 after two half-lives, got {score}"

    def test_decay_below_forget_threshold(self):
        """After enough time, memories should be forgotten (score < 0.1)."""
        # log(0.1) / -DECAY_CONSTANT ≈ 23.25 days
        score = calculate_decay(1.0, 30, access_count=0)
        assert (
            score < FORGET_THRESHOLD
        ), f"Memory at 30 days should be below forget threshold {FORGET_THRESHOLD}, got {score}"

    def test_access_boost_prevents_forgetting(self):
        """Frequently accessed memory should survive longer due to ACCESS_BOOST."""
        score_no_access = calculate_decay(1.0, 30, access_count=0)
        score_with_access = calculate_decay(1.0, 30, access_count=3)
        assert score_with_access > score_no_access
        assert (
            score_with_access >= FORGET_THRESHOLD
        ), "3 accesses should rescue a 30-day-old memory from forgetting"

    def test_extreme_time_jump_ten_years(self):
        """
        After 3650 days, decay should be effectively zero — well below forget threshold.
        Note: IEEE 754 exp(-huge) returns a tiny positive float, not exactly 0.0.
        """
        score = calculate_decay(1.0, 3650, access_count=0)
        assert (
            score < FORGET_THRESHOLD
        ), f"10-year-old memory should be forgotten (< {FORGET_THRESHOLD}), got {score}"


# =====================================================================
# D3: Time Travel — Concurrent Writes
# =====================================================================


class TestD3_Concurrent:
    """
    Race condition: two threads writing to the same SqliteSoulDB simultaneously.
    SQLite in WAL mode should handle this, but we verify no data loss.
    """

    def test_concurrent_appends_no_data_loss(self, isolated_db):
        """50 threads each writing 1 record → must have exactly 50 records."""
        errors = []

        def write_one(idx):
            try:
                isolated_db.append(
                    MemorySource.CUSTOM,
                    {"msg": f"thread-{idx}", "idx": idx},
                )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=write_one, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        if errors:
            pytest.fail(f"Concurrent writes raised {len(errors)} errors: {errors[:3]}")

        all_records = list(isolated_db.stream(MemorySource.CUSTOM))
        assert (
            len(all_records) == 50
        ), f"Expected 50 records after concurrent writes, got {len(all_records)}"


# =====================================================================
# D4: Environment — Path & Variable Isolation
# =====================================================================


class TestD4_Environment:
    """Environment hostility tests."""

    def test_missing_deep_directory_auto_creates(self, qa_sandbox):
        """SqliteSoulDB should mkdir -p when given a non-existent deep path."""
        deep_path = qa_sandbox / "a" / "b" / "c" / "d" / "test.db"
        db = SqliteSoulDB(db_path=deep_path)
        db.append(MemorySource.CUSTOM, {"msg": "deep"})
        assert deep_path.exists()

    def test_environment_variables_absent(self, monkeypatch, qa_sandbox):
        """SqliteSoulDB should work even when HOME/APPDATA are unset."""
        monkeypatch.delenv("USERPROFILE", raising=False)
        monkeypatch.delenv("HOME", raising=False)
        monkeypatch.delenv("APPDATA", raising=False)

        # _default_memory_root() uses __file__ resolution, not env vars
        db = SqliteSoulDB()
        assert db is not None
