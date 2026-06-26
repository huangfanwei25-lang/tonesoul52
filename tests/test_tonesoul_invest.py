"""Tests for 語魂投資 v0 (apps/stocklens/tonesoul_invest.py)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "tonesoul_invest",
    Path(__file__).resolve().parents[1] / "apps" / "stocklens" / "tonesoul_invest.py",
)
ti = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
sys.modules[_SPEC.name] = ti
_SPEC.loader.exec_module(ti)


def _thesis():
    return [
        {"dimension": "基本面", "side": "bull", "claim": "AI 占比拉到 30%", "evidence_level": "E0"},
        {"dimension": "基本面", "side": "bull", "claim": "Q1 EPS 創高", "evidence_level": "E1"},
        {
            "dimension": "基本面",
            "side": "bear",
            "claim": "毛利含一次性庫存利益",
            "evidence_level": "E2",
        },
        {"dimension": "技術面", "side": "bull", "claim": "長線多頭", "evidence_level": "E1"},
        {"dimension": "技術面", "side": "bear", "claim": "跌破均線", "evidence_level": "E1"},
        {"dimension": "籌碼面", "side": "bull", "claim": "外資持股", "evidence_level": "E1"},
        {"dimension": "籌碼面", "side": "bear", "claim": "法人賣超", "evidence_level": "E1"},
        {"dimension": "消息面", "side": "bull", "claim": "缺貨漲價", "evidence_level": "E1"},
        {"dimension": "消息面", "side": "bear", "claim": "法人砍評", "evidence_level": "E1"},
    ]


def test_never_gives_a_verdict():
    r = ti.run("X", _thesis())
    assert r["verdict"] is None
    assert r["stocklens"]["verdict"] is None  # reuses StockLens, which is also verdict-free


def test_load_bearing_surfaces_weak_bull_support():
    r = ti.run("X", _thesis())
    weak = r["load_bearing"]["weakest_bull_support"]
    claims = [w["claim"] for w in weak]
    assert "AI 占比拉到 30%" in claims  # E0 bull
    assert "Q1 EPS 創高" in claims  # E1 bull
    assert weak[0]["evidence_level"] == "E0"  # E0 sorted first
    # bear claims and E2+ claims are NOT load-bearing-bull
    assert all(w["evidence_level"] in ("E0", "E1") for w in weak)


def test_external_eye_is_for_a_separate_reviewer():
    r = ti.run("X", _thesis())
    ee = r["external_eye"]
    assert "SEPARATE" in ee["hand_this_to"] or "separate" in ee["hand_this_to"]
    assert "auditor" in ee["why"].lower() and "auditee" in ee["why"].lower()
    # the packet must NOT ask for a verdict, and MUST carry the trap checklist
    assert "buy/sell verdict" in ee["refutation_prompt"]
    assert "REFUTE" in ee["refutation_prompt"]
    assert len(ee["trap_checklist"]) >= 6
    # the thesis is embedded so the external eye sees what it's refuting
    assert "Q1 EPS 創高" in ee["refutation_prompt"]


def test_it_does_not_run_the_external_eye_itself():
    # 語魂投資 prepares the packet; it must not contain a refutation result, only the prompt.
    r = ti.run("X", _thesis())
    assert "refutation_prompt" in r["external_eye"]
    assert "refutation_result" not in r["external_eye"]  # it does not grade itself


def test_deterministic():
    assert ti.run("X", _thesis()) == ti.run("X", _thesis())
