# CODEX_TASK — ToneSoul 後端下一步任務

> **上次更新**：2026-02-12T01:18 (UTC+8)
> **目前狀態**：Supabase 持久化已上線 ✅，需要繼續完成 Council Playground 改版和新 API 路由

---

## 已完成（不需再做）

### ✅ 1. Supabase 資料庫建表
- Supabase Project：`sjtoyjsnykstclcbktoo`
- Region：`ap-northeast-2`（首爾）
- 已建立 4 張表：`soul_memories`、`conversations`、`messages`、`audit_logs`
- RLS 已開，Service Role 有完整存取 Policy
- SQL 在 `docs/plans/supabase_migration.sql`

### ✅ 2. SupabasePersistence 持久化模組
- 檔案：`tonesoul/supabase_persistence.py`（458 行）
- 功能：
  - `SupabasePersistence.from_env()` — 從環境變數自動初始化
  - `enabled` property — 判斷 Supabase 是否已設定
  - `status_dict()` — 回傳連線狀態 dict
  - `ensure_conversation()` — 建立/查找對話
  - `record_chat_exchange()` — 儲存 user+assistant 訊息到 messages 表
  - `record_chat_audit()` — 儲存 Council verdict 到 audit_logs 表
  - `record_consent()` / `withdraw_consent()` — 同意書管理
  - `record_session_report()` — 儲存 session 分析報告
- 設計：best-effort（Supabase 不可用時不阻塞使用者流程）
- 用 `requests` 直接呼叫 Supabase REST API，不依賴 `supabase-py` SDK

### ✅ 3. server.py 已整合 Persistence
- 檔案：`apps/api/server.py`（565 行）
- `from tonesoul.supabase_persistence import SupabasePersistence`（Line 22）
- `supabase_persistence = SupabasePersistence.from_env()`（Line 42）
- 已整合的路由：
  - `/api/health` — 回傳 `persistence` 狀態
  - `/api/conversation` — 建立時寫入 Supabase
  - `/api/consent` — 建立/撤銷同意時寫入
  - `/api/session-report` — 分析報告寫入
  - `/api/chat` — 聊天完後寫入訊息 + audit log

### ✅ 4. Render 部署已完成
- 環境變數 `SUPABASE_URL` 和 `SUPABASE_KEY` 已設定
- 已部署，`GET /api/health` 回傳：
```json
{
  "status": "ok",
  "version": "0.6.0",
  "persistence": {
    "configured": true,
    "enabled": true,
    "provider": "supabase",
    "last_error": null
  }
}
```

---

## 🔜 待完成任務

### Task A：新增讀取類 API Routes

目前 server.py 只有「寫入」Supabase 的邏輯，缺少「讀取」的 API。

需要在 `apps/api/server.py` 新增以下路由：

#### A1. `GET /api/conversations`
列出所有對話（分頁），從 Supabase `conversations` 表讀取。
```
GET /api/conversations?limit=20&offset=0
Response: { "conversations": [...], "total": 42 }
```

#### A2. `GET /api/conversations/<id>`
取得單一對話及其所有訊息。從 `conversations` + `messages` 表 JOIN 讀取。
```
GET /api/conversations/conv_abc123
Response: { "conversation": { "id": "...", "title": "...", "messages": [...] } }
```

#### A3. `DELETE /api/conversations/<id>`
刪除對話及相關訊息（CASCADE 已設定在 DB 層）。

#### A4. `GET /api/audit-logs`
取得審計日誌（分頁），從 `audit_logs` 表讀取。
```
GET /api/audit-logs?limit=20&offset=0
Response: { "logs": [...], "total": 15 }
```

#### A5. `GET /api/status`
系統狀態總覽：DB 連線、LLM 狀態、記憶數量。
```
GET /api/status
Response: {
  "persistence": { "enabled": true, "provider": "supabase" },
  "llm_backend": "Gemini API",
  "memory_count": 5,
  "conversation_count": 12,
  "audit_log_count": 30
}
```

#### A6. 修改 `GET /api/memories`
目前 `/api/memories` 讀的是本地 `self_journal.jsonl`（Line 292-295）。
應改為：如果 `supabase_persistence.enabled`，從 Supabase `soul_memories` 表讀取。

**實作方式**：
在 `SupabasePersistence` 類裡新增讀取方法：
- `list_conversations(limit, offset)` → 查 conversations 表
- `get_conversation(id)` → 查 conversations + messages
- `delete_conversation(id)` → 刪除 conversations（CASCADE 會清 messages）
- `list_audit_logs(limit, offset)` → 查 audit_logs 表
- `list_memories(limit)` → 查 soul_memories 表
- `get_counts()` → 各表的 COUNT

---

### Task B：Council Playground 介面改版

目前的 Council Playground（Render 首頁 `https://tonesoul52.onrender.com/`）很基本。

需要改版以下檔案：

#### [MODIFY] `apps/council-playground/index.html`

改為有清楚說明的 Landing Page：

1. **Hero Section**
   - 語魂 ToneSoul 標題 + 說明
   - 核心方程 `γ·Honesty > β·Helpfulness`
   - 簡述這是什麼系統

2. **系統狀態卡片**（呼叫 `GET /api/status`）
   - 即時顯示：DB 連線狀態、LLM 後端、記憶數量、對話數量、審計日誌數量
   - 用顏色區分：綠色=正常、紅色=異常

3. **功能區塊**（卡片式導航）
   - 🧪 **Council 審議** — 測試 AI 輸出是否通過治理門控
   - 💬 **Chat** — 與語魂對話（連結到 `/chat`）
   - 📖 **記憶日誌** — 查看 AI 的決策記憶（呼叫 `/api/memories`）
   - 💭 **自我反思** — 查看記憶整合與模式分析（呼叫 `/api/consolidate`）
   - 📊 **審計日誌** — 查看 Gate 決策歷史（呼叫 `/api/audit-logs`）
   - 📋 **對話歷史** — 查看所有對話（呼叫 `/api/conversations`）

4. **API 文件區**
   - 列出所有 API endpoint 及使用範例
   - 用表格格式，包含 Method、Route、說明

5. **Footer**
   - GitHub 連結：https://github.com/Fan1234-1/tonesoul52
   - 版本號
   - © 2026

#### [MODIFY] `apps/council-playground/style.css`

更新為現代深色主題設計（目前已有一些樣式），確保：
- 深色背景（#0f0f1a 或類似）
- 漸層色標題
- 卡片有質感（glassmorphism 效果）
- 響應式布局
- 狀態指示燈（綠/紅圓點）
- 與前端站 (tonesoul52.vercel.app) 風格統一

#### [MODIFY] `apps/council-playground/app.js`

新增：
- `fetchStatus()` — 呼叫 `/api/status` 更新系統狀態卡片
- `fetchAuditLogs()` — 呼叫 `/api/audit-logs` 顯示審計日誌
- `fetchConversations()` — 呼叫 `/api/conversations` 顯示對話列表
- 頁面載入時自動呼叫 `fetchStatus()`
- 修改現有 `fetchMemories()` 和 `fetchConsolidation()` 確保正確顯示

---

### Task C：測試

#### 單元測試
- 新增 `tests/test_supabase_persistence.py` — 測試 SupabasePersistence 類的所有方法
- 新增 `tests/test_server_persistence.py` — 測試 server.py 新增的 API routes

#### 整合驗證
部署後驗證以下 API：
```bash
# 1. 建立對話
curl -X POST https://tonesoul52.onrender.com/api/conversation \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session"}'

# 2. 發送聊天（會自動寫入 DB）
curl -X POST https://tonesoul52.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "conv_xxx"}'

# 3. 驗證對話歷史
curl https://tonesoul52.onrender.com/api/conversations

# 4. 驗證審計日誌
curl https://tonesoul52.onrender.com/api/audit-logs

# 5. 驗證系統狀態
curl https://tonesoul52.onrender.com/api/status

# 6. 驗證記憶
curl https://tonesoul52.onrender.com/api/memories
```

---

## 重要參考檔案

| 檔案 | 說明 |
|------|------|
| `tonesoul/supabase_persistence.py` | Supabase 持久化模組（已完成） |
| `apps/api/server.py` | Flask 後端主程式 |
| `apps/council-playground/index.html` | Playground 前端 HTML |
| `apps/council-playground/style.css` | Playground 前端樣式 |
| `apps/council-playground/app.js` | Playground 前端邏輯 |
| `apps/council-playground/chat.html` | Chat 頁面 |
| `tonesoul/memory/soul_db.py` | SoulDB Protocol 定義 |
| `tonesoul/council/self_journal.py` | 自我記憶日誌模組 |
| `docs/plans/supabase_migration.sql` | Supabase 表結構 |

## 環境變數

以下已設定在 Render：
- `SUPABASE_URL` = `https://sjtoyjsnykstclcbktoo.supabase.co`
- `SUPABASE_KEY` = （service_role key，已設定）
- `GEMINI_API_KEY` = （Gemini API key，建議）
- `GOOGLE_API_KEY` = （相容別名，可與 `GEMINI_API_KEY` 擇一）
