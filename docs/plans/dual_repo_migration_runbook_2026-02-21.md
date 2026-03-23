# 雙倉庫遷移 Runbook（Dual-Track Migration Runbook）

> Purpose: provide the migration runbook for separating and operating ToneSoul's public and private repositories.
> Last Updated: 2026-03-23

> 日期：2026-02-21
> 狀態：Execution Ready
> 範圍：把公開倉與私有倉從「概念分離」推進到「可重演分離」。

## 0. 遷移前提

1. 先確認邊界：`docs/plans/dual_repo_boundary_manifest_2026-02-21.md`
2. 指定 owner：
- Public maintainer
- Private maintainer
- Release gatekeeper
3. 冻結視窗：遷移期間避免同時做大功能重構。

## 1. Phase A：基線凍結（公開倉）

1. 建立標記點
- `git tag pre-dual-repo-split-2026-02-21`

2. 產出基線證據
- `ruff check tonesoul tests`
- `black --check tonesoul tests`
- `pytest -q`
- 保存結果到 `reports/`（可選）

3. 清單對齊
- 逐條核對 A/B/C 路徑分級是否與現況一致。

## 2. Phase B：私有倉初始化

1. 在私有倉建立目錄骨架
- `tonesoul_evolution/`
- `memory/`（僅私有條目）
- `docs/private/`（內部 runbook、payload policy）

2. 首批搬移（B 類）
- 搬移 raw memory 與演化資料（B 類路徑）
- 保留公開倉同名路徑的 ignore 規則與 README 指向

3. 驗證
- 私有倉可獨立讀取資料並執行既有夜間流程（若有）

## 3. Phase C：介面拆分（C 類）

目標：公開倉保留穩定 API；私有倉承載策略實作。

1. 公開倉動作
- 把 `tonesoul/memory/consolidator.py` 保留為 interface/stub
- 清楚拋出 "private implementation required" 的錯誤或回退行為

2. 私有倉動作
- 實作真正 consolidator/adversarial pipeline
- 以 adapter 注入公開 runtime（可透過環境變數或插件路徑）

3. 合約測試
- 公開倉測 stub 契約與 fallback
- 私有倉測真實策略

## 4. Phase D：防回滲守門

1. 新增公開倉邊界檢查（pre-commit + CI）
2. PR 模板加入 "Dual-Track Boundary" checkbox
3. 任一命中私有條件的變更，強制拆 PR（public/private）

## 5. 回滾策略

- 任何 Phase 失敗，回滾到 `pre-dual-repo-split-2026-02-21`
- 私有倉搬移失敗時，不回寫公開倉敏感資料；先修私有流程再重試

## 6. 驗收清單

- 公開倉不含 B 類私有路徑內容
- 公開倉 CI 全綠
- 私有倉演化流程可運行
- 兩倉邊界規則在 PR 流程可被機器驗證

## 7. 建議工期（可調）

1. Phase A：0.5 天
2. Phase B：1 天
3. Phase C：1-2 天
4. Phase D：0.5 天

總計：約 3-4 天
