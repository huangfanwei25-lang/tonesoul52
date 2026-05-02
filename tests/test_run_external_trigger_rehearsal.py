from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_external_trigger_rehearsal_module"
    module_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "run_external_trigger_rehearsal.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _status_by_id(payload: dict) -> dict[str, str]:
    return {item["id"]: item["status"] for item in payload["next_actions"]}


def test_reduce_events_marks_ready_without_promoting_to_evidence() -> None:
    module = _load_script_module()
    events = json.loads(
        (
            Path(__file__).resolve().parent / "fixtures" / "external_trigger_rehearsal_events.json"
        ).read_text(encoding="utf-8")
    )

    payload = module.reduce_events(events)

    assert payload["mode"] == "rehearsal"
    assert payload["is_real_evidence"] is False
    assert payload["evidence_status"]["status"] == "synthetic_rehearsal_only"
    assert payload["blocked_by"] == []
    assert "ci_red_is_known_master_lint_debt_only" in payload["no_op_reasons"]
    assert _status_by_id(payload) == {
        "day1_start": "ready",
        "day6_consolidation": "ready",
        "memory_admission_gate": "ready",
    }
    assert payload["summary"]["merged_prs"] == ["32", "33"]
    assert payload["summary"]["countable_beta_sessions"] == 3
    assert payload["summary"]["qualifying_memory_inflation_cases"] == 3


def test_reduce_events_blocks_when_prs_and_evidence_are_missing() -> None:
    module = _load_script_module()
    payload = module.reduce_events(
        [
            {"type": "pr_merged", "number": 32},
            {"type": "beta_session_recorded", "classification": "inconclusive"},
            {"type": "memory_inflation_case", "non_obvious": True, "duplicate": False},
        ]
    )

    assert "missing_pr_merge:33" in payload["blocked_by"]
    assert "1 beta sessions are inconclusive/no-count" in payload["no_op_reasons"]
    assert _status_by_id(payload) == {
        "day1_start": "blocked",
        "day6_consolidation": "blocked",
        "memory_admission_gate": "blocked",
    }


def test_unknown_ci_failure_blocks_even_if_prs_are_merged() -> None:
    module = _load_script_module()
    payload = module.reduce_events(
        [
            {"type": "pr_merged", "number": "#32"},
            {"type": "pr_merged", "number": "#33"},
            {"type": "ci_completed", "status": "failure", "reason": "new_lint_failure"},
        ]
    )

    assert "ci:new_lint_failure" in payload["blocked_by"]
    assert _status_by_id(payload)["day1_start"] == "blocked"


def test_load_events_accepts_jsonl(tmp_path: Path) -> None:
    module = _load_script_module()
    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"type": "pr_merged", "number": 32}),
                json.dumps({"type": "pr_merged", "number": 33}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert module.load_events(path) == [
        {"type": "pr_merged", "number": 32},
        {"type": "pr_merged", "number": 33},
    ]


def test_main_writes_optional_outputs(tmp_path: Path) -> None:
    module = _load_script_module()
    events_path = tmp_path / "events.json"
    json_out = tmp_path / "latest.json"
    markdown_out = tmp_path / "latest.md"
    events_path.write_text(
        json.dumps(
            [
                {"type": "pr_merged", "number": 32},
                {"type": "pr_merged", "number": 33},
            ]
        ),
        encoding="utf-8",
    )

    exit_code = module.main(
        [
            "--events",
            str(events_path),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
    )

    assert exit_code == 0
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["mode"] == "rehearsal"
    assert markdown_out.exists()
    assert "# External Trigger Rehearsal Latest" in markdown_out.read_text(encoding="utf-8")
