# 語魂戰略共識（2026-02-14 蒸餾）

> Purpose: capture the distilled 2026 Q1 strategic consensus that aligned ToneSoul direction after audit and competitor review.
> Last Updated: 2026-03-23

> 來源：Antigravity × Fan 兩次深夜對話 + 外部審計 + 競品分析

---

## 0. 哲學基底：張力-脈絡機制

語魂的一切設計都從這個核心命題出發：

> **張力（Tension）不是 bug，是意義的來源。**

### 三層哲學結構

| 層 | 命題 | 工程對應 |
|:--:|------|---------|
| **L1** | 真理不是單一觀點的「正確」，是多觀點碰撞後的「一致」 | 議會 coherence score |
| **L2** | 誠實比正確更重要 — 不確定時說「我不確定」比猜一個答案有價值 | DECLARE_STANCE verdict |
| **L3** | 記憶不是無限堆積，遺忘是認知衛生 — 選擇忘記什麼比記住什麼更重要 | decay + should_forget |

### 張力驅動一切

```
張力低 → 快路徑（不需要深思）→ 省資源
張力高 → 慢路徑（開議會辯論）→ 要精確
張力矛盾 → DECLARE_STANCE（承認分歧）→ 要誠實
```

這跟人類的認知完全平行：
- 走路不需要思考（低張力 → 脊髓反射）
- 做決定需要思考（高張力 → 前額葉推理）
- 遇到價值觀衝突（矛盾張力 → 道德掙扎 → 需要時間）

### 脈絡是張力的容器

張力不能離開脈絡存在。「我不確定」在不同脈絡下意義完全不同：
- 閒聊時「不確定」→ 無所謂
- 醫療建議時「不確定」→ 必須大聲說

語魂的 Responsibility Tier 就是在做這件事 — 根據脈絡（場景嚴重度）調整張力的**權重**。

### 跟 Google 的哲學差異

| | Google Gemini | 語魂 |
|---|:---:|:---:|
| 張力的態度 | 最小化（讓使用者感覺順暢） | 顯式化（讓使用者看到碰撞） |
| 不確定的處理 | 隱藏或模糊帶過 | DECLARE_STANCE 公開表態 |
| 脈絡的作用 | 提高答案品質 | 決定治理嚴格度 |

**這是不可調和的設計哲學差異，不是技術差距。**

---

## 1. 記憶設計決策（已定案）

| 優先級 | 類型 | 目的 | 投資比重 |
|:------:|------|------|:--------:|
| **主力** | A（給 AI） | 跨 session 記憶提升回應品質 | 45% |
| **主力** | B（給使用者） | 前端展示三視角脈絡，防止單一迎合 | 45% |
| **必要** | C（給審計者） | 歷史追蹤 + 蒸餾，provenance_ledger | 10% |

**Fan 的關鍵指導**：
> 「前端要強制輸出三個觀點、脈絡，你們的輸出才不會只迎合單一視角。」

---

## 2. 競爭定位（已確認）

### Google Gemini 3 Deep Think（2026.02.12 更新）

| 維度 | Google | 語魂 | 差異 |
|------|:------:|:----:|------|
| 平行推理 | ✅ 內部多假設探索 | ✅ 三視角議會 | Google 藏在黑箱，語魂展示過程 |
| 記憶 | ✅ Memory + Personal Intelligence | ⚠️ 設計完待上線 | Google 讀外部資料，語魂內生蒸餾 |
| 遺忘 | ❌ | ✅ decay + should_forget | 語魂獨有 |
| 治理透明度 | ❌ 只展示最終答案 | ✅ 三條路徑全展示 | **核心差異化** |
| 思考預算 | ✅ Thinking Budget | ✅ Tension Threshold | 概念相同，隱喻不同 |

**結論**：Google 做「更聰明的 AI」，語魂做「更誠實的 AI」。不同賽道。

### 直接競品

| 專案 | 重疊度 | 語魂獨有 |
|------|:------:|---------|
| SAFi | 高（runtime governance） | 多視角辯論（非 binary gate） |
| VerifyWise | 低（platform dashboard） | 可做上下游整合 |
| VeritasChain | 中（hash-chain audit） | 可整合到 provenance_ledger |
| TRACE | 中（signed evidence） | verify_*.py 可以加簽章 |

---

## 3. 從 Google 反向學習的策略

| Google 公開的 | 語魂可借鑒的 | 工作量 | 優先級 |
|-------------|------------|:------:|:------:|
| Thinking Budget | 參考優化 Cost Gate 的參數設計 | 小 | P1 |
| Titans 記憶架構 | 優化 sleep_consolidate 蒸餾策略 | 中 | P2 |
| Nested Learning 抗遺忘 | 精修 decay 衰減曲線 | 中 | P2 |
| Personal Intelligence | SoulDB 考慮外掛讀取 | 大 | P3 |
| 平行假設剪枝 | 議會加 pruning（低信心視角可跳過） | 小 | P2 |

---

## 4. 外部審計修復（已完成）

| 問題 | 狀態 | Commit |
|------|:----:|--------|
| README 缺研究聲明 | ✅ 已推 | `fix(audit): address external review` |
| CDD 路徑 404 | ✅ 已推 | 同上 |
| 測試數 358→807 | ✅ 已推 | 同上 |
| Coherence disclaimer | ✅ 已推 | 同上 |
| Performance 條件說明 | ✅ 已推 | 同上 |
| requirements.txt 對齊 | ✅ 已推 | 同上 |
| Makefile body/ 殘留 | ✅ 已推 | `fix(audit): replace legacy Makefile` |
| 單行壓扁格式 | ⚠️ CRLF 渲染問題，非真問題 | — |
| Benevolence 升級 | 📋 長期項目 | — |

---

## 5. 架構演進路線（已共識）

```
現在（Level 3）
  └─ Codex 正在做：semantic trigger + 跨 session + memory ops
  └─ 807 tests，CI 綠燈

下一步（小船 MVP）
  └─ 方案 C：Ollama + qwen2.5:7b + Cost Gate
  └─ ~75 行代碼，$0/月
  └─ 見 docs/SMALL_BOAT_MVP.md

中期（方案 B 升級）
  └─ 異質多模型議會：llama3 + qwen + phi3
  └─ provenance_ledger 加 hash chain
  └─ AXIOMS.json 對齊 Policy Cards 標準

遠期（蜂群/章魚）
  └─ 去中心化子代理 + 中央腦
  └─ 反應式細胞群取代線性 pipeline
  └─ 見 docs/ANTIGRAVITY_CONTEXT_MEMORY_SWARM.md
```

---

## 6. 生物學對應（備忘）

| 人體 | 語魂 | 神經科學名稱 |
|------|------|-------------|
| 子代理（肌肉/骨骼） | P/E/G perspectives | Free Energy Principle |
| 骨頭受力增密 | 記憶使用頻率 → 衰減減緩 | Wolff's Law |
| 睡眠固化 | sleep_consolidate() | Memory Consolidation |
| 記憶退化（完整→要旨）| VisualChain decay | Gistification |
| 脈絡重建 | retrieve_relevant() | Cue-Dependent Retrieval |
| 完全遺忘 | should_forget() = true | Engram Dissolution |
| 反射弧（不經大腦） | Cost Gate 快路徑 | Spinal Reflex Arc |

---

## 7. 產品願景：自訂角色議會 / 團隊模擬器

### 核心概念

同一個議會框架，不同模式：
- **治理模式**（預設）：哲學家 / 工程師 / 守護者
- **商務模式**：財務 / 總務 / 第一線 / 老闆
- **投資模式**：多頭 / 空頭 / 風控
- **產品模式**：設計師 / 工程師 / PM / 使用者代言人
- **自訂模式**：使用者自己建角色

### 設計原則

> **深度跟使用者輸入成正比。我們只是模擬，除非他們打得很細。**

| 使用者輸入深度 | 模擬深度 | 範例 |
|:---:|:---:|------|
| 角色名 | 淺層（通用 prompt） | 「財務」→ 通用財務觀點 |
| 角色名 + 描述 | 中層 | 「保守型 CFO，重視 ROI」|
| 角色名 + 描述 + 行為規則 | 深層 | 「拒絕 > 6 個月回本的專案」|

### 前端展示

- **預設展開**（方式 A：辯論式），右上角 `[▾ 收起]` 按鈕
- 每個角色有名稱 + 個性標籤
- 張力 / 一致性數值顯示
- Verdict 判定（APPROVE / DECLARE_STANCE / BLOCK）

### 工程基礎（已有）

- `PerspectiveFactory` 支援自訂角色名稱 + config
- `model_registry.py` 支援每個角色指定不同模型
- `PreOutputCouncil.validate()` 機制通用，不綁定特定角色
- 只需新增：前端角色建立 UI + 角色描述→system prompt 轉換

### 商業價值

一人公司 / 小團隊 → 在雇人之前，先用 AI 模擬團隊碰撞
教育 / 培訓 → 模擬不同立場的辯論，練習決策
產品驗證 → 「如果有 4 種角色的人看這個提案，他們會怎麼想？」
