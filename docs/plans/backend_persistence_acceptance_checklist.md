# Backend Persistence 驗收清單

最後更新：2026-02-12

## 0. 前置條件

- [ ] Supabase SQL 已執行：`docs/plans/supabase_migration.sql`
- [ ] Render 已設定 `SUPABASE_URL`
- [ ] Render 已設定 `SUPABASE_KEY`（service role）
- [ ] 後端已重啟

## 1. 一鍵驗收（建議）

執行：

```bash
python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com
```

可選：

```bash
python scripts/verify_backend_persistence.py \
  --base https://tonesoul52.onrender.com \
  --delete-after
```

通過標準：

- [ ] `GET /api/health` 回傳 `persistence.enabled=true`
- [ ] `POST /api/conversation` 可建立 `conversation_id`
- [ ] `POST /api/chat` 成功並有 `response`
- [ ] `GET /api/conversations/<id>` 可讀到 `user` + `assistant` 訊息
- [ ] `GET /api/audit-logs` 成功回傳
- [ ] `GET /api/status` 回傳計數欄位
- [ ] `GET /api/memories` 成功回傳

## 2. 手動驗收（必要時）

### 2.1 健康檢查

```bash
curl https://tonesoul52.onrender.com/api/health
```

預期：

- [ ] `status = ok`
- [ ] `persistence.enabled = true`

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

- [ ] `/api/conversations/<conversation_id>` 含 `messages`
- [ ] `/api/audit-logs` 有最新記錄或 `total` 可讀
- [ ] `/api/status` 內含 `memory_count`、`conversation_count`、`audit_log_count`

