"""
語魂 - 對話 + 技能 + 遠端畫面佔位
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import yaml
from components.council import render_council
from utils.llm import chat_with_council
from utils.search import build_search_context, default_search_roots


def _load_yaml(path: Path) -> Optional[Dict]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_skills(root: Path) -> List[Dict]:
    skills: List[Dict] = []
    if not root.exists():
        return skills

    for skill_path in sorted(root.glob("*.yaml")):
        payload = _load_yaml(skill_path)
        if not isinstance(payload, dict):
            continue
        skill = payload.get("skill", payload)
        gravity_wells = skill.get("gravity_wells", [])
        keywords = []
        for well in gravity_wells:
            keywords.extend(well.get("semantic", {}).get("keywords", []))
        skills.append(
            {
                "path": str(skill_path),
                "id": skill.get("id", skill_path.stem),
                "name": skill.get("name", skill_path.stem),
                "version": skill.get("version", "n/a"),
                "keywords": sorted(set(keywords)),
                "gravity_count": len(gravity_wells),
            }
        )
    return skills


def _load_open_source_apps(workspace: Path) -> List[Dict]:
    apps: List[Dict] = []
    dir_path = workspace / "spec" / "open_source_apps"
    file_path = workspace / "spec" / "open_source_apps.yaml"

    def add_app(payload: Dict, path: Optional[Path] = None) -> None:
        if not isinstance(payload, dict):
            return
        app = payload.get("app", payload)
        name = app.get("name") or app.get("title") or (path.stem if path else "untitled")
        repo = app.get("repo") or app.get("repo_url") or app.get("url") or ""
        description = app.get("description") or app.get("summary") or ""
        license_name = app.get("license") or "n/a"
        tags = app.get("tags") or app.get("keywords") or []
        if isinstance(tags, str):
            tags = [tags]
        apps.append(
            {
                "name": name,
                "repo": repo,
                "description": description,
                "license": license_name,
                "tags": tags,
                "path": str(path) if path else "",
            }
        )

    if dir_path.exists():
        for app_path in sorted(dir_path.glob("*.yaml")):
            payload = _load_yaml(app_path)
            if payload is None:
                continue
            add_app(payload, app_path)
    elif file_path.exists():
        payload = _load_yaml(file_path)
        if isinstance(payload, dict):
            items = payload.get("apps")
            if isinstance(items, list):
                for item in items:
                    add_app(item, file_path)
            else:
                add_app(payload, file_path)
        elif isinstance(payload, list):
            for item in payload:
                add_app(item, file_path)

    return apps


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _format_clock(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%H:%M:%S")
    except ValueError:
        return value


def _format_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _append_log(action: str, detail: str) -> None:
    if "remote_log" not in st.session_state:
        st.session_state.remote_log = []
    st.session_state.remote_log.insert(
        0,
        {
            "timestamp": _now_iso(),
            "action": action,
            "detail": detail,
        },
    )


def _runtime_dir(frontend_dir: Path) -> Path:
    env_dir = os.getenv("TS_RUNTIME_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    return frontend_dir.parent / "runtime"


def _ensure_runtime_dir(frontend_dir: Path) -> Path:
    runtime_dir = _runtime_dir(frontend_dir)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "screenshots").mkdir(parents=True, exist_ok=True)
    return runtime_dir


def _write_control_request(runtime_dir: Path, action: str, command: Optional[str] = None) -> Dict:
    payload = {
        "action": action,
        "command": command or "",
        "timestamp": _now_iso(),
    }
    request_path = runtime_dir / "control_request.json"
    request_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _read_control_result(runtime_dir: Path) -> Optional[Dict]:
    result_path = runtime_dir / "control_result.json"
    if not result_path.exists():
        return None
    try:
        return json.loads(result_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_screenshot_path(runtime_dir: Path, screenshot_path: Optional[str]) -> Optional[Path]:
    if not screenshot_path:
        return None
    candidate = Path(screenshot_path)
    if not candidate.is_absolute():
        candidate = runtime_dir / screenshot_path
        if not candidate.exists():
            candidate = runtime_dir.parent / screenshot_path
    return candidate if candidate.exists() else None


def _latest_screenshot(runtime_dir: Path) -> Optional[Path]:
    shots_dir = runtime_dir / "screenshots"
    if not shots_dir.exists():
        return None
    candidates = sorted(shots_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _control_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status)
    label_map = {
        "success": "成功",
        "failed": "失敗",
        "pending": "處理中",
        "unknown": "未知",
    }
    return label_map.get(status_text.lower(), status_text)


def _render_chat_panel(workspace: Path) -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "council_discussion" not in st.session_state:
        st.session_state.council_discussion = None
    if "selected_memories" not in st.session_state:
        st.session_state.selected_memories = []

    st.markdown('<div class="ts-section-title">對話區</div>', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.info("試試問我：\n- 幫我整理今天進度\n- 盤點需要優先處理的問題\n- 提供下一步行動建議")

    search_col1, search_col2 = st.columns(2)
    with search_col1:
        use_local_search = st.checkbox("本地檢索", value=False, key="skills_local_search")
    with search_col2:
        use_web_search = st.checkbox("網路檢索", value=False, key="skills_web_search")

    if st.session_state.selected_memories:
        st.caption("已加入對話記憶")
        for path in st.session_state.selected_memories:
            st.markdown(f"- {Path(path).name}")
        if st.button("清空引用", key="clear_skill_refs"):
            st.session_state.selected_memories = []

    if st.session_state.council_discussion:
        with st.expander("正在討論...", expanded=True):
            render_council(st.session_state.council_discussion)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    with st.form("skills_chat_form", clear_on_submit=True):
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
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("思考中..."):
            council, response = chat_with_council(
                user_input,
                st.session_state.selected_memories,
                retrieval_context=search_context,
            )
            st.session_state.council_discussion = council

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

        st.rerun()


def _render_skills_panel(skills: List[Dict]) -> None:
    st.markdown('<div class="ts-section-title">技能 / 技能庫</div>', unsafe_allow_html=True)
    st.caption("勾選技能後會帶入對話上下文")

    if not skills:
        st.info("尚未找到技能，請在 `spec/skills` 新增 YAML。")
        return

    search = st.text_input("搜尋技能", "", key="skills_search")
    filtered = skills
    if search:
        keyword = search.strip().lower()
        filtered = [s for s in skills if keyword in s["name"].lower() or keyword in s["id"].lower()]

    if not filtered:
        st.info("尚未找到符合搜尋的技能")
        return

    if "selected_memories" not in st.session_state:
        st.session_state.selected_memories = []

    for idx, skill in enumerate(filtered):
        keywords = ", ".join(skill["keywords"]) if skill["keywords"] else "無"
        with st.container():
            st.markdown(
                f"""
                <div class="ts-card" style="margin-bottom: 8px;">
                  <div class="ts-pill">技能</div>
                  <h4>{skill['name']}</h4>
                  <p class="ts-muted">識別碼: {skill['id']}</p>
                  <p class="ts-muted">版本: {skill['version']}</p>
                  <p class="ts-muted">語義重力井數: {skill['gravity_count']}</p>
                  <p class="ts-muted">關鍵詞: {keywords}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            selected = skill["path"] in st.session_state.selected_memories
            if st.checkbox("加入對話記憶", value=selected, key=f"skill_ref_{idx}"):
                if skill["path"] not in st.session_state.selected_memories:
                    st.session_state.selected_memories.append(skill["path"])
            else:
                if skill["path"] in st.session_state.selected_memories:
                    st.session_state.selected_memories.remove(skill["path"])

    st.caption(f"已加入對話記憶：{len(st.session_state.selected_memories)} 個")

    st.markdown('<div class="ts-section-title">技能庫快捷</div>', unsafe_allow_html=True)
    shortcut_count = min(4, len(filtered))
    cols = st.columns(shortcut_count)
    for idx in range(shortcut_count):
        skill = filtered[idx]
        with cols[idx]:
            if st.button(skill["name"], key=f"skill_quick_{idx}"):
                if skill["path"] not in st.session_state.selected_memories:
                    st.session_state.selected_memories.append(skill["path"])
                st.success(f"已加入 {skill['name']}")


def _render_open_source_panel(apps: List[Dict]) -> None:
    st.markdown('<div class="ts-section-title">開源應用分享區</div>', unsafe_allow_html=True)
    st.caption("分享可搭配使用的開源工具與範例")

    if not apps:
        st.info(
            "尚無分享，請在 `spec/open_source_apps.yaml` 或 `spec/open_source_apps/*.yaml` 填入"
        )
        return

    search = st.text_input("搜尋分享", "", key="oss_search")
    filtered = apps
    if search:
        keyword = search.strip().lower()
        filtered = [
            app
            for app in apps
            if keyword in app["name"].lower()
            or keyword in app.get("description", "").lower()
            or keyword in app.get("repo", "").lower()
            or any(keyword in tag.lower() for tag in app.get("tags", []))
        ]

    if not filtered:
        st.info("尚未找到分享")
        return

    for app in filtered:
        tags = " / ".join(app["tags"]) if app["tags"] else "無"
        repo = app.get("repo") or ""
        repo_html = f'<a href="{repo}" target="_blank">{repo}</a>' if repo else "尚未提供"
        description = app.get("description") or "尚未提供簡述"
        st.markdown(
            f"""
            <div class="ts-card" style="margin-bottom: 8px;">
              <div class="ts-pill">開源</div>
              <h4>{app['name']}</h4>
              <p class="ts-muted">授權: {app['license']}</p>
              <p class="ts-muted">標籤: {tags}</p>
              <p class="ts-muted">倉庫: {repo_html}</p>
              <p class="ts-muted">{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_remote_panel(frontend_dir: Path) -> None:
    st.markdown('<div class="ts-section-title">遠端畫面</div>', unsafe_allow_html=True)
    runtime_dir = _ensure_runtime_dir(frontend_dir)

    if "remote_url" not in st.session_state:
        st.session_state.remote_url = ""
    if "remote_status" not in st.session_state:
        st.session_state.remote_status = "disconnected"
    if "remote_log" not in st.session_state:
        st.session_state.remote_log = []
    if "remote_command" not in st.session_state:
        st.session_state.remote_command = ""

    st.session_state.remote_url = st.text_input("遠端來源 (可選)", st.session_state.remote_url)
    status_label = {
        "disconnected": "未連線",
        "connected": "已連線",
        "paused": "已暫停",
        "stopped": "已停止",
        "pending": "處理中",
    }.get(st.session_state.remote_status, st.session_state.remote_status)
    st.caption(f"目前狀態: {status_label}")

    st.markdown('<div class="ts-section-title">控制指令</div>', unsafe_allow_html=True)
    st.session_state.remote_command = st.text_area(
        "輸入指令", st.session_state.remote_command, height=90
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("連接"):
            if st.session_state.remote_url:
                _write_control_request(runtime_dir, "connect")
                st.success("已送出連接請求")
                st.session_state.remote_status = "connected"
                _append_log("連接", st.session_state.remote_url)
            else:
                st.warning("請先輸入遠端來源")
    with col2:
        if st.button("截圖"):
            _write_control_request(runtime_dir, "screenshot")
            st.info("已送出截圖請求")
            _append_log("截圖", "待處理")
            st.session_state.remote_status = "pending"
    with col3:
        if st.button("執行"):
            command = st.session_state.remote_command.strip()
            _write_control_request(runtime_dir, "execute", command=command)
            st.info("已送出執行請求")
            _append_log("執行", command or "-")
            st.session_state.remote_status = "pending"

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("暫停"):
            st.info("暫停功能待接後端")
            _write_control_request(runtime_dir, "pause")
            _append_log("暫停", "-")
            st.session_state.remote_status = "paused"
    with col5:
        if st.button("恢復"):
            st.info("恢復功能待接後端")
            _write_control_request(runtime_dir, "resume")
            _append_log("恢復", "-")
            st.session_state.remote_status = "connected"
    with col6:
        if st.button("停止"):
            st.info("停止功能待接後端")
            _write_control_request(runtime_dir, "stop")
            _append_log("停止", "-")
            st.session_state.remote_status = "stopped"

    if st.session_state.remote_url:
        st.components.v1.iframe(st.session_state.remote_url, height=360, scrolling=True)
    else:
        st.markdown(
            """
            <div class="ts-card" style="
                height: 360px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                gap: 12px;
            ">
              <div class="ts-pill">遠端畫面</div>
              <div class="ts-muted">尚未連線，畫面佔位</div>
              <div style="
                width: 100%;
                height: 220px;
                border-radius: 12px;
                border: 1px dashed var(--ts-border);
                background: rgba(31, 28, 22, 0.04);
              "></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    result = _read_control_result(runtime_dir)
    screenshot_path = result.get("screenshot_path") if result else None
    preview_path = _resolve_screenshot_path(runtime_dir, screenshot_path) or _latest_screenshot(
        runtime_dir
    )

    st.markdown('<div class="ts-section-title">截圖預覽</div>', unsafe_allow_html=True)
    st.caption("目前以截圖方式預覽，如需即時畫面請接 WebRTC/VNC。")
    if preview_path:
        caption = screenshot_path or preview_path.name
        st.image(str(preview_path), caption=caption)
        st.caption(f"最後更新: {_format_mtime(preview_path)}")
    else:
        st.info("尚無截圖，請按「截圖」取得。")

    st.markdown('<div class="ts-section-title">控制記錄</div>', unsafe_allow_html=True)
    if st.session_state.remote_log:
        for item in st.session_state.remote_log[:6]:
            timestamp = item.get("timestamp") or item.get("time", "")
            st.markdown(f"- {_format_clock(timestamp)} · {item['action']} · {item['detail']}")
    else:
        st.caption("尚無控制記錄")

    if st.button("刷新結果"):
        st.info("已刷新控制結果")

    if result:
        status = result.get("status")
        status_text = _control_status_label(status)
        log = result.get("log", "-")
        result_ts = result.get("timestamp")
        result_path = runtime_dir / "control_result.json"
        updated_at = datetime.fromtimestamp(result_path.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        st.markdown('<div class="ts-section-title">控制結果</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ts-card">
              <div class="ts-pill">結果</div>
              <p class="ts-muted">狀態: {status_text}</p>
              <p class="ts-muted">結果時間: {_format_clock(result_ts) if result_ts else updated_at}</p>
              <p class="ts-muted">訊息: {log}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render() -> None:
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(
        """
        <div class="ts-hero">
          <h1>技能控制台</h1>
          <p>管理 AI 技能、瀏覽開源工具分享，並連接遠端畫面控制。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"現在時間: {now_text}")

    workspace = Path(__file__).parent.parent.parent
    skills = _load_skills(workspace / "spec" / "skills")
    open_source_apps = _load_open_source_apps(workspace)

    col_left, col_right = st.columns([2.2, 1], gap="large")

    with col_left:
        _render_chat_panel(workspace)

    frontend_dir = Path(__file__).parent.parent
    with col_right:
        tab_skills, tab_open, tab_remote = st.tabs(["技能", "分享", "遠端"])
        with tab_skills:
            _render_skills_panel(skills)
        with tab_open:
            _render_open_source_panel(open_source_apps)
        with tab_remote:
            _render_remote_panel(frontend_dir)
