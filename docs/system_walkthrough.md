# ToneSoul System Walkthrough
# 語魂系統走讀（2026-02-14）

> Version: 1.0.0  
> Scope: 對齊目前主線實作（Phase 1-100 已落地項）  
> Baseline: `python -m pytest -q` => `849 passed`（2026-02-14）

---

## 1. 你現在看到的是什麼系統

ToneSoul 目前不是單一「聊天模型包裝器」，而是三層結構：

1. Runtime Plane（即時對話層）
   - Web/UI -> API -> `UnifiedPipeline.process(...)`
   - 包含：persona 注入、Council 審議、Graph/Visual 記憶查詢、輸出裁決
2. Governance Plane（治理與門檻層）
   - CI workflows + 檢查腳本 + blocking contracts
   - 包含：docs consistency、commit attribution、外部來源信任、swarm readiness
3. Evolution Plane（離線演化層）
   - `yss_pipeline.py` + gates
   - 用於離線驗證、證據沉澱、策略演化，不直接替代即時主線

---

## 2. 目前主線狀態（快照）

- Program Board：Level 1 / 2 / 3、Phase A/B/C、Phase 82-100 均已完成。
- 最新測試：`849 passed`。
- Backlog Radar 主要項目已收斂，原先 backend persistence 阻塞已在 2026-02-14 重跑驗收解除：
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com --timeout 40` => pass。
- 其他 backlog（Chat UI、roadmap 勾選、semantic-control 優先序、release staging）已收斂。

---

## 3. 一次請求如何流過系統（Runtime）

1. 前端送出請求到 `/api/chat`（web route）。
2. 後端 API 進行 payload 與 persona 驗證（fail-closed）。
3. `UnifiedPipeline` 載入上下文：
   - 使用者訊息
   - 歷史記憶/圖鏈
   - 自訂角色（custom roles）與附件摘錄（allowlist + budget）
4. 進入調度與審議：
   - dispatcher trace（Resonance / Tension / Conflict）
   - Council runtime（guardian/analyst/critic/advocate + custom roles）
5. 產生裁決與回覆：
   - response
   - 可審計 metadata（含 dispatch trace）
6. 寫入觀測與工件：
   - transcript / status artifact / 相關記憶資料

---

## 4. 多人格與自訂角色（你最常會改到）

### 4.1 預設多視角
- Guardian：安全與阻擋
- Analyst：事實與一致性
- Critic：盲點與反例
- Advocate：用戶目標與可用性

### 4.2 自訂角色（Phase 96-99）
- 支援 `persona.custom_roles`
- 每個角色可帶：
  - `name`
  - `description`
  - `prompt_hint`
  - `attachments`
- 角色與附件都走 schema 驗證與安全限制：
  - role/attachment 數量上限
  - 路徑 allowlist + traversal guard
  - excerpt 預算控制

---

## 5. 記憶與跨 session

目前主線有三種常用記憶能力：

1. 視覺鏈（VisualChain）
   - 快照 + 張力資料 + frame metadata
2. 語義圖譜（SemanticGraph）
   - 多跳檢索與矛盾訊號
3. 跨 session 恢復（Level 3 / 3b）
   - 以圖鏈/記憶訊號補回前情，不只依賴單輪輸入

---

## 6. 治理與檢查（CI/Gates）

核心 blocking 面向：

1. 程式與測試
   - pytest、workflow contract tests
2. 文件與一致性
   - `verify_docs_consistency.py`
3. 提交歸屬
   - `verify_commit_attribution.py`（需 `Agent` / `Trace-Topic` trailers）
4. 安全與來源
   - red-team 測試
   - external source registry allowlist gate
5. 蜂群狀態
   - persona swarm framework artifact + strict gate

---

## 7. 舊系統相容（Legacy）

### 7.1 `UnifiedCore`
- 目前標記為 `legacy_non_runtime`。
- 不是 API 主線，但仍有少數引用（測試/舊工具）。
- 策略是「去主線化 + 漸進淘汰」，不是立即刪除。

### 7.2 舊檢查腳本
- 根目錄已提供相容入口：
  - `scripts/verify_fortress.py`
  - `scripts/verify_metabolism.py`
  - `scripts/verify_identities.py`
- `scripts/legacy/*.py` 保留 shim，舊指令可直接轉送到新入口。
- 缺少 legacy runtime 或 key 時預設 `SKIP`（可用 strict 參數強制 FAIL）。

---

## 8. Walkthrough 實作順序（建議）

如果你今天要接手開發，照這個順序：

1. 看任務盤點：`task.md`
2. 看收斂藍圖：`docs/ARCHITECTURE_CONVERGENCE_PLAN.md`
3. 看 release staging：`docs/plans/release_readiness_staging.md`
4. 跑最小健康檢查：
   - `python scripts/verify_docs_consistency.py`
   - `python -m pytest tests/test_run_repo_healthcheck.py -q`
5. 再跑全量：
   - `python -m pytest -q`

---

## 9. 當前待辦（真正未完成）

1. 發布後續維運（非阻塞）
   - 文件：`docs/plans/release_readiness_staging.md`
   - 狀態：v0.1.0 tag 與發版產物已完成，後續以例行回歸與監控為主

---

## 10. 入口索引

- 任務盤：`task.md`
- 架構收斂：`docs/ARCHITECTURE_CONVERGENCE_PLAN.md`
- 本文件：`docs/system_walkthrough.md`
- Release staging：`docs/plans/release_readiness_staging.md`
- Backend persistence 驗收：`docs/plans/backend_persistence_acceptance_checklist.md`

---

*ToneSoul 的主線重點：先有可審計 contract，再擴展人格與行為。*
