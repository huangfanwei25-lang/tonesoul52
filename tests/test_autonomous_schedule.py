from __future__ import annotations

import json
from pathlib import Path

from tonesoul.autonomous_schedule import AutonomousRegistrySchedule
from tonesoul.dream_observability import JSON_FILENAME


def _write_registry(path: Path) -> Path:
    path.write_text(
        """
policy:
  review_cycle_days: 120
  allowed_hosts:
    - "example.org"
  blocked_hosts: []
registries:
  - id: "alpha"
    name: "Alpha"
    category: "research"
    urls:
      - "https://example.org/a"
    reviewed_at: "2026-03-01"
  - id: "beta"
    name: "Beta"
    category: "research"
    urls:
      - "https://example.org/b"
    reviewed_at: "2026-03-01"
  - id: "gamma"
    name: "Gamma"
    category: "news"
    urls:
      - "https://example.org/c"
    reviewed_at: "2026-03-01"
""".strip() + "\n",
        encoding="utf-8",
    )
    return path


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class DummyResult:
    def __init__(self, urls: list[str]) -> None:
        self._urls = list(urls)

    def to_dict(self) -> dict[str, object]:
        return {
            "overall_ok": True,
            "urls_requested": len(self._urls),
            "selected_urls": list(self._urls),
        }


class DummyRunner:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(dict(kwargs))
        return DummyResult(list(kwargs.get("urls", [])))


class FailureThenSuccessRunner:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(dict(kwargs))
        urls = list(kwargs.get("urls", []))
        if len(self.calls) == 1:
            return {
                "overall_ok": False,
                "urls_requested": len(urls),
                "urls_failed": len(urls),
                "ingestion_failures": [{"url": url, "error": "boom"} for url in urls],
            }
        return {
            "overall_ok": True,
            "urls_requested": len(urls),
            "urls_failed": 0,
            "ingestion_failures": [],
        }


class TensionBreachRunner:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(dict(kwargs))
        urls = list(kwargs.get("urls", []))
        return {
            "overall_ok": True,
            "urls_requested": len(urls),
            "ingestion_failures": [],
            "wakeup_payload": {
                "results": [
                    {
                        "summary": {
                            "max_friction_score": 0.91,
                            "max_lyapunov_proxy": 0.22,
                            "council_count": 2,
                        }
                    }
                ]
            },
        }


class PreflightLatencyBreachRunner:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(dict(kwargs))
        urls = list(kwargs.get("urls", []))
        return {
            "overall_ok": True,
            "urls_requested": len(urls),
            "ingestion_failures": [],
            "wakeup_payload": {
                "results": [
                    {
                        "summary": {
                            "max_friction_score": 0.31,
                            "max_lyapunov_proxy": 0.08,
                            "council_count": 0,
                            "llm_preflight_latency_ms": 2002,
                            "llm_preflight_selection_latency_ms": 759,
                            "llm_preflight_probe_latency_ms": 1243,
                            "llm_preflight_timeout_count": 1,
                            "llm_preflight_reason": "timeout",
                        }
                    }
                ]
            },
        }


class RuntimeFailureStreakRunner:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run(self, **kwargs):
        self.calls.append(dict(kwargs))
        urls = list(kwargs.get("urls", []))
        return {
            "overall_ok": True,
            "urls_requested": len(urls),
            "ingestion_failures": [],
            "runtime_state": {
                "session_id": "wakeup_alpha",
                "next_cycle": 4,
                "consecutive_failures": 2,
                "resumed": True,
            },
            "wakeup_payload": {
                "results": [
                    {
                        "summary": {
                            "max_friction_score": 0.21,
                            "max_lyapunov_proxy": 0.05,
                            "council_count": 0,
                            "consecutive_failure_count": 2,
                            "session_resumed": True,
                        }
                    }
                ]
            },
        }


def test_schedule_rotates_through_registry_entries_and_writes_history(tmp_path: Path) -> None:
    runner = DummyRunner()
    schedule = AutonomousRegistrySchedule(
        runner=runner,
        registry_path=_write_registry(tmp_path / "registry.yaml"),
        state_path=tmp_path / "state.json",
        snapshot_path=tmp_path / "latest.json",
        history_path=tmp_path / "history.jsonl",
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=2,
        entries_per_cycle=1,
        urls_per_cycle=1,
        cycle_kwargs={"limit": 1, "generate_reflection": False},
    )

    assert payload["overall_ok"] is True
    assert runner.calls[0]["urls"] == ["https://example.org/a"]
    assert runner.calls[1]["urls"] == ["https://example.org/b"]
    assert payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["alpha"]
    assert payload["results"][1]["registry_batch"]["selected_entry_ids"] == ["beta"]
    assert payload["state"]["cursor"] == 2

    history_rows = [
        json.loads(line)
        for line in (tmp_path / "history.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(history_rows) == 2
    assert history_rows[0]["registry_batch"]["selected_urls"] == ["https://example.org/a"]


def test_schedule_persists_cursor_across_invocations(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    runner_one = DummyRunner()
    schedule_one = AutonomousRegistrySchedule(
        runner=runner_one,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    first_payload = schedule_one.run(
        max_cycles=1,
        entries_per_cycle=1,
        urls_per_cycle=1,
        cycle_kwargs={"generate_reflection": False},
    )

    runner_two = DummyRunner()
    schedule_two = AutonomousRegistrySchedule(
        runner=runner_two,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    second_payload = schedule_two.run(
        max_cycles=1,
        entries_per_cycle=1,
        urls_per_cycle=1,
        cycle_kwargs={"generate_reflection": False},
    )

    assert first_payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["alpha"]
    assert second_payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["beta"]
    assert runner_two.calls[0]["urls"] == ["https://example.org/b"]


def test_schedule_marks_payload_not_ok_when_registry_filter_matches_nothing(
    tmp_path: Path,
) -> None:
    runner = DummyRunner()
    schedule = AutonomousRegistrySchedule(
        runner=runner,
        registry_path=_write_registry(tmp_path / "registry.yaml"),
        state_path=tmp_path / "state.json",
        snapshot_path=tmp_path / "latest.json",
        history_path=tmp_path / "history.jsonl",
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=1,
        categories=["nonexistent"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        cycle_kwargs={"generate_reflection": False},
    )

    assert payload["overall_ok"] is False
    assert payload["results"][0]["registry_batch"]["selected_entry_ids"] == []
    assert runner.calls[0]["urls"] == []
    assert payload["state"]["cursor"] == 0


def test_schedule_applies_revisit_cooldown_and_reports_deferred_entries(
    tmp_path: Path,
) -> None:
    runner = DummyRunner()
    schedule = AutonomousRegistrySchedule(
        runner=runner,
        registry_path=_write_registry(tmp_path / "registry.yaml"),
        state_path=tmp_path / "state.json",
        snapshot_path=tmp_path / "latest.json",
        history_path=tmp_path / "history.jsonl",
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=3,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        revisit_interval_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    assert payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["alpha"]
    assert payload["results"][1]["registry_batch"]["selected_entry_ids"] == ["beta"]
    assert payload["results"][2]["registry_batch"]["selected_entry_ids"] == []
    assert payload["results"][2]["registry_batch"]["deferred_entries"] == [
        {
            "id": "alpha",
            "reason": "revisit_cooldown",
            "available_after_cycle": 4,
            "last_selected_cycle": 1,
        },
        {
            "id": "beta",
            "reason": "revisit_cooldown",
            "available_after_cycle": 5,
            "last_selected_cycle": 2,
        },
    ]
    assert runner.calls[2]["urls"] == []


def test_schedule_applies_failure_backoff_across_invocations(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    failing_runner = FailureThenSuccessRunner()
    first_schedule = AutonomousRegistrySchedule(
        runner=failing_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    first_payload = first_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        failure_backoff_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    second_runner = DummyRunner()
    second_schedule = AutonomousRegistrySchedule(
        runner=second_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    second_payload = second_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        failure_backoff_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    assert first_payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["alpha"]
    assert second_payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["beta"]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["entry_states"]["alpha"]["consecutive_failures"] == 1
    assert state["entry_states"]["alpha"]["backoff_until_cycle"] == 3


def test_schedule_applies_deterministic_weighted_category_cadence(tmp_path: Path) -> None:
    runner = DummyRunner()
    schedule = AutonomousRegistrySchedule(
        runner=runner,
        registry_path=_write_registry(tmp_path / "registry.yaml"),
        state_path=tmp_path / "state.json",
        snapshot_path=tmp_path / "latest.json",
        history_path=tmp_path / "history.jsonl",
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=4,
        entries_per_cycle=1,
        urls_per_cycle=1,
        category_weights={"research": 1, "news": 2},
        cycle_kwargs={"generate_reflection": False},
    )

    assert [call["urls"] for call in runner.calls] == [
        ["https://example.org/a"],
        ["https://example.org/c"],
        ["https://example.org/c"],
        ["https://example.org/b"],
    ]
    assert [row["registry_batch"]["selected_categories"][0] for row in payload["results"]] == [
        "research",
        "news",
        "news",
        "research",
    ]
    assert payload["results"][0]["registry_batch"]["selection_mode"] == (
        "category_weighted_round_robin"
    )
    assert payload["results"][0]["registry_batch"]["category_slots"] == [
        "research",
        "news",
        "news",
    ]
    assert payload["state"]["category_cursor"] == 1
    assert payload["state"]["category_entry_cursors"] == {"news": 0, "research": 0}


def test_schedule_scales_failure_backoff_by_category_multiplier(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    failing_runner = FailureThenSuccessRunner()
    schedule = AutonomousRegistrySchedule(
        runner=failing_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        failure_backoff_cycles=2,
        category_backoff_multipliers={"research": 3},
        cycle_kwargs={"generate_reflection": False},
    )

    assert payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["alpha"]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["entry_states"]["alpha"]["consecutive_failures"] == 1
    assert state["entry_states"]["alpha"]["backoff_until_cycle"] == 7


def test_schedule_applies_tension_budget_cooldown_to_selected_category(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    breach_runner = TensionBreachRunner()
    first_schedule = AutonomousRegistrySchedule(
        runner=breach_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    first_payload = first_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_friction_score=0.8,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    second_runner = DummyRunner()
    second_schedule = AutonomousRegistrySchedule(
        runner=second_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    second_payload = second_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_friction_score=0.8,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    first_budget = first_payload["results"][0]["tension_budget"]
    assert first_budget["breached"] is True
    assert first_budget["cooled_categories"] == ["research"]
    assert second_payload["results"][0]["registry_batch"]["selected_entry_ids"] == []
    assert second_payload["results"][0]["registry_batch"]["deferred_categories"] == [
        {
            "category": "research",
            "reason": "tension_budget_cooldown",
            "available_after_cycle": 4,
            "last_budget_status": "breached",
            "last_breach_reasons": [
                "max_friction_score>0.8 (observed=0.91)",
            ],
        }
    ]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["category_states"]["research"]["tension_cooldown_until_cycle"] == 3
    assert state["category_states"]["research"]["last_budget_status"] == "breached"


def test_schedule_applies_llm_preflight_budget_as_global_llm_backoff(
    tmp_path: Path,
) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    breach_runner = PreflightLatencyBreachRunner()
    first_schedule = AutonomousRegistrySchedule(
        runner=breach_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    first_payload = first_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_llm_preflight_latency_ms=1800,
        tension_max_llm_probe_latency_ms=1200,
        tension_max_llm_timeout_count=0,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": True, "require_inference_ready": True},
    )

    second_runner = DummyRunner()
    second_schedule = AutonomousRegistrySchedule(
        runner=second_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    second_payload = second_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_llm_preflight_latency_ms=1800,
        tension_max_llm_probe_latency_ms=1200,
        tension_max_llm_timeout_count=0,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": True, "require_inference_ready": True},
    )

    first_budget = first_payload["results"][0]["tension_budget"]
    assert first_budget["breached"] is True
    assert first_budget["governance_breached"] is False
    assert first_budget["llm_breached"] is True
    assert first_budget["cooled_categories"] == []
    assert first_budget["llm_backoff_requested"] is True
    assert "llm_preflight_latency_ms>1800 (observed=2002)" in first_budget["breach_reasons"]
    assert "llm_probe_latency_ms>1200 (observed=1243)" in first_budget["breach_reasons"]
    assert "llm_preflight_timeout_count>0 (observed=1)" in first_budget["breach_reasons"]
    assert second_payload["results"][0]["registry_batch"]["selected_entry_ids"] == ["beta"]
    assert second_runner.calls[0]["generate_reflection"] is False
    assert second_runner.calls[0]["require_inference_ready"] is False
    assert second_payload["results"][0]["autonomous_payload"]["llm_policy"]["active"] is True
    assert (
        second_payload["results"][0]["autonomous_payload"]["llm_policy"]["action"]
        == "disable_reflection"
    )


def test_schedule_applies_runtime_failure_budget_as_governance_cooldown(
    tmp_path: Path,
) -> None:
    registry_path = _write_registry(tmp_path / "registry.yaml")
    state_path = tmp_path / "state.json"
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    breach_runner = RuntimeFailureStreakRunner()
    first_schedule = AutonomousRegistrySchedule(
        runner=breach_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    first_payload = first_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_consecutive_failure_count=1,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    second_runner = DummyRunner()
    second_schedule = AutonomousRegistrySchedule(
        runner=second_runner,
        registry_path=registry_path,
        state_path=state_path,
        snapshot_path=snapshot_path,
        history_path=history_path,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )
    second_payload = second_schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_consecutive_failure_count=1,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    first_budget = first_payload["results"][0]["tension_budget"]
    assert first_budget["breached"] is True
    assert first_budget["governance_breached"] is True
    assert first_budget["observation"]["max_consecutive_failure_count"] == 2
    assert first_budget["governance_breach_reasons"] == ["consecutive_failure_count>1 (observed=2)"]
    assert first_budget["cooled_categories"] == ["research"]
    assert second_payload["results"][0]["registry_batch"]["selected_entry_ids"] == []
    assert second_payload["results"][0]["registry_batch"]["deferred_categories"] == [
        {
            "category": "research",
            "reason": "tension_budget_cooldown",
            "available_after_cycle": 4,
            "last_budget_status": "breached",
            "last_breach_reasons": [
                "consecutive_failure_count>1 (observed=2)",
            ],
        }
    ]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["category_states"]["research"]["tension_cooldown_until_cycle"] == 3
    assert state["category_states"]["research"]["last_budget_status"] == "breached"
    assert state["llm_backoff"]["backoff_until_cycle"] == 0
    assert state["llm_backoff"]["last_status"] == "ok"


def test_schedule_refreshes_dashboard_with_schedule_governance_artifacts(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"
    dashboard_out_dir = tmp_path / "status"
    journal_path.write_text("", encoding="utf-8")
    _write_jsonl(
        wakeup_path,
        [
            {
                "cycle": 1,
                "status": "ok",
                "finished_at": "2026-03-08T04:00:00Z",
                "summary": {
                    "avg_friction_score": 0.4,
                    "max_friction_score": 0.5,
                    "max_lyapunov_proxy": 0.1,
                    "council_count": 0,
                    "frozen_count": 0,
                },
            }
        ],
    )

    schedule = AutonomousRegistrySchedule(
        runner=TensionBreachRunner(),
        registry_path=_write_registry(tmp_path / "registry.yaml"),
        state_path=tmp_path / "state.json",
        snapshot_path=tmp_path / "latest.json",
        history_path=tmp_path / "history.jsonl",
        journal_path=journal_path,
        wakeup_path=wakeup_path,
        dashboard_out_dir=dashboard_out_dir,
        interval_seconds=0.0,
        sleep_func=lambda _seconds: None,
    )

    payload = schedule.run(
        max_cycles=1,
        categories=["research"],
        entries_per_cycle=1,
        urls_per_cycle=1,
        tension_max_friction_score=0.8,
        tension_cooldown_cycles=2,
        cycle_kwargs={"generate_reflection": False},
    )

    assert payload["overall_ok"] is True
    dashboard_payload = json.loads((dashboard_out_dir / JSON_FILENAME).read_text(encoding="utf-8"))
    assert (
        dashboard_payload["inputs"]["schedule_history_path"]
        == (tmp_path / "history.jsonl").as_posix()
    )
    assert dashboard_payload["summary"]["schedule_governance_cooldown_applied_total"] == 1
    assert dashboard_payload["schedule_state"]["active_governance_cooldown_count"] == 1
    assert dashboard_payload["recent_schedule_cycles"][-1]["cooled_categories"] == ["research"]
