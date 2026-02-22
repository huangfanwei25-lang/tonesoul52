# Codex Task: Flask → Vercel Serverless Migration

> **目標**: 把 `apps/api/server.py` (Flask, 1741 行) 遷移到 `apps/web/src/app/api/` (Vercel Python Serverless Functions)，讓前端和後端都在 Vercel 上運行，不再依賴 Render。

## 背景

- 前端: Next.js 16 on Vercel (`tonesoul52-one.vercel.app`) — ✅ 運行中
- 後端: Flask on Render (`tonesoul52.onrender.com`) — ❌ 免費額度用完，已死
- 結果: 前端白頁 (無法連線後端)

## 方案

Vercel 支援 Python Serverless Functions。把 Flask 的 route handler 拆成獨立的 `.py` 檔案放在 `apps/web/api/` 下。

### 遷移對應表

| Flask Route | Vercel File | 優先級 |
|-------------|------------|:------:|
| `POST /api/chat` | `api/chat.py` | 🔴 P0 |
| `POST /api/validate` | `api/validate.py` | 🔴 P0 |
| `GET /api/health` | `api/health.py` | 🟢 P2 |
| `GET /api/status` | `api/status.py` | 🟢 P2 |
| `GET /api/memories` | `api/memories.py` | 🟡 P1 |
| `POST /api/conversations` | `api/conversations/index.py` | 🟡 P1 |
| `GET /api/conversations` | `api/conversations/index.py` | 🟡 P1 |
| `GET /api/conversations/<id>` | `api/conversations/[id].py` | 🟡 P1 |
| `DELETE /api/conversations/<id>` | `api/conversations/[id].py` | 🟡 P1 |
| `POST /api/consent` | `api/consent.py` | 🟢 P2 |
| `GET /api/audit-logs` | `api/audit-logs.py` | 🟢 P2 |
| `GET /api/evolution/summary` | `api/evolution/summary.py` | 🟢 P2 |
| `GET /api/evolution/patterns` | `api/evolution/patterns.py` | 🟢 P2 |
| `POST /api/evolution/distill` | `api/evolution/distill.py` | 🟢 P2 |
| `POST /api/session-report` | `api/session-report.py` | 🟢 P2 |
| `GET /api/llm/models` | `api/llm/models.py` | 🟢 P2 |
| `POST /api/llm/switch` | `api/llm/switch.py` | 🟢 P2 |

### Vercel Python Function 格式

每個檔案的基本結構：

```python
# api/health.py
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
```

### 共用邏輯

從 `server.py` 抽出以下共用模組到 `api/_shared/`：

- `api/_shared/auth.py` — API token 驗證 + rate limiting
- `api/_shared/db.py` — SoulDB / Supabase 連線
- `api/_shared/llm.py` — LLM client 初始化 (Ollama/Gemini)
- `api/_shared/council.py` — PreOutputCouncil wrapper
- `api/_shared/utils.py` — 通用工具函式

### 環境變數 (Vercel Dashboard 設定)

```
TONESOUL_READ_API_TOKEN=<generate new>
LLM_BACKEND=gemini
GEMINI_API_KEY=<user's key>
SUPABASE_URL=<existing>
SUPABASE_KEY=<existing>
```

### 前端修正

`apps/web/.env.local` 改成：
```diff
-TONESOUL_BACKEND_URL="https://tonesoul52.onrender.com"
+TONESOUL_BACKEND_URL=""
```
（空字串 = 使用相對路徑 `/api/xxx`，自動指向同域名的 Vercel Functions）

## 執行步驟

1. **P0 先行**: 只遷移 `/api/chat` 和 `/api/validate`，確認 Chat 能動
2. **P1 跟進**: 遷移 conversations CRUD，確認對話歷史能存取
3. **P2 收尾**: 遷移剩餘的 evolution / audit / llm 端點
4. **清理**: 移除 `.env.local` 中的 Render URL，更新 `vercel.json`

## 驗證

- [ ] `https://tonesoul52-one.vercel.app/` 不再白頁
- [ ] Chat 能正常對話
- [ ] Council Chamber 能顯示三視角審議結果
- [ ] 對話歷史能正常儲存和讀取

### 2026-02-22 進度（程式已修，待部署驗收）

- 已完成 same-origin backend 基礎：`apps/web/src/app/api/_shared/backendConfig.ts` 會在 Vercel 無外部 backend URL 時改走 `/api/_backend` 前綴。
- 已新增 Python alias 入口：`apps/web/api/_backend/**`（含 WSGI prefix-strip middleware），避免 `/api/chat -> /api/chat` 遞迴。
- 已補齊缺漏路由：`/api/health`、`/api/conversations`、`/api/conversations/[id]`。
- 已通過相關測試：`apiRoutes.chatTransport`、`apiRoutes.transportFallback`、`apiRoutes.backendHealth`。
- 尚未在 `https://tonesoul52-one.vercel.app/` 完成 redeploy + 實站 smoke，故上面 4 個驗收 checkbox 先保留未勾選。

## 注意事項

> ⚠️ Vercel Serverless 有 10 秒執行時間限制 (免費版)。
> `/api/chat` 如果呼叫外部 LLM API 可能接近此限制。
> 如果超時，考慮使用 Vercel 的 `edge` runtime 或 streaming response。
