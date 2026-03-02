from __future__ import annotations

import tonesoul.memory.boot as boot


def test_memory_boot_empty_store(monkeypatch):
    class DummyCrystallizer:
        def top_crystals(self, n=5):
            return []

    class DummyIngester:
        def __init__(self, db):
            self.db = db

        def ingest_handoff_dir(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 0, "errors": 0}

        def ingest_sync_md(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 1, "errors": 0}

    monkeypatch.setattr(boot, "MemoryCrystallizer", DummyCrystallizer)
    monkeypatch.setattr(boot, "HandoffIngester", DummyIngester)
    monkeypatch.setattr(boot, "JsonlSoulDB", lambda: object())
    monkeypatch.setattr(boot, "check_and_consolidate", lambda force=False: None)

    result = boot.memory_boot()

    assert result.crystals_loaded == 0
    assert result.top_rules == []
    assert result.consolidation_ran is False
    assert result.consolidation_result is None
    assert result.handoffs_ingested == 0
    assert result.boot_time_ms >= 0.0


def test_memory_boot_loads_crystals_without_consolidation(monkeypatch):
    class DummyCrystal:
        def __init__(self, rule):
            self.rule = rule

    class DummyCrystallizer:
        def top_crystals(self, n=5):
            return [DummyCrystal("rule-a"), DummyCrystal("rule-b")]

    class DummyIngester:
        def __init__(self, db):
            self.db = db

        def ingest_handoff_dir(self, *_args, **_kwargs):
            return {"ingested": 2, "skipped": 0, "errors": 0}

        def ingest_sync_md(self, *_args, **_kwargs):
            return {"ingested": 1, "skipped": 0, "errors": 0}

    monkeypatch.setattr(boot, "MemoryCrystallizer", DummyCrystallizer)
    monkeypatch.setattr(boot, "HandoffIngester", DummyIngester)
    monkeypatch.setattr(boot, "JsonlSoulDB", lambda: object())
    monkeypatch.setattr(boot, "check_and_consolidate", lambda force=False: None)

    result = boot.memory_boot()

    assert result.crystals_loaded == 2
    assert result.top_rules == ["rule-a", "rule-b"]
    assert result.consolidation_ran is False
    assert result.consolidation_result is None
    assert result.handoffs_ingested >= 2


def test_memory_boot_force_consolidation(monkeypatch):
    class DummyCrystallizer:
        def top_crystals(self, n=5):
            return []

    class DummyIngester:
        def __init__(self, db):
            self.db = db

        def ingest_handoff_dir(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 0, "errors": 0}

        def ingest_sync_md(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 1, "errors": 0}

    calls = {"force": None}

    def _fake_consolidate(force=False):
        calls["force"] = force
        return {"status": "success", "episodes_processed": 3}

    monkeypatch.setattr(boot, "MemoryCrystallizer", DummyCrystallizer)
    monkeypatch.setattr(boot, "HandoffIngester", DummyIngester)
    monkeypatch.setattr(boot, "JsonlSoulDB", lambda: object())
    monkeypatch.setattr(boot, "check_and_consolidate", _fake_consolidate)

    result = boot.memory_boot(force_consolidation=True)

    assert calls["force"] is True
    assert result.consolidation_ran is True
    assert isinstance(result.consolidation_result, dict)
    assert result.consolidation_result.get("status") == "success"
