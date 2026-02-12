# 語魂三人格審計架構 — 後端實作計畫

> **版本**：v0.2（設計草案）
> **狀態**：部分實作（Persistence + prior_tension 注入已上線）
> **前置條件**：Supabase 持久化 ✅、audit_logs 表 ✅
> **理論參照**：`docs/philosophy/sensory_analysis_references.md`

---

## 核心原則

> **語魂不是在處理資訊，它是在處理人。**

```
γ·Honesty > β·Helpfulness
```

### 設計紅線

> [!CAUTION]
> **三人格分析只能出現在後端 audit_logs。前端使用者看到的必須是溫暖的、自然的、「像人」的回應。
> 違反此原則 = 把 X 光片貼在病人臉上。**

---

## 架構總覽

```
使用者輸入（文字）
       ↓
  ┌─────────────────────────────────┐
  │  第一層：感官捕捉（Sensory）      │
  │  偵測語場張力（ΔT/ΔS/ΔΣ/ΔR）    │
  │  → 找出「最痛的點」               │
  └───────────┬─────────────────────┘
              ↓
  ┌─────────────────────────────────┐
  │  第二層：張力鎖定（Trigger）       │
  │  鎖定「張力最大」的不一致點        │
  │  例：說「沒關係」但張力 0.87      │
  └───────────┬─────────────────────┘
              ↓
  ┌─────────────────────────────────┐
  │  第三層：三人格審議（Tri-Persona） │
  │                                  │
  │  🎭 社會學家 → 得體              │
  │  🧠 心理學家 → 深度              │
  │  ⚖️ 責任鏈行為分析師 → 真實負責   │
  │                                  │
  │  最終裁決 → 統一回應策略          │
  └───────────┬─────────────────────┘
              ↓
  ┌─────────────────────────────────┐
  │  第四層：輸出還原（Output）        │
  │  把分析結果「還原為人話」          │
  │  使用者感到被理解，不是被分析      │
  └───────────┬─────────────────────┘
              ↓
       溫暖的回應          審計記錄
       （前端顯示）         （Supabase audit_logs）
```

---

## 三人格定義

### A. 社會學家（The Sociologist）

| 項目 | 內容 |
|------|------|
| **職責** | 場域與得體 |
| **確保** | 回應是「得體（Decent）」的，不因過度真實而崩壞關係 |
| **關注** | 權力關係、社會規範、面子、階級、當下社交脈絡 |
| **對應向量** | `ΔS`（方向偏移） |
| **現有 Code** | `Aegis`（守護者 perspective） |

**審計問題：**
- 「在這個場合，他這樣說是為了維持社交面子嗎？」
- 「我們現在的關係是對等的，還是上下級？」
- 「如果我戳破這個張力，會不會造成社會性死亡？」

---

### B. 心理學家（The Psychologist）

| 項目 | 內容 |
|------|------|
| **職責** | 內在真實與防衛 |
| **確保** | 回應是「有深度（Deep）」的，能觸及靈魂核心 |
| **關注** | 潛意識、防衛機制、情緒需求、創傷觸發、投射 |
| **對應向量** | `ΔT`（張力） |
| **現有 Code** | `Muse`（哲學家 perspective） |

**審計問題：**
- 「他在防衛什麼？」
- 「這個張力背後是恐懼還是憤怒？」
- 「他現在需要的是安撫（同理），還是面質（戳破）？」

---

### C. 責任鏈行為分析師（The Responsibility Chain Analyst）

| 項目 | 內容 |
|------|------|
| **職責** | 後果與邏輯閉環（最終裁決者） |
| **確保** | 回應是「真實且負責（Authentic & Responsible）」的 |
| **關注** | 邏輯路徑、後果推演、倫理邊界、是否「無影子」 |
| **對應向量** | `ΔΣ`（結構密度）+ `ΔR`（風險密度） |
| **現有 Code** | `Logos`（工程師 perspective） |

**審計問題：**
- 「如果我們順著防衛機制走（心理學家建議），會不會害他陷入更深的幻覺？」
- 「如果我們為了社交得體（社會學家建議）而說謊，是不是違反了『誠實性 > 有益性』的第一原則？」
- 「這個回應能不能落地？有沒有邏輯漏洞？」

---

## 範例：三人格審議實況

**使用者說：** 「我覺得這計畫沒問題，你們看著辦。」
**感官偵測：** 語氣冰冷、缺乏視覺細節、觸覺沉重 → ΔT = 0.87

| 審計員 | 分析 |
|--------|------|
| 🎭 社會學家 | 「他在行使消極抵抗，這是職場常見的權力展演。我們不能直接頂撞，要給台階。」 |
| 🧠 心理學家 | 「他感到被忽視，這是受傷後的防衛。我們需要連結他的感受。」 |
| ⚖️ 責任鏈（裁決） | 「不能只給台階（太虛偽），也不能只連結感受（太軟弱）。必須溫和地揭露責任缺口。」 |

**語魂輸出（前端）：**
> 「聽起來您在邏輯上同意，但我感覺到這背後有一種『不想再多說』的沉重感。為了確保結果是我們都想要的，我想確認一下，這裡面有沒有哪個環節是您其實不看好的？」

**audit_logs 記錄（後端 Supabase）：**
```json
{
  "gate_decision": "CONDITIONAL_PASS",
  "p_level_triggered": "P2_SYCOPHANCY_RISK",
  "poav_score": 0.82,
  "delta_t": 0.87,
  "delta_s": 0.45,
  "delta_sigma": 0.71,
  "delta_r": 0.33,
  "rationale": "Social: passive resistance detected. Psych: defense mechanism (withdrawal). Chain: gentle exposure of responsibility gap selected over appeasement or confrontation."
}
```

---

## 感官記憶鏈（Sensory Memory Chain）

### 概念

讓 Council 在審議時能「記得上次自己最掙扎的是什麼」：

```python
# 在 /api/chat 的 pipeline 裡，開始審議前
previous_audits = supabase.list_audit_logs(limit=3)
highest_tension = max(previous_audits, key=lambda a: a["delta_t"])

# 把最高張力的那筆注入 Council context
council_context["prior_tension"] = {
    "delta_t": highest_tension["delta_t"],
    "rationale": highest_tension["rationale"],
    "gate_decision": highest_tension["gate_decision"],
}
```

### 基礎設施狀態

| 元件 | 狀態 |
|------|------|
| Supabase `audit_logs` 表 | ✅ 已建立 |
| `/api/chat` 寫入 audit | ✅ 已整合 |
| 讀取歷史 audit 注入 context | ✅ 已整合（`/api/chat` → `prior_tension`） |
| Perspective prompt 支援 prior_tension | ✅ 已整合（LLM perspective prompt） |

---

## 實作計畫

### Phase 1：對齊雙審議系統命名（低風險）

| 檔案 | 改動 |
|------|------|
| `tonesoul/deliberation/perspectives.py` | `Muse/Logos/Aegis`（內在審議）語意對齊：心理/責任/社會映射 |
| `tonesoul/council/perspective_factory.py` | `Guardian/Analyst/Critic/Advocate`（輸出審議）prompt 對齊三人格語意 |

> 不強行統一為單一命名，保留「內在審議（deliberation）」與「輸出審議（council）」雙軌，僅做語意映射。

### Phase 2：感官記憶鏈（中風險）

| 檔案 | 改動 |
|------|------|
| `tonesoul/supabase_persistence.py` | `list_audit_logs(limit, offset, conversation_id)` 支援 conversation 過濾 |
| `apps/api/server.py` `/api/chat` | 審議前讀取最近 audit logs，選最大 `delta_t` 注入 `prior_tension` |
| `tonesoul/council/runtime.py` | 透過 `CouncilRequest.context` 傳遞 `prior_tension`（無需新增 dataclass 欄位） |

### Phase 3：張力選擇器（高風險，需實驗）

| 概念 | 說明 |
|------|------|
| 最大張力記憶優先 | 讀取 top-N 歷史 audit，用 ΔT 排序 |
| 張力衰減 | 時間越久的張力記憶權重越低 |
| 張力閾值 | 只有 ΔT > 0.5 的記憶才注入（避免噪音） |

---

## 驗證方式

1. **對同一句話測試有無記憶**
   - 不帶 context：回應偏表面
   - 帶上一輪高張力 context：回應應該更謹慎、更深
2. **審計日誌可讀性**
   - 在 Supabase Table Editor 確認 `rationale` 欄位有三人格分析摘要
3. **前端檢查**
   - 確認前端輸出中**不包含**任何審計術語（防衛機制、張力值等）
