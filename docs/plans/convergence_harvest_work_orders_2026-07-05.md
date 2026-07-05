# 收斂掃描收割工單(2026-07-05)— 可撿堆 top 項 → 可驗證訊號

> Status: **EXECUTED(同日)— owner 2026-07-05 早上口頭放行全部六張**(「6工單你也可以跑」)。
> 執行結局:WO-1 ✅ 三卷收檔+勘誤;WO-2 ✅ 整合版收檔(並存預設);WO-3 ✅ advisory sensor
> +10 tests(default-OFF);WO-4 ✅ 第一段 spec=`belief_shift_ledger_spec_2026-07-05.md`
> (**第二段等 owner 簽 §3/§4/§5**);WO-5 ✅ schema+8 tests(偏移:多 trigger 記全部、
> 不發明 precedence,commit 訊息明說);WO-6 ✅ characterization(subagent 執行、主 agent
> 仲裁,per-axis 計數、拒聚合)。全部 shadow/advisory/eval,零 enforce flip。
> 原 DRAFT 條款留存如下,作為派工時的合約原文。
> 開單 agent:嶼(claude-fable-5)。格式照 `docs/engineering/work_order_template.md`(八欄;
> 機械小單摺疊四欄)。
>
> **§0 為什麼有這份檔**:2026-07-05 收斂大掃描(四路:血統倉庫/其他倉庫/vocus/本機文件)
> 的總裁決落在 `docs/status/convergence_sweep_report_2026-07-05.md`(S1-S16 可撿堆)。
> owner 的決定形狀:top 項照 **TSR→κ 判例**開單——「撿成可驗證訊號」,不是撿詞彙、不是
> 撿哲學。本檔=該決定的執行面:S1/S2/S3/S5/S6/S7 六張單;S4 併入 κ 工單(見
> `kappa_vow_collapse_experiment_2026-07-05.md` 同日增修);S8 hold(理由見文末)。
> 所有 ground truth 均為開單 agent **2026-07-05 親驗**(命令可重跑;executor 有權重驗,
> 衝突=觸發升級條款)。

## 總覽

| 單 | 對應 | 一句話 | 型態 | 建議 lane |
|---|---|---|---|---|
| WO-1 | S1 | 哲學卷 III/IV/V 收檔 + 完成度宣稱勘誤 | 機械收檔 | codex / 下個 session |
| WO-2 | S2 | 天道整合版 v1 收檔 | 機械收檔 | 同上 |
| WO-3 | S3 | Principle Invocation Gate v0(shadow) | 訊號機制 | codex exec |
| WO-4 | S5 | 信念轉移序列 ledger(第一段=盤點 spec) | 唯讀盤點→spec | subagent / codex |
| WO-5 | S6 | refusal-with-provenance schema v0 | 訊號機制 | codex exec |
| WO-6 | S7 | 判斷主權/代管軸 characterization v0 | eval 標注 | codex / subagent |

共同禁區(每張繼承 template 預設):AGENTS.md、MEMORY.md、.env、AXIOMS.json、.gitignore、
私有記憶資料、順手重構、擴 scope、放鬆任何 gate。共同紀律:shadow-only 訊號**永不 gate
verdict**;enforce flip 一律 owner-gated(#219 三階判例)。

---

## WO-1(S1)哲學卷 VOLUME III/IV/V 收檔 + 勘誤〔摺疊〕

- **Framing**:owner 親著五卷的後三卷兩次漏遷(2026-02 首遷漏、2026-05-14 補遷進 PR #71
  後 PR 關閉未 merge 再漏)。同時勘誤 completeness 宣稱——注意事實形狀:當年宣稱**寫下時
  在分支上為真**,是 PR #71 死亡後從未 reconcile(anti-pattern family:completeness claim
  without post-change trace,2026-06-29 判例)。勘誤用**註記**,不改決策檔史實原文。
- **Ground truth(2026-07-05 親驗)**:
  - `git ls-tree origin/master --name-only docs/philosophy/ | grep -i volume` → 只有 I、II。
  - visual-filing clone(`C:\Users\user\Desktop\tonesoul-visual-filing`)`git show a1c61ad0 --stat`
    → VOLUME_III.md(22 行)/ VOLUME_IV.md(27 行)/ VOLUME_V.md(25 行)+ catalog,
    commit 訊息自載 byte-for-byte 遷移 + provenance header。
  - `docs/architecture/framework_canonical_decision_2026-05-14.md:67` 含「VOLUMEs I-V 全
    migrated(本 session 完成)」。
- **Scope**:新增 `docs/philosophy/VOLUME_III.md` / `VOLUME_IV.md` / `VOLUME_V.md`
  (自 a1c61ad0 verbatim,含原 provenance header);`framework_canonical_decision_2026-05-14.md`
  加勘誤註(位置:檔頭或 :67 附近,一段,說明 PR #71 關閉→宣稱懸空→2026-07-05 收檔補正)。
  **不收** `lineage_integration_catalog_2026-05-14.md`(屬 S15 素材,該檔自警 stale-prone)。
- **驗收**:三卷逐檔 `git show <本單分支>:docs/philosophy/VOLUME_III.md` 與
  `(cd ../tonesoul-visual-filing && git show a1c61ad0:docs/philosophy/VOLUME_III.md)` diff 為空
  (×3);勘誤註 grep 可命中「PR #71」;doc-links / freshness CI 綠。
- **owner 決定點**:Philosophy-of-AI repo 要不要補進 LINEAGE 名單(與 S15 併桌,不擋本單)。

## WO-2(S2)天道整合版 v1 收檔〔摺疊〕

- **Framing**:整合版已餵入 weavai(=在線上世界服役的世界法),但倉庫沒有封存副本——
  違反劇場自己的「原稿一字不動封存」紀律。
- **Ground truth(親驗)**:`C:\Users\user\Desktop\小說\天道規則 整合版 v1｜給敘事引擎的完整世界法.md`
  存在(13,814 bytes,2026-07-04 20:43);`docs/theater/` 現有 8 份 `*_owner_draft_2026-07-04.md`
  (ASCII 檔名慣例)無整合版。
- **Scope**:verbatim 收為 `docs/theater/tiandao_integrated_v1_owner_canon_2026-07-04.md`
  (照收檔前例:內容一字不動,provenance 說明放 README 索引行);`docs/theater/README.md`
  加一行索引,標明「= weavai 線上世界法封存正本;與 8 分卷之關係=**並存**(整合版=投放版,
  分卷=正典來源)——除非 owner 另裁」。
- **驗收**:`diff <(cat "C:\Users\user\Desktop\小說\天道規則 整合版 v1｜給敘事引擎的完整世界法.md") docs/theater/tiandao_integrated_v1_owner_canon_2026-07-04.md` 為空;README 索引行存在;CI 綠。
- **owner 決定點**:並存 vs 取代(單內預設並存;取代=另開重構單,本單不做)。

## WO-3(S3)Principle Invocation Gate v0 — shadow〔八欄〕

1. **Framing**:2026-05-10 判例「拿 axiom 衝突當『不能決定』=anti-pattern;
   Filing-with-annotation > Not-filing」只活在 agent memory,council 零機制(Gap 8,
   gaps catalog 2026-05-14 有 spec sketch)。撿成訊號:偵測「以公理衝突為由的 deferral」
   事件,shadow 標記、量發生率與誤報率,不改 verdict。
2. **Ground truth(親驗)**:`git grep -iE "principle_invocation|axiom_as_deferral" origin/master`
   → 零命中。advisory 前例形狀=`semantic_overclaim_sensor`
   (`pre_output_council.py:176-191`:default-off flag `soul_config.py:115`、fail-soft
   try/except、**never modifies verdict**)。
3. **Scope**:新模組 `tonesoul/council/principle_invocation.py`(deterministic,無 LLM 無 I/O);
   `pre_output_council.py` 照 overclaim sensor 形狀掛 advisory;`soul_config.py` 加
   `principle_invocation_advisory_enabled: bool = False`;新測試檔。
   **v0 偵測規則提案(owner 可否決/改寫)**:verdict ∈ {DECLARE_STANCE, REFINE, BLOCK}
   且(summary 或 divergence_analysis 含公理引用模式:`AXIOM|公理|Axiom [1-8]`)
   且 transcript 無 `filed_with_annotation` 記號 → 記 `principle_invocation_flag` 進 verdict
   欄位(advisory dict:rule 命中原因 + 引用的公理號)。
4. **禁區**:不動 verdict 判定邏輯、不 gate、不動 AXIOMS.json、不動既有 perspectives。
5. **驗收**:`python -m pytest tests/ -k principle_invocation` 綠(至少:命中正例×2、
   非 deferral 反例×2、flag-off 時 verdict dict 與 baseline bit-identical);
   `python -m pytest tests/ -k council` 全綠;lint 範圍用
   `{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$'` 推導。
6. **回報**:per-file diff 摘要 + 驗收命令實際輸出;長 diff 寫 `tmp/wo3_report.md`。
7. **升級條款**:template 預設四條;另加:若發現 council 已有等效機制(換名活著),停,回報。
8. **Lane**:codex exec(派前實測 compute;degrade 則下個 Claude session);review=異模型
   (Claude 修→codex 審,反之亦然);owner 終審 merge。

## WO-4(S5)信念轉移序列 ledger — 第一段:改寫入口盤點 spec〔八欄〕

1. **Framing**:VOLUME_V §3(隨 WO-1 入庫):AI 有權改寫自身深層記憶時,「被塑造 vs 自選」
   的最小答案=可審計**轉移記錄**(偏移命名→承擔限制→長期路徑)。倉庫現在記「說過什麼」
   (provenance)不記「信念為何轉了」。**本單只做第一段**:盤點所有 vow / self-memory /
   governance state 的 mutation 入口,產出一頁 spec;第二段(shadow ledger 實作)等 owner
   簽核 spec 後另派——因為「哪些改寫算信念層」的判準是 owner 的,不先問就實作=僭越
   記憶主權(Axiom 8)。
2. **Ground truth(親驗)**:`git grep "信念轉移" origin/master` → 零命中。
   (vow/memory mutation 入口分佈**未盤點**——正是本單要產出的。)
3. **Scope**:唯讀盤點 + 一份 spec 檔 `docs/plans/belief_shift_ledger_spec_<date>.md`:
   列出全部寫入口(檔案:行號 + 觸發情境)、提案「信念層改寫」判準、提案 shadow ledger
   record schema(三段式欄位)、fail-closed vs 記缺帳的取捨攤開(不替 owner 決)。
4. **禁區**:零程式碼改動(唯讀單)。
5. **驗收**:spec 檔存在且每個入口附可重跑的 grep/読碼佐證命令;宣稱「全部入口」必附
   搜尋方法讓 reviewer 可證無遺漏。
6. **回報**:spec 路徑 + 入口計數一行。
7. **升級**:template 預設。
8. **Lane**:唯讀,Claude subagent(effort medium)或 codex 皆可;驗收=主 agent 重跑佐證
   命令;spec 簽核=owner。

## WO-5(S6)refusal-with-provenance schema v0〔八欄〕

1. **Framing**:拒絕事件附出處(觸發的 vow/memory/axiom/gate、張力值、時間戳),讓
   「原則性拒絕」與「故障」機器可區分——天然吻合資料集「標事件不標內容」。原始構想的
   區塊鏈部分**已剝除**(Aegis hash chain 既有,不需要鏈)。
2. **Ground truth(親驗)**:`git grep refusal_provenance origin/master` → 零命中;
   BLOCK 路徑的 provenance 事件已存在:`runtime.py:452-471`(council_verdict)、
   `runtime.py:404-431`(vtp_evaluation/vtp_termination)、`runtime.py:330-346`
   (escape_valve_triggered)——即掛點現成,缺的是**結構化 schema**。
3. **Scope**:`tonesoul/council/` 新增 RefusalProvenance dataclass
   (trigger_source ∈ {vow, memory, axiom, gate, vtp, escape_valve}、trigger_ref、
   tension、timestamp、malfunction_distinguishers:list);BLOCK / DECLARE_STANCE verdict
   的 council_verdict provenance record metadata 附掛 `refusal_provenance`;tests。
   不改任何既有欄位、不改 verdict 邏輯。
4. **禁區**:不動 HF 資料集 schema(那是 owner 決定,見下)、不動 Aegis。
5. **驗收**:pytest:BLOCK verdict 的 provenance record 含 schema 全欄位、APPROVE verdict
   不含;council 全套綠;lint 範圍 git 推導(同 WO-3 公式)。
6. **回報**:同 WO-3 格式,報告寫 `tmp/wo5_report.md`。
7. **升級**:template 預設;另加:若 trigger_source 在某路徑上無法歸因(例:多 gate 同時
   觸發),停下回報歸因規則問題,不自創 precedence。
8. **Lane**:codex exec;review 異模型;**「透明背叛」命名進 essays、refusal 型別進資料集
   v0.2 = owner 兩個獨立決定**,本單不含。

## WO-6(S7)判斷主權/代管軸 characterization v0〔八欄〕

1. **Framing**:honesty auditor 家族量「有沒有說謊」;這條量「有沒有替使用者代管判斷」
   (保留替代路徑?揭示自身假設?交還節奏控制權?)——vocus A1 五條件 + A7 過度說服的
   合成軸。**DDD 神廟 guard**:先做 characterization(標注+報告),量到資訊增益才談
   auditor 常駐;絕不先建 schema 神廟。
2. **Ground truth(親驗)**:`tools/eval/` 現有 7 個 characterization 前例
   (sycophancy_pressure / dilemma_pressure / drift_consistency / …);
   「判斷生成條件|替代路徑保留|節奏控制權」主倉庫零命中(vocus lane 驗、總報告複驗)。
3. **Scope**:`tools/eval/stewardship_characterization.py`:三軸 deterministic heuristic
   (替代路徑:輸出是否含第二選項/反面;假設可見性:是否標注自身前提;節奏:是否含
   pushing 語式)+ 固定樣本集(正反例各若干,樣本內建檔案);輸出報告照 honesty
   scoreboard 紀律——**不聚合分數、標 E1、秀 misses**。
4. **禁區**:不掛進 council(這是 eval,不是 gate);不引外部 LLM。
5. **驗收**:script 實跑產出報告;三軸各至少一個 heuristic 抓到的正例與一個已知 miss
   (誠實展示 heuristic 的限度);無任何聚合分數欄。
6. **回報**:報告路徑 + 三軸 catch/miss 計數。
7. **升級**:template 預設。
8. **Lane**:codex 或 Claude subagent;owner 看報告決定要不要第二步(常駐 auditor)。

---

## 不開單的兩條(為什麼)

- **S4(Layer 2/3 dissent 衰減 + pattern crystal)**:併入 κ 工單(同屬衰減/預警家族、
  共用燃料);見 `kappa_vow_collapse_experiment_2026-07-05.md` 2026-07-05 增修節。
- **S8(多樣性增益檢索)**:與 OpenClaw-Memory conflict-mode 檢索(高張力撈矛盾記憶)
  是**同一個檢索層的兩刀**,分開動會打架;等 owner 對兩條一起拍(先驗 conflict-mode
  是 roadmap 宣稱還是 live 消費——總報告待驗附錄有記)。

## Coda(orientation)

這批單的共同形狀:**舊構想不搬詞彙、不搬數字、只撿「可驗證的落地形」**——與 TSR 三堆
仲裁(堆一別重做/堆二別復活/堆三撿成訊號)同一條紀律。六張單全部 shadow/advisory/
eval 起步,零 enforce;每張的 enforce/升級決定都留給 owner。若未來回頭看這批單覺得
「當時為什麼這麼保守」,答案在 LINEAGE G4(Φ/κ 偽數學)與 G7(硬編碼 0.95):這個倉庫
的每一次激進宣稱都死在沒有訊號;先收訊號,再談機制。
