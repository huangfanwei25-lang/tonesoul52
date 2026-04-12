"""
首頁 — 30 秒內讓新來的人理解 ToneSoul 是什麼
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


def _load_governance_snapshot() -> dict[str, Any]:
    """Load current governance posture for the overview cards."""
    try:
        from tonesoul.runtime_adapter import load, summary

        posture = load(agent_id="dashboard-overview", source="dashboard")
        return {
            "soul_integral": round(posture.soul_integral, 4),
            "session_count": posture.session_count,
            "active_vows": len(posture.active_vows),
            "active_tensions": len(posture.tension_history),
            "last_updated": posture.last_updated or "from_empty",
            "summary": summary(posture),
            "tension_history": posture.tension_history,
            "baseline_drift": posture.baseline_drift,
        }
    except Exception:
        return {
            "soul_integral": 0.0,
            "session_count": 0,
            "active_vows": 0,
            "active_tensions": 0,
            "last_updated": "unavailable",
            "summary": "unable to load governance state",
            "tension_history": [],
            "baseline_drift": {},
        }


def _load_health_snapshot() -> dict[str, Any]:
    """Load system health for the overview cards."""
    try:
        from tonesoul.store import get_store

        store = get_store()
        backend = store.backend_name
    except Exception:
        backend = "unknown"

    try:
        from tonesoul.aegis_shield import AegisShield
        from tonesoul.store import get_store

        store = get_store()
        shield = AegisShield.load(store)
        chain_status = "intact" if shield.chain_head else "empty"
    except Exception:
        chain_status = "unknown"

    try:
        from tonesoul.runtime_adapter import get_recent_visitors

        visitors = get_recent_visitors(n=3)
        recent_visitors = [str(v.get("agent", "unknown")) for v in visitors]
    except Exception:
        recent_visitors = []

    return {
        "backend": backend,
        "chain_status": chain_status,
        "recent_visitors": recent_visitors,
    }


def _load_vow_snapshot() -> dict[str, Any]:
    """Load vow enforcement state."""
    try:
        from tonesoul.vow_system import VowRegistry

        registry = VowRegistry()
        active = registry.active_vows()
        return {
            "total": len(registry.all_vows()),
            "active": len(active),
            "vow_names": [v.title for v in active[:5]],
            "raw_vows": [
                {
                    "id": getattr(v, "id", ""),
                    "content": getattr(v, "title", str(v)),
                    "source": getattr(v, "source", ""),
                    "created": getattr(v, "created", ""),
                }
                for v in active
            ],
        }
    except Exception:
        return {
            "total": 0,
            "active": 0,
            "vow_names": [],
            "raw_vows": [],
        }


def _load_reflex_snapshot() -> dict[str, Any]:
    """Load reflex arc state for the soul band indicator."""
    try:
        from tonesoul.governance.reflex import GovernanceSnapshot, ReflexEvaluator
        from tonesoul.governance.reflex_config import load_reflex_config
        from tonesoul.runtime_adapter import load as load_posture

        config = load_reflex_config()
        posture = load_posture()
        snapshot = GovernanceSnapshot.from_posture(posture, tension=0.0)
        evaluator = ReflexEvaluator(config=config)
        decision = evaluator.evaluate(snapshot)
        band = decision.soul_band
        return {
            "enabled": config.enabled,
            "mode": config.vow_enforcement_mode,
            "soul_band": band.level.value if band else "unknown",
            "gate_modifier": band.gate_modifier if band else 1.0,
            "force_council": band.force_council if band else False,
            "max_autonomy": band.max_autonomy if band else None,
            "action": decision.action.value,
        }
    except Exception:
        return {
            "enabled": False,
            "mode": "unknown",
            "soul_band": "unknown",
            "gate_modifier": 1.0,
            "force_council": False,
            "max_autonomy": None,
            "action": "pass",
        }


_BAND_COLORS = {
    "serene": "#4ade80",  # green
    "alert": "#facc15",  # yellow
    "strained": "#f97316",  # orange
    "critical": "#ef4444",  # red
}

_BAND_LABELS = {
    "serene": "平靜",
    "alert": "警覺",
    "strained": "緊繃",
    "critical": "危機",
}


def render() -> None:
    """Render the overview landing page."""

    # ── Live data auto-refresh ───────────────────────────────────────────
    try:
        from utils.live_data import render_auto_refresh_toggle

        render_auto_refresh_toggle()
    except Exception:
        pass

    st.markdown(
        """
        <div class="ts-hero">
          <h1>ToneSoul / 語魂</h1>
          <p>AI 治理框架 — 讓 AI 對自己說過的話負責</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.markdown(
        "語魂是一套**語義責任系統**：AI 在對話中做出的承諾會被記錄、追蹤、驗證。"
        "每次對話都經過內部審議，治理狀態跨 session 存續。"
    )

    # ── World Map ─────────────────────────────────────────────────────────

    show_world = st.checkbox("顯示世界地圖", value=False, key="show_world_map")
    if show_world:
        if "world_html_cache" not in st.session_state:
            try:
                from utils.world_bridge import build_world_html

                st.session_state["world_html_cache"] = build_world_html()
            except Exception:
                st.session_state["world_html_cache"] = None

        if st.session_state["world_html_cache"]:
            st.components.v1.html(st.session_state["world_html_cache"], height=620, scrolling=False)
        else:
            st.caption("世界地圖載入失敗 — 請確認 world.html 存在")

    # ── Three overview cards ──────────────────────────────────────────────

    gov = _load_governance_snapshot()
    vows = _load_vow_snapshot()
    health = _load_health_snapshot()
    reflex = _load_reflex_snapshot()

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            """
            <div class="ts-card">
              <div class="ts-pill">AI 的承諾</div>
              <h4>語義誓言 (Vow)</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("啟用中的誓言", f"{vows['active']} / {vows['total']}")
        if vows["vow_names"]:
            for name in vows["vow_names"]:
                st.caption(f"  - {name}")
        else:
            st.caption("使用預設誓言：不誤導、揭露不確定性、不造成傷害")

    with col_b:
        st.markdown(
            """
            <div class="ts-card">
              <div class="ts-pill">治理狀態</div>
              <h4>靈魂積分 / 會話數</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        metric_a, metric_b = st.columns(2)
        with metric_a:
            st.metric("壓力指數", gov["soul_integral"])
        with metric_b:
            st.metric("對話次數", gov["session_count"])
        if gov["active_tensions"] > 0:
            st.caption(f"目前有 {gov['active_tensions']} 個活躍壓力")
        else:
            st.caption("目前狀態平穩")

        # Soul Band indicator
        band_name = reflex["soul_band"]
        band_color = _BAND_COLORS.get(band_name, "#9ca3af")
        band_label = _BAND_LABELS.get(band_name, band_name)
        mode_label = "硬執行" if reflex["mode"] == "hard" else "軟執行"
        st.markdown(
            f'<div style="margin-top:8px;padding:6px 12px;border-radius:8px;'
            f'background:{band_color}22;border:1px solid {band_color}">'
            f'<span style="color:{band_color};font-weight:bold">'
            f"目前狀態: {band_label}</span>"
            f' <span style="font-size:0.85em;color:#888">'
            f"| 閘門 {reflex['gate_modifier']:.0%} | {mode_label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_c:
        st.markdown(
            """
            <div class="ts-card">
              <div class="ts-pill">系統健康</div>
              <h4>後端 / 完整性</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("儲存後端", health["backend"].upper())
        st.caption(f"Aegis 鏈: {health['chain_status']}")
        if health["recent_visitors"]:
            st.caption("最近訪客: " + ", ".join(health["recent_visitors"]))
        else:
            st.caption("尚無訪客記錄")

    # ── Quick start ───────────────────────────────────────────────────────

    # ── Governance Pulse ─────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("### 治理脈搏")

    pulse_a, pulse_b, pulse_c = st.columns(3)

    with pulse_a:
        try:
            from components.soul_band_gauge import render_soul_band_gauge

            render_soul_band_gauge(
                soul_integral=float(gov["soul_integral"]),
                band_name=reflex["soul_band"],
                gate_modifier=reflex["gate_modifier"],
                force_council=reflex.get("force_council", False),
            )
        except Exception:
            st.caption("Soul Band gauge 載入失敗")

    with pulse_b:
        try:
            from components.tension_chart import render_tension_chart

            tensions = gov.get("tension_history", [])
            render_tension_chart(tensions)
        except Exception:
            st.caption("壓力歷程載入失敗")

    with pulse_c:
        try:
            from components.drift_radar import render_drift_radar

            drift = gov.get("baseline_drift", {})
            render_drift_radar(drift)
        except Exception:
            st.caption("性格偏移載入失敗")

    # ── Vow cards ────────────────────────────────────────────────────────

    try:
        from components.vow_cards import render_vow_cards

        raw_vows = vows.get("raw_vows", [])
        render_vow_cards(raw_vows)
    except Exception:
        pass  # Falls back to existing vow display in the cards above

    # ── Quick start ───────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("### 快速開始")
    st.markdown("選擇你想做的事：")

    qs_a, qs_b, qs_c = st.columns(3)

    with qs_a:
        st.markdown(
            """
            <div class="ts-card" style="text-align: center;">
              <h4>跟 AI 對話</h4>
              <p class="ts-muted">在對話工作區中，AI 的每個回應都經過 Council 審議。你可以看到它在想什麼。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("從左側導航進入「對話工作區」")

    with qs_b:
        st.markdown(
            """
            <div class="ts-card" style="text-align: center;">
              <h4>看 AI 的記憶</h4>
              <p class="ts-muted">AI 的技能、筆記、對話記錄都在這裡。你可以幫它記住重要的事。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("從左側導航進入「AI 記憶」")

    with qs_c:
        st.markdown(
            """
            <div class="ts-card" style="text-align: center;">
              <h4>看決策歷史</h4>
              <p class="ts-muted">每次決策都有記錄：通過了哪些內在守門、收斂到什麼狀態。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("從左側導航進入「決策回顧」")

    # ── How it works ──────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("### 運作原理")
    st.markdown("""
        ```
        Session 開始            對話中               Session 結束
        ┌──────────┐    ┌─────────────────┐    ┌──────────────┐
        │  Load    │───>│  Council 審議    │───>│   Commit     │
        │ 載入治理  │    │ 多角度內部討論    │    │  寫入治理記錄  │
        │ 狀態     │    │ Vow 誓言驗證     │    │  更新積分     │
        └──────────┘    └─────────────────┘    └──────────────┘
              │                                        │
              └────────── 跨 Session 存續 ──────────────┘
        ```

        - **Load**: 每次對話開始，AI 載入上次的治理狀態（tensions, vows, drift）
        - **Council**: 對話過程中，內部 Council（多個觀點角色）對每個回應進行審議
        - **Vow Check**: 在輸出前驗證是否符合所有語義誓言
        - **Commit**: 對話結束後，將本次 session 的治理記錄寫回，更新 soul integral
        """)

    # ── For developers / AI agents ────────────────────────────────────────

    with st.expander("開發者 / AI Agent 入口", expanded=False):
        st.markdown("""
            如果你是開發者或 AI agent，可以用 CLI 直接接入：

            ```bash
            # Session 開始
            python scripts/start_agent_session.py --agent your-id --no-ack

            # 查看治理狀態
            python -m tonesoul.diagnose --agent your-id

            # Session 結束
            python scripts/end_agent_session.py --agent your-id --summary "..."
            ```

            或透過 HTTP Gateway（任何能發 HTTP 的 agent 都能用）：

            ```bash
            python scripts/gateway.py --port 7700 --token YOUR_SECRET
            # POST /load, POST /commit, GET /summary, GET /audit
            ```
            """)
