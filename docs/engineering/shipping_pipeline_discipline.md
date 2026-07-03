# 出貨管線紀律 — 一個 session 被擋八次之後的企劃書

> 2026-07-03,owner 要求:「挺多工作被阻擋的,看看怎樣做比較好,把步驟拆散。」
> 本文=失敗分類學(全部真實發生)+ 修訂後的出貨協議。給任何在此倉庫出 PR 的
> agent(含 7/7 後的接班者)。

## 一、這個 session 真實發生的阻擋(分類學)

| # | 症狀 | 根因 | 案例 |
|---|---|---|---|
| 1 | commit 被 pre-commit hook 擋(black 漂移) | 驗證跑在 commit 時,不在 commit 前 | essays 產生器、gateway、api/_shared(master 帶進來的漂移也算你的) |
| 2 | push 被 fast-forward 拒絕,**工作靜默滯留本機** | remote 分支被 update-branch 推前;拒絕訊息埋在背景輸出尾巴 | 文章 003/004 差點蒸發 |
| 3 | PR 開失敗:「No commits between」 | hook 擋掉 commit 後,鏈的後段(push/PR)照跑 | essays 首篇、survival-fix |
| 4 | merge 衝突/檔案損毀(events.json 夾衝突標記) | **多條併鏈並行**,同檔案互相追尾 | 反證鏈 events + SKILL.md |
| 5 | 分支基底過期 → BEHIND → update-branch 連環 | worktree 從快取的 origin/master 切出,沒先 fetch | 多次 |
| 6 | heredoc 吃反斜線,`\n` 變真換行 | bash heredoc 的跳脫地雷 | gateway banner 補丁把字串寫斷 |
| 7 | pipe 吃 exit code,「綠」是假的 | `cmd \| tail` 回傳 tail 的 0 | pytest、linkcheck 各一次 |
| 8 | merged ≠ live | Pages 部署 timeout(GitHub 端),狀態頁照綠 | essays 上線延遲一小時 |

共同形狀:**一條長鏈把五個階段焊死,每階段的失敗都無法阻止下一階段,而且
輸出只在最後被讀一次。**

## 二、修訂後的出貨協議(五階段,每階段有硬驗證)

**原則:階段拆散;每階段結束驗「世界的實際狀態」,不驗「命令有沒有喊完」。**

1. **開分支**:`git fetch origin` **之後**才 `worktree add -b <branch> origin/master`。
   驗證:`git log --oneline -1` 的 SHA 等於剛 fetch 的 origin/master。
2. **改動+預檢**:寫檔一律用編輯工具(不用 heredoc 寫含跳脫的內容)。
   commit **之前**主動跑 `black --line-length 100` + `ruff` 於**所有** staged 檔
   (含 merge 帶進來的)。
3. **commit**:帶齊 trailers(`Agent:` + `Trace-Topic:`)。
   驗證:`git rev-parse HEAD` **變了**才算成立——hook 擋下時 HEAD 不動,
   後續一切停止。
4. **push + PR**:push 後驗 `git rev-parse origin/<branch>` == 本機 HEAD
   (fast-forward 拒絕在這裡現形,不會靜默)。PR 開完驗拿到編號。
5. **merge(全倉序列化)**:**同一時間只允許一條併鏈在跑。** 兩條 PR 動到同一
   檔案族(events.json、SKILL.md、site/)時,第二條必須等第一條 MERGED 且
   本地 rebase 過才進鏈。merge 後:(a) 驗 master 含該 commit;(b) 對外頁面
   改動必須 **curl 線上內容驗到字串**才算上線(merged ≠ live)。

## 三、并行的邊界

- **可以並行**:改動不相交的多個 worktree 的「階段 1-4」。
- **不可以並行**:任何兩條「階段 5」;任何兩個分支動同一檔案族的階段 2。
- 背景長任務(全套測試、部署盯艦)可以背景,但**它的輸出必須被讀**——
  結論性宣稱(綠/上線)只能引用讀到的輸出,不能引用「命令退出了」。

## 四、既有工具的接點

- 預檢=pre-commit hook 的前移執行(hook 是最後防線,不是第一防線)。
- 階段 5 的線上驗證,對 site/** 改動即 `curl` 帶 cache-buster。
- 本文各條的原始事故紀錄:PR #261-#264 的 commit messages 與
  `docs/status/yu_handoff_final.md` known-issues 節。

## 五、不做的

不建自動化 ship 腳本(現在)——協議先跑熟;若 7/7 後接班 agent 反覆踩同坑,
再把階段 1-4 固化成 `scripts/ship_preflight.py`(候選,非承諾)。
