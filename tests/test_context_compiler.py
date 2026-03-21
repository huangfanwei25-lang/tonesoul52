import json
import re
import sys
from pathlib import Path

import pytest
import yaml

from tonesoul import context_compiler as compiler_mod


def test_load_seed_supports_json_yaml_and_rejects_invalid_payloads(tmp_path):
    json_path = tmp_path / "seed.json"
    yaml_path = tmp_path / "seed.yaml"
    text_path = tmp_path / "seed.txt"
    bad_path = tmp_path / "bad.json"
    json_path.write_text(json.dumps({"task": "T"}), encoding="utf-8")
    yaml_path.write_text("task: T\n", encoding="utf-8")
    text_path.write_text("task: T\n", encoding="utf-8")
    bad_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    assert compiler_mod._load_seed(str(json_path)) == {"task": "T"}
    assert compiler_mod._load_seed(str(yaml_path)) == {"task": "T"}

    with pytest.raises(ValueError, match="Seed file must be .json or .yaml/.yml"):
        compiler_mod._load_seed(str(text_path))
    with pytest.raises(ValueError, match="Seed payload must be an object"):
        compiler_mod._load_seed(str(bad_path))


def test_compile_context_fills_defaults_and_time_island(monkeypatch):
    monkeypatch.setattr(compiler_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(compiler_mod, "stable_hash", lambda value: "hash123")

    payload = compiler_mod.compile_context(
        {
            "task": "T",
            "objective": "O",
            "source": "api",
            "payload": {"value": 1},
            "dependency_basis": ["dep"],
            "change_log": ["chg"],
            "trigger": "cron",
            "decision_mode": "cautious",
            "residual_risk": "medium",
            "rollback_condition": "revert",
            "audit_pointer": "audit#1",
        }
    )

    assert payload["context"] == {
        "task": "T",
        "objective": "O",
        "domain": "general",
        "audience": "internal",
        "mode": "analysis",
    }
    assert payload["assumptions"] == []
    assert payload["constraints"] == []
    assert payload["inputs"] == {"source": "api", "payload": {"value": 1}}
    assert payload["time_island"] == {
        "chronos": {
            "time_stamp": "2026-03-20T00:00:00Z",
            "dependency_basis": ["dep"],
            "change_log": ["chg"],
        },
        "kairos": {
            "trigger": "cron",
            "decision_mode": "cautious",
        },
        "trace": {
            "residual_risk": "medium",
            "rollback_condition": "revert",
            "audit_pointer": "audit#1",
        },
    }
    assert payload["seed_hash"] == "hash123"
    assert payload["generated_at"] == "2026-03-20T00:00:00Z"


def test_resolve_output_and_generate_run_id_format(monkeypatch, tmp_path):
    monkeypatch.setattr(compiler_mod, "_generate_run_id", lambda: "RUN123")

    assert compiler_mod._resolve_output(None, str(tmp_path)) == str(
        tmp_path / "RUN123" / "context.yaml"
    )
    assert compiler_mod._resolve_output(str(tmp_path / "explicit.yaml"), str(tmp_path)) == str(
        (tmp_path / "explicit.yaml").resolve()
    )
    assert re.match(r"^\d{8}T\d{6}\d{3}Z_[0-9a-f]{6}$", compiler_mod._generate_run_id()) is None


def test_generate_run_id_matches_expected_pattern():
    run_id = compiler_mod._generate_run_id()

    assert re.match(r"^\d{8}T\d{6}\d{3}Z_[0-9a-f]{6}$", run_id)


def test_main_loads_seed_applies_overrides_and_writes_yaml(tmp_path, monkeypatch):
    seed_path = tmp_path / "seed.json"
    output_path = tmp_path / "out" / "context.yaml"
    seed_path.write_text(
        json.dumps({"task": "Seed Task", "objective": "Seed Objective", "domain": "ops"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(compiler_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(compiler_mod, "stable_hash", lambda value: "hash123")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "context_compiler",
            "--input",
            str(seed_path),
            "--output",
            str(output_path),
            "--task",
            "Override Task",
            "--decision-mode",
            "lockdown",
        ],
    )

    result = compiler_mod.main()
    saved = yaml.safe_load(output_path.read_text(encoding="utf-8"))

    assert Path(result["context"]) == output_path.resolve()
    assert saved["context"]["task"] == "Override Task"
    assert saved["context"]["objective"] == "Seed Objective"
    assert saved["context"]["domain"] == "ops"
    assert saved["time_island"]["kairos"]["decision_mode"] == "lockdown"
