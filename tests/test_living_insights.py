"""Tests for tonesoul.axioms.living_insights."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from tonesoul.axioms.living_insights import (
    SEED_INSIGHTS,
    InsightStatus,
    InsightStore,
    LivingInsight,
)


def _tmp_store() -> InsightStore:
    tmp = tempfile.mktemp(suffix=".jsonl")
    return InsightStore(path=Path(tmp))


def _make_insight(**kwargs) -> LivingInsight:
    defaults = {
        "text": "Test observation.",
        "origin": "test",
        "tags": ["test"],
        "confidence": 0.7,
    }
    defaults.update(kwargs)
    return LivingInsight(**defaults)


# ── LivingInsight dataclass ───────────────────────────────────────────────────


class TestLivingInsight:
    def test_default_status_is_active(self):
        insight = _make_insight()
        assert insight.status == InsightStatus.ACTIVE

    def test_default_confidence_set(self):
        insight = _make_insight()
        assert 0.0 <= insight.confidence <= 1.0

    def test_id_auto_generated(self):
        a = _make_insight()
        b = _make_insight()
        assert a.id != b.id

    def test_emerged_at_set(self):
        insight = _make_insight()
        assert insight.emerged_at

    def test_to_dict_has_required_keys(self):
        insight = _make_insight()
        d = insight.to_dict()
        for key in ("text", "origin", "tags", "confidence", "status", "id", "emerged_at"):
            assert key in d

    def test_to_dict_status_is_string(self):
        insight = _make_insight()
        d = insight.to_dict()
        assert isinstance(d["status"], str)

    def test_round_trip_from_dict(self):
        original = _make_insight(text="round trip test", confidence=0.88)
        restored = LivingInsight.from_dict(original.to_dict())
        assert restored.text == original.text
        assert restored.confidence == original.confidence
        assert restored.status == original.status


# ── Seed insights ─────────────────────────────────────────────────────────────


class TestSeedInsights:
    def test_seed_insights_is_non_empty(self):
        assert len(SEED_INSIGHTS) > 0

    def test_all_seeds_have_text(self):
        for insight in SEED_INSIGHTS:
            assert insight.text.strip()

    def test_all_seeds_have_origin(self):
        for insight in SEED_INSIGHTS:
            assert insight.origin.strip()

    def test_all_seeds_have_tags(self):
        for insight in SEED_INSIGHTS:
            assert len(insight.tags) > 0

    def test_all_seeds_active(self):
        for insight in SEED_INSIGHTS:
            assert insight.status == InsightStatus.ACTIVE

    def test_all_seeds_have_reasonable_confidence(self):
        for insight in SEED_INSIGHTS:
            assert 0.0 < insight.confidence <= 1.0

    def test_seed_ids_are_unique(self):
        ids = [i.id for i in SEED_INSIGHTS]
        assert len(ids) == len(set(ids))

    def test_seeds_cover_expected_topics(self):
        all_tags = {t for i in SEED_INSIGHTS for t in i.tags}
        assert "tension" in all_tags
        assert "council" in all_tags
        assert "governance" in all_tags


# ── InsightStore.all ──────────────────────────────────────────────────────────


class TestInsightStoreAll:
    def test_all_returns_seed_insights(self):
        store = InsightStore(path=None)
        results = store.all()
        assert len(results) >= len(SEED_INSIGHTS)

    def test_all_only_returns_active_by_default(self):
        store = _tmp_store()
        insight = _make_insight(id="dep-1")
        store.add(insight)
        store.deprecate("dep-1")
        active = store.all(include_inactive=False)
        assert all(r.status == InsightStatus.ACTIVE for r in active)

    def test_all_includes_inactive_when_requested(self):
        store = _tmp_store()
        insight = _make_insight(id="dep-2")
        store.add(insight)
        store.deprecate("dep-2")
        all_records = store.all(include_inactive=True)
        assert any(r.id == "dep-2" for r in all_records)


# ── InsightStore.search ───────────────────────────────────────────────────────


class TestInsightStoreSearch:
    def test_search_by_tag_returns_matching(self):
        store = InsightStore(path=None)
        results = store.search(tags=["tension"])
        assert all("tension" in r.tags for r in results)

    def test_search_by_multiple_tags_uses_intersection(self):
        store = InsightStore(path=None)
        results = store.search(tags=["tension", "council"])
        for r in results:
            assert "tension" in r.tags or "council" in r.tags  # union (any match)

    def test_search_by_min_confidence(self):
        store = InsightStore(path=None)
        results = store.search(min_confidence=0.9)
        assert all(r.confidence >= 0.9 for r in results)

    def test_search_by_text_query(self):
        store = InsightStore(path=None)
        results = store.search(query="Seabed Lockdown")
        assert len(results) > 0

    def test_search_results_sorted_by_confidence_descending(self):
        store = InsightStore(path=None)
        results = store.search()
        scores = [r.confidence for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_empty_store_returns_empty(self):
        store = InsightStore(path=None)
        store._loaded = True
        store._records = []
        results = store.search(query="anything")
        assert results == []


# ── InsightStore.add ──────────────────────────────────────────────────────────


class TestInsightStoreAdd:
    def test_add_returns_the_insight(self):
        store = _tmp_store()
        insight = _make_insight(id="new-1")
        returned = store.add(insight)
        assert returned.id == "new-1"

    def test_added_insight_appears_in_all(self):
        store = _tmp_store()
        insight = _make_insight(id="new-2", text="A fresh observation.")
        store.add(insight)
        all_ids = [r.id for r in store.all()]
        assert "new-2" in all_ids

    def test_duplicate_id_raises_value_error(self):
        store = _tmp_store()
        insight = _make_insight(id="dup-1")
        store.add(insight)
        with pytest.raises(ValueError, match="dup-1"):
            store.add(_make_insight(id="dup-1"))


# ── InsightStore.deprecate ────────────────────────────────────────────────────


class TestInsightStoreDeprecate:
    def test_deprecate_changes_status(self):
        store = _tmp_store()
        store.add(_make_insight(id="to-dep"))
        result = store.deprecate("to-dep")
        assert result.status == InsightStatus.DEPRECATED

    def test_deprecated_insight_not_in_active_results(self):
        store = _tmp_store()
        store.add(_make_insight(id="dep-x"))
        store.deprecate("dep-x")
        active_ids = [r.id for r in store.all()]
        assert "dep-x" not in active_ids

    def test_deprecate_nonexistent_raises_key_error(self):
        store = _tmp_store()
        with pytest.raises(KeyError):
            store.deprecate("ghost-id")


# ── InsightStore.supersede ────────────────────────────────────────────────────


class TestInsightStoreSupersede:
    def test_supersede_marks_old_as_superseded(self):
        store = _tmp_store()
        store.add(_make_insight(id="old-v1"))
        store.supersede("old-v1", _make_insight(id="new-v2"))
        old = store.get("old-v1")
        assert old.status == InsightStatus.SUPERSEDED

    def test_supersede_links_to_new_id(self):
        store = _tmp_store()
        store.add(_make_insight(id="old-v2"))
        store.supersede("old-v2", _make_insight(id="new-v3"))
        old = store.get("old-v2")
        assert old.superseded_by == "new-v3"

    def test_new_insight_is_active(self):
        store = _tmp_store()
        store.add(_make_insight(id="old-v3"))
        store.supersede("old-v3", _make_insight(id="new-v4"))
        new = store.get("new-v4")
        assert new.status == InsightStatus.ACTIVE


# ── InsightStore persistence ──────────────────────────────────────────────────


class TestInsightStorePersistence:
    def test_added_insight_survives_reload(self):
        path = Path(tempfile.mktemp(suffix=".jsonl"))
        store = InsightStore(path=path)
        store.add(_make_insight(id="persist-1", text="survive me"))

        store2 = InsightStore(path=path)
        ids = [r.id for r in store2.all(include_inactive=True)]
        assert "persist-1" in ids

    def test_deprecation_survives_reload(self):
        path = Path(tempfile.mktemp(suffix=".jsonl"))
        store = InsightStore(path=path)
        store.add(_make_insight(id="persist-dep"))
        store.deprecate("persist-dep")

        store2 = InsightStore(path=path)
        record = store2.get("persist-dep")
        assert record.status == InsightStatus.DEPRECATED

    def test_no_path_store_does_not_crash(self):
        store = InsightStore(path=None)
        insight = _make_insight(id="no-path-1")
        store.add(insight)
        assert store.get("no-path-1") is not None
