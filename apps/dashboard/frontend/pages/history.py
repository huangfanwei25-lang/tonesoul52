"""
回顧頁面 - 對話歷史 + 決策追溯
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from utils.llm import log_mistake, log_pattern


def _load_json(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_session_traces() -> List[Dict]:
    """Load session traces from JSONL file."""
    traces_path = Path(__file__).resolve().parents[3] / "memory" / "autonomous" / "session_traces.jsonl"
    traces: List[Dict] = []
    if not traces_path.exists():
        return traces
    try:
        for line in traces_path.read_text(encoding="utf-8").strip().splitlines():
            line = line.strip()
            if line:
                traces.append(json.loads(line))
    except Exception:
        pass
    return traces


def _collect_runs(limit: int = 20) -> List[Dict]:
    run_root = Path(__file__).parent.parent.parent / "run" / "execution"
    runs: List[Dict] = []
    if not run_root.exists():
        return runs

    for run_path in sorted(run_root.iterdir(), reverse=True):
        if not run_path.is_dir():
            continue

        gate_report = _load_json(run_path / "gate_report.json") or {}
        dcs_result = _load_json(run_path / "dcs_result.json") or {}
        audit_request = _load_json(run_path / "audit_request.json") or {}
        intent_verification = _load_json(run_path / "intent_verification.json") or {}

        runs.append(
            {
                "id": run_path.name,
                "path": run_path,
                "time": datetime.fromtimestamp(run_path.stat().st_mtime),
                "overall": gate_report.get("overall", "unknown"),
                "gates": gate_report.get("results", []),
                "dcs_state": dcs_result.get("state"),
                "dcs_decision": dcs_result.get("decision"),
                "audit_request": audit_request,
                "intent_verification": intent_verification,
            }
        )

        if len(runs) >= limit:
            break

    return runs


def _load_conversation_ledger(workspace: Path, limit: int = 20) -> List[Dict]:
    ledger_path = workspace / "memory" / "conversation_ledger.jsonl"
    if not ledger_path.exists():
        return []

    entries: List[Dict] = []
    try:
        with ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    entries.append(payload)
    except Exception:
        return []

    if len(entries) > limit:
        return entries[-limit:]
    return entries


def _load_persona_trace(workspace: Path, limit: int = 30) -> List[Dict]:
    trace_path = workspace / "memory" / "persona_trace.jsonl"
    if not trace_path.exists():
        return []

    entries: List[Dict] = []
    try:
        with trace_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    entries.append(payload)
    except Exception:
        return []

    if len(entries) > limit:
        return entries[-limit:]
    return entries


def _format_timestamp(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def _conversation_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status).lower()
    label_map = {
        "success": "成功",
        "error": "失敗",
        "connection_error": "連線失敗",
        "exception": "例外",
    }
    return label_map.get(status_text, status_text)


def _conversation_label(entry: Dict) -> str:
    timestamp = _format_timestamp(entry.get("timestamp"))
    context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
    user_msg = context.get("user_message", "")
    summary = user_msg if len(user_msg) <= 28 else user_msg[:28] + "..."
    return f"{timestamp} · {summary}"


def _persona_trace_label(entry: Dict) -> str:
    timestamp = _format_timestamp(entry.get("timestamp"))
    persona_id = entry.get("persona_id") or "base"
    diff = entry.get("diff") if isinstance(entry.get("diff"), dict) else {}
    delta_len = diff.get("delta_len")
    delta_text = f"Δ字數 {delta_len:+}" if isinstance(delta_len, int) else "Δ字數 n/a"
    return f"{timestamp} · {persona_id} · {delta_text}"


MISTAKE_TYPE_OPTIONS = {
    "錯誤宣稱": "false_claim",
    "執行失敗": "execution_error",
    "上下文遺失": "context_loss",
    "安全風險": "security_risk",
    "其他": "other",
}


def _status_label(status: str) -> str:
    if not status:
        return "未知"
    status_text = str(status)
    label_map = {
        "PASS": "可用",
        "WARN": "注意",
        "FAIL": "阻擋",
        "PENDING": "處理中",
        "UNKNOWN": "未知",
    }
    return label_map.get(status_text.upper(), status_text)


def _intent_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status).lower()
    label_map = {
        "achieved": "達成",
        "failed": "失敗",
        "inconclusive": "證據不足",
        "unknown": "未知",
    }
    return label_map.get(status_text, status_text)


def render():
    """渲染回顧頁面"""

    st.markdown(
        """
        <div class="ts-hero">
          <h1>回顧</h1>
          <p>看看人工智慧過去怎麼做決定，每個決定都有記錄。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_decisions, tab_journal, tab_council = st.tabs(["決策記錄", "對話日誌", "審議時間軸"])

    # ── Load session traces for journal & council tabs ────────────────────
    traces = _load_session_traces()

    with tab_journal:
        try:
            from components.session_journal import render_session_journal

            render_session_journal(traces)
        except Exception:
            st.info("對話日誌載入失敗")

    with tab_council:
        try:
            from components.council_timeline import render_council_timeline

            render_council_timeline(traces)
        except Exception:
            st.info("審議時間軸載入失敗")

    with tab_decisions:
        workspace = Path(__file__).parent.parent.parent
        runs = _collect_runs(limit=40)
        if not runs:
            st.markdown(
                """
                <div class="ts-card">
                  <h4>決策流程</h4>
                  <p class="ts-muted">
                    在對話工作區與 AI 對話後，每個回應都會經過以下流程，記錄會自動出現在這裡。
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.code(
                "使用者輸入\n"
                "    │\n"
                "    ▼\n"
                "┌──────────────┐\n"
                "│  Gate 守門    │ ← 內在規則檢查\n"
                "└──────┬───────┘\n"
                "       ▼\n"
                "┌──────────────┐\n"
                "│ Council 審議  │ ← Guardian / Analyst / Critic / Advocate\n"
                "└──────┬───────┘\n"
                "       ▼\n"
                "┌──────────────┐\n"
                "│  Vow 誓言    │ ← 驗證是否違反承諾\n"
                "└──────┬───────┘\n"
                "       ▼\n"
                "   AI 回應 + 決策記錄",
                language=None,
            )

            st.markdown("**狀態圖例**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("🟢 **可用 (PASS)** — 通過所有守門")
            with col_b:
                st.markdown("🟡 **注意 (WARN)** — 有顧慮但放行")
            with col_c:
                st.markdown("🔴 **阻擋 (FAIL)** — 回應被攔截修正")

            st.info("在「對話工作區」與 AI 對話後，決策記錄會自動出現在這裡。")
            conversations = _load_conversation_ledger(workspace, limit=20)
            if conversations:
                with st.expander("對話追蹤", expanded=False):
                    rows = []
                    for entry in reversed(conversations):
                        context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
                        rows.append(
                            {
                                "時間": _format_timestamp(entry.get("timestamp")),
                                "狀態": _conversation_status_label(entry.get("status")),
                                "使用者": context.get("user_message", ""),
                                "回覆摘要": (entry.get("response") or "")[:60],
                            }
                        )
                    st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.caption("尚無對話追蹤記錄。")
            return

        pass_count = sum(1 for run in runs if run["overall"] == "PASS")
        warn_count = sum(1 for run in runs if run["overall"] == "WARN")
        fail_count = sum(1 for run in runs if run["overall"] == "FAIL")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("決策數", len(runs))
        with col2:
            st.metric("可用", pass_count)
        with col3:
            st.metric("注意", warn_count)
        with col4:
            st.metric("阻擋", fail_count)

        table_rows = [
            {
                "時間": run["time"].strftime("%Y-%m-%d %H:%M"),
                "決策編號": run["id"],
                "結果": _status_label(run["overall"]),
                "收斂狀態": run.get("dcs_state") or "無",
            }
            for run in runs
        ]
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

        conversations = _load_conversation_ledger(workspace, limit=20)
        if conversations:
            with st.expander("對話追蹤", expanded=False):
                rows = []
                for entry in reversed(conversations):
                    context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
                    rows.append(
                        {
                            "時間": _format_timestamp(entry.get("timestamp")),
                            "狀態": _conversation_status_label(entry.get("status")),
                            "使用者": context.get("user_message", ""),
                            "回覆摘要": (entry.get("response") or "")[:60],
                        }
                    )
                st.dataframe(rows, use_container_width=True, hide_index=True)

            with st.expander("對話追蹤工具", expanded=False):
                selection = st.selectbox(
                    "選擇對話記錄",
                    list(range(len(conversations))),
                    format_func=lambda i: _conversation_label(conversations[i]),
                )
                entry = conversations[selection]
                context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
                user_message = context.get("user_message", "")
                response_text = entry.get("response") or ""
                record_id = entry.get("record_id") or _format_timestamp(entry.get("timestamp"))
                status_label = _conversation_status_label(entry.get("status"))
                status_text = str(entry.get("status") or "").lower()
                is_error_state = status_text not in {"", "success"}

                st.markdown(
                    f"""
                    <div class="ts-card">
                      <div class="ts-pill">對話記錄</div>
                      <p class="ts-muted">編號: {record_id}</p>
                      <p class="ts-muted">狀態: {status_label}</p>
                      <p class="ts-muted">使用者: {user_message}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if response_text:
                    st.text_area("回覆摘要", response_text[:200], height=120)
                if is_error_state:
                    st.warning(f"偵測到異常狀態（{status_label}），建議建立踩雷記錄。")

                tab_mistake, tab_pattern = st.tabs(["新增踩雷", "新增策略"])

                with tab_mistake:
                    with st.form("conversation_mistake_form"):
                        mistake_label = st.selectbox("類型", list(MISTAKE_TYPE_OPTIONS.keys()))
                        mistake_type = MISTAKE_TYPE_OPTIONS[mistake_label]
                        description = st.text_area(
                            "描述", f"對話記錄 {record_id}（{status_label}）", height=80
                        )
                        context_text = st.text_area("情境", user_message, height=60)
                        lesson = st.text_area("教訓", "", height=60)
                        prevention = st.text_area("防止方式", "", height=60)
                        submit_mistake = st.form_submit_button("儲存踩雷記錄")
                        if submit_mistake:
                            if not description.strip():
                                st.warning("請先填寫描述。")
                            else:
                                mistake_id = log_mistake(
                                    mistake_type,
                                    description.strip(),
                                    context_text.strip(),
                                    lesson.strip(),
                                    prevention.strip(),
                                )
                                st.success(f"已記錄: mistake_{mistake_id}.json")

                with tab_pattern:
                    with st.form("conversation_pattern_form"):
                        default_name = user_message[:18] + ("..." if len(user_message) > 18 else "")
                        pattern_id = st.text_input("策略 ID（可留空）", "")
                        name = st.text_input("名稱", default_name)
                        when = st.text_input("使用時機", user_message or "對話追蹤轉存")
                        steps_text = st.text_area("步驟（每行一項）", "", height=100)
                        success_rate = st.slider("成功率", 0.0, 1.0, 0.8, 0.05)
                        last_used = st.text_input("最後使用日期", datetime.now().strftime("%Y-%m-%d"))
                        submit_pattern = st.form_submit_button("儲存策略模式")
                        if submit_pattern:
                            steps = [line.strip() for line in steps_text.splitlines() if line.strip()]
                            if not name.strip():
                                st.warning("請先填寫名稱。")
                            elif not steps:
                                st.warning("請至少輸入一條步驟。")
                            else:
                                pattern_key = log_pattern(
                                    pattern_id.strip(),
                                    name.strip(),
                                    when.strip(),
                                    steps,
                                    success_rate,
                                    last_used.strip(),
                                )
                                st.success(f"已記錄: pattern_{pattern_key}.json")
        else:
            st.caption("尚無對話追蹤記錄。")

        persona_traces = _load_persona_trace(workspace, limit=30)
        if persona_traces:
            with st.expander("人格追蹤", expanded=False):
                rows = []
                for entry in reversed(persona_traces):
                    shadow = entry.get("shadow") if isinstance(entry.get("shadow"), dict) else {}
                    vector = (
                        shadow.get("vector_estimate")
                        if isinstance(shadow.get("vector_estimate"), dict)
                        else {}
                    )
                    distance = (
                        shadow.get("vector_distance")
                        if isinstance(shadow.get("vector_distance"), dict)
                        else {}
                    )
                    diff = entry.get("diff") if isinstance(entry.get("diff"), dict) else {}
                    rows.append(
                        {
                            "時間": _format_timestamp(entry.get("timestamp")),
                            "人格": entry.get("persona_id") or "base",
                            "ΔT": vector.get("deltaT"),
                            "ΔS": vector.get("deltaS"),
                            "ΔR": vector.get("deltaR"),
                            "距離max": distance.get("max"),
                            "是否變更": "是" if diff.get("changed") else "否",
                        }
                    )
                st.dataframe(rows, use_container_width=True, hide_index=True)

                selection = st.selectbox(
                    "查看人格追蹤細節",
                    list(range(len(persona_traces))),
                    format_func=lambda i: _persona_trace_label(persona_traces[i]),
                    key="persona_trace_select",
                )
                entry = persona_traces[selection]
                shadow = entry.get("shadow") if isinstance(entry.get("shadow"), dict) else {}
                persona_meta = shadow.get("persona") if isinstance(shadow.get("persona"), dict) else {}
                vector = (
                    shadow.get("vector_estimate")
                    if isinstance(shadow.get("vector_estimate"), dict)
                    else {}
                )
                distance = (
                    shadow.get("vector_distance")
                    if isinstance(shadow.get("vector_distance"), dict)
                    else {}
                )
                st.markdown(
                    f"""
                    <div class="ts-card">
                      <div class="ts-pill">人格向量估計</div>
                      <p class="ts-muted">人格: {persona_meta.get('name') or entry.get('persona_id') or 'base'}</p>
                      <p class="ts-muted">ΔT: {vector.get('deltaT')} | ΔS: {vector.get('deltaS')} | ΔR: {vector.get('deltaR')}</p>
                      <p class="ts-muted">距離平均: {distance.get('mean', 'n/a')} | 最大: {distance.get('max', 'n/a')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                raw_text = entry.get("raw_response") or ""
                final_text = entry.get("final_response") or ""
                if raw_text:
                    st.text_area("原始輸出", raw_text[:800], height=140)
                if final_text:
                    st.text_area("人格後輸出", final_text[:800], height=140)
        else:
            st.caption("尚無人格追蹤記錄。")

        selected = st.selectbox(
            "查看單次決策", list(range(len(runs))), format_func=lambda i: runs[i]["id"]
        )
        run = runs[selected]

        st.markdown(
            f"""
            <div class="ts-card">
              <div class="ts-pill">決策詳情</div>
              <p class="ts-muted">編號: {run['id']}</p>
              <p class="ts-muted">時間: {run['time'].strftime('%Y-%m-%d %H:%M:%S')}</p>
              <p class="ts-muted">結果: {_status_label(run['overall'])}</p>
              <p class="ts-muted">收斂狀態: {run.get('dcs_state') or '無'}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        intent_payload = run.get("intent_verification") or {}
        audit_payload = (
            intent_payload.get("audit") if isinstance(intent_payload.get("audit"), dict) else {}
        )
        intent_status = audit_payload.get("status") or intent_payload.get("status")
        intent_confidence = audit_payload.get("confidence")
        intent_reason = audit_payload.get("reason")
        if intent_status:
            confidence_text = (
                f"{float(intent_confidence):.2f}"
                if isinstance(intent_confidence, (int, float))
                else "無"
            )
            st.markdown(
                f"""
                <div class="ts-card">
                  <div class="ts-pill">意圖達成驗證</div>
                  <p class="ts-muted">狀態: {_intent_status_label(intent_status)}</p>
                  <p class="ts-muted">信心: {confidence_text}</p>
                  <p class="ts-muted">原因: {intent_reason or '無'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="ts-section-title">內在守門</div>', unsafe_allow_html=True)
        for gate in run.get("gates", []):
            name = gate.get("gate", "未知規則")
            passed = gate.get("passed", False)
            status = "通過" if passed else "注意"
            st.markdown(f"{status} · {name}")

        audit_request = run.get("audit_request") or {}
        inputs = audit_request.get("inputs") or {}
        trace_capture = inputs.get("tech_trace_capture")
        trace_normalize = inputs.get("tech_trace_normalize")

        if trace_capture or trace_normalize:
            st.markdown('<div class="ts-section-title">外部蒐集</div>', unsafe_allow_html=True)
            st.markdown(f"- 擷取: {trace_capture or '無'}")
            st.markdown(f"- 正規化: {trace_normalize or '無'}")
