# 天道十二律 + v0.2 外眼審 — 仲裁記錄(2026-07-04)

> Reviewer: codex(codex-cli 0.134.0,effort=high,read-only)。原始 findings:
> `tmp/codex_review_tiandao_20260704.md`。仲裁者:claude-fable-5(主 agent)。
> 協議:`docs/engineering/review_adjudication_protocol.md`(五步)。
> **正典層(owner 原稿)的任何處置 = owner 終審;本檔只裁 finding 真偽與 build 層對策。**

## 派工過程(誠實記錄,含 2 次失敗)

| 次 | 作法 | 結果 |
|---|---|---|
| 1 | `codex_review.py --target` 三檔,焦點聲明文件審查 | **失敗**:codex 無視 targets,審了 working-tree diff(graph 檔) |
| 2 | 清乾淨 working tree + focus 加「NOT a git-diff review」 | **失敗**:改審 branch 對 origin/master 的 commit diff |
| 3 | 三檔複製到**無 git 的 scratch 目錄**,`--dir` 指過去 | **成功**:真的審了文件,4 findings |

判例:**codex exec 在 git repo 內對「審文件」的指令有壓倒性的審-diff 偏向,prompt 拉不回;
解法=把待審檔複製到無 git 目錄再 `--dir` 過去**。副作用:被引用的檔案不在包內會產生
「缺檔」假陽性(見 F1)——隔離時要嘛補齊引用檔,要嘛 focus 聲明勿以缺檔立案。
已回寫 `docs/engineering/model_dispatch_protocol.md` §0。

## 逐條仲裁

| # | codex finding | 判定 | 證據 | 處置 |
|---|---|---|---|---|
| F1 | (High) README 引用的支撐檔案全缺,索引不可執行 | **REFUTED** | 倉庫 docs/theater/ 六個被引檔全存在(本 session 逐檔讀過);缺檔=審查打包造成(只複製 3 檔進隔離目錄) | 進反證鏈(events.json #22);打包紀律入判例 |
| F2 | (Medium) v0.2 第三律解析欄位含 `target`,第八律內部保存清單漏 `target` | **CONFIRMED** | v0.2 line 58 有 target;lines 152-163 內部清單無 target(有 tone_drift/contradiction_level) | 正典=封存原稿,改不改由 **owner 終審**(可在合併版世界書標注);**build 層採超集**:trace schema 含 target,兩讀法相容 |
| F3 | (Medium) 「一字未改」與檔頭嶼的對照注記矛盾,provenance 未分離 | **REFUTED** | 五份 owner 原稿同一慣例:策展注記=blockquote 檔頭+具名,原稿在 `---` 之後;「一字未改」指分隔線以下 | 進反證鏈(#23);「更強分離語法」降為 style 選項給 owner |
| F4 | (Medium) 第二律「三項中的兩項」後列 8 項,兩弱標示可躲掉成功率/代價/後果 | **CONFIRMED(歧義)** | v0.2 lines 36-44:「以下三項中的兩項」後接 8 個列項,枚舉結構真歧義;codex 描述的漏洞在寬讀法下成立 | 正典釐清=**owner 終審**;**build 層採嚴格讀法**:成功可能/主要代價/失敗後果三項中 ≥2 必標(滿足兩種讀法),已寫入可玩版驗收 |

## 結論

天道核心(codex 原話):「coherent and strong as a design philosophy」——主要風險在
打包/schema 一致性/可操作化,不在思想層。2 CONFIRMED 都是 factual-class、都有
build 層無痛對策;0 條需要動 owner 原稿才能開工。**可玩版動工不被阻擋。**

給 owner 的兩個待決(不急,見上表 F2/F4「owner 終審」欄):
1. v0.2 第八律內部清單要不要補 `target`(建議:在合併版世界書標注,原稿不動)。
2. 第二律「三項中的兩項」指前三項還是全列表(建議:前三項嚴格讀法,v0.2 若出 v0.3 再釐清)。
