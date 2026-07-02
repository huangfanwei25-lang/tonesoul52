# responsibility_runtime 核心紅隊 — 2026-06-29（含一個關於我自己的教訓）

目標：對 fail-closed 核心（`intent_validator`/`policy`/`enforcer`/`trace`）做**異模型**紅隊——這是
整個 repo **最老、一直沒清**的 caveat（核心只被 Opus 紅隊過 = correlated blind spot）。

## 誠實的三個結果

### 1. 異模型核心紅隊**沒做成**（codex 工具限制）
codex 反覆只審「git HEAD 的 diff」或在 `--stdin` 模式 degrade（exit 1）——3 次都無法被強迫去看我指定的
核心檔案。wrapper 依 fail-closed 紀律拒絕假裝。**結論：核心的異模型紅隊仍是 open caveat。** 不是「審過、乾淨」。

### 2. codex 抓到 #224 的一個真殘留 → 已修
我在 #224 把 `ShadowLedger.summary` 改成 cross-tab，**但漏了 `record()` 仍在每筆 entry 存舊的
`agrees` binary**，還透過 `would_deny_but_written_cases` 漏出去。codex 抓到、我覆驗屬實 → 移除 `agrees`，
reframe 才算完整。（又一次：跨模型外眼抓到我自己的殘留。）

### 3. 我自己的 Opus 核心分析**錯了**，被既有測試抓到
我（Opus）先前標了一個核心 finding：「`enforcer` 在 adapter 執行**前**就寫 trace=executed → real adapter
若 raise 會留 phantom executed」。我據此把順序改成 adapter-first。**結果 `test_trace_append_failure_prevents_adapter_call`
立刻 fail**——因為原本的 trace-first 是**刻意的 fail-closed 屬性：trace 寫不了就不准寫（不留 untraced write）**。
我的「修正」會把這個屬性換掉（允許 untraced write）。**我反轉了改動。**

## 真正的設計取捨（記錄下來，給未來 enforce）

`enforcer` 是 **trace-first = 不留 untraced write**（trace append 失敗 → adapter 不執行）。代價：若**寫入**
本身失敗，會留下一筆 `executed` trace（phantom）。目前是 fake adapter（不會 raise），故 latent。
**enforce-mode（real adapter）時**，正解是**兩段式 trace**（先 `authorized` 再 `executed`/`failed`）——
同時保住「無 untraced write」與「無 phantom executed」。**但這是核心改動，需要異模型眼睛覆驗，不在同模型
分析上貿然做**（本輪正是反例）。

## 元教訓（本 session 主題最尖銳的一次落點）

我的**同模型**核心分析產出一個**錯的** finding；我**沒有異模型 check**（codex 咬不住核心）；最後是**既有
測試**當外部之眼抓到我。所以：
- **核心 fail-closed 邏輯的同模型分析，不安全到可以直接動手**——這正是我反轉的理由。
- 核心**真的需要**異模型紅隊（最老 caveat 仍開著）；等 codex（或人）能穩定咬住核心 target。
- 既有測試這次扮演了我缺的那個外部之眼——這也是「約束本身要可反駁（會 fail 的測試）」meta 原則的回報。
