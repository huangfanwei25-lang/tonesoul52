# Commit Attribution Check 反覆紅燈 — 原因、脈絡、解法

> 寫給未來踩到這顆地雷的人(或 AI)。owner 2026-07-02 要求把脈絡留下來:
> 「這個問題好像是我倉庫的老問題,可以的話留下解法和原因脈絡給未來參考。」

## 症狀

CI 的 **Commit Attribution Check**(`scripts/verify_incremental_commit_attribution.py`,
在 test.yml 是 blocking)紅燈,錯誤訊息:
`Missing Agent/Trace-Topic trailers in incremental commits.`

## 規則(檢查器實際執行的,不是傳說)

PR 裡**每一個 incremental commit** 的訊息結尾都必須有兩個 trailer:

```
Agent: <agent-id>            # 例:claude-fable-5[1m] / Codex / 人名
Trace-Topic: <topic-name>    # 這個 commit 屬於哪條工作線
```

**唯一豁免**:synthetic merge commit — 訊息以 `Merge ` 開頭**且**變更檔案為零
(`_is_synthetic_merge_commit`,`verify_incremental_commit_attribution.py:105`)。
沒有 docs-only 豁免、沒有空 commit 豁免、沒有「很小所以不用」豁免。

## 為什麼一直復發(三個根因)

1. **規則只活在檢查器裡**:CLAUDE.md / onboarding 過去沒寫這條,每個新 agent
   (或換了模型的同一個 agent)都要用一次紅燈來學。
2. **「小 commit」的直覺陷阱**:空的 retrigger commit、一行 typo 修正——直覺上
   「這麼小不用儀式」,但檢查器不看大小。2026-07-02 的 #235 就是這樣紅的:
   一個重觸發 Vercel 的空 commit 帶了 `Agent:` 卻漏了 `Trace-Topic:`(run #966)。
3. **merge commit 的歷史舊帳**:GitHub UI 產生的 merge commit 天生沒有 trailer,
   在 synthetic-merge 豁免加入之前也會咬人;healthcheck 側的 commit_attribution
   檢查亦曾對 #230 的 merge 報缺歸因(2026-07-02 外部稽核發現)。豁免只認
   「`Merge ` 開頭 + 零變更檔」,squash merge 或改寫過訊息的 merge 不在內。

## 解法(按情境)

- **還沒 push**:commit 訊息尾端補上兩行 trailer 即可。
- **已 push、紅在自己的 PR 分支、且壞的是 tip**:
  `git commit --amend`(補 trailer)→ `git push --force-with-lease`。
  自己的 feature 分支可以 force-with-lease;master 永遠不行。
- **壞的埋在分支中段**:`git rebase -i` 改那顆的訊息(僅限自己的分支),
  或接受重寫成本太高時——加一顆帶完整 trailer 的說明 commit **救不了**
  (檢查器逐顆驗),只能重寫。
- **每次都想不起來**:抄這個模板進 commit:

```
<type>(<scope>): <subject>

<body>

Agent: <你的 agent id>
Trace-Topic: <工作線名>
Co-Authored-By: <模型名> <noreply@anthropic.com>
```

## 這條規則為什麼值得留著(不是官僚)

這個倉庫的論點是「AI 對自己說過的話負責」——commit 是 AI 在這裡最主要的發言。
`Agent:` 回答「誰說的」,`Trace-Topic:` 回答「在哪條脈絡裡說的」。拿掉它們,
問責鏈在最底層斷掉。付出的代價是每個 commit 兩行;換到的是整條 git 歷史
可以按 agent、按工作線審計(`run_identity_card.py` 的「人 who」欄位就是直接
從這些 trailer 聚合的)。

## 歷史案例(供比對症狀)

| 日期 | 事件 | 根因 | 修法 |
|---|---|---|---|
| 2026-07-02 | #235 run #966 紅 | 空 retrigger commit 漏 `Trace-Topic:` | amend + force-with-lease;本文件落地 |
| 2026-07-02 | 外部稽核:#230 merge 缺歸因記錄 | merge commit 無 trailer(healthcheck 側) | synthetic-merge 豁免涵蓋 CI 側;healthcheck 側屬 stale-artifact 家族 |
