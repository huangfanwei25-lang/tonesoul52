# 語魂九層自述地圖 — 約束導向 AI 協作開發（ToneSoul 視角）

- 日期：2026-06-29
- 性質：**不是新架構**。這是把語魂**已經有的**問責機制，用「約束導向 AI 開發
  （Constraint-Oriented AI Development）」的共用詞彙，命名成一張可指認的地圖。
- 評估來源：2026-06-29，11-agent workflow 對 master 逐層落地驗 + 人/AI 綜合（綜合由
  Claude Opus 做；synthesis agent 因 schema 過重失敗，故綜合非機器產出）。
- 核心判斷：**語魂已具備全部九層（問責形式）→ 吸收詞彙、拒絕外部實作。**

> 誠實邊界（把 claim ≤ evidence 套在這份文件自己身上）：下表的**檔案路徑已於 2026-06-29
> 親驗存在**；但每層「已成熟」的判斷是子代理對程式碼的讀，未逐一深驗。本文件**不宣稱**語魂
> 「完備」或「記憶不可繞過」（`AXIOMS.meta.not_for`）；它只宣稱：這九層的**問責版本已存在且
> 可指認**。

---

## 九層地圖

| 層（中文名） | 語魂既有的對應 | 主要檔案 | 性質 |
|---|---|---|---|
| 0 意圖收納層 | 治理決策記錄模板 + Vow / Scope Guard | `CLAUDE.md`（治理綁定段）、`task.md` | extend |
| 1 語義落點層 | **CognitiveFrame**（問題→actors/facts/unknowns/evidence_refs） | `tonesoul/cognition/cognitive_frame.py`（#218） | extend |
| 2 主張對測層 | responsibility-runtime 意圖閘 + **E0–E4 證據階梯** | `tonesoul/responsibility_runtime/intent_validator.py`、`tonesoul/reviewer/evidence_levels.py` | extend |
| 3 責任邊界層 | 層邊界 CI 閘 + `__ts_layer__` 自宣告 + ROOT_MODULE_LAYER | `scripts/verify_layer_boundaries.py`、`scripts/analyze_codebase_graph.py` | extend **·不吞 DDD/CQRS** |
| 4 視角分工層 | 議會六視角 + Critic（黑鏡）+ 總審層 | `tonesoul/council/perspective_factory.py`、`tonesoul/council/pre_output_council.py` | extend |
| 5 模式記憶層 | thesis-defender 技能 + 刪除危害地圖 + 失敗回寫備忘 | `.claude/skills/tonesoul-thesis-defender/`、`docs/SUCCESSOR_MAP.md` | extend |
| 6 不變式閘層 | validate→policy→enforce + AXIOMS FOL + 影子閘 | `tonesoul/responsibility_runtime/`、`tonesoul/dream_responsibility_shadow.py`（#219） | extend |
| 7 品質閘門層 | 18 條 CI 工作流 + 25 支 `verify_*.py` + 知識閘 | `.github/workflows/`、`scripts/verify_*.py`、`tonesoul/council/epistemic_labeler.py`、`tonesoul/council/semantic_overclaim_sensor.py` | extend |
| 8 模式演化層 | 基質堆疊理論（層歸因）+ 錯誤帳本 + 策略結晶 + 失敗回寫迴圈 | `docs/philosophy/substrate_stack_theory_*.md`、`docs/memory/STRATEGIC_CRYSTAL_FORMAT.md` | extend |
| 9 治理覆蓋 | 知識標籤器 + 漂移監測 + 守衛過度宣稱（黑鏡） | `tonesoul/council/epistemic_labeler.py`、`tonesoul/drift_monitor.py`（接於 `unified_pipeline.py:305`）、`tonesoul/council/semantic_overclaim_sensor.py` | **不吞 Overlay facade** |

---

## 不要吞（明列為 anti-pattern，免得未來 session cargo-cult）

1. **DDD / CQRS / Clean Architecture 腳手架**（第 3 層）：不要 Aggregate / ValueObject /
   CommandBus / ReadModel / BoundedContext 類別。子代理判為 **HIGH 過度工程**；依賴方向語魂已用
   `__ts_layer__` + CI 做完。這是創作者自己嗅到的「神廟」。
2. **「Governance Overlay」模組 / facade / 聚合狀態**（第 9 層）：一個聚合六閘的 god-object 會
   **摧毀各閘的獨立問責**。知識標籤器 / 漂移監測 / 守衛 必須**各自獨立、各自可歸責**。這是九層裡
   唯一 `do-not-swallow` 的原因。
3. **為湊外部 8 節點而增生 sub-agent**（第 4 層）：cargo-cult + `persona_audit` 防的
   fake-diversity collapse。六視角是刻意的。
4. **通用 intake / BDD 框架 / per-function DBC 裝飾層**：AI-pad 樣板垃圾；語魂有的是
   問責特化版本。

---

## Meta 原則（keeper，axiom-shaped，日後可由創作者升格為公理）

> **AI 可以提出約束，但約束本身必須可審查、可歸責、可反駁。**

這是整個外部提案裡最強的一條。它是 **auditor ≠ auditee 命題 + claim ≤ evidence 上升到 meta 層**：
gate rule 自己也受 gate 紀律管。

**可執行化（讓它是規則不是口號）**：每一條被提出的約束，落地時必須帶——
- **(a) provenance**：它來自哪個**真實失敗**（可審查）；
- **(b) 一個會 fail 的測試**：能被反駁（可反駁）；
- **(c) 一個能否決它的 owner**（可歸責）。

這正是「失敗回寫備忘」已經在做的事（例：本專案 2026-06-29 自抓「測試全綠」過度宣稱 → 回寫成一條
帶來源、帶測試、可被否決的規則）。

---

## 演化護欄

外部提的軌跡「AI 產出審查者 → AI 約束場設計者 → AI 責任鏈維護者」**成立——但唯有上面的 Meta 原則
當護欄**。AI 設計約束是「restraint-directed capability」（設計要**防**什麼），符合 thesis；前提是它
設計出的每條約束都保持可審 / 可反駁 / owner-vetoed。否則就是 AI 自寫規則、自己打分＝治理層的
self-authored-test 陷阱。

---

## 這份地圖之後（工程細節補足的方向）

沒有任何一層回報「缺失」。所以接下來的工程不是**蓋新層**，是對既有層做小幅 **extend**，每一刀都用
Meta 原則的三件套（provenance / 會 fail 的測試 / owner-veto）約束自己。候選見對應層的 `extend` 標記。
