from __future__ import annotations

import json
from pathlib import Path

import scripts.run_l7_l8_contract_artifacts as runner


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_l7_payload_contains_authority_routes_and_verifiers() -> None:
    payload = runner.build_l7_payload()

    assert payload["contract_version"] == "v1"
    assert payload["default_reading_order"][0] == "architecture_anchor"
    assert any(surface["id"] == "verifier" for surface in payload["surfaces"])
    assert any(
        route["question_type"] == "latest_repo_state" for route in payload["question_routes"]
    )
    assert any(check["id"] == "docs_consistency" for check in payload["verifier_checks"])


def test_build_l8_payload_loads_schema_and_forbidden_surfaces(tmp_path: Path) -> None:
    _write_json(
        tmp_path / runner.DATASET_SCHEMA_PATH,
        {
            "required": ["row_id", "behavior_class", "provenance"],
            "properties": {
                "row_id": {"type": "string"},
                "behavior_class": {"type": "string"},
                "provenance": {"type": "object"},
                "evaluation_expectations": {"type": "object"},
            },
        },
    )
    _write_json(
        tmp_path / runner.DATASET_EXAMPLE_PATH,
        {
            "row_id": "adapter-row-001",
            "behavior_class": "public_safe_behavior_trace",
            "training_objective": "governance_posture",
        },
    )

    payload = runner.build_l8_payload(tmp_path)

    assert payload["dataset_required_fields"] == ["row_id", "behavior_class", "provenance"]
    assert payload["dataset_property_count"] == 4
    assert "private vault memory" in payload["forbidden_surfaces"]
    assert payload["example_record_preview"]["row_id"] == "adapter-row-001"


def test_main_writes_all_artifacts(monkeypatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "status"
    _write_json(
        tmp_path / runner.DATASET_SCHEMA_PATH,
        {
            "required": ["row_id", "behavior_class", "provenance"],
            "properties": {
                "row_id": {"type": "string"},
                "behavior_class": {"type": "string"},
                "provenance": {"type": "object"},
            },
        },
    )
    _write_json(
        tmp_path / runner.DATASET_EXAMPLE_PATH,
        {
            "row_id": "adapter-row-001",
            "behavior_class": "public_safe_behavior_trace",
            "training_objective": "governance_posture",
        },
    )

    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        runner,
        "build_parser",
        lambda: type(
            "Parser",
            (),
            {
                "parse_args": staticmethod(
                    lambda _argv=None: type(
                        "Args",
                        (),
                        {
                            "output_dir": str(out_dir.relative_to(tmp_path)),
                        },
                    )()
                )
            },
        )(),
    )

    exit_code = runner.main([])
    l7_payload = json.loads((out_dir / runner.L7_JSON_FILENAME).read_text(encoding="utf-8"))
    l8_payload = json.loads((out_dir / runner.L8_JSON_FILENAME).read_text(encoding="utf-8"))
    l7_markdown = (out_dir / runner.L7_MARKDOWN_FILENAME).read_text(encoding="utf-8")
    l8_markdown = (out_dir / runner.L8_MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert exit_code == 0
    assert l7_payload["contract_version"] == "v1"
    assert l8_payload["dataset_schema_ref"] == runner.DATASET_SCHEMA_PATH
    assert "# L7 Retrieval Contract Latest" in l7_markdown
    assert "# L8 Distillation Boundary Latest" in l8_markdown
