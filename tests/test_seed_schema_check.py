from __future__ import annotations

import json
import sys
from pathlib import Path

from tonesoul.issue_codes import IssueCode, issue
from tonesoul.seed_schema_check import REQUIRED_TOP, check_seed_schema, main


def _valid_seed() -> dict[str, object]:
    return {
        "seed_version": "1.0",
        "run_id": "run-001",
        "run_path": "memory/seeds/run-001.json",
        "created_at": "2026-03-19T00:00:00+00:00",
        "metadata": {
            "id": "seed-001",
            "chronos": "kairos",
            "author": "tonesoul",
            "license": "MIT",
        },
        "provenance": {
            "source": {
                "run_id": "run-001",
                "run_path": "memory/seeds/run-001.json",
                "context": "bootstrap",
            },
            "confidence": 0.8,
            "parent_seed": None,
        },
        "content": {
            "title": "Seed title",
            "summary": "Seed summary",
        },
        "governance": {
            "canonical": True,
            "rules": [],
        },
        "anchor": {
            "content_hash": "abc123",
            "event_id": "evt-001",
        },
        "sigma_stamp": {},
        "state_history": [],
        "context_hash": "ctx-001",
        "pointers": {
            "context": "context.json",
            "frame_plan": "frame_plan.json",
            "constraints": "constraints.json",
            "execution_report": "execution_report.json",
            "audit_request": "audit_request.json",
        },
        "ystm_stats": {},
        "ystm_snapshot": {},
    }


def test_valid_seed_passes() -> None:
    assert check_seed_schema(_valid_seed()) == []


def test_missing_required_key() -> None:
    seed = _valid_seed()
    del seed["run_id"]

    issues = check_seed_schema(seed)

    assert issue(IssueCode.SEED_FIELD_MISSING, field="run_id") in issues


def test_partial_seed_lists_all_missing() -> None:
    issues = check_seed_schema(
        {
            "metadata": {"id": "seed-001"},
            "provenance": {"source": {}},
            "content": {},
        }
    )

    assert issue(IssueCode.SEED_FIELD_MISSING, field="seed_version") in issues
    assert issue(IssueCode.METADATA_FIELD_MISSING, field="chronos") in issues
    assert issue(IssueCode.PROVENANCE_FIELD_MISSING, field="confidence") in issues
    assert issue(IssueCode.PROVENANCE_SOURCE_FIELD_MISSING, field="run_id") in issues
    assert issue(IssueCode.CONTENT_FIELD_MISSING, field="title") in issues


def test_empty_seed() -> None:
    issues = check_seed_schema({})

    for key in REQUIRED_TOP:
        assert issue(IssueCode.SEED_FIELD_MISSING, field=key) in issues
    assert issue(IssueCode.METADATA_MISSING) in issues
    assert issue(IssueCode.PROVENANCE_MISSING) in issues
    assert issue(IssueCode.CONTENT_MISSING) in issues
    assert issue(IssueCode.GOVERNANCE_MISSING) in issues
    assert issue(IssueCode.ANCHOR_MISSING) in issues
    assert issue(IssueCode.POINTERS_MISSING) in issues


def test_main_with_valid_file(monkeypatch, tmp_path: Path) -> None:
    seed_path = tmp_path / "seed.json"
    seed_path.write_text(json.dumps(_valid_seed()), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["seed_schema_check.py", "--seed", str(seed_path)])

    assert main() == 0
