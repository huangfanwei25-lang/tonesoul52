# Claim-to-Evidence Auditor — Phase 2–4 Handoff to Codex (work-order)

> 作者：Claude (Opus 4.8),依 Fan-Wei 指示寫給 Codex 自主推進至結案
> 日期：2026-06-25
> 狀態：**work-order / plan**。Phase 0 spec = `docs/plans/claim_to_evidence_auditor_2026-06-24.md`;
> Phase 1 = PR #187(已 Claude 獨立 review,verdict: approve-with-notes)。
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

## §1 Phase 1 review 的 carry-over(先清這兩條)

Claude 獨立探針在 PR #187 抓到、Codex happy-path 測試沒覆蓋的兩條(都不是 blocker,是 lexical
tradeoff;但要嘛修、要嘛當 known limitation 寫進文件,不能默默留著):

- **L1 — False NEGATIVE,前置子句否定過度抑制。**
  `This is not a toy; it guarantees safety.` → 0 findings。`is_negated_scope_statement` 掃
  match 前 flat 80 字元窗,所以**前一個子句**的 `not` 會殺掉**後一個子句**的真 overclaim。
  → 修法:把否定窗 **clause-scope**(以 `;`/`.`/`,` 切句,只看 match 所在子句),不要 flat window。
  → 釘測試:這個 input 應 flag(修好後)或標 `xfail` 並寫進 limitations(若暫不修)。

- **L2 — False POSITIVE,數字/量詞限定沒被辨識。**
  auditor 會 flag `POSITIONING.md` 自己誠實的 **"0 fully enforced"**(`strongest_tier_enforcement_overstated`)——
  guard 認得 `no/not/never`,不認得 `0 / none / zero`。**結果是工具 flag 了倉庫自己的誠實 ledger。**
  → 修法:把 `0 / zero / none (of) … fully enforced` 這類**量詞-零限定**納入 negation/scope guard。
  → 釘測試:`0 fully enforced` 應 → 0 findings;`fully enforced everywhere` 仍應 flag。

---

## §2 Phase 2 — deterministic 規則硬化 + modes `[determinism 不可破]`

1. 清掉 §1 兩條,各帶 pinned test。
2. 擴充 rule 覆蓋(更多 overclaim 類)——但**每加一條 rule,必須同時加一個 false-positive
   fixture**(證明它不會誤報合法措辭),否則不准進。
3. 依 Phase 0 spec 補 `--issue`(產生可貼進 GitHub issue 的 sanitized 摘要)與
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
2. **誠實 limitations 文件**:lexical-only、paraphrase/unicode/拆字 evade、L1 clause-negation、
   L2 量詞限定(若留)、LLM 層是 advisory-候選。明寫「它做不到什麼」。
3. **characterization report**(`canonical: false`,跟其他 honesty-auditor harness 同規格):在
   sanitized fixtures 上量 catch / miss rate,**把 miss 也報**。接進 honesty scoreboard 作另一個
   個別 piece(**不**併成總分)。
4. publish the nulls。

---

## §5 誠實邊界(從 Phase 0 帶下來,每個 Phase 都重述進 acceptance criteria)

- **不是** truth oracle;不裁定真值、倫理、意圖、身份、production readiness。
- **flags patterns, 不 comprehend**;paraphrase / unicode / 拆字可穿透——這是**有記錄的限制**,不藏。
- **不認證 ToneSoul 自己**;它對 ToneSoul 的文件一樣會 flag(且**應該**會,如 L2 那樣)。
- advisory:有 findings 也 `exit 0`;它是 reviewer 的輔助,不是 runtime gate。
- **一個 overclaim 自己偵測力的 auditor,會變成它所稽核的那個東西**——別讓它宣稱比量到的多。

---

## §6 結案的定義 (Definition of Done)

**不是**「Codex 說做完了」。是以下全中:

1. Phase 2–4 全 merge,且每步都過了 §0 的獨立驗證閘(不是 self-report);
2. §1 兩條 limitation:修好+釘測試,或寫進 limitations 文件+標 xfail;
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
