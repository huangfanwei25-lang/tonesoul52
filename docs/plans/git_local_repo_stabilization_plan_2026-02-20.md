# Git 與本地倉庫整治企畫書（2026-02-20）

> Purpose: stabilize the local git repository and worktree before larger dual-track convergence and migration work.
> Last Updated: 2026-03-23

## 1. 企畫目標
- 先把目前 `git` 與本地倉庫狀態完整盤點，形成可追溯基線。
- 將最近新增檔案與當前工作樹變更分群，避免語魂 1.0 開發時混入無關改動。
- 建立可執行的分階段流程，回到「小步、可驗證、可審計」的節奏。

## 2. 現況摘要

### Git 基線
- 分支：`master`
- 目前提交：`16ffd79`
- 最近提交日期：`2026-02-14`
- 遠端：`origin https://github.com/Fan1234-1/tonesoul52.git`

### 工作樹狀態（含支線）
- 已修改：
  - `AGENTS.md`
  - `docs/status/git_hygiene_latest.json`
  - `docs/status/git_hygiene_latest.md`
  - `memory/ANTIGRAVITY_SYNC.md`
  - `scripts/verify_git_hygiene.py`
  - `task.md`
  - `tonesoul/council/runtime.py`
  - `tonesoul/persona_dimension.py`
  - `tonesoul/unified_pipeline.py`
- 未追蹤：
  - `.agent/skills/local_llm/`（支線：由另一個 AI 進行）
  - `.github/workflows/agent-integrity-check.yml`
  - `RESTART_MEMORY.md`
  - `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`
  - `scripts/check_agent_integrity.py`
  - `spec/personas/yuhun_v1_multi_persona_audit.yaml`

### 近 7 日新增檔案主軸
- 多人格群體審計（swarm）：
  - `tonesoul/council/swarm_framework.py`
  - `scripts/run_persona_swarm_framework.py`
  - `scripts/run_persona_swarm_dispatch.py`
  - `docs/experiments/PERSONA_SWARM_FRAMEWORK.md`
  - `docs/experiments/persona_swarm_input_template.json`
- 外部來源信任治理：
  - `spec/external_source_registry.yaml`
  - `scripts/verify_external_source_registry.py`
  - `scripts/run_external_source_registry_check.py`
  - `docs/EXTERNAL_SOURCE_TRUST_POLICY.md`
- 釋出與就緒：
  - `docs/RELEASE_NOTES_v0.1.0.md`
  - `docs/plans/release_readiness_staging.md`
  - `reports/coverage_latest.*`
- VM 與基礎設施：
  - `docs/plans/ANTIGRAVITY_VM_RUNBOOK.md`
  - `scripts/vm/bootstrap_antigravity_vm.sh`
  - `scripts/vm/run_antigravity_smoke.sh`

## 3. 文件架構總覽

### 根目錄主文件
- 核心入口：`README.md`, `SOUL.md`, `task.md`, `CODEX_TASK.md`, `AGENTS.md`, `AXIOMS.json`

### `docs/`（主文檔域，約 154 檔）
- 高密度子域：
  - `docs/engineering/`（16）
  - `docs/philosophy/`（16）
  - `docs/status/`（11）
  - `docs/research/`（9）
  - `docs/plans/`（6）
  - `docs/governance/`（4）
  - `docs/experiments/`（4）

### `spec/`（規格域，約 34 檔）
- 結構重點：
  - `spec/personas/`（2）
  - `spec/governance/`、`spec/tools/`、`spec/skills/`（各 2）
  - 其餘為單檔規格（council、frontend、memory、metrics 等）

### `law/`（治理法規域，約 80 檔）
- 高密度子域：
  - `law/docs/`（22）
  - `law/engineering/`（15）
  - `law/EXAMPLES/`（4）
  - `law/DIAGRAMS/`（3）

## 4. 主要風險
- 風險 1：工作樹同時混有 runtime、治理、狀態工件與文檔改動，提交邊界不清。
- 風險 2：`AGENTS.md` 屬受保護檔，若與一般改動混提，完整性流程風險提高。
- 風險 3：`docs/status/*` 為自動化工件，手動變更容易和 CI 輸出漂移。
- 風險 4：`docs/spec/law` 三域雖完整，但索引與責任對照仍可收斂。

## 5. 分階段執行計畫

## Phase 1：基線封存（已完成）
- [x] 建立 `git status` 與近 7 日新增檔案快照，存入報告。
- [x] 對目前工作樹變更做分類（runtime / 治理 / 狀態工件 / 文檔 / 支線）。
- [x] 標記受保護檔與支線處理策略。
**產出**
- `reports/git_local_baseline_2026-02-20.md`
- `reports/git_worktree_classification_2026-02-20.md`
**成功標準**
- 任一檔案都能回答：為何修改、屬於哪一類、由哪個階段處理。

## Phase 2：Git 整理（已完成，2026-02-21）
- [x] 以主題切分提交，避免單次提交混 runtime + docs + status。
- [x] 對 `docs/status/*` 採固定策略（由 CI 更新，或手動更新需附檢查證據）。
- [x] 對 untracked 檔案逐一決策：納入版本、延後、或排除。
**成功標準**
- `git log --name-only` 呈現清楚的一次一責任提交序列。
  - 已完成批次提交序列：runtime / governance / docs / status。
  - 已決策支線檔案：`.agent/skills/local_llm/`、`tonesoul/adaptive_gate.py`、`tests/test_adaptive_gate.py` 目前保留未提交。

## Phase 3：文件架構收斂（已完成，2026-02-21）
- [x] 以 `docs/INDEX.md` 作為單一入口，補齊新規格與新企畫索引。
- [x] 明確切分 `docs/REPOSITORY_STRUCTURE.md` 與 `docs/STRUCTURE.md` 的定位（地圖 vs 命名規則）。
- [x] 建立 `docs/spec/law` 一頁式對照，降低重複敘述。
**成功標準**
- 新人可在 5 分鐘內定位「規格、實作、治理」三條主線。

## Phase 4：驗證關卡（已完成，2026-02-21）
- [x] `python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28`
- [x] `python scripts/verify_docs_consistency.py`
- [x] `python scripts/run_repo_healthcheck.py --allow-missing-discussion`
**成功標準**
- 三項檢查可重現，且輸出可審計結果。

## 6. 立即執行順序
1. 完成 Phase 1 報告與分類（已完成）。
2. 先決策 `AGENTS.md` 與 `docs/status/*` 的提交策略，再進入 Phase 2。
3. 完成 Phase 2 後再做 Phase 3/4，避免邊整理邊擴散變更面。
