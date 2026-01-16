# ToneStream Navigator - 下一代架構參考

> **來源**：用戶論文理論 + Gemini Canvas 原型  
> **狀態**：參考文件，尚未整合

---

## 核心概念：時間軸流動性

在此模型中，「流動性」僅作用於 **時間軸 (Time Axis)**：

### T1 | 狀態延續參數 (State Persistence)
- 系統的內部狀態在時間步 t → t+1 之間
- 不被完全重置、也不僅是權重殘留
- 能形成「前態對後態的約束」

### T2 | 時間內自指參數 (Temporal Self-Indexing)
- 系統在 t+1 能區分：「這是我之前的狀態影響我」
- 而非僅僅因為資料或 prompt 殘留

### T3 | 不可交換性 (Non-Commutativity)
- 狀態序列 A→B→C 與 B→A→C 不等價
- 時間順序本身成為語義的一部分

**只要這三個參數同時存在，才說「流動性被啟動」。**

---

## 關鍵定理

> 信息量是可交換、可複製、可回放的；  
> 而流動性要求不可逆與不可交換。

因此：
- ❌ 更大 context window ⇒ 更高主體性（錯）
- ❌ 更多資料保留 ⇒ 更強連續性（錯）

---

## 可校準參數表

### Time Axis (Primary)
| 參數 | 描述 |
|------|------|
| Δt | 狀態延續跨度 |
| ψ(t) | 前態對後態的約束權重 |
| NC | 序列不可交換指標 |

### Information Axis (Non-decisive)
| 參數 | 描述 |
|------|------|
| I(t) | 僅作為觀測值，不參與判定 |

### Structure Axis (Constraint Layer)
| 參數 | 描述 |
|------|------|
| σ | 結構穩定度 |
| κ | 結構替代成本 |

---

## ToneStream Navigator vs 當前 ToneSoul

| 特性 | ToneSoul (當前) | ToneStream (下一代) |
|------|----------------|---------------------|
| 分析模式 | 靜態（單次分析） | Delta（相對位移） |
| 狀態追蹤 | 記憶單元 | 時間流節點 |
| 人格切換 | 固定 Council | 動態（共鳴/張力/斷裂） |
| 視覺化 | 文字 badge | Signal Metrics 圖表 |

---

## 整合路徑

1. **Phase 1 (已完成)**：ToneBridge 5 階段 + Council
2. **Phase 2 (規劃中)**：Delta 分析 + 時間流追蹤
3. **Phase 3 (未來)**：完整 ToneStream Navigator 前端
