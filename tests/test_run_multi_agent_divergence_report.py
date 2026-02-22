from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_multi_agent_divergence_report as divergence_runner


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _valid_record(*, role: str, risk_level: str, next_role: str) -> dict[str, object]:
    return {
        "role": role,
        "claim": f"{role} claim",
        "evidence": ["e1", "e2"],
        "risk": {"level": risk_level, "basis": "contract-check"},
        "handoff": {"next_role": next_role, "action": "continue"},
    }


def test_build_report_returns_warning_when_journal_is_missing(tmp_path: Path) -> None:
    payload = divergence_runner.build_report(tmp_path / "missing.jsonl")
    assert payload["overall_ok"] is True
    assert payload["metrics"]["entry_count"] == 0
    assert payload["metrics"]["contract_record_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]


def test_build_report_aggregates_contract_metrics(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "payload": {
                    "verdict": "approve",
                    "core_divergence": "need stronger provenance",
                    "transcript": {
                        "multi_agent_contract": {
                            "records": [
                                _valid_record(
                                    role="Engineer", risk_level="low", next_role="Guardian"
                                ),
                                _valid_record(
                                    role="Guardian", risk_level="high", next_role="Philosopher"
                                ),
                            ]
                        }
                    },
                }
            },
            {
                "verdict": "revise",
                "divergence_analysis": {"core_divergence": "memory confidence mismatch"},
                "transcript": {
                    "multi_agent_contract": {
                        "records": [
                            _valid_record(
                                role="Philosopher", risk_level="critical", next_role="Engineer"
                            )
                        ]
                    }
                },
            },
        ],
    )

    payload = divergence_runner.build_report(journal_path)
    metrics = payload["metrics"]
    assert payload["overall_ok"] is True
    assert metrics["entry_count"] == 2
    assert metrics["contract_entry_count"] == 2
    assert metrics["contract_record_count"] == 3
    assert metrics["invalid_record_count"] == 0
    assert metrics["high_risk_record_count"] == 2
    assert metrics["verdict_counts"]["approve"] == 1
    assert metrics["verdict_counts"]["revise"] == 1
    assert metrics["role_counts"]["Engineer"] == 1
    assert metrics["risk_level_counts"]["critical"] == 1
    assert metrics["handoff_next_role_counts"]["Guardian"] == 1
    assert "need stronger provenance" in payload["divergence_examples"]


def test_build_report_marks_invalid_contract_records(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "verdict": "approve",
                "transcript": {
                    "multi_agent_contract": {
                        "records": [
                            {
                                "role": "",
                                "claim": "missing fields",
                                "evidence": [],
                                "risk": {"level": "high"},
                                "handoff": {"next_role": "Engineer"},
                            }
                        ]
                    }
                },
            }
        ],
    )
    payload = divergence_runner.build_report(journal_path)
    assert payload["overall_ok"] is False
    assert payload["metrics"]["invalid_record_count"] == 1
    assert payload["issues"]


def test_main_strict_returns_non_zero_on_invalid_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_dir = tmp_path / "status"
    _write_jsonl(
        journal_path,
        [
            {
                "verdict": "approve",
                "transcript": {"multi_agent_contract": {"records": [{"role": "Engineer"}]}},
            }
        ],
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_multi_agent_divergence_report.py",
            "--journal-path",
            str(journal_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = divergence_runner.main()
    assert exit_code == 1
    assert (out_dir / divergence_runner.JSON_FILENAME).exists()
    assert (out_dir / divergence_runner.MARKDOWN_FILENAME).exists()
