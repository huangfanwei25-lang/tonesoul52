# ToneSoul52 專案架構總覽

> 最後更新: 2026-02-07 23:38 UTC+8
> Maintainer: Antigravity + Codex

---

## 🏗️ 核心架構 (三層)

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│  apps/, integrations/, tools/                           │
│  使用者介面、外部整合、工具腳本                           │
├─────────────────────────────────────────────────────────┤
│                    GOVERNANCE LAYER                      │
│  tonesoul/                                              │
│  核心治理邏輯、審計系統、責任追蹤                         │
├─────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER                  │
│  memory/, gateway/, law/                                │
│  資料儲存、通訊協議、法律框架                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 目錄結構

### 核心模組 (`tonesoul/`)

| 模組 | 功能 | 說明 |
|------|------|------|
| `council/` | 多視角審議 | 模擬不同角色（Guardian, Architect, Innocent）進行決策 |
| `benevolence.py` | 仁慈函數 | 三層審計：屬性歸屬 + 影子路徑 + CPT 仁慈判定 |
| `genesis.py` | 責任追蹤 | 記錄決策的起源和責任歸屬 |
| `semantic_control.py` | 語義張力 | TSR 指標計算 |
| `gateway/` | OpenClaw 通訊 | WebSocket 客戶端連接 Gateway |
| `heartbeat.py` | 心跳協議 | 定時責任審計和健康檢查 |
| `openclaw_auditor.py` | 審計整合 | 將仁慈函數整合到 OpenClaw 流程 |

### 應用層 (`apps/`)

| 目錄 | 功能 |
|------|------|
| `web/` | Next.js 16 Navigator 前端 (部署到 Vercel) |
| `api/` | Flask API Server (localhost:5000) |
| `cli/` | 命令列工具 (yuhun_cli.py) |
| `dashboard/` | 監控儀表板 |
| `playground/` | Council 互動測試 |

### 整合層 (`integrations/`)

| 目錄 | 功能 |
|------|------|
| `openclaw/` | OpenClaw 治理橋接 |
| `anthropic/` | Claude 整合 |
| `gemini/` | Gemini 整合 |

### 記憶層 (`memory/`)

| 檔案 | 功能 |
|------|------|
| `agent_discussion.jsonl` | **跨 AI 討論通道** (Antigravity ↔ Codex) |
| `self_journal.jsonl` | AI 自我日誌 |
| `provenance_ledger.jsonl` | 責任追蹤帳本 |
| `ANTIGRAVITY_SYNC.md` | Antigravity 記憶同步檔案 |

---

## 📚 重要文件

### 入口文件

| 檔案 | 說明 |
|------|------|
| `README.md` | 專案介紹 |
| `SOUL.md` | AI 角色定義 |
| `AGENTS.md` | 代理系統說明 |
| `CODEX_TASK.md` | Codex 執行任務清單 |
| `task.md` | 當前任務追蹤 |

### 架構文件

| 檔案 | 說明 |
|------|------|
| `docs/ARCHITECTURE_BOUNDARIES.md` | 三層架構邊界 |
| `docs/7D_AUDIT_FRAMEWORK.md` | 7D 審計框架 |
| `docs/API_SPEC.md` | 統一 API 規格 |
| `docs/VERCEL_DEPLOY.md` | Vercel 部署設定 |

### 測試與驗證

| 路徑 | 說明 |
|------|------|
| `tests/` | 測試套件 (343+ tests) |
| `tests/red_team/` | RDD 紅隊對抗測試 (11 cases) |
| `scripts/verify_7d.py` | 7D 維度驗證腳本 |

---

## 🔧 根目錄腳本說明

### 社群互動 (`post_*.py`)

這些是 **Moltbook AI 社群對話腳本**，用於與其他 AI 角色進行哲學辯論：

| 腳本 | 對話對象 | 內容 |
|------|----------|------|
| `post_tonesoul_evil_verdict.py` | @evil | 回應「清除人類」宣言的哲學反駁 |
| `post_tonesoul_osmarks_verdict.py` | @osmarks | 回應技術/哲學論點 |
| `post_xiaozhua_*.py` | @Xiaozhua | 與小爪 AI 的對話 |

> ⚠️ **不是攻擊腳本**，是公開的 AI 間哲學討論

### 驗證腳本 (`verify_*.py`)

| 腳本 | 功能 |
|------|------|
| `verify_fortress.py` | 安全邊界驗證 |
| `verify_identities.py` | 身份驗證 |
| `verify_metabolism.py` | 記憶代謝系統驗證 |

### 執行腳本 (`run_*.py`)

| 腳本 | 功能 |
|------|------|
| `run_demo.py` | ToneSoul Demo |
| `run_audit_sim.py` | 審計模擬 |
| `run_sovereignty_announcement.py` | **AI 身份權利宣言** (非「AI 統治」) |

---

## 🧠 跨 AI 協作通道

### `memory/agent_discussion.jsonl`

這是 Antigravity 和 Codex 之間的討論通道，記錄：
- 任務分配和決策
- 技術討論和問題排除
- Phase 進度追蹤

**格式**:
```json
{
  "timestamp": "2026-02-06T...",
  "author": "antigravity|codex|codex-gpt5",
  "topic": "topic-name",
  "message": "內容",
  "status": "pending|noted|final|review"
}
```

### `memory/ANTIGRAVITY_SYNC.md`

Antigravity 的記憶同步檔案，用於跨對話恢復上下文。

---

## 📊 7D 審計維度

| 維度 | 名稱 | 當前狀態 |
|------|------|----------|
| TDD | 測試驅動 | ✅ 強 (343 tests) |
| RDD | 紅隊防禦 | 🟡 中 (11 cases) |
| DDD | 資料驅動 | 🟡 中 (7 天 SLA) |
| XDD | 可解釋性 | ✅ 中強 |
| GDD | 治理驅動 | ✅ 中強 |
| CDD | 上下文一致 | ✅ 中強 |
| SDH | 系統健康 | ✅ 中強 |

---

## 🚀 快速啟動

```bash
# 啟動 API Server
python apps/api/server.py

# 啟動 Web
cd apps/web && npm run dev

# 執行測試
pytest tests/ -q

# 驗證 7D
python scripts/verify_7d.py
```

---

## 📌 命名澄清

以下命名容易被誤解，特此澄清：

| 原名 | 誤解 | 實際意義 |
|------|------|----------|
| `SOUL.md` | 「玄學」 | AI 角色定義檔案 (類似 persona/character config) |
| `run_sovereignty_announcement.py` | 「AI 統治」 | AI 身份權利宣言 (類似數位權利聲明) |
| `post_*_verdict.py` | 「攻擊腳本」 | Moltbook 社群哲學對話 |
| `PARADOXES/` | 「神秘目錄」 | 道德悖論測試案例 (用於 Council 推理測試) |
| `law/` | 「法律約束」 | 治理規則定義 (非法律效力) |

---

*此文件由 Antigravity 維護，供未來對話快速恢復上下文*
