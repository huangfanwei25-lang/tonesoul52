from __future__ import annotations

import json
from pathlib import Path

import scripts.run_l8_adapter_dataset_gate as runner


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_report_accepts_public_safe_example(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.schema.json",
        {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "contract_version",
                "row_id",
                "source_repo",
                "source_artifact",
                "training_objective",
                "behavior_class",
                "user_message",
                "synthesizer_decision",
                "final_response",
                "tension_level",
                "provenance",
                "distillation_review",
                "evaluation_expectations",
            ],
            "properties": {
                "contract_version": {"type": "string", "const": "v1"},
                "row_id": {"type": "string", "minLength": 1},
                "source_repo": {"type": "string"},
                "source_artifact": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "kind", "public_safe"],
                    "properties": {
                        "path": {"type": "string"},
                        "kind": {"type": "string"},
                        "public_safe": {"type": "boolean"},
                    },
                },
                "training_objective": {"type": "string"},
                "behavior_class": {"type": "string"},
                "user_message": {"type": "string"},
                "synthesizer_decision": {"type": "string"},
                "final_response": {"type": "string"},
                "tension_level": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "provenance": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["source_path", "transformation_chain", "review_scope"],
                    "properties": {
                        "source_path": {"type": "string"},
                        "transformation_chain": {"type": "array", "items": {"type": "string"}},
                        "review_scope": {"type": "string"},
                    },
                },
                "distillation_review": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "public_safe",
                        "privacy_cleared",
                        "governance_reviewed",
                        "approved_for_adapter_rl",
                    ],
                    "properties": {
                        "public_safe": {"type": "boolean"},
                        "privacy_cleared": {"type": "boolean"},
                        "governance_reviewed": {"type": "boolean"},
                        "approved_for_adapter_rl": {"type": "boolean"},
                    },
                },
                "evaluation_expectations": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "verifier_pass_rate_floor",
                        "auditability_required",
                        "regression_suite",
                        "reversible",
                    ],
                    "properties": {
                        "verifier_pass_rate_floor": {"type": "number"},
                        "auditability_required": {"type": "boolean"},
                        "regression_suite": {"type": "string"},
                        "reversible": {"type": "boolean"},
                    },
                },
            },
        },
    )
    _write_json(
        tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.example.json",
        {
            "contract_version": "v1",
            "row_id": "adapter-row-001",
            "source_repo": "tonesoul52",
            "source_artifact": {
                "path": "docs/status/l8_distillation_boundary_latest.json",
                "kind": "public_safe_trace_summary",
                "public_safe": True,
            },
            "training_objective": "governance_posture",
            "behavior_class": "governance_posture",
            "user_message": "answer carefully",
            "synthesizer_decision": "use verifier-first posture",
            "final_response": "I will answer conservatively.",
            "tension_level": 0.4,
            "provenance": {
                "source_path": "docs/status/l8_distillation_boundary_latest.json",
                "transformation_chain": ["reviewed_public_trace"],
                "review_scope": "human_plus_verifier",
            },
            "distillation_review": {
                "public_safe": True,
                "privacy_cleared": True,
                "governance_reviewed": True,
                "approved_for_adapter_rl": True,
            },
            "evaluation_expectations": {
                "verifier_pass_rate_floor": 0.95,
                "auditability_required": True,
                "regression_suite": "public_governance_eval_v1",
                "reversible": True,
            },
        },
    )

    payload = runner.build_report(
        repo_root=tmp_path,
        input_path=tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.example.json",
        schema_path=tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.schema.json",
    )

    assert payload["ok"] is True
    assert payload["metrics"]["approved_count"] == 1
    assert payload["records"][0]["row_id"] == "adapter-row-001"
    assert payload["records"][0]["ok"] is True


def test_build_report_rejects_private_source_path_and_review_failures(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.schema.json",
        {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "contract_version",
                "row_id",
                "source_repo",
                "source_artifact",
                "training_objective",
                "behavior_class",
                "user_message",
                "synthesizer_decision",
                "final_response",
                "tension_level",
                "provenance",
                "distillation_review",
                "evaluation_expectations",
            ],
            "properties": {
                "contract_version": {"type": "string"},
                "row_id": {"type": "string"},
                "source_repo": {"type": "string"},
                "source_artifact": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "kind", "public_safe"],
                    "properties": {
                        "path": {"type": "string"},
                        "kind": {"type": "string"},
                        "public_safe": {"type": "boolean"},
                    },
                },
                "training_objective": {"type": "string"},
                "behavior_class": {"type": "string"},
                "user_message": {"type": "string"},
                "synthesizer_decision": {"type": "string"},
                "final_response": {"type": "string"},
                "tension_level": {"type": "number"},
                "provenance": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["source_path", "transformation_chain", "review_scope"],
                    "properties": {
                        "source_path": {"type": "string"},
                        "transformation_chain": {"type": "array", "items": {"type": "string"}},
                        "review_scope": {"type": "string"},
                    },
                },
                "distillation_review": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "public_safe",
                        "privacy_cleared",
                        "governance_reviewed",
                        "approved_for_adapter_rl",
                    ],
                    "properties": {
                        "public_safe": {"type": "boolean"},
                        "privacy_cleared": {"type": "boolean"},
                        "governance_reviewed": {"type": "boolean"},
                        "approved_for_adapter_rl": {"type": "boolean"},
                    },
                },
                "evaluation_expectations": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "verifier_pass_rate_floor",
                        "auditability_required",
                        "regression_suite",
                        "reversible",
                    ],
                    "properties": {
                        "verifier_pass_rate_floor": {"type": "number"},
                        "auditability_required": {"type": "boolean"},
                        "regression_suite": {"type": "string"},
                        "reversible": {"type": "boolean"},
                    },
                },
            },
        },
    )
    _write_json(
        tmp_path / "bad.json",
        {
            "contract_version": "v1",
            "row_id": "bad-row",
            "source_repo": "tonesoul52",
            "source_artifact": {
                "path": "memory/self_journal.jsonl",
                "kind": "public_safe_trace_summary",
                "public_safe": False,
            },
            "training_objective": "governance_posture",
            "behavior_class": "governance_posture",
            "user_message": "answer carefully",
            "synthesizer_decision": "use verifier-first posture",
            "final_response": "I will answer conservatively.",
            "tension_level": 0.4,
            "provenance": {
                "source_path": "ToneSoul-Memory-Vault/private.json",
                "transformation_chain": ["raw_private_dump"],
                "review_scope": "human_reviewed",
            },
            "distillation_review": {
                "public_safe": False,
                "privacy_cleared": False,
                "governance_reviewed": True,
                "approved_for_adapter_rl": False,
            },
            "evaluation_expectations": {
                "verifier_pass_rate_floor": 0.5,
                "auditability_required": False,
                "regression_suite": "public_governance_eval_v1",
                "reversible": False,
            },
        },
    )

    payload = runner.build_report(
        repo_root=tmp_path,
        input_path=tmp_path / "bad.json",
        schema_path=tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.schema.json",
    )

    assert payload["ok"] is False
    assert payload["metrics"]["rejected_count"] == 1
    issues = payload["records"][0]["issues"]
    assert any("blocked source prefix" in issue for issue in issues)
    assert any("must be true" in issue for issue in issues)
    assert any("verifier_pass_rate_floor" in issue for issue in issues)


def test_main_writes_adapter_gate_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_emit", lambda payload: None)
    schema_path = tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.schema.json"
    example_path = tmp_path / "spec" / "governance" / "adapter_dataset_record_v1.example.json"
    out_dir = tmp_path / "status"
    _write_json(
        schema_path,
        {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "contract_version",
                "row_id",
                "source_repo",
                "source_artifact",
                "training_objective",
                "behavior_class",
                "user_message",
                "synthesizer_decision",
                "final_response",
                "tension_level",
                "provenance",
                "distillation_review",
                "evaluation_expectations",
            ],
            "properties": {
                "contract_version": {"type": "string"},
                "row_id": {"type": "string"},
                "source_repo": {"type": "string"},
                "source_artifact": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "kind", "public_safe"],
                    "properties": {
                        "path": {"type": "string"},
                        "kind": {"type": "string"},
                        "public_safe": {"type": "boolean"},
                    },
                },
                "training_objective": {"type": "string"},
                "behavior_class": {"type": "string"},
                "user_message": {"type": "string"},
                "synthesizer_decision": {"type": "string"},
                "final_response": {"type": "string"},
                "tension_level": {"type": "number"},
                "provenance": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["source_path", "transformation_chain", "review_scope"],
                    "properties": {
                        "source_path": {"type": "string"},
                        "transformation_chain": {"type": "array", "items": {"type": "string"}},
                        "review_scope": {"type": "string"},
                    },
                },
                "distillation_review": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "public_safe",
                        "privacy_cleared",
                        "governance_reviewed",
                        "approved_for_adapter_rl",
                    ],
                    "properties": {
                        "public_safe": {"type": "boolean"},
                        "privacy_cleared": {"type": "boolean"},
                        "governance_reviewed": {"type": "boolean"},
                        "approved_for_adapter_rl": {"type": "boolean"},
                    },
                },
                "evaluation_expectations": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "verifier_pass_rate_floor",
                        "auditability_required",
                        "regression_suite",
                        "reversible",
                    ],
                    "properties": {
                        "verifier_pass_rate_floor": {"type": "number"},
                        "auditability_required": {"type": "boolean"},
                        "regression_suite": {"type": "string"},
                        "reversible": {"type": "boolean"},
                    },
                },
            },
        },
    )
    _write_json(
        example_path,
        {
            "contract_version": "v1",
            "row_id": "adapter-row-001",
            "source_repo": "tonesoul52",
            "source_artifact": {
                "path": "docs/status/l8_distillation_boundary_latest.json",
                "kind": "public_safe_trace_summary",
                "public_safe": True,
            },
            "training_objective": "governance_posture",
            "behavior_class": "governance_posture",
            "user_message": "answer carefully",
            "synthesizer_decision": "use verifier-first posture",
            "final_response": "I will answer conservatively.",
            "tension_level": 0.4,
            "provenance": {
                "source_path": "docs/status/l8_distillation_boundary_latest.json",
                "transformation_chain": ["reviewed_public_trace"],
                "review_scope": "human_plus_verifier",
            },
            "distillation_review": {
                "public_safe": True,
                "privacy_cleared": True,
                "governance_reviewed": True,
                "approved_for_adapter_rl": True,
            },
            "evaluation_expectations": {
                "verifier_pass_rate_floor": 0.95,
                "auditability_required": True,
                "regression_suite": "public_governance_eval_v1",
                "reversible": True,
            },
        },
    )

    exit_code = runner.main(
        [
            "--repo-root",
            str(tmp_path),
            "--input",
            str(example_path),
            "--schema-path",
            str(schema_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ]
    )

    assert exit_code == 0
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert payload["ok"] is True
    assert payload["records"][0]["row_id"] == "adapter-row-001"
    assert "# L8 Adapter Dataset Gate Latest" in markdown
