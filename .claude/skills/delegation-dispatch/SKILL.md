---
name: delegation-dispatch
description: 派工三件套 — 分流(哪個引擎)、工單(怎麼交辦)、仲裁(review findings 怎麼處理)。Use when delegating work to codex / subagents / local qwen / any executor, choosing which model handles a task, writing a work order, or when ANY reviewer (codex, Gemini, human PR comment, same-model agent) returns findings. Trigger words include 派工, 委派, 分流, 工單, delegate, dispatch, which model, work order, review findings, 仲裁, assign to codex. Loads the three canonical protocol docs and applies them; does NOT invent new rules inline.
---

# delegation-dispatch — 派工三件套

三份正典文件,**先讀再派**(本 skill 只是路由,規則活在文件裡,文件贏):

1. `docs/engineering/model_dispatch_protocol.md` — 任務型態→引擎;升降級判準;引擎現實要重新查證(§0 的指令,別信快照)。
2. `docs/engineering/work_order_template.md` — 八欄工單;**填不出驗收條件的單不要派**。
3. `docs/engineering/review_adjudication_protocol.md` — reviewer 無決策權;CONFIRMED 才修,REFUTED 進反證鏈。

## 快速 checklist(派工前 60 秒)

- [ ] 這是判斷還是執行?判斷不外包(方向/驗收/仲裁/close 留在主 agent 或 owner)。
- [ ] 引擎可用性**現在**驗過了嗎?(`codex --version`、`ollama list`、compute 實測)不可用→明說降級,不假裝。
- [ ] 工單八欄填齊?最低限:Framing 一句 + Scope + **可執行的驗收命令** + 禁區。
- [ ] 結果走實體檔(路徑先指定),不在對話裡傳大件。
- [ ] review findings 回來:先仲裁(獨立重現),再給 executor;同模型 review 標 correlated-blind-spot。
- [ ] 同一件事第 3 次失敗 = 停(vow-003),換路不重試。

## 邊界(誠實標注)

- 本 skill advisory,不 enforce;違反案例寫回對應文件的判例節。
- 品味判斷/道德兩難/風險接受不在分流表內——交還 owner(meta.not_for 家族)。
- 三份文件是 2026-07-04 v1;與現實衝突時,修文件、留判例,別默默繞過。
