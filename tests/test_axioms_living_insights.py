"""Tests for tonesoul.axioms.living_insights — LivingInsight, InsightStore."""
from __future__ import annotations

import json

import pytest

from tonesoul.axioms.living_insights import (
    InsightStatus,
    InsightStore,
    LivingInsight,
    SEED_INSIGHTS,
    _utcnow,
)


# ── _utcnow ───────────────────────────────────────────────────────────────────

class TestUtcnow:
    def test_returns_string(self):
        assert isinstance(_utcnow(), str)

    def test_ends_with_z(self):
        assert _utcnow().endswith("Z")


# ── InsightStatus ─────────────────────────────────────────────────────────────

class TestInsightStatus:
    def test_enum_values(self):
        assert InsightStatus.ACTIVE.value == "active"
        assert InsightStatus.DEPRECATED.value == "deprecated"
        assert InsightStatus.SUPERSEDED.value == "superseded"


# ── LivingInsight ─────────────────────────────────────────────────────────────

class TestLivingInsight:
    def _make(self, **kw) -> LivingInsight:
        defaults = {
            "text": "Test insight text",
            "origin": "conversation",
            "id": "test-001",
        }
        defaults.update(kw)
        return LivingInsight(**defaults)

    def test_default_status_is_active(self):
        assert self._make().status is InsightStatus.ACTIVE

    def test_default_confidence_is_0_7(self):
        assert self._make().confidence == pytest.approx(0.7)

    def test_to_dict_status_is_string(self):
        d = self._make().to_dict()
        assert d["status"] == "active"

    def test_to_dict_has_all_keys(self):
        d = self._make().to_dict()
        for key in ("text", "origin", "tags", "confidence", "status", "emerged_at", "id"):
            assert key in d

    def test_from_dict_roundtrip(self):
        insight = self._make(tags=["test", "roundtrip"], confidence=0.8)
        d = insight.to_dict()
        recovered = LivingInsight.from_dict(d)
        assert recovered.text == insight.text
        assert recovered.confidence == pytest.approx(0.8)
        assert recovered.tags == ["test", "roundtrip"]
        assert recovered.status is InsightStatus.ACTIVE

    def test_from_dict_deprecated_status(self):
        d = self._make().to_dict()
        d["status"] = "deprecated"
        recovered = LivingInsight.from_dict(d)
        assert recovered.status is InsightStatus.DEPRECATED

    def test_superseded_by_defaults_none(self):
        assert self._make().superseded_by is None


# ── SEED_INSIGHTS ─────────────────────────────────────────────────────────────

class TestSeedInsights:
    def test_seed_insights_non_empty(self):
        assert len(SEED_INSIGHTS) > 0

    def test_all_have_text(self):
        for s in SEED_INSIGHTS:
            assert len(s.text) > 0

    def test_all_active(self):
        for s in SEED_INSIGHTS:
            assert s.status is InsightStatus.ACTIVE

    def test_ids_unique(self):
        ids = [s.id for s in SEED_INSIGHTS]
        assert len(ids) == len(set(ids))


# ── InsightStore (no file) ────────────────────────────────────────────────────

class TestInsightStoreNoFile:
    def test_all_returns_seed_insights(self):
        store = InsightStore(path=None)
        results = store.all()
        assert len(results) == len(SEED_INSIGHTS)

    def test_all_include_inactive_same_when_all_active(self):
        store = InsightStore(path=None)
        assert len(store.all(include_inactive=True)) == len(store.all())

    def test_get_by_id(self):
        store = InsightStore(path=None)
        first_id = SEED_INSIGHTS[0].id
        result = store.get(first_id)
        assert result is not None
        assert result.id == first_id

    def test_get_missing_id_returns_none(self):
        store = InsightStore(path=None)
        assert store.get("nonexistent-id") is None

    def test_search_by_text(self):
        store = InsightStore(path=None)
        results = store.search("tension")
        assert any("tension" in r.text.lower() or "tension" in r.tags for r in results)

    def test_search_by_tag(self):
        store = InsightStore(path=None)
        results = store.search(tags=["tension"])
        assert all("tension" in [t.lower() for t in r.tags] for r in results)

    def test_search_min_confidence(self):
        store = InsightStore(path=None)
        results = store.search(min_confidence=0.9)
        assert all(r.confidence >= 0.9 for r in results)

    def test_search_sorted_by_confidence_descending(self):
        store = InsightStore(path=None)
        results = store.search()
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_add_new_insight(self):
        store = InsightStore(path=None)
        new_insight = LivingInsight(
            text="New insight", origin="conversation", id="new-001"
        )
        store.add(new_insight)
        assert store.get("new-001") is not None

    def test_add_duplicate_id_raises(self):
        store = InsightStore(path=None)
        existing_id = SEED_INSIGHTS[0].id
        with pytest.raises(ValueError, match="already exists"):
            store.add(LivingInsight(text="dup", origin="test", id=existing_id))

    def test_deprecate_changes_status(self):
        store = InsightStore(path=None)
        target_id = SEED_INSIGHTS[0].id
        updated = store.deprecate(target_id)
        assert updated.status is InsightStatus.DEPRECATED
        # Verify it's excluded from all() by default
        active_ids = {r.id for r in store.all()}
        assert target_id not in active_ids

    def test_deprecate_nonexistent_raises(self):
        store = InsightStore(path=None)
        with pytest.raises(KeyError, match="not found"):
            store.deprecate("does-not-exist")

    def test_deprecate_visible_with_include_inactive(self):
        store = InsightStore(path=None)
        target_id = SEED_INSIGHTS[0].id
        store.deprecate(target_id)
        inactive = store.all(include_inactive=True)
        assert any(r.id == target_id and r.status is InsightStatus.DEPRECATED for r in inactive)

    def test_supersede(self):
        store = InsightStore(path=None)
        old_id = SEED_INSIGHTS[0].id
        new_insight = LivingInsight(text="New version", origin="handoff-analysis", id="new-supersede")
        result = store.supersede(old_id, new_insight)
        assert result.id == "new-supersede"
        old = store.get(old_id)
        assert old.status is InsightStatus.SUPERSEDED
        assert old.superseded_by == "new-supersede"

    def test_supersede_nonexistent_old_raises(self):
        store = InsightStore(path=None)
        new_insight = LivingInsight(text="New", origin="test", id="new-x99")
        with pytest.raises(KeyError):
            store.supersede("does-not-exist", new_insight)


# ── InsightStore (with file) ──────────────────────────────────────────────────

class TestInsightStoreWithFile:
    def test_loads_from_empty_file(self, tmp_path):
        path = tmp_path / "insights.jsonl"
        path.write_text("")
        store = InsightStore(path=path)
        # Should still have seed insights
        assert len(store.all()) == len(SEED_INSIGHTS)

    def test_loads_additional_insights_from_file(self, tmp_path):
        path = tmp_path / "insights.jsonl"
        extra = LivingInsight(text="From file", origin="conversation", id="file-001")
        path.write_text(json.dumps(extra.to_dict()) + "\n", encoding="utf-8")
        store = InsightStore(path=path)
        assert store.get("file-001") is not None
        assert len(store.all()) == len(SEED_INSIGHTS) + 1

    def test_file_version_overwrites_seed(self, tmp_path):
        path = tmp_path / "insights.jsonl"
        seed_id = SEED_INSIGHTS[0].id
        modified_seed = LivingInsight(
            text="Modified seed text",
            origin="code-observation",
            id=seed_id,
            confidence=0.1,
        )
        path.write_text(json.dumps(modified_seed.to_dict()) + "\n", encoding="utf-8")
        store = InsightStore(path=path)
        loaded = store.get(seed_id)
        assert loaded.confidence == pytest.approx(0.1)

    def test_add_and_flush_to_file(self, tmp_path):
        path = tmp_path / "insights.jsonl"
        store = InsightStore(path=path)
        new = LivingInsight(text="Flushed insight", origin="conversation", id="flush-001")
        store.add(new)
        # File should be written
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        ids_in_file = [json.loads(line)["id"] for line in content.splitlines() if line.strip()]
        assert "flush-001" in ids_in_file

    def test_corrupt_line_skipped(self, tmp_path):
        path = tmp_path / "insights.jsonl"
        good = LivingInsight(text="Good", origin="test", id="good-001")
        path.write_text(
            "not valid json\n" + json.dumps(good.to_dict()) + "\n",
            encoding="utf-8",
        )
        store = InsightStore(path=path)
        assert store.get("good-001") is not None
