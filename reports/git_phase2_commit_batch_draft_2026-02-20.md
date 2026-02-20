# Phase 2 提交切分草案（Dry Run）

> 產生時間：2026-02-21  
> 目的：把目前工作樹拆成單一責任提交，避免混合提交造成回溯困難。  
> 狀態：草案（尚未執行 `git add` / `git commit`）。

## 1. 切分原則
- 一個提交只處理一個責任域。
- 受保護檔（`AGENTS.md`）不與 runtime 混提。
- 狀態工件（`docs/status/*`）不與邏輯修正混提。
- 使用者指定支線 `.agent/skills/local_llm/` 不納入本輪主線提交。

## 2. 目前可切分批次

## 批次 A：核心執行（runtime）
- `tonesoul/council/runtime.py`
- `tonesoul/persona_dimension.py`
- `tonesoul/unified_pipeline.py`

建議提交訊息：
- `fix(runtime): align council/persona/pipeline behavior after hygiene audit`

## 批次 B：治理與完整性
- `scripts/verify_git_hygiene.py`
- `scripts/check_agent_integrity.py`
- `.github/workflows/agent-integrity-check.yml`
- `AGENTS.md`（受保護檔，建議與 B 同批或單獨成 B2）

建議提交訊息：
- `feat(governance): add agent integrity check workflow and guardrails`

## 批次 C：規格與企畫文件
- `task.md`
- `RESTART_MEMORY.md`
- `memory/ANTIGRAVITY_SYNC.md`
- `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`
- `reports/git_local_baseline_2026-02-20.md`
- `reports/git_worktree_classification_2026-02-20.md`
- `reports/git_phase2_commit_batch_draft_2026-02-20.md`
- `spec/personas/yuhun_v1_multi_persona_audit.yaml`

建議提交訊息：
- `docs(plan): add git baseline artifacts and yuhun multi-persona audit profile`

## 批次 D：狀態工件
- `docs/status/git_hygiene_latest.json`
- `docs/status/git_hygiene_latest.md`
- `docs/status/persona_swarm_framework_latest.json`
- `docs/status/repo_healthcheck_latest.json`
- `docs/status/repo_healthcheck_latest.md`

建議提交訊息：
- `chore(status): refresh git hygiene status artifact`

## 支線保留（本輪不處理）
- `.agent/skills/local_llm/`

## 3. 預計執行順序（建議）
1. 批次 A
2. 批次 B（或 B + B2）
3. 批次 C
4. 批次 D

## 4. 每批次提交前固定檢查
- `python -m ruff check tonesoul tests scripts`
- `python -m black --check tonesoul tests scripts`
- `python -m pytest tests -q`

## 5. 備註
- 本輪已完成審計基線：`python scripts/run_repo_healthcheck.py --allow-missing-discussion`，結果 `overall_ok: true`。
- 若 `AGENTS.md` 在你與其他代理之間持續變動，建議改成獨立提交，避免與 workflow 腳本綁死。
