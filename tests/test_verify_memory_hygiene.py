import json
from pathlib import Path

import scripts.verify_memory_hygiene as hygiene


def test_check_utf8_no_bom_detects_bom(tmp_path: Path):
    clean = tmp_path / "clean.py"
    clean.write_text("print('ok')\n", encoding="utf-8")
    bom = tmp_path / "bom.py"
    bom.write_bytes(b"\xef\xbb\xbfprint('x')\n")

    report = hygiene._check_utf8_no_bom([clean, bom])

    assert report["files_scanned"] == 2
    assert bom.as_posix() in report["bom_files"]
    assert report["decode_errors"] == []


def test_discussion_tail_ignores_old_invalid_lines(tmp_path: Path):
    discussion = tmp_path / "discussion.jsonl"
    discussion.write_text(
        "\n".join(
            [
                "{not valid json",
                json.dumps(
                    {
                        "timestamp": "2026-02-08T00:00:00Z",
                        "author": "codex",
                        "topic": "a",
                        "status": "final",
                        "message": "ok",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "timestamp": "2026-02-08T00:00:10Z",
                        "author": "codex",
                        "topic": "b",
                        "status": "final",
                        "message": "ok",
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = hygiene._check_discussion_tail(discussion, tail_lines=2)
    assert report["exists"] is True
    assert report["tail_checked"] == 2
    assert report["invalid_json"] == []
    assert report["missing_fields"] == []


def test_discussion_tail_fails_for_recent_invalid_or_missing_fields(tmp_path: Path):
    discussion = tmp_path / "discussion.jsonl"
    bad_missing = {
        "timestamp": "2026-02-08T00:00:10Z",
        "author": "codex",
        "topic": "bad",
        "status": "final",
    }
    discussion.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-02-08T00:00:00Z",
                        "author": "codex",
                        "topic": "ok",
                        "status": "final",
                        "message": "ok",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(bad_missing, ensure_ascii=False),
                "{bad json line",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = hygiene._check_discussion_tail(discussion, tail_lines=3)
    assert len(report["invalid_json"]) == 1
    assert len(report["missing_fields"]) == 1
    assert report["missing_fields"][0]["missing_fields"] == ["message"]


def test_build_report_can_allow_missing_discussion(tmp_path: Path):
    target = tmp_path / "ok.py"
    target.write_text("print('ok')\n", encoding="utf-8")
    missing_discussion = tmp_path / "missing.jsonl"

    report = hygiene._build_report(
        targets=[target.as_posix()],
        discussion_path=missing_discussion,
        tail_lines=20,
        allow_missing_discussion=True,
    )

    assert report["ok"] is True
    assert report["discussion_tail"]["exists"] is False


def test_discussion_tail_detects_text_anomaly(tmp_path: Path):
    discussion = tmp_path / "discussion.jsonl"
    discussion.write_text(
        json.dumps(
            {
                "timestamp": "2026-02-09T00:00:00Z",
                "author": "codex",
                "topic": "encoding-check",
                "status": "final",
                "message": "bad\ue000payload",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    report = hygiene._check_discussion_tail(discussion, tail_lines=10)
    assert len(report["text_anomalies"]) == 1
    assert report["text_anomalies"][0]["line_number"] == 1
    assert "message" in report["text_anomalies"][0]["fields"]


def test_build_report_fails_on_text_anomaly(tmp_path: Path):
    target = tmp_path / "ok.py"
    target.write_text("print('ok')\n", encoding="utf-8")
    discussion = tmp_path / "discussion.jsonl"
    discussion.write_text(
        json.dumps(
            {
                "timestamp": "2026-02-09T00:00:00Z",
                "author": "codex",
                "topic": "encoding-check",
                "status": "final",
                "message": "bad\ue000payload",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    report = hygiene._build_report(
        targets=[target.as_posix()],
        discussion_path=discussion,
        tail_lines=20,
        allow_missing_discussion=False,
    )

    assert report["ok"] is False
    assert len(report["discussion_tail"]["text_anomalies"]) == 1
