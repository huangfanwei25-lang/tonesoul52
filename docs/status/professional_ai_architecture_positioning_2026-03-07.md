# Professional AI Architecture Positioning (2026-03-07)

## Reading Notes
- document_type: architecture positioning memo
- note_date: 2026-03-07
- intent: explain what the system structurally is, not certify repo health
- not_for_use_as: substitute for CI, healthcheck, or release validation
- companion_docs:
  - `docs/status/professional_ai_architecture_review_2026-03-04.md`
  - `docs/status/repo_healthcheck_latest.md`
  - `docs/status/round2_handoff_framework.md`

## Scope
- 問題：語魂系統現在到底是什麼架構？
- 角度：以專業 AI 系統架構師視角，區分「文件中的理想架構」與「程式碼中的實際架構」。
- 目的：給出可落地的優化方向，並把脈絡留成可回讀筆記。

## Context Recovered
- 理論自述仍以 `DDD + Clean Architecture + CQRS` 為工程定位。
  - `docs/engineering/OVERVIEW.md:8`
- README 將系統描述為一條治理導向的推理鏈：
  - `User Input -> ToneBridge -> TensionEngine -> Council -> ComputeGate -> ResonanceClassifier -> Journal + Crystallizer`
  - `README.md:59`
- 實際上線主線由 API 直接建立 `UnifiedPipeline`，不是由明確的 application service / use case layer 驅動。
  - `api/chat.py:133`
  - `api/chat.py:137`
- `UnifiedPipeline.process(...)` 已經承擔路由、回復、上下文注入、張力計算、阻斷、內在審議、人格切換、記憶整合等多重責任。
  - `tonesoul/unified_pipeline.py:1217`
- `CouncilRuntime.deliberate(...)` 內含審議、仁慈審計、逃生閥、Genesis、VTP、自我記憶寫入、provenance 寫入。
  - `tonesoul/council/runtime.py:76`
- 記憶層同時存在 JSONL 與 SQLite 兩條主路，外加 crystallizer 與其他衍生記憶機制。
  - `tonesoul/memory/soul_db.py:328`
  - `tonesoul/memory/soul_db.py:479`
  - `tonesoul/memory/crystallizer.py:73`
- 另有一條離線演化管線 `yss_pipeline`，自己維護 run_dir、gate、evidence、skill promotion、memory compaction。
  - `tonesoul/yss_pipeline.py:66`
  - `tonesoul/yss_pipeline.py:793`

## Executive Judgment
- 語魂系統目前最準確的描述不是「純 Clean Architecture」，而是：
  - **治理優先的認知代理模組化單體**
  - **Governance-first cognitive agent modular monolith**
- 它已經形成四個清楚的平面，但還沒有被正式協議化：
  - **Runtime Plane**：即時推理與對話回應
  - **Governance Plane**：Council、Benevolence、Escape Valve、VTP、Genesis
  - **Memory Plane**：episodic / provenance / crystal / semantic / sqlite
  - **Evolution Plane**：YSS 離線證據、技能提升、壓測與工件生成

## What It Actually Is

### 1. Runtime Orchestrator Architecture
- 主線是一個 orchestrator-centered runtime。
- `UnifiedPipeline` 不是單一服務，而是把路由、治理、內在 deliberation、記憶注入與 LLM backend 協調在一起的「中央編排器」。
- 這讓系統能快速迭代，但也讓主流程變成高耦合、高責任密度的樞紐。

### 2. Governance-Centric Agent
- 語魂系統的真正核心不是生成模型，而是治理決策。
- `CouncilRuntime` 並不是輔助檢查器，它實際上是輸出合法性的決策核心。
- 換句話說，這個系統更像「被治理層包住的 agent runtime」，而不是「附帶 guardrail 的聊天系統」。

### 3. Dual Memory + Audit Architecture
- 它不是單純聊天歷史保存，而是把記憶、審計與演化混在同一個生態系裡。
- 目前記憶至少有幾種角色：
  - episodic memory：`self_journal`
  - provenance / responsibility trace：`provenance_ledger`
  - durable policy memory：`crystals`
  - queryable store：`JsonlSoulDB` / `SqliteSoulDB`
  - specialized memory：semantic graph / visual chain / openclaw memory
- 這是優勢，但也表示「資料模型尚未統一」。

### 4. Split-Brain Online/Offline System
- `UnifiedPipeline` 是線上對話主線。
- `yss_pipeline` 是離線治理與工件生成主線。
- 兩者目前是互補，不是同一套協議下的兩種執行模式。
- 這種狀態在研究期很常見，但在產品化時會造成 schema drift、評估漂移與心智模型分裂。

## Professional Strengths
- 有明確的治理核心，不是把 safety 當成後處理。
- 有可審計輸出，並持續把 verdict / provenance / self memory 寫回系統。
- 已具備 online path 與 offline evaluation path，這對高風險 AI 系統是正確方向。
- 系統不是只有 prompt engineering，而是有內部 state、memory、gate、role differentiation。

## Professional Weaknesses

### Weakness A: UnifiedPipeline Responsibility Density Too High
- `UnifiedPipeline.process(...)` 吞了太多 concern。
- 這會帶來三個問題：
  - 主線很難替換單一子系統
  - 觀測與除錯會沿著長函式堆疊進行
  - 線上延遲與離線邏輯容易互相污染

### Weakness B: Governance Logic Is Distributed, Not Kernelized
- 現在治理責任分散在：
  - `api/_shared/core.py`
  - `tonesoul/unified_pipeline.py`
  - `tonesoul/council/runtime.py`
- 結果是：
  - 同一個治理決策會在不同層重複包裝
  - contract 難以固定
  - API 形狀與 runtime semantics 容易分岔

### Weakness C: Memory Is Rich but Not Canonical
- 記憶很多，但 canonical schema 不夠清楚。
- 現況比較像多種記憶機制疊加，而不是單一 memory architecture。
- 這會讓以下事情越來越難：
  - 查詢一致性
  - replay 與 regression
  - 訓練資料導出
  - retention / compaction policy

### Weakness D: Online Runtime and YSS Evolution Drift
- `UnifiedPipeline` 與 `yss_pipeline` 都在做治理，但不是同一條 contract。
- 如果不收斂，未來會出現：
  - 線上回應的欄位與離線評估欄位不同
  - promotion / replay 不能直接回灌主線
  - 同一個概念在兩條系統中被不同名稱表示

### Weakness E: Typed Contract Coverage Is Still Too Thin
- 很多關鍵資料仍以 `Dict[str, Any]` 在模組間傳遞。
- 這在探索期很快，但對專業 AI 平台來說，之後會變成最主要的演化阻力。

## Recommended Target Positioning
- 我會把語魂系統正式定位為：

```text
Governance-First Agent Platform

Ingress Layer
  -> Runtime Orchestrator
  -> Governance Kernel
  -> Memory Service
  -> Model Router
  -> Audit/Event Stream

Offline Plane
  -> Replay / Evaluation
  -> Skill Promotion
  -> Memory Compaction
  -> Architecture Reports
```

- 也就是：
  - **線上主線負責做決策**
  - **離線主線負責驗證、學習、收斂**
  - **兩者共享 schema、事件與治理 contract**

## Optimization Plan

### P0. 定義 Canonical Runtime Contract
- 先不要再加新模組，先定義主線共用資料契約：
  - `RuntimeRequest`
  - `RuntimeContext`
  - `GenerationDraft`
  - `GovernanceDecision`
  - `MemoryWriteSet`
  - `RuntimeResponse`
- 目的：
  - 讓 `UnifiedPipeline`、API、YSS、報表工件都說同一種語言
- 這是所有後續優化的基礎。

### P0. 把治理層抽成 Governance Kernel
- 把目前散落在 API / Pipeline / Council 的治理責任收斂成單一核心：
  - policy selection
  - council evaluation
  - fail-closed / fail-open decision
  - provenance event emission
  - self-memory write policy
- `UnifiedPipeline` 應該負責 orchestration，不應再直接承擔完整治理邏輯。

### P1. 重新切分 Memory Topology
- 我會把記憶收斂成三層，而不是多個平行功能：
  - **Working Memory**：當前回合與短視窗狀態
  - **Episodic / Audit Memory**：journal、provenance、decision trace
  - **Semantic / Policy Memory**：crystals、semantic graph、retrieval index
- 每次 runtime 只產生一份 `MemoryWriteSet`，由單一 writer 分發到不同存儲。
- 好處：
  - 寫入策略可測試
  - retention 容易治理
  - 回放容易做

### P1. 分離 Model Routing and Cognitive Logic
- 目前 LLM backend 選擇、fast path、compute gate、local fallback 與 cognitive pipeline 很靠近。
- 我會拆成：
  - `ModelRouter`
  - `GenerationAdapter`
  - `GovernedResponseAssembler`
- 這樣可以把：
  - provider failover
  - latency / budget routing
  - governance escalation
  分開評估。

### P2. 建立 Online/Offline Shared Replay Contract
- `yss_pipeline` 不應該只是另一套流程，而應該是 runtime 的 replay / evaluation plane。
- 我會要求：
  - 線上每次決策都能輸出可 replay 的最小事件包
  - 離線 replay 能重新跑 governance kernel
  - promotion artifact 可直接反饋到 runtime policy

### P2. 把 Observability 從報表提升為事件流
- 現在已有很多 report artifact，這很好。
- 下一步應該是讓 report 來自統一事件流，而不是各腳本各自推導。
- 建議增加：
  - trace id / intent id / conversation id 全鏈路貫通
  - stage latency
  - policy version
  - model version
  - memory write summary
  - governance decision reason code

## Suggested Near-Term Execution Order
1. 先定義 canonical runtime schema，禁止再新增匿名 dict 欄位。
2. 抽出 governance kernel，把 API 與 pipeline 的治理責任集中。
3. 把 memory write path 收斂成單一 writer。
4. 讓 `yss_pipeline` 轉為 runtime replay/eval plane，而不是平行宇宙。
5. 最後再擴展新的人格、skill promotion、multi-agent route。

## Bottom Line
- 語魂系統已經不是簡單聊天系統，而是具備治理內核、審計記憶、演化工件的 agent platform 原型。
- 它最大的優勢是：**治理是第一級公民**。
- 它最大的結構風險是：**主線編排、治理、記憶、離線演化已經長出來，但還沒被一套明確協議統一起來**。
- 專業角度下，現在最值得做的不是再加能力，而是把這些能力收斂成可驗證、可重播、可維運的架構。
