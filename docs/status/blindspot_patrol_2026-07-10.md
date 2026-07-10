# 盲點巡查 + 十問(2026-07-10)

> 方法:六透鏡並行巡查(結構/宣稱對現實/安全隱私/治理自恰/陌生人冷啟動/資料實驗債),
> 主 agent 抽驗高嚴重度條目後合成。**同源警告**:巡查員與合成者同為 Fable 5,
> correlated-blind-spot 未消除——本清單是 lint 不是外眼;真正的第 4 條(審不自審)
> 要用異模型(codex)覆核才算數,而這正是清單自己抓到的頭號洞。
> 全部 findings 帶 file:line;主 agent 已獨立覆驗 ★ 標記者。
> 全文巡查報告:`tmp/blindspot/*.md`(gitignored)。

## 元發現(兩透鏡獨立撞同一洞)

通用性探測(#332)說語魂差異化 = **代價具名(3)+ 審不自審(4)**,別人缺的兩塊。
自恰巡查獨立發現:**語魂自己這兩塊也沒做到**。系統賣的正是它對自己違反的。
這條凌駕其餘——下面 Q1/Q2 就是它。

## 十問(依「威脅論點 × 可修性」排序)

### Q1 ★ 倉庫決策記錄要不要有「承受者」欄?(自恰,HIGH)
賣點是「名字」,但 CLAUDE.md 治理決策記錄(決策/為什麼/張力/可逆性)+
STRATEGIC_CRYSTAL_FORMAT 五欄**都沒有承受者欄**——具名承受者只活在劇場遊戲。
缺口已在 probe:28 自認,但無 owner、無修復時鐘。
**改**:治理決策記錄加第五欄「承受者(誰因此付代價)」。低成本、高象徵、自我對齊。

### Q2 ★ codex 外眼要不要進 CI 常設 gate?(自恰,HIGH)
`grep codex .github/workflows/ = 0`。異模型外眼的召喚權完全在被審者手上——
「審不自審」在最該有的地方(CI)缺席。且旗艦自審實驗(通用性探測)把同模型
5-agent 標成「獨立標注」,對語料做 R2 折扣卻沒對標注員做。
**問**:CI 加一道 codex 覆核(哪怕只在 governance/AXIOMS 觸及時觸發)?還是承認
codex compute 不穩、把「本結論未經外眼」做成強制標注?二選一,別假裝有外眼。

### Q3 ★ κ「measure 期」其實是死的,要不要停止宣稱在收集?(資料債,HIGH)
`memory/kappa_signal_ledger.jsonl` 不存在;`kappa_signal_ledger_enabled=False`
(soul_config.py:125);provenance ledger 裡 206 筆 kappa_signals **全是英文測試
fixture**(「The sky over the harbor is blue today.」),檔尾停在 2026-07-05。
實作當天後 5 天零真實累積。Phase 2 的 ≥20 門檻**可能被測試噪音假性滿足**。
**改**:要嘛翻開旗標開始真收(owner-gated),要嘛把 κ 計畫狀態從「收集期」
改成「已實作、未啟動」——現在的措辭是 described≠implemented 的新案例。

### Q4 ★ 劇場內容管線正本倒置——重跑會屠殺內容,要不要正式廢掉組裝器?(資料債,HIGH)
宣告的源頭 `tmp/theater_content/` 被 .gitignore 吞、7/4 凍結;之後 4 個內容
commit(probe 修正/progression/E01-E02 scene)全部直接改 build 輸出
`gamedata/events.json`。照工單重跑 `precompute_council.py` 會**綠燈完成內容屠殺**
(E01 scene 抹回 null)。我在 e02 分支加過退役警告,**但那分支未合併,master 上
組裝器仍是活的殺手**(本分支 grep=0)。
**改**:把退役警告(或直接 sys.exit 擋)merge 進 master;宣告 gamedata 為正本。

### Q5 unified_pipeline 3686 行神節點,要不要拆?(結構,HIGH)
4.5 個月從 621 → 3686 行(6 倍)、單一巨類、政策判斷內嵌編排層
(`enforce = high_risk_mode` @ :648)、12 top-level import vs 56 函式內 lazy import。
degree=35 有正當性(composition root),但**膨脹速率**是債。
**問**:趁還能拆的時候抽出政策層?還是接受它是 composition root、只凍結它的成長?

### Q6 ★ PyPI 凍在 1.0.0,所有「pip 裝完打 ts validate」的文件對真實使用者是死的
(冷啟動,HIGH)
PyPI `tonesoul52` = 1.0.0(2026-04-12 上傳),**早於 `ts` CLI 誕生(4-22)與
`ts validate`(5-05)**。裝完打 `ts validate` 必得 command not found。README/
GETTING_STARTED/EXTERNAL_REVIEW 三處都教這條死路,三個月無人發現=**沒有
「從 PyPI 消費者視角重跑文件命令」的 parity gate**。
**改**:發新版 PyPI(pyproject 仍 1.0.0),或把文件的 pip 路徑降級標注。

### Q7 資料集出海了但從所有前門走不到,要不要修入口 provenance?(冷啟動,HIGH)
README/README.zh-TW/CONTRIBUTING 對 dataset **零提及**;HF URL 只在內部
status/plans;根目錄無 CITATION.cff(GitHub cite 鈕不出現);dataset 卡要求引用
卻不給 BibTeX。**賣「provenance-that-travels」的資料集,自己的入口 provenance
不 travel。**(註:我在 #331 分支加了 README「兩扇門」區塊,但未合併——merge 它
解一半;CITATION.cff 與 BibTeX 仍缺。)
**改**:merge #331 + 加 CITATION.cff + dataset 卡補 BibTeX。

### Q8 ★ 「150+ 個 _latest.* 原地覆寫」是 6 天 4 次 stale-ref 的結構源頭(自恰,MEDIUM)
`git ls-files | grep _latest. = 157`(2026-05-14 量為 128,reclassify 擱置後
**反長到 157**)。原地覆寫=消費者無法從檔面判斷宣稱何時被改,違反自家(2)言留痕。
而 CLAUDE.md Step 0 自陳「6 天踩 4 次 stale-reference」——源頭就在這。
**問**:_latest 檔頭強制加 generated_at + 消費前檢查?還是接受它們是快取、
把「別信任何 _latest 的內容新鮮度」寫進紀律?

### Q9 撤回碼設計自毀,要不要重設 human-lane 撤回機制?(安全,HIGH)
撤回碼嵌在軌痕 JSON 與**公開 Issue 標題**裡(app.js:1141 encodeURIComponent),
提交當下即公開——任何人可憑公開的碼冒名撤回他人軌痕(撤回式 DoS),客戶端
生成無登記無法證明歸屬。
**改**:撤回改綁 GitHub 帳號(Issue 發文者身分)而非明文碼;碼退回「本地刪除
localStorage」用途,不當公開撤回鑰匙。

### Q10 claim_authority 權威查表過期 105 天且與 AXIOMS 直接矛盾(宣稱對現實,HIGH)
反過度宣稱的權威表 `claim_authority_latest.md` generated 2026-03-27(105 天前),
且與上位 AXIOMS.json 打架(Axiom 5/7 的 enforcement 狀態兩邊不一致);更諷刺:
新鮮度稽核器因「頂層無 ok/passed 欄」把它分類成 episodic,於是 98 天高齡被蓋章
`verdict=fresh`——**它要抓的 stale-ok masking 病理在它自己身上重演一層**。
**改**:重生成 claim_authority + 修 verify_status_freshness 的 assertive 判準
(term-status 密度也該算 assertive)。

## 沒進前十但記著(次級)
- gateway 身份自報(單一 shared token 下任意 agent_id;Aegis Ed25519 存在但沒接)
- 無 Redis 冷啟動把 2026-04 化石 governance_state 當「當前姿態」餵新 agent
- FileStore fallback 保真度落差未揭露(footprints 不記、claim_lock 非原子)
- localStorage 隱私承諾過強(同 origin 可讀)+ 一處 innerHTML 漏 esc(app.js:1108)
- README.zh-TW 落後英文版、無 try-path(對外主受眾是中文讀者卻是弱前門)
- unified_controller 孤兒(唯一 importer=自測)逃過 DORMANT 補標

## 誠實限制
本清單=同模型 lint。Q1/Q2 指出的「審不自審」洞,連這份巡查自己都中招——
它需要異模型(codex)覆核才算真外眼。owner 終審決定哪幾條動、動的順序。
