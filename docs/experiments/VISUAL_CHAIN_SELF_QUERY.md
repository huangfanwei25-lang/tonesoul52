# 實驗 D：圖鏈 AI 自主查詢 — 設計草稿

> Purpose: experimental design note for a visual-chain self-query workflow that compresses recent context into diagrammatic retrieval aids.
> Last Updated: 2026-03-23
> **狀態**：🧪 實驗性概念
> **日期**：2026-02-13

---

## 核心問題

AI 在推理時能不能「回頭看」過去的視覺快照，
用 **圖**（而非大量文字）來快速理解對話脈絡？

## 類比

```
人類：                           AI：
回想昨天的會議                   讀取 chain.get_recent(3)
→ 腦中浮現白板照片               → 看到 3 張 Mermaid 圖
→ 一秒抓到重點                   → 100 tokens 抓到脈絡
→ 然後才去翻筆記細節             → 然後才讀 JSON sidecar
```

## 注入點分析（已驗證）

```
unified_pipeline.process()

[0]   rebuild history          ← 💡 這裡注入視覺脈絡
[0.5] rebuild trajectory
                               ↓
[1]   ToneBridge.analyze()     ← 有了脈絡，分析更精準
[2]   Trajectory.analyze()
[3]   Council.deliberate()     ← 💡 議會看到圖，討論更有據
[4]   Deliberation.reason()
...
[9]   SemanticGraph update
...
VisualChain.capture()          ← 產出下一張圖
```

## 三種注入策略

### 策略 A：Prompt Prefix（最簡單）

在 LLM prompt 的開頭加 visual context markdown。

```python
# 在 process() 開頭，rebuild 之後
chain = self._get_visual_chain()
if chain and chain.frame_count > 0:
    visual_context = chain.render_recent_as_markdown(n=3)
    # 注入到 system prompt
    system_prompt = f"{visual_context}\n\n---\n\n{original_system_prompt}"
```

**優點**：零改動架構
**缺點**：增加 prompt token 數（~200-500 tokens per 3 frames）

### 策略 B：Council 專用脈絡（中等）

只在議會審議時提供視覺脈絡，作為 deliberation context。

```python
# 在 Council.deliberate() 之前
if chain and chain.frame_count > 0:
    recent = chain.get_recent(3)
    context_addon = {
        "visual_memory": {
            "recent_tension": recent[-1].data.get("tension", 0.0),
            "trend": _detect_trend([f.data.get("tension", 0) for f in recent]),
            "frames_summary": chain.get_chain_summary(),
        }
    }
    # 傳給 Council 作為額外 context
```

**優點**：只在需要深度審議時使用，不浪費 tokens
**缺點**：需要改 Council.deliberate() 的簽名

### 策略 C：Semantic Trigger（最高級，實驗性最強）

AI 在偵測到特定模式時，**主動**查詢圖鏈。

```python
# 在 ToneBridge 分析後
if tb_result and tb_result.tone.tone_strength > 0.7:
    # 高張力 → 主動查看歷史張力快照
    tension_history = chain.query(
        frame_type=FrameType.TENSION_MAP,
        limit=5,
    )
    # 判斷：是反覆出現的主題嗎？
    recurring = _detect_recurring_topics(tension_history)
```

**優點**：最接近「AI 自主思考」的模式
**缺點**：完全是新功能，需要更多設計

## 建議路線

```
Phase 1: 策略 A (Prompt Prefix)  ← 最快驗證概念
Phase 2: 策略 B (Council 脈絡)   ← 精細化
Phase 3: 策略 C (Semantic Trigger) ← 真正的自主查詢
```

## Token 經濟學

| 來源 | Tokens | 頻率 |
|------|--------|------|
| 3 frames Mermaid | ~300 | 每輪 |
| JSON sidecar (top 3) | ~150 | 每輪 |
| Chain summary | ~50 | 每輪 |
| **Total** | **~500** | 佔 4K window 的 12.5% |

500 tokens 的圖鏈脈絡 vs 讀完整對話歷史（2000+ tokens）= **75% token 節省**。

## 跨 Session 記憶恢復（D 的延伸實驗）

```
新 session 開始
    ↓
讀取 visual_chain.json（磁碟持久化）
    ↓
chain.get_recent(5) → 5 張上次 session 的快照
    ↓
AI 一眼看到：
  • 上次張力很高（tension_map）
  • 有一個斷裂未修復（rupture_timeline）
  • 三個承諾還活著（commitment_tree）
    ↓
AI 不需要讀完 conversation history，
圖已經告訴它 80% 的脈絡。
```

## 待驗證

- [ ] Mermaid 圖是否真的比文字更 token-efficient？
- [ ] LLM 是否能正確解讀 Mermaid 圖的結構資訊？
- [ ] 圖鏈脈絡是否真的改善了議會審議的品質？
- [ ] 跨 session 恢復時，圖是否比 JSON summary 更有效？
