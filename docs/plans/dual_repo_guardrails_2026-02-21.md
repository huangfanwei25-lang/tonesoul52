# 雙倉庫防回滲守門規範（Dual-Track Guardrails）

> Purpose: define guardrails that prevent private evolution data and strategy from leaking into the public repository.
> Last Updated: 2026-03-23

> 日期：2026-02-21
> 狀態：Draft for Immediate Adoption
> 目標：避免私有演化資料與策略誤提交到公開倉。

## 1. 守門層級

1. 本機層：pre-commit（最快阻擋）
2. 平台層：GitHub Actions（最終阻擋）
3. 審查層：PR checklist + codeowner

## 2. 路徑阻擋規則（公開倉）

以下路徑若被新增或修改，預設 fail：

- `tonesoul_evolution/`
- `memory/handoff/`
- `memory/external_framework_analysis/`
- `memory/narrative/`
- `memory/vectors/`
- `memory/.semantic_index/`
- `memory/.hierarchical_index/`
- `memory/memory/.semantic_index/`
- `memory/memory/.hierarchical_index/`
- `.agent/`
- `obsidian-vault/`
- `simulation_logs/`
- `reports/ystm_demo/`
- `generated_prompts/`
- `.moltbook/`
- `memory/` 私有運行產物（例如 `ANTIGRAVITY_SYNC.md`、`antigravity_journal.md`、`summary_balls.jsonl`、`web_chat_debug.md`）
- `memory/self_journal.jsonl`
- `memory/agent_discussion.jsonl`
- `memory/agent_discussion_curated.jsonl`

## 3. 內容阻擋規則（公開倉）

若檔案內容命中下列訊號，預設 fail 並要求人工覆核：

1. 未脫敏對話原文（含 user 可識別資訊）
2. 私有系統 prompt / payload 原文
3. 私有營收閘門策略參數（非公開版）
4. 明確憑證、金鑰、token（含變形格式）

## 4. PR Checklist（新增欄位）

每個 PR 必填：

- [ ] 本 PR 未包含私有倉 B 類路徑內容
- [ ] 若涉及 C 類（介面層），已拆成 public interface + private implementation
- [ ] 已通過 dual-track boundary check（local + CI）

## 5. 例外流程（Break-glass）

僅允許以下條件暫時 bypass：

1. 重大事故修復（P0）
2. 已由 gatekeeper 明確批准
3. 24 小時內補上修復 PR，恢復守門規則

## 6. 導入順序

1. 先上 CI 檢查（觀察模式 1-2 天）
2. 再切成 blocking mode
3. 最後加 pre-commit 本機檢查

## 7. 度量指標

1. 每週「私有路徑誤提交」次數
2. 每週 boundary check fail 次數與原因分布
3. 例外流程觸發次數（應趨近於 0）

## 8. 對主線的要求

- 守門規則不能破壞主線開發速度：
  - 錯誤訊息必須指出具體路徑
  - 提供對應修復建議（搬到私有倉或改為 stub）
