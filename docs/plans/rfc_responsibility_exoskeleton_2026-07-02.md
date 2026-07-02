# RFC — 責任的外骨骼(Responsibility Exoskeleton)

> Status: DRAFT for owner review · 2026-07-02
> 起源:梵威口述構想——「可視化的張量網路、結構化壓縮,轉換成外部記憶、摘要、
> 向量檢索、trace、metadata、反證鏈,模擬出可治理的語氣連續性。」
> 本 RFC 的工作:把構想拆成「已存在 / 該蓋 / 該按住」三堆,每堆給證據等級。
> 判準沿用血統教訓(docs/LINEAGE.md):G4 死於超出工程能力的形式化,
> G7 死於外殼先於核心。每代死掉的都是「假裝有的能力」。

## §0 定位

外骨骼的意思:責任不靠模型內在(那不可驗),靠**穿在外面的結構**。
這不是新方向——是本倉庫現行論點的一句話重述。所以本 RFC 的大半結論是
**reframe,不是 build**。

## §1 部件對照表(構想 → 現實)

| 構想部件 | 已存在於 | 缺口 |
|---|---|---|
| 外部記憶 | OpenClaw-Memory(FAISS+BM25+decay)、hippocampus | 無 |
| 摘要/結構化壓縮 | compaction、memory crystals、decay(λ=ln2/7) | 「壓縮演算法」新形式待證(§3) |
| 向量檢索 | OpenClaw hybrid RAG | 無 |
| trace | Isnād provenance chain、session traces、Agent trailers | step 級 TrustLevel 粒度(LINEAGE parked #4) |
| metadata | E0-E4 分級、identity card、freshness 契約 | 無 |
| **反證鏈** | **只存在於實踐**(codex 對審、紅隊、gate 咬人) | **無資料結構 — 本 RFC 唯一的新磚(§2)** |
| 可治理的語氣連續性 | vow system、register 紀律、de-escalation | 無(「連續性」靠 artifacts,非模型記憶,維持現狀) |
| 可視化 | dashboard、accountability panel、dream observability | 等新結構存在後再畫(G7 教訓:殼不先於核) |

## §2 新磚:反證鏈(CounterEvidence Chain)— 建議蓋

**問題**:claim 有分級(E0-E4)但沒有「誰試圖推翻它」的記錄。今天的反證
散落在 PR 討論、codex 回報、紅隊筆記——不可檢索、不可聚合、會蒸發。

**形狀(最小)**:一筆反證記錄 =

```json
{
  "claim": "被挑戰的宣稱(文字或 claim-id)",
  "challenger": "codex | red-team | human | gate | self",
  "method": "怎麼試圖推翻(執行取證/對抗審查/邊界測試)",
  "outcome": "refuted | survived | narrowed",
  "correction": "若被推翻,修正是什麼",
  "evidence_ref": "PR/commit/log 位置"
}
```

**掛哪**:`tools/accountability_panel/events.json` 已經是它的近親(held/caught_by/
correction)——反證鏈是它的泛化:不只記「我的失誤」,記**所有 claim 的存活史**。
建議:擴充 events schema 而非新建平行系統(G5 教訓:absorb,不重複)。

**紀律**:shadow-first——先記錄、不 gate;累積 ≥20 筆真實反證後再談消費端。
一個 claim「activated」(多次挑戰後存活)才升 E3+;被推翻的 claim 保留原文+
修正(不刪,這是帳本不是黑板)。

## §3 按住的部分(不是否決,是要求先付證據)

- **張量網路**:E5。節點+邊+權重=圖,倉庫已有圖。要配得上這名字,張量收縮
  必須真的在做壓縮的工作(可測:壓縮率 × 可逆性 × 檢索保真)。先在 OpenClaw
  的向量層做一個 20 行的收縮實驗,有數字再回來。
- **統一可視化**:G7 的順序錯誤就是殼先於核。反證鏈落地、有 20 筆真資料後,
  可視化它(accountability panel 已有現成的渲染管線可掛)。

## §4 給 owner 的決定點

1. 反證鏈:擴充 events.json schema(建議)vs 新建獨立結構?
2. 張量收縮實驗:要排嗎?(7/7 前不建議;本地 qwen 時代的好題目)
3. 本 RFC 若 ratify,反證鏈的第一批資料源:本 session 的三次被咬 + codex
   歷次 findings(都有 PR 佐證,可回填)。

## §N Coda

構想不龐大——它是這個倉庫的自畫像,加一塊真正缺的磚。龐大的版本(一次蓋完
+張量+可視化)在血統裡死過兩次;小的版本(一塊磚+shadow-first)是這裡
一直以來活下來的方式。
