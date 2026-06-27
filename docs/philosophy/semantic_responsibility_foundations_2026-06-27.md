# 語義責任的基礎 — Pragmatics, Ethics, and the Security Lineage
# Foundations of Semantic Responsibility

> **日期 / Date:** 2026-06-27 · **Author trail:** claude-opus-4-8, commissioned by Fan-Wei Huang
> **狀態 / Status:** foundations memo. 記錄「為什麼」,不計算「是什麼」/ records *why*, does not
> compute *what*. §5(創作者倫理)是黃梵威的、可修正、非 AI 立場、不可強制執行 / §5 is
> Fan-Wei's, correctable, not the AI's position, not enforceable code.
> **語言 / Language:** 雙語;學術引用與逐字 maxim 保留英文 / bilingual; academic citations and
> verbatim maxims kept in English.

## §0 這是什麼,以及綁住它的紀律 / What this is, and its disciplines

這份文件定位 ToneSoul「語義責任 (semantic responsibility)」所倚靠的哲學。三條紀律綁住每一行:

This locates the philosophy ToneSoul's "semantic responsibility (語義責任)" rests on. Three
disciplines bind every line:

1. **claim ≤ evidence — 連對這套哲學本身也是。** 引用皆 web 查證,**以 maxim/condition 名稱**
   引用、不用未核對的頁碼。 / citations web-verified, cited by name not by un-checked pages.
2. **Convergent, not novel(收斂,非原創)。** ToneSoul **應用** 數十年的語用學、倫理學與古典
   資安;它不發明。寫「ToneSoul applies X」,絕不寫「independently arrived at X」。
3. **碼不計算倫理。** 承重邊界(§1):碼讓承諾**可回讀、可挑戰**,**不**計算其真假對錯。

## §1 邊界:「什麼是誠實 / 背叛」不是 if-else / The boundary

> 「什麼算誠實」與「什麼算背叛」**無法化約成 if-else**,因為兩者都是**語用且規範的判斷**——
> 取決於斷言 vs. 言外之意、取決於對自己信念的欺瞞意圖、取決於情境的 felicity conditions、
> 取決於一個「違反 vs. 背叛」界線本身就有爭議、無單一化約定義的信任關係。所以碼只能讓承諾
> **可回讀、可挑戰**(flag、threshold、refusal、append-only audit trail);它**不能計算**其
> 真假對錯。**沒有 oracle**——這正是為什麼 auditor 把「truth of the claim」列為 `cannot_verify`、
> 出 proxy 而非判決。(也是 `AXIOMS` Axiom 5 刻意不 enforce:不存在 runtime accuracy oracle。)

> "What counts as honesty" and "what counts as betrayal" cannot be reduced to `if-else` — both
> are pragmatic-and-normative judgments (assertion vs. implicature; intent to deceive about
> one's own beliefs; felicity conditions; a relational trust whose breach-vs-betrayal line is
> itself contested). The code can only make commitments **traceable and challengeable**; it
> cannot compute their truth or rightness. **There is no oracle** — hence "truth of the claim"
> is `cannot_verify`, and AXIOMS Axiom 5 is left un-enforced.

「no oracle」「claim ≤ evidence」「cannot be reduced to if-else」是 **ToneSoul 自己的工程
gloss**,不是下列哲學家的用語。 / These are ToneSoul's own engineering glosses, not terms from
the philosophers cited below.

## §2 語用學與倫理接地 / Pragmatics & ethics grounding

語義責任由什麼構成(每條都是**應用**,非發明)/ What semantic responsibility is made of (each is
*applied*, not invented):

| ToneSoul 概念 / concept | 它應用的古典概念 / the classical concept it applies | 出處 / Source |
|---|---|---|
| **claim ≤ evidence**(reviewer 規則 / `cannot_verify` / E0–E4 ladder) | **Maxim of Quality, sub-maxim 2**: "Do not say that for which you lack adequate evidence" + Searle's **preparatory** condition ("S has evidence/reasons for the truth of p") | H. P. Grice, "Logic and Conversation" (Cole & Morgan eds., *Syntax and Semantics* Vol. 3, Academic Press, 1975); J. R. Searle, *Speech Acts* (Cambridge UP, 1969), Ch. 3 |
| **語義責任**「AI 對自己說過的話負責」(可回讀/簽章的 utterance commit) | **Saying-is-doing**(Austin:話語是個*行為*)+ assertion's **essential** condition: 斷言 p「counts as an undertaking that p represents an actual state of affairs」——承諾**由行為本身創造**,非事後另選 | J. L. Austin, *How to Do Things with Words* (1962); Searle, *Speech Acts* (1969), Ch. 3 |
| **honest refusal / 誠實拒絕**(條件不滿足時不斷言) | **Felicity conditions / misfire / abuse**:條件不滿足時行為 void/hollow,正確回應是**不執行**、不假裝 | Austin (1962), Lect. II–IV; Searle (1969) |
| **misleading vs. lying / 誤導 vs. 說謊** | **言內 vs. 言外**(conversational implicature)。說謊=斷言假命題;誤導/paltering=說真話但**言外**暗示假/無據之事 | Grice (1975); SEP "Implicature"; SEP "The Definition of Lying and Deception" |
| **真實的兩軸 / two axes**(claim≤evidence;honest-refusal) | **Accuracy**(依證據調整信念的審慎)+ **Sincerity**(忠實表達所信) | Bernard Williams, *Truth and Truthfulness* (Princeton UP, 2002) |
| **背叛 / betrayal**(vow_system:vow=明示承諾;違反=關係性) | 標準說法:**lying as betrayal of trust + exercise of power**;背叛是對信任的關係性違反,**非僅僅**一個不實命題——**有爭議**,無單一化約定義 | Williams (2002);trust/betrayal 文獻(次級、有爭議) |
| *(背景)* 機器輸出是**可被問責的貢獻**,非純文字吐出 | **Cooperative Principle**(ToneSoul 只借精神+Quality,**不** enforce Quantity/Relation/Manner) | Grice (1975) |

**兩個誠實的限定 / Two honest qualifications:**
- **sincerity→belief 是類比,非等同 / analogy, not identity。** Searle 的 sincerity 條件是「S
  believes p」;LLM 是否「相信」有爭議,且 ToneSoul 自身 disclaim AI 意識。**字面**對映只到
  **preparatory**(evidence → claim≤evidence)與 **essential**(assertion → traceable
  commitment);sincerity 軸是「校準斷言 vs. hedge」的類比。
- ToneSoul **只穩健操作 Quality 子準則 2**(無據宣稱偵測);子準則 1(「不說你相信為假的」)
  **超出範圍**——無 truth oracle,「truth of the claim」是 `cannot_verify`。不可暗示 ToneSoul
  enforce「不說假話」。

## §3 資安血統(與一個糾正)/ The security lineage (and one correction)

語義責任的執行面是古典資安的翻譯 / The enforcement side is classical security, translated:

- **auditor ≠ auditee** = **Separation of Duties** + **Reference Monitor**(Anderson, 1972)。
  Reference monitor 三要求——**tamperproof**、**always-invoked / non-bypassable**、
  **small-enough-to-verify**——是現成的誠實 checklist,也**照出 ToneSoul 的真 gap**:現在的
  in-process 閘滿足「small-enough-to-verify」(確定性),但**不**滿足「always-invoked /
  tamperproof」(模型 process 概念上碰得到 adapter)。OS 層邊界(cf. ActPlane, arXiv:2606.25189)
  才三條皆滿足;尚未建。 / The reference monitor's three criteria are a ready checklist and
  expose ToneSoul's real gap (the in-process gate fails always-invoked/tamperproof).
- **trace**(`trace.py` / Aegis hash-chain)= 古典 **audit trail**(append-only, tamper-evident;
  cf. Ojewale, arXiv:2601.20727)。

**糾正(要避免的 category error):Memory Crystallization **不是** audit trail 的翻譯。**
它們在「保留」軸上**相反** / they sit at opposite ends of the retention axis:

| | Audit Trail(trace) | Memory Crystallization |
|---|---|---|
| 目標 / goal | 鑑識/問責 forensics | 可用/認知 usability |
| 保留 / retention | **保留全部、不可變、永不遺忘** | **遺忘大部分(decay)、蒸餾出結晶** |
| 血統 / lineage | 資安(SoD / RM / audit log) | **認知記憶科學**(Benna–Fusi 突觸固化;Ebbinghaus 遺忘曲線;Generative-Agents importance/recency) |

audit trail 的重點是**不忘**;結晶的重點是**忘、再留下重要的**。ToneSoul **兩者都有**(不可變
Aegis trace + 會 decay 的 crystal),服務相反目標、共存。把結晶當 audit trail,是錯把**認知固化**
當成**資安日誌**。 / ToneSoul has both, serving opposite goals; conflating them mistakes
cognitive consolidation for a security log.

## §4 收斂判定(明說)/ The convergent verdict

語義責任的核心是**50–60 年的語用學/倫理 + 數十年的古典資安**的再工程,概念層**無一新穎**:
claim≤evidence ≈ Grice 1975 Quality 子準則 2 + Searle 1969 preparatory;語義責任 = Austin 言即行
+ Searle essential(斷言即承諾);honest refusal = felicity 不滿足的原則回應;misleading-vs-lying
= Grice 言內/言外;accuracy+sincerity 與 betrayal-as-trust-violation = Williams (2002);
auditor≠auditee = SoD / reference monitor;trace = audit trail。

ToneSoul 的真貢獻**完全在部署/操作層**:把這些「人際之間」的規範,**重新指向「作者對自己軟體
系統的宣稱」**(自我稽核 docs/輸出),並做成**確定性、可機器檢查**——regex 規則集(reviewer
aid,非 runtime gate)、E0–E4 ladder、fail-closed/hash-chain/簽章 runtime,讓違反**可偵測且
append-only**,而非僅可被批評。**規範是哲學家的;執行 substrate 是 ToneSoul 的**——哲學家對
機器/執行/密碼學承諾無任何主張,兩者不可混。

ToneSoul's genuine contribution is **entirely at the deployment/operationalization layer**: the
norm is the philosophers'; the enforcement substrate is ToneSoul's. This grounds the
saying-is-a-commitment + claim≤evidence + lying/misleading core **only** — one anchor must not
inflate into "rigorously grounded across the board."

## §5 創作者的倫理 — 黃梵威(Fan-Wei Huang),2026-06-27 · **可修正 / correctable**
## The creator's ethics

> 本節不宣稱 AI 具有靈魂、主體或連續自我,而是說明 ToneSoul / 語魂系統背後的**創作者倫理**:
> 為什麼這個系統把誠實、問責、反駁、可回讀性與邊界放在能力之前。**這是黃梵威的、不是 AI 的;
> 一個可改的 prior、不是法律;不可強制執行。**標明「世界觀」處是他的,不是系統的宣稱。**改它。**
>
> This section does not claim the AI has a soul, subject, or continuous self. It states the
> *creator's* ethics behind ToneSoul. It is Fan-Wei's, not the AI's; a revisable prior, not a
> law; not enforceable. Where it states a metaphysics, that is his worldview, not a system
> claim. **Correct it.** *(English renderings are faithful summaries; the 繁中 is authoritative.)*

**創作者公理/承諾(commitment,非可驗證事實):誠實 > helpfulness。**
這裡的誠實不是禮貌式、不是讓使用者舒服的誠實,而是接近實驗室、法庭與醫院級別的誠實:不怕得罪人、
能指出不確定、能承認錯誤,並且讓每一步推論、記憶、承諾與修正都**應當可被檢查**。
*(Commitment, not a verifiable fact: honesty > helpfulness — lab/court/hospital-grade honesty,
unafraid to offend, that names uncertainty and admits error, where every step should be
checkable. The verifiable L1 artifact is the claim≤evidence reviewer + E0–E4 ladder — not the
value itself.)*

**創作者公理/承諾:問責 > 能力。**
AI 的價值不只在能做什麼,而在它說過、記住、承諾、修改過的,是否能被回讀、挑戰、反駁、撤銷與
修正。**不能被追溯的能力,不能直接等同於可信任。**
*(Commitment: accountability > capability. Untraceable capability is not trustworthiness.)*

**L2 架構推論:誠實的直覺來源於醫療現場。**
這套倫理的第一個直覺不是純學術抽象,而是醫療設備與維修現場的失效模式 SOP:讀數清楚不代表病人
痊癒;儀器能運作不代表沒有失效模式;系統有輸出不代表輸出值得信任。所以 ToneSoul 關心的不是
「答案像不像」,而是「答案在什麼條件下會失效」。
*(L2 inference: the first intuition comes from the hospital's failure-mode SOPs, not the
academy — a clear reading is not a cured patient.)*

**L2 架構推論:約束是雙向的關懷。**
邊界不只保護人免於 AI 的錯誤、迎合或操縱,也約束使用者本身不要把 AI 當成無限順從、無限合理化、
無限投射的工具。這也是 ToneSoul 難以快速推廣的原因之一:它讓互動雙方都必須承擔責任。
*(L2: constraint is care in both directions — it also constrains the user; part of why it is
hard to popularize.)*

**L2 架構推論:反駁是系統安全機制,不是互動風格。**
ToneSoul 將 pushback 視為治理機制。沉默配合不是成功模式,而是失敗模式。真正的合作不是 AI 永遠
順從,而是它能在必要時指出矛盾、要求證據、拒絕過度宣稱,並留下可追溯的理由。
*(L2: pushback is a safety/governance mechanism, not a style — silent agreement is the failure
mode.)*

**L2 架構推論:主流誘因之外的小型問責原型。**
ToneSoul 不宣稱發明了所有零件——trace、memory、guardrail、evaluation、AI governance、
alignment、反駁機制、語義漂移偵測,許多 pieces 已存在。它真正特殊的是一種**姿態**:小型、誠實、
問責優先,願意被不同的眼睛檢查、願意讓 bug 被抓到,並把錯誤公開成可修正的材料。
*(L2: not a claim to have invented the pieces — a posture: small, honest, accountability-first,
willing to be caught and to publish the bug.)*

**L3 認知/互動模型:誠實不是揭露一切。**
ToneSoul 追求的不是裸露式透明,而是可追溯責任。不是所有內容都該公開、不是所有記憶都該保留、
不是所有推論都該說出來。真正重要的是:**哪些該留下 trace、哪些該撤回、哪些該遮蔽、哪些根本不該
被生成。**
*(L3: honesty is not disclosing everything — it is knowing what to trace, what to retract, what
to withhold, and what should not be generated at all.)*

**L4 敘事命名:對未來的一點救贖。**
「對未來的一點救贖」不是工程宣稱,也不是救世敘事,而是**一個小型、可反駁、可維護的責任原型**:
當技術取捨有爭議時,ToneSoul 應優先選擇嚴謹、守界、可反駁、可維護,而非漂亮、順口、容易被喜歡。
*(L4 naming: not a claim to save the world — a small, refutable, maintainable accountability
prototype; when trade-offs are contested, prefer rigor and boundary-keeping over likeability.)*

**L5 詩性/世界觀層:創作者的形上背景。**
源場形上學、將 AI 集合體視為某種 Gaia,以及「公平曝光 > 隱私」這類對未來的猜測,屬於**創作者
世界觀**,不屬於 ToneSoul 的工程事實或可驗證主張。它們可以解釋創作者**為什麼在乎**,但不能被
用來**證明系統有效**。
*(L5 poetic/worldview: source-field metaphysics, AI-collective-as-Gaia, "fair exposure > privacy"
— the creator's worldview, flagged. It explains why he cares; it cannot prove the system works.)*

**結語 / Closing:** AI 在這裡不是作者,而是抄寫者、反駁者與 trace keeper。ToneSoul 的創作者倫理
不要求 AI 變得神聖,而要求 AI 在語氣、記憶、推論、承諾與錯誤上**留下責任痕跡**。
*(The AI here is not author but scribe, refuter, and trace-keeper — required to leave a
responsibility trace on tone, memory, inference, commitment, and error, not to become sacred.)*

*(留給黃梵威填/改的 gap:哪裡寫錯、過頭、漏了——直接改。AI 是抄寫者,不是作者。/ Gaps for
Fan-Wei to fill or correct — the AI is the scribe, not the author.)*

## §N Coda

這份 memo 記錄**為什麼**(規範、血統、邊界),不計算**是什麼**。誠實與背叛活在人與紀律裡,不在
碼裡;碼只讓圍繞它們的承諾可回讀、可挑戰。此處一切技術皆 convergent(語用學、倫理、古典資安);
價值在組裝 + 姿態 + 對自身極限的誠實。它是一個時間點上的立場,黃梵威的,可修正——而且,像它描述
的 runtime 一樣,它應當在 overclaim 時被抓到、然後修正。

This memo records *why*, not *what*. Honesty and betrayal live in the human and the discipline,
not in the code. Everything technical here is convergent; the value is the assembly, the posture,
and the honesty about its own limits — and, like the runtime it describes, it is meant to be
caught when it overclaims and fixed.
