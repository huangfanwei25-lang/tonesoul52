from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.autonomous_cycle import AutonomousDreamCycleRunner
from tonesoul.perception.stimulus import StimulusProcessor
from tonesoul.perception.web_ingest import IngestResult, WebIngestor


class DummyIngestor:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def ingest_urls_sync(self, urls: list[str]):
        self.calls.append(list(urls))
        return list(self.results)


def test_runner_supports_idle_cycle_without_urls(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    journal_path.write_text("", encoding="utf-8")
    runner = AutonomousDreamCycleRunner(
        db_path=tmp_path / "soul.db",
        crystal_path=tmp_path / "crystals.jsonl",
        journal_path=journal_path,
        history_path=tmp_path / "dream_wakeup_history.jsonl",
        snapshot_path=tmp_path / "dream_wakeup_snapshot.json",
        state_path=tmp_path / "dream_wakeup_state.json",
        dashboard_out_dir=tmp_path / "status",
        enable_scribe=False,
        ingestor=DummyIngestor([]),
        stimulus_processor=StimulusProcessor(min_word_count=10),
    )

    result = runner.run(urls=[], max_cycles=1, generate_reflection=False)

    assert result.overall_ok is True
    assert result.urls_requested == 0
    assert result.stimuli_processed == 0
    assert result.memory_write.written == 0
    assert result.wakeup_overall_status == "idle"
    assert Path(result.paths["history_path"]).exists()
    assert Path(result.paths["snapshot_path"]).exists()
    assert Path(result.paths["state_path"]).exists()
    assert Path(result.paths["dashboard_json_path"]).exists()
    assert Path(result.paths["dashboard_html_path"]).exists()
    assert result.runtime_state["next_cycle"] == 2
    assert result.runtime_state["resumed"] is False


def test_runner_ingests_writes_and_refreshes_dashboard(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    journal_path.write_text("", encoding="utf-8")
    content = (
        "This article covers AI governance, memory architecture, agent safety, "
        "pipeline refactors, and deliberation patterns. " * 18
    )
    dummy_ingestor = DummyIngestor(
        [
            IngestResult(
                url="https://example.com/governance",
                title="AI Governance Architecture",
                markdown=content,
                success=True,
            )
        ]
    )
    runner = AutonomousDreamCycleRunner(
        db_path=tmp_path / "soul.db",
        crystal_path=tmp_path / "crystals.jsonl",
        journal_path=journal_path,
        history_path=tmp_path / "dream_wakeup_history.jsonl",
        snapshot_path=tmp_path / "dream_wakeup_snapshot.json",
        state_path=tmp_path / "dream_wakeup_state.json",
        dashboard_out_dir=tmp_path / "status",
        enable_scribe=False,
        ingestor=dummy_ingestor,
        stimulus_processor=StimulusProcessor(min_word_count=10),
    )

    result = runner.run(
        urls=["https://example.com/governance"],
        max_cycles=1,
        limit=1,
        min_priority=0.1,
        related_limit=3,
        crystal_count=2,
        generate_reflection=False,
    )

    assert dummy_ingestor.calls == [["https://example.com/governance"]]
    assert result.urls_requested == 1
    assert result.urls_ingested == 1
    assert result.urls_failed == 0
    assert result.stimuli_processed == 1
    assert result.memory_write.written == 1
    assert result.wakeup_cycle_count == 1
    assert result.wakeup_overall_status == "ok"
    assert result.wakeup_payload["results"][0]["dream_result"]["stimuli_selected"] == 1
    assert result.wakeup_payload["runtime_state"]["next_cycle"] == 2
    assert result.dashboard_payload["metrics"]["wakeup_cycle_count"] == 1
    assert result.dashboard_payload["summary"]["wakeup_avg_friction"]["point_count"] == 1

    history_rows = [
        json.loads(line)
        for line in Path(result.paths["history_path"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(history_rows) == 1
    assert history_rows[0]["status"] == "ok"


def test_runner_resumes_wakeup_state_across_invocations(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    journal_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "dream_wakeup_state.json"

    first_runner = AutonomousDreamCycleRunner(
        db_path=tmp_path / "soul.db",
        crystal_path=tmp_path / "crystals.jsonl",
        journal_path=journal_path,
        history_path=tmp_path / "dream_wakeup_history.jsonl",
        snapshot_path=tmp_path / "dream_wakeup_snapshot.json",
        state_path=state_path,
        dashboard_out_dir=tmp_path / "status",
        enable_scribe=False,
        ingestor=DummyIngestor([]),
        stimulus_processor=StimulusProcessor(min_word_count=10),
    )
    first_result = first_runner.run(urls=[], max_cycles=1, generate_reflection=False)

    second_runner = AutonomousDreamCycleRunner(
        db_path=tmp_path / "soul.db",
        crystal_path=tmp_path / "crystals.jsonl",
        journal_path=journal_path,
        history_path=tmp_path / "dream_wakeup_history.jsonl",
        snapshot_path=tmp_path / "dream_wakeup_snapshot.json",
        state_path=state_path,
        dashboard_out_dir=tmp_path / "status",
        enable_scribe=False,
        ingestor=DummyIngestor([]),
        stimulus_processor=StimulusProcessor(min_word_count=10),
    )
    second_result = second_runner.run(urls=[], max_cycles=1, generate_reflection=False)

    assert first_result.wakeup_payload["results"][0]["cycle"] == 1
    assert second_result.wakeup_payload["results"][0]["cycle"] == 2
    assert first_result.runtime_state["session_id"] == second_result.runtime_state["session_id"]
    assert second_result.runtime_state["resumed"] is True


def test_runner_raises_when_sync_ingestion_is_used_inside_running_event_loop(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    journal_path.write_text("", encoding="utf-8")
    runner = AutonomousDreamCycleRunner(
        db_path=tmp_path / "soul.db",
        crystal_path=tmp_path / "crystals.jsonl",
        journal_path=journal_path,
        history_path=tmp_path / "dream_wakeup_history.jsonl",
        snapshot_path=tmp_path / "dream_wakeup_snapshot.json",
        state_path=tmp_path / "dream_wakeup_state.json",
        dashboard_out_dir=tmp_path / "status",
        enable_scribe=False,
        ingestor=WebIngestor(timeout=1),
        stimulus_processor=StimulusProcessor(min_word_count=10),
    )

    async def _exercise() -> None:
        with pytest.raises(RuntimeError, match="await ingest_urls"):
            runner.run(
                urls=["https://example.com/async-boundary"],
                max_cycles=1,
                generate_reflection=False,
            )

    import asyncio

    asyncio.run(_exercise())
