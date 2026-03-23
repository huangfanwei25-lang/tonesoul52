# Backend Persistent Storage Plan

> Purpose: define the persistent-storage integration tasks for `apps/api`, Supabase, and the related acceptance path.
> Last Updated: 2026-03-23

> 範圍：`apps/api` + Supabase 持久化整合  
> 負責：Codex  
> 最後更新：2026-02-12

## Task 1：建立 Supabase Persistence 介面
- [x] 新增 Supabase persistence adapter（走 HTTP REST，不綁 SDK）
- [x] 以環境變數控制啟用：`SUPABASE_URL` + `SUPABASE_KEY`
- [x] 採 fail-open 策略（Supabase 異常不阻塞 API 主流程）

**成功標準**：在 Supabase 不可用時，API 仍可回應，並透過 `status_dict()` 暴露連線狀態。

## Task 2：Conversation / Consent 寫入整合
- [x] `/api/conversation` 建立對話時同步寫入 `conversations`
- [x] `/api/consent` 建立同意時寫入 `soul_memories`
- [x] `/api/consent/<session_id>` 撤回同意時執行 best-effort 清理

**成功標準**：對話與 consent 事件可追蹤，且撤回流程有刪除報告。

## Task 3：Chat / Audit 寫入整合
- [x] `/api/chat` 儲存 user + assistant 訊息到 `messages`
- [x] `/api/chat` 將治理 verdict 寫入 `audit_logs`
- [x] 保持 chat API 回應契約不變

**成功標準**：一次 chat 後可在資料庫看到訊息與對應審計紀錄。

## Task 4：Session Report 與 Health 狀態
- [x] `/api/session-report` 可寫入 `soul_memories`
- [x] 建立 session / consent / conversation 的關聯記錄
- [x] `/api/health` 回傳 `persistence` 狀態資訊

**成功標準**：`/api/health` 可明確看到 `persistence.enabled=true`，且 session report 可持久化。

## Task 5：讀取 API + 測試驗證
- [x] 新增讀取 API：`/api/conversations`、`/api/conversations/<id>`、`/api/audit-logs`、`/api/status`
- [x] `/api/memories` 在 persistence 啟用時改讀 `soul_memories`
- [x] 補齊單元/路由測試（`tests/test_supabase_persistence.py`、`tests/test_server_persistence.py`）

**成功標準**：新增 API 路由測試全綠，行為與 `CODEX_TASK.md` 契約一致。

## 外部部署步驟（手動）
1. 在 Supabase SQL Editor 執行 `docs/plans/supabase_migration.sql`
2. 在 Render 設定 `SUPABASE_URL`、`SUPABASE_KEY`（service role）
3. 重啟後端服務
4. 呼叫 `GET /api/health` 確認 `persistence.enabled=true`
