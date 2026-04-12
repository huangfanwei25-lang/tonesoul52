"""
工作區頁面 - 對話 + Council 顯示 + 記憶面板
"""

import json
from pathlib import Path

import streamlit as st
from components.council import render_council
from components.memory_panel import render_memory_panel
from components.status_panel import render_status_panel
from utils.llm import chat_with_council
from utils.memory import list_seeds, list_skills
from utils.search import (
    build_search_context_boundary_cue,
    build_search_context_from_hits,
    build_search_preview_model,
    default_search_roots,
    search_local,
    search_web,
)
from utils.session_start import (
    build_dashboard_command_shelf,
    build_operator_walkthrough_pack,
    build_tier0_start_strip,
    build_tier1_orientation_shell,
    build_tier2_deep_governance_drawer,
    run_session_start_bundle,
)

WORKSPACE_PANEL_HEIGHT = 680
CHAT_CONTAINER_HEIGHT = 420
WORKSPACE_AGENT_ID = "dashboard-workspace"


def _latest_run_summary() -> dict:
    run_root = Path(__file__).parent.parent.parent / "run" / "execution"
    if not run_root.exists():
        return {"status": "N/A", "id": None}

    runs = sorted(
        [p for p in run_root.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not runs:
        return {"status": "N/A", "id": None}

    latest = runs[0]
    status = "unknown"
    gate_report = latest / "gate_report.json"
    if gate_report.exists():
        try:
            status = json.loads(gate_report.read_text(encoding="utf-8")).get("overall", "unknown")
        except Exception:
            status = "unknown"

    return {"status": status, "id": latest.name}


def _status_label(status: str) -> str:
    if not status:
        return "未知"
    status_text = str(status)
    label_map = {
        "PASS": "可用",
        "WARN": "注意",
        "FAIL": "阻擋",
        "UNKNOWN": "未知",
        "N/A": "無",
    }
    return label_map.get(status_text.upper(), status_text)


def render():
    """渲染工作區頁面"""

    st.markdown(
        """
        <div class="ts-hero">
          <h1>對話工作區</h1>
          <p>讓用戶看到人工智慧在想什麼，像一位可以對話的工作夥伴。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 初始化 session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "council_discussion" not in st.session_state:
        st.session_state.council_discussion = None
    if "selected_memories" not in st.session_state:
        st.session_state.selected_memories = []
    if "search_preview" not in st.session_state:
        st.session_state.search_preview = {}

    workspace = Path(__file__).parent.parent.parent
    seeds = list_seeds()
    skills = list_skills()
    latest = _latest_run_summary()
    tier0_bundle = run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=0, repo_root=workspace)
    tier1_bundle = run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=1, repo_root=workspace)
    tier2_bundle = run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=2, repo_root=workspace)
    tier0_shell = build_tier0_start_strip(tier0_bundle) if tier0_bundle.get("present") else {}
    tier1_shell = build_tier1_orientation_shell(tier1_bundle) if tier1_bundle.get("present") else {}
    tier2_drawer = (
        build_tier2_deep_governance_drawer(tier2_bundle)
        if tier2_bundle.get("present")
        else {}
    )
    walkthrough_pack = build_operator_walkthrough_pack(
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
    )
    command_shelf = build_dashboard_command_shelf(
        agent_id=WORKSPACE_AGENT_ID,
        tier0_shell=tier0_shell,
        tier2_drawer=tier2_drawer,
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("專案筆記", len(seeds))
        if not seeds:
            st.caption("尚未新增專案筆記，可在「我的記憶」新增。")
    with col_b:
        st.metric("技能庫", len(skills))
        if not skills:
            st.caption("尚未新增技能，可在 `spec/skills` 新增 YAML。")
    with col_c:
        st.metric("最近決策", _status_label(latest["status"]))
        if latest.get("status") in {None, "N/A", "unknown"}:
            st.caption("尚無決策紀錄。")

    # ── Quick status strip (always visible) ─────────────────────────────
    readiness = tier0_shell.get("readiness_status") or "unknown"
    track = tier0_shell.get("task_track") or "unclassified"
    mode = tier0_shell.get("deliberation_mode") or "unknown"
    strip_a, strip_b, strip_c = st.columns(3)
    with strip_a:
        st.metric("就緒狀態", readiness)
    with strip_b:
        st.metric("任務路徑", track)
    with strip_c:
        st.metric("審議模式", mode)

    # ── Tiered Operator Shell — Collapsible operator panels ────────────

    # Tier 0 · Instant Gate
    with st.expander("快速狀態檢查", expanded=False):
        if not tier0_bundle.get("present"):
            st.warning(tier0_bundle.get("error") or "無法載入狀態")
        else:
            if tier0_shell.get("canonical_summary"):
                st.caption(tier0_shell["canonical_summary"])

            next_followup = tier0_shell.get("next_followup") or {}
            st.markdown("**下一步建議**")
            st.code(next_followup.get("command") or "n/a", language="bash")
            if next_followup.get("reason"):
                st.caption(next_followup["reason"])

            hook_badges = tier0_shell.get("hook_badges") or []
            if hook_badges:
                hooks_text = " | ".join(
                    f"{item['name']}:{item['status']}" for item in hook_badges[:3]
                )
                st.caption(f"Hooks: {hooks_text}")

    # Tier 1 · Orientation Shell
    with st.expander("當前工作方向", expanded=False):
        if not tier1_bundle.get("present"):
            st.warning(tier1_bundle.get("error") or "無法載入方向資訊")
        else:
            canonical_cards = tier1_shell.get("canonical_cards") or {}
            st.info(canonical_cards.get("short_board") or "目前沒有明確的短板")
            if canonical_cards.get("successor_correction"):
                st.caption(canonical_cards["successor_correction"])

            parity_counts = tier1_shell.get("parity_counts") or {}
            parity_cols = st.columns(4)
            parity_labels = [
                ("基線", "baseline"),
                ("Beta 可用", "beta_usable"),
                ("部分完成", "partial"),
                ("延後", "deferred"),
            ]
            for col, (label, key) in zip(parity_cols, parity_labels):
                with col:
                    st.metric(label, int(parity_counts.get(key, 0) or 0))

            closeout_attention = tier1_shell.get("closeout_attention") or {}
            if closeout_attention.get("present"):
                st.warning(closeout_attention.get("summary_text") or "有需要注意的收尾事項")
            else:
                st.caption("沒有需要特別注意的收尾事項")

            observer_shell = tier1_shell.get("observer_shell") or {}
            counts = observer_shell.get("counts") or {}
            st.caption(
                "觀察窗口: "
                f"穩定={int(counts.get('stable', 0) or 0)} | "
                f"爭議={int(counts.get('contested', 0) or 0)} | "
                f"過時={int(counts.get('stale', 0) or 0)}"
            )

            family_cards = tier1_shell.get("family_cards") or []
            if family_cards:
                st.markdown("**子系統缺口**")
                for family in family_cards:
                    st.markdown(
                        f"- `{family['name']}` [{family['status']}]"
                        f" — 缺口: {family['main_gap']} | 下一步: {family['next_move']}"
                    )

    # Tier 2 · Deep Governance — Open Tier 2 drawer
    with st.expander("深層治理審查", expanded=False):
        if not tier2_drawer.get("present"):
            st.caption("深層審查不可用")
        else:
            if tier2_drawer.get("recommended_open"):
                st.warning(
                    "建議開啟深層審查: "
                    + ", ".join(tier2_drawer.get("trigger_reasons") or [])
                )
            else:
                st.caption("目前不需要深層審查。僅在有爭議或高風險操作時開啟。")

            st.caption(tier2_drawer.get("summary_text") or "")
            for group in tier2_drawer.get("groups") or []:
                st.markdown(f"**{group['name']}**")
                for card in group.get("cards") or []:
                    st.markdown(
                        f"- `{card['title']}` [{card['status']}] — {card['summary']}"
                    )

            commands = tier2_drawer.get("next_pull_commands") or []
            if commands:
                st.markdown("**建議的深層指令**")
                for command in commands:
                    st.code(command, language="bash")

    with st.expander("操作指南", expanded=False):
        st.caption(walkthrough_pack.get("operator_rule") or "使用最小必要的層級。")
        for scenario in walkthrough_pack.get("scenarios") or []:
            st.markdown(f"**{scenario['name']}** — 預設: `{scenario['default_tier']}`")
            st.markdown(f"- 使用時機: {scenario['use_when']}")
            st.markdown(f"- 目前動作: {scenario['next_move']}")

    with st.expander("常用指令", expanded=False):
        st.caption(command_shelf.get("operator_rule") or "Dashboard 是 CLI 的薄殼，不是替代品。")
        for item in command_shelf.get("commands") or []:
            st.markdown(f"**{item['label']}** ({item['tier']})")
            st.caption(item["purpose"])
            if item.get("source_surface"):
                st.caption(f"來源面: {item['source_surface']}")
            if item.get("activation_reason"):
                st.caption(f"顯示原因: {item['activation_reason']}")
            if item.get("return_rule"):
                st.caption(f"退回規則: {item['return_rule']}")
            st.code(item["command"], language="bash")

    col_main, col_side = st.columns([3, 1.1], gap="large")

    with col_main:
        main_panel = st.container(height=WORKSPACE_PANEL_HEIGHT)
        with main_panel:
            st.markdown('<div class="ts-section-title">對話工作區</div>', unsafe_allow_html=True)

            if not st.session_state.messages:
                st.info(
                    "試試問我：\n- 幫我整理今天進度\n- 我該先處理哪些問題？\n- 把需求拆成可執行步驟"
                )

            search_col1, search_col2 = st.columns(2)
            with search_col1:
                use_local_search = st.checkbox("本地檢索", value=False, key="workspace_local_search")
            with search_col2:
                use_web_search = st.checkbox("網路檢索", value=False, key="workspace_web_search")
            search_boundary_cue = build_search_context_boundary_cue(
                enable_local=use_local_search,
                enable_web=use_web_search,
            )
            st.caption(
                f"{search_boundary_cue['summary']} {search_boundary_cue['boundary']}"
            )
            search_preview = st.session_state.get("search_preview") or {}
            if search_preview.get("present"):
                st.markdown("**Retrieval Preview**")
                st.caption(search_preview.get("operator_rule") or "")
                with st.expander("Open retrieval preview", expanded=False):
                    st.caption(f"Query: {search_preview.get('query') or 'n/a'}")
                    for item in search_preview.get("items") or []:
                        st.markdown(f"**{item['source']}** · {item['label']}")
                        if item.get("detail"):
                            st.caption(item["detail"])
                        if item.get("snippet"):
                            st.markdown(f"- {item['snippet']}")

            if st.session_state.council_discussion:
                with st.expander("🧠 我在想...", expanded=False):
                    render_council(st.session_state.council_discussion)

            chat_container = st.container(height=CHAT_CONTAINER_HEIGHT)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            with st.form("workspace_chat_form", clear_on_submit=True):
                user_input = st.text_area("輸入訊息", "", height=90)
                submitted = st.form_submit_button("送出")
        if submitted and user_input:
            search_context = ""
            if use_local_search or use_web_search:
                roots = default_search_roots(workspace)
                local_hits = search_local(user_input, roots) if use_local_search else []
                web_hits = search_web(user_input) if use_web_search else []
                search_context = build_search_context_from_hits(
                    local_hits=local_hits,
                    web_hits=web_hits,
                )
                st.session_state.search_preview = build_search_preview_model(
                    query=user_input,
                    local_hits=local_hits,
                    web_hits=web_hits,
                )
            else:
                st.session_state.search_preview = {}
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("讓我想想..."):
                council, response = chat_with_council(
                    user_input,
                    st.session_state.selected_memories,
                    retrieval_context=search_context,
                )
                st.session_state.council_discussion = council

            st.session_state.messages.append({"role": "assistant", "content": response})

            st.rerun()

    with col_side:
        side_panel = st.container(height=WORKSPACE_PANEL_HEIGHT)
        with side_panel:
            tab_status, tab_memory = st.tabs(["系統狀態", "參考資料"])
            with tab_status:
                render_status_panel(
                    workspace,
                    tier0_shell=tier0_shell,
                    tier1_shell=tier1_shell,
                    tier2_drawer=tier2_drawer,
                )
            with tab_memory:
                render_memory_panel(
                    tier0_shell=tier0_shell,
                    tier1_shell=tier1_shell,
                )
