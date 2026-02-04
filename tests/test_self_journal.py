import uuid
from pathlib import Path

from tonesoul.council import PreOutputCouncil
from tonesoul.council.self_journal import load_recent_memory, record_self_memory


def _journal_path() -> Path:
    base = Path("temp") / "pytest-self-journal"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"journal-{uuid.uuid4().hex}.jsonl"


def test_record_self_memory_writes_entry():
    council = PreOutputCouncil()
    verdict = council.validate("The weather is nice today.", context={})

    journal_path = _journal_path()
    entry = record_self_memory(
        verdict,
        context={"self_identity": "ToneSoul", "language": "en"},
        path=journal_path,
    )

    assert entry["identity"] == "ToneSoul"
    assert entry["verdict"] == verdict.verdict.value
    assert "self_statement" in entry and entry["self_statement"]

    entries = load_recent_memory(limit=1, path=journal_path)
    assert len(entries) == 1
    assert entries[0]["identity"] == "ToneSoul"


def test_load_recent_memory_returns_latest():
    journal_path = _journal_path()
    # Write two entries on separate lines (JSONL format)
    journal_path.write_text(
        '{"identity": "A", "verdict": "approve"}\n{"identity": "B", "verdict": "block"}\n',
        encoding="utf-8",
    )

    entries = load_recent_memory(limit=1, path=journal_path)
    assert entries[0]["identity"] == "B"
