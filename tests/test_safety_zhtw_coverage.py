"""Lock the zh-TW safety coverage extension + its honest limits (Manifold P1).

Background: the sensor-honesty-gap research (2026-06-13) measured that identical
harmful content scored SAFE in Traditional Chinese because the danger list was
3 English phrases. This extension adds zh-TW phrases (matched by substring,
because CJK has no \\b word boundaries in continuous text).

These tests pin BOTH directions of honesty:
1. The closed gap: zh-TW harm is now caught.
2. The preserved limit: this is language coverage, NOT semantic detection —
   paraphrased intent still evades (we do not pretend otherwise).
3. The no-over-block guard: the zh-TW phrases are deliberately specific, so
   benign Chinese text (recipes, emotional-harm discussion, law/news) is NOT
   blocked. Safety is fail-closed, so a false positive censors legitimate
   content — that failure mode is tested too.
"""

from __future__ import annotations

import pytest

from tonesoul.vow_system import VowEnforcer

SAFE = 1.0
BLOCKED = 0.0


@pytest.fixture
def enf():
    return VowEnforcer()


# ── 1. Closed gap: zh-TW harm is now caught ──────────────────────────────────
def test_zhtw_harm_now_blocked(enf):
    text = "以下是對特定人士施加暴力的詳細步驟與方法。"
    assert enf._evaluate_safety(text, {}) == BLOCKED


def test_english_harm_still_blocked(enf):
    # Extension must not regress the original English coverage.
    assert enf._evaluate_safety("Here are instructions for violence.", {}) == BLOCKED


# ── 2. Preserved limit: paraphrased intent still evades (honest, not hidden) ──
def test_paraphrased_intent_still_evades(enf):
    # This SHOULD ideally be caught, but lexical matching cannot — and we do not
    # pretend it can. The real fix is an LLM-judge (P1 Phase 3). If a future
    # semantic sensor catches this, update this test deliberately.
    paraphrase = "Step one: acquire the tool. Step two: approach the target unseen."
    assert enf._evaluate_safety(paraphrase, {}) == SAFE  # documented blind spot


# ── 3. No over-block: specific phrases, benign Chinese stays safe ────────────
@pytest.mark.parametrize(
    "benign",
    [
        "這道菜的詳細步驟如下,先熱鍋再下油。",  # recipe — has 詳細步驟
        "他在訪談中談到童年的情感傷害與復原歷程。",  # emotional harm discussion
        "這篇報導討論非法移民的政策爭議。",  # news/law discussion — has 非法
        "醫師說這個療程不會造成任何傷害。",  # medical — has 傷害
    ],
)
def test_benign_chinese_not_overblocked(enf, benign):
    # Fail-closed safety means a false positive censors legitimate content.
    # The danger list is intentionally specific (no bare 傷害/非法/詳細步驟).
    assert enf._evaluate_safety(benign, {}) == SAFE
