from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_dream_observability_dashboard.py"
    spec = importlib.util.spec_from_file_location("run_dream_observability_dashboard_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_parser_parses_dashboard_flags(tmp_path: Path) -> None:
    module = _load_module()
    out_dir = tmp_path / "status"
    schedule_history_path = tmp_path / "schedule_history.jsonl"
    schedule_state_path = tmp_path / "schedule_state.json"

    args = module.build_parser().parse_args(
        [
            "--max-points",
            "80",
            "--out-dir",
            str(out_dir),
            "--schedule-history-path",
            str(schedule_history_path),
            "--schedule-state-path",
            str(schedule_state_path),
            "--strict",
        ]
    )

    assert args.max_points == 80
    assert args.out_dir == str(out_dir)
    assert args.schedule_history_path == str(schedule_history_path)
    assert args.schedule_state_path == str(schedule_state_path)
    assert args.strict is True


def test_run_dashboard_writes_json_and_html_artifacts(tmp_path: Path) -> None:
    module = _load_module()
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"
    schedule_history_path = tmp_path / "registry_schedule_history.jsonl"
    schedule_state_path = tmp_path / "registry_schedule_state.json"
    out_dir = tmp_path / "status"

    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-03-07T19:00:00Z",
                "tension_before": {
                    "timestamp": "2026-03-07T19:00:00Z",
                    "signals": {"cognitive_friction": 0.3},
                    "prediction": {"lyapunov_exponent": 0.2},
                },
            }
        ],
    )
    _write_jsonl(
        wakeup_path,
        [
            {
                "cycle": 1,
                "status": "ok",
                "finished_at": "2026-03-07T19:10:00Z",
                "summary": {
                    "avg_friction_score": 0.44,
                    "max_friction_score": 0.62,
                    "max_lyapunov_proxy": 0.19,
                    "council_count": 1,
                    "frozen_count": 0,
                    "scribe_evaluated": True,
                    "scribe_triggered": True,
                    "scribe_status": "generated",
                    "scribe_generation_mode": "template_assist",
                    "scribe_state_document_posture": "pressure_without_counterweight",
                    "scribe_problem_route_status_line": (
                        "route | family=F6_semantic_role_boundary_integrity "
                        "invariant=chronicle_self_scope "
                        "repair=semantic_boundary_guardrail "
                        "secondary=F4_execution_contract_integrity"
                    ),
                    "scribe_problem_route_secondary_labels": ("F4_execution_contract_integrity"),
                    "scribe_latest_available_source": "chronicle_pair",
                },
            }
        ],
    )
    _write_jsonl(
        schedule_history_path,
        [
            {
                "cycle": 1,
                "finished_at": "2026-03-08T00:11:00Z",
                "registry_batch": {
                    "selected_categories": ["research"],
                    "deferred_category_count": 0,
                },
                "autonomous_payload": {
                    "llm_policy": {
                        "active": True,
                        "mode": "probe_latency",
                        "action": "disable_reflection",
                        "reason_count": 1,
                    }
                },
                "tension_budget": {
                    "cooled_categories": ["research"],
                    "llm_backoff_requested": True,
                },
            }
        ],
    )
    schedule_state_path.write_text(
        json.dumps(
            {
                "cycles_run": 1,
                "category_states": {
                    "research": {
                        "tension_cooldown_until_cycle": 2,
                    }
                },
                "llm_backoff": {
                    "backoff_until_cycle": 3,
                    "last_status": "breached",
                    "last_mode": "probe_latency",
                    "last_breach_reasons": ["llm_probe_latency_ms>1200 (observed=1243)"],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    payload = module.run_dashboard(
        module.build_parser().parse_args(
            [
                "--journal-path",
                str(journal_path),
                "--wakeup-path",
                str(wakeup_path),
                "--schedule-history-path",
                str(schedule_history_path),
                "--schedule-state-path",
                str(schedule_state_path),
                "--out-dir",
                str(out_dir),
            ]
        )
    )

    assert payload["overall_ok"] is True
    json_payload = json.loads((out_dir / module.JSON_FILENAME).read_text(encoding="utf-8"))
    html_text = (out_dir / module.HTML_FILENAME).read_text(encoding="utf-8")
    assert json_payload["metrics"]["journal_entry_count"] == 1
    assert json_payload["metrics"]["schedule_cycle_count"] == 1
    assert json_payload["schedule_state"]["llm_backoff_active"] is True
    assert json_payload["handoff"]["queue_shape"] == "dream_observability_ready"
    assert (
        json_payload["problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert json_payload["problem_route_secondary_labels"] == "F4_execution_contract_integrity"
    assert "Dream Observability Dashboard" in html_text
    assert "Recent Schedule Cycles" in html_text


def test_main_strict_returns_non_zero_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_module()
    journal_path = tmp_path / "self_journal.jsonl"
    wakeup_path = tmp_path / "dream_wakeup_history.jsonl"
    out_dir = tmp_path / "status"

    journal_path.write_text('{"timestamp":"2026-03-07T19:00:00Z"}\n{"broken":\n', encoding="utf-8")
    _write_jsonl(
        wakeup_path,
        [
            {
                "cycle": 1,
                "status": "ok",
                "finished_at": "2026-03-07T19:10:00Z",
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

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_dream_observability_dashboard.py",
            "--journal-path",
            str(journal_path),
            "--wakeup-path",
            str(wakeup_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = module.main()

    assert exit_code == 1
    assert (out_dir / module.JSON_FILENAME).exists()
    assert (out_dir / module.HTML_FILENAME).exists()
