# Backend Persistence 驗收清單

> Purpose: checklist and command reference for validating deployed backend persistence behavior and health signals.
> Last Updated: 2026-03-23

最後更新：2026-02-14

## 近期執行紀錄（2026-02-14）

- 已執行：
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com`
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com --timeout 40`
- 結果：驗收腳本完整通過（exit code 0），`/api/health`、`/api/conversation`、`/api/chat`、`/api/conversations/<id>`、`/api/audit-logs`、`/api/status`、`/api/memories` 全部成功回應。
- 備註：本次驗收確認 `persistence.enabled=true` 且 provider=`supabase`，阻塞解除。

## 0. 前置條件

- [x] Supabase SQL 已執行：`docs/plans/supabase_migration.sql`（由寫入與讀取驗收結果反證）
- [x] Render 已設定 `SUPABASE_URL`（`/api/health` 回傳 `persistence.configured=true`）
- [x] Render 已設定 `SUPABASE_KEY`（service role）（`/api/health` 回傳 `persistence.enabled=true`）
- [x] 後端已重啟（本次遠端驗收可正常建立與讀取資料）

## 1. 一鍵驗收（建議）

執行：

```bash
python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com
```

若有設定 `TONESOUL_READ_API_TOKEN`（讀取路由保護）：

```bash
python scripts/verify_backend_persistence.py \
  --base https://tonesoul52.onrender.com \
  --read-token "<TONESOUL_READ_API_TOKEN>"
```

可選：

```bash
python scripts/verify_backend_persistence.py \
  --base https://tonesoul52.onrender.com \
  --delete-after
```

通過標準：

- [x] `GET /api/health` 回傳 `persistence.enabled=true`
- [x] `POST /api/conversation` 可建立 `conversation_id`
- [x] `POST /api/chat` 成功並有 `response`
- [x] `GET /api/conversations/<id>` 可讀到 `user` + `assistant` 訊息
- [x] `GET /api/audit-logs` 成功回傳
- [x] `GET /api/status` 回傳計數欄位
- [x] `GET /api/memories` 成功回傳

## 2. 手動驗收（必要時）

### 2.1 健康檢查

```bash
curl https://tonesoul52.onrender.com/api/health
```

預期：

- [x] `status = ok`
- [x] `persistence.enabled = true`

### 2.2 建立對話

```bash
curl -X POST https://tonesoul52.onrender.com/api/conversation \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"manual-check\"}"
```

### 2.3 發送聊天

將上一步回傳的 `conversation_id` 代入：

```bash
curl -X POST https://tonesoul52.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"manual check\",\"conversation_id\":\"<conversation_id>\",\"session_id\":\"manual-check\",\"history\":[],\"full_analysis\":false}"
```

### 2.4 讀取驗證

```bash
curl https://tonesoul52.onrender.com/api/conversations
curl https://tonesoul52.onrender.com/api/conversations/<conversation_id>
curl https://tonesoul52.onrender.com/api/audit-logs
curl https://tonesoul52.onrender.com/api/status
curl https://tonesoul52.onrender.com/api/memories
```

預期：

- [x] `/api/conversations/<conversation_id>` 含 `messages`
- [x] `/api/audit-logs` 有最新記錄或 `total` 可讀
- [x] `/api/status` 內含 `memory_count`、`conversation_count`、`audit_log_count`
