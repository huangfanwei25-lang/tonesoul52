from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_memory_governance_contract_check as runner


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_render_markdown_includes_failures_and_warnings() -> None:
    payload = {
        "generated_at": "2026-03-01T00:00:00Z",
        "ok": False,
        "failed_count": 1,
        "warning_count": 1,
        "checks": [
            {"name": "schema.read", "status": "pass", "detail": "schema loaded"},
            {"name": "example.routing_trace.route", "status": "fail", "detail": "invalid route"},
            {
                "name": "example.governance_friction.components.delta_wave",
                "status": "warn",
                "detail": "value is null",
            },
        ],
    }
    markdown = runner._render_markdown(payload)
    assert "# Memory Governance Contract Latest" in markdown
    assert "| example.routing_trace.route | FAIL | invalid route |" in markdown
    assert "## Failures" in markdown
    assert "## Warnings" in markdown


def test_run_check_ok_with_valid_schema_and_example(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "spec" / "governance" / "memory_governance_contract_v1.schema.json",
        {
            "type": "object",
            "required": [
                "contract_version",
                "generated_at",
                "source_repo",
                "prior_tension",
                "governance_friction",
                "routing_trace",
            ],
            "properties": {
                "contract_version": {"type": "string"},
                "generated_at": {"type": "string"},
                "source_repo": {"type": "string"},
                "prior_tension": {"type": "object"},
                "governance_friction": {"type": "object"},
                "routing_trace": {"type": "object"},
            },
        },
    )
    _write_json(
        tmp_path / "spec" / "governance" / "memory_governance_contract_v1.example.json",
        {
            "contract_version": "v1",
            "generated_at": "2026-03-01T00:00:00Z",
            "source_repo": "tonesoul52",
            "prior_tension": {"delta_t": 0.3, "gate_decision": "block"},
            "governance_friction": {
                "score": 0.4,
                "components": {"delta_t": 0.2, "delta_wave": 0.4, "boundary_mismatch": False},
            },
            "routing_trace": {
                "route": "route_single_cloud",
                "journal_eligible": False,
                "reason": "standard path",
            },
        },
    )

    payload = runner.run_check(
        repo_root=tmp_path,
        schema_relpath="spec/governance/memory_governance_contract_v1.schema.json",
        example_relpath="spec/governance/memory_governance_contract_v1.example.json",
    )
    assert payload["ok"] is True
    assert payload["failed_count"] == 0


def test_main_strict_fails_when_example_missing_reason(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_json(
        tmp_path / "spec" / "governance" / "memory_governance_contract_v1.schema.json",
        {
            "type": "object",
            "required": [
                "contract_version",
                "generated_at",
                "source_repo",
                "prior_tension",
                "governance_friction",
                "routing_trace",
            ],
            "properties": {
                "contract_version": {"type": "string"},
                "generated_at": {"type": "string"},
                "source_repo": {"type": "string"},
                "prior_tension": {"type": "object"},
                "governance_friction": {"type": "object"},
                "routing_trace": {"type": "object"},
            },
        },
    )
    _write_json(
        tmp_path / "spec" / "governance" / "memory_governance_contract_v1.example.json",
        {
            "contract_version": "v1",
            "generated_at": "2026-03-01T00:00:00Z",
            "source_repo": "tonesoul52",
            "prior_tension": {"delta_t": 0.3, "gate_decision": "block"},
            "governance_friction": {
                "score": 0.4,
                "components": {"delta_t": 0.2, "delta_wave": 0.4, "boundary_mismatch": False},
            },
            "routing_trace": {"route": "route_single_cloud", "journal_eligible": False},
        },
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_memory_governance_contract_check.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )
    exit_code = runner.main()
    assert exit_code == 1
    assert (out_dir / runner.JSON_FILENAME).exists()
    assert (out_dir / runner.MARKDOWN_FILENAME).exists()
