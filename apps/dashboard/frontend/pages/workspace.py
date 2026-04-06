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

    st.markdown("### Tiered Operator Shell")
    shell_col_a, shell_col_b = st.columns([1.25, 1.75], gap="large")

    with shell_col_a:
        st.markdown("**Tier 0 · Instant Gate**")
        if not tier0_bundle.get("present"):
            st.warning(tier0_bundle.get("error") or "無法載入 Tier 0 session-start")
        else:
            gate_row_a, gate_row_b, gate_row_c = st.columns(3)
            with gate_row_a:
                st.metric("Readiness", tier0_shell.get("readiness_status") or "unknown")
            with gate_row_b:
                st.metric("Track", tier0_shell.get("task_track") or "unclassified")
            with gate_row_c:
                st.metric("Mode", tier0_shell.get("deliberation_mode") or "unknown")

            if tier0_shell.get("canonical_summary"):
                st.caption(tier0_shell["canonical_summary"])

            next_followup = tier0_shell.get("next_followup") or {}
            st.markdown("**Next bounded move**")
            st.code(next_followup.get("command") or "n/a", language="bash")
            if next_followup.get("reason"):
                st.caption(next_followup["reason"])

            hook_badges = tier0_shell.get("hook_badges") or []
            if hook_badges:
                hooks_text = " | ".join(
                    f"{item['name']}:{item['status']}" for item in hook_badges[:3]
                )
                st.caption(f"Hooks: {hooks_text}")

    with shell_col_b:
        st.markdown("**Tier 1 · Orientation Shell**")
        if not tier1_bundle.get("present"):
            st.warning(tier1_bundle.get("error") or "無法載入 Tier 1 session-start")
        else:
            canonical_cards = tier1_shell.get("canonical_cards") or {}
            st.info(canonical_cards.get("short_board") or "current short board not visible")
            if canonical_cards.get("successor_correction"):
                st.caption(canonical_cards["successor_correction"])

            parity_counts = tier1_shell.get("parity_counts") or {}
            parity_cols = st.columns(4)
            parity_labels = [
                ("Baseline", "baseline"),
                ("Beta", "beta_usable"),
                ("Partial", "partial"),
                ("Deferred", "deferred"),
            ]
            for col, (label, key) in zip(parity_cols, parity_labels):
                with col:
                    st.metric(label, int(parity_counts.get(key, 0) or 0))

            closeout_attention = tier1_shell.get("closeout_attention") or {}
            if closeout_attention.get("present"):
                st.warning(closeout_attention.get("summary_text") or "closeout attention present")
            else:
                st.caption("Closeout attention: none")

            observer_shell = tier1_shell.get("observer_shell") or {}
            counts = observer_shell.get("counts") or {}
            st.caption(
                "Observer shell: "
                f"stable={int(counts.get('stable', 0) or 0)} | "
                f"contested={int(counts.get('contested', 0) or 0)} | "
                f"stale={int(counts.get('stale', 0) or 0)}"
            )

            with st.expander("Tier 1 details", expanded=False):
                if canonical_cards.get("source_precedence"):
                    st.markdown(f"**Source precedence**  \n{canonical_cards['source_precedence']}")

                family_cards = tier1_shell.get("family_cards") or []
                if family_cards:
                    st.markdown("**Subsystem gaps**")
                    for family in family_cards:
                        st.markdown(
                            f"- `{family['name']}` [{family['status']}]"
                            f" — gap: {family['main_gap']} | next: {family['next_move']}"
                        )

                for label, items in (
                    ("Stable", observer_shell.get("stable_headlines") or []),
                    ("Contested", observer_shell.get("contested_headlines") or []),
                    ("Stale", observer_shell.get("stale_headlines") or []),
                ):
                    if items:
                        st.markdown(f"**{label}**")
                        for item in items:
                            st.markdown(f"- {item}")

            st.markdown("**Tier 2 · Deep Governance**")
            if not tier2_drawer.get("present"):
                st.caption("Tier 2 drawer unavailable")
            else:
                if tier2_drawer.get("recommended_open"):
                    st.warning(
                        "Deep governance review recommended: "
                        + ", ".join(tier2_drawer.get("trigger_reasons") or [])
                    )
                else:
                    st.caption("No default Tier 2 trigger is active. Open only for contested or risky work.")

                with st.expander("Open Tier 2 drawer", expanded=False):
                    st.caption(tier2_drawer.get("summary_text") or "drawer summary unavailable")
                    active_groups = tier2_drawer.get("active_group_names") or []
                    if active_groups:
                        st.caption("Active groups: " + " | ".join(active_groups))

                    for group in tier2_drawer.get("groups") or []:
                        st.markdown(f"**{group['name']}**")
                        for card in group.get("cards") or []:
                            st.markdown(
                                f"- `{card['title']}` [{card['status']}]"
                                f" — {card['summary']}"
                            )
                            if card.get("guard"):
                                st.caption(card["guard"])

                    commands = tier2_drawer.get("next_pull_commands") or []
                    if commands:
                        st.markdown("**Next deeper pull**")
                        for command in commands:
                            st.code(command, language="bash")

            st.markdown("**Operator Walkthrough Pack**")
            st.caption(walkthrough_pack.get("operator_rule") or "Use the smallest honest tier.")
            with st.expander("Open walkthrough pack", expanded=False):
                st.caption(walkthrough_pack.get("public_boundary") or "")
                for scenario in walkthrough_pack.get("scenarios") or []:
                    st.markdown(
                        f"**{scenario['name']}**  \n"
                        f"Default: `{scenario['default_tier']}`"
                    )
                    st.markdown(f"- Use when: {scenario['use_when']}")
                    st.markdown(f"- Stay here when: {scenario['stop_here_rule']}")
                    st.markdown(f"- Current move: {scenario['next_move']}")
                    st.markdown(f"- Escalate when: {scenario['escalate_when']}")

            st.markdown("**Command Shelf**")
            st.caption(command_shelf.get("operator_rule") or "Keep CLI/runtime parity visible.")
            with st.expander("Open command shelf", expanded=False):
                for item in command_shelf.get("commands") or []:
                    st.markdown(f"**{item['label']}**  \n{item['purpose']}")
                    st.caption(item["tier"])
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
