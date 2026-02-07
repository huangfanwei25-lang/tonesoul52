import json
import uuid
from pathlib import Path

import memory.self_memory as self_memory
import tools.governed_poster as governed_poster
from memory.genesis import Genesis
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource
from tools.schema import tool_success


def _tmp_dir() -> Path:
    base = Path("temp") / "pytest-governed"
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / f"run-{uuid.uuid4().hex}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def test_governed_poster_records_self_memory(monkeypatch):
    run_dir = _tmp_dir()
    journal_path = run_dir / "self_journal.jsonl"

    def _resolve_soul_db(journal_path_arg=None, soul_db_arg=None):
        return JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: journal_path})

    class DummyGate:
        def load_memories(self):
            return None

        def enhance(self, content, k=2):
            return "memory snapshot"

    def _mock_post_to_moltbook(account, submolt, title, content):
        return tool_success(
            data={"payload": {"id": "test123"}, "post_id": "test123"},
            genesis=Genesis.REACTIVE_SOCIAL,
            intent_id="moltbook:test123",
        )

    def _mock_council_deliberation(content, memories):
        return "APPROVE", "ok", 0.9

    monkeypatch.setattr(self_memory, "_resolve_soul_db", _resolve_soul_db)
    monkeypatch.setattr(governed_poster, "NarrativeGate", DummyGate)
    monkeypatch.setattr(governed_poster, "post_to_moltbook", _mock_post_to_moltbook)
    monkeypatch.setattr(governed_poster, "run_council_deliberation", _mock_council_deliberation)

    output_file = run_dir / "result.json"
    result = governed_poster.governed_post(
        account="tester",
        submolt="unit",
        title="Test Post",
        content="Test content",
        output_file=str(output_file),
    )

    assert result and result.get("success") is True
    assert result.get("data", {}).get("post_id") == "test123"
    assert journal_path.exists()

    line = journal_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    record = json.loads(line)
    payload = record.get("payload", {})

    assert payload.get("genesis") == "reactive_social"
    assert payload.get("is_mine") is False
    assert payload.get("intent_id") == "moltbook:test123"
