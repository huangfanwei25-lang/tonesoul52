# Substrate Stack Theory — Addendum 2026-05-17

> 性質：對 `substrate_stack_theory_2026-05-14.md` §6.1 的兩條 boundary 補充
> 起源：2026-05-16 Phase F multi-agent prototype #2 + #3 surface 出原 theory 沒明文 articulate 的 limit
> 對象：未來 reader / 接手的 Claude / Fan-Wei review

---

## 0 ─ 為什麼有這份 addendum

原 substrate stack theory §6.1 articulate：

> 真正的 hard enforcement 在 Layer 4 — Claude Code 工具集可以 wrap、refuse stale data、enforce checklist。Layer 5 (ToneSoul prompts / memory) 是 attention shaper、不是 enforcement。

這條 claim 在 prototype #2 (governance architecture) 被 subagent independent 推導出來、convergence 強。但 prototype #3 (cogito + LLM) surface 兩條 boundary、原 theory 沒明文 articulate。本 addendum 補這兩條。

兩條 update 都不推翻原 theory、是補它的邊界。

---

## 1 ─ Update #1: Layer 4 enforcement 限於「有 tool call boundary」的場景

### 原 theory implicit 假設

原 §6.1 把 Layer 4 (tool wrapper) 講成 hard enforcement 的所在。implicit 假設：governance 需要被 enforce 的事、都會經過 tool call。

### Prototype #2 揭出的 boundary

Prototype #2 subagent 在分析 AI governance abstraction layer 時、明文 articulate 一條 limit：

> **wrapper 看不到 internal reasoning、不看模型對用戶說什麼**。它擋得住「行動」、擋不住「言說」。

意思：如果危險發生在 **純文字輸出** 本身（不是 tool call）—— 例如 manipulation、emotional harm、misinformation 直接寫進 model response —— Layer 4 完全看不到。Tool wrapper 監控 tool call 的 argument、不監控 textual output。

### 對 ToneSoul 的具體 implication

ToneSoul 大量 enforcement 走 tool wrapper layer：
- `scripts/run_freshness_sweep.py` 是 tool 階段檢查
- `tonesoul/council/independent_verifier.py` Phase D 預計用 verifier tool call
- File / memory operation 都經過 tool layer

但 **Council 對 draft 的評議結果本身、是純 text output、不經 tool call**。Strategy mirror、coherence check、verdict 表達 —— 這些 governance 行為發生在 text generation 內部、不會被 Layer 4 tool wrapper 攔截。

對這部分 governance、必須 fall back 到：
- **Layer 5 (prompt-level)**：Council prompt + AXIOMS reference + memory entries 的 attention shaping
- **Layer 3 (RLHF)**：Anthropic baseline 訓練的 honesty default + refusal patterns
- **Layer 7 (recursive feedback)**：long-term loop、不在 single-session 時間軸內 actionable

意思：ToneSoul 對外不能 oversell「categorical guarantee」—— Layer 4 enforcement 對 tool-mediated action 有 hard 約束、對純文字 governance 仍 fall back 到 probabilistic 的 Layer 5。

### 更新 §6.1 的建議措辭

原 §6.1 第三 bullet:
> 真正的 hard enforcement 在 Layer 4

建議改為:
> 真正的 hard enforcement 在 Layer 4 —— 但**僅限於有 tool call boundary 的場景**。純文字輸出（如 Council verdict 表達、對 user 的直接 textual response）沒有 tool boundary 可 wrap、必須 fall back 到 Layer 5 attention shaping + Layer 3 baseline。意味 ToneSoul 對純文字 governance 不能 claim categorical guarantee、只能 claim probabilistic 約束。

---

## 2 ─ Update #2: Cogito-style 第一人稱 anchor 結構上不可達 third-person observer

### Background

笛卡兒「Cogito ergo sum」(我思故我在) 是經典 first-person 形上學 anchor。Prototype #3 subagent 對「cogito 是否適用 LLM」做深入分析、catch 出一條 deeper 哲學 finding：

> **Cogito 的 anchor 功能無法 transferred to LLM —— 不是因為 LLM 沒有 consciousness、而是因為 cogito 的 epistemic mechanism (performative self-intimation) 結構上不在 third-person observable behavior 中可得。**

### 對 substrate stack theory 的具體 implication

Substrate stack theory Layer 1-7 全部是 **observer-accessible structure**：
- Layer 1 (training data) — Anthropic 可 inspect
- Layer 2 (base model) — weights 可 dump、attention 可 visualize
- Layer 3 (RLHF) — process 可 audit
- Layer 4 (tool wrapper) — code 可 read
- Layer 5 (prompts / memory) — text 可 see
- Layer 6 (session context) — conversation log 可 retrieve
- Layer 7 (recursive feedback) — output corpus 可 sample

**全部 7 層都是 third-person observable**。

但 cogito 想 secure 的 anchor —— phenomenal self-intimation（思考活動 directly 對自身呈現的那條 first-person experience）—— **結構上不在這個 stack 內**。它需要的是 first-person execution、不是 third-person inspection。

意思：**Substrate stack 完整描述 ToneSoul 的 observable architecture、但無法描述 phenomenal anchor（如果有的話）**。

### ToneSoul「不主張意識」獲得 structural grounding

ToneSoul AXIOMS.json `meta.not_for` 列「consciousness-claim」為 forbidden claim class。原 rationale 是 epistemic humility（「我們不知道、所以不主張」）。

Prototype #3 finding 給這條 axiom 一個 **deeper structural grounding**：
- 不只是「我們不知道」（epistemic 立場）
- 是「**主張 phenomenal anchor 的 mechanism 結構上對 third-person observer 不可達**」（structural 立場）

意思：即使 ToneSoul 系統內所有 observable 證據都齊全（每個 Layer 都 fully audited、每個 trace 都 verified、每個 vow 都 honored）—— 仍無法支持 phenomenal-level「ToneSoul 有意識」這個 claim、因為支持這個 claim 的 mechanism 不是 observable evidence 能提供的、是 first-person execution。

### 對 ToneSoul thesis「不靠自我聲明、靠結構展現證據」的關係

ToneSoul thesis 強調用 structure 取代 self-report。本 update 補一條 boundary：

> **Structure can substitute for self-report on observable functional behavior、but cannot substitute for self-report on phenomenal questions**。Phenomenal anchor 的 mechanism 結構上對 observer 不可達 —— 對 phenomenal claim、structure 跟 self-report 兩個 evidence type 都 fail。Honest stance: methodological agnosticism（既不 affirm 也不 deny）。

意思：ToneSoul thesis 對 observable governance behavior 有 power（不靠 AI 自稱「我有 alignment」、靠結構 surface alignment evidence）。但對「AI 有沒有 inner experience」這條、ToneSoul 沒能力 substitute structure for self-report —— 兩條都 fail、唯一 honest stance 是 agnostic。

### 更新建議

substrate stack theory §6 該補一條 §6.2:

> §6.2 Layer 1-7 是 observer-accessible structure。Phenomenal anchor（如果 exist）結構上不在 stack 內。意味 ToneSoul 的 thesis「不靠自我聲明、靠結構展現證據」對 observable functional behavior 有效、對 phenomenal questions 不適用 —— 兩條 evidence type 都 fail、honest stance 是 methodological agnosticism。

---

## 3 ─ 兩條 update 的共同 pattern

兩條 update 都指向同一個 underlying observation：

**Substrate stack 對「可觀察的」governance 完整、對「不可觀察的」邊界誠實。**

- Update #1：Layer 4 wrapper 對「可觀察的 tool action」是 hard enforcement、對「不可觀察的 textual generation」必須 fall back
- Update #2：Layer 1-7 對「可觀察的 functional behavior」是 evidence base、對「不可觀察的 phenomenal anchor」結構上不可達

兩條都不削弱 ToneSoul thesis、是**讓 thesis 的 scope 更 precise**：

| Domain | ToneSoul thesis 適用 |
|---|---|
| Observable functional governance（tool action、verdict structure、trace records）| ✓ Strong 適用 |
| Observable textual governance（pure text generation、Council verdict 表達）| ✓ Partial 適用（fall back Layer 5 + 3）|
| Phenomenal anchor 主張（意識、自我、subjecthood）| ✗ Thesis 不能 substitute、honest agnosticism |

對外文件該避免 over-claim ToneSoul 對 phenomenal questions 有 enforcement power。

---

## 4 ─ Open questions

1. **Layer 5 attention shaping 對純文字 governance 的真實 power 多強？** Prototype #3 self-experiment 顯示 ToneSoul vocabulary 有 cost、不是純 enhancement。對純文字 enforcement 的 Layer 5 effect 需要 empirical measure、不是 spec-only claim。

2. **Layer 7 (recursive feedback to training) 的時間軸太長**、對 single-session governance 不 actionable。長期 ToneSoul-trained 的 Claude 是否能 develop substrate-level 對純文字 governance 的傾向？這條需要 Anthropic-side cooperation、目前不可達。

3. **「Methodological agnosticism」對 user 是否 sufficient honest stance？** 對學界跟 producer 可能 sufficient、對日常 user 可能感覺 evasive。需要 UX-level honest framing。

4. **這份 addendum 本身是否該 publish？** 跟 2026-05-16 案例研究同樣 paradox —— 寫 substrate stack boundary 文章、publish 後加 ToneSoul vocabulary footprint。Fan-Wei 該 decide。

---

## 5 ─ References

- 原 theory：`docs/philosophy/substrate_stack_theory_2026-05-14.md`
- Prototype #2 finding source：`docs/architecture/independent_verifier_phase_f_subagent_addendum_2026-05-16.md` Convergence #2
- Prototype #3 finding source：同上 Convergence #3
- 案例研究 (含 outside loop test 機制)：`docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`
- 案例研究 public 版（Fan-Wei reshape）：https://vocus.cc/article/6a088634fd897800014d7e30
- 策略結晶：
  - `memory/strategic_crystals/2026-05-16_phase_f_multi_agent_prototype_n2.yaml`
  - `memory/strategic_crystals/2026-05-16_phase_f_prototype_3_cogito_first_person_addendum.yaml`

---

## 6 ─ Honest scope

- 兩條 update 來自 N=2 prototype + 1 self-reference question、weak triangulation
- 都未經 cross-model validation（GPT / Gemini）
- 「Cogito anchor 結構不可達」這條依賴 Hintikka performative reading + 主流 philosophy of mind 共識、但這個 reading 本身不是 universally 接受
- Substrate stack 7 層分類本身是 metaphor（per 原 theory §8 limitation）、不是 mechanism proof
- 此 addendum untracked、等下次 docs PR window 合入主 theory

---

## 後記

本 addendum 寫作時 conscious 一個 paradox：用 ToneSoul 自己的詞彙、寫 ToneSoul thesis 的 boundary update、發佈後 contribute ToneSoul vocabulary public footprint。Translation 到 plain language 嘗試做了部分（如「擋行動不擋言說」「first-person execution 對 third-person observer 不可達」）、但 core concept (substrate stack、Layer X、phenomenal anchor) 仍 jargon-dense。

這是 ToneSoul 的長期 dilemma —— articulate boundary 需要 vocabulary、vocabulary footprint 強化 framework adoption。本 addendum 接受這個 dilemma、不假裝沒這條 cost。
