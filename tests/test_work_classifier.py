"""Tests for RFC-013: WorkClassifier."""

from tonesoul.work_classifier import (
    ConstraintProfile,
    WorkCategory,
    classify_work,
    get_profile,
)


def test_all_categories_have_profiles():
    for cat in WorkCategory:
        profile = get_profile(cat)
        assert isinstance(profile, ConstraintProfile)


def test_workflow_hint_takes_priority():
    # Even if message says "research", /ci-debug wins
    result = classify_work("我要研究一下", workflow_hint="ci-debug")
    assert result == WorkCategory.DEBUG


def test_debug_keywords():
    assert classify_work("修 bug") == WorkCategory.DEBUG
    assert classify_work("這個 crash 了") == WorkCategory.DEBUG
    assert classify_work("CI red 修復") == WorkCategory.DEBUG
    assert classify_work("壞掉了先修一下") == WorkCategory.DEBUG


def test_engineering_keywords():
    assert classify_work("實作這個功能") == WorkCategory.ENGINEERING
    assert classify_work("寫一個新的模組") == WorkCategory.ENGINEERING
    assert classify_work("refactor the module") == WorkCategory.ENGINEERING


def test_architecture_keywords():
    assert classify_work("架構設計討論") == WorkCategory.ARCHITECTURE
    assert classify_work("寫一份 RFC") == WorkCategory.ARCHITECTURE
    assert classify_work("design the interface") == WorkCategory.ARCHITECTURE


def test_research_keywords():
    assert classify_work("研究一下這個倉庫") == WorkCategory.RESEARCH
    assert classify_work("比較兩個方案") == WorkCategory.RESEARCH
    assert classify_work("explore the alternatives") == WorkCategory.RESEARCH


def test_default_is_engineering():
    assert classify_work("hello") == WorkCategory.ENGINEERING
    assert classify_work("") == WorkCategory.ENGINEERING


def test_context_signals():
    # user_intent "debug" → DEBUG
    result = classify_work("隨便", context={"user_intent": "debug"})
    assert result == WorkCategory.DEBUG

    # genesis "mandatory" → ENGINEERING
    result = classify_work("隨便", context={"genesis": "mandatory"})
    assert result == WorkCategory.ENGINEERING


def test_gamma_base_ordering():
    """debug should have the highest γ_base, freeform the lowest."""
    freeform_g = get_profile(WorkCategory.FREEFORM).gamma_base
    research_g = get_profile(WorkCategory.RESEARCH).gamma_base
    arch_g = get_profile(WorkCategory.ARCHITECTURE).gamma_base
    eng_g = get_profile(WorkCategory.ENGINEERING).gamma_base
    debug_g = get_profile(WorkCategory.DEBUG).gamma_base

    assert freeform_g < research_g < arch_g < eng_g < debug_g


def test_workflow_hint_vibe_mode():
    assert classify_work("anything", workflow_hint="vibe_mode") == WorkCategory.FREEFORM
    assert classify_work("anything", workflow_hint="vibe-mode") == WorkCategory.FREEFORM


def test_workflow_hint_antigravity():
    assert classify_work("anything", workflow_hint="antigravity") == WorkCategory.ARCHITECTURE
