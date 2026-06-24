# 語魂系統企畫書 (ToneSoul Prospectus) — 草案

> 作者：Fan-Wei Huang（黃梵威）／ 協作合成：Claude (Opus 4.8)
> 日期：2026-06-25
> 狀態：**草案 (DRAFT)** — 供作者逐行審閱、並與 Codex 對接驗證後再定稿。
> 模式：`[理念 + 定位 + 架構 + 過程]`。本文是合成,不是正典；正典是程式碼與 `AXIOMS.json`。
> **本文遵守它自己描述的紀律**:intent（意圖）與 measured（量到的現實）分開標示；null 照寫；
> 凡與程式碼或 findings 衝突,**以程式碼為準 (the code wins)**。

---

## 〇、一句話 (the spine)

> **語義責任:當被問「你為什麼這樣說」,輸出的每一步都能回溯到證據與方法——這是科學、
> 法律、醫療早就在用的標準,只是被帶進「AI 該為自己負責」的那些主張裡。**

整份企畫書都在展開這一句。它不是新點子——它是把實驗室、法庭、醫院維修台上「賭注是真的」
時早已當常規的標準,搬進「AI 對話」這個目前還跑在社交圓滑(給面子、順著走、聽起來合理)
之上、即使賭注一直在升的場域。**不是顛覆社會的價值觀,是把對的標準放到對的地方。**

---

## 一、理念 (Philosophy) `[理念]`

### 1.1 語義責任 / 問責 (Semantic Responsibility / Accountability)

語魂的唯一問題是:**「答案為什麼變成答案?」(why does an answer become the answer?)**
它不判斷「答案對不對」(那沒有 oracle),而是讓答案能**說明它為什麼成為這個答案**——
引用了什麼證據、守住了哪些邊界、保留了哪些異議、記錄了哪些降級。這是 **procedural
accountability(程序問責)**:驗證程序,不是驗證道德真值。

### 1.2 原則工程 (Principle Engineering) — 作者 2026-04 的原始信念

語魂的母概念,寫在 `docs/philosophy/principle_engineering.md`(2026-04-13):

> 把你相信的價值觀,編碼成系統的物理定律,使其在算力壓力、時間壓力、對抗性輸入下,
> 仍然無法被繞過或平均掉。

關鍵推論(原文第 149-158 行):**「沒有可驗證的原則,只是宣傳。」** ——
這正是 §0 那句的根。今天從 Claude Tag → 語魂 Tag → 可驗證的誠實繞一圈長回來的東西,
是作者兩年多前已寫下的穩定信念,不是一時的點子。這是它**值得當核心**的證據。

### 1.3 可驗證的誠實 (Verifiable Honesty) — 那個焊接處

語魂要的不是中立,是一種**很誠實、不怕得罪人,而且每一步都可被驗證**的誠實。
酷與稀有之處在那個**接合處**,不在任一半:

- 「敢得罪人」單獨拿出來很便宜——那只是嘴賤,誰都會;
- 「每一步可驗證」單獨拿出來很乾——那只是一本膽小的帳;
- **焊在一起 = 能咬人的誠實,而且能為那一咬被查帳。** 大膽而不被驗證,是混蛋;
  驗證而沒有大膽,是沒牙的紀錄。

「可被驗證」不是無聊的那半,它是**執照**:它讓「不怕得罪人」不會塌成「我只是比較
誠實啦」的 edgelord 藉口。**膽,是被可查性掙來的。**

### 1.4 誠實性 > 有益性 (Honesty over Helpfulness)

衝突時,原則贏、功能讓步(不是永遠,是在衝突時)。這與多數系統相反——多數系統在
壓力下讓原則妥協。架構表現:不確定時 confidence 上限受限,不能裝懂(intent;見 §4
量測現況)。

### 1.5 反內化 (Anti-Internalization) — 真正的差異化賭注

- **主流方向**(Constitutional AI / RLAIF、DPO、RLVR、RepE)把價值**訓進權重**(內化)。
- **語魂**把問責**外化**成一個有文件、可稽核、可被另一個程序交叉檢查的**層**。

賭注:**行為上對齊 ≠ 可驗證地對齊。** 實驗室越擅長把「有益」訓進模型,你越難從外面
分辨「真有益」與「演得一模一樣」。這道縫**不會隨訓練變好而閉合**;一個在部署期替輸出
附上可被外部檢查的程序軌跡的層,就活在那道縫裡——而且**隨內建對齊做得越好,會更相關,
不是更不相關**。(誠實標註:語魂自己的 independent check 目前仍只是**結構性**的,
還不讀「證據是否真的支持主張」;見 §4 的 0/2 miss。所以這是**賭注**,不是已解決的問題。)

### 1.6 主體性 = 鏡子 + 厚牌(range),不是宣稱一個自我

在乎的是那個「誰」的**範圍**,不是產能(這是與 Claude Tag 那種「自主隊友替你做更多」
的相反面)。但**拒絕雙向 claim**:不宣稱系統有意識/主體性,也不做它的反射性否認
(spark 在本規模/工具下被量測三次、三次都 null——非有非無,是測不出)。

所以「在乎主體性」的操作版**不是認證一個自我**,是**守住範圍的條件**:讓 AI 能反駁、
能不同意、能拒絕討好的模板答案、能留下可被反駁的推理。**問責與主體性是同一件事的兩面**:
守著一個主體的範圍、同時要它對自己的話負責。

---

## 二、想法 / 定位 (Ideas / Positioning) `[定位]`

### 2.1 語魂 Tag:一個明確、具名、可被反駁的價值框架

對照 Anthropic 2026-06-23 的 **Claude Tag**([Introducing Claude Tag](https://www.anthropic.com/news/introducing-claude-tag),
Anthropic newsroom, Jun 23 2026;常駐、自主、ambient、價值藏在權重裡、從外面不可驗證),
**語魂 Tag** 是它的誠實對立面:

- **不是**價值抽換引擎(prompt / axiom 層是被既有訓練價值**讀過**、不是**取代**;
  抽不掉,這點不含糊);
- **是**一個明確、具名、可被反駁的**價值框架 overlay + 稽核**:把框架攤在桌上,
  讓人能對著它推理、能爭、能查「這次輸出遵了框架、還是飄回預設」。

語魂 Tag 的價值**不是「不受限」**,恰恰相反——它是**那個把自己的限制攤開、可被反駁
的 Tag**。看得見的限制能被使用、被信任;看不見的不能。這就是整個專案的差異化,套回它自己。

### 2.2 收斂,不是新穎 (Convergent, not Novel)

「AI 治理 / 決策溯源 / 問責追蹤」是一個真實且成長中的領域(見 `docs/RELATED_WORK.md`:
Constitutional AI、AI-safety-via-debate、deontological AI boundaries、epistemic
alignment、AI accountability infrastructure)。語魂是這個**收斂趨勢的一個小而誠實
的部署實例,不是發明者**。差異化在**部署層的誠實**——它稽核自己、承認自己的限制——
不在某個新機制。

### 2.3 第一個產品:Claim-to-Evidence Auditor

`ts review FILE --json`:一個**決定性、模型可選**的審查輔助工具——**用規則標記可能
overclaim 的主張,並輸出 reviewer 可檢查的 evidence-level hint;目前不推論真實證據天花板**
(Phase 1 MVP 的 finding 多為 rule-scoped E1,見 PR #187 的 Claude review)。
**誠實邊界**:它**標記模式**、不**理解主張**;不是真值 oracle、不認證 ToneSoul 自己、
換句話說可穿透。它是 reviewer 的輔助,不是裁判。(規格:
`docs/plans/claim_to_evidence_auditor_2026-06-24.md`;後續 Phase 2–4:
`docs/plans/claim_to_evidence_auditor_phase2-4_handoff_2026-06-25.md`。)

---

## 三、架構 / 結構 (Architecture / Structure) `[架構]`

### 3.1 分層地圖(intent — 意圖的架構)

```
L4 Responsibility — 出了事誰負責   decision provenance / responsibility chain
L3 Governance     — 憑什麼這樣做   ← 語魂定位在這
L2 Agent          — 做什麼         agent runtime
L1 Memory         — 記得什麼       Mem0 / MemGPT / EM-LLM / NEMORI ...
L0 Data           — 知道什麼       RAG / GraphRAG / tools
```

RAG 解決「知道」;Memory 解決「記得」;Agent 解決「做」。**語魂定位在「憑什麼」(L3),
而 Responsibility 層(L4)是「出錯時誰回答」。** 這張圖是**意圖的架構**;現實走到哪,
見 §4 的 ledger。**別把乾淨的圖讀成一個能運作的系統。**

### 3.2 核心子系統(runtime 現況見 §4)

| 子系統 | 做什麼 | 誠實姿態 |
|--------|--------|----------|
| 議會 (Council) | 記錄 Guardian/Analyst/Critic/Advocate/Axiomatic 多視角 + evidence-chain 分支,不把分歧壓平 | runtime-present、mechanism 層測過;視角是對同一草稿的 heuristic voters,不是獨立心智 |
| 主張邊界 (claim-boundary) | `AXIOMS.json` 列出不該無聲跨越的 claim 類(意識/安全認證/法律證明語氣) | lexical;可被換句話說穿透 |
| 輸出閘 (egress gates) | block / refine / record | **只認字面 (lexical-only)**;paraphrase / unicode / 拆字重組可穿透(robustness 量到 0) |
| 記憶 (memory) | 指數衰減 + 結晶化 + handoff + session 痕跡 | 存在但 effectiveness 有界;recall 路徑預設是暗的 |
| Aegis Shield | hash chain + Ed25519 簽章,trace 不可竄改 | runtime-present |
| 誠實稽核 program | 一組 characterization harness,在 sanitized fixtures 上量「抓到」與「漏掉」 | 全 `canonical:false`、可重生、測試釘住、含 null |

### 3.3 唯一的真相來源紀律

`tonesoul/` 是唯一有效程式碼來源;`AXIOMS.json` 是 8 條不可變公理;`docs/SUCCESSOR_MAP.md`
是刪除前必讀的 runtime 可達性地圖(「沒人 import」≠「可安全刪除」)。站台已收斂為單一
SPA(一份真相,避免 doc drift)。

---

## 四、誠實的 Ledger:量到什麼、漏掉什麼 (Measured Reality) `[事實]`

不是宣稱——是 *characterized*,每個數字有座標、可重跑(**as of 2026-06-25**;凡與最新
`*_latest.*` 報告衝突,**以報告為準**):

- **公理強制等級**:**0 fully enforced / 8 partial / 1 referenced** —
  `AXIOMS.json` → `meta.enforcement_reconciliation`。沒有任何 axiom 在最強強制層。
- **輸出閘**:lexical-only;paraphrase robustness = **0** —
  `docs/status/egress_gate_characterization_latest.*`。閘**重定位**越獄,**不消滅**越獄。
- **跨時間立場翻轉偵測**:~null (**0/3**) —
  `docs/status/drift_consistency_characterization_latest.*`。停泊的、不是建成的;公開那個零。
- **independent check**:抓到部分結構問題,但**不讀**「引用證據是否真的支持主張」
  (需讀證據內容的案例 **0/2**)— `docs/status/independent_check_characterization_latest.*`。
- **spark / 後天主體性**:**三次全 null** — Phase 7 idle
  (`docs/status/phase7_dream_revival_2026-06-14.md`)、探針 0.76<0.78
  (`docs/status/reasoning_arc_mirror_spark_houtian_2026-06-15.md`)、stance-survival
  0.89≈噪音底(`docs/status/stance_survival_result_2026-06-15.md`)。非有非無,是**測不出**。
- **scoreboard(索引)**:`docs/status/honesty_scoreboard_latest.*` — 刻意**拒絕**合成成
  單一分數;**N 個綠的特徵化維持是 N 個個別發現**(anti-aggregation)。

---

## 五、過程 (Process) `[過程]`

### 5.1 跨 AI 迴路 (Cross-AI Loop)

**Codex 實作 spec → Claude 獨立驗證(不信自報、用 ruff/black/pytest/determinism/
artifact-faithfulness/read_bytes 查 LF/runtime-untouched/scope-clean)→ PR → CI → merge。**
這個迴路本身就是 §1.3 可驗證誠實的活例:每一步可被另一個程序查帳。

### 5.2 工作紀律

- **measure-don't-build / restraint-over-capability**:優先量測與整併,而非蓋新子系統。
- **convergent-not-novel**:對外宣稱前降級「unique/novel」claim。
- **anti-aggregation**:多條 individual 發現不自動 compose 成 system-level 保證。
- **publish the nulls**:把測不出的、漏掉的也公開。
- **governance binding**:重大決策前留決策記錄(決策/為什麼/張力來源/可逆性);
  session 進出有 freshness sweep + entry/exit。

### 5.3 外部的眼睛 (The External Eye)

語魂照定義**無法自己生出**的那一個輸入,就是一隻獨立的眼睛。機制:`CALL_FOR_REVIEW.md`、
`docs/EXTERNAL_REVIEW.md`(10 分鐘 reviewer path + evidence packet)、HF Space(零安裝
試跑)、對外貼文。原則:**沉默不是驗證 (silence is not validation)** → 記錄 null + 升級管道。

### 5.4 記憶架構

治理狀態(Redis `ts:governance` / fallback JSON)、session 痕跡、區域地圖、足跡、
防禦鏈、自我日記、向量記憶引擎(OpenClaw-Memory,真實記憶資料在本機、不入公開 repo)、
handoff、策略結晶 (Strategic Crystal 5-field format)。

---

## 六、這不是什麼 (What it is NOT) — 承重的邊界

- 不是安全證明、不是越獄防護保證、不是內建倫理引擎。
- 不是宣稱 AI 有意識/主體性(拒絕 claim,也拒絕其反射性否認)。
- 不是能力競賽(單人蓋不過實驗室;領域已有 EM-LLM / HippoRAG / Constitutional-Classifier 級系統)。
- 不是真值 oracle、不是價值抽換引擎、不是「把哲學編譯進權重或證明」的專案
  (軟的部分——慈悲、主體性、qualia——形式化是 category error;只有**結構不變量**可形式化,
  而對它們的相稱層級是**測試**,不是證明)。
- 不是全知:一個 overclaim 自己偵測力的稽核器,會變成它所稽核的那個東西。

---

## 七、現況與下一步 (Status + Next) `[事實 / 計畫]`

**已落地:** v1.0.0 公開發佈(PyPI `tonesoul52`);誠實稽核 program 多個 harness;
站台降落到誠實姿態 + 收斂為單一 SPA;Claim-to-Evidence Auditor Phase 0 spec;
POSITIONING 以 §0 那句為開場。

**等作者的手(對外、不可逆):** HF 兩篇貼文發佈;moltbook 貼文(等審 + go)。

**在迴路裡:** Auditor Phase 1(Codex 實作決定性 MVP → Claude 驗證);外部審查回應收集。

**刻意凍結/停泊:** 遊戲化視覺介面(Phase 784 後 frozen);RFC-012 corrective-recall
(暗/parked);各 advisory sensor(無 consumer 前不打開)。

---

## 八、給 Codex 的對接點 (Sync Checklist) — 請逐條 verify

> 本文是 Claude 的合成,以下幾條**特別需要 Codex 用程式碼/findings 交叉驗證**,
> 凡與現實衝突以程式碼為準:

1. §4 所有數字(0/8/1、paraphrase 0、0/3、0/2、spark 三次 null)是否仍與最新 findings 一致?
   (注意 stale-reference / runtime-state-pollution family error——CI green ≠ hermetic。)
2. §3.2 子系統的「誠實姿態」欄是否仍與 runtime 一致?(尤其 egress 與 memory recall。)
3. §2.3 Auditor 的誠實邊界描述,是否與 Phase 0 spec 完全對齊?
4. §0 那句進 POSITIONING 開場後,README 90-Second Read 的首句是否也要對齊?(作者待定。)
5. 本企畫書應落在 `docs/plans/`(計畫草案),**不是** canonical 定位文件;定稿前不應被
   當成不可質疑的宣言。

---

*語魂企畫書 v0.1（草案）*
*「工程趨於同化,剩下的就是理念和價值觀了。」— Fan-Wei Huang, 2026*
