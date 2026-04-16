# ToneSoul V1.2 Proposals (2026-04-16)

> Status: parked — 不在 V1.1 scope 內，等 v0a commit 後再評估優先序
> Origin: Claude Code 架構對照分析（fullstackladder.dev 18 章 vs ToneSoul）

---

## Proposal A: MCP 相容 — Governance Gateway as MCP Server

### 動機
語魂現有的 governance gateway 是自定 HTTP API（`scripts/gateway.py`，POST /load, /commit, GET /summary, /visitors, /audit）。
Claude Code 的 MCP 協定（JSON-RPC 2.0，8 種 transport）已成為 agent 工具生態的事實標準。
把 gateway 包成 MCP server，任何 Claude Code / Cursor / Windsurf / 其他 MCP client 都能直接接。觸及面比自定 API 大一個數量級。

### 範圍
- 把現有 gateway 的 5 個 endpoint 轉譯成 MCP tool definitions
- 支援 stdio transport（本地）+ SSE transport（遠端）
- 保留現有 HTTP API 作為 fallback
- 安全邊界：MCP server 只暴露 read + bounded write，不暴露 governance state 直接修改

### 不做
- 不重寫 gateway 內部邏輯
- 不改 council runtime
- 不動治理層 fail-closed 行為

### 預估
- ~300-500 行新增（MCP adapter layer）
- 需要 `mcp` Python SDK 或手寫 JSON-RPC handler

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
| A: MCP 相容 | 高 — 打開整個 agent 工具生態 | 中 — 需要理解 MCP 協定細節 | 先做 |
| B: 啟動最佳化 | 中 — 改善 DX，降低 agent 跳過 session start 的機率 | 低 — 純 refactor | 後做 |

---

*This document is subordinate to `task.md`. Do not treat these proposals as active until they are explicitly pulled into the live short board.*
