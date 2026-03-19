import json
import sys

import pytest

from tonesoul.tech_trace import validate as validate_mod


def test_load_json_rejects_non_object_payload(tmp_path):
    payload_path = tmp_path / "normalize.json"
    payload_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="Normalize payload must be a JSON object"):
        validate_mod._load_json(str(payload_path))


def test_validate_claims_collects_ids_and_shape_errors():
    issues = []
    claim_ids = validate_mod._validate_claims(
        {
            "claims": [
                {"id": "claim-1", "text": "valid"},
                {"id": "claim-2", "statement": ""},
                "not-a-dict",
            ]
        },
        issues,
    )

    assert claim_ids == {"claim-1", "claim-2"}
    assert issues == ["claims[1].text_missing", "claims[2]_not_object"]
    assert validate_mod._validate_claims({"claims": "bad"}, []) == set()


def test_validate_links_and_attributions_cover_strict_branches():
    issues = []
    validate_mod._validate_links({"links": [{"uri": ""}, "not-a-dict"]}, issues)
    validate_mod._validate_attributions(
        {
            "attributions": [
                {"claim_id": None},
                {"source_ref": "source-a", "claim_id": "unknown"},
                {"source_ref": "source-b", "claim_id": ""},
                "not-a-dict",
            ]
        },
        {"claim-1"},
        issues,
        strict=True,
    )

    assert issues == [
        "links[0].uri_missing",
        "links[1]_not_object",
        "attributions[0].source_ref_missing",
        "attributions[0].claim_id_missing",
        "attributions[1].claim_id_unknown",
        "attributions[2].claim_id_invalid",
        "attributions[3]_not_object",
    ]


def test_validate_normalize_payload_integrates_claims_links_and_attributions():
    issues = validate_mod.validate_normalize_payload(
        {
            "claims": [{"id": "claim-1", "text": "ok"}],
            "links": [{"url": "https://example.com"}, {"uri": ""}],
            "attributions": [
                {"reference": "source-a", "claim_id": "claim-1"},
                {"reference": "source-b", "claim_id": "missing"},
            ],
        },
        strict=True,
    )

    assert issues == ["links[1].uri_missing", "attributions[1].claim_id_unknown"]


def test_main_writes_output_and_returns_status(tmp_path, monkeypatch, capsys):
    payload_path = tmp_path / "normalize.json"
    output_path = tmp_path / "validate.json"
    payload_path.write_text(
        json.dumps(
            {
                "claims": [{"id": "claim-1", "text": "valid"}],
                "links": [{"uri": "https://example.com"}],
                "attributions": [{"reference": "source-a", "claim_id": "claim-1"}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate",
            "--normalize",
            str(payload_path),
            "--strict",
            "--output",
            str(output_path),
        ],
    )

    exit_code = validate_mod.main()
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert saved["passed"] is True
    assert saved["issue_count"] == 0
    assert saved["normalize_path"] == str(payload_path)
    assert "Tech-Trace normalize validation PASS" in stdout


def test_main_returns_failure_when_validation_finds_issues(tmp_path, monkeypatch, capsys):
    payload_path = tmp_path / "normalize.json"
    payload_path.write_text(json.dumps({"claims": "bad"}), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate",
            "--normalize",
            str(payload_path),
        ],
    )

    exit_code = validate_mod.main()
    stdout = capsys.readouterr().out

    assert exit_code == 1
    assert "claims_not_list" in stdout
    assert str(payload_path) in stdout
