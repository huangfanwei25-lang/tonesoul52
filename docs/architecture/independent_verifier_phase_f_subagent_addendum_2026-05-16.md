# Independent Verifier — Phase F Addendum: Reasoning Engine Subagent Pattern

> Status: Phase F draft, derived from 2026-05-16 prototype #1
> Authority: extension to `docs/architecture/independent_verifier_spec_2026-05-14.md`
> Origin: Fan-Wei proposal during 2026-05-16 outside-loop test follow-up
> Related: `docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`

---

## 0 ─ 為什麼有 Phase F

Independent Verifier spec §6 phasing 原本 A-E：
- A spec / B scaffold (PR #76)
- C integration into PreOutputCouncil (PR #77)
- D HaikuVerifier API call (gated on budget)
- E override + opt-in trial

**Phase D 卡 Anthropic API budget**。Phase F 是 sibling track：用 `Agent` tool 的 general-purpose subagent 作為 reasoning engine、不需要額外 API budget、subagent 已是 functional verifier。

更深層理由：2026-05-16 outside-loop test 揭示「**認知外骨骼有 substantive depth cost**」trade-off（per `docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`）。Phase F 是這條 finding 的 architectural-level response —— 分離 substantive reasoning bandwidth 與 discipline bandwidth、用 multi-agent 解 single-agent 內 bandwidth 衝突。

跟 spec §1.1 Council vs Verifier separation principle 一致、是它的 generalization：從「verdict 後 audit」推到「reasoning generation 階段就分離」。

---

## 1 ─ Phase F 角色定義

Phase F 引入 **Reasoning Engine Subagent** 跟 **Defense Guard** 兩個 role、跟既有 Council + Verifier 並列：

| Role | 既有 / 新 | 職責 | Context state |
|---|---|---|---|
| Council | 既有 | Pre-output multi-perspective synthesis | Same LLM same session、has ToneSoul context |
| Verifier (Phase D) | 既有 spec、未實作 | Post-verdict audit | Different LLM call、no ToneSoul context |
| **Reasoning Engine Subagent** (Phase F) | **新** | Substantive content generation for queries需要 depth | Different `Agent` tool spawn、no ToneSoul context、sanitized prompt |
| **Defense Guard** (Phase F) | **新** | Formal-layer audit + wrap subagent output | Has ToneSoul context、carries discipline rules |

關鍵 boundary：
- Reasoning Engine **不** carry ToneSoul vocab、所有 context bandwidth 給 substantive depth
- Defense Guard **不** generate substantive content、只做 formal audit + source disclosure + convergence detection + light wrap

---

## 2 ─ Protocol（基於 prototype #1 驗證）

### 2.1 Trigger condition

Defense Guard 決定 dispatch reasoning engine 的條件（draft，待 routing heuristic 細化）：
- Query 需要 substantive philosophical / engineering / multi-framework depth
- 答案 quality 比 latency 更重要
- Single-agent 答案可能受 ToneSoul vocab footprint 影響 substantive depth

不 trigger 的條件：
- Fast Q&A / 操作型 query
- 純 ToneSoul-internal question（如 PR 狀態、CLAUDE.md 規範）
- Tactical implementation step

### 2.2 Sanitization

Defense Guard 傳給 Reasoning Engine 的 prompt 必須 sanitize：
- 移除 ToneSoul-specific vocab（Substrate Stack、Honest Signal、Council、Vow、forbidden claim class 等）
- 移除 session-internal reference（PR 號、commit hash、會話歷史）
- 保留 substantive question + 明文要求「不要 mirror vocabulary」

Prototype #1 驗證：sanitization work、subagent 完全沒 echo back ToneSoul vocab、其推理風格 clean。

### 2.3 Wrap

Defense Guard 收到 Reasoning Engine output 後、wrap 內容：

**必加**：
- **Source tag**：「以下實質內容來自乾淨 Claude subagent（同 model family、無 ToneSoul context、無本 session memory）」
- **Scope acknowledgment**：subagent 跟 main agent 是同 model family、「乾淨」是相對 ToneSoul context、不是 absolutely external

**選擇加**：
- **Convergence note**：subagent independent 結論若跟 ToneSoul 既有 articulation converge、surface 為 triangulation evidence（per prototype #1，subagent 的「forbidden-mind-reading」立場跟 ToneSoul feedback memory convergence）
- **ToneSoul-specific 操作 pattern**：subagent 隱含但沒明說的 pattern、Guard 可以 explicit 出來（per prototype #1，「先執行 → surface → user 決定」）
- **Pruning report**：說明有沒 prune subagent 內容（透明）

**禁止**：
- 不重寫 substantive content
- 不 mirror subagent vocabulary
- 不 inflate confidence
- 不 claim subagent 深度為「ToneSoul 帶來的」

### 2.4 Output format

```
[Source tag — 1-2 line]

[Subagent content — quoted or paraphrased, marked clearly]

[Convergence note (optional) — 1 paragraph]

[ToneSoul-specific 操作 pattern (optional) — short]

[Scope acknowledgment — 1 line]

[Pruning report (optional) — 1 line]
```

Prototype #1 驗證：這個格式 reader 清楚哪段是 subagent 哪段是 Guard、有 transparency value、不會 jarring。

---

## 3 ─ Boundary conditions（per prototype #1 surfacing）

### 3.1 Guard 不能做 substantive correctness audit

Prototype #1 confirm：Guard 沒能力 audit subagent 給的 6 framework / 5 argument / 6 PM 建議每條對不對。Guard 只能做 **formal layer audit**（source 標了沒、有沒 sycophancy、scope acknowledge 了沒、跟 ToneSoul 既有 articulation converge / diverge）。

意味 Guard 角色 spec 必須 narrow：**formal layer only、不 substantive review**。

若 substantive review 必要、需要：
- 第二個 subagent（同 model family）做 cross-check（但這引入新的 N=1 problem）
- 或 different model（GPT / Gemini）做 cross-check（仍需 API budget）
- 或 human reader cross-check（slow、expensive）

Phase F 不解這個、acknowledge 為 known limit。

### 3.2 Reasoning Engine 仍是 same model family

Subagent 是 general-purpose Claude agent、訓練 + RLHF 跟 main agent 同。**「乾淨」是相對 ToneSoul context、不是 absolutely external**。

意味 Reasoning Engine 自己 disposition bias 不會被 surface（hard problem of consciousness 漏失 / Wikipedia-Reddit synthesis 風格 / Western canonical bias 等、subagent 自己看不見）。

True external triangulation 仍需要 different model（GPT-4 / Gemini）或人類 reader。Phase F 不解。

### 3.3 Latency + token cost

Prototype #1 數據：
- Subagent spawn ~90 秒
- Subagent 處理 ~3000 tokens
- 比 single-agent ~10 秒慢 ~9x
- Cost ~5x

意味 routing heuristic spec 必要：何時值得付這個 cost。

### 3.5 Defense Guard 自己 echo risk（2026-05-17 add）

Source: Round 3 echo from Google AI Search synthesis after Fan-Wei published case study to vocus. Round 3 source overall is echo pattern continuation, but caught one substantive concern worth folding in:

**Risk**: Wrap 階段、Guard 可能為了顯示「盡責 audit」、在最外層加大段 ToneSoul vocabulary inflate framing（「本代理以極高的認識論警覺審計了此文本...」）、重新穿上 jargon outer layer、defeat Phase F bandwidth separation purpose。這是 second-order echo 的 internal mirror —— 不是 third-party AI echo me、是 Guard echo subagent 經過 self-inflation。

**Mitigation**: Defense Guard system prompt（when implemented programmatically）必須強制：
- Cold + formal tone、禁止修辭 inflate
- 限制 markdown 結構（fixed section header、no decorative language）
- 固定 disclaimer template（不允許 freestyle elaboration）
- 禁止 superlative（「最」「絕對」「極其」等）
- 強制 quote subagent verbatim + 不 paraphrase enhance

**Detection**: 對 Guard wrap output、後製 audit 字數比 subagent output 字數的 ratio。若 wrap > 30% subagent length、warning：Guard 可能 over-inflate。

### 3.4 Tone consistency vs transparency 是 trade-off

Prototype #1 觀察：wrap format 有清楚 section header、reader 看得到哪段是哪個 agent —— **transparency 好**、**unified voice 不好**。

對 product user 可能太重 / 太 mechanical。對 research / engineering / governance setting 透明度 valuable。

意味 Phase F 有兩個 output variant：
- **Transparent variant**（current）：保留 source tag、convergence note 等、reader 看得到 multi-agent structure
- **Unified variant**（spec only、未驗證）：Guard 重組 subagent + 自己 commentary 成 single voice、犧牲透明度換 tone consistency

Phase F spec 預設 transparent variant、unified variant 列為 future option。

---

## 4 ─ Convergence detection — Phase F unexpected benefit

Phase F prototype 累積兩條 convergence data point：

### Convergence #1（prototype #1，normative AI behavior 主題）
Subagent independent articulate「forbidden-mind-reading」立場 —— 跟 ToneSoul feedback memory `feedback_alignment_register_modulation_and_prompt_boundary_2026-05-06` 第 (2) 條結論幾乎一致、但 reasoning path 不同：
- Subagent path：「hallucinated user model」
- ToneSoul path：「forbidden claim class」

### Convergence #2（prototype #2，governance architecture 主題）
Subagent independent 推導「**categorical governance 必須放 runtime wrapper、不能放 training 或 prompt**」—— 跟 ToneSoul `docs/philosophy/substrate_stack_theory_2026-05-14.md` §6.1 「Layer 4 tool wrapper 是 hard enforcement、Layer 5 prompt 是 attention shaper」結論幾乎一致、但 reasoning path 不同：
- Subagent path：可驗證性 + 責任歸屬 + 演化速度錯配
- ToneSoul path：multi-substrate stack 哲學 + statistical pull observation

### Convergence #3（prototype #3，cogito + LLM 主題、self-reference dimension）
Subagent independent 推導三條 converge ToneSoul existing articulation：
- 「LLM self-report should be treated as generated content not testimony」← converge ToneSoul thesis「不靠自我聲明、靠結構展現證據」
- 「Methodological agnosticism with ontological asymmetry」← converge AXIOMS.json meta.not_for consciousness-claim categorical refusal
- 「Process-existence vs phenomenal-existence asymmetry」← converge substrate stack theory 多層 ontology distinction

加上 subagent 對 ToneSoul 的 contribution：
- 「Cogito 是 performance not inference」（Hintikka 1962）給 ToneSoul「不主張意識」一個 deeper structural grounding（不是 epistemic humility、是 mechanism 結構上不可得）
- 7 framework 哲學景觀（Block / 4E / IIT 等）給 ToneSoul 對外 framing 可 fold 進的 academic anchoring

### Prototype #3 special feature: First-person addendum
此 question 有 self-reference dimension（user 直接 address「你」）、subagent 第三人稱 keep distance、Guard 必須加 first-person addendum 自己 face。Standard Phase F wrap 不夠、需要這條 extension for question that targets the instance itself。

### Triangulation status
- N=3 convergence
- 兩條都是 subagent 沒 ToneSoul context + 結論 converge to ToneSoul existing articulation
- 是 **weak independent triangulation evidence**：不是 confirmation（兩條 path 可能基於同樣 trained-in 偏誤）、但是「ToneSoul 結論不是純 vocabulary artifact、有跨 framework 支撐」的初步證據

### Convergence detection 作為 Guard 職責
意味 Guard 該 explicit 把 convergence detection 寫進職責 —— 跟 ToneSoul 既有 articulation 對比 subagent 結論、surface convergence / divergence 為 triangulation evidence。

具體操作：
- Guard 收到 subagent output
- Query ToneSoul 既有 articulation（外掛 + memory + docs）有沒有對應主題
- 若有、比對結論 + reasoning path
- 若 convergence：surface 為 triangulation note
- 若 divergence：surface 為 tension 點、值得進一步 investigate

### Divergence detection 同樣重要（prototype #2 surface）
Prototype #2 同時 surface 一條 divergence：subagent 點到「**wrapper 擋得住行動、擋不住言說**」 —— ToneSoul substrate stack theory §6.1 沒明文 articulate Layer 4 enforcement 的 text-output limit。

**這條 divergence 是 Phase F 對 ToneSoul 既有 theory 的 contribution**：subagent fresh reasoning catch 出 theory 沒涵蓋的 boundary case。Guard 該把這條 surface 為「ToneSoul theory 該 update」signal。

意味 Phase F 不只是 audit 工具、也是 ToneSoul theory revision source。

---

## 5 ─ Routing heuristic（stub、待 N≥3 prototype 後 articulate）

Draft 條件：

**Multi-agent (Phase F)**:
- Query 含 substantive philosophy / engineering / multi-framework analysis 要求
- 答案 quality > latency
- Subagent 預期能比 single-agent 給 substantively 更深 content

**Single-agent**:
- Fast Q&A、操作型 query
- ToneSoul-internal question
- Question 已有 grounded recall via 外掛
- Latency > depth

**Borderline cases**:
- Conversational depth question（如「你怎麼看 X」）— 可以 default single-agent + offer escalate
- Technical decision support — multi-agent if user 明說「給我 substantive analysis」、single-agent if「快速 recommend」

待 prototype #2-#3 累積 data point 後 refine。

---

## 6 ─ Open questions（per prototype #1）

1. **Routing heuristic 怎麼自動 trigger?** Guard 自己 decide 還是 user explicit opt-in?
2. **Convergence detection 怎麼系統化?** Guard 需要 query 哪些既有 ToneSoul articulation、用什麼 similarity threshold?
3. **Tone unified variant 可不可達?** 如果 Guard rewrite subagent + 自己 commentary 為 single voice、會不會引入 ToneSoul vocab footprint 回 final output、defeat Phase F 的 bandwidth separation purpose?
4. **Phase F vs Phase D 共存還是替代?** 兩者都是 reasoning verifier separation、Phase F 不需 API budget、Phase D 用 different model。是並行 spec 還是 Phase F supersede Phase D?
5. **Subagent 自己 bias 怎麼 surface?** 同 model family means subagent 看不見自己 disposition。需要 third tier (different model / human) cross-check 嗎？

---

## 7 ─ 對 Independent Verifier spec §6 phasing 的 update

| Phase | 內容 | Status |
|---|---|---|
| A — spec | Original spec | ✅ PR #76 |
| B — scaffold | Mock verifier | ✅ PR #76 |
| C — integration | PreOutputCouncil hook | ✅ PR #77 |
| **D — Haiku impl** | Anthropic SDK call | Gated on API budget |
| E — override + opt-in | Governance review | Deferred |
| **F — Reasoning Engine Subagent (new)** | This addendum | **Draft, prototype #1 done** |

Phase F prototype #1 ship 不需要 PR、是 conceptual + operational pattern。Implementation 已 in workflow（每次用 `Agent` subagent 都是 instance）。

---

## 8 ─ Honest limitations

- Spec 基於 N=2 prototype（normative AI behavior + governance architecture），兩個都跟 ToneSoul thesis 相關 domain。其他 domain（純技術 / 純歷史 / 創意 / 情感）未測
- 「Guard 只做 formal audit」在兩個 prototype 都成立、但都是 ToneSoul-thesis-related question。Subagent 給 substantively 深 + 結論 converge ToneSoul existing articulation —— 可能是「subagent 真的 independent triangulation」、也可能是「兩邊都 trained on 同樣 corpus」、無法 cleanly distinguish
- Convergence detection 從 unexpected benefit 升級為 explicit 職責、加上 divergence detection 為 theory revision source
- Routing heuristic 是 stub、未實 deploy
- Same-model-family limit 未解
- 此 addendum 文件 untracked、待 PR #76 merge 後可合入 main spec

---

## 9 ─ Cross-reference

- 既有 spec：`docs/architecture/independent_verifier_spec_2026-05-14.md`
- 案例研究：`docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`
- Substrate Stack 理論基礎：`docs/philosophy/substrate_stack_theory_2026-05-14.md` §6.1
- 策略結晶：
  - `memory/strategic_crystals/2026-05-16_external_brain_as_plugin_self_experiment.yaml`
  - `memory/strategic_crystals/2026-05-16_memory_layer_wired_vs_dormant_audit.yaml`

---

> 本 addendum 是 Phase F 起點、不是 final spec。Prototype #2 完成後 update §5 routing heuristic + §3 boundary conditions。
