import json
import sys
from pathlib import Path

from tonesoul.tech_trace import capture as capture_mod


def test_normalize_tags_and_load_text(tmp_path):
    text_path = tmp_path / "note.txt"
    text_path.write_text("  file text  ", encoding="utf-8")

    assert capture_mod.normalize_tags([" alpha ", "", None, "beta "]) == ["alpha", "beta"]
    assert capture_mod.load_text(str(text_path), " inline text ") == "inline text"
    assert capture_mod.load_text(str(text_path), None) == "file text"
    assert capture_mod.load_text(None, None) == ""


def test_capture_record_prunes_none_and_hashes_source(monkeypatch):
    monkeypatch.setattr(capture_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(capture_mod, "stable_hash", lambda value: f"h{len(str(value))}")

    payload = capture_mod.capture_record(
        raw_text="source text",
        source_type="paper",
        uri=None,
        title="Example",
        grade="A",
        retrieved_at=None,
        verified_by="pytest",
        notes=None,
        tags=[" alpha ", "", "beta"],
    )

    assert payload == {
        "capture_id": "capture_h29",
        "captured_at": "2026-03-20T00:00:00Z",
        "source": {
            "type": "paper",
            "hash": "h11",
            "title": "Example",
            "grade": "A",
            "verified_by": "pytest",
        },
        "raw_text": "source text",
        "tags": ["alpha", "beta"],
    }


def test_main_writes_capture_payload(tmp_path, monkeypatch):
    output_path = tmp_path / "capture.json"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "capture",
            "--text",
            "captured body",
            "--source-type",
            "blog",
            "--uri",
            "https://example.com/post",
            "--title",
            "Example Post",
            "--grade",
            "B",
            "--tag",
            "alpha",
            "--output",
            str(output_path),
        ],
    )

    result = capture_mod.main()
    saved = json.loads(output_path.read_text(encoding="utf-8"))

    assert Path(result["capture"]) == output_path.resolve()
    assert saved["source"]["type"] == "blog"
    assert saved["source"]["uri"] == "https://example.com/post"
    assert saved["source"]["title"] == "Example Post"
    assert saved["source"]["grade"] == "B"
    assert saved["raw_text"] == "captured body"
    assert saved["tags"] == ["alpha"]
