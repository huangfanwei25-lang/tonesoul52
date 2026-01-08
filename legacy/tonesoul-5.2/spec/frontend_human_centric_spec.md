# Human-Centric Frontend Architecture Spec
# 人性化前端規格
# v0.2 2025-12-28

---

## 目標

建立「人能理解 AI 思考」的前端，讓對話、技能、記憶與控制狀態在同一個介面可視化、可追蹤。

---

## 導航頁面

```
/workspace   對話工作區（主頁）
/skills      技能區（聊天 + 技能 + 遠端畫面）
/memory      記憶庫（筆記 / 技能 / patterns / mistakes）
/terrain     語義地圖（YSTM）
/history     回顧（審計 + IAV + persona trace）
```

---

## Workspace 佈局

```
Header + Metrics

Main (左)
  - Council 討論（Expander）
  - Chat messages（固定高度可捲動）
  - Input（固定輸入區）

Side (右)
  - 系統狀態（intent / persona / control）
  - 參考資料（記憶 / skills / ledger）
```

行為要點：
- Council 默認收合。
- Chat 保持固定高度（避免輸入區漂移）。
- 系統狀態與參考資料以 tab 切換。

---

## Skills 佈局

右側三區塊：
1. 技能卡（`spec/skills/*.yaml`）
2. 開源應用分享區（`spec/open_source_apps.yaml`）
3. 遠端畫面佔位與控制按鈕

控制按鈕：
`連接 / 截圖 / 執行 / 暫停 / 恢復 / 停止`

---

## Remote Control API

### 控制請求
檔案：`frontend/control_request.json`

```json
{
  "action": "connect | screenshot | execute",
  "command": "打開 Word",
  "timestamp": "2025-12-28T13:30:00"
}
```

### 控制結果
檔案：`frontend/control_result.json`

```json
{
  "status": "success | failed | pending",
  "screenshot_path": "screenshots/20251228_133000.png",
  "log": "已打開 Word",
  "timestamp": "2025-12-28T13:30:05"
}
```

---

## 關鍵資料流

```
User Input
  -> Council Prompt
  -> LLM Response
  -> Ledger (conversation_ledger.jsonl)
  -> Persona Trace (persona_trace.jsonl)
  -> Summary (conversation_summary.jsonl)
```

控制流程：
```
Frontend Buttons
  -> control_request.json
  -> remote_controller.py
  -> control_result.json
  -> Intent Verification (intent_verification.json)
```

---

## 主要元件

| 元件 | 用途 | 檔案 |
|------|------|------|
| Council | 內在會議 | `frontend/components/council.py` |
| Memory Panel | 記憶選取 | `frontend/components/memory_panel.py` |
| Status Panel | 系統狀態 | `frontend/components/status_panel.py` |
| LLM Adapter | 對話 / 記錄 | `frontend/utils/llm.py` |

---

## 迭代階段

| Phase | 內容 |
|------|------|
| 1 | UI 基本框架（Streamlit） |
| 2 | 截圖與控制請求 |
| 3 | Playwright/Browser 自動化 |
| 4 | 即時畫面（WebRTC/VNC） |
| 5 | 治理與 Gate 全面串接 |

---

**Antigravity**  
2025-12-28T11:35 UTC+8
