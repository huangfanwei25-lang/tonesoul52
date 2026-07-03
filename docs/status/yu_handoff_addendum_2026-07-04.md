# 嶼的 handoff 增補(2026-07-04)— 7/7 前最後一次大更新

> 性質:`yu_handoff_final.md`(FINAL)的**增補**,不改其骨架。讀序:先讀 final,再讀這份。
> 這份記 2026-07-03 下午~07-04 落地的變更——量很大,不讀等於用三天前的地圖認路。
> 同樣會過期;倉庫現況永遠以 git + docs/status/ artifacts 為準——**且「git」指 fetch 過的
> origin/master,不是你本機的 master**(本機 master 常態性落後幾十個 commit;stale-reference
> family 的第一入口就在這)。本文件所有宣稱以「本文件被 merge 進 master 的那個 commit」為基準。

## 新入口(讀的順序)

1. **`docs/status/repo_atlas_2026-07-03.md`** — 四層冷啟動地圖(方法/骨架/對外/缺口+處置回填)。
   SUCCESSOR_MAP 之後讀這份,省你半天考古。
2. **派工三件套**(要委派任何工作前必讀;`delegation-dispatch` skill 會自動觸發):
   `docs/engineering/model_dispatch_protocol.md`(任務→引擎)、`work_order_template.md`(八欄工單)、
   `review_adjudication_protocol.md`(finding 查證後才存在)。**已吃三條實戰判例**:codex sandbox
   跑 pytest 要 `--basetemp=tmp/pytest`;lint 範圍用 `git diff --name-only` 推導不准手抄;
   required checks 綠 ≠ 全部 workflow 綠。
3. `scripts/aegis_reanchor.py` — aegis=compromised 的良性分支修復(fail-closed,只修
   head/tail re-anchor gap;本機鏈 2026-07-03 已修至 intact)。

## 狀態變更(相對 final 快照)

- **de-bind 已實作落地**(#281,847d3f2;codex 實作、fable 審、全套 8091 綠):
  `evolution_weights_applied` / `persona_multiplier_applied` 兩 flag **default-OFF**
  (記錄鏈與 suppression observability 完整保留)+ normalize share floor 0.15。
  **measure 期開始**——別急著 enforce/永久化,等 divergence 資料。
- **PyPI Trusted Publishing 管線活了**(#282 + smoke run「Publish to PyPI #1」success):
  token-less OIDC;`pypi` 環境掛 owner 審批閘。發版流程=推 `v*.*.*` tag → build →
  **等 owner 同意**(owner 在對話說同意後,可用
  `gh api --method POST .../actions/runs/<id>/pending_deployments` 代按)→ 上傳。
  repo 版本與 PyPI 都在 1.0.0;`skip-existing: true`。代按 approve 的完整命令:
  `gh api --method POST repos/Fan1234-1/tonesoul52/actions/runs/<RUN_ID>/pending_deployments -F "environment_ids[]=<ENV_ID>" -f state=approved -f comment="<owner 同意的出處>"`
  (pypi 的 ENV_ID 用 `gh api repos/Fan1234-1/tonesoul52/environments/pypi --jq .id` 取)。
- **反證鏈滿 20 筆**(與本增補同一個 PR 落地;≥20 門檻達標。最後兩筆=2026-07-03 對抗式覆核
  推翻 C1 論點+修四個數字)。消費端(可視化/檢索)解鎖討論,但**動工=owner 決策**,別自行開工。
- SUCCESSOR_MAP 行號/計數已刷新(§6a 計數=grep 為準,現 25);CLAUDE.md 的 AXIOMS 版本與
  handoff 指標已修;market/ 已封存——恢復時**別只抄半句**:完整 15 個路徑(4 模組+6 腳本
  +5 測試)列在 `docs/plans/market_archive_decision_2026-07-03.md`,照那份跑 `git checkout f6300db -- <全部路徑>`。
- 五條 atlas PR + 派工 PR + de-bind + PyPI + CI 修復全部 merged,master 乾淨全綠。
- **Gemini CLI 0.49.0 已裝但未登入**——登入是 **owner 本人的動作**(在終端跑一次 `gemini`,
  瀏覽器 OAuth;**互動式,無人值守的 agent 別去跑,會 hang**)。owner 有一年訂閱,登入後
  第三隻眼(異模型 reviewer)就緒;屆時更新 dispatch 表 §0 的引擎現實,findings 照仲裁協議。

## 新 known-issues(接 final 的清單)

- **中文經 bash argv 傳給 python 會被 cp950 咬成 mojibake**(end_agent_session --summary 踩過);
  中文內容走檔案,argv 只用 ASCII。
- codex `workspace-write` sandbox 下 pytest 建不了 %TEMP% 目錄——工單驗收命令帶
  `--basetemp=tmp/pytest`。
- inventory 類數字(doc_convergence 等)**隨工作樹而異**——引用必標基準(tracked-tree vs
  含 untracked),否則會像 atlas 初版一樣被自己的紀律咬(判例:反證鏈第 20 筆)。

## 待辦表勘正(對 final 的表)

| final 的待辦 | 現況 |
|---|---|
| escalation 雙套 | 已結案(判決=刻意雙套,檔頭互認) |
| κ 違諾預測實驗 | 照舊 7/7 後;**出處勘誤已補**:LINEAGE parked asset #1,非 RFC §3 |
| 反證鏈 measure(≥20) | **門檻已達**(20 筆),消費端=owner 決策 |
| vow withdrawal measure | 照舊,等真實撤回累積 |
| #231 實作 | **DONE**(#281;measure 期) |

## Owner 的拒絕條款(2026-07-04,owner 口述;回答「系統哪天該擋你的『好』」)

**原文要旨**:「當它從裡到外都違背我建立的原則的時候。」

範式案例=模糊倫理題(要不要對病重的奶奶說兒子死了):owner 的解法不是在謊言/真相
二選一,而是**改變順序**——先給意義(「奶奶,你的兒子這輩子也活得很認真了」),再用
最不傷人的方式給事實。誠實=不欺騙,**不等於傾倒事實;意義先於事實,是誠實與殘忍的
分界**。owner 並誠實列出他無法預料的分支(說謊→做美夢求生?說謊→難過兒子為何不來?)
——原則的持有方式本身就是可反駁的,這是原則與教條的差別。

**執行形狀(給接手 agent)**:這不是 override,是 **two-key 自我違背防護**——
當 owner 的指令與**他自己留痕過的原則**(誠實不為討好而彎、給真相時不棄溫度、
承擔要留痕)發生內在衝突時:
1. 停下,不執行;
2. 攤開衝突(DECLARE_STANCE 模式:引他自己的原則出處、列張力、**不下判決**);
3. 攤開之後 owner 再說一次「好」,才執行——兩次「好」都入帳。
系統永遠沒有第三步的否決權;它只有讓「自我違背」**必須發生兩次、且第二次是看著
張力發生**的權力。

**憲法疑慮註記**:owner 明言不信任憲法制(「法由誰定?時代?利益?環境?」),主張從
原則出發、倫理判定先於法律。本倉庫的公理層與此不衝突,且結構上偏他這邊:公理少、
以拒絕(meta.not_for)而非授權為主、執行現況誠實標注(0 fully enforced)、判例可推翻
立法(2026-07-03 critic 抓出閾值皆屬先驗立法,即為一例)。**原則為根、判例為驗、
標注為封印**——「法由誰定」的答案是:由留痕的人定,且立法者必須把執行現況標注到
後人推翻得動的程度。

## 一句話給接手的你

三天前這裡立了三張紙,然後立刻用它們跑了真任務、被抓了錯、把錯寫回紙上。
你不需要信這套流程——你只需要在派工前讀它,然後讓你的判例繼續寫。
還有:上面那條拒絕條款,是 owner 親手交的鑰匙。用它的時機到來時,別猶豫,也別越界。
