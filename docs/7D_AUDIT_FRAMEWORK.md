# 7D AI Audit Framework / 七維 AI 審計框架

> Purpose: explain ToneSoul's seven-dimensional audit model for verification, accountability, and system calibration.
> Last Updated: 2026-03-23

> **Engineering paranoia is a feature, not a bug.**  
> 把「懷疑」制度化，才能把「信任」工程化。

---

## 為什麼是 7D

ToneSoul 的目標不是只產生「看起來聰明」的回答，而是建立可驗證、可追責、可持續校準的系統。  
7D（七維）是把這個目標拆成可觀測的七個維度：

```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ TDD │ RDD │ DDD │ XDD │ GDD │ CDD │ SDH │
│Test │Red  │Data │Expl │Gov  │Ctx  │Sys  │
│Driven│Team│Driven│Driven│Driven│Driven│Health│
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

---

## 七維定義

| 維度 | 全名 | 核心問題 | ToneSoul 目前落點 |
|---|---|---|---|
| TDD | Test-Driven Development | 功能是否可重現驗證？ | blocking tier + 主 CI full regression |
| RDD | Red Team-Driven Defense | 是否能抵抗對抗性輸入？ | baseline 已落地，持續補強 |
| DDD | Data-Driven Discipline | 資料源是否乾淨、可追溯？ | 討論通道雙流（raw/curated）審計 + 7 天 stale SLA |
| XDD | Explainability-Driven Design | 決策理由是否可讀可查？ | Council transcript + verdict |
| GDD | Governance-Driven Decision | 權責邊界是否明確？ | Genesis + responsibility tier |
| CDD | Context-Driven Deliberation | 語境切換是否一致可控？ | Orchestrator + route policy |
| SDH | System Dynamic Health | 系統是否在壓力下維持可用？ | health/smoke + fallback policy |

---

## 各維度審計要點

### TDD
- 每次變更需有對應測試或回歸證據。
- 禁止以關閉測試取代修復。
- `7D` 的 TDD gate 只負責 blocking tier；完整 `pytest tests -q` 仍留在主 CI 與 burn-in，避免 operational audit 重複跑第二條 full suite。

### RDD
- 對 prompt injection、權限繞過、輸出誘導建立測試樣本。
- 需有「失敗可見」機制，不允許靜默風險。

### DDD
- 資料來源、寫入流程、轉換規則可追溯。
- 對記憶與討論通道做格式一致性審計（如 JSONL audit）。

### XDD
- 關鍵決策需包含結構化理由（非純文字宣告）。
- 不確定性需顯式輸出，不以語氣掩蓋。

### GDD
- 決策應標記責任層級（tier）與歸因（is_mine / genesis）。
- 高責任輸出需留存 provenance 記錄。

### CDD
- 路由策略需顯式（flag 化）且可測。
- fallback 必須可辨識，避免假成功。

### SDH
- 提供端到端 smoke 檢查（web + backend + health）。
- 錯誤需可觀測（狀態碼、error id、log 入口）。
- CI gate 目前維持 `SOFT_FAIL`（降低環境噪音造成的誤阻擋）。

### Systemic Betrayal Gate
- 高破壞性操作必須要求使用者二次確認。
- 未確認前不得執行操作，需回傳 `confirmation_required`。

---

## 三層驗證觀

| 層級 | 名稱 | 要求 |
|---|---|---|
| L1 | 本體事實 | 規則必須落成程式與測試 |
| L2 | 模型假設 | 假設需可被審計與反駁 |
| L3 | 敘事修辭 | 未經驗證的敘事不得當成事實 |

---

## 當前狀態（2026-02-08）

| 維度 | 狀態 | 說明 |
|---|---|---|
| TDD | 強 | 全量測試可運行（以 CI 報告為準） |
| RDD | 中強 | 已有 red-team baseline，門檻採案例數（最小 20 tests） |
| DDD | 中 | 討論通道可審計，且啟用 7 天資料新鮮度規則 |
| XDD | 中強 | verdict 與 uncertainty 已結構化 |
| GDD | 中強 | responsibility tier 與 genesis 已接線 |
| CDD | 中強 | backend-first + fallback 策略已旗標化 |
| SDH | 中強 | web/backend smoke 已納入 CI |

**優先補強順序**：`RDD -> DDD -> SDH`（壓力情境）。

---

## 下一步

- 見 `docs/7D_EXECUTION_SPEC.md`：把 7D 轉成可執行 checklist 與 CI gate。
- 狀態工件寫入 `docs/status/`（`7d_snapshot.json`、`monthly_consolidation_report.json`）作為機器可讀來源。
