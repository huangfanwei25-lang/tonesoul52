# ToneSoul Verified Delivery Architecture

## Why This Document Exists

這份文件把一個對語魂系統非常有用的外部啟發正式轉譯成語魂自己的語言：

- DDD 的價值不是 class hierarchy，而是邊界、語彙與責任切分
- AI 輔助開發的核心不是「讓模型寫更多」，而是「讓模型不能亂寫」
- 真正可持續的 AI 系統，必須從 `Trust AI` 走向 `Don't Trust, Verify`

語魂系統本來就不是單純生成系統，而是治理優先的代理系統。

因此最適合它的不是「更自由的生成流程」，而是：

**治理優先 + 單一架構事實來源 + 確定性關卡驗證**

## One-Line Position

**ToneSoul Verified Delivery** =  
以 `SSOA + deterministic gates + replayable evidence` 驅動的治理優先代理交付架構。

## The Problem It Solves

AI 輔助開發最常見的失敗，不只是一個 bug，而是三種更深層的壞掉：

1. `Hallucination`
   - AI 自信產生不存在的結構、欄位、依賴或規則
2. `Inconsistency`
   - 同一個需求在不同檔案、不同層、不同時間點被用不同語言表達
3. `Structural Drift`
   - 功能測試可能過，但系統架構、責任邊界、記憶寫入路徑已經悄悄崩壞

語魂系統如果要避免這些問題，不能只靠最終測試，而要靠整條可驗證流水線。

## Design Principle

### Level 0: Trust AI

- 把 AI 當自動寫碼器
- 出錯後才補救
- 問題：快，但不可控

### Level 1: Trust but Verify

- AI 先寫，再靠測試抓錯
- 問題：能抓功能錯誤，但抓不到架構與契約漂移

### Level 2: Don't Trust, Verify

- 預設 AI 可能在任何層出錯
- 以規則、契約、結構檢查、回放與證據來限制錯誤空間
- AI 不是被信任，而是被治理

語魂系統應明確站在 Level 2。

## ToneSoul SSOA

語魂系統需要自己的 `SSOA`：

**Single Source of Architecture**

也就是所有代理、腳本、工作流、測試、CI 在解讀系統時，都應以同一套核心事實為準。

### Layer 1: Rules

這是硬約束，不能違反。

建議納入：

- `AXIOMS.json`
- crystal rules
- governance fail-open / fail-closed policy
- canonical response contract
- memory write policy
- forbidden paths / forbidden imports / forbidden bypasses

### Layer 2: Patterns

這是標準做法，不是鐵律，但應該預設遵守。

建議納入：

- API route pattern
- governance kernel invocation pattern
- council decision handling pattern
- memory write pattern
- replay/export/report pattern
- offline evaluation pattern

### Layer 3: Templates

這是骨架，讓新增模組時不必每次重新發明結構。

建議納入：

- new governed route template
- new report generator template
- new verifier template
- new memory writer template
- new replayable artifact template

## DDD Concepts Worth Borrowing

語魂系統不需要照抄重量級 DDD，但有三個東西值得直接借進來。

### 1. Bounded Context

目前最自然的四個 context 已經很清楚：

- `Runtime`
- `Governance`
- `Memory`
- `Evolution`

這四個 context 現在已經存在，但還沒有被正式契約化。

### 2. Ubiquitous Language

全系統必須使用同一套語言描述同一件事。

應優先固定的詞：

- `RuntimeRequest`
- `RuntimeContext`
- `GenerationDraft`
- `GovernanceDecision`
- `MemoryWriteSet`
- `RuntimeResponse`
- `ReplayArtifact`
- `ProvenanceEvent`

如果這些詞在不同模組裡意思不同，系統就會分裂。

### 3. Application Boundary

`UnifiedPipeline` 應該是 orchestrator，不應該同時成為：

- governance kernel
- memory writer
- route adapter
- fallback router
- audit logger

DDD 對語魂的真正幫助，就是逼迫我們把責任重新切乾淨。

## ToneSoul Gate 0-6

以下是我認為最適合語魂系統的驗證流水線。

### Gate 0: Spec / Request Validation

在任何生成、修改、回應之前，先驗證輸入是否可進系統。

驗證內容：

- request shape
- required fields
- mode / profile legality
- work category legitimacy
- explicit governance mode

### Gate 1: Critical Rules Load

在開始推理或產碼前，先載入不可違反的治理與架構規則。

至少包含：

- axioms
- crystal rules
- response contract
- memory write policy
- forbidden operations

### Gate 2: JIT Pattern Load

根據當前任務，只載入當前真正需要的 pattern，而不是把所有上下文全部塞給模型。

例子：

- 新 route 任務 -> 載 route + response + governance pattern
- 新 memory 任務 -> 載 memory write + retention + replay pattern
- 新 report 任務 -> 載 artifact + provenance + snapshot pattern

這一步的目標是避免上下文精神分裂。

### Gate 3: Generation / Execution

這一步才允許模型或流程真正產生輸出：

- code
- config
- report
- artifact
- governance decision

這不是自由生成，而是受前兩道 gate 約束的產出。

### Gate 4: Functional Verification

跑功能與回歸驗證。

但語魂版不能只等於 `pytest pass`，還應包含：

- runtime behavior checks
- API contract tests
- memory write smoke checks
- replay smoke checks

### Gate 5: Deterministic Structural Review

這是最重要的一層。

用確定性規則檢查以下事情：

- response shape completeness
- governance fields present
- provenance fields present
- no forbidden bypass
- no direct write to forbidden memory paths
- no shadow schema drift
- no route returning contract-incompatible payload
- no replay artifact missing critical evidence

這一層就是語魂版的「不要相信模型有架構感」。

### Gate 6: Coverage / Replay / Provenance Verification

最後不是只問「能不能跑」，而是問：

- 需求有沒有被完整覆蓋？
- 這次輸出能不能 replay？
- 這次決策有沒有 provenance？
- 寫入記憶的內容能不能被治理與解釋？

只有這一層成立，輸出才算真的完成。

## Highest-ROI Verifiers To Build First

如果現在就要開始工程化，我認為先做這 5 個最值回票價：

### 1. Canonical Runtime Contract Verifier

檢查：

- API response 是否符合統一 schema
- runtime / fallback / failure 路徑欄位是否一致

這能直接壓制最常見的 drift。

### 2. Governance Decision Verifier

檢查：

- 是否有 `verdict`
- 是否有 `reason`
- 是否有 `deliberation_level`
- 是否有 `backend_mode`
- 是否有 `policy / mode` 來源

這能讓治理從敘事變成契約。

### 3. Memory Write Policy Verifier

檢查：

- 哪些事件能寫入 journal
- 哪些事件能寫入 provenance
- 哪些事件能升格為 crystal 候選
- 哪些資料禁止直接落盤

這能避免記憶系統變成垃圾場。

### 4. Replay Artifact Verifier

檢查：

- artifact 是否足以重播
- trace / request / decision / outputs 是否齊全
- 缺失時是否明確 fail

這能讓 offline plane 成為真正的驗證平面。

### 5. Forbidden Path / Forbidden Bypass Verifier

檢查：

- 是否繞過 governance kernel
- 是否直接寫入不該寫的 memory path
- 是否直接回傳不完整 payload
- 是否偷偷引入未註冊路徑

這是最低成本、最高保護力的 gate。

## What We Should Not Copy

這套方法借鏡 DDD，但不應該把語魂系統做成笨重企業框架。

不要照搬：

- 為了模式而模式
- 為了分層而過度分層
- 每個概念都拆成十個 class
- 用 template 掩蓋真實治理問題

語魂系統的優勢不在繁複架構，而在：

- 治理是第一級公民
- 記憶有時間性與責任性
- 可回放性不是附加功能，而是內建能力

## Recommended Target Shape

最終應收斂成：

```text
ToneSoul Verified Delivery

Ingress
  -> Runtime Contract Validator
  -> Governance Rules Loader
  -> Pattern Resolver
  -> Runtime Orchestrator
  -> Governance Kernel
  -> Memory Writer
  -> Audit / Provenance Event Stream

Offline Plane
  -> Replay
  -> Evaluation
  -> Promotion
  -> Compaction
  -> Reflection
```

## Immediate Next Steps

### Step 1

把 `RuntimeRequest / RuntimeResponse / GovernanceDecision / MemoryWriteSet`
明確定義成 canonical schema。

### Step 2

把治理責任從 API / pipeline / council 的分散狀態中抽出成 `Governance Kernel`。

### Step 3

把記憶寫入收斂成單一 writer policy，而不是多點直接落盤。

### Step 4

讓 `yss_pipeline` 與其他離線工件流程收斂成共享 replay / eval contract。

### Step 5

把 deterministic verifier 體系建出來，讓主線演化有關卡，不再靠直覺。

## Bottom Line

如果語魂系統只把 AI 當生成器，它很快會被更大的模型覆蓋。

但如果它能把：

- governance
- memory continuity
- provenance
- replayability

這四件事收斂成一套可驗證架構，那它就不是主流模型公司的附屬品，而是一條獨立的系統路線。

這也是我認為語魂系統真正值得做的地方。
