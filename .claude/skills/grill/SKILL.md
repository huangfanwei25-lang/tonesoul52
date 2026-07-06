---
name: grill
description: 動手前拷問器 — 在寫任何非瑣碎 code 之前,用 Council 五視角一次一個問題把設計盲點電出來,逼出完整決策樹再動手。語魂原生版(改自 mattpocock/skills 的 grill-me / grill-with-docs)。Use when about to implement a non-trivial feature, when a plan/design is still fuzzy, or when the owner says /grill、電我一輪、拷問這個設計、動手前先想清楚、grill me. NOT a substitute for owner taste/decisions (surface them, don't decide them).
---

# 動手前拷問器(grill)— 語魂原生

> 出處與時機:2026-07-06 我出了一個場景 bug——沒在寫 code 前把設計拷問清楚、沒動手驗就出貨。
> owner 指出 mattpocock/skills 的 grill-me / grill-with-docs 正是那個洞的解。本技能是它的語魂版:
> 不是一個籠統「資深工程師」問你,是**五視角輪流電**,每個宣稱掛證據,決策樹落痕,誠實標盲點。
> **核心紀律**:寫 code 之前,先讓決策樹每個分支都有答案(或明確「這格 owner 決定」)。

## 什麼時候觸發

- 要實作一個非瑣碎功能(碰共享狀態、有真實失敗面、改資料/存檔/判定)之前——**必跑**。
- 設計/計劃還模糊,細節沒逼出來。
- owner 說 /grill、電我一輪、拷問這個、動手前先想清楚。

**不觸發**:純機械小改(改字、換色、單行修)、已被 grill 過的設計、純 owner 品味決定(那是攤開交還,不是拷問)。

## 兩種模式(誠實:預設深拷問)

- **淺拷問(in-context)**:我在同一個 context 裡扮五視角自問自答。快,**但同 context = correlated
  blind spot**——這正是出場景 bug 那次的失效模式(自己審自己抓不到自己的盲點)。只用於低風險、
  純釐清語義。
- **深拷問(fan-out,預設)**:五個獨立 agent 各戴一個視角拷問(Workflow / Agent tool)。**要動手寫
  的 code 一律走這條**——因為拷問的全部意義,就是抓**作者自己**的盲點,而作者的 in-context 自審
  跟作者共享盲點。bug 已證明:「應該沒問題」不是驗證。

## 五視角拷問(每個一個角度,一次一個問題)

| 視角 | 拷問什麼 | 典型問題 |
|---|---|---|
| **Guardian** | 失敗模式 / 邊界 / 傷害 | 「這會怎麼壞?誰受傷?最壞情況?存檔/相容/空值/併發?」 |
| **Analyst** | 機制 / 證據 | 「這一步的前提是什麼?你怎麼知道?——標 E0(直覺)到 E4(驗過)」 |
| **Critic** | 最強反方 | 「這設計最蠢的一點是什麼?用力攻擊它,別客氣。」 |
| **Axiomatic** | 原則一致性 | 「這跟既有設計/公理/thesis 衝突嗎?會不會偷偷推翻某條既有紀律?」 |
| **Advocate** | 值不值得 | 「這到底解決什麼真問題?不做會怎樣?範圍是不是膨脹了?」 |

**一次一個問題**是關鍵——不是丟一串(會被略過),是逼出一個答案,再往下鑽那個答案的下一層。

## 硬規則

1. **claim ≤ evidence**:拷問中每個「應該/大概/沒問題」都要標 E0-E4;把**假設**跟**已知**分開。
   出 bug 那次就是把 E0(沒驗)當 E4(已驗)。
2. **restraint 守門**:至少一條分支必問「這是問責還是能力膨脹?」(thesis-defender 角度)。
3. **落痕**:拷問完的決策樹寫進 `docs/plans/`(grill 記錄 / 決策樹)——拷問完不能聊完就散
   (抄 grill-with-docs 的 ADR-inline)。
4. **不替 owner 決定**:碰品味/方向/canon(如一表 vs 二表、門檻值)→ 攤成清單交還 owner,
   標「這格 owner 決定」,不代拍。
5. **誠實收尾**:結束時必答「這輪(同模型)拷問**抓不到**什麼?——真人試玩 / codex 異模型 /
   owner 本人才抓得到的盲點是什麼」。correlated-blind-spot 一律標。
6. **收斂條件**:決策樹每個分支都有(答案 or「owner 決定」or「動手時驗」),才准動手寫 code。
   還有懸空分支 = 還沒問完 = 不准動手。

## 輸出

一份 grill 記錄(`docs/plans/grill_<topic>_<date>.md`):
- 決策樹:每個被電出的問題 + 解決(答案+證據級 / 或標 owner-decides / 或標 verify-on-build)。
- 剩給 owner 的決定(短清單,不代拍)。
- 誠實收尾:這輪抓不到的盲點在哪。
- 然後才是「可以動手了」的綠燈 + 動手時的 verify 清單(哪些分支標了「動手時驗」)。

## 誠實限制

- grill 抓的是**想得到但沒想清楚**的盲點;抓不到**想不到**的(那要真人試玩/異模型)。
- 五視角同模型時 correlated;codex 可用時,Critic 那格優先換異模型(codex-second-opinion)。
- grill 不保證 code 對——它保證「動手前該問的都問了」,把「應該沒問題」逼成「問過、標了證據級」。
