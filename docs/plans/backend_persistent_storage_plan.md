# Backend Persistent Storage Plan

> Scope: `apps/api` + Supabase persistence wiring  
> Owner: Codex  
> Last Updated: 2026-02-11

## Task 1: 持久化架構與開關
- [x] 新增 Supabase persistence adapter（HTTP REST，無額外 SDK 相依）
- [x] 以環境變數控制啟用：`SUPABASE_URL` + `SUPABASE_KEY`
- [x] 保留 fail-open 行為：未設定或連線失敗時 API 不中斷
**成功標準**: 後端可在「啟用 Supabase」與「純本地」兩種模式下都可運行。

## Task 2: Conversation / Consent 持久化
- [x] `/api/conversation` 建立對應 conversation 記錄（外部 ID 與 DB UUID 對應）
- [x] `/api/consent` 寫入 consent 事件
- [x] `/api/consent/<session_id>` 觸發資料刪除流程（best-effort）
**成功標準**: Conversation 與 consent 生命週期都有持久化事件可追蹤。

## Task 3: Chat 訊息與審計落地
- [x] `/api/chat` 將 user/assistant turn 寫入 `messages`
- [x] `/api/chat` 將 verdict 摘要寫入 `audit_logs`
- [x] 保持既有 API 回傳契約不變
**成功標準**: 每次 chat 可在 DB 追溯到訊息與審計摘要。

## Task 4: Session Report 與記憶事件
- [x] `/api/session-report` 將報告摘要寫入持久層
- [x] 補充 `soul_memories` 事件（consent/session mapping/report）
- [x] `/api/health` 回報 persistence 狀態
**成功標準**: 報告與會話生命週期均可由 `/api/health` + DB 事件確認。

## Task 5: 測試與部署交接
- [x] 新增 persistence 模組單元測試（mock HTTP client）
- [x] 新增 API 與 persistence wiring 測試
- [x] 補充部署環境變數說明（Render/Supabase）
**成功標準**: 相關 pytest 通過，部署方可依文件完成配置。
