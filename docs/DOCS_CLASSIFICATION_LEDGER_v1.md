# ToneSoul 文件分類台帳 v1

> Purpose: classify documentation lanes into governance zones so retrieval and cleanup work can distinguish authority surfaces.
> Last Updated: 2026-03-23

> 日期：2026-03-18
> 用途：把「先分類、後搬移」落成可執行清單。

---

## 1. 使用方式

1. 先依照本台帳標記檔案所屬 Zone。
2. 再決定是否需要重命名、搬移、合併。
3. 每次異動都更新 docs/INDEX.md 與 README 入口。

---

## 2. Zone 分類總表

### A. Canonical Specs（規範真源）

- docs/VTP_SPEC.md
- docs/SEMANTIC_SPINE_SPEC.md
- docs/AUDIT_CONTRACT.md
- docs/COUNCIL_RUNTIME.md
- docs/API_SPEC.md
- docs/CORE_MODULES.md
- docs/7D_AUDIT_FRAMEWORK.md
- law/docs/v1.2/vol-1.md
- law/docs/v1.2/vol-2.md
- law/docs/v1.2/vol-3.md
- law/docs/v1.2/vol-4.md
- law/docs/v1.2/vol-5.md

### B. Plans（執行計畫）

- docs/plans/architecture_blueprint_2026-03-18.md
- docs/plans/iu_oi_backplane_convergence_2026-03-18.md
- docs/plans/backend_persistent_storage_plan.md
- docs/plans/release_readiness_staging.md
- docs/plans/roadmap_2026q2_memory_governance.md

### C. Status / Reports（狀態與審計輸出）

- docs/status/repo_healthcheck_latest.md
- docs/status/refreshable_artifact_report_latest.md
- docs/status/memory_quality_latest.md
- docs/status/multi_agent_divergence_latest.md
- reports/test_coverage_latest.md
- reports/security_vulnerability_assessment_latest.md

### D. Archive（歷史封存）

- docs/archive/deprecated_modules/README.md
- docs/ARCHITECTURE_REVIEW_2026-02-13.md（建議後續歸檔）

---

## 3. 命名調整候選（先列，不立即改）

### 高優先（入口可讀性）

- docs/GITHUB_INTRO_DRAFT.md
  - 候選：docs/GITHUB_INTRO_v1.md

- docs/INDEX.md
  - 目前可維持，作為主入口

### 中優先（語義一致）

- docs/PHILOSOPHY.md / docs/PHILOSOPHY_EN.md
  - 建議補 cross-link，避免雙語分岔

- docs/ARCHITECTURE_REVIEW.md / docs/ARCHITECTURE_DEPLOYED.md
  - 建議在檔首標註「review/deployed」時態

---

## 4. 資料區管理建議（未來）

### 4.1 docs/status

- 保持 latest 快照命名模式
- 若要追歷史，放到 docs/status/history/（待建立）

### 4.2 memory

- 保留 runtime 內部資料，不作為外部規格來源
- 對外可引用時，改由 docs/status 產生摘要文件

### 4.3 reports

- 偏向審計與驗證輸出
- 能長期引用者，回填至 docs/ Canonical Specs

---

## 5. 本版界線

v1 只做三件事：

1. 分類可視化
2. 檔名規則先對齊
3. 入口文件先更新

不做：

- 一次性大搬檔
- 破壞既有連結
- 跨目錄激進重命名
