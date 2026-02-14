# 對話 UI 改善規格
# Chat UI Improvement Specification
# 2025-12-29

---

## 目標

- 介面體驗接近 ChatGPT / Gemini：視覺乾淨、輸入區固定、訊息流暢。
- Council 討論可折疊，不干擾主對話。
- 右側維持參考資料與狀態，不影響對話閱讀。

---

## 影響範圍

`C:\Users\user\Desktop\倉庫\apps\dashboard\frontend\pages\workspace.py`

---

## 核心調整

1. 對話區固定高度、可捲動。
2. Council 區塊使用展開區，預設收合。
3. 輸入區固定在底部，避免跳動與定位問題。

---

## UI 佈局示意

```
[Header]
  - 對話工作區
  - 簡短說明

[Metrics]
  - 專案筆記 / 技能庫 / 最近決策

[Main | Side]
  Main (左)
    - Council (Expander)
    - Chat Messages (fixed height)
    - Input Form (text area + send button)

  Side (右)
    - 系統狀態
    - 參考資料
```

---

## 實作指引

### 1) 對話區固定高度

```python
chat_container = st.container(height=400)
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
```

### 2) Council 展開區

```python
if st.session_state.council_discussion:
    with st.expander("🧠 我在想...", expanded=False):
        render_council(st.session_state.council_discussion)
```

### 3) 輸入區固定在底部

```python
with st.form("workspace_chat_form", clear_on_submit=True):
    user_input = st.text_area("輸入訊息", "", height=90)
    submitted = st.form_submit_button("送出")
```

---

## workspace.py 參考實作（摘要）

```python
def render():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "council_discussion" not in st.session_state:
        st.session_state.council_discussion = None

    col_main, col_side = st.columns([3, 1.1], gap="large")

    with col_main:
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

    with col_side:
        tab_status, tab_memory = st.tabs(["系統狀態", "參考資料"])
        with tab_status:
            render_status_panel(workspace)
        with tab_memory:
            render_memory_panel()
```

---

## 驗收項目

- [x] Council 區塊可收合。
- [x] 對話區固定高度、可捲動。
- [x] 輸入區可固定在下方，不遮擋訊息。
- [x] 右側狀態/參考資料不影響對話區。

驗收完成時間：2026-02-14（依 `apps/dashboard/frontend/pages/workspace.py` 實作）

---

## 相關檔案

- `frontend/pages/workspace.py`
- `frontend/components/council.py`
- `frontend/components/status_panel.py`
- `frontend/components/memory_panel.py`
- `frontend/utils/llm.py`

---

**Antigravity**  
2025-12-29T14:48 UTC+8
