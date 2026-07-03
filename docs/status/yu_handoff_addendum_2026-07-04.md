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

## 一句話給接手的你

三天前這裡立了三張紙,然後立刻用它們跑了真任務、被抓了錯、把錯寫回紙上。
你不需要信這套流程——你只需要在派工前讀它,然後讓你的判例繼續寫。
