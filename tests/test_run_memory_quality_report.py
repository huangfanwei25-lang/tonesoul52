from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_memory_quality_report as memory_quality_runner


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_report_returns_warning_when_journal_is_missing(tmp_path: Path) -> None:
    payload, samples = memory_quality_runner.build_report(tmp_path / "missing.jsonl")
    assert payload["overall_ok"] is True
    assert payload["metrics"]["entry_count"] == 0
    assert payload["metrics"]["failure_case_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]
    assert samples == []


def test_build_report_extracts_failure_learning_samples(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "verdict": "approve",
                "timestamp": "2026-02-01T00:00:00Z",
            },
            {
                "payload": {
                    "timestamp": "2026-02-01T00:01:00Z",
                    "verdict": "block",
                    "risk_level": "high",
                    "intent_id": "intent-1",
                    "genesis": "reactive_user",
                    "core_divergence": "guardian safety objection",
                    "recommended_action": "block and escalate",
                    "coherence": 0.24,
                    "uncertainty_band": "high",
                    "transcript": {
                        "multi_agent_contract": {
                            "records": [
                                {
                                    "role": "Guardian",
                                    "evidence": ["policy-1"],
                                    "risk": {"level": "high", "basis": "safety"},
                                }
                            ]
                        }
                    },
                }
            },
            {
                "timestamp": "2026-02-01T00:02:00Z",
                "verdict": "declare_stance",
                "coherence": 0.61,
                "transcript": {
                    "divergence_analysis": {
                        "core_divergence": "critic vs advocate",
                        "recommended_action": "declare stance",
                    }
                },
            },
        ],
    )

    payload, samples = memory_quality_runner.build_report(journal_path)
    metrics = payload["metrics"]
    quality = payload["quality_signals"]

    assert payload["overall_ok"] is True
    assert metrics["entry_count"] == 3
    assert metrics["failure_case_count"] == 2
    assert metrics["learning_sample_count"] == 2
    assert metrics["verdict_counts"]["approve"] == 1
    assert metrics["verdict_counts"]["block"] == 1
    assert metrics["verdict_counts"]["declare_stance"] == 1
    assert metrics["risk_level_counts"]["high"] == 1
    assert metrics["risk_level_counts"]["medium"] == 1
    assert quality["provenance_coverage_rate"] == 0.5
    assert quality["contract_coverage_rate"] == 0.5
    assert len(samples) == 2
    assert samples[0]["verdict"] in {"block", "declare_stance"}
    assert "sample_id" in samples[0]


def test_main_strict_fails_when_invalid_json_lines_detected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    out_dir = tmp_path / "status"
    journal_path.write_text(
        '{"timestamp":"2026-02-01T00:00:00Z","verdict":"block"}\n' '{"timestamp":"broken"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_memory_quality_report.py",
            "--journal-path",
            str(journal_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )
    exit_code = memory_quality_runner.main()
    assert exit_code == 1
    assert (out_dir / memory_quality_runner.JSON_FILENAME).exists()
    assert (out_dir / memory_quality_runner.MARKDOWN_FILENAME).exists()
    assert (out_dir / memory_quality_runner.SAMPLES_FILENAME).exists()
