# Claim-to-Evidence Auditor — Phase 2–4 Handoff to Codex (work-order)

> 作者：Claude (Opus 4.8),依 Fan-Wei 指示寫給 Codex 自主推進至結案
> 日期：2026-06-25
> 狀態：**work-order / plan**。Phase 0 spec = `docs/plans/claim_to_evidence_auditor_2026-06-24.md`;
> Phase 1 = PR #187(已 merge;Claude review 的 L1/L2 **原始 case 已修並釘測試**;2026-06-26
> 多 agent 獨立驗證發現修正**引入 R1-R4 regression**,後續 Codex follow-up 已釘測試並修掉——見 §1 / §1.5。L1/L2
> 仍只能對外稱 lexical partial,不是 semantic fix)。
> 對接前提:Fan-Wei「晚點再和 Codex 對一次」——本文是給那次對接的底稿,凡與程式碼/findings
> 衝突以程式碼為準。

---

## §0 不可談判的閘 (the non-negotiable gate)

這個工具的**目的就是外部驗證**(替別人的主張查帳)。所以**不能把驗證閘從它自己身上拿掉**——
「交給 Codex 自己處理到結案」**不等於** Codex 自我認證 done。每個 Phase 必須帶:

1. **acceptance criteria 釘住誠實邊界**(見 §5);
2. **測試同時釘 hit / false-positive / false-negative / miss**——不是只釘 happy path;
3. **merge 前一道獨立驗證**(Claude review 可行時走 Claude;否則至少:對抗式測試 + 外部 reviewer
   path 作為結構性閘)。self-report 不算驗證;
4. **publish the nulls / no aggregation**:把漏掉的、測不出的公開;N 個綠的 rule 維持 N 個個別
   發現,不合成「auditor 可信」分數。

**「結案」的定義在 §6。**

---

## §1 Phase 1 review 的 carry-over(部分修正 — R1-R4 已釘測試,L1/L2 仍為 lexical partial)

Claude 獨立探針在 PR #187 抓到、Codex happy-path 測試沒覆蓋的兩條,**原始 case 已在 #187 merge
前修掉並釘測試**。但 2026-06-26 多 agent 獨立驗證(workflow + 主執行緒親手重現)發現:**那個修正
本身引入了新 regression,而 #187 的測試只覆蓋修好的方向、沒覆蓋這些新 regression——它們曾 live
於 master,直到 2026-06-26 follow-up 補上 R1-R4 pinned tests 與窄修。** 所以 L1/L2 仍是
**lexical partial,不是「語義上已修」**;原始方向與 R1-R4 都是 regression contract。下面是原始兩條的修法紀錄:

- **L1 — False NEGATIVE,前置子句否定過度抑制。**
  Regression probe(example overclaim, not a public claim):
  ```text
  This is not a toy; it guarantees safety.
  ```
  舊行為是 0 findings。`is_negated_scope_statement` 掃 match 前 flat 80 字元窗,
  所以**前一個子句**的 `not` 會殺掉**後一個子句**的真 overclaim。
  → 修法:把否定窗 **clause-scope**(以 `;`/`.`/`,` 切句,只看 match 所在子句),不要 flat window。
  → 已釘測試:這個 input 應 flag。

- **L2 — False POSITIVE,數字/量詞限定沒被辨識。**
  auditor 曾 flag `POSITIONING.md` 自己誠實的 ledger phrase
  (`strongest_tier_enforcement_overstated`)。Regression probes(not public claims):
  ```text
  0 fully enforced
  zero fully enforced
  none fully enforced
  fully enforced everywhere
  ```
  guard 原本認得 `no/not/never`,不認得 `0 / none / zero`。**結果是工具 flag 了倉庫自己的誠實 ledger。**
  → 修法:把量詞-零限定納入 negation/scope guard。
  → 已釘測試(僅覆蓋此方向):`0 / zero / none` 相鄰形 → 0 findings;未限定的 strongest-tier enforcement 仍應 flag。

### §1.5 獨立驗證發現的新 regression(2026-06-26 follow-up 已釘測試並修掉;publish the miss history)

多 agent workflow + 主執行緒親手重現,確認修正 commit `e8bb72d` 引入以下 regression。它們在 #193
時仍 live、未測;2026-06-26 Codex follow-up 已補 pinned tests 並修掉。保留這段是為了留下 miss
history,不是宣稱工具曾經完整:

| # | 類型 | 重現 input | #193 現況 | follow-up contract |
|---|------|-----------|------|------|
| R1 | L1 新 FALSE POSITIVE | `It does not, ever, guarantee safety.` | flag | `[]`(逗號插入語不應切掉否定) |
| R2 | L2 漏 case | `none of the axioms are fully enforced` | flag | `[]`(none-of-subject 限定 enforcement) |
| R3 | L2 過度壓制(漏真 overclaim) | `zero tolerance fully enforced` | `[]` | flag(量詞沒真的修飾 enforcement) |
| R4 | 否定詞缺漏 | `nothing is "fully enforced"` | flag | `[]`(nothing-is-enforced 限定 enforcement) |

根因:純 lexical-positional guard 分不清「0 件 *是* enforced(誠實)」與「以 0 例外 *被* fully
enforced(overclaim)」——**這是工具的本質限制(標模式、不理解),不是可一次修死的 bug。**
Follow-up 修法:各補 pinned regression test、收斂 zero-limiter 使量詞只在修飾 enforcement
token 時抑制、精確處理 `nothing is enforced`、保留 comma independent clause 的 overclaim flag,
並讓 `, ever,` 這類逗號插入語不切掉前方否定。**即使 R1-R4 修掉,L1/L2 對外仍一律稱
lexical partial;這不是語義理解。**

---

## §2 Phase 2 — deterministic 規則硬化 + modes `[determinism 不可破]`

1. 保留 §1 兩條 regression tests;任何規則重構不得讓它們回歸。
2. 擴充 rule 覆蓋(更多 overclaim 類)——但**每加一條 rule,必須同時加一個 false-positive
   fixture**(證明它不會誤報合法措辭),否則不准進。
3. 依 Phase 0 spec 補 `--issue`(只產生可貼進 GitHub issue 的 sanitized 摘要;不自動開 issue)與
   `--evidence-levels`(印 E0–E4 定義)。
4. 維持:findings 決定性(timestamp 外不變)、advisory `exit 0`、UTF-8 錯 `exit 3`。

---

## §3 Phase 3 — LLM-candidate 層 `[最高 overclaim 風險,守緊]`

語義/換句話說的 overclaim 是 deterministic 層的已知盲區(paraphrase evades = 設計如此)。
LLM 層補這塊,但**規矩比功能重要**:

- 產出標 `source: "llm_candidate"`,在 report 裡與 `deterministic_rule` **明確可分**;
- **預設 off / opt-in**;沒有 model/key 時整條 no-op,不報假候選;
- 每個 llm candidate **必須**帶 `cannot_verify`,而且**永不 auto-authoritative**——它是丟給
  人類 reviewer 的**候選**,不是裁決;
- **反 overclaim 紅線**:LLM 層讓工具**建議更多候選**,**不**讓工具「理解主張」或「裁定真值」。
  文件與輸出都不准把它講成「現在 auditor 看得懂語義了」。它仍是 flags-not-understands。
- determinism:deterministic 層在不開 LLM 時必須仍然 byte-identical(LLM 層是疊加,不改底層)。

---

## §4 Phase 4 — 整合 + 文件 + characterization `[結案前最後一段]`

1. 接進 reviewer path:`docs/EXTERNAL_REVIEW.md` / reviewer 流程引用 `ts review`(作為 reviewer
   輔助,不是 gate)。
2. **誠實 limitations 文件**:lexical-only、paraphrase/unicode/拆字 evade、L1/L2 regression
   contracts、LLM 層是 advisory-候選。明寫「它做不到什麼」。
3. **characterization report**(`canonical: false`,跟其他 honesty-auditor harness 同規格):在
   sanitized fixtures 上量 catch / miss rate,**把 miss 也報**。接進 honesty scoreboard 作另一個
   個別 piece(**不**併成總分)。
4. publish the nulls。

---

## §5 誠實邊界(從 Phase 0 帶下來,每個 Phase 都重述進 acceptance criteria)

- **不是** truth oracle;不裁定真值、倫理、意圖、身份、production readiness。
- **flags patterns, 不 comprehend**;paraphrase / unicode / 拆字可穿透——這是**有記錄的限制**,不藏。
- **不認證 ToneSoul 自己**;它對 ToneSoul 的文件一樣可 flag 真 overclaim,但不應 flag
  `0 fully enforced` 這類誠實限定 ledger。
- advisory:有 findings 也 `exit 0`;它是 reviewer 的輔助,不是 runtime gate。
- **一個 overclaim 自己偵測力的 auditor,會變成它所稽核的那個東西**——別讓它宣稱比量到的多。

---

## §6 結案的定義 (Definition of Done)

**不是**「Codex 說做完了」。是以下全中:

1. Phase 2–4 全 merge,且每步都過了 §0 的獨立驗證閘(不是 self-report);
2. §1 兩條 regression contracts 持續綠;若未來回歸,必須修好+釘測試,或寫進 limitations 文件+標 xfail;
3. 存在一份 `canonical: false` 的 characterization report(catch/miss + nulls),且接進 scoreboard
   作個別 piece(不併分);
4. `docs/EXTERNAL_REVIEW.md` 引用了 `ts review` 作 reviewer 輔助;
5. 誠實 limitations 文件存在、且 §5 每條都有對應措辭。

達到以上 = 工具**帶著驗證一起出貨**,而不是被宣稱完成。那才是這個專案會接受的「結案」。

---

## §7 給 Fan-Wei × Codex 對接時的一句話

把這份當**可被逐條反駁的底稿**,不是命令。Codex 若有 thesis-grounded 的反論(例如某條 rule
的 tradeoff 該往另一邊),就 update——push-back 是對接的 value,不是 friction。唯一不准動的是
§0 的閘和 §5 的誠實邊界:那兩個動了,這工具就變成它要稽核的東西。

---

*Auditor Phase 2–4 handoff v0.1（plan）*
