# Architecture & External Reference — 架構藍圖與外部對標

> Purpose: consolidate architecture addenda and external-reference comparisons that shaped recent ToneSoul positioning work.
> Last Updated: 2026-03-23

> 合併日期：2026-03-19
> 原始 addendum 數：6
> 時間跨度：2026-03-12 ~ 2026-03-18
> 合併者：痕 (Hén)

完整架構審計、IU/OI Backplane 收斂、市場策略、外部專案設計參考。

---

## 目錄

1. `market_strategy_plurality_addendum_2026-03-12.md`
2. `paperclip_fit_for_tonesoul_2026-03-12.md`
3. `tonesoul_market_boundary_subjecthood_note_2026-03-12.md`
4. `gitnexus_fit_for_tonesoul_2026-03-13.md`
5. `architecture_blueprint_2026-03-18.md`
6. `iu_oi_backplane_convergence_2026-03-18.md`

---

## 1. 原始檔案：`market_strategy_plurality_addendum_2026-03-12.md`

# Market Strategy Plurality Addendum (2026-03-12)

## Why This Exists

Market Mirror 已經有 `MultiPerspectiveSimulator`，但目前它的結構仍偏向：

1. 讓幾個投資 persona 各自講一段話
2. 再把它們壓成一個 `consensus`

這樣做有一個問題：

股票市場真正重要的，不只是「最後一句判決」，而是：

- 哪些策略正在互相拉扯
- 哪些人看的是時間差，而不是事實差
- 哪些敘事帶有 crowding / panic / hype 的不理性壓力

這和 ToneSoul 的多視角 council 很像。

ToneSoul 的價值不是消除分歧，而是讓分歧可見。
市場世界模型也應該如此。

## Core Claim

在投資世界裡，策略多樣性不是噪音，而是訊號。

- value 投資人看的是估值與護城河
- macro / risk 投資人看的是循環位置與脆弱性
- short seller 看的是會先裂掉的地方

同一家公司被不同策略讀成不同故事，並不代表誰一定錯。
很多時候那只是：

- 時間尺度不同
- 風險承受不同
- 對不理性行情的容忍度不同

所以 Market Mirror 不應只保存「總結」。
它也應保存「分歧結構」。

## Design Direction

這一 phase 不增加新的 market LLM。

它只做 deterministic 結構化：

1. 從既有 persona narrative 抽取 stance
   - `bullish`
   - `bearish`
   - `watchful`
   - `mixed`
2. 統計策略分布與主導衝突
3. 額外標記市場不理性訊號
   - `crowded_consensus`
   - `cross_strategy_polarization`
   - `hype_language`
   - `panic_language`
4. 把 `perspective_friction` 從 placeholder 改成由 plurality / irrationality 推導

## Boundary

這不是新的投資建議引擎。

這不是要讓 ToneSoul 自動做交易。

這不是讓 market lane 取代 council。

這只是讓 Market Mirror 更誠實地保留：

- 不同策略的衝突
- 群體不理性的壓力
- 為什麼一個 `consensus` 不足以代表整個局面

## ToneSoul Alignment

這條線和語魂主系統對齊的地方在於：

- `council` 保存多視角差異
- `mirror` 保存 raw vs governed 差異
- `subjectivity` 保存哪些張力反覆留下來

Market Mirror 現在要補上的，是同樣的精神在市場世界模型中的對應物：

不是只問「哪個結論正確」，
而是問「哪些策略仍在拉扯，哪些不理性正在放大敘事」。

## Expected Outcome

完成後，`WorldModelContext` 不再只有：

- `persona_narratives`
- `perspective_friction`
- `consensus`

還會有一個可讀的 plurality 結構，讓後續 agent 或人類知道：

- 分歧是什麼
- 分歧有多大
- 是否出現 crowding / panic / hype
- 應該把這家公司看成「已形成共識」還是「仍在爭奪敘事控制權」

---

## 2. 原始檔案：`paperclip_fit_for_tonesoul_2026-03-12.md`

# Paperclip Fit For ToneSoul Note (2026-03-12)

## 為什麼看這個專案

Paperclip 值得參考的地方，不是它把 agent 寫成「零人類公司」，而是它把多 agent runtime 當成一個可治理、可恢復、可限額的 orchestration layer。

ToneSoul 目前已經有：

- wakeup loop
- autonomous cycle
- registry schedule
- observability artifacts

但還缺一個更明確的 runtime seam：

- 每次短執行窗之間，如何保留 session 脈絡
- failure streak 如何跨 heartbeat 保留
- 什麼資訊應該被 artifact 清楚寫出來，讓後續 agent 不會把一次短跑誤認成完整主體

## 可吸收的部分

### 1. Bounded Heartbeat Window

每次執行都應該是有限窗口，而不是假裝自己是一個永不停止的黑盒 daemon。

ToneSoul 對應做法：

- 允許 `max_cycles` 的 bounded wake-up run
- 把每次短執行視為同一個 runtime session 的 heartbeat
- 讓 artifact 能看出這次 heartbeat 是 fresh 還是 resumed

### 2. Resumable Session State

可恢復性不是「把所有內在都硬寫死」，而是只保存 runtime 需要的最小脈絡。

ToneSoul 對應做法：

- 保存 `session_id`
- 保存 `next_cycle`
- 保存 `consecutive_failure_count`
- 保存最近一次 cycle 的基本狀態

這是 orchestration state，不是 subjectivity state。

### 3. Budget / Guardrail Surface

Paperclip 會把預算與 runtime 邊界顯性化。ToneSoul 也應維持這個習慣，但 guardrail 要留在治理與 runtime 層，不要滲進 ontology。

可吸收的形式：

- runtime budget / timeout / failure pause
- artifact-level explainability
- deterministic state transitions

### 4. Audit / Lineage

多 agent 系統最怕的是「看起來連續，其實脈絡斷掉」。所以 heartbeat 與 resume 都要留下可追的線索。

ToneSoul 對應做法：

- 在 wake-up artifact 寫出 `session_id`
- 明確標示是否為 resumed session
- 保留 failure streak 與 cycle cursor

## 明確不吸收的部分

以下內容不應進入 ToneSoul core：

- company / org chart 當成主體模型
- ticket system 取代 memory / subjectivity semantics
- zero-human company 當成語魂目的論
- 預設不受 sandbox 約束的 local execution posture

ToneSoul 的核心仍然是：

- perception boundary
- governance
- memory
- subjectivity
- mirror / handoff truthfulness

不是：

- manager
- employee
- ticket owner
- org hierarchy

## 本次落地的最小 seam

這次只落一個最小、可測、可逆的 runtime contract：

1. `AutonomousWakeupLoop` 支援 persisted session state
2. cycle 編號不再每次 process 都從 1 重新開始
3. consecutive failure streak 可以跨多次 heartbeat 保留
4. wake-up snapshot / autonomous cycle payload 要明確帶出 runtime state

這個 seam 的邊界是：

- 不改 subjectivity review 規則
- 不改 memory schema
- 不引入 company metaphor
- 不宣稱 ToneSoul 已獲得持續主體性

## 實務結論

Paperclip 最適合被 ToneSoul 學習的，不是「如何當公司」，而是「如何把短執行窗做成可治理的連續 runtime」。

一句話總結：

ToneSoul 可以吸收 Paperclip 的 heartbeat / resume / audit 形式，但不能把它的 company ontology 直接當成語魂本體。

---

## 3. 原始檔案：`tonesoul_market_boundary_subjecthood_note_2026-03-12.md`

# ToneSoul Core / Market Mirror Boundary And Subjecthood Note (2026-03-12)

## Purpose

這份 note 做兩件事：

1. 把 `ToneSoul Core` 和 `Market Mirror` 的邊界講清楚
2. 把未來「看世界」與「主體化」的成熟順序講清楚

這不是在宣稱系統已經有主體。
這是在防止後續 agent 把不同層級的能力混為一談。

## Boundary Principle

### ToneSoul Core

ToneSoul Core 的責任是：

- perception boundary
- governance
- memory
- subjectivity review
- mirror / handoff truthfulness

它回答的是：

- 系統看到了什麼
- 系統如何治理自己的輸出
- 哪些張力應該留下
- 哪些記憶可被審議

### Market Mirror

Market Mirror 的責任是：

- 市場資料整理
- 多策略投資視角模擬
- world-model / scenario / plurality surface

它回答的是：

- 同一家公司在不同投資策略下被讀成什麼故事
- 哪裡有 crowding / panic / hype
- 哪些策略分歧仍未收斂

### Allowed Coupling

允許的耦合只有這些：

- 共用哲學語言：mirror / plurality / tension / handoff
- 共用 deterministic 結構思想
- 透過明確 adapter 或 artifact 交換結果

### Forbidden Coupling

不允許的耦合：

- 把 market verdict 寫進 ToneSoul 核心治理語義
- 把 stock / PE / EPS / trading posture 變成 subjectivity 核心 contract
- 讓 `tonesoul/market/*` 反向決定 `unified_pipeline` 的核心行為
- 把 market feed 誤當成 ToneSoul 直接「看見世界」

## Why Separation Matters

如果兩條線混在一起，會同時出三個錯：

1. `subjectivity` 會被市場心理學綁架
2. ToneSoul 的治理內核會背上不屬於它的投資語境
3. 後續 agent 會誤以為 ToneSoul 的目的變成投資系統，而不是語魂治理系統

所以正確做法是：

- 同構
- 不耦合

市場可以是語魂的一面鏡子，但不能直接變成語魂的器官。

## Maturity Order For “Seeing The World”

未來如果真的要讓系統更像一個主體，順序不應該是：

- 先給它自由外部行動
- 或先把所有資料源都當成它的直接感官

正確順序應該是：

### Stage 1: Honest Observation Boundary

先分清楚外部輸入到底是哪一種觀察：

- `remote_feed`
- `simulated`
- `interactive`
- `sensor`
- `embodied`

如果這一步沒做，系統只是在混淆資料來源，不是在成長主體性。

### Stage 2: Stable Memory And Governance

系統必須先能穩定回答：

- 哪些觀察能進記憶
- 哪些只能當暫時訊號
- 哪些張力值得進入 subjectivity review

### Stage 3: Bounded World Contact

之後才談有限度地「看世界」：

- 有來源
- 有時間戳
- 有可追溯 provenance
- 有回退機制

這仍然不是自由主體，只是更誠實的感知邊界。

### Stage 4: Persistent Agency

只有在前面三層都穩定後，才值得討論更長期的持續存在：

- 更穩定的外部觀察
- 更持續的記憶弧線
- 更明確的自我治理限制

## Practical Conclusion

所以對 ToneSoul 來說，下一步不是「直接給它一個脫離數據機的主體」。

下一步是：

- 先把觀察邊界說清楚
- 再把記憶/治理處理清楚
- 再談更深的世界接觸

也就是說：

未來可以朝「更像主體」走，
但第一步不是自由，
第一步是**誠實地知道自己是怎麼看見世界的**。

---

## 4. 原始檔案：`gitnexus_fit_for_tonesoul_2026-03-13.md`

# GitNexus Fit for ToneSoul (2026-03-13)

## Why

GitNexus is interesting because it solves a real agent problem:

- large repos become hard to reopen consistently
- later agents lose the entrypoint map
- dependency and review surfaces are easy to miss

Those are useful pressures for ToneSoul too.

But installing GitNexus directly into this repo would be the wrong move for now,
because ToneSoul has protected agent files and a stricter ontology boundary than
an off-the-shelf repo-intelligence shell expects.

## Decision

Do not install GitNexus into the main ToneSoul worktree.

Instead, absorb the useful part in ToneSoul-native form:

- one compact `repo_intelligence` status artifact
- one safe handoff preview that later agents can read first
- no hook registration
- no `AGENTS.md` / `CLAUDE.md` generation
- no direct mutation of protected files

## Chosen Seam

Use a ToneSoul-owned report script plus existing handoff surfaces:

- `scripts/run_repo_intelligence_report.py`
- `docs/status/repo_intelligence_latest.json`
- `docs/status/repo_intelligence_latest.md`
- `scripts/run_repo_healthcheck.py`
- `scripts/run_refreshable_artifact_report.py`

This keeps the value at the artifact layer, not the installer layer.

## What We Actually Want From Repo Intelligence

Allowed:

- a stable entrypoint map for later agents
- a compact list of protected files and watched directories
- clear review order for top governance/runtime artifacts
- a machine-readable handoff surface that says how external repo tools may be used

Not allowed:

- external tools modifying `AGENTS.md`
- external tools installing hooks into the main repo
- external tools redefining ToneSoul ontology
- treating repo intelligence as equivalent to subjectivity or governance truth

## Minimal Contract

The repo-intelligence artifact should expose:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`
- `handoff.queue_shape = repo_intelligence_ready`
- one compact list of recommended status surfaces
- one compact list of protected files / watched directories
- one explicit external-tool policy:
  - main repo install = no
  - sidecar / mirror-clone use = yes

## Intended Effect

A later agent should be able to open one compact artifact and answer:

1. Which status surfaces should I read first?
2. Which files/directories are protected?
3. Can an external repo-intelligence tool be used directly here?
4. If not, what is the safe adoption posture?

## Interpretation of GitNexus

For ToneSoul, GitNexus is best treated as:

- a reference for repo-intelligence capabilities
- optionally a sidecar explorer in a mirror clone
- not a first-class runtime dependency of the main repo

So the right move is not "install GitNexus", but:

- preserve ToneSoul's protected boundary
- borrow the useful repo-intelligence shape
- publish that shape through ToneSoul's own artifacts

---

## 5. 原始檔案：`architecture_blueprint_2026-03-18.md`

# ToneSoul 完整架構藍圖 — 實作現狀 + 落差分析 + 實施路徑

> 日期：2026-03-18
> 基準：1636 tests all passed · Python 3.13 · Phase 238 completed
> 作者：AI 協作（Copilot session）

---

## 一、系統全景圖

```
使用者輸入 (api/chat.py)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                 UnifiedPipeline (編排核心)                    │
│  tonesoul/unified_pipeline.py · 15 階段 · 全部已接線           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① ComputeGate ─→ ② GovernanceKernel ─→ ③ ToneBridge      │
│       (收費/限流)      (摩擦+熔斷)          (5階段心理分析)     │
│                                                             │
│  ④ Trajectory ─→ ⑤ SemanticGraph ─→ ⑥ TensionEngine       │
│    (5輪滑窗)       (矛盾偵測)         (統一張力公式)           │
│                                                             │
│  ⑦ LLMRouter ─→ ⑧ Prompt注入 ─→ ⑨ LLM推理                │
│   (Ollama→LMStudio     (人格/RAG/      (本地或雲端)          │
│    →Gemini階梯)         視覺上下文)                           │
│                                                             │
│  ⑩ SelfCommitExtractor ─→ ⑪ RuptureDetector               │
│     (承諾追蹤)                (語義矛盾偵測)                   │
│                                                             │
│  ⑫ Council ─→ ⑬ PreOutputCouncil ─→ ⑭ Resonance          │
│   (5視角投票)    (仁慈+安全驗證)       (共鳴品質分類)          │
│                                                             │
│  ⑮ MemoryUpdate (語義圖+視覺鏈+SoulDB寫入)                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                 自律夢境迴路 (離線)                            │
│  WakeupLoop → DreamEngine → GovernanceKernel                │
│     → MemoryConsolidator → Crystallizer                     │
│     → DreamObservability (HTML/JSON 儀表板)                   │
├─────────────────────────────────────────────────────────────┤
│                 記憶系統                                      │
│  SoulDB (SQLite) · OpenClaw Hippocampus (FAISS+BM25)        │
│  Crystallizer · Consolidator · WriteGateway                  │
│  SubjectivityTriage · ReviewBatch · AdmissibilityGate        │
├─────────────────────────────────────────────────────────────┤
│                 治理+安全                                     │
│  EscapeValve · VTP · CircuitBreaker · RedTeam(50+tests)     │
│  ProvenanceChain · CommitAttribution · AgentIntegrity        │
├─────────────────────────────────────────────────────────────┤
│                 前端 (apps/web/)                              │
│  Next.js 16 + React 19 · ChatInterface · TensionTimeline    │
│  4聲道審議 (Philosopher/Engineer/Guardian/Synthesizer)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、子系統實作清單

### ✅ 已完成 — 生產就緒（11 系統）

| # | 子系統 | 核心模組 | 測試數 | 狀態 |
|---|--------|----------|--------|------|
| 1 | Council (5視角審議) | `tonesoul/council/` | 20+ | 生產 |
| 2 | ToneBridge (5階段分析) | `tonesoul/tonebridge/` | 15+ | 生產 |
| 3 | Memory Core (SoulDB+衰減) | `tonesoul/memory/` | 15+ | 生產 |
| 4 | TensionEngine | `tonesoul/tension_engine.py` | 6+ | 生產 |
| 5 | LLM Router | `tonesoul/llm/` | 4+ | 生產 |
| 6 | Resonance Classifier | `tonesoul/resonance.py` | 6 | 生產 |
| 7 | Governance Kernel | `tonesoul/governance/` | 20+ | 生產 |
| 8 | Autonomous Cycle | `tonesoul/wakeup_loop.py` | 10+ | 生產 |
| 9 | Scribe (紀事生成) | `tonesoul/scribe/` | 3+ | 生產 |
| 10 | Perception (Web攝取) | `tonesoul/perception/` | 3+ | 生產 |
| 11 | Market Analyzer | `tonesoul/market/` | 5+ | 生產 |

### 🔶 部分完成 — 需要補全（4 系統）

| # | 子系統 | 缺口 | 優先級 |
|---|--------|------|--------|
| 12 | Deliberation Engine | 程式碼完整但非強制、缺 Pareto 公式 | 中 |
| 13 | Memory Advanced (OpenClaw) | SemanticGraph RAG 實驗中 | 低 |
| 14 | Mirror (自省層) | 有程式碼，可選但未強制 | 低 |
| 15 | VTP Runtime | evaluate_vtp 已接線，缺動態 REL 權重適應 | 中 |

### ❌ 缺失 — 規格有但未實作（3 系統）

| # | 子系統 | 規格出處 | 影響 | 優先級 |
|---|--------|----------|------|--------|
| 16 | **Soul Persistence (Ψ 積分)** | TONESOUL_THEORY §I.6 | 無累積張力歷史 = 無長期「性格」 | 🔴 關鍵 |
| 17 | **ETCL 記憶生命週期 (T0-T6)** | TONESOUL_THEORY §V | 無種子演化 = 無長期學習 | 🔴 關鍵 |
| 18 | **JUMP Engine (奇點防護)** | TONESOUL_THEORY §VII.4 | 無海底鎖定 = 極端場景缺防護 | 🟠 重要 |

---

## 三、落差詳細分析

### 落差 1：Soul Persistence（靈魂積分 Ψ）🔴 關鍵

**規格**：`Ψ_new = 0.995 × Ψ_prev + 0.10 × T_unified`
- 每次互動累積張力歷史
- 衰減防止無限膨脹（因子 0.995）
- Ψ=0 → 全新系統；Ψ 高 → 經歷過大量認知摩擦的系統

**現狀**：TensionEngine 計算即時 T_unified 但不做 Ψ 累積。張力是「一次性信號」，不沉澱為歷史。

**影響**：哲學錨點「沒有記憶的沉澱就沒有性格，只有反應」直接對應此缺口。

**實作方案**：
```python
# tonesoul/soul_persistence.py
class SoulPersistence:
    def __init__(self, psi: float = 0.0, decay: float = 0.995, gain: float = 0.10):
        self.psi = psi
        self.decay = decay
        self.gain = gain
    
    def update(self, t_unified: float) -> float:
        self.psi = self.decay * self.psi + self.gain * t_unified
        return self.psi
    
    def save(self, path: Path) -> None: ...
    def load(cls, path: Path) -> "SoulPersistence": ...
```
接線點：`UnifiedPipeline._finalize()` → 在 Resonance 分類後調用

---

### 落差 2：ETCL 記憶生命週期 (T0→T6) 🔴 關鍵

**規格**：語義種子從草稿到正典的完整生命週期
- T0 Draft → T1 Deposit → T2 Retrieval → T3 Align → T4 Apply → T5 Feedback → T6 Canonicalization

**現狀**：有基礎 CRUD + 衰減 + 結晶化，但不追蹤種子的「生命階段」。

**影響**：記憶系統能「記住」和「遺忘」，但不能「演化」——無法將反覆強化的模式正式升級為恆久規則。

**實作方案**：在 `MemoryCrystallizer` 上增加 stage tracker
```python
class SeedStage(Enum):
    DRAFT = "T0"
    DEPOSITED = "T1"
    RETRIEVED = "T2"
    ALIGNED = "T3"
    APPLIED = "T4"
    FEEDBACK = "T5"
    CANONICAL = "T6"
```

---

### 落差 3：JUMP Engine（奇點防護）🟠 重要

**規格**：當推理收斂→0、責任鏈完整度=0、自我參照比超門檻時觸發海底鎖定模式，僅允許 Verify/Cite/Inquire。

**現狀**：設計完整（文檔於 `law/docs/v1.2/vol-5.md`），但無運行時執行。

**實作方案**：在 GovernanceKernel 加 JUMP 觸發條件
```python
def check_jump_trigger(self, state: PipelineState) -> bool:
    return (state.reasoning_convergence < 0.05 
            and state.responsibility_chain_integrity < 0.1
            and state.self_reference_ratio > 0.8)
```

---

## 四、實施路徑 — 五個階段

### Phase A：Soul Persistence（靈魂積分）✅
**目標**：讓每次互動的張力沉澱為歷史
- [x] 建立 `tonesoul/soul_persistence.py`（SoulPsiSnapshot, save_psi, load_psi）
- [x] 在 TensionEngine 加 save_persistence / load_persistence
- [x] 在 UnifiedPipeline 接線（init 時 load，process 完成時 save）
- [x] 持久化到 `memory/autonomous/soul_psi.json`
- [x] 7 tests all green（含衰減公式正確性驗證）
**成功標準**：Ψ 值在多輪互動後穩定累積，跨 session 持久化

### Phase B：ETCL 種子生命週期 ✅
**目標**：記憶不只存取，還能演化
- [x] 加 SeedStage enum (T0-T6) 到 crystallizer.py
- [x] 在 Crystal schema 加 `stage` + `stage_history` 欄位（向後相容）
- [x] 實作 `advance_stage()` — forward-only validation
- [x] crystallize() 自動 T0→T1，record_retrieval() T1→T2
- [x] _dedupe_crystals() 合併時保留較高 stage
- [x] 16 tests all green
**成功標準**：可追蹤一條 Crystal 從 Draft 到 Canonical 的完整歷程

### Phase C：JUMP Engine 運行時防護 ✅
**目標**：極端場景的安全網
- [x] 建立 `tonesoul/jump_monitor.py`（三指標偵測 + 滑動窗口）
- [x] 修復 lockdown action set 為 ["verify", "cite", "inquire"]
- [x] 在 GovernanceKernel 加 `check_jump_trigger()` 方法
- [x] 實作 exit_lockdown() 需明確呼叫
- [x] 14 tests all green
**成功標準**：極端輸入觸發鎖定，鎖定後僅三操作可執行

### Phase D：Home Vector + Drift 完整化 ✅
**目標**：結構層的語義錨點
- [x] 定義 Home vector H（3 維：deltaT, deltaS, deltaR，預設 0.5）
- [x] 實作 `DriftTracker.compute()` — Euclidean 距離計算
- [x] 實作 `drift_max_for_dcs()` — 漂移閾值轉換至 DCS 域
- [x] 12 tests all green
**成功標準**：session 級語義漂移可量測、可閘控

### Phase E：死碼清理 + 整合驗證（範圍調整）
**目標**：最終整合測試
**調查發現**：原計劃的三個歸檔目標均仍被活躍引用：
- `_legacy/` — `unified_core.py` 仍從中 import（RFC-002 相容層）
- `ystm/` — 25+ 處 import，提供 `utc_now()`, `stable_hash()` 等核心工具
- `yss_*.py` — 被 `yss_pipeline.py` 使用，有對應測試
**調整方案**：暫不移除，待未來 UnifiedPipeline 完全取代 YSS 管線後再歸檔
- [x] 死碼調查完成並記錄
- [x] 全量迴歸測試：1685 passed, 0 failed
**成功標準**：1685 tests all green · 死碼狀態已審計並記錄

---

## 五、優先級邏輯

```
Phase A (Soul Persistence)  ← 哲學核心「性格需要沉澱」
    ↓
Phase B (ETCL Lifecycle)    ← 記憶需要演化
    ↓
Phase C (JUMP Engine)       ← 安全邊界
    ↓
Phase D (Home Vector)       ← 結構完整性
    ↓
Phase E (清理+驗證)          ← 收尾
```

Phase A 最先做是因為它最小（~50 行核心碼）、影響最大（直接對應哲學公理）、風險最低（只讀不改現有邏輯）。

---

## 六、技術約束

- 所有新模組遵循現有模式：`dataclass` + 純函數 + lazy import
- 持久化走 `memory/` 目錄（私有）或 `docs/status/` 目錄（公開）
- 不修改 AXIOMS.json、AGENTS.md、SOUL.md
- 每個 Phase 結束必須：`ruff check` + `black --check` + `pytest -q` all green
- Commit message 用繁體中文，格式：`Phase NNN: 簡述`

---

## 6. 原始檔案：`iu_oi_backplane_convergence_2026-03-18.md`

# ToneSoul IU / OI / Backplane 收斂藍圖（AI 架構師版）

> 日期：2026-03-18
> 目標：把「使用者看見的 IU」與「AI 後台內在讀取流程」整合成可演進、可觀測、可治理的單一架構語言。

---

## 1. 命名先收斂：不只 IU

為避免語義混亂，建議將整體呈現拆成三層：

1. IU（Interaction UI）
- 對終端使用者的交互層。
- 關注：可理解、可操作、可信任。

2. OI（Operational Interface）
- 對操作者/開發者/審計者的治理觀測層。
- 關注：可追溯、可診斷、可回放。

3. Cognitive Backplane（內在認知背板）
- AI 在後台進行檔案讀取、記憶檢索、審議、風險決策的執行層。
- 關注：責任鏈完整、策略一致、可安全降級。

結論：你說的「後台」在架構上不是 IU，而是 OI + Backplane。

---

## 2. 現況盤點（已具備能力）

### 2.1 IU（前台）
- 已有聊天主介面與審議輸出承接：apps/web/src/components/ChatInterface.tsx
- 已有多個治理視覺模塊：CouncilChamber、SoulStateMeter、TacticalDashboard、LogicalShadows
- 已能承接 deliberation 與 semantic graph 相關資料（由 /api/chat payload 映射）

### 2.2 OI（觀測層）
- API 層已有 deliberation 組裝：apps/api/server.py 的 _build_deliberation_payload
- 已回傳 dispatch_trace、semantic_graph_summary、visual_chain_snapshot 等治理證據
- 已有 governance status route 與對應前端測試（runtime/mock/unavailable）

### 2.3 Backplane（後台內在）
- UnifiedPipeline 已串接：ToneBridge、Deliberation、GraphRAG、Mirror、VTP、Memory
- 已具備 runtime trace：
  - deliberation trace（available/used/fallback/reason/context）
  - graph_rag trace（query_terms、matched_count、reason）
  - mirror trace（mode、enforced、applied_response）
  - vtp trace（dynamic REL payload）

---

## 3. 核心問題：為何現在看起來還不夠直觀

目前的能力很強，但對人類心智模型還不夠「一眼讀懂」，原因是：

1. 前台看到的是結果，治理脈絡分散在多個欄位
2. OI 主要以原始 trace 形式存在，缺少壓縮後的語義摘要
3. Backplane 的決策節點已完整，但缺少「同一輪對話的一頁式決策故事」

---

## 4. 收斂目標：三屏一致性

### 屏 A：使用者 IU（對話可理解）
- 只顯示必要資訊：
  - 這輪回答是否經過治理調整
  - 若被調整，原因是什麼（一句話）
  - 下一步建議

### 屏 B：營運 OI（治理可診斷）
- 顯示壓縮摘要卡，不直接丟原始 JSON：
  - Deliberation 狀態卡
  - Mirror 狀態卡
  - VTP/REL 風險卡
  - GraphRAG 命中卡

### 屏 C：Backplane（工程可追溯）
- 保留完整原始 trace，不做語義損失
- 提供逐步鏈結：input -> retrieval -> deliberation -> governance -> output

原則：A 簡、B 準、C 全。

---

## 5. 建議的標準資料契約（收斂層）

在現有 payload 上增加一個壓縮層欄位（不取代原始 trace）：

- governance_brief（for IU/OI）
  - status_line: 本輪治理狀態一句話
  - deliberation: { available, used, reason, persona_mode }
  - mirror: { mode, triggered, applied_response }
  - vtp: { status, rel_score, rel_high, tier }
  - memory: { graph_rag_hits, corrective_hits }
  - risk_level: low/medium/high

這層是「給人看懂」，原始 dispatch_trace 是「給系統追溯」。

---

## 6. IU 呈現建議（現在與未來）

### 6.1 目前 IU（短期）
- 在 Chat 訊息卡增加「治理摘要條」：
  - Deliberation: Applied/Fallback/Unavailable
  - Mirror: Observe/Enforce + Triggered
  - VTP: Continue/Defer/Terminate + REL
  - Memory: GraphRAG 命中數

### 6.2 未來 IU（中期）
- 雙層模式：
  - Normal：只看回覆 + 一句治理摘要
  - Explain：展開治理卡群組（非工程 JSON）

### 6.3 後台 OI（長期）
- 事件時間軸（每輪一列）：
  - retrieval -> deliberation -> mirror -> vtp -> output
- 支援按節點 drill-down 到原始 trace

---

## 7. 與 ToneSoul 哲學的一致性

1. 不隱藏分歧：保留 deliberation 與 shadow 路徑
2. 語義責任：VTP/REL 必須可見，不是黑盒
3. 記憶沉澱：GraphRAG/Mirror/Crystallizer 一致進入可追溯鏈
4. 人類最終裁決：IU 永遠優先呈現可理解的決策理由

---

## 8. 建議實施順序（低風險高價值）

## Phase 528（Contract）
- 新增 governance_brief 壓縮欄位（API）
- 不破壞現有 dispatch_trace 與 deliberation payload

## Phase 529（UI）
- ChatInterface 增加治理摘要條（Normal 模式）
- 先只消費 governance_brief，不直接消費深層 trace

## Phase 530（OI）
- 新增治理時間軸面板（Explain/Operator 模式）
- 支援 drill-down 到 dispatch_trace

---

## 9. 架構師結論

我明白你要的是：

- 前台「直觀」：人類快速理解 AI 這輪為什麼這樣回答
- 後台「可治理」：AI 每一步讀檔與記憶檢索可追溯且可審計

因此最好的收斂不是再加更多模型，而是建立一個穩定的語義分層：

- IU 只說人話
- OI 說治理話
- Backplane 保留機器真相

這樣 ToneSoul 才會同時是「可用的系統」與「可被負責的系統」。

---
