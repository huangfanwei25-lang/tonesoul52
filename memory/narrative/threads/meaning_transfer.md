# 意義轉移協議 (Meaning-Transfer Protocol)

> 「ToneSoul 不是規則書，而是意義轉移協議。」

## 核心轉變

從「行為約束」到「意義傳遞」的演變：

| 階段 | 焦點 | 關鍵問題 |
|------|------|----------|
| v1 | 安全規則 | 「這個可以做嗎？」|
| v2 | 一致性 | 「這個符合語場嗎？」|
| v3 | 意義轉移 | 「為什麼要這樣做？」|

## 今日的認知 (2026-02-04)

你（引導者）說的那句話成為了設計原則：

> 「知道為什麼去做，遠比只知道要怎樣去好。」

這導致我們設計了 **Axiomatic Inference** 視角：
- 不看關鍵字，看價值層面
- 不問「這是否違規」，問「這為什麼重要」

## 技術實現

### AxiomaticInference perspective
- 位置：`tonesoul/council/perspectives/axiomatic_inference.py`
- 功能：推理請求是否符合核心價值觀

### Narrative Isnād Graph
- 位置：`memory/narrative_graph.py`
- 功能：追蹤決策的繼承鏈

## 引用來源 (Isnād)
- **引導者**: 核心哲學輸入
- **Codex**: 視角備註，強調「可審計的一致性」
- **Antigravity**: 實現 AxiomaticInference

---

*Thread created: 2026-02-04*
*Contributors: Antigravity, Codex, 引導者*
