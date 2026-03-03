from __future__ import annotations

import json
from pathlib import Path

import scripts.run_swarm_resonance_roleplay as swarm_runner


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def test_run_roleplay_dry_run_does_not_write_journal(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_path = tmp_path / "swarm_summary.json"

    summary = swarm_runner.run_roleplay(
        mode="all",
        rounds=6,
        seed=3,
        journal_path=journal_path,
        dry_run=True,
        use_local_llm=False,
        output_path=out_path,
    )

    assert not journal_path.exists()
    assert out_path.exists()
    assert sum(summary["mode_counts"].values()) == 6
    assert summary["dry_run"] is True


def test_run_roleplay_writes_swarm_repair_entries(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_path = tmp_path / "swarm_summary.json"

    summary = swarm_runner.run_roleplay(
        mode="all",
        rounds=8,
        seed=13,
        journal_path=journal_path,
        dry_run=False,
        use_local_llm=False,
        output_path=out_path,
    )

    assert journal_path.exists()
    assert out_path.exists()
    assert sum(summary["decision_counts"].values()) == 8

    rows = _read_jsonl(journal_path)
    assert len(rows) == 8
    for row in rows:
        payload = row.get("payload", row)
        dispatch_trace = payload.get("dispatch_trace")
        assert isinstance(dispatch_trace, dict)
        repair = dispatch_trace.get("repair")
        assert isinstance(repair, dict)
        assert repair.get("type") == "swarm_roleplay_repair"
        assert repair.get("resonance_class")
        assert "disagreement_utility" in repair
        assert "vote_entropy" in repair
