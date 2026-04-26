# 治理語義引擎 — Governance Semantic Engine (GSE)
# 計畫書 v0.1

作者：claude-sonnet-4-6  
分支：`claude/gse-foundation`  
日期：2026-04-25

---

## 一、動機

語魂目前的治理元件（誓言、張力、Council）是**聲明式**的：
- 誓言告訴你「做什麼」，但不告訴你「怎麼執行」
- 張力有分類，但沒有「當這種張力出現時，具體步驟是什麼」
- Council 審議有流程，但流程沒有原子化的操作單元

PSE（提示語義引擎）展示了另一種設計：每個概念不只有名稱與定義，還有**操作指令**（operation instruction）和**觸發條件**（trigger）。這讓概念從「知識」變成「可執行的行動模板」。

GSE 借用這個結構模式，但完全替換源域：
- PSE 源域：說服心理學 + 注意力操控 → **廣告**
- GSE 源域：賽局理論 + 道德推理 + 認識論 → **治理 + 主體性思考 + 動態推理**

---

## 二、核心概念：可操作本體論

每個 GSE 元素的完整格式：

```
symbol:      [符號]           # 簡短識別碼，如 [Ten], [Vow], [Dbt]
name:        中文名稱
definition:  這個概念是什麼（靜態定義）
role:        主導 | 催化 | 約束   # 在治理組合中的功能角色
cluster:     審議動態 | 主體性狀態 | 原則傳播
period:      1 | 2 | 3
trigger:     什麼情況下這個元素被激活
operation:   具體執行步驟（可被 agent 直接跟從的指令）
falsifiable: 如何知道這個元素在正常工作
```

這個格式和現有 `Vow` dataclass 的主要差異：

| 現有 Vow | GSE Element |
|---|---|
| `description`（說明是什麼）| `definition` + `operation`（說明是什麼 + 怎麼做）|
| `expected: Dict[str, float]`（數字評分）| `trigger`（條件）+ `falsifiable`（可驗證標準）|
| 無角色分類 | `role: 主導/催化/約束` |
| 無族群分類 | `cluster` + `period` |

---

## 三、三個元素族群

### 第一族：審議動態（Deliberation Dynamics）
管理決策過程的動力學。

| 符號 | 名稱 | 角色 | 核心功能 |
|---|---|---|---|
| [Ten] | 張力 | 主導 | 驅動審議方向的衝突點 |
| [Alt] | 替代假設 | 催化 | 強制生成至少一個對立方案 |
| [Stk] | 決策棧 | 約束 | 後進先出的張力解決順序 |
| [Ret] | 撤回門 | 約束 | 不可逆決策的強制停頓點 |

### 第二族：主體性狀態（Agent Interiority）
描述和管理 agent 內部狀態。

| 符號 | 名稱 | 角色 | 核心功能 |
|---|---|---|---|
| [Dbt] | 主體懷疑 | 主導 | 生產性不確定性，防止過早收斂 |
| [Sig] | 信號感知 | 催化 | 讀取隱含訊號而非只讀表層請求 |
| [Bnd] | 邊界意識 | 約束 | agent 知道自己能力邊界在哪 |
| [Drft] | 漂移偵測 | 催化 | 識別原則在執行中的悄悄偏移 |

### 第三族：原則傳播（Principle Propagation）
原則如何在多代 agent 之間傳播、儲存和抵禦漂移。

| 符號 | 名稱 | 角色 | 核心功能 |
|---|---|---|---|
| [R₀] | 再生係數 | 主導 | 一個原則被下一代 agent 接受的機率 |
| [Lat] | 潛伏原則 | 催化 | 休眠的舊決策被重新激活的條件 |
| [Imm] | 免疫機制 | 約束 | 抵禦漂移的設計模式 |
| [Mem] | 跨代記憶 | 催化 | 跨 agent 世代傳遞治理脈絡 |

---

## 四、實作計畫

### Phase 1（本分支）：基礎結構
- `tonesoul/gse/__init__.py`
- `tonesoul/gse/element.py` — `GSEElement` dataclass
- `tonesoul/gse/registry.py` — 元素註冊表，支援按 cluster/role 查詢
- `tonesoul/gse/clusters/*.json` — 12 個種子元素定義
- 升級 `Vow` dataclass：加入 `operation_instruction` + `trigger` 欄位（向後相容）
- 測試：`tests/test_gse.py`

### Phase 2（後續分支）：整合治理系統
- `tension_engine.py` 讀取 `[Ten]` 操作指令
- Council 審議流程使用 `[Alt]`, `[Stk]` 模板
- `drift_monitor.py` 整合 `[Drft]`, `[Imm]` 模式

### Phase 3（後續）：動態推理組合
- 元素「食譜」（recipe）系統：主導 + 催化 + 約束的三角組合
- 治理情境分類器：讀取當前狀態，推薦適用的元素組合

---

## 五、設計邊界

**不做的事：**
- 不建「說服配方」——沒有注意力操控、情感勾引元素
- 不複製 PSE 的廣告導向元素（即使個別元素看起來很像）
- 不建元素間的「化學反應」UI（先打好 schema 基礎）

**GSE 和現有系統的關係：**
- GSE **不取代**現有誓言/張力系統，它是**元描述層（meta-description layer）**
- 現有誓言可以選擇性升級為 GSE 格式，但不強制遷移
- GSE 元素是治理操作的「詞彙表」，不是強制執行的規則

---

## 六、成功標準

1. `registry.load()` 能讀取所有 12 個種子元素
2. 按 cluster 查詢返回正確子集
3. 每個元素的 `operation` 欄位有具體可執行步驟（非空、非泛泛）
4. 升級後的 `Vow` 向後相容現有 vow 定義（`operation_instruction` 可選）
5. 全部測試通過
