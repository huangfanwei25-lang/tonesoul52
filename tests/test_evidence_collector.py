from __future__ import annotations

import argparse
import json
from pathlib import Path

from tonesoul import evidence_collector as module


def _write_json(path: Path, payload: object, *, encoding: str = "utf-8") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=encoding)
    return path


def test_load_json_supports_bom_and_invalid_json_returns_none(tmp_path: Path) -> None:
    valid_path = _write_json(tmp_path / "valid.json", {"ok": True}, encoding="utf-8-sig")
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json}", encoding="utf-8")

    assert module._load_json(str(valid_path)) == {"ok": True}
    assert module._load_json(str(invalid_path)) is None


def test_claim_preview_counts_text_and_limits_preview() -> None:
    claims = [
        {"text": "first claim"},
        {"claim": "second claim"},
        {"statement": "third claim"},
        "",
    ]

    count, preview = module._claim_preview(claims)

    assert count == 3
    assert preview == ["first claim", "second claim"]


def test_tech_trace_digest_summarizes_trace_payload(tmp_path: Path) -> None:
    trace_path = _write_json(
        tmp_path / "normalize.json",
        {
            "summary": "trace summary",
            "claims": [{"text": "claim one"}, {"claim": "claim two"}],
            "links": [{"uri": "https://a"}, {"uri": ""}],
            "attributions": [{"source_ref": "doc-1"}, {"source_ref": None}],
        },
    )

    assert module._tech_trace_digest(str(trace_path)) == [
        "- tech_trace_summary: trace summary",
        "- tech_trace_claims: 2 | claim one | claim two",
        "- tech_trace_links: 1",
        "- tech_trace_attributions: 1",
    ]


def test_intent_verification_digest_formats_status_confidence_and_reason(tmp_path: Path) -> None:
    intent_path = _write_json(
        tmp_path / "intent.json",
        {"audit": {"status": "verified", "confidence": 0.875, "reason": "aligned with evidence"}},
    )

    assert module._intent_verification_digest(str(intent_path)) == [
        "- intent_status: verified",
        "- intent_confidence: 0.88",
        "- intent_reason: aligned with evidence",
    ]


def test_build_evidence_summary_includes_artifacts_and_digests(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(module, "utc_now", lambda: "2026-03-19T12:00:00Z")
    tech_trace_path = _write_json(
        tmp_path / "normalize.json",
        {"summary": "trace summary", "claims": ["claim one"], "links": [{"uri": "u"}]},
    )
    intent_path = _write_json(
        tmp_path / "intent.json",
        {"audit": {"status": "verified", "confidence": 0.9, "reason": "clear"}},
    )

    summary = module.build_evidence_summary(
        str(tmp_path / "context.yaml"),
        str(tmp_path / "execution_report.md"),
        artifacts={
            "action_set": str(tmp_path / "action_set.json"),
            "tech_trace_normalize": str(tech_trace_path),
            "intent_verification": str(intent_path),
        },
    )

    assert "- Run: " + str(tmp_path / "context.yaml") in summary
    assert "- Execution report: " + str(tmp_path / "execution_report.md") in summary
    assert "- action_set: " + str(tmp_path / "action_set.json") in summary
    assert "- tech_trace_claims: 1 | claim one" in summary
    assert "- intent_status: verified" in summary
    assert summary.endswith("- Collected at: 2026-03-19T12:00:00Z")


def test_entry_offsets_finds_each_run_section() -> None:
    lines = [
        "# Evidence Summary\n",
        "\n",
        "- Run: first\n",
        "- detail: a\n",
        "- Run: second\n",
    ]

    assert module._entry_offsets(lines) == [2, 4]


def test_rollover_summary_archives_older_entries(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(module, "utc_now", lambda: "2026-03-19T12:34:56Z")
    summary_path = tmp_path / "summary.md"
    summary_path.write_text(
        "# Evidence Summary\n\n"
        "- Run: first\n- detail: one\n"
        "- Run: second\n- detail: two\n"
        "- Run: third\n- detail: three\n",
        encoding="utf-8",
    )

    archive_path = module._rollover_summary(
        str(summary_path),
        max_entries=2,
        keep_latest=1,
        archive_dir=str(tmp_path / "archive"),
    )

    assert archive_path == str(tmp_path / "archive" / "evidence_summary_20260319T123456Z.md")
    assert Path(archive_path).exists()
    rewritten = summary_path.read_text(encoding="utf-8")
    assert "- Run: first" not in rewritten
    assert "- Run: second" not in rewritten
    assert "- Run: third" in rewritten
    archived = Path(archive_path).read_text(encoding="utf-8")
    assert "- Run: first" in archived
    assert "- Run: second" in archived


def test_append_to_summary_creates_file_and_applies_retention(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(module, "utc_now", lambda: "2026-03-19T12:34:56Z")
    summary_path = tmp_path / "summary.md"

    module.append_to_summary(
        str(summary_path),
        "- Run: first\n- detail: one",
        retention={"max_entries": 1, "keep_latest": 1, "archive_dir": str(tmp_path / "archive")},
    )
    module.append_to_summary(
        str(summary_path),
        "- Run: second\n- detail: two",
        retention={"max_entries": 1, "keep_latest": 1, "archive_dir": str(tmp_path / "archive")},
    )

    text = summary_path.read_text(encoding="utf-8")
    assert text.startswith("# Evidence Summary")
    assert "- Run: first" not in text
    assert "- Run: second" in text
    archives = list((tmp_path / "archive").glob("evidence_summary_*.md"))
    assert len(archives) == 1


def test_main_writes_evidence_summary_output(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "out" / "summary.md"
    args = argparse.Namespace(
        context=str(tmp_path / "context.yaml"),
        execution_report=str(tmp_path / "execution_report.md"),
        error_ledger=None,
        ystm_nodes=None,
        ystm_audit=None,
        ystm_diff=None,
        ystm_terrain=None,
        ystm_terrain_json=None,
        ystm_terrain_svg=None,
        ystm_terrain_png=None,
        ystm_terrain_p2=None,
        ystm_terrain_p2_json=None,
        ystm_terrain_p2_svg=None,
        ystm_terrain_p2_png=None,
        tech_trace_capture=None,
        tech_trace_normalize=None,
        intent_verification=None,
        skills_applied=None,
        reflection=None,
        action_set=None,
        mercy_objective=None,
        council_summary=None,
        tsr_metrics=None,
        dcs_result=None,
        max_entries=None,
        keep_latest=None,
        archive_dir=None,
        output=str(output_path),
    )

    class _Parser:
        def parse_args(self) -> argparse.Namespace:
            return args

    monkeypatch.setattr(module, "build_arg_parser", lambda: _Parser())
    monkeypatch.setattr(module, "utc_now", lambda: "2026-03-19T12:00:00Z")

    result = module.main()

    assert result == {"evidence_summary": str(output_path.resolve())}
    text = output_path.read_text(encoding="utf-8")
    assert "- Run: " + str(tmp_path / "context.yaml") in text
    assert "- Execution report: " + str(tmp_path / "execution_report.md") in text
