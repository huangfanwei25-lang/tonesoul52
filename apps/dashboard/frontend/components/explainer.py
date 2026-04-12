"""
Explainer — concept tooltip components for layered disclosure.

首頁用親民用詞，點 (?) 展開技術細節和計算方式。
"""

from __future__ import annotations

import streamlit as st

_EXPLANATIONS = {
    "soul_integral": {
        "title": "壓力指數 (Soul Integral)",
        "simple": "AI 目前承受的語義壓力有多大。數字越高，表示最近的對話中累積了越多未解決的張力。",
        "detail": (
            "Soul Integral (SI) 是語義壓力的累積衰減值。每次 session 中偵測到的 tension "
            "會被加入，並隨時間以指數衰減。計算方式：\n\n"
            "```\nSI(t) = Σ tension_i × e^(-λ × Δt_i)\n```\n\n"
            "其中 λ 是衰減率，Δt 是距離該 tension 發生的時間差。"
        ),
    },
    "soul_band": {
        "title": "目前狀態 (Soul Band)",
        "simple": "AI 的整體健康狀態分為四級：平靜、警覺、緊繃、危機。狀態越緊繃，內部審議會越嚴格。",
        "detail": (
            "四段帶分級：\n"
            "- **平靜** (SI < 0.30): 閘門 100%，正常自主\n"
            "- **警覺** (0.30 ≤ SI < 0.55): 閘門 90%，輕微收緊\n"
            "- **緊繃** (0.55 ≤ SI < 0.80): 閘門 75%，強制 Council\n"
            "- **危機** (SI ≥ 0.80): 閘門 55%，最大限制\n\n"
            "閘門靈敏度 (gate_modifier) 會調整反射弧的判斷門檻。"
        ),
    },
    "tension": {
        "title": "壓力 (Tension)",
        "simple": "AI 輸出和預期之間的語義差距。差距越大，壓力越高。",
        "detail": (
            "Tension 由 TensionEngine.compute() 計算：\n\n"
            "```\ntension = f(intended, generated, text_tension, confidence)\n```\n\n"
            "包含事實阻力 (fact)、邏輯阻力 (logic)、倫理阻力 (ethics) 三個維度。"
        ),
    },
    "drift": {
        "title": "性格偏移 (Baseline Drift)",
        "simple": "AI 的行為風格隨時間的偏移程度。三個軸分別代表謹慎度、創意度、自主度。",
        "detail": (
            "三軸指標：\n"
            "- **caution_bias**: 謹慎度（0=大膽, 1=極度謹慎）\n"
            "- **innovation_bias**: 創意度（0=保守, 1=極度創新）\n"
            "- **autonomy_level**: 自主度（0=完全依賴, 1=完全自主）\n\n"
            "中性值為 0.5。偏離越大，表示行為風格越偏離基線。"
        ),
    },
    "vow": {
        "title": "承諾 (Vow)",
        "simple": "AI 對使用者的語義誓言。每次輸出前會驗證是否違反任何承諾。",
        "detail": (
            "Vow System 由 VowEnforcer 執行：\n\n"
            "1. 每個 vow 是一條可機器執行的規則\n"
            "2. AI 輸出前，enforce(output) 檢查所有 active vows\n"
            "3. 違規時：阻擋輸出 或 觸發修正\n"
            "4. 違規記錄寫入治理狀態"
        ),
    },
    "council": {
        "title": "內部審議 (Council)",
        "simple": "AI 內部的多角度議會。Guardian、Analyst、Critic、Advocate 四個角色從不同角度審查每個回應。",
        "detail": (
            "Council 審議流程：\n\n"
            "1. 收到草稿輸出 + 使用者意圖\n"
            "2. 各角色獨立投票：approve / concern / block\n"
            "3. 彙整判決：通過 / 修正 / 阻擋\n"
            "4. 計算一致性 (coherence)\n\n"
            "當 Soul Band 進入緊繃區，強制召集 Council。"
        ),
    },
}


def render_explainer(key: str) -> None:
    """Render an inline explainer for the given concept key."""
    info = _EXPLANATIONS.get(key)
    if not info:
        return

    with st.expander(f"(?) {info['title']}", expanded=False):
        st.markdown(info["simple"])
        st.markdown("---")
        st.markdown(info["detail"])
