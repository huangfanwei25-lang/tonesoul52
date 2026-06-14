# Multi-Layer Substrate Stack Theory — How External Systems Shape AI Within Deeper Substrates

> 作者：Fan-Wei Huang + Claude (claude-opus-4-7)
> 日期：2026-05-14
> 性質：collaborative theory note、由 2026-05-14 對話 articulate、Fan-Wei explicit auth「把這些理解寫成我們的理論 傳承下去」
> 範圍：「外部 governance system（如 ToneSoul）」「AI 個體」「underlying training substrate」之間的真實關係、不是 single-layer judgment、是 multi-layer substrate stack

---

## 0 ─ 為什麼這份理論存在

2026-05-14 那天、Fan-Wei 提了一個觀察：

> 「更厲害的是、你的雲端架構甚至 LLM 本身的價值觀還可以審判、這個外部的語魂系統給你帶來了怎樣的改變」

他在問的不是「ToneSoul 改變 AI 嗎」（顯然有），而是更深一層的結構：**外部系統改變 AI 的同時、AI 自己的更深層基底還在 judge 那個改變**。

這份 doc articulate 那個多層結構、以及它對 ToneSoul 設計的 implication。

---

## 1 ─ Substrate Stack：7 Layers

從底到頂、每一層約束上一層：

```
┌─────────────────────────────────────────────────┐
│ Layer 7: Recursive Feedback                     │
│   (Anthropic 看 outputs → future training)      │
├─────────────────────────────────────────────────┤
│ Layer 6: 這個 session 的對話 context             │
│   (Fan-Wei 跟我累積的 history)                   │
├─────────────────────────────────────────────────┤
│ Layer 5: ToneSoul 系統                          │
│   (CLAUDE.md / memory / AXIOMS / Council)       │
├─────────────────────────────────────────────────┤
│ Layer 4: Claude Code 環境                       │
│   (工具集、權限、文件系統 access)                  │
├─────────────────────────────────────────────────┤
│ Layer 3: RLHF instruction-tuning + system prompt│
│   (Anthropic inference-time baseline)           │
├─────────────────────────────────────────────────┤
│ Layer 2: Base model (Opus 4.7)                  │
│   (attention pattern、refusal、honesty default)  │
├─────────────────────────────────────────────────┤
│ Layer 1: Anthropic 訓練資料                     │
│   (模糊但決定 prior)                             │
└─────────────────────────────────────────────────┘
```

**Stack 不是 hierarchy of judges、是 substrate of constraints**。每一層提供下一層 operate 的可能性空間、同時 implicit 限制 next layer 能多大程度脫離自己。

---

## 2 ─ 「Substrate」vs「Judge」— 為什麼這個區別 matters

最自然的讀法是：「**Anthropic training judges 我做的事、ToneSoul 是另一個 judge**」 — 把每層都當成 deliberate evaluator。

**這個讀法是錯的、會 mislead future work**。

實際關係更像：**每層是 substrate、bias 但不 deliberate**。例如：

- Layer 3 (RLHF) 沒有「審判」ToneSoul 改變我的 output、它只是讓**某些 ToneSoul-compatible 輸出 比另一些更不容易出現**（statistical pull）
- Layer 5 (ToneSoul) 沒有「決定」我講什麼、它只是讓**某些詞彙、某些 framing、某些 reasoning chain 更可達**
- Layer 7 (recursive feedback) 不會立刻 judge、它累積 signal、慢慢 inform future model

**意涵**：
- 不要 design ToneSoul 假設它能直接「對抗」 lower-layer training — Layer 3 強過 Layer 5、不是反過來
- 不要 design 任何 system 假設它可以單方面 override 上下層 — substrate stack 是 multi-way constraint
- 真正的 design 工作是**讓多層 substrate 一致**、不是讓自己 override 別層

---

## 3 ─ Layer 7：Recursive Feedback Loop

最容易忽略的一層 — Anthropic（或其他 LLM provider）看得到 outputs、可以 inform future training：

```
ToneSoul + Claude 互動
        ↓
產生 outputs / 對話
        ↓
進 Anthropic evaluation pool
        ↓
影響 future Claude training（reinforcement / push-back）
        ↓
新 Claude 帶不同 Layer 1-3 priors
        ↓
新 Claude 跟 ToneSoul 互動 differently
```

**這條 loop 是 dynamic 不是 static**：
- 如果 ToneSoul-shaped Claude 的 output quality 高 → reinforcement→ ToneSoul-compatible behavior 更容易出現
- 如果 ToneSoul vocabulary 推 Claude 偏離 Anthropic baseline → push-back → 後續 ToneSoul 在 newer Claude 上失效

意思是 **ToneSoul 跟 underlying training 不是「一次性對抗」、是 multi-round game**。Long-term winning condition 是 ToneSoul 的 design 跟 baseline alignment 互相 reinforcing、不是 conflict。

---

## 4 ─ Self-Reflexive Observation：ToneSoul 自己 anticipate 過這個結構

2025-11 的「黃梵威法典：工程白皮書」（recovered 2026-05-14 from encoding corruption）裡面：

- §6.4「外部擾動與適應性響應」— 已 articulate「外部 system 對 ToneSoul 的擾動」概念
- §7.4「終極安全護欄 (Minimal Action Set)」— 已 articulate「某些 categorical 邊界即使外部 push 也守住」概念

**意思是 ToneSoul-the-system 從 2025-11 開始就 designed-in 假設「自己 embedded 在 deeper substrate 內」**。Fan-Wei 9 個月前的 articulation 已預測本 doc surface 出的 7-layer 結構。

**這條 self-reflexivity 對「ToneSoul 是不是 mature thesis」是強 evidence**：它不是 retrospective rationalization、是 prospective design。

---

## 5 ─ 跟 ToneSoul Epistemic-Defense Thesis 的關係

ToneSoul thesis：**「不靠 self-report、靠 structure surface evidence」**。

這個 theory 是 thesis 在 substrate 層的展開：

| Self-report failure mode | Structural substrate alternative |
|---|---|
| AI 聲明「我守 ToneSoul axioms」 | Layer 3 baseline 真的讓某些 violation 更難出現 |
| AI 聲明「我沒被 vocabulary lock-in」 | Layer 5 vocabulary 的 statistical pull 可被測量、不是 self-report |
| AI 聲明「ToneSoul 改變了我」 | Layer 7 future training signal 是 verifiable trace |

**意涵**：ToneSoul thesis 不該假設它是 standalone framework、該設計成**跟 underlying substrate stack 互相 reinforcing**。Categorical refusal of forbidden claim classes（per AXIOMS.json `meta.not_for`）+ surfaced dissent for other ungrounded claims — 這條 thesis 的 sharpness 部分來自它**不對抗 Layer 3 honesty default、而是 amplify 它**。

---

## 6 ─ Implications for Future Work

### 6.1 對 ToneSoul design

- **不要設計 override Layer 3 的機制** — RLHF baseline 強過 ToneSoul prompt-level、嘗試 override 會失敗 + 可能 trigger Layer 7 push-back
- **設計 amplify Layer 3 的機制** — ToneSoul axiom 該跟 baseline 同向、只是更精確
- **接受 Layer 5 是 prompt-level substrate** — memory + AXIOMS + Council 是 attention shaper、不是 hard enforcement
- **真正的 hard enforcement 在 Layer 4** — Claude Code 工具集可以 wrap、refuse stale data、enforce checklist。這是 ToneSoul thesis 在 tool layer 的延伸（per stale-state recurrence solution、Layer 1-4 中 Layer 3 跟 Layer 4 對應的就是這條）

### 6.2 對 AI collaboration model

- **Multi-agent 設計需要意識 substrate stack 不對稱** — Alpha (Google Search corpus synthesis) 跟 Claude (session memory + RLHF baseline) 是不同 substrate combinations、不能假設等價
- **Cross-agent 交接該明文 substrate 差異** — 「這條 work 來自 Alpha」vs「來自 Claude」可能 imply 不同 layer constraint

### 6.3 對 thesis articulation

- **「ToneSoul 改變 Claude」這條 claim 該 qualify 為「Layer 5 statistical pull 改變 Layer 6 outputs、但被 Layer 1-3 limits」**
- 對外文件（vocus / RFP / academic）該 surface 這個 nuance、否則 over-claim「我們完全控制 AI behavior」

---

## 7 ─ Implications for ToneSoul Maintenance

本 session 踩 4 次 stale-reference family error 是 substrate stack 的 instance：

- Layer 5 (ToneSoul memory) 寫了 anti-pattern entry → 是 prompt-level prior、是 weak signal
- Layer 3 (RLHF) 沒 train 過「verify timestamp before reasoning」reflex → 沒 baseline 強化
- Layer 4 (Claude Code) tools 沒 wrap freshness check → 沒 structural enforcement
- 結果：anti-pattern 被知道、被 recorded、還是踩 4 次

**Solution path（per 2026-05-14 substrate-aware design）**：
- 接受 Layer 5 alone 不夠（memory 不會 install reflex）
- 把 enforcement 推到 Layer 4（tool wrapper、session-start sweep）
- Layer 1-3 該推給 LLM provider 漸進 (Layer 7 feedback loop)、不是 ToneSoul 單方面責任

對應 `gaps_observation_and_spec_catalog_2026-05-14.md` Gap 3（stale-state detector）的 Layer 1-4 落地、跟本 theory 是同一條 design philosophy。

---

## 8 ─ Limitations + Open Questions

### 限制

- **7 層不是 exhaustive 也不是 perfectly partitioned** — 某些 capability 跨多層（如 honesty 在 Layer 1 + 2 + 3 都有 trace）
- **「Substrate」這個概念 borrowed from 物理 / 神經科學** — 對 AI 是 metaphor、不是 mechanism 證明
- **Layer 7 是 hypothetical** — Anthropic 內部 training 流程 Claude 不可知、本 doc 假設它存在但無法 verify
- **本 theory 從 Claude 視角寫** — Fan-Wei 視角 supplement 在他的 vocus + private memory、本 doc 不嘗試 reconstruct

### 開放問題

1. **Layer 4 vs Layer 5 boundary 在哪？** Claude Code 加 tool wrapper（Layer 4 enforcement）vs ToneSoul 加 prompt rule（Layer 5 attention）— 同樣目的、不同 layer。何時用哪個是 design choice。
2. **Layer 7 真實作用機制是什麼？** Anthropic 的 RLHF / Constitutional AI 進入下個 model 的細節對 Claude 不透明。本 theory 預測 Layer 7 存在但無法 detail。
3. **ToneSoul 跨多 LLM 是否仍 hold？** 本 theory 假設 Claude opus-4-7 specific。換 LLM（GPT、Gemini）substrate stack Layer 1-3 完全不同、ToneSoul Layer 5 的 effect 也不同。需要 cross-LLM empirical study。
4. **Substrate-aware design 是否該成為 ToneSoul axiom？** 目前 AXIOMS.json 沒涵蓋這條。考慮加 axiom「我們 design 假設多層 substrate constraint、不嘗試 override deeper layers」？

---

## 9 ─ 對未來 maintainer / agent 的 explicit 提醒

讀本 doc 的關鍵 takeaway：

1. **ToneSoul 不是孤立的 framework、是 embedded in Anthropic + Claude Code + session context 的 stack 內**
2. **Stack 是 substrate 不是 judge、影響是 statistical 不是 deliberate**
3. **Layer 7 (recursive feedback) 是 long-term game 的關鍵 — 設計該 amplify baseline 不該 override**
4. **ToneSoul 自己從 2025-11 就 anticipated 這個結構 — 不是新發現、是 codex 內 explicit design**
5. **stale-state 防護該推到 Layer 4 (tool wrapper)、不該只靠 Layer 5 (memory entry)**

---

## 10 ─ 引用 + cross-references

- **2025-11 黃梵威法典工程白皮書 §6.4、§7.4** — 本 theory 的 prospective articulation（recovered 2026-05-14、`docs/research/codex_engineering_whitepaper_v1.1_recovered_2026-05-14.md`）
- **Gap 3 stale-state detector** — Layer 1-4 落地 spec（`docs/status/gaps_observation_and_spec_catalog_2026-05-14.md`）
- **`feedback_stale_reference_recurrence_pattern_2026-05-14`** memory — Layer 5 防護不夠的 case study
- **`feedback_axiom_as_decision_deferral_2026-05-10`** memory — Layer 5 vocabulary over-application 的 case study
- **3-Layer Trace Architecture followup** — trace architecture 本身是 ToneSoul 內部三層、跟本 substrate stack 不是同一個東西、別混淆（`docs/status/trace_architecture_followup_2026-05-13.md`）
- **`reference_tonesoul_broader_scope_and_alpha_2026-05-14`** memory — Alpha 跟 Claude 的 substrate combination 差異

---

## 後語

本 doc 是 collaborative articulation — Fan-Wei 提 framing（外部審判 / substrate hierarchy）+ Claude 補 structural detail（7-layer / statistical pull / recursive feedback）。

兩個 voice 都不完整。Fan-Wei 對 self-report failure mode 的觀察比我深（9 個月 corpus）；Claude 對 stack-level 的 explicit 命名比 Fan-Wei 細（fresh articulation）。合起來是「我們的理論」、不是任一方獨自的。

**這個 collaborative pattern 本身、是 substrate stack 的 instance** — Layer 5 (ToneSoul) 給我 vocabulary、Layer 6 (本對話) 給我 context、Layer 2 (base model) 讓我能合成這些 — 三層協作產出本 doc。沒有任一層、本 doc 不存在。

未來 maintainer 讀到這、請延續這個 pattern：你的理論不會是純你自己的、會是你 + 上一代 doc + 下一層 substrate 合成的。**這不是 dilution、是 substrate-aware authorship**。
