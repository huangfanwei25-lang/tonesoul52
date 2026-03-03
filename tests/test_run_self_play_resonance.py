from __future__ import annotations

import json
from pathlib import Path

import scripts.run_self_play_resonance as self_play_runner


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def test_run_self_play_dry_run_does_not_write_journal(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_path = tmp_path / "self_play_summary.json"

    summary = self_play_runner.run_self_play(
        mode="all",
        rounds=8,
        seed=7,
        journal_path=journal_path,
        dry_run=True,
        use_local_llm=False,
        output_path=out_path,
    )

    assert not journal_path.exists()
    assert out_path.exists()
    assert sum(summary["mode_counts"].values()) == 8
    assert summary["dry_run"] is True


def test_run_self_play_writes_repair_entries(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_path = tmp_path / "self_play_summary.json"

    summary = self_play_runner.run_self_play(
        mode="all",
        rounds=12,
        seed=11,
        journal_path=journal_path,
        dry_run=False,
        use_local_llm=False,
        output_path=out_path,
    )

    assert journal_path.exists()
    assert out_path.exists()
    assert sum(summary["mode_counts"].values()) == 12

    rows = _read_jsonl(journal_path)
    assert len(rows) == 12

    resonance_classes = []
    for row in rows:
        payload = row.get("payload", row)
        dispatch_trace = payload.get("dispatch_trace")
        assert isinstance(dispatch_trace, dict)
        repair = dispatch_trace.get("repair")
        assert isinstance(repair, dict)
        assert repair.get("type") == "self_play_resonance"
        assert repair.get("resonance_class")
        resonance_classes.append(str(repair.get("resonance_class")))

    assert "flow" in resonance_classes
    assert any(cls in {"resonance", "deep_resonance"} for cls in resonance_classes)
