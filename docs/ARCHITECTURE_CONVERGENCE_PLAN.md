> [!NOTE]
> **Superseded by [RFC-009](RFC-009_Context_Engineering_Pivot.md)**. This document is retained for historical reference.

# ToneSoul 架構收斂企劃書（整合審計版）

> Purpose: historical convergence plan describing how earlier ToneSoul architecture variants were intended to unify.
> Last Updated: 2026-03-23

**版本**: v2  
**日期**: 2026-02-14  
**狀態**: Draft for Execution  
**來源基線**:
- 測試收斂基線：`python -m pytest --collect-only -q` => `841 tests collected`
- 目前主線狀態：Phase 99 已完成（custom-role council contract coverage）
- 舊版文件：`docs/INTEGRATION_AUDIT_DRAFT.md`、舊版 `RFC-002` 草案

---

## 1) 一句話結論

ToneSoul 已完成「多人格審議」與「蜂群治理」的關鍵地基，但仍存在 **執行層（UnifiedPipeline）與演化層（yss_pipeline）上下文模型分裂**、以及 **Trinket Protocol 仍停留在概念層** 的收斂缺口。  
下一步不是再加新模組，而是先做 **協議化與對齊化**。

---

## 2) 現況驗證（修正舊審計的過時判斷）

### 2.1 生產路徑（L1 事實）
- `/api/chat` 由 `apps/api/server.py` 實際呼叫 `tonesoul.unified_pipeline.create_unified_pipeline()`。
- 主流程為 `UnifiedPipeline.process(...)`，已包含：
  - persona/context 注入
  - GraphRAG / semantic trigger / cross-session recovery
  - council deliberation + custom roles
  - semantic contradiction / visual chain capture

### 2.2 `UnifiedCore` 不是純殭屍，但不是主線
- 舊說法「可直接刪除」不精確。  
- 實際上 `UnifiedCore` 仍被以下路徑引用：
  - `tonesoul/tonesoul_llm.py`
  - `tonesoul/self_test.py`
  - `tests/test_unified_core.py`
  - `tests/test_unified_core_properties.py`
- 正確策略應為：**標記邊界 + 去主線化 + 漸進淘汰**，不是立即硬刪。

### 2.3 `yss_pipeline` 與主線仍有語義漂移
- `yss_pipeline` 為完整離線治理/證據/門控流程（M0-M5 風格），但沒有共用 `UnifiedPipeline` 的 request schema。
- 現況是「互補」，不是「一致」。  
- 這是目前收斂工作的主要工程缺口之一。

---

## 3) 語魂系統框架（更新版）

## 3.1 Runtime Plane（對話即時層）
- 入口：`apps/web` -> `/api/chat` -> `UnifiedPipeline`
- 核心子系統：
  - ToneBridge（語氣/動機）
  - Deliberation（內在聲部）
  - CouncilRuntime（審議與裁決）
  - Persona custom roles（動態角色）
  - SemanticGraph + VisualChain（語義與視覺記憶）

## 3.2 Governance Plane（治理與審計層）
- CI/Healthcheck：
  - `test.yml`
  - `semantic_health.yml`
  - `persona_swarm.yml`
  - `repo_healthcheck.yml`
- Blocking contracts：
  - commit attribution
  - docs consistency
  - layer boundaries
  - external source registry
  - persona swarm readiness gate

## 3.3 Evolution Plane（演化與離線層）
- `yss_pipeline.py` + `yss_gates.py`
- evidence summary / tech trace / skill promotion / compaction
- 角色：離線驗證、證據沉澱、策略演化，不直接替代即時主線

---

## 4) TEST 內容盤點（841 tests）

## 4.1 覆蓋輪廓
- 測試檔案數：`127`
- 收集總數：`841`
- 含高風險區塊：
  - red-team API hardening
  - council / guardian / VTP
  - workflow contracts（CI 配置即程式契約）
  - swarm framework + dispatch + runner
  - persona custom role council（新增 19 tests）

## 4.2 新增且關鍵的保護牆
- `tests/test_custom_role_council.py`：
  - `create_from_custom_role`
  - `create_custom_council`
  - unknown perspective fallback semantics
  - evaluate baseline behavior

## 4.3 當前測試風險訊號
- `docs/status/multi_persona_eval_latest.json` 仍是空值占位（A/B/C 指標未灌入真實窗口資料）。
- repo health artifact 部分仍停在較舊測試數（例如 819），代表「報表節奏」與「主線節奏」有時差。

---

## 5) 多人格審計框架現況

## 5.1 已落地
- Tri-persona deliberation（既有）
- User-defined custom role council（Phase 96/99）
- Persona swarm framework（Phase 82-90）
- Gate 指標：
  - safety_pass_rate
  - swarm_score
  - decision_support
  - token_latency_cost_index
  - guardian fail-fast consistency

## 5.2 尚未落地到可生產決策的部分
- A/B/C 連續窗口 promotion 邏輯尚未接到真實資料流（目前多為框架與工件）
- 「高張力動態調度（Trinket）」尚未成為 `UnifiedPipeline` 明確協議
- custom roles 目前主要是「審議輸入擴展」，還不是「工具可執行代理」

---

## 6) 舊概念整合：Trinket Protocol（工程化版本）

你提出的韋小寶隱喻可以保留，但需轉為可審計協議。  
核心原則：**靈活不等於規避責任**。

## 6.1 協議四條（可實作）
1. Layer Decoupling  
   - 每個輸出片段標註 L1/L2/L3 層級來源，禁止跨層偷渡。
2. Is-Ought Monitor  
   - 凡是價值判斷，強制標註價值前提與來源（不可偽裝成客觀事實）。
3. Currency Audit  
   - 監控術語密度，超閾值觸發白話重寫。
4. Responsibility Trace  
   - 每次「非標準路徑」必須有 trace：觸發原因、風險、回退條件、人工接手點。

## 6.2 動態調度狀態機（A/B/C）
- `Resonance`（低張力）: A 模式，標準路徑
- `Tension`（中張力）: B 模式，責任鏈審計 + 多路徑比較
- `Conflict`（高張力）: C 模式，守護者策略（限制輸出/轉人工）

## 6.3 禁止事項（醫療/合規場景）
- 不允許把「高風險規避」包裝成「技術升級」後直接執行。  
- 高風險場景只能輸出：風險揭露、替代路徑比較、合規核准/專家升級流程。

---

## 7) 收斂路線圖（Phase 100）

## 7.1 Phase 100A: 協議定錨（Spec First）
- 產物：
  - `docs/governance/TRINKET_PROTOCOL_SPEC.md`
  - L1/L2/L3 標註 schema
  - dispatcher state contract（A/B/C）
- 成功標準：
  - 有可機器檢查的 contract
  - docs consistency 納入檢查

## 7.2 Phase 100B: Runtime 接線（UnifiedPipeline）
- 產物：
  - `detect_semantic_tension()`（明確輸入/輸出）
  - dispatcher state 路由（A/B/C）
  - trace payload 落地到 verdict metadata
- 成功標準：
  - 新增 runtime contract tests（張力升降級、fail-fast、一致性）

## 7.3 Phase 100C: Evolution 對齊（YSS Wrapper）
- 產物：
  - yss 與 unified 的 shared context schema adapter
  - offline eval 可回灌 A/B/C metrics artifact
- 成功標準：
  - `multi_persona_eval_latest.json` 不再是 null 占位
  - 主線與離線評估欄位一致

## 7.4 Phase 100D: 多人格能力升級（可選）
- 產物：
  - custom role -> tool proposal -> guarded execution（僅在安全條件下）
- 成功標準：
  - 每一步有權限邊界 + 可追蹤審計

---

## 8) 決策建議（給目前專案）

1. **不要立即刪 `UnifiedCore.py`**  
先做「去主線化標記」與遷移計畫，待引用清零後再移除。

2. **Trinket 先做協議，不先做花式行為**  
先有審計欄位與狀態機，再接創意路徑。

3. **先補資料閉環，再談模型人格擴張**  
把 `multi_persona_eval_latest.json` 真實化，否則 promotion 只是口號。

4. **把「蜂群蓋輾」落為工程語言**  
用 gate、contract、trace，避免只停留在隱喻層。

---

## 9) 附錄：本版與舊版差異
- 舊版「UnifiedCore 立即刪除」-> 新版改為「邊界化 + 漸進淘汰」
- 舊版重哲學敘事 -> 新版新增測試盤點、工件現況、可執行 phase
- 舊版未對齊最新進度 -> 新版對齊 Phase 96-99、841 tests、swarm readiness
