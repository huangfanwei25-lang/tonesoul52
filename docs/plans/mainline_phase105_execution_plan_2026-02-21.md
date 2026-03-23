# Mainline Phase 105 執行企畫 (2026-02-21)

> Purpose: execution plan for stabilizing the Phase 105 mainline before broader convergence and delivery work.
> Last Updated: 2026-03-23

## 目標

在不干擾支線進行的前提下，推進主線未完成架構任務，先完成「可驗證、可提交、可回溯」的執行基線。

## 範圍與邊界

- 僅處理主線任務與主線文件。
- `.agent/skills/local_llm/`、`qa_auditor` 相關支線檔案維持本機隔離，不納入主線提交。
- 不在本 phase 直接合併支線功能。

## Phase 105-A: 主線基線凍結

- [ ] 盤點主線可提交工作樹（排除支線檔案）
- [ ] 固定主線驗證口徑（主線測試、文件一致性、git hygiene）
- [ ] 在 `task.md` 與 `reports/` 形成單一審計事實來源

**驗收標準**:
- `master` 每次提交都可追溯到主線任務，不混入支線檔案。

## Phase 105-B: Decay 效能治理設計

- [ ] 盤點 `memory/soul_db.py` 相關 decay 查詢路徑
- [ ] 建立最小 benchmark（資料量階梯 + 查詢延遲）
- [ ] 提出候選方案比較（應用層過濾 vs DB 層條件/索引）
- [ ] 產出實作決策文件與風險

**驗收標準**:
- 有可重跑的 benchmark 與明確決策基準，不再只停留風險描述。

## Phase 105-C: 前端語義可觀測性接線規格

- [ ] 定義 `semantic_contradictions` / `semantic_graph_summary` 前端顯示契約
- [ ] 定義 visual chain 快照最小 UI 規格與 fallback 行為
- [ ] 寫出 API/前端契約測試草案

**驗收標準**:
- 前後端對同一組欄位與降級行為有一致契約。

## Phase 105-D: Evolution 持久化路線

- [ ] 規劃本地 JSON -> Supabase `evolution_results` 欄位映射
- [ ] 定義回填策略（增量、冪等、錯誤復原）
- [ ] 定義最小 smoke 驗證流程

**驗收標準**:
- 可明確說明「何時寫入、寫入什麼、失敗怎麼恢復」。

## 交付物

- `reports/project_audit_report_2026-02-21_mainline_followup.md`
- `docs/plans/mainline_phase105_execution_plan_2026-02-21.md`
- `task.md` 的 Phase 105 追蹤區塊

## 驗證命令

```bash
python scripts/verify_docs_consistency.py
python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28
pytest -q $(git ls-files tests/test_*.py)
```

## 風險註記

- 全倉 `ruff check` 目前存在歷史 lint 債，需獨立整理，不與本 phase 混批。
- 若支線測試檔進入收集，`pytest -q` 會受 `freezegun` 缺依賴影響；主線驗證需維持既定口徑。
