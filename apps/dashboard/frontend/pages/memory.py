"""
記憶頁面 - 瀏覽技能、筆記、對話記憶
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from utils.llm import log_mistake, log_pattern
from utils.memory import list_memory_entries, list_skills, load_memory, save_memory


def _preview_text(path: Path, limit: int = 800) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"讀取失敗: {exc}"

    if len(text) > limit:
        return text[:limit] + "\n...(內容已截斷)"
    return text


def _safe_parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_records(directory: Path, limit: int = 12) -> List[Dict]:
    records: List[Dict] = []
    if not directory.exists():
        return records

    for path in directory.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        payload["_path"] = str(path)
        payload["_mtime"] = path.stat().st_mtime
        records.append(payload)

    def sort_key(item: Dict) -> float:
        timestamp = _safe_parse_iso(item.get("timestamp"))
        if timestamp:
            return timestamp.timestamp()
        return item.get("_mtime", 0.0)

    records.sort(key=sort_key, reverse=True)
    return records[:limit]


def _load_memory_skills(root: Path) -> List[Dict]:
    skills: List[Dict] = []
    if not root.exists():
        return skills

    for skill_path in sorted(root.glob("*.json")):
        try:
            payload = json.loads(skill_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        criteria = payload.get("criteria", {})
        pass_rate = criteria.get("pass_rate")
        mastery = round(pass_rate * 100) if isinstance(pass_rate, (int, float)) else None
        name = payload.get("policy_template", {}).get("when", {}).get("objective") or payload.get(
            "skill_id", skill_path.stem
        )
        skills.append(
            {
                "name": name,
                "id": payload.get("skill_id", skill_path.stem),
                "status": payload.get("status", "unknown"),
                "mastery": mastery,
                "path": str(skill_path),
                "source": "memory",
            }
        )
    return skills


def _ledger_summary(workspace: Path) -> Optional[Dict]:
    candidates = [
        workspace / "memory" / "conversation_ledger.jsonl",
        workspace.parent / "ledger.jsonl",
        workspace.parent / "body" / "ledger" / "ledger.jsonl",
        workspace / "ledger.jsonl",
    ]
    for path in candidates:
        if not path.exists():
            continue
        count = 0
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        count += 1
        except Exception:
            count = 0
        return {
            "path": path,
            "count": count,
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
        }
    return None


def _status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status)
    label_map = {
        "DRAFT": "草案",
        "PROPOSED": "提案",
        "APPROVED": "已核准",
        "DEPRECATED": "停用",
        "PASS": "通過",
        "WARN": "注意",
        "FAIL": "失敗",
        "UNKNOWN": "未知",
    }
    return label_map.get(status_text.upper(), status_text)


def _gate_label(gate: Optional[str]) -> str:
    if not gate:
        return "未知"
    gate_text = str(gate)
    label_map = {
        "PASS": "可用",
        "WARN": "注意",
        "FAIL": "阻擋",
    }
    return label_map.get(gate_text.upper(), "未知")


LAYER_LABELS = {
    "seeds": "專案筆記",
    "user": "使用者記憶",
    "session": "會話記憶",
    "agent": "代理記憶",
}

MISTAKE_TYPE_OPTIONS = {
    "錯誤宣稱": "false_claim",
    "執行失敗": "execution_error",
    "上下文遺失": "context_loss",
    "安全風險": "security_risk",
    "其他": "other",
}


def _render_memory_cards(
    entries: List[Dict],
    section_title: str,
    pill_label: str,
    button_label: str,
    key_prefix: str,
    empty_text: str,
    show_gate: bool = False,
) -> None:
    st.markdown(f'<div class="ts-section-title">{section_title}</div>', unsafe_allow_html=True)
    if not entries:
        st.info(empty_text)
        return

    cols = st.columns(2)
    for idx, entry in enumerate(entries):
        updated = datetime.fromtimestamp(entry["time"]).strftime("%Y-%m-%d")
        title = entry["title"]
        label = title if len(title) <= 20 else title[:20] + "..."
        if show_gate:
            status = _gate_label(entry.get("gate", "unknown"))
            meta_primary = f"狀態: {status}"
        else:
            meta_primary = f"類型: {section_title}"
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="ts-card">
                  <div class="ts-pill">{pill_label}</div>
                  <h4>{label}</h4>
                  <p class="ts-muted">{meta_primary}</p>
                  <p class="ts-muted">最後更新: {updated}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(button_label, key=f"{key_prefix}_btn_{idx}"):
                st.session_state.selected_seed_path = entry["path"]


def render():
    """渲染記憶頁面"""

    st.markdown(
        """
        <div class="ts-hero">
          <h1>我的記憶</h1>
          <p>這是人工智慧的記憶庫，你可以幫它記住重要的事。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search = st.text_input("搜尋記憶", "", placeholder="輸入關鍵字")

    # ── 語魂核心概念引導 ─────────────────────────────────────────────
    workspace = Path(__file__).parent.parent.parent

    # 決定是否展開：沒有記憶資料時展開，有的話收合
    _has_any_data = any(
        (workspace / "memory" / layer).exists()
        and list((workspace / "memory" / layer).glob("*.json"))
        for layer in ("seeds", "user", "session", "agent")
    )

    with st.expander("語魂核心概念", expanded=not _has_any_data):
        # 七條公理
        axioms_path = workspace / "AXIOMS.json"
        if axioms_path.exists():
            try:
                import json as _json
                axioms_data = _json.loads(axioms_path.read_text(encoding="utf-8"))
                st.markdown("**七條公理** — AI 行為的不可變法則")
                ep = axioms_data.get("existential_principle", {})
                if ep:
                    st.caption(f"E0 · {ep.get('name_zh', '')} — {ep.get('statement_zh', '')}")
                for ax in axioms_data.get("axioms", []):
                    priority = ax.get("priority", "")
                    st.caption(
                        f"#{ax['id']} · {ax.get('name_zh', ax.get('name', ''))} "
                        f"[{priority}] — {ax.get('natural', '')}"
                    )
            except Exception:
                st.caption("AXIOMS.json 載入失敗")
        else:
            st.caption("AXIOMS.json 不存在")

        st.markdown("---")

        # 治理循環
        st.markdown("**治理循環** — 每次對話都經過的流程")
        st.code(
            "Session 開始          對話中             Session 結束\n"
            "┌──────────┐   ┌─────────────────┐   ┌──────────────┐\n"
            "│  Load    │──>│  Council 審議    │──>│   Commit     │\n"
            "│ 載入治理  │   │ 多角度內部討論    │   │  寫入治理記錄  │\n"
            "│ 狀態     │   │ Vow 誓言驗證     │   │  更新壓力指數  │\n"
            "└──────────┘   └─────────────────┘   └──────────────┘",
            language=None,
        )

        st.markdown("---")

        # 四層記憶說明
        st.markdown("**記憶分層** — AI 的四種記憶")
        st.markdown(
            "| 層 | 名稱 | 用途 |\n"
            "|---|---|---|\n"
            "| seeds | 專案筆記 | AI 對專案的理解和筆記 |\n"
            "| user | 使用者記憶 | 使用者告訴 AI 要記住的事 |\n"
            "| session | 會話記憶 | 單次對話中產生的臨時記憶 |\n"
            "| agent | 代理記憶 | AI 自己的學習和模式記錄 |"
        )

        st.caption("👉 用右邊的「新增記憶」表單幫 AI 記住重要的事，或在對話中說「記住 XXX」。")

    # ── 記憶資料載入 ─────────────────────────────────────────────────
    memory_skill_dir = workspace / "memory" / "skills"
    mistakes_dir = workspace / "memory" / "mistakes"
    patterns_dir = workspace / "memory" / "patterns"

    entries = list_memory_entries()
    memory_skills = _load_memory_skills(memory_skill_dir)
    spec_skills = list_skills()
    mistakes = _load_records(mistakes_dir, limit=8)
    patterns = _load_records(patterns_dir, limit=8)

    if memory_skills:
        skills = memory_skills
    else:
        skills = [
            {
                "name": skill["name"],
                "id": skill["name"],
                "status": "draft",
                "mastery": None,
                "path": skill["path"],
                "source": "spec",
            }
            for skill in spec_skills
        ]

    if search:
        keyword = search.strip().lower()
        entries = [s for s in entries if keyword in s["title"].lower()]
        skills = [s for s in skills if keyword in s["name"].lower() or keyword in s["id"].lower()]

    layered = {"seeds": [], "user": [], "session": [], "agent": []}
    for entry in entries:
        layer = entry.get("layer") or "seeds"
        if layer in layered:
            layered[layer].append(entry)
        else:
            layered.setdefault("seeds", []).append(entry)

    if "selected_seed_path" not in st.session_state:
        st.session_state.selected_seed_path = None
    if "selected_skill_path" not in st.session_state:
        st.session_state.selected_skill_path = None

    col_main, col_side = st.columns([2.2, 1], gap="large")

    with col_main:
        st.markdown('<div class="ts-section-title">技能</div>', unsafe_allow_html=True)
        if not skills:
            st.info("尚未發現技能，請在 `spec/skills` 新增 YAML。")
        else:
            cols = st.columns(2)
            for idx, skill in enumerate(skills):
                mastery_text = f"{skill['mastery']}%" if skill["mastery"] is not None else "未評估"
                source_label = "已學習" if skill["source"] == "memory" else "規格草案"
                status_label = _status_label(skill["status"])
                with cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div class="ts-card">
                          <div class="ts-pill">技能</div>
                          <h4>{skill['name']}</h4>
                          <p class="ts-muted">掌握度: {mastery_text}</p>
                          <p class="ts-muted">狀態: {status_label}</p>
                          <p class="ts-muted">來源: {source_label}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("查看技能", key=f"skill_btn_{idx}"):
                        st.session_state.selected_skill_path = skill["path"]

        _render_memory_cards(
            layered["seeds"],
            "專案筆記",
            "專案筆記",
            "查看筆記",
            "seed",
            "尚未發現專案筆記，可在「新增記憶」建立。",
            show_gate=True,
        )

        _render_memory_cards(
            layered["user"],
            "使用者記憶",
            "使用者記憶",
            "查看記憶",
            "user",
            "尚未發現使用者記憶。",
        )

        _render_memory_cards(
            layered["session"],
            "會話記憶",
            "會話記憶",
            "查看記憶",
            "session",
            "尚未發現會話記憶。",
        )

        _render_memory_cards(
            layered["agent"],
            "代理記憶",
            "代理記憶",
            "查看記憶",
            "agent",
            "尚未發現代理記憶。",
        )

        st.markdown('<div class="ts-section-title">對話記憶</div>', unsafe_allow_html=True)
        ledger_info = _ledger_summary(workspace)
        if ledger_info:
            st.markdown(
                f"""
                <div class="ts-card">
                  <div class="ts-pill">對話記憶</div>
                  <p class="ts-muted">記錄數量: {ledger_info['count']}</p>
                  <p class="ts-muted">最後更新: {ledger_info['updated_at']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("對話記憶會在工作區使用時自動累積。")

        st.markdown('<div class="ts-section-title">踩雷記錄</div>', unsafe_allow_html=True)
        if mistakes:
            rows = []
            for record in mistakes:
                timestamp = _safe_parse_iso(record.get("timestamp"))
                rows.append(
                    {
                        "時間": timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "",
                        "類型": record.get("type", "未分類"),
                        "摘要": (record.get("description") or "")[:40],
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("還沒有踩雷記錄。")

        st.markdown('<div class="ts-section-title">策略模式</div>', unsafe_allow_html=True)
        if patterns:
            rows = []
            for record in patterns:
                rate = record.get("success_rate")
                if isinstance(rate, (int, float)):
                    rate_text = f"{rate:.2f}"
                else:
                    rate_text = "未評估"
                rows.append(
                    {
                        "名稱": record.get("name") or record.get("pattern_id", "未命名"),
                        "使用時機": (record.get("when") or "")[:20],
                        "成功率": rate_text,
                        "最後使用": record.get("last_used") or "",
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("還沒有策略模式。")

    with col_side:
        st.markdown('<div class="ts-section-title">預覽</div>', unsafe_allow_html=True)

        seed_path = st.session_state.selected_seed_path
        if seed_path:
            seed = load_memory(seed_path)
            if seed:
                created_at = seed.get("created_at")
                gate = seed.get("gate_overall", "unknown")
                status = _gate_label(gate)
                st.markdown(
                    f"""
                    <div class="ts-card">
                      <div class="ts-pill">專案筆記</div>
                      <h4>{seed.get('content', {}).get('title', '未命名')}</h4>
                      <p class="ts-muted">狀態: {status}</p>
                      <p class="ts-muted">建立時間: {created_at}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area("內容", seed.get("content", {}).get("body", ""), height=180)

        skill_path = st.session_state.selected_skill_path
        if skill_path:
            skill_text = _preview_text(Path(skill_path))
            st.markdown(
                f"""
                <div class="ts-card">
                  <div class="ts-pill">技能檔案</div>
                  <p class="ts-muted">{Path(skill_path).name}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.text_area("內容", skill_text, height=180)

        st.markdown('<div class="ts-section-title">新增踩雷</div>', unsafe_allow_html=True)
        with st.form("mistake_form"):
            mistake_label = st.selectbox("類型", list(MISTAKE_TYPE_OPTIONS.keys()))
            mistake_type = MISTAKE_TYPE_OPTIONS[mistake_label]
            description = st.text_area("描述", "", height=80)
            context = st.text_area("情境", "", height=60)
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
                        context.strip(),
                        lesson.strip(),
                        prevention.strip(),
                    )
                    st.success(f"已記錄: mistake_{mistake_id}.json")

        st.markdown('<div class="ts-section-title">新增策略</div>', unsafe_allow_html=True)
        with st.form("pattern_form"):
            pattern_id = st.text_input("策略 ID（可留空）", "")
            name = st.text_input("名稱", "")
            when = st.text_input("使用時機", "")
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

        st.markdown('<div class="ts-section-title">新增記憶</div>', unsafe_allow_html=True)
        layer_choice = st.selectbox(
            "記憶層級",
            list(LAYER_LABELS.keys()),
            format_func=lambda key: LAYER_LABELS.get(key, key),
        )
        title = st.text_input("標題", "")
        body = st.text_area("內容", "", height=120)
        if st.button("儲存記憶"):
            if not body.strip():
                st.warning("請先輸入內容")
            else:
                saved_path = save_memory(body.strip(), title.strip() or None, layer_choice)
                st.success(f"已保存: {Path(saved_path).name}")
