# ToneSoul 文件資訊架構 v1

> Purpose: declare the documentation-zone baseline, movement rules, and naming boundaries for ToneSoul docs.
> Last Updated: 2026-03-23

> 日期：2026-03-18
> 狀態：Baseline v1（先收斂規則，不做大規模搬檔）

---

## 1. 目標

本文件定義三件事：

1. 文件分類：同類資訊放在同一區。
2. 檔名控管：檔名能直接反映用途與時態。
3. 資料區管理：規格、狀態、草案、歷史分層保存。

這是倉庫文件收斂的第一版基準，不是最終版。

---

## 2. 文件分區（Data Zones）

### Zone A: Canonical Specs（規範真源）
- 位置：docs/, docs/governance/, docs/engineering/, docs/philosophy/, law/docs/
- 用途：會被實作直接引用的規格與原理
- 規則：
  - 優先使用中性、長期穩定檔名
  - 避免在檔名中放 draft、latest、tmp

### Zone B: Plans（執行計畫）
- 位置：docs/plans/
- 用途：階段計畫、addendum、路線圖
- 規則：
  - 檔名格式：topic_addendum_YYYY-MM-DD.md 或 topic_plan_YYYY-MM-DD.md
  - 計畫完成後，關鍵結論需回填到 Zone A 或 Zone C

### Zone C: Status & Reports（運行狀態與審計輸出）
- 位置：docs/status/, reports/
- 用途：latest 快照、週報、審計報告
- 規則：
  - latest 檔視為操作入口，不是長期知識來源
  - 能回填規格的結論，要升級到 Zone A

### Zone D: Archive（歷史封存）
- 位置：docs/archive/
- 用途：淘汰規格、已失效模組描述
- 規則：
  - 不可被 README 主入口直接引用為現行規格

---

## 3. 檔名控管規範 v1

### 3.1 類型前綴

- SPEC 類：
  - 例：VTP_SPEC.md, SEMANTIC_SPINE_SPEC.md
- GUIDE 類：
  - 例：GETTING_STARTED.md, reproducibility_guide.md
- PLAN 類：
  - 例：architecture_blueprint_2026-03-18.md
- STATUS 類：
  - 例：repo_healthcheck_latest.md
- REPORT 類：
  - 例：project_audit_report_2026-02-21.md

### 3.2 時態與穩定度

- 穩定文件：不用日期
- 版本快照/活動紀錄：加日期
- latest 僅限 status 型檔案

### 3.3 禁止命名

- final_final, new2, temp_last
- 不帶語義的縮寫（除非有術語表定義）

---

## 4. 目錄責任分工（Owner Semantics）

- docs/README.md + docs/INDEX.md：人類導覽入口
- docs/DOCS_INFORMATION_ARCHITECTURE_v1.md：文件治理規則
- docs/FILE_PURPOSE_MAP.md：跨目錄命名規約
- docs/plans/：變更提案與過渡設計
- docs/status/：系統狀態與治理快照

---

## 5. IU / OI / Backplane 對應文件

### IU（Interaction UI）
- docs/DEMO_SHOWCASE.md
- spec/chat_ui_improvement_spec.md
- apps/web/README.md

### OI（Operational Interface）
- docs/7D_AUDIT_FRAMEWORK.md
- docs/AUDIT_CONTRACT.md
- docs/status/README.md

### Backplane（內在執行層）
- docs/plans/architecture_blueprint_2026-03-18.md
- docs/plans/iu_oi_backplane_convergence_2026-03-18.md
- docs/AI_CONTINUITY_PROTOCOL.md

---

## 6. 近期收斂步驟（不破壞現況）

1. 先建立索引，不先搬檔。
2. 新文件必須符合本規範的檔名與分區。
3. 舊文件採增量重命名：每次只處理一組主題。
4. 每一輪重命名需更新 docs/INDEX.md 與 README 入口。

---

## 7. 成熟度聲明

ToneSoul 文件體系仍在收斂中，可視為未達 50% 完整度。

當前策略不是追求一次性完美重構，而是：

- 先建立可持續的分類規則
- 再以低風險方式逐批整理
- 每次整理都回填入口與介紹文件
