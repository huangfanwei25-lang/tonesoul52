from __future__ import annotations

import tonesoul.memory.boot as boot
from tonesoul.memory.crystallizer import MemoryCrystallizer


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


def test_boot_loads_crystals_from_real_store(tmp_path, monkeypatch):
    """If crystals.jsonl exists, boot should load them."""
    crystal_path = tmp_path / "crystals.jsonl"
    crystal_path.write_text(
        '{"rule":"test rule","source_pattern":"test","weight":0.8,'
        '"created_at":"2026-03-02T00:00:00Z","access_count":0,"tags":["test"]}\n',
        encoding="utf-8",
    )

    class DummyIngester:
        def __init__(self, db):
            self.db = db

        def ingest_handoff_dir(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 0, "errors": 0}

        def ingest_sync_md(self, *_args, **_kwargs):
            return {"ingested": 0, "skipped": 1, "errors": 0}

    monkeypatch.setattr(
        boot,
        "MemoryCrystallizer",
        lambda: MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1),
    )
    monkeypatch.setattr(boot, "HandoffIngester", DummyIngester)
    monkeypatch.setattr(boot, "JsonlSoulDB", lambda: object())
    monkeypatch.setattr(boot, "check_and_consolidate", lambda force=False: None)

    result = boot.memory_boot()
    assert result.crystals_loaded == 1
    assert result.top_rules == ["test rule"]
