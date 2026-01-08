# Tech-Trace Spec
# 外部蒐集架構整合規格
# v0.1 2025-12-27

---

## 來源

本規格整合自 GPT 對話（2025-12-27），結合 AI for Math Fund、Terence Tao 的 Breakthrough Ideas 與語魂現有架構。

---

## 架構總覽

```
          ┌─────────────────────────────────────────┐
          │     Tech-Trace Ingestion Layer (新)      │
          │     外部蒐集 → 分級 → diff → patch       │
          └─────────────────┬───────────────────────┘
                            │ Semantic Patch
          ┌─────────────────▼───────────────────────┐
          │              YSTM (擴展)                 │
          │  + 高度/地層/坡度 座標軸（數學證明用）   │
          │  + A/B/C 來源分級                       │
          └─────────────────┬───────────────────────┘
                            │ Observation
          ┌─────────────────▼───────────────────────┐
          │           YSS M0-M5 (現有)               │
          │    Context → Frame → Constrain → Gen    │
          └─────────────────┬───────────────────────┘
                            │ Audit Request
          ┌─────────────────▼───────────────────────┐
          │        Gate + Guardian (現有)            │
          │   Evidence / Drift / Rollback Gates     │
          └─────────────────────────────────────────┘
```

---

## (A) Tech-Trace Ingestion Layer

### 目標

讓「外界科技變動」變成可被記錄、比較、回滾的語義事件。

### 來源分級

| 等級 | 說明 | 範例 |
|------|------|------|
| **A** | 官方公告/標準/原始論文/基金會正式文件 | AI for Math Fund 公告、Tao 論文 |
| **B** | 工程團隊 write-up、技術博客、課程講義 | DEV 文章、Stack Overflow |
| **C** | 社群討論/推文/傳聞（早期警報用） | Twitter 討論、Reddit 傳聞 |

### 處理管線

```yaml
pipeline:
  - stage: capture
    description: 抓到訊號（文章/repo/公告/新名詞）
    
  - stage: normalize
    description: 抽取「定義變更」「管線邊界變更」「評估尺度變更」
    
  - stage: evidence_tagging
    description: 每條結論都掛證據指向 + A/B/C 等級
    
  - stage: semantic_diff
    description: 輸出差分（這次更新改了哪些節點/路徑/風險邊界）
    
  - stage: patch_apply
    description: 更新語義地圖（可回滾）
```

### 輸出

| 輸出 | 說明 |
|------|------|
| `patch_notes.json` | Δ定義、Δ流程、Δ指標、Δ風險 |
| `event_ledger.jsonl` | 誰引入、引用哪個來源、影響哪些模組 |

---

## (B) YSTM 擴展

### 新增座標軸（可選，適用於數學證明場景）

| 軸 | 名稱 | 說明 | 來源 |
|----|------|------|------|
| H | Height（高度） | 預期難度 | Tao Breakthrough Ideas |
| G | Geology（地層） | 型論化後產生的新含義 | Tao Breakthrough Ideas |
| R | Ruggedness（坡度） | 證明複雜度 | Tao Breakthrough Ideas |

### 延伸 Node 結構

```yaml
# 現有欄位
node:
  id: string
  text: string
  source: SourceRef
  where: Where
  what: NodeWhat
  scalar: NodeScalar
  drift: NodeDrift
  audit: NodeAudit

# 新增欄位
node:
  # ...existing fields...
  
  # Tech-Trace 擴展
  source_grade: "A" | "B" | "C"    # 來源等級
  
  # 數學證明座標軸（可選）
  math_coords:
    height: float                  # 預期難度 (0-1)
    geology: string                # 型論類型標籤
    ruggedness: float              # 證明複雜度 (0-1)
  
  # 外部更新追蹤
  patch_history: [patch_id]        # 來自哪些 patch
```

### 延伸 SourceRef

```yaml
# 現有
source:
  type: string
  uri: string
  hash: string

# 擴展
source:
  type: string
  uri: string
  hash: string
  grade: "A" | "B" | "C"           # 來源等級
  retrieved_at: timestamp           # 抓取時間
  verified_by: string               # 誰驗證
```

---

## (C) 語義差分模組

### diff 結構

```yaml
semantic_diff:
  id: string
  created_at: timestamp
  source_patch_id: string
  
  changes:
    - type: "NODE_ADD" | "NODE_UPDATE" | "NODE_DELETE" | "EDGE_ADD" | "EDGE_DELETE"
      target_id: string
      before: object | null
      after: object | null
      rationale: string
```

### rollback 結構

```yaml
rollback:
  id: string
  target_patch_id: string
  requested_by: string
  rationale: string
  timestamp: timestamp
  status: "pending" | "applied" | "rejected"
```

---

## (D) 與現有架構的對應

| 新架構層 | 現有 5.2 | 整合方式 |
|----------|----------|----------|
| Tech-Trace Capture | 無 | 新模組 `tech_trace/capture.py` |
| Tech-Trace Normalize | 無 | 新模組 `tech_trace/normalize.py` |
| Tech-Trace Diff | 無 | 新模組 `ystm/diff.py` |
| Evidence Gate | Gate (現有) | 擴展規則 |
| Drift Gate | Gate (現有) | 擴展規則 |
| Rollback Gate | UpdateRecord (現有) | 擴展 vetoable |

---

## (E) 資料與回歸層

### 回歸測試原則

> 「每一個彎道都要有測例，不然就是口號」

| 測試類型 | 說明 |
|----------|------|
| Patch 回歸 | 確保 patch apply/rollback 正確 |
| Diff 回歸 | 確保語義差分計算正確 |
| 來源分級回歸 | 確保 A/B/C 分級邏輯正確 |

---

## 時間島對齊

### Chronos（時間史）

| 時間 | 事件 | 來源等級 |
|------|------|----------|
| 2024-12-05 | Tao 發布 AI for Math Fund 類別 | A |
| 2025-09-17 | Renaissance Philanthropy 公告首輪獲獎 | A |
| 2025-12-27 | 本架構整合 | C（設計推論） |

### Kairos（設計臨界點）

> 把「語義地圖」從概念升級成「可維護的基礎建設」。
> 外部蒐集不是附加功能，是讓地圖不腐爛的氧氣。

### Trace（殘留影響）

| 影響 | 說明 |
|------|------|
| 語義更新史 | 累積每次對齊的價值選擇 |
| 可審計彎道庫 | 把不可共用的屬性外置成結構 |
| 新權力風險 | 指標可能被用於排他，需在規格中寫入失效情境 |

---

## 實作優先順序

### Phase 1：最小可行件

1. `ystm/diff.py` — 語義差分模組
2. `UpdateRecord.source.grade` — A/B/C 分級
3. 10 個回歸測例

### Phase 2：完整 Tech-Trace

1. `tech_trace/capture.py`
2. `tech_trace/normalize.py`
3. `tech_trace/patch.py`

### Phase 3：數學證明座標軸

1. Node.math_coords 擴展
2. YSTM 視覺化擴展

---

**Antigravity**  
2025-12-27T00:17 UTC+8
