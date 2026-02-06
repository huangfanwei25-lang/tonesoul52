import json
from pathlib import Path

from memory.agent_discussion import (
    append_entry,
    audit_file,
    load_entries,
    normalize_entry,
    normalize_file,
)


def _write_lines(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")


def test_normalize_entry_applies_required_defaults():
    entry = normalize_entry({"message": "hello"})
    assert entry["message"] == "hello"
    assert entry["author"] == "unknown"
    assert entry["topic"] == "general"
    assert entry["status"] == "noted"
    assert isinstance(entry["timestamp"], str)
    assert entry["timestamp"]


def test_load_entries_can_include_invalid_lines(tmp_path: Path):
    journal = tmp_path / "agent_discussion.jsonl"
    _write_lines(
        journal,
        [
            json.dumps({"author": "a", "topic": "t1", "status": "noted", "message": "ok"}),
            "{invalid-json",
            json.dumps(["not", "object"]),
        ],
    )

    normal = load_entries(path=journal, include_invalid=False)
    assert len(normal) == 1
    assert normal[0]["author"] == "a"

    with_invalid = load_entries(path=journal, include_invalid=True)
    assert len(with_invalid) == 3
    assert with_invalid[1]["status"] == "invalid"
    assert with_invalid[2]["status"] == "invalid"


def test_audit_file_reports_invalid_counts(tmp_path: Path):
    journal = tmp_path / "agent_discussion.jsonl"
    _write_lines(
        journal,
        [
            json.dumps({"author": "a", "topic": "t1", "status": "noted", "message": "ok"}),
            "{broken",
            json.dumps({"author": "b", "topic": "t2", "status": "pending", "message": "x"}),
        ],
    )

    report = audit_file(path=journal, sample_limit=3)
    assert report["exists"] is True
    assert report["total_lines"] == 3
    assert report["valid_entries"] == 2
    assert report["invalid_entries"] == 1
    assert len(report["invalid_samples"]) == 1


def test_normalize_file_rewrites_and_keeps_invalid_with_backup(tmp_path: Path):
    journal = tmp_path / "agent_discussion.jsonl"
    _write_lines(
        journal,
        [
            json.dumps({"author": "a", "topic": "t1", "status": "noted", "message": "ok"}),
            "{broken",
            json.dumps({"author": "b", "topic": "t2", "status": "pending", "message": "x"}),
        ],
    )

    outcome = normalize_file(path=journal, create_backup=True, keep_invalid=True)
    assert outcome["rewritten"] is True
    assert outcome["invalid_entries_before"] == 1
    assert outcome["invalid_entries"] == 0
    assert outcome["written_entries"] == 3
    assert outcome["backup_path"]
    assert Path(outcome["backup_path"]).exists()

    lines = journal.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    parsed = [json.loads(line) for line in lines]
    assert parsed[1]["status"] == "invalid"


def test_append_entry_writes_normalized_payload(tmp_path: Path):
    journal = tmp_path / "agent_discussion.jsonl"
    entry = append_entry(
        {
            "author": "codex",
            "topic": "sync-test",
            "status": "final",
            "message": "done",
        },
        path=journal,
    )
    assert entry["author"] == "codex"
    assert entry["topic"] == "sync-test"

    rows = load_entries(path=journal)
    assert len(rows) == 1
    assert rows[0]["message"] == "done"
