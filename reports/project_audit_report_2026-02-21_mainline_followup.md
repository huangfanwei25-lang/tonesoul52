# Project Audit Report (Mainline Follow-up)

> 日期: 2026-02-21  
> 範圍: 主線 (`master`) 實際 Git 狀態、近幾日新增檔案、倉庫文件架構、下一步主線任務

## 1) Git 實際狀況

- 分支: `master`
- 最新提交: `a4bed75` (`chore(mainline): remove one-off root scripts and sync docs`)
- 遠端同步: `origin/master` 已同步
- 主線清理已完成:
  - 刪除 `diagnostic_post.py`
  - 刪除 `reply_tone_tension.py`
  - 刪除 `test_api_post.py`
  - 同步 `SCRIPTS_README.md`、`reports/REPO_INVENTORY.md`、`docs/ARCHITECTURE_DEPLOYED.md`、`task.md`
- 現存本地工作樹差異 (支線/他人作業，依指示暫不處理):
  - `tests/conftest.py` (modified)
  - `.agent/skills/qa_auditor/` (untracked)
  - `tests/test_adaptive_gate_qa_audit.py` (untracked)
  - `tests/test_qa_auditor_d3_d4.py` (untracked)

## 2) 近幾日新增檔案摘要 (2026-02-19 之後)

重點新增檔案:

- `reports/project_audit_report_2026-02-21.md`
- `reports/multi_persona_audit_discussion_2026-02-20.md`
- `reports/git_local_baseline_2026-02-20.md`
- `reports/git_worktree_classification_2026-02-20.md`
- `reports/git_phase2_commit_batch_draft_2026-02-20.md`
- `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`
- `docs/plans/side_branch_isolation_playbook_2026-02-21.md`
- `docs/SPEC_LAW_CROSSWALK.md`
- `spec/personas/yuhun_v1_multi_persona_audit.yaml`
- `scripts/check_agent_integrity.py`
- `.github/workflows/agent-integrity-check.yml`

結論: 近幾日新增主要集中在治理、審計、企畫、狀態產物與完整性防護，主線方向一致。

## 3) 倉庫文件架構摘要

`docs/` 目前可分為:

- 架構主軸: `ARCHITECTURE_DEPLOYED.md`, `ARCHITECTURE_CONVERGENCE_PLAN.md`, `REPOSITORY_STRUCTURE.md`, `STRUCTURE.md`
- 治理/規範: `AUDIT_CONTRACT.md`, `EXTERNAL_SOURCE_TRUST_POLICY.md`, `TOOLS_API_SCHEMA.md`
- 企畫與執行: `docs/plans/*`
- 狀態產物: `docs/status/*`
- 研究與理念: `docs/research/*`, `docs/philosophy/*`

倉庫核心目錄結構仍維持:

- `tonesoul/` (核心 runtime / governance / memory)
- `apps/` (web 與 API 入口)
- `scripts/` (驗證/健康檢查/治理腳本)
- `tests/` (主線測試)
- `reports/` (審計與盤點產物)

## 4) 目前風險與約束

- 本地 `pytest -q` 會被支線未追蹤測試檔中斷 (`freezegun` 缺失)；主線驗證需排除支線測試收集。
- 全倉 `ruff check` 目前有大量歷史 lint 債，非本次主線清理引入；需獨立治理批次處理。
- 依目前策略，支線檔案僅本機隔離，不進主線提交。

## 5) 主線下一步建議 (按優先級)

1. **P0: Decay 查詢效能治理**
   - 對應 `docs/ARCHITECTURE_DEPLOYED.md` 未完成項: Python 應用層過濾效能風險。
   - 先做基準測試 + 查詢路徑盤點，再決定 SQL/索引/分層快取方案。

2. **P1: 前端語義可觀測性**
   - 補上 `semantic_contradictions` / `semantic_graph_summary` / visual chain 快照顯示規格與接線。

3. **P1: Evolution 結果持久化**
   - 規劃本地 JSON 向 Supabase `evolution_results` 的同步與回填策略。

4. **P2: 蒸餾排程與本地模型 PoC**
   - 設計 cron/webhook 與 LoRA/QLoRA 最小可行流程，先出實驗門檻與驗收規格。

## 6) 本輪已完成的主線行動

- 清理主線一次性腳本並推送遠端 (`a4bed75`)。
- 更新主線文件與盤點一致性。
- 產出本 follow-up 審計報告與下一階段企畫文件。
