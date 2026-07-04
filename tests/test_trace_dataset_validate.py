"""Validator must catch what it claims to catch — seeded-fault tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.trace_dataset.validate import validate  # noqa: E402

GOOD = {
    "id": "ce-0001",
    "trace_type": "counter_evidence",
    "actors": {"claimant": "agent"},
    "register": "zh-TW",
    "claim_or_action": "測試宣稱",
    "outcome": "refuted",
    "evidence_grade": "E1",
    "label_provenance": "incident",
    "source_ref": "tools/accountability_panel/events.json#0",
}


def _write(tmp_path: Path, records) -> Path:
    p = tmp_path / "traces.jsonl"
    p.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records),
        encoding="utf-8",
        newline="\n",
    )
    return p


def test_clean_record_passes(tmp_path: Path) -> None:
    assert validate(_write(tmp_path, [GOOD]), sample=1) == []


def test_leak_and_duplicate_are_caught(tmp_path: Path) -> None:
    leaky = dict(GOOD, id="ce-0002", claim_or_action="token: hf_ABCDEFGHIJKLMNOPQRSTUV123456")
    dup = dict(GOOD)
    findings = validate(_write(tmp_path, [GOOD, leaky, dup]), sample=1)
    assert any("hf token shape" in f for f in findings)
    assert any("duplicate id" in f for f in findings)


def test_private_plane_reference_is_caught(tmp_path: Path) -> None:
    bad = dict(GOOD, id="ce-0003", claim_or_action="讀了 memory_base/ 的內容")
    findings = validate(_write(tmp_path, [bad]), sample=1)
    assert any("private-plane" in f for f in findings)
