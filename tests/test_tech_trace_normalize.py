import json
import sys
from pathlib import Path

import pytest

from tonesoul.tech_trace import normalize as normalize_mod


def test_prune_none_summary_and_extract_claims_helpers():
    assert normalize_mod._prune_none(
        {"keep": 1, "drop": None, "nested": {"ok": 2, "skip": None}, "items": [1, None, {"x": 3}]}
    ) == {"keep": 1, "nested": {"ok": 2}, "items": [1, {"x": 3}]}
    assert normalize_mod._summary_from_text("", 10) == ""
    assert normalize_mod._summary_from_text("abcdef", 5) == "ab..."
    assert normalize_mod._extract_claims(
        "First sufficiently long sentence. Tiny. Second sentence is also long enough!",
        limit=2,
        min_chars=10,
    ) == [
        "First sufficiently long sentence.",
        "Second sentence is also long enough!",
    ]
    assert normalize_mod._extract_claims(
        "single fallback clause without punctuation",
        limit=2,
        min_chars=10,
    ) == ["single fallback clause without punctuation"]


def test_load_json_arg_supports_inline_and_file(tmp_path):
    claims_path = tmp_path / "claims.json"
    claims_path.write_text(json.dumps(["claim-a"]), encoding="utf-8")

    assert normalize_mod._load_json_arg('["claim-a"]', "--claims") == ["claim-a"]
    assert normalize_mod._load_json_arg(str(claims_path), "--claims") == ["claim-a"]

    with pytest.raises(ValueError, match="--claims must be JSON or a JSON file path"):
        normalize_mod._load_json_arg("{broken", "--claims")


def test_normalize_claims_links_and_attributions():
    claims = normalize_mod._normalize_claims(
        [
            "  first claim  ",
            {"claim": "second claim"},
            {"text": "third claim", "id": "custom-3"},
            "",
        ]
    )
    links = normalize_mod._normalize_links([" https://example.com ", {"url": "https://b.example"}])
    attributions = normalize_mod._normalize_attributions(
        ["source-a", {"uri": "https://src.example"}]
    )

    assert [item["text"] for item in claims] == ["first claim", "second claim", "third claim"]
    assert claims[2]["id"] == "custom-3"
    assert claims[0]["id"].startswith("claim_")
    assert links == [{"uri": "https://example.com"}, {"url": "https://b.example"}]
    assert attributions == [{"reference": "source-a"}, {"uri": "https://src.example"}]

    with pytest.raises(ValueError, match="claims must be a JSON list"):
        normalize_mod._normalize_claims("not-a-list")
    with pytest.raises(ValueError, match="links must be a JSON list"):
        normalize_mod._normalize_links("not-a-list")
    with pytest.raises(ValueError, match="attributions must be a JSON list"):
        normalize_mod._normalize_attributions("not-a-list")


def test_normalize_record_auto_claims_and_prunes(monkeypatch):
    monkeypatch.setattr(normalize_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(normalize_mod, "stable_hash", lambda value: f"h{len(str(value))}")

    payload = normalize_mod.normalize_record(
        raw_text="First sentence is long enough. Second sentence is also long enough.  ",
        capture_id="capture-1",
        source={"type": "note", "uri": None},
        source_grade="A",
        summary=None,
        notes=None,
        tags=[" alpha ", "", "beta"],
        max_length=40,
        claims=None,
        links=["https://example.com"],
        attributions=["source-ref"],
        auto_claims=True,
        auto_claim_limit=1,
        auto_claim_min_chars=10,
    )

    assert payload["normalize_id"] == "normalize_h23"
    assert payload["normalized_at"] == "2026-03-20T00:00:00Z"
    assert payload["capture_id"] == "capture-1"
    assert payload["source"] == {"type": "note"}
    assert payload["source_grade"] == "A"
    assert payload["normalized_text"] == "First sentence is long enough. Second se"
    assert payload["summary"] == "First sentence is long enough. Second se"
    assert payload["claims"] == [{"id": "claim_h32", "text": "First sentence is long enough."}]
    assert payload["links"] == [{"uri": "https://example.com"}]
    assert payload["attributions"] == [{"reference": "source-ref"}]
    assert payload["raw_hash"] == "h69"
    assert payload["normalized_hash"] == "h40"
    assert payload["tags"] == ["alpha", "beta"]
    assert "notes" not in payload


def test_load_capture_rejects_non_object_payload(tmp_path):
    payload_path = tmp_path / "capture.json"
    payload_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="Capture payload must be a JSON object"):
        normalize_mod._load_capture(str(payload_path))


def test_main_writes_normalized_payload_from_capture(tmp_path, monkeypatch):
    capture_path = tmp_path / "capture.json"
    output_path = tmp_path / "normalized.json"
    capture_path.write_text(
        json.dumps(
            {
                "capture_id": "capture-77",
                "raw_text": "A long enough sentence for normalization. Another long sentence follows.",
                "source": {"type": "paper", "uri": "https://example.com/source"},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "normalize",
            "--input",
            str(capture_path),
            "--output",
            str(output_path),
            "--summary",
            "Manual summary",
            "--tag",
            "alpha",
        ],
    )

    result = normalize_mod.main()
    saved = json.loads(output_path.read_text(encoding="utf-8"))

    assert Path(result["normalized"]) == output_path.resolve()
    assert saved["capture_id"] == "capture-77"
    assert saved["summary"] == "Manual summary"
    assert saved["source"]["type"] == "unknown"
    assert saved["source"]["uri"] == "https://example.com/source"
    assert saved["tags"] == ["alpha"]
