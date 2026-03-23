# 雙倉庫邊界清單（Dual-Track Boundary Manifest）

> Purpose: define the executable boundary checklist between the public ToneSoul repo and the private evolution repo.
> Last Updated: 2026-03-23

> 日期：2026-02-21
> 狀態：Draft for Execution
> 目的：把 ToneSoul 的公開倉與私有演化倉邊界寫成可執行清單，降低定義漂移與誤提交風險。

## 1. 依據文件（記憶脈絡）

1. `docs/ADR-001-dual-track-resolution.md`
2. `docs/PHILOSOPHY.md`（Dual-Track Evolution 章節）
3. `docs/rfc-005-memory-consolidator.md`
4. `.gitignore`（已存在的隔離意圖）

## 2. 倉庫角色定義

- `Public Repo (tonesoul52)`：可開源的引擎、協議、測試、文件與可重演流程。
- `Private Repo (tonesoul-evolution)`：會暴露內部演化策略、長期記憶原文、攻防 payload、私密治理素材的內容。

## 3. 路徑分級

### A. 公開倉必留（Source of Truth）

- `tonesoul/`（核心 runtime 與可公開演算法）
- `apps/`
- `tests/`
- `scripts/`（不含私鑰、token、私有 payload）
- `docs/`（不含敏感運行資料快照）
- `docs/status/` 治理狀態產物（公開可審計）：
  - `repo_healthcheck_latest.json` / `repo_healthcheck_latest.md`
  - `persona_swarm_framework_latest.json`
  - `external_source_registry_latest.json` / `external_source_registry_latest.md`
  - `dual_track_boundary_latest.json` / `dual_track_boundary_latest.md`
  - `multi_agent_divergence_latest.json` / `multi_agent_divergence_latest.md`
  - `memory_quality_latest.json` / `memory_quality_latest.md`
  - `memory_learning_samples_latest.jsonl`（脫敏樣本）
- `.github/workflows/`（公開 CI）

### B. 私有倉必留（Private-only）

- `tonesoul_evolution/`
- `memory/self_journal.jsonl`
- `memory/agent_discussion.jsonl`
- `memory/agent_discussion_curated.jsonl`
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

### C. 介面層（公開保留介面，私有保留實作）

- `tonesoul/memory/consolidator.py`
- `tonesoul/memory/adversarial.py`（若進入真實 Red/Blue payload）

原則：公開倉可以保留「抽象介面 + 安全 stub + 契約測試」，私有倉放「具體策略與 prompt/payload」。

## 4. 變更判定規則（PR Review 用）

若 PR 命中任一條件，需轉私有倉或拆分：

1. 包含可還原長期記憶語料（例如 self journal 原文）。
2. 包含可直接被 prompt injection 反向利用的攻防規則細節。
3. 包含私有商業策略（定價、風控、私鑰流程、營收閘門內參）。
4. 包含未脫敏的運行資料快照（含 user-sensitive context）。

## 5. 主線落地優先順序

1. 先凍結邊界：把 A/B/C 清單寫入治理文件與 CI 規則。
2. 再做搬移：先搬 B 類，最後處理 C 類（介面拆分）。
3. 最後驗證：公開倉 `ruff + black --check + pytest -q` 與 docs consistency 全綠。

## 6. 完成定義（DoD）

- 邊界清單可被 reviewer 逐條核對。
- 新增 CI 檢查可阻止 B 類路徑誤入公開倉。
- `task.md` 與主線追蹤板有對應 Phase/Owner。
- 所有搬移後 import 與測試無回歸。
