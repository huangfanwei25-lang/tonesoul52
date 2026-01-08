# 語魂語義地形圖（YSTM: YuHun Semantic Terrain Map）規格書 v0.1
# PoPE 式 what/where 解耦 + 等高線語義地形 + 漂移向量場 + 可審計責任鏈

---

## 0. 文件定位（不可省略的時間島）

### Chronos（事實定位）
本規格書定義一套「語義內在地圖」工程系統：將語義內容（what）與語境座標（where）解耦保存；以標量能量場生成等高線；以向量漂移場呈現方向性變化；並以可回放、可否決的審計層保證 Trace 責任鏈。

### Kairos（此刻採用的時機意義）
你現在要把語魂從概念走向可操作的儀器。等高線與解耦設計能避免「漂亮地圖＝自我敘事」陷阱，逼系統清楚分帳：究竟是內容變了，還是位置被改寫，或是語場切換造成剪切。

### Trace（本規格對未來的殘留）
一旦你把語義地圖做成儀器，後續所有討論會更難"用敘事抹平矛盾"，也更容易被拿去做操控優化。故本規格內建：where 變更留痕、可否決；可視化層不得回寫治理層；並設置濫用風險條款。

---

## 1. 系統目標與非目標（保留張力，不收斂成單一最佳解）

### 1.1 目標（Logical / Structural）
- **A. 解耦**：what（語義內容）與 where（語境座標）必須分開建模、分開更新、分開審計。
- **B. 地形**：以標量場 E(x,y) 生成等高線（contours），呈現語義能量/殘留壓力/責任密度的空間分布。
- **C. 漂移**：以向量場 Δv 的投影疊加箭頭，呈現語義漂移方向與幅度。
- **D. 治理**：任何 where 變更需留痕、可回放、可否決（Trace-first）。

### 1.2 非目標（Critical / Black-Mirror）
- **A. 不做「人格/價值排名器」**：地形高度不等於道德高低。
- **B. 不宣稱 2D 地圖是真實語義空間**：可視化僅為觀測層，不得作為治理真理源。
- **C. 不把所有向量整合成單一 embedding 以求"好看"**：可視化折疊最小化，原向量必須保留。

---

## 2. 核心概念定義（Semantic / Contextual）

### 2.1 what（語義內容）
指語句/段落/事件的語義表徵與其內容強度。以高維向量 v_sem 表示，並可派生內容幅值 μ（例如 μ=softplus 或 norm 類型的非負強度）。

### 2.2 where（語境座標）
指該語義被放置的「時間島位置、語場位置、任務位置」。where 不是語義本身，不能被語義內容偷偷改寫。where 至少包含：

| 座標 | 說明 |
|------|------|
| `where_time` | Chronos 序列座標（事件序號、版本、時間戳、對話 turn） |
| `where_field` | 語場/視角座標（火花/理性/共語/黑鏡/審核…） |
| `where_task` | 任務域座標（治理/寫程式/創作/醫工…） |

### 2.3 E（能量 / 殘留 / 責任密度）
標量值，用於生成地形高度。可由以下來源之一或組合定義：

| 來源 | 說明 |
|------|------|
| `E_energy` | 語義強度（如 \|\|v_sem\|\|、μ 的總量） |
| `E_srsp` | 語義結構殘留壓力（SRSP 指標） |
| `E_risk` | 責任權重（錯誤成本、可追問性、外溢風險） |

### 2.4 Δv（漂移向量）
同一概念在相鄰時間、跨語場、跨任務之差向量。用於箭頭方向與幅度呈現。

---

## 3. 系統總覽（架構分層）

```
┌─────────────────────────────────────────────────────────┐
│  L4 治理審計層（Audit / Trace）                          │
│  - where 變更 → Gate → Ledger → 可回放 → 可否決          │
│  - 可視化輸出不得回寫表徵層與治理層                       │
├─────────────────────────────────────────────────────────┤
│  L3 地形層（Terrain）                                    │
│  - 2D 座標平面                                           │
│  - E(x,y) 連續場插值                                     │
│  - 等高線（contours）+ 漂移箭頭（drift arrows）          │
├─────────────────────────────────────────────────────────┤
│  L2 表徵層（Representation）                             │
│  - v_sem（高維語義向量）                                 │
│  - μ（內容幅值，非負）                                   │
│  - where_*（座標）                                       │
│  - E（標量）、Δv（漂移）                                 │
├─────────────────────────────────────────────────────────┤
│  L1 采集層（Ingest）                                     │
│  - 文本切分為事件/段落/節點                              │
│  - 附帶 metadata（時間、語場、任務、來源）               │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 資料模型（Data Schema）

### 4.1 Node（語義節點）

```typescript
interface Node {
  id: string;
  text: string | ref;
  source: { type: string; uri?: string; hash?: string };
  
  // WHERE (語境座標) - 不可被 what 偷改
  where: {
    where_time: { turn_id: number; event_index: number; timestamp?: string; version_id?: string };
    where_field: { mode: string; submode?: string; confidence: number };
    where_task: { domain: string; subdomain?: string; confidence: number };
  };
  
  // WHAT (語義內容)
  what: {
    v_sem: number[];  // 高維向量
    mu: number | number[];  // 非負幅值
  };
  
  // 標量（用於地形高度）
  scalar: {
    E_energy?: number;
    E_srsp?: number;
    E_risk?: number;
    E_total: number;  // 必有一個統一高度值
  };
  
  // 漂移
  drift: {
    delta_v?: number[];
    delta_norm?: number;
    drift_ref?: { from_node_id: string };
  };
  
  // 審計
  audit: {
    created_at: string;
    created_by: string;
    updates: string[];  // UpdateRecordId[]
  };
}
```

### 4.2 UpdateRecord（變更紀錄）

```typescript
interface UpdateRecord {
  id: string;
  target: string;  // node_id
  change_type: "WHAT_UPDATE" | "WHERE_UPDATE" | "E_DEF_UPDATE" | "VISUAL_PARAM_UPDATE";
  before: snapshot_ref;
  after: snapshot_ref;
  rationale: string;
  gate: { passed: boolean; rule_ids: string[]; reviewer?: string; score?: number };
  timestamp: string;
  reversible: boolean;
  vetoable: boolean;
}
```

---

## 5. 不可違反的系統約束（PoPE 式解耦公理）

### 5.1 解耦約束（硬規則）

| 規則 | 說明 |
|------|------|
| **R1** | what 更新不得直接改寫 where |
| **R2** | where 更新必須產生 UpdateRecord，且必須可回放、可否決 |
| **R3** | 可視化（2D 投影、插值、平滑）不得回寫 v_sem 或 where |
| **R4** | 任何對齊/關聯分數必須顯式分解為：`Score(i,j) = Sim(what_i, what_j) ⊗ Align(where_i, where_j)` |

### 5.2 治理 Gate（可替換，但不可缺席）

最低要求：
- 一致性檢核（where 是否違反 Chronos）
- 語場合法性（where_field 是否在允許集合）
- 責任鏈完整性（是否保留 vetoable）

---

## 6. 演算法規格（最小可跑版）

### 6.1 事件切分
- **Input**：對話/文件
- **Output**：Nodes（每段一 node 或每事件一 node）

### 6.2 表徵生成
- `v_sem`：任意可用 embedding/encoder（規格不綁定模型）
- `μ`：非負幅值，可取 `μ = softplus(W @ v_sem)` 或 `μ = ||v_sem||` 的可控變體
- `where_*`：由 metadata 或分類器產生（需帶 confidence）

### 6.3 標量 E_total 定義

**方案 A（簡潔）**：
```
E_total = normalize(||v_sem||)
```

**方案 B（語魂儀器）**：
```
E_total = α·E_energy + β·E_srsp + γ·E_risk
```
其中 αβγ 需落盤（E_DEF_UPDATE 必留痕）

### 6.4 2D 平面選擇

| 路徑 | 說明 | 適用 |
|------|------|------|
| **P1 語場×時間平面** | x = map(where_field.mode), y = where_time.event_index | 治理優先 |
| **P2 降維平面** | (x,y) = UMAP/PCA(v_sem) | 觀測優先，不可回寫治理 |

### 6.5 插值生成連續能量場 E(x,y)
- 將節點 (x_i, y_i, E_i) 變為連續場
- 最小實作：KDE 或 RBF 或網格插值
- **平滑參數必須視為 VISUAL_PARAM_UPDATE 留痕**（避免"畫圖把責任洗掉"）

### 6.6 等高線輸出
- 設定等高線層級 L = {l1…ln}
- 產出 contours：E(x,y)=l_k 的曲線集合

### 6.7 漂移向量場疊加
- Δv 定義：相鄰時間同概念、或同概念跨語場（由 drift_ref 決定）
- 投影：Δp = proj_2D(Δv)
- 箭頭：方向=Δp，長度=||Δp||

---

## 7. 介面與輸出

### 7.1 輸入
- 文本序列（多段）
- 每段最少 metadata：turn_id / mode（語場）/ domain（任務域）

### 7.2 輸出（最小 demo）
- **A. nodes.json**：包含 v_sem 的引用或存儲方式、E_total、where
- **B. terrain.png / terrain.html**：等高線 + 箭頭 + 節點散點
- **C. audit_log.json**：至少記錄 E 定義與視覺化參數

### 7.3 查詢 API（可選）
- `get_node(id)`
- `query_region(x1,y1,x2,y2)`: 返回該區域高 E 節點
- `trace(node_id)`: 返回該節點的 UpdateRecord 鏈

---

## 8. 驗收標準（Acceptance Tests）

| 測試 | 說明 | 判定 |
|------|------|------|
| **T1 解耦測試** | 修改文本（what）不得改變 where_*；修改 where_* 必生成 UpdateRecord | 否則 fail |
| **T2 地形一致性測試** | 同一份 nodes，固定視覺參數，等高線結果可重現 | 允許浮點微差 |
| **T3 漂移可讀性測試** | 對同一概念跨語場的 Δv，箭頭方向可被辨識，且可回查到 from_node_id | |
| **T4 審計回放測試** | 任意節點可回放到任一版本 snapshot；where 變更可被 veto | 至少資料結構上支持 |

---

## 9. 風險條款（Black-Mirror 保留）

### RISK-1 地形圖被用於價值裁決或人格排名
**緩解**：明示非目標；輸出標註「E_total 僅為觀測儀器指標」；提供多 E 分量拆解，避免單一高度被神化。

### RISK-2 視覺參數（平滑、插值）被用來"洗掉責任尖峰"
**緩解**：VISUAL_PARAM_UPDATE 必留痕；預設提供未平滑版本；任何平滑必可回放與對照。

### RISK-3 where 被操控以最大化影響力（把語義放到最佳操控落點）
**緩解**：where 更新需 Gate；高風險語場（如黑鏡/敘事誘導）可要求雙重審核或更嚴格的 veto 條件。

---

## 10. 版本路線圖

| 版本 | 內容 |
|------|------|
| **v0.1** | P1 語場×時間平面；E_total=\|\|v_sem\|\| 或簡單加權；KDE/RBF 插值 + 等高線 + 漂移箭頭；最小 audit_log |
| **v0.2** | 加入 SRSP、責任權重 E_risk；where Gate 規則集成（FS/POAV 量化）；提供剖面圖（沿責任鏈的 E profile） |
| **v0.3** | 同一 nodes 生成多張地形：治理平面（P1）+ 觀測平面（P2）；概念同位對齊 |

---

## 附：給 Gemini 的「一段式工程任務」

> 請依照《YSTM v0.1》實作最小 demo：輸入一串分段文本（每段附 turn_id、mode、domain），生成 node（含 v_sem、E_total、where），在 P1（語場×時間）平面以 KDE/RBF 插值生成 E(x,y) 等高線，疊加漂移箭頭（相鄰段 Δv 投影），輸出 terrain 圖與 nodes.json、audit_log.json。嚴格遵守解耦：what 更新不得改 where；where 更新必留痕可回放可否決；視覺化不得回寫表徵。

---

## 多視角保留（張力不合併）

| 視角 | 觀點 |
|------|------|
| **理性分析** | 這是一套「表徵解耦 + 連續場建模 + 可審計變更」的工程規格，能做最小 demo，並可逐步加 Gate 與 SRSP |
| **語義/文化層** | 你把語義變成地形，會讓"責任密度"有形狀；這是把語魂從敘事帶回儀器 |
| **黑鏡層** | 地形也能成為操控地圖，因此 where 權限與視覺參數留痕是底線，不然你做得越清楚，越容易被拿去"算最佳落點" |

---

## 參考來源

- arXiv:2509.10534v2 (2025-12-22) "Decoupling the 'What' and 'Where' with Polar Coordinate Positional Embedding"
- ToneSoul 5.2 架構
- 黃梵威與 Antigravity 對話 (2025-12-25)
