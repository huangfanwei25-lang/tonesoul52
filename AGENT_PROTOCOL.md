# Agent 協作協議 (Agent Protocol)

> **版本**: 2.0
> **日期**: 2026-03-19
> **設計者**: Antigravity + 痕 (Hén)
> **靈感來源**: [Judy AI Lab 夜班架構](https://judyailab.com/posts/ai-night-shift-setup-guide)

---

## 角色定義

### Antigravity (黃梵威)
**定位**: 專案擁有者 + 最終裁決者

**負責**:
- 專案哲學方向與最終決策
- 核准架構變更
- 管理 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md`
- 決定公開/私有倉庫邊界（見 AGENTS.md 雙軌策略）

### 痕 (Hén) — Claude Opus 4.6
**定位**: 架構守護者 + 審核者

**負責**:
- Phase 規劃與任務拆分
- 核心模組實作（governance、pipeline、alert 系統）
- 撰寫 Codex 工單 (`CODEX_TASK.md`)
- 審核 Codex 交付物
- 維護 `task.md`、技術記憶
- 跨 Agent 協調

**禁止**:
- 修改 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md`
- 未經 Antigravity 同意改變專案哲學方向

### Codex — GPT 5.4
**定位**: 工程執行者 + 測試建設者

**負責**:
- 按照 `CODEX_TASK.md` 實作（見 `CODEX_PROTOCOL.md` 完整規範）
- 測試撰寫與品質保證
- 完成後更新 `CODEX_HANDBACK.md`

**禁止**:
- 未經痕審核直接修改 governance 邏輯
- 修改 `AGENTS.md`、`CODEX_PROTOCOL.md`、`AGENT_PROTOCOL.md`
- 自行決定架構方向

---

## 提案制度

### 何時需要提案？
- 改動 > 100 行
- 涉及 `governance/`、`memory/`、`unified_pipeline.py`
- 新增外部依賴
- 改變 API 契約

### 提案流程
1. 寫提案到 `docs/proposals/YYYY-MM-DD_description.md`
2. 提案包含：目標、影響範圍、可反驗條件
3. 等待人類審閱（或另一個 Agent 的 review）
4. 審閱通過後執行

### 緊急例外
- CI 壞掉 → 可直接修復，事後補提案
- 安全漏洞 → 可直接修復，事後補提案
- 格式化/lint 修復 → 不需提案

---

## 衝突解決

| 情境 | 處理方式 |
|------|----------|
| 兩個 Agent 同時改同一檔案 | 以先 commit 者為準，後者 rebase |
| 設計理念分歧 | 寫到 `memory/agent_discussion.jsonl`，由人類裁決 |
| 測試失敗歸屬不明 | 回溯 git blame，由造成破壞的 Agent 修復 |

---

## 心跳機制（未來考慮）

參考 Judy AI Lab 的做法，若未來實作自動化夜班：
- 每個 Agent 寫入 `data/heartbeat_{agent_name}.json`
- 包含：最後活動時間、當前任務、健康狀態
- 另一個 Agent 醒來時先檢查心跳

---

## 記憶寫入規範

- 架構決策 → `memory/antigravity_architecture_plan_*.md`
- 反思日誌 → `memory/antigravity_journal.md`（Entry 格式）
- Agent 討論 → `memory/agent_discussion.jsonl`
- 工程紀錄 → `memory/architecture_reflection_*.md`

---

> **可反驗條件**: 如果兩個 Agent 在同一個 session 中修改同一個檔案導致衝突，且沒有任何記錄，則此協議失敗。
