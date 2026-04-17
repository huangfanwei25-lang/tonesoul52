# ToneSoul V1.2 Proposals (2026-04-16)

> Status: parked — 不在 V1.1 scope 內，等 v0a commit 後再評估優先序
> Origin: Claude Code 架構對照分析（fullstackladder.dev 18 章 vs ToneSoul）

---

## Proposal A: Council-as-Tool — 最小 Token 治理介面 + MCP 相容

### 動機（雙重）

**面向一：Token 效率**
語魂的治理資訊目前透過 session-start context dump 注入 AI（6KB–142KB）。
這代表每次對話都把完整治理狀態塞進 context window，即使 AI 只需要一個 verdict。
如果把 council 包成 MCP tool，AI 呼叫一次拿回 ~50 tokens 的結構化結果，
token 成本降兩個數量級。Council 變成跟 Read / Bash 一樣的工具——
呼叫、拿結果、不帶原始資料進 context。

**面向二：生態觸及**
語魂現有的 governance gateway 是自定 HTTP API（`scripts/gateway.py`）。
Claude Code 的 MCP 協定（JSON-RPC 2.0，8 種 transport）已成為 agent 工具生態的事實標準。
包成 MCP server，任何 Claude Code / Cursor / Windsurf / 其他 MCP client 都能直接接。

### 核心設計：兩層 MCP Tools

**治理工具層（Council-as-Tool）**
| Tool | 輸入 | 輸出（compact） | Token 成本 |
|---|---|---|---|
| `council_deliberate` | draft_output + user_intent | verdict + coherence + minority + risk | ~50 tokens |
| `council_check_claim` | claim_text | ceiling + evidence_level + blocked_reasons | ~30 tokens |
| `council_get_calibration` | (none) | 4 指標 summary（v0a baseline） | ~80 tokens |

**Gateway 工具層（原 HTTP API 轉 MCP）**
| Tool | 對應原 endpoint | 用途 |
|---|---|---|
| `governance_load` | POST /load | 載入治理狀態 |
| `governance_commit` | POST /commit | 提交治理變更 |
| `governance_summary` | GET /summary | 當前狀態摘要 |
| `governance_visitors` | GET /visitors | agent 訪問記錄 |
| `governance_audit` | GET /audit | 審計鏈 |

### 關鍵約束
- Council rules_only 模式：**零 API 成本**，純本地
- Council hybrid 模式：只花 Gemini Flash token（guardian + critic），其餘規則引擎
- MCP tool 回傳格式嚴格壓縮——不帶 vote reasoning、不帶 raw transcript
- 保留現有 HTTP API 作為 fallback
- 安全邊界：MCP server 只暴露 read + bounded write，不暴露 governance state 直接修改

### 不做
- 不重寫 gateway 內部邏輯
- 不改 council runtime verdict 邏輯
- 不動治理層 fail-closed 行為
- 不做 composite score 或 health grade

### 預估
- ~400-700 行新增（MCP adapter + compact result serializer）
- 需要 `mcp` Python SDK 或手寫 JSON-RPC handler
- Council-as-Tool 層可獨立於 gateway 層先做

### 驗證 session-start 可以瘦身
一旦 council 是 tool，session-start 不再需要帶完整治理 context：
- tier 0 可以只帶 readiness + claim boundary（~1KB）
- 需要治理細節時 AI 主動呼叫 `council_deliberate` / `council_check_claim`
- 預估 context 注入從 6-142KB 降到 1-2KB

---

## Proposal B: 啟動管線最佳化 — Tier 0 < 500ms

### 動機
Claude Code 的啟動管線在 240ms 內完成（5 檔平行 I/O + 延遲載入）。
ToneSoul 的 `start_agent_session.py --tier 0` 目前需要數秒，主要花在：
- Python 啟動 + import chain
- governance_state 讀取（file I/O）
- readiness 計算
- git status probe

Agent 如果「怕叫 session start」就會跳過，導致在沒有正確 context 的狀態下工作。

### 範圍
- 量測目前 tier 0 的時間分佈（哪一步最慢）
- 平行化獨立 I/O（governance read ∥ git probe ∥ aegis check）
- 延遲載入非必要模組（observer, diagnose, packet 在 tier 0 不需要）
- 目標：tier 0 < 500ms，tier 1 < 2s

### 不做
- 不改 tier 分層語義
- 不犧牲 readiness 檢查的完整性換速度
- 不引入 daemon/cache server（保持零基礎設施）

### 預估
- 主要是 refactor，新增程式碼量小
- 可能需要 lazy import + asyncio 或 threading

---

## 優先序建議

| 提案 | 影響 | 風險 | 建議順序 |
|---|---|---|---|
| A: Council-as-Tool + MCP | 極高 — 同時解決 token 成本 + 生態觸及 + session-start 瘦身 | 中 — MCP 協定 + compact serializer | 先做（council tool 層可獨立於 gateway 層先落） |
| B: 啟動最佳化 | 中 — 改善 DX | 低 — 純 refactor。注意：A 做完後 tier 0 瘦身可能已經解掉一半問題 | A 做完再評估是否還需要 |

---

*This document is subordinate to `task.md`. Do not treat these proposals as active until they are explicitly pulled into the live short board.*
