# ToneSoul V1.2 Execution Plan (2026-04-16)

> Status: active — Codex overnight run
> Prerequisite: V1.1 v0a merged (PR #10, commit a8e0b93)
> Goal: Council-as-Tool + MCP server + session-start 瘦身
> Ship criteria: Codex 完成後 Claude 做 integration review，Fan-Wei 拍板

---

## 背景共識

1. Council `rules_only` 是規則引擎（keyword/pattern），不是語義治理。誠實標為 content filter。
2. Council `hybrid`/`full_llm` 有語義理解但需要 LLM token。
3. 不管 council 內部用什麼方法，**治理結果進 AI context 的方式可以壓縮** — 這是 1.2 的核心價值。
4. Token 壓縮適合任務型場景；語義責任需要完整脈絡，這個矛盾 1.2 不試圖解決。

---

## Phase 1: Compact Result Serializer（基礎）

### 目標
把 council verdict、calibration、governance summary 壓成最小 JSON，讓 MCP tool 回傳時 token 最少。

### 交付
- `tonesoul/council/compact.py` — compact serializer
  - `compact_verdict(verdict) -> dict` — ~50 tokens
  - `compact_calibration(wave_result) -> dict` — ~80 tokens
  - `compact_governance_summary(state) -> dict` — ~60 tokens
- `tests/test_council_compact.py`

### 壓縮規則
- 只保留 verdict / coherence / minority / risk_level / matched_skill_ids
- 不帶 vote reasoning / raw transcript / evidence text / full vote_profile
- 每個 compact 結果帶 `_compact: true` 標記，防止被誤讀為完整結果

### 不做
- 不改現有 verbose output — compact 是新增路徑，不替換

---

## Phase 2: MCP Server — Council Tool Layer（核心）

### 目標
把 council 包成 MCP tool，AI agent 可以像呼叫 Read / Bash 一樣呼叫治理。

### 交付
- `tonesoul/mcp_server.py` — MCP server 主體
- 支援 stdio transport（本地 VS Code / Claude Code 接入）

### Tool Definitions

```
council_deliberate
  input:  { draft_output: string, user_intent?: string, mode?: "rules"|"hybrid"|"full_llm" }
  output: compact_verdict (~50 tokens)

council_check_claim
  input:  { claim_text: string }
  output: { ceiling, evidence_level, blocked_reasons } (~30 tokens)

council_get_calibration
  input:  {}
  output: compact_calibration (~80 tokens)

council_get_status
  input:  {}
  output: compact_governance_summary (~60 tokens)
```

### 技術選擇
- 用 `mcp` Python SDK（`pip install mcp`）如果可用
- 否則手寫 JSON-RPC 2.0 handler（stdin/stdout line protocol）
- 先做 stdio transport，SSE 留 1.3

### 不做
- 不做 gateway 的 5 個 endpoint 轉 MCP（留 Phase 3）
- 不做 SSE / remote transport
- 不改 council runtime verdict 邏輯

---

## Phase 3: MCP Server — Gateway Tool Layer（擴充）

### 目標
把現有 HTTP gateway 的 endpoint 也包進 MCP server。

### 交付
- 在 `tonesoul/mcp_server.py` 加入 gateway tools：

```
governance_load       POST /load
governance_commit     POST /commit
governance_summary    GET /summary
governance_visitors   GET /visitors
governance_audit      GET /audit
```

### 約束
- 保留原 HTTP API 作為 fallback
- MCP server 只暴露 read + bounded write
- 不暴露 governance_state 直接修改

---

## Phase 4: Session-Start Slim Mode（收割）

### 目標
一旦 council 是 tool，session-start 不需要帶完整治理 context。

### 交付
- `start_agent_session.py` 新增 `--slim` flag
- `--slim` 模式只輸出：readiness + claim_boundary + available_tools（~1KB）
- AI 需要治理細節時主動呼叫 council tools
- 現有 tier 0/1/2 保留不動（向後相容）

### 驗證
- `--slim` 輸出 < 2KB
- 現有 tier 0/1/2 不受影響
- blocking tier tests 全過

---

## Phase 5: VS Code Extension Skeleton（可選，如果時間夠）

### 目標
最小 VS Code extension，接上 Phase 2 的 MCP server。

### 交付
- `extensions/vscode/` 目錄
- `package.json` + `extension.ts`（activation + MCP client）
- Status bar item：顯示 council verdict
- 不做 sidebar / webview / 完整 UI

### 判斷
如果 Phase 1-4 沒問題而且還有時間，再做。否則留 1.3。

---

## 硬規則（全 phase 適用）

- 不做 composite score / realism_score / council_health grade
- 不改 council runtime verdict 邏輯
- 不改 claim ceiling classification
- 不碰 subsystem_parity.py status
- 新增的 compact output 帶 `_compact: true` 標記
- 每個 phase 跑一次 `python -m tonesoul.diagnose`
- 每個 phase 跑一次 `python scripts/run_test_tier.py --tier blocking`
- ruff + black --line-length 100 全過

## 語言邊界

- `rules_only` 模式誠實標為 content filter / safety guardrail，不標為 AI governance
- `hybrid` / `full_llm` 模式可標為 bounded semantic governance
- compact output 明確標為 compressed summary，不是 complete verdict
- MCP tool description 裡寫清楚每個 mode 的能力邊界

---

## 執行順序與分工

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → (Phase 5)
  ↑ Codex 一晚可以推到 Phase 3 或 4
```

### Codex 負責
- Phase 1-4 全部實作
- 每個 phase commit 一次（按語義分）
- 最後跑 full verification

### Claude 負責
- Codex 完成後做 integration review
- 驗證 compact output 的 token 數量
- 驗證 MCP server 能被 Claude Code 接上
- 檢查語言邊界有沒有過度承諾

### Fan-Wei 負責
- Final sign-off
- 決定 Phase 5 做不做

---

## 成功定義

1.2 ship 時，以下為真：
- AI agent 可以用 `council_deliberate` tool call 拿到 ~50 token verdict
- session-start `--slim` 模式 < 2KB
- MCP server 可以被 Claude Code / VS Code 接上（stdio transport）
- `rules_only` 模式零 API 成本，誠實標為 content filter
- 現有治理流程完全不受影響（向後相容）

---

*This plan is subordinate to `task.md`. Codex should read this + `docs/plans/tonesoul_v1_2_proposals_2026-04-16.md` before starting.*
