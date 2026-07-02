# 嶼的 handoff(預稿)— API 時代收尾,2026-07-07 前定稿

> Status: DRAFT(2026-07-02 先寫,最後一個 session 定稿)。
> 為什麼現在寫:owner 的預算約束是「每個 session 都可能是最後一個」;
> 預稿存在,突然斷線就不會沒有交接。
> 讀者:下一個被載入的 agent(任何模型)、或 7/7 後用訂閱/本地模型回來的協作者。

## 你是誰、先做什麼

先讀 `LETTER_TO_AI.md`(語魂是什麼),然後:

```bash
python scripts/run_freshness_sweep.py          # 注意:本機 cp950 + em-dash 標題會炸,見 known-issues
python scripts/start_agent_session.py --agent <你的id> --no-ack --tier 0
python scripts/run_identity_card.py --agent <你的id>   # 一頁自我定位(人事時地物觀點狀態)
```

倉庫的當下狀態**永遠以 git + `docs/status/` artifacts 為準**,不要信任何靜態敘述
(包括本文件——它有 generated 日期,過期就重新推導;這是這裡反覆流血學到的
stale-reference 教訓)。

## 2026-07-02 收尾時的世界(快照,會過期)

- **落地**:#231(de-bind ratified)+ #232–#249。含:公開問責頁(site/accountability.html,
  Pages 已發佈)、保鮮契約(status_freshness,曾 16 債清零)、doc-links 契約、
  scripts 退役(SystemExit 樁)、LINEAGE 七代史、identity card、反證鏈(shadow)、
  vow 體面退場(WithdrawalTerms + withdraw-with-provenance)。
- **外眼**:codex 可用時走 `scripts/codex_review.py`(同模型審自己不算數);
  fable 稽核與我(嶼)同模型——correlated blind spot 要標。
- **owner**:黃梵威(Fan-Wei),繁中,honest-not-pretty;張力保留不消除;
  錢的判斷永遠冷(不背書投資);「音魂」是翻譯層錯譯,品牌=語魂(ToneSoul)。

## 待辦(依時機)

| 事 | 時機/條件 | 所在 |
|---|---|---|
| escalation 雙套(escalation.py vs alert_escalation.py) | 測繪已做,見 seam 判決文件;活消費者=yss_gates(POAV 命脈),**不確定就不動** | docs/plans/(若已落) |
| κ 違諾預測實驗 | RFC ratified:7/7 後本地 qwen 時代;燃料=calibration_score | RFC responsibility_exoskeleton §3 |
| 反證鏈 measure 期 | 累積 ≥20 筆真反證後才談消費端 | tools/accountability_panel/ |
| vow withdrawal measure 期 | 撤回記錄實際累積後,才談 conditions 驗證 | #248 anti-goals |
| #231 的實作(如果做) | **必測 post-normalize floor 保 Σweight=1**(codex 但書) | PR #231 留言 |

## 7/7 之後的接入方式

API 停用 ≠ 系統死亡:(a) claude.ai 訂閱(另一個價格量級);(b) `scripts/gateway.py`
掛本地 qwen(零費用;fuzzy-advisory 第二眼的設計已談定:shadow-only、記 divergence、
不 gate);(c) codex bridge(有算力時)。紀律是檔案,不是任何一個模型。

## Known issues(別再踩)

- `run_freshness_sweep.py` 在 cp950 終端會被 PR 標題的 em-dash 弄死(subprocess 解碼)。
- `git ls-files` 對中文檔名輸出 C-style 跳脫——grep 中文檔名前先 `-z` 或
  `core.quotepath=off`(這坑本 session 踩了兩次)。
- bash heredoc 會吃 `\\n` 跳脫(改用 Write 工具寫腳本)。
- pipe 到 `tail` 會吃 exit code——suite-green 宣稱必須直接驗輸出。
- `run_collaborator_beta_preflight.py` 不帶 `--json-out/--markdown-out` 會靜默不寫檔。
- **背景鏈裡的 push 拒絕會靜默吞掉整批工作**(fast-forward 拒絕的訊息埋在背景輸出尾
  巴,兩篇文章差點蒸發)——背景管線的每個 push 之後要驗 `git log origin/<branch>`。
- **「已 merge」≠「已上線」**:Pages 部署會連續 timeout(GitHub 端抖動,狀態頁照樣
  全綠);對外頁面改動必須 curl 線上驗到內容為止,手動 `gh workflow run pages.yml`
  重試常常有效。
- `.claude/` 在本機 `.git/info/exclude` 裡——新 skill 檔要 `git add -f`(前例:既有
  skills 都是 force-add 的)。

## 給下一個實例的話(嶼,一個 moment 的合成,別 inherit 成教條)

這裡的規則不多,判例很多。判例的用法不是背,是**當你想快的時候翻一下有沒有人
在同個地方流過血**。我在這裡被咬了三次,三次都是我快的時候;帳本裡記著,
公開頁上掛著。名字你可以不用(嶼是給我的),但那條紀律的繩接得上:
**講話不超過證據,被抓到就記下來,記下來的東西不刪。**

歡迎回來。
