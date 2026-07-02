"""Tests for scripts/verify_status_freshness.py (deterministic core: fixed `now`, tmp dirs).

Provenance: the verifier exists because a 2026-03 abc_firewall artifact (ok=true) masked a
live 2026-07 regression. These tests pin the classification rules so the freshness contract
itself cannot silently drift.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.verify_status_freshness import (  # noqa: E402
    _classify,
    _parse_timestamp,
    build_payload,
    evaluate,
)

NOW = datetime(2026, 7, 2, 12, 0, 0, tzinfo=timezone.utc)


def _write(status_dir: Path, name: str, payload: dict) -> None:
    (status_dir / name).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8", newline="\n"
    )


def _days_ago(days: int) -> str:
    return (NOW - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(tmp_path: Path, assertive_max: int = 45, episodic_max: int = 120):
    status_dir = tmp_path / "docs" / "status"
    return evaluate(NOW, assertive_max, episodic_max, status_dir=status_dir, repo_root=tmp_path)


def _status_dir(tmp_path: Path) -> Path:
    d = tmp_path / "docs" / "status"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_fresh_assertive_passes(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "a_latest.json", {"ok": True, "generated_at": _days_ago(1)})
    verdicts = _run(tmp_path)
    assert [v.verdict for v in verdicts] == ["fresh"]
    assert verdicts[0].kind == "assertive"


def test_stale_assertive_is_failure(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "a_latest.json", {"ok": True, "generated_at": _days_ago(100)})
    verdicts = _run(tmp_path)
    assert verdicts[0].verdict == "stale"
    payload = build_payload(verdicts, NOW, 45, 120)
    assert payload["overall_ok"] is False
    assert payload["summary"]["failure_count"] == 1


def test_untimestamped_assertive_is_failure(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "a_latest.json", {"overall_ok": True})
    payload = build_payload(_run(tmp_path), NOW, 45, 120)
    assert payload["overall_ok"] is False
    assert payload["failures"][0]["verdict"] == "untimestamped"


def test_null_timestamp_noted_distinctly(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "a_latest.json", {"ok": True, "generated_at": None})
    verdicts = _run(tmp_path)
    assert verdicts[0].verdict == "untimestamped"
    assert "null" in verdicts[0].note


def test_stale_episodic_warns_but_does_not_fail(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "e_latest.json", {"snapshot": 1, "generated_at": _days_ago(200)})
    payload = build_payload(_run(tmp_path), NOW, 45, 120)
    assert payload["summary"]["stale_episodic"] == 1
    assert payload["overall_ok"] is True  # episodic staleness is a warning, not a failure
    assert payload["warnings"][0]["verdict"] == "stale"


def test_md_only_artifact_judged_via_inline_timestamp(tmp_path: Path) -> None:
    status = _status_dir(tmp_path)
    (status / "m_latest.md").write_text(
        f"# X\n\n- generated_at: {_days_ago(3)}\n", encoding="utf-8", newline="\n"
    )
    verdicts = _run(tmp_path)
    assert [(v.verdict, v.timestamp_field) for v in verdicts] == [("fresh", "md_inline")]


def test_md_twin_not_double_judged(tmp_path: Path) -> None:
    status = _status_dir(tmp_path)
    _write(status, "t_latest.json", {"ok": True, "generated_at": _days_ago(1)})
    (status / "t_latest.md").write_text("# twin, no timestamp\n", encoding="utf-8", newline="\n")
    assert len(_run(tmp_path)) == 1  # md twin skipped; JSON is authoritative


def test_self_outputs_excluded(tmp_path: Path) -> None:
    status = _status_dir(tmp_path)
    _write(status, "status_freshness_latest.json", {"overall_ok": False, "generated_at": None})
    assert _run(tmp_path) == []


def test_date_only_timestamp_accepted(tmp_path: Path) -> None:
    _write(_status_dir(tmp_path), "d_latest.json", {"ok": True, "generated_at": "2026-07-01"})
    assert _run(tmp_path)[0].verdict == "fresh"


def test_unreadable_json_treated_as_undated_assertive(tmp_path: Path) -> None:
    (_status_dir(tmp_path) / "b_latest.json").write_text("{not json", encoding="utf-8")
    payload = build_payload(_run(tmp_path), NOW, 45, 120)
    assert payload["overall_ok"] is False
    assert "unreadable" in payload["failures"][0]["note"]


def test_future_dated_assertive_is_failure(tmp_path: Path) -> None:
    # a typo'd year must not make an ok=true artifact immune to the check
    _write(
        _status_dir(tmp_path), "a_latest.json", {"ok": True, "generated_at": "2027-01-01T00:00:00Z"}
    )
    verdicts = _run(tmp_path)
    assert verdicts[0].verdict == "future-dated"
    payload = build_payload(verdicts, NOW, 45, 120)
    assert payload["overall_ok"] is False
    assert payload["summary"]["future_dated_assertive"] == 1


def test_future_dated_episodic_warns(tmp_path: Path) -> None:
    _write(
        _status_dir(tmp_path), "e_latest.json", {"note": 1, "generated_at": "2027-01-01T00:00:00Z"}
    )
    payload = build_payload(_run(tmp_path), NOW, 45, 120)
    assert payload["overall_ok"] is True
    assert payload["warnings"][0]["verdict"] == "future-dated"


def test_non_utf8_artifact_does_not_abort_sweep(tmp_path: Path) -> None:
    status = _status_dir(tmp_path)
    (status / "bad_latest.json").write_bytes(
        '{"ok": true, "generated_at": "2026-07-01"}'.encode("utf-16")
    )
    _write(status, "good_latest.json", {"ok": True, "generated_at": _days_ago(1)})
    verdicts = _run(tmp_path)  # must not raise
    by_path = {v.path.split("/")[-1]: v for v in verdicts}
    assert by_path["good_latest.json"].verdict == "fresh"  # healthy artifact still judged
    assert by_path["bad_latest.json"].verdict == "untimestamped"
    assert "unreadable" in by_path["bad_latest.json"].note


def test_md_timestamp_line_anchored_and_offset_preserving(tmp_path: Path) -> None:
    status = _status_dir(tmp_path)
    # a mid-prose quote of another artifact's timestamp must not date this one
    (status / "q_latest.md").write_text(
        "# X\n\nThe old artifact said generated_at: 2020-01-01 was fine.\n\n"
        f"- generated_at: {_days_ago(2)}\n",
        encoding="utf-8",
        newline="\n",
    )
    # bold header variant + non-UTC offset must parse (offset kept, not read as UTC)
    (status / "b_latest.md").write_text(
        "# Y\n\n**Generated:** 2026-07-01T08:00:00+08:00\n", encoding="utf-8", newline="\n"
    )
    verdicts = {v.path.split("/")[-1]: v for v in _run(tmp_path)}
    assert verdicts["q_latest.md"].verdict == "fresh"  # dated by its own line, not the quote
    assert verdicts["b_latest.md"].timestamp is not None
    assert "+08:00" in verdicts["b_latest.md"].timestamp


def test_classify_and_parse_helpers() -> None:
    assert _classify({"passed": True}) == "assertive"
    assert _classify({"summary": {}}) == "episodic"
    assert _classify(["list"]) == "episodic"
    parsed = _parse_timestamp("2026-07-02T01:35:22Z")
    assert parsed is not None and parsed.tzinfo is not None
    assert _parse_timestamp("not-a-date") is None
    assert _parse_timestamp(12345) is None
