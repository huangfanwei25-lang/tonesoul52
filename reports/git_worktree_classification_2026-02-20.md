# 工作樹變更分類報告（2026-02-20）

> 目的：把目前未提交變更依責任域分類，作為 Phase 2 切分提交依據。  
> 備註：`.agent/skills/local_llm/` 已由使用者確認為支線（另一個 AI 進行中）。

## 1. 分類規則
- `核心執行`: 會影響 runtime 行為或治理流程。
- `治理與完整性`: 會影響規範、完整性檢查、受保護檔策略。
- `狀態工件`: 自動化輸出或健康檢查結果。
- `規格與企畫`: 規格、計畫、任務追蹤文件。
- `支線工作`: 其他協作代理正在進行，不與本次主線混提。

## 2. 目前檔案分類

| 路徑 | 狀態 | 類別 | 建議 |
|---|---|---|---|
| `tonesoul/council/runtime.py` | M | 核心執行 | 與 runtime 相關改動同批提交 |
| `tonesoul/persona_dimension.py` | M | 核心執行 | 與 persona/runtime 同批提交 |
| `tonesoul/unified_pipeline.py` | M | 核心執行 | 與 pipeline 相關改動同批提交 |
| `scripts/verify_git_hygiene.py` | M | 治理與完整性 | 與完整性流程檔案同批提交 |
| `.github/workflows/agent-integrity-check.yml` | ?? | 治理與完整性 | 與 `scripts/check_agent_integrity.py` 同批提交 |
| `scripts/check_agent_integrity.py` | ?? | 治理與完整性 | 與完整性 workflow 同批提交 |
| `AGENTS.md` | M | 治理與完整性（受保護） | 單獨提交或與完整性機制綁定提交 |
| `docs/status/git_hygiene_latest.json` | M | 狀態工件 | 視為 CI 產物；避免與核心程式混提 |
| `docs/status/git_hygiene_latest.md` | M | 狀態工件 | 視為 CI 產物；避免與核心程式混提 |
| `docs/status/persona_swarm_framework_latest.json` | M | 狀態工件 | 視為 CI 產物；避免與核心程式混提 |
| `docs/status/repo_healthcheck_latest.json` | M | 狀態工件 | 視為 CI 產物；避免與核心程式混提 |
| `docs/status/repo_healthcheck_latest.md` | M | 狀態工件 | 視為 CI 產物；避免與核心程式混提 |
| `memory/ANTIGRAVITY_SYNC.md` | M | 規格與企畫 | 可與文檔計畫類合併提交 |
| `task.md` | M | 規格與企畫 | 可與本次企畫更新同批提交 |
| `RESTART_MEMORY.md` | ?? | 規格與企畫 | 確認是否納入主線文件 |
| `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md` | ??/M | 規格與企畫 | 納入「Git 整治企畫」批次 |
| `spec/personas/yuhun_v1_multi_persona_audit.yaml` | ?? | 規格與企畫 | 納入「語魂 1.0 多人格審計」批次 |
| `.agent/skills/local_llm/` | ?? | 支線工作 | 不與本次主線混提；僅追蹤狀態 |

## 3. 建議提交批次（Phase 2）

1. `核心執行批次`
- `tonesoul/council/runtime.py`
- `tonesoul/persona_dimension.py`
- `tonesoul/unified_pipeline.py`

2. `治理與完整性批次`
- `scripts/verify_git_hygiene.py`
- `scripts/check_agent_integrity.py`
- `.github/workflows/agent-integrity-check.yml`
- `AGENTS.md`（建議同批或獨立）

3. `規格與企畫批次`
- `task.md`
- `memory/ANTIGRAVITY_SYNC.md`
- `RESTART_MEMORY.md`
- `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`
- `spec/personas/yuhun_v1_multi_persona_audit.yaml`

4. `狀態工件批次`
- `docs/status/git_hygiene_latest.json`
- `docs/status/git_hygiene_latest.md`
- `docs/status/persona_swarm_framework_latest.json`
- `docs/status/repo_healthcheck_latest.json`
- `docs/status/repo_healthcheck_latest.md`

5. `支線保留`
- `.agent/skills/local_llm/`（不動）

## 4. 下一步
- 先確認 `AGENTS.md` 與狀態工件是否跟隨本輪提交。
- 確認後按上述批次進行 `git add` 與提交切分。
