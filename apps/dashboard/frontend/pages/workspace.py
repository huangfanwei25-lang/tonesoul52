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
from utils.search import build_search_context, default_search_roots


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

    workspace = Path(__file__).parent.parent.parent
    seeds = list_seeds()
    skills = list_skills()
    latest = _latest_run_summary()

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

    col_main, col_side = st.columns([3, 1.1], gap="large")

    with col_main:
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

        if st.session_state.council_discussion:
            with st.expander("🧠 我在想...", expanded=False):
                render_council(st.session_state.council_discussion)

        chat_container = st.container(height=400)
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
                search_context = build_search_context(
                    user_input,
                    roots,
                    enable_local=use_local_search,
                    enable_web=use_web_search,
                )
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
        tab_status, tab_memory = st.tabs(["系統狀態", "參考資料"])
        with tab_status:
            render_status_panel(workspace)
        with tab_memory:
            render_memory_panel()
