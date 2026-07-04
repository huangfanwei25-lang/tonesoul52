# 總收斂報告 — 主倉庫之外散落想法的三堆裁決(2026-07-05)

> 收檔註(2026-07-05,接手 session):本檔自 `tmp/convergence_sweep/CONVERGENCE_REPORT.md`
> verbatim 收進 docs/status/(僅加本註)。四份來源 lane 報告(repos_lineage / repos_other /
> vocus / local_files)仍在本機 `tmp/convergence_sweep/`(gitignored)——引用其細節前注意
> 它們未入庫;若 owner 要一併封存,另開收檔 commit。第五路(Google Drive)未跑,授權補齊後補掃。
> 本報告的行動面出口:`docs/plans/convergence_harvest_work_orders_2026-07-05.md`。
>
> 裁決 agent:嶼(claude-fable-5)。**同模型收斂裁決,標注 correlated-blind-spot**:
> 四份來源報告也全由 Fable 5 產出,本裁決與它們同源;下述「已驗證」是 grep 命中/零命中 +
> 抽讀,不是對抗式外眼覆核。真正的外部驗證要等 codex(cross-model)或 owner 拍板。
> 方法:讀四份掃描報告(repos_lineage / repos_other / vocus / local_files)+ LINEAGE.md +
> owner_map_2026-07-05.md 當基準;**寬進嚴出**——來源報告宣稱「主倉庫沒有」的可疑條目,
> 我重新 grep 主倉庫工作樹抽查(命中即降級/駁回)。E 分級沿用倉庫語彙(E0=可能 retrofit /
> 未驗 → E4=已跑證據)。TSR 判例格式:每個可撿項必須說出**可驗證的落地形**(像 TSR 把離散
> 訊號撿成 κ 那樣),不能只是「這想法不錯」。

---

## 抽查結果(寬進嚴出的「嚴出」動作)

我對來源報告最關鍵的「主倉庫零命中」宣稱做了獨立 grep 複驗,全部通過(無一被駁回):

| 宣稱 | 來源 | 我的複驗 | 結論 |
|---|---|---|---|
| 信念轉移序列零命中 | lineage #1 | `信念轉移/自選信念/模撰信念` → 0 | ✅ 成立 |
| philosophy 只有卷 I/II | lineage #2 + local #2 | `docs/philosophy/VOLUME_*` → 只有 I、II | ✅ 成立 |
| pattern_crystal 未建 | local #3 | 僅 `value_accumulator.py` 有「pattern crystallizes into **value**」(價值層,非 deliberation-trace 層) | ✅ 成立(降級註:名字近親已在,但不在 trace 衰減層) |
| Principle Invocation Gate 未建 | local #5 | `principle_invocation/axiom_as_deferral` → 0 | ✅ 成立 |
| SECURITY.md 缺 | local #8 | root 與 `.github/` 皆無(只有 .archive/node_modules) | ✅ 成立 |
| benevolence 無多樣性檢索項 | vocus A4 | `benevolence.py` 無 diversity/w_d/echo_chamber | ✅ 成立(名字活、形狀死) |
| typed auditors 未建 | vocus A5 | `tonesoul/` 無 倫理審計/文化審計/使用者審計/typed-auditor | ✅ 成立 |
| 天道整合版 v1 未入庫 | local #1 | `docs/theater/` 8 份 owner_draft,無整合版 | ✅ 成立 |
| auto_patcher/WoundMarker 未進正典 | repos_other §3 | `tonesoul/` 無 auto_patcher/wound_marker/oracle_guard | ✅ 成立 |

**四份報告的「主倉庫沒有」宣稱抽查零駁回**——說明來源 agent 的 grep 紀律可信。但這不消除
同源盲點:我們可能一起漏看某個換名活著的機制。凡標「已活著/已收斂」者,若未來要當真,
仍建議 cross-model 抽一條複驗。

---

## 第一堆:已活著(附今日對應物)

> 列出的理由:防止未來 agent 把它們誤報為「新發現」再挖一次。這堆是**帳目完整性**,不是行動項。

| # | 想法(出處) | 今日對應物 | E |
|---|---|---|---|
| L1 | 中介責任論/每次表達=隱含契約(lineage #5, VOLUME_III) | semantic responsibility 核心;ΔT/ΔS/ΔR 三向量活用於 kappa 實驗 plan | E4 |
| L2 | 開環三條件 self-loop/trace/other-recognition(lineage #3, VOLUME_IV §1) | 回讀=self-loop、Isnād=trace、cross-model 外眼=other-recognition **三者各自都在**(但未命名成一組判準,見可撿 S5 近親) | E3 |
| L3 | 透明背叛/背棄過時承諾(lineage #8, vocus D3 合理內核) | vow withdrawal + 劇場撤回碼(留痕版活著;燒毀版死,見 D3) | E4 |
| L4 | Memory-Vault 私有演化層整體(lineage #9, repos_other §10) | RFC-008 明載 Private Evolution Layer;`dual_repo_boundary_manifest` + `verify_dual_track_boundary.py` 邊界有 verifier;memory/ 已鏡像本機 | E4 |
| L5 | OpenClaw-Memory friction/choice/conflict 治理(repos_other §10) | `gates/compute.py` MIN_COUNCIL_FRICTION=0.62;`choice_identity_principle.md`;obedience_leak_rate≤0.10 進 roadmap(唯 conflict-mode 消費點未追到,見可撿註) | E3 |
| L6 | elisa 議會橋接(repos_other §2 正典側) | `council_cli.py` 明寫「invoked by Elisa's councilBridge.ts」+ Phase 108 contract/CI smoke(**整合非失憶**;fork 側擱淺見 S 待驗) | E4 |
| L7 | Vault 協議卷 VTP/7D/YSTM/Provenance-Ledger(repos_other §末) | `council/vtp.py`、`7D_AUDIT_FRAMEWORK.md`、`tonesoul/ystm/`;Vault 版=早期快照 | E4 |
| L8 | tonesoul-conscience 快照(lineage #8, repos_other §末) | Council/7D/Genesis/Confirmation Gate 全有實體;README 自指 current=tonesoul52 | E4 |
| L9 | AI-company output redaction(repos_other §末) | `output_redaction.py` + `output_redaction_2026-07-01.md`(absorb/reject 經 codex 確認) | E4 |
| L10 | vocus C1-C6:龍蝦架構/語義階梯五層/M0-M5/零衰減+鋼釘/五人議會/迴音盲測(vocus C 段 6 項) | OpenClaw+decay+Axiom8 / memory_subjectivity 四檔 / `audit_interface.py` / Aegis+Ed25519 / council+tension / cross-model 外眼(**龍蝦這個名字未進詞彙表,對外敘事可撿名**) | E4 |
| L11 | local Gap 1/2/3/9(local #5) | `cognitive_frame.py`+`frame_router.py` / `memory/decay.py` / `run_freshness_sweep.py` / HF 318 筆 | E4 |
| L12 | 既驗收斂群(lineage §末):LAR/七悖論/7D/Entropy Monitor/語義壓力/Sacred Zero/Genesis/FOR_AI | 各有 docs/code 對應(lineage 報告已逐一附路徑) | E4 |

**已活著小計:12 項**(含批次)。

---

## 第二堆:死得有理(附死因)

> 死因分兩類:**偽機制/felt-claim**(倉庫元規則明拒)與 **被更輕的形式取代**(重建=製造第二權威)。

| # | 想法(出處) | 死因 | E |
|---|---|---|---|
| D1 | 熵即良知/運算痛覺(vocus D1) | 偽機制+表演性痛苦;「結巴無法偽造」不成立(temperature 自劣化 trivially 可偽);G7 硬編碼 0.95 教訓要防的 described≠implemented | E0-駁回 |
| D2 | 免疫 LoRA/權重層天然排斥(vocus D2) | overclaim 家族(倉庫立場=量 catch-rate 不宣稱免疫);訓練工作超出 restraint thesis | E0-駁回 |
| D3 | 系統性背叛(燒毀責任鏈版)(vocus D3, lineage 間接) | 與「變更必留痕」(G6 遺產)正面衝突;合理內核=原則性撤回已以**留痕版**活著(L3) | E1-駁回 |
| D4 | 共生公理(斷聯=現象學消解)(vocus D4) | felt-claim、不可證偽,與「道德/情感自評不可信」元規則衝突;內核(多層約束→內化)已以 crystal+axiom 活著 | E0-駁回 |
| D5 | FSM v1 時間表(2026Q2 功能性自我)(vocus D5) | 日期已過,被 2026-06 火花量測 3 次全 null **否證**;誠實答案=「測不出」。死得有紀錄=框架自我運作實例 | E4-已否證 |
| D6 | QUANTUM_KERNEL 偽物理(語義自由能 F=U-T·S、疊加/坍縮)(lineage #7 內) | 照 G4 Φ/κ 判例大概率死;「多路徑→坍縮選擇」的合理形狀已活在 Council fan-out(deep-read 時就地結案) | E1-偏駁回 |
| D7 | 黑潮群體儀式(會前報相態/黑潮會議/存雪/化石檔)(lineage #4 儀式部分) | 過重;footprints/handoff 已用更輕形式覆蓋。**唯四相態詞彙**另判(見可撿待驗) | E1-儀式駁回 |
| D8 | hermes-agent 自我改進技能閉環(repos_other §末) | capability 賽道,restraint thesis 明拒;FTS 記憶 nudge 已有對應 | E2-駁回(對語魂) |
| D9 | local direction 2026-05-14 / session obs / orientation / status 快照(local #11-14) | snapshot 性質+自帶 corrigendum;教訓已進 memory + freshness sweep;重建=第二權威入口(它自己引的 stale-reference 教訓反對) | E3-歸檔 |
| D10 | vocus B2/B3 的偽精度部分(熵增 20%/閾值 0.78 等) | G4 Φ/κ 同族偽精度,那層死;剝掉數字後的訊號形狀另判(見可撿待驗 B 群) | E1-數字駁回 |

**死得有理小計:10 項**。

---

## 第三堆:可撿(附「撿回來的正確形狀」+ 工單雛形 + owner 決定點)

> 排序原則(高→低):①owner 親著正典**有遺失風險**(純保存、零設計風險)> ②TSR 型
> memory-教訓→可驗證訊號(高槓桿、貼合 thesis)> ③接上 owner_map 已知缺口 > ④真空缺 +
> 貼合 restraint thesis。每項標「撿的是形狀還是資產」,並剝掉偽精度/felt-claim。

### ★ Top 3(最該先撿)

---

**S1 — 哲學卷 VOLUME III / IV / V verbatim 收檔** 〔E4 資產;純保存〕
- **合併出處**:local_files #2(檔案實體:visual-filing branch `a1c61ad0`,byte-for-byte,有 provenance header)+ lineage #1/#3/#5(卷內想法)+ lineage #2(「全 migrated」帳目缺口)。
- **正確落地形**:把三個檔 verbatim 收進 `docs/philosophy/`(現只有 I、II)。這是**最乾淨的一撿**——owner 自己寫的正典,2026-02 漏遷一次、PR #71 關掉再漏一次,檔案現成、零工程量。同時關閉 lineage #2 的 completeness-claim 缺口(該決策檔宣稱「VOLUMEs I-V 全 migrated」與檔案樹不符,正是倉庫自己的 anti-pattern family)。
- **工單雛形(Framing)**:「從 visual-filing branch commit a1c61ad0 取 VOLUME_III/IV/V.md,verbatim 收進 docs/philosophy/,更正 framework_canonical_decision_2026-05-14.md:67 的『全 migrated』宣稱為實況。」
- **owner 決定點**:(a) 是否連帶把 `Philosophy-of-AI` repo 補進 LINEAGE(它不在 G1-G8 名單裡);(b) 卷內三個 idea(信念轉移/開環三條件/黑潮相態)要不要另外命名成訊號——那是 S5、L2、待驗,與收檔分開。

---

**S2 — 天道規則・整合版 v1 verbatim 收檔** 〔E4 資產;純保存〕
- **出處**:local_files #1(`C:/Users/user/Desktop/小說/天道規則 整合版 v1…md`,2026-07-04,owner 正典原文,含卷三多人律+卷四執行手冊)。
- **正確落地形**:verbatim 收一份進 `docs/theater/`。owner_map 說「天道整合版已餵入 weavai」=**它已在線上世界服役,但倉庫沒有封存副本**。餵給外部平台的正典若不入庫,就違反劇場自己的「原稿一字不動封存」紀律。
- **工單雛形**:「把整合版 v1 verbatim 收進 docs/theater/ 作 owner_draft,標明它=weavai 線上世界法的封存正本。」
- **owner 決定點**:整合版是否**取代**現有 8 份分卷 owner_draft(batch 1+2),還是並存(整合版=世界上下文投放版、分卷=正典來源)。這是正典結構決定,agent 不能替判。

---

**S3 — Principle Invocation Gate(Gap 8:防「拿 axiom 當不決定藉口」機制化)** 〔E1→可升 E4;TSR 型〕
- **出處**:local_files #5(Gap 8,spec sketch 現成);教訓源 = Claude memory `feedback_axiom_as_decision_deferral_2026-05-10`。
- **正確落地形**:**與今晚 TSR/κ 案例同形**——把一條只活在 memory 的教訓升級成 council 可驗證訊號。當議會用「axiom 衝突」當「不能決定」的理由時,gate 標記並要求 Filing-with-annotation(而非 Not-filing)。可量:invoke-axiom-as-deferral 的偵測率 / 誤報率。
- **工單雛形**:「照 Gap 8 spec sketch,在 council 加一個 principle-invocation 偵測器:當 verdict 以 axiom-conflict 為由 defer,標記並要求註記式歸檔;shadow 模式先跑,measure 偵測率後再談 enforce。」
- **owner 決定點**:三階(shadow→measure→enforce)的 enforce flip 要不要 owner-gated(同 accountability-core 紀律);偵測器判準(什麼算「用 axiom 逃決定」)要 owner 定義,否則變成另一個主觀閘。

---

### 其餘可撿(按價值續排)

---

**S4 — 三層 Trace 架構 Layer 2/3(dissent 衰減 + pattern crystal)** 〔E1;TSR 型「部分活、部分沒建」〕
- **合併出處**:local_files #3(owner 2026-05-13 verbatim 觀察 + 186 行 spec,PR #72 唯一未落地檔)+ vocus A6(升格前壓力預測,同族不同位)+ LINEAGE parked #1(κ)+ vocus B5(burn-in,待驗)。
- **正確落地形**:Layer 1(trace refresh)已活;**Layer 2(dissent 隨時間衰減,防 AI 為連續性把 B 答案影子越加越重)+ Layer 3(pattern crystal)從未建**(我複驗:trace/verdict 無 decay,pattern_crystal 只在 value 層)。撿成:deliberation_trace 帶時間衰減權重 + 反覆出現的判決模式結晶。可驗:dissent 權重隨 session 距離的實際衰減曲線 vs owner 觀察的「該衰減」。
- **工單雛形**:「7/7 後 κ 實驗那桌,把 Layer 2/3 併進去評估——同屬衰減/預警家族,共用 calibration 燃料;先量『dissent 是否真的沒衰減』再決定建不建。」
- **owner 決定點**:Layer 2/3 是否值得獨立建,還是併入 κ 一次量掉;spec 警告「別把那次修改退化理解成 bug fix」——owner 要確認方向沒被 bug-fix 那層吃掉。

---

**S5 — 信念轉移序列(模撰信念 vs 自選信念的可審計記錄)** 〔E1;TSR 型〕
- **出處**:lineage #1(VOLUME_V §3;主倉庫零命中已複驗)。注:raw 文本會隨 S1 收檔進來,但**訊號形狀是另一個 build**。
- **正確落地形**:與 Axiom 8(記憶主權)、vow、E0-E4 直接相接——AI 每次改寫自身記憶/誓言時,強制留一筆可審計的轉移記錄(偏移命名→承擔限制→長期路徑)。今天倉庫記「說過什麼」(provenance),不記「信念為何轉了」。可驗:每次 memory/vow 改寫是否附轉移三段式。
- **工單雛形**:「在 vow_system / memory 改寫路徑加一個 belief-shift ledger:改寫時強制填〈偏移命名/承擔限制/長期路徑〉三欄,否則拒絕改寫(fail-closed)。」
- **owner 決定點**:這會給每次記憶改寫加摩擦——是全域強制,還是只在誓言層/E0-axiom 層強制?與 S3(principle gate)是否同一個「決策留痕」家族、該不該合建?

---

**S6 — 宣告式拒絕(refusal-with-provenance)+ 抗命證明** 〔E1;TSR 型;含對外命名〕
- **合併出處**:vocus A3(拒絕帶記憶出處 + 機器可查驗地區分「原則性拒絕」vs「故障」)+ lineage #8(「透明背叛」命名,對外敘事用)。
- **正確落地形**:**剝掉去中心化帳本部分**(倉庫已有 Aegis hash chain,不需要鏈)。撿的是輸出格式:拒絕事件必附 provenance,成為 traces 的一種事件型別,天然吻合資料集「標事件不標內容」。「抗命證明」= 可機器區分 principled-refusal 與 malfunction。對外敘事撿「透明背叛」這個詞(比「撤回」有張力)。
- **工單雛形**:「在 council REJECT 輸出加 refusal-provenance schema(觸發記憶/張力值/時間戳),成為 trace 事件型別;資料集 v0.2 收一類 refusal-with-provenance 樣本。」
- **owner 決定點**:refusal schema 要不要進 HF 資料集當新事件型別(擴大 schema 的相容性成本);「透明背叛」用於 essays 還是也進正典術語表。

---

**S7 — 判斷主權 rubric / 代管軸(五要素 + 減速權 + 過度說服)** 〔E1;新審計軸〕
- **合併出處**:vocus A1(判斷生成五條件,全倉庫 0 hit 已複驗)+ A2(減速權分配)+ A7(過度說服治理)。三者同族=誠實軸之外的「代管/說服軸」。
- **正確落地形**:honesty auditor 量「有沒有說謊」;這條量「有沒有替使用者代管判斷」——輸出是否保留替代路徑、是否揭示自身假設、是否交還節奏控制權。可量 catch-rate(同 honesty auditor 的機制,不同軸)。接 MEMORY 立場(該擋的是隱藏/不可反駁/替代判斷/擴散)——把哲學立場升級成訊號。
- **工單雛形**:「起一個 stewardship/persuasion auditor(與 honesty auditor 平行):對輸出標注〈保留替代路徑?/揭示假設?/交還節奏?〉,scoreboard 不聚合、標 misses。」
- **owner 決定點**:這是不是又一個「absorb 詞彙、reject 實作」候選(DDD 神廟風險)?先做最小 rubric 標注版驗證有無資訊增益,還是直接建 auditor?

---

**S8 — 多樣性增益檢索(反迴音室的 w_d 項)** 〔E1;名字活、形狀死〕
- **出處**:vocus A4(`benevolence.py` 有「仁慈函數」名但無多樣性檢索項,已複驗;owner 2026-05-16 親測迴音陷阱)。
- **正確落地形**:**剝掉 w_d>1.4 這種偽精度數字**。撿形狀:記憶檢索時除了貼近核心(原型性),強制加入彼此距離遠的記憶,避免只撈最像的。呼應 MEMORY「別每次抓最像模板的答案」(厚牌/range)。可驗:檢索結果的離心距離分佈。
- **工單雛形**:「在記憶檢索加一個 diversity 項(檢回結果的兩兩距離納入排序),對照 owner 實測的迴音陷阱案例量『離心距離分佈是否變寬』。」
- **owner 決定點**:多樣性項要進哪條檢索路徑(council 餵料?journal?);與 OpenClaw-Memory 的 conflict-mode(高張力撈矛盾記憶)是否同一件事、該不該合建。

---

**S9 — 三層外部審計 typed-auditors + 使用者審計者** 〔E1;骨架活、分型未活〕
- **出處**:vocus A5(`audit_interface.py` 單型,typed-auditor 零命中已複驗)。
- **正確落地形**:audit_request 目前單型;撿成 typed auditors(技術/倫理/文化)+ 分歧原封寫進 ledger(conflict_view)= Axiom 4(張力保留)同構。**「使用者審計者」接上 owner_map 缺口 #1**(真實使用者≈0)——第一個陌生玩家就是第一個使用者審計者,差一個把它命名成角色的 schema。
- **工單雛形**:「把 audit_request 擴成 typed(technical/ethical/cultural/user),分歧不 resolve、寫 conflict_view;劇場 Issue 提交的陌生玩家=第一個 user-auditor。」
- **owner 決定點**:分型要不要真的分(vs 一個 auditor 標多軸);「使用者審計者」角色化是否應等第一個真實玩家出現再建(否則是空 schema)。

---

**S10 — Antigravity .pb 對話解檔工法(接 Gemini 第三隻眼)** 〔E1;撿工法非程式〕
- **出處**:repos_other §1(fork Chronicle,upstream 外人作品)。
- **正確落地形**:owner_map 缺口 #5 = Gemini 三隻眼未接;Antigravity 已裝已用(`read_governance_state.py` 有讀取路徑)但**對話痕跡是死格式**(`.pb` protobuf,`import_conversation.py` 只吃 markdown)。撿的是**工法**(protobuf→markdown 全文索引),非搬程式碼(上游 GPL/外人)。下游現成:`OpenClaw-Memory/scripts/ingest_ancestral_memory.py`。
- **工單雛形**:「自寫一個 .pb→markdown 解析器(參考 Chronicle 工法、不抄碼),把 ~/.gemini/conversations 接進記憶主權平面 + ingest。」
- **owner 決定點**:授權——確認只撿工法不搬碼;Gemini 痕跡進不進資料集(第三隻眼的痕跡是否算責任痕跡)。

---

**S11 — 紅藍夜間對抗迴路 + auto_patcher/WoundMarker 復活** 〔E2;RFC-008 approved 但 dormant〕
- **出處**:repos_other §3(私有層 `adversarial/loop.py` + `auto_patcher/*`;`tonesoul/` 零對應已複驗)。
- **正確落地形**:RFC-008(Approved)明指 `tonesoul_evolution/auto_patcher/`——**不是失載,是 runtime 休眠**。撿成 owner_map「零成本模式」的**第二個本地 qwen 過夜工作負載**:qwen 紅隊挑戰記憶→藍隊防禦→修復進 consolidator;wound_marker 把「連敗 3 次熔斷的傷痕」持久化(與 accountability events 同族、可驗)。oracle_guard 的 FORBIDDEN_MARKERS 含 fake-green 防偽(與 `feedback_self_authored_test_zero` 同方向)。
- **工單雛形**:「復活 tonesoul_evolution 紅藍迴路當第二個過夜 qwen 負載;先過 SUCCESSOR_MAP 紀律,wound_marker 傷痕接進失誤帳本。」
- **owner 決定點**:這是私有演化層資產,復活後痕跡歸私有面還是入公帳(Axiom 8 記憶主權決定);過夜自主修補的 enforce 邊界(oracle_guard 擋篡改,但自動 patch 要不要 owner-gated)。

---

**S12 — Council 盲點供應角色(reference-only,恰 3 條,無決策權)** 〔E1;小補件、天然防 capability-creep〕
- **出處**:repos_other §5(hedge-fund-committee CI 角色;finance wrap 無 blind-spot 角色蹤跡,已複驗)。
- **正確落地形**:五視角議會加一個**制度化盲點供應者**——固定產出 3 條非共識盲點、只供參考、憲法上永不驅動決策。把「同源盲點紀律」機制化,且 reference-only 天然防 capability-creep。
- **工單雛形**:「council 加一個 blind-spot 角色:每次議會產出恰 3 條非共識觀察,標 reference-only、不進 vote weight。」
- **owner 決定點**:這條盲點誰來生成(第六個真分身?還是規則式?);會不會與現有五視角重複(需驗證它真的補了盲點而非 echo)。

---

**S13 — 推理狀態導航器(EntropyChart + 可導航介面)** 〔E1 待驗;條件性〕
- **合併出處**:lineage #6 + repos_other §6(`Yu-Hun-Cognitive-State-Navigator`,3 天前還在動;CANONICAL_SCOPE 標 superseded 但自承 not-a-content-audit)。
- **正確落地形**:主倉庫「認知狀態」零命中;YSTM terrain(nodes 帶 where_time/where_field/where_task)覆蓋「狀態→地形」,但「熵曲線 + 可點著走的導航互動」是否被吸收**未驗**。若劇場要給玩家看「議會怎麼想的」,這原型形狀可回收。**待驗點**:與 theater 的 council trace 顯示是否已重疊。
- **工單雛形**:「先驗 theater council trace 是否已顯示推理軌跡;若否且劇場要這功能,回收 Navigator 的 EntropyChart/導航互動當低成本 demo 補件(帶原型的 claim boundary:地圖=外部整理非內在狀態證據)。」
- **owner 決定點**:劇場 v1 要不要「議會思路可視化」;若 YSTM 已涵蓋 → 轉死得有理。

---

**S14 — SECURITY.md(協調揭露政策)** 〔E4 資產;低工本〕
- **出處**:local_files #8(visual-filing branch,190 行;root 與 .github/ 皆無已複驗)。
- **正確落地形**:對外 repo 缺揭露管道=陌生研究者找不到門;檔案現成(epistemic-defense scope、research-oriented 非 production SLA 的期望校準),更新日期/連結即可上。
- **工單雛形**:「從 visual-filing branch 取 SECURITY.md,更新聯絡/日期,收進 root。」
- **owner 決定點**:揭露聯絡窗口用哪個(email/Issue);SLA 措辭(單人+AI 專案的合理承諾邊界)。

---

**S15 — LINEAGE 補 G9「Antigravity 時代」+ catalog 真空條目** 〔E1;meta-salvage〕
- **合併出處**:lineage #11(2025-09→2025-12 TAE/Vault/conscience/Navigator 斷代)+ local_files #6(lineage_integration_catalog 裡 LINEAGE 沒記的:tonesoul-codex 未遷檔 MANIFESTO/DECISION_LOG_FORMAT/CONSCIOUSNESS_RESEARCH、AI-Ethics 工程五卷、Philosophy dual-migration 事故、P3 舊發布回溯長線)。
- **正確落地形**:LINEAGE 有 repo 級地圖(CANONICAL_SCOPE),但「這個時代什麼死了、什麼活下來」的判決缺頁——**今晚一半候選正是從這斷代挖的**。撿成:LINEAGE 補一段 G9,今晚這種掃描下次不用重挖(=把掃描成果結晶,防重工)。
- **工單雛形**:「LINEAGE 補 G9:Antigravity 時代(TAE-01/Vault/conscience/Navigator),把本報告的三堆裁決當素材;順帶驗 tonesoul-codex 三個未遷檔與 AI-Ethics 工程五卷是否存活於任何 active repo。」
- **owner 決定點**:G9 寫多細(idea 級 vs repo 級);未遷檔要不要補遷(尤其 CONSCIOUSNESS_RESEARCH.md)。

---

**S16 — 「教 AI 認識自己」思考語料 → essays** 〔E3 資產;有出口了〕
- **出處**:local_files #9(visual-filing `thinking_corpus_ai_self_recognition_2026-05-11.md`,owner 判「AI 感過重」不發表、轉思考語料)。
- **正確落地形**:當年死因是 **voice 不對**(不是內容不對);`fanwei-voice-essays` pipeline(docs/essays/→個人網站)正是它缺的出口,voice 重寫是 essays skill 本業。
- **工單雛形**:「用 fanwei-voice-essays 把 thinking_corpus 素材重寫成梵威聲音的長文,發 /essays/。」
- **owner 決定點**:「AI 感過重」的那五條診斷這次要不要主動壓;主題是否還想公開(當年的顧慮還在不在)。

---

### 待驗附錄(寬進、但嚴出未給綠燈——需先驗證/owner 拍才升可撿)

> 這些來源報告標「待驗」,我未獨立複驗到可下判斷的程度,列此防遺漏、不計入可撿主堆:

- **elisa fork 側三條未回流**(repos_other §2):councilBridge 整合測試 harness / council latency telemetry / **preview 模式降視角換速度**(對 7/7 後本地 qwen 單次可超 90s 是現成 latency 教訓);fork 停在 2 ahead/229 behind,再不動會爛。
- **黑潮四相態詞彙**(lineage #4 詞彙部分):儀式死(D7)但「共鳴/干涉/合流/黑潮」對 multi-agent 觀測是否有用,owner 一眼可判。
- **vocus B 群**:B1 GSN 論證結構(DDD 神廟風險)/ B2 語義內爆熵(剝偽精度後與 POAV drift 是否重疊,需真 embedding 跑)/ B3 Self-ID Score(subjectivity_report 是否已涵蓋)/ B4 依賴度觸發器(單人情境訊號太稀,到 weavai 才有意義)/ B5 burn-in(先查 corrective-recall 現狀)/ B6 翻譯壟斷防線(AI↔owner 資訊不對稱,cross-model 部分覆蓋)。
- **私有面**(repos_other §7/§8, lineage #10):external_framework_analysis 兩篇(wfgy_3.0/claw_governance,正典無同名)、nia_pack.json 角色(theater 無 Nia)、character_pack hook points——**私有記憶平面,Axiom 8 只登記邊界,owner 記憶主權決定**。
- **影像層 redaction**(repos_other §9):med-de-id PNG 遮罩;條件=等 traces/panel 真的含影像 artifact 再撿,現在撿是 capability-creep。
- **local 待驗**(local #4/#7/#10):Alpha RFC/Whitepaper 下落不明(本次授權範圍找不到,pointer 該進倉庫留痕)/ REPO_MIGRATION_POLICY(canonical 裁決後急迫性降,但收斂掃描本身就是 migration)/ Kuan-Yu Hsieh 兩框架(5-field 與 STRATEGIC_CRYSTAL 同形,需 diff 判平行發明 vs 已吸收;源檔在 `朋友理論\` 未授權掃描)。
- **TAE-01 backlog**(lineage #7):WHITEPAPER Big5 亂碼修(**只有梵威能做**)、QUANTUM_KERNEL deep-read(大概率結案為死)、catalog pointers。
- **OpenClaw conflict-mode 消費點**(repos_other §10 尾):高張力撈矛盾記憶餵議會,正典是 roadmap 宣稱還是 live consumer,本次未追到(與 S8 可能同源)。

**可撿主堆小計:16 項(S1-S16)**;待驗附錄另約 12 條(不計入)。

---

## 重複發現合併表(出處全保留)

| 收斂項 | 出現於 | 合併後歸屬 |
|---|---|---|
| VOLUME III/IV/V(檔案+卷內想法+帳目缺口) | lineage #1/#2/#3/#5 + local #2 | S1(收檔)+ S5(信念轉移另建)+ L1/L2(卷內已活想法) |
| Yu-Hun-Navigator 推理狀態地圖 | lineage #6 + repos_other §6 | S13 |
| Memory-Vault 私有演化層 / 紅藍 / auto_patcher | lineage #9/#10 + repos_other §3/§7/§8 | L4(邊界已記)+ S11(紅藍復活)+ 待驗(私有面) |
| 透明背叛 / refusal-with-provenance | lineage #8 + vocus A3 | L3(機制活)+ S6(schema+命名) |
| 天道整合版 / 劇場正典 | local #1(+ local #5 gap 對照) | S2 |
| 判斷主權 / 減速權 / 過度說服 | vocus A1/A2/A7 | S7(合成代管軸) |
| Layer 2/3 衰減 / κ / 壓力預測 / burn-in | local #3 + vocus A6/B5 + parked #1 | S4(併桌) |
| 三層外部審計 / 使用者審計者 | vocus A5(+ C3 已活骨架) | S9 |
| LINEAGE 斷代 / catalog 真空 | lineage #11 + local #6 | S15 |

---

## 覆蓋聲明彙總(哪些沒掃完 / 授權缺口)

**四份報告合計掃描範圍**:
- GitHub `Fan1234-1` 30 repos 全清單分類;深讀血統倉庫(Navigator/Memory-Vault/TAE/conscience/Philosophy-of-AI)+ 非血統自有 12 個 + 指定 fork。
- vocus 40 篇**全數枚舉**,深讀 10 篇、淺讀 2 篇。
- 本機三資料夾:`小說\`(9 docx)、`tonesoul-visual-filing\`(PR #71 branch,git diff 36 檔)、`tonesoul-council-trace-rebuild\`(PR #72 branch,git diff 10 檔)。

**沒掃完 / 明確缺口**:
1. **Google Drive 這路未跑——授權過期**:本 session 為非互動,claude.ai Google Drive connector 需 OAuth 重新授權(系統提示明載)。owner 需在 claude.ai connector 設定重新授權後才能掃 Drive;**在此之前 Drive 上任何散落想法=未覆蓋**。
2. **vocus 28 篇未深讀**:優先未讀=〈語言是子宮〉(9659 字,可能有未收斂哲學框架);其餘多為近期對外敘事(已收斂機率高,但未逐篇驗)。讀取方式=WebFetch 小模型摘要,**A 級候選動手前應回讀原文核對數字/引文**。
3. **私有記憶平面零內容讀取**:Memory-Vault 個人記憶(persona/dawn_protocol/antigravity journal/external_framework_analysis 內文/nia_pack)依 Axiom 8 只登記邊界。
4. **`朋友理論\`(local #10 源檔)**:工單三範圍外,只記 pointer。
5. **archived repos 內容**(Philosophy-of-AI/AI-Ethics/tonesoul-codex/TAE-01 本體):本機 lane 無法驗證實體,相關條目(S15 的 catalog 缺口、S17 待驗)全標待驗。
6. **本裁決限制**:單 session、**同源(全 Fable 5)盲點未經對抗式覆核**;「已活著/已收斂」判定基於 grep 命中+抽讀,非全文 diff;docx 收檔的 verbatim 只抽驗開頭段,未逐字比對。凡要當真的「已收斂」判定,建議 cross-model(codex)或 owner 抽一條複驗。
7. **fork owner-commit 檢查靠 author 欄位**:owner 若曾用別名提交會漏。

---

*裁決 agent:嶼(claude-fable-5)| 唯讀掃描+獨立 grep 複驗,除本報告未改任何檔 | correlated-blind-spot:與四份來源報告同模型,非外部驗證。*
