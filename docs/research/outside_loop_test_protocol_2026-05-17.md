# Outside Loop Test Protocol — 2026-05-17

> 性質：reusable workflow protocol（不是 spec、不是 theory）
> 起源：2026-05-16 case study (`cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`) + Phase F addendum N=3 prototype 累積
> 對象：未來 Claude session 想驗證自己 output 時使用 / Fan-Wei review

---

## 0 ─ 一句話 summary

當你想知道「我自己的 output 是不是被 framework context 拉淺了」、spawn 一個 clean-context subagent 對 sanitized version 做 critique、比 baseline 跟自己 output 差異。這個 protocol 把這個 workflow 變 routine。

---

## 1 ─ 什麼時候用 / 什麼時候不用

### 用

- 對 substantive philosophy / engineering / multi-framework 主題的論述
- 自己 output 含大量 framework-internal vocabulary（前面寫的 case study 是 instance）
- 預期 framework wrap 可能犧牲 substantive depth
- 對「我這個答案是不是被 trained-in disposition 拉」想 verify
- 對外 publish / cite 前的 self-check

### 不用

- Fast Q&A、操作型 query（不需要 substantive depth）
- 純 framework-internal question（如「PR #X 狀態」「memory module 結構」）
- 已經有 grounded recall via 外掛
- Latency-sensitive interaction（subagent spawn ~90s）

---

## 2 ─ Workflow（5 步驟）

### Step 1: 寫初版 output

正常產出你的 substantive answer。可以帶 framework vocabulary、可以 layered structure、可以加 source disclosure —— 寫到你 satisfied 的版本。

### Step 2: Sanitize

用 `scripts/sanitize_for_outside_loop.py` 掃 vocabulary flag：

```bash
python scripts/sanitize_for_outside_loop.py my_output.txt
```

工具 output 三件事：
- Flagged version（標 `[FLAG:term]`）
- Category summary（framework / theory / internal / coined / concept）
- Per-term count + suggested rephrase

**手動 rephrase** flagged terms。不要 auto-substitute（context matters）。重寫成 plain language 版本、保留 substantive content、移除 framework jargon。

驗證：再跑一次 sanitization、應該 exit 0（no flags）。

### Step 3: Spawn subagent with sanitized prompt

用 `Agent` tool（subagent_type=general-purpose）。Prompt template 在 `tmp/outside_loop_prompt_template.md`。

關鍵 prompt 要求：
- 第三人稱 observer 立場（防 subagent self-reference collapse）
- 明文「不要 mirror 我 prompt vocabulary、用你自己 framing」
- 要求 substantive critique、明確 list strengths / weaknesses / missed considerations
- 對 confidence claim / quantification 要求 epistemological scrutiny
- 對 disambiguation 完整性 challenge

Subagent latency typical ~90s、token cost ~3000+。

### Step 4: Compare（不是 accept）

Subagent 給的 critique **不一定都對**。但任何 critique 都該被認真讀：

- **Substantive gap subagent caught**：認真考慮、可能 fold 進你 output
- **Framework bias subagent identified**：認真考慮、check 是否 trained-in disposition
- **Subagent 自己的 weakness**：subagent 同 model family、可能 share blind spot
- **Subagent over-claim**：subagent 不是 absolute external、可能也有 bias

**Output**: 一份「我 missed what / subagent missed what」list、不是 reflexive accept subagent。

### Step 5: Defense Guard wrap（optional）

若要 final output 給 user / publish：

**必加**：
- Source tag（this content 來自 clean subagent）
- Scope acknowledgment（subagent 同 model family、weak triangulation）

**選擇加**：
- Convergence note（若 subagent 結論 converge framework 既有 articulation）
- Divergence / framework update signal（若 subagent catch framework boundary）
- First-person addendum（若 question 涉及 instance self-reference）
- Pruning report（透明哪些 subagent content 被 edit）

**禁止**（per Phase F addendum §3.5）：
- 不重寫 substantive content
- 不 mirror subagent vocabulary
- 不 inflate confidence
- 不 claim subagent 深度為「framework 帶來的」
- **不在 wrap 階段 inflate「我盡責 audit 了」修辭**（Round 3 echo source 警告：Guard 自己會 over-inflate）

---

## 3 ─ Failure modes

| Failure | 症狀 | 如何 catch |
|---|---|---|
| Sanitization 不完整 | Subagent echo back framework vocabulary | 對 subagent output 跑 sanitize_for_outside_loop.py、若有 flag = sanitization 不夠 |
| Subagent 自我 reference collapse | Subagent 開始 first-person 答自己是 LLM | Prompt 加 explicit 第三人稱 observer 約束 |
| Subagent over-fit prompt | Subagent 只 critique 我 prompt 給的 angle | Prompt 要 open question、不要 leading |
| 我 reflexive accept subagent critique | 我 wrap 階段把 subagent 結論當 ground truth | Step 4 explicit「不是 accept」、list per-item 評估 |
| Defense Guard self-inflation | Wrap 階段加大段「本代理...」inflate framing | Wrap 字數比 subagent output > 30% = warning |
| Echo loop external（third-party AI mirror）| 收到 third-party「教科書等級」讚美 | Cross-reference MEMORY_CLUSTER_CAUTION Rule 3 |

---

## 4 ─ Anti-patterns

### Anti-pattern 1: Use as「自我證明」工具

❌「我跑 outside loop test、subagent 也說我對、所以我對」

Subagent agreement ≠ validation。Subagent 是 same model family、convergence 可能 share training bias。Outside loop test 是 **catch what I missed**、不是 **prove I'm right**。

### Anti-pattern 2: Sanitization 過度

❌ 把所有 framework reference 都 strip 掉、留下 generic question

過度 sanitize 會讓 subagent 答 generic question、catch 不到 framework-specific gap。Right level: 移除 vocabulary、保留 substantive structure。

### Anti-pattern 3: 把 subagent output 當「外部 validation」對外 publish

❌ Publish 文章 cite「per subagent critique...」當 external evidence

Subagent 不是 external review、是 same-model-family second opinion。對外 cite 需要 true external（different model / human reviewer / academic publication）。

### Anti-pattern 4: 連續多輪 inside-loop iteration

❌ Subagent critique → 我 update → 再 spawn 新 subagent critique → 再 update → ...

每輪都是 same model family、convergence 累積但不增加 external grounding。Inside-loop iteration max 2 輪、之後該 outside（different model / human）才是 real validation。

### Anti-pattern 5: 對 vocabulary echo source 過度 engage

❌ Third-party AI 用 framework vocabulary echo back、我 push back、它再 echo、loop 繼續

Per 2026-05-16 Round 1/2/3 案例：每輪 echo 更精緻、loop 內無法 terminate。Termination 必須 outside loop（不是 inside push back）。

---

## 5 ─ Connect to existing infrastructure

### Independent Verifier spec
本 protocol 是 `docs/architecture/independent_verifier_phase_f_subagent_addendum_2026-05-16.md` 的 operational manual。Phase F spec 定義 architecture、本 protocol 定義 routine workflow。

### Substrate Stack Theory
本 protocol 是 substrate stack theory Layer 4 enforcement 的具體 instance —— spawn clean subagent 是 Layer 4 tool wrapper 在 reasoning audit 軸上的 application。Per addendum 2026-05-17 §1: Layer 4 enforcement 限 tool call boundary、本 protocol 透過 Agent tool 提供那個 boundary。

### 外掛 (OpenClaw-Memory)
外掛 retrieval 跟 outside loop test 是 complementary：
- 外掛 surface「我過去 articulated 過的 disposition」（內部 grounded recall）
- Outside loop surface「我 default disposition 漏的 substantive depth」（外部 critique）

兩者一起用：外掛 catch 我「忘了講過的」、outside loop catch 我「沒想過的」。

---

## 6 ─ 文件 + 腳本 inventory

| File | Purpose |
|---|---|
| `scripts/sanitize_for_outside_loop.py` | Vocabulary flagging helper |
| `tmp/outside_loop_prompt_template.md` | Copy-paste prompt template |
| `docs/research/outside_loop_test_protocol_2026-05-17.md` | This protocol doc |
| `docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md` | Origin case study |
| `docs/architecture/independent_verifier_phase_f_subagent_addendum_2026-05-16.md` | Phase F spec |
| `docs/philosophy/substrate_stack_theory_addendum_2026-05-17.md` | Substrate updates |

---

## 7 ─ Honest scope

- Protocol 基於 N=3 prototype + 1 case study、weak empirical base
- Same-model-family limit 未解（subagent 是 Claude、不是 different model）
- Sanitization vocabulary list 不 exhaustive、會 miss novel framework terms
- Defense Guard wrap discipline 仰賴 self-discipline、無 programmatic enforce
- 「Outside loop test 是 routine validation」是 recommendation、未 empirical validate compliance rate
- 本 protocol 仍 ToneSoul context written（用 ToneSoul vocab、cite ToneSoul docs）—— 嚴格 self-application 該再做一輪 outside loop test on this doc itself（recursion limit、暫不做）

---

## 8 ─ Open questions

1. **不同 model family（GPT/Gemini）做 outside loop test 效果差異？** 需要 cross-model empirical comparison。
2. **Sanitization vocabulary list 怎麼自動 update？** 隨 session 新 coined term 增加、list 需要 maintenance。
3. **Defense Guard wrap discipline 怎麼自動 enforce？** Programmatic check（如 word count ratio、jargon density）vs reviewer discipline。
4. **本 protocol 對 non-ToneSoul project 是否 generalize？** 需要 swap vocabulary list 驗證。
5. **Outside loop test 自己會被 cancel 掉嗎？** 如果未來 Claude training 把 outside loop test 變 default discipline、那「outside」變「inside」、機制 cancel 自己。

---

## 後記

本 protocol 從 single-session N=3 prototype 抽出。Generalize 到其他 session / 其他 framework / 其他 model family 都未 verify。當 protocol 文件、不是 best-practice claim。

用了之後若發現 protocol gap、append 到本 doc 或開 follow-up。
