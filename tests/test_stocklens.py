"""Tests for StockLens — the forced bull/bear honesty frame (apps/stocklens/core.py)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "stocklens_core", Path(__file__).resolve().parents[1] / "apps" / "stocklens" / "core.py"
)
stocklens = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
# Register before exec: @dataclass + `from __future__ import annotations` resolves types via
# sys.modules[cls.__module__], which is None for an unregistered importlib-loaded module.
sys.modules[_SPEC.name] = stocklens
_SPEC.loader.exec_module(stocklens)

review = stocklens.review
Point = stocklens.Point


def _both_sides_all_dims():
    pts = []
    for dim in stocklens.DIMENSIONS:
        pts.append(Point(dim, "bull", f"{dim} 多方論點", "E2"))
        pts.append(Point(dim, "bear", f"{dim} 空方論點", "E2"))
    return pts


def test_never_gives_a_verdict():
    r = review("2330", _both_sides_all_dims())
    assert r["verdict"] is None
    assert "不給買賣判定" in r["no_verdict_note"]


def test_full_coverage_has_no_gaps():
    r = review("2330", _both_sides_all_dims())
    assert r["dissent_coverage_gaps"] == []


def test_one_sided_dimension_is_flagged():
    pts = [Point("籌碼面", "bull", "外資買超", "E2")]  # only bull, only one dimension
    r = review("2330", pts)
    gaps = " ".join(r["dissent_coverage_gaps"])
    assert "籌碼面" in gaps and "空方" in gaps  # missing bear flagged
    assert "基本面" in gaps  # untouched dimension flagged ("你完全沒給")


def test_overclaim_is_flagged():
    pts = [Point("消息面", "bull", "AI 題材保證續強,接下來必漲", "E0")]
    r = review("2330", pts)
    matched = {f["matched"] for f in r["overclaim_flags"]}
    assert r["overclaim_flags"], "should flag 保證/必漲"
    assert any("保證" in m or "必漲" in m for m in matched)


def test_clean_claim_is_not_overclaimed():
    pts = [Point("基本面", "bull", "毛利率長期維持在 50% 以上", "E2")]
    r = review("2330", pts)
    assert r["overclaim_flags"] == []


def test_language_outruns_evidence():
    pts = [Point("消息面", "bull", "接下來必漲", "E0")]
    r = review("2330", pts)
    assert any(m["evidence_level"] == "E0" for m in r["evidence_mismatches"])


def test_strong_language_with_high_evidence_not_flagged_as_mismatch():
    # E3/E4 evidence + strong wording is not an evidence-mismatch (it's earned)
    pts = [Point("基本面", "bull", "一定程度反映在估值", "E3")]
    r = review("2330", pts)
    assert r["evidence_mismatches"] == []


def test_cannot_verify_always_present():
    r = review("2330", [])
    assert any("未來價格" in c for c in r["cannot_verify"])


def test_input_problems_flag_bad_fields():
    pts = [Point("玄學面", "long", "claim", "E9")]
    r = review("2330", pts)
    probs = " ".join(r["input_problems"])
    assert "未知面向" in probs and "side" in probs and "證據等級" in probs


def test_deterministic():
    pts = _both_sides_all_dims() + [Point("消息面", "bull", "保證必漲", "E0")]
    assert review("2330", pts) == review("2330", pts)
