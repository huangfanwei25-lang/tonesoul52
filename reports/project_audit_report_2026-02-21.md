# Project Audit Report

> 審計時間：2026-02-21 03:08 (+08:00)  
> 審計範圍：Git 狀態、CI 現況、任務看板、文件待辦、狀態產物新鮮度  
> 基準提交：`e9b6662`

## 一、總覽結論

- 目前主線 CI 為全綠（9 個 workflow 全部 `completed success`）。
- `task.md` 目前沒有未完成 checkbox，主看板已清空。
- 仍有 3 個本地未追蹤檔案（屬支線）尚未做納管決策：
  - `.agent/skills/local_llm/`
  - `tonesoul/adaptive_gate.py`
  - `tests/test_adaptive_gate.py`
- 文件層 backlog 仍偏大，且分散在多份規劃文件中，缺少單一執行入口。

## 二、關鍵發現（依優先級）

## P0（本週應完成）

1. 支線檔案未納管  
   - 現況：3 個未追蹤檔案長時間存在。  
   - 風險：後續容易與主線改動混提交，或成為「本地可跑、CI 不可重現」來源。  
   - 建議：對三個檔案逐一標記「納入主線 / 延後 / 永久忽略」。

2. Git 穩定化計畫（Phase 2/3/4）仍是未勾選狀態  
   - 來源：`docs/plans/git_local_repo_stabilization_plan_2026-02-20.md:103-119`  
   - 風險：實際已完成動作與計畫勾選不同步，治理可追溯性下降。  
   - 建議：將已完成事項補勾選，未完成事項拆為可執行子任務。

## P1（下週建議完成）

1. 文件入口仍分散  
   - 來源：同上計畫文件 `:110-112`（`docs/INDEX.md` 入口、`REPOSITORY_STRUCTURE` vs `STRUCTURE` 定位、`docs/spec/law` 一頁式對照）。  
   - 風險：新成員（或新代理）查找成本高，容易重工。  
   - 建議：完成單一入口與文檔分工對照表。

2. 狀態產物新鮮度不一致  
   - 新鮮（0 天）：`git_hygiene_latest.*`, `repo_healthcheck_latest.*`, `persona_swarm_framework_latest.json`  
   - 偏舊（6.5~10.2 天）：`external_source_registry_latest.*`, `multi_persona_eval_latest.json`, `monthly_consolidation_report.json`, `7d_snapshot.json`  
   - 風險：決策基準混用「最新」與「舊快照」。  
   - 建議：建立更新節奏（每週或每次里程碑合併後重跑）。

## P2（中期研發/產品 backlog）

1. 架構與產品層待辦仍多  
   - `docs/ARCHITECTURE_DEPLOYED.md:728-737`（資料持久化、蒸餾排程、前端可視化等）  
   - `docs/SMALL_BOAT_MVP.md:211-215`（本地模型整合驗證）  
   - `docs/DEMO_SHOWCASE.md:26-29`（展示前檢查與產物）  
   - `docs/bayesian_accountability_plan.md:88-102`（治理研究線）

## 三、文件待辦密度（Top）

- `docs/bayesian_accountability_plan.md`：11 項未勾選  
- `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`：9 項未勾選  
- `docs/research/experimental_design.md`：8 項未勾選  
- `docs/ARCHITECTURE_DEPLOYED.md`：8 項未勾選

## 四、建議下一輪任務（可直接執行）

1. 任務 A：支線檔案納管決策  
   - 內容：對 3 個未追蹤檔案逐一決策並落地（提交 / `.gitignore` / 保留支線）。  
   - 驗收：`git status --short` 僅保留明確允許的路徑。

2. 任務 B：同步 Git 穩定化計畫勾選  
   - 內容：更新 `docs/plans/git_local_repo_stabilization_plan_2026-02-20.md`，把已完成工作回填。  
   - 驗收：計畫勾選與現況一致，無「已做未勾」。

3. 任務 C：文檔入口治理  
   - 內容：補 `docs/INDEX.md` 索引，補 `docs/REPOSITORY_STRUCTURE.md` vs `docs/STRUCTURE.md` 分工說明。  
   - 驗收：`verify_docs_consistency.py` 通過，新增入口可定位新計畫/規格。

4. 任務 D：狀態產物刷新週期化  
   - 內容：重跑偏舊 status 生成腳本並確認 CI artifact 對齊。  
   - 驗收：主要 `docs/status/*latest*` 與 consolidation 產物在同一週期內更新。

## 五、建議驗證指令

```bash
python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28
python scripts/verify_docs_consistency.py
python scripts/run_repo_healthcheck.py --allow-missing-discussion
```
