# ToneSoul 系統架構 — 實際部署與未來路線圖

> 最後更新：2026-02-13 Antigravity 審計後

## 核心定位

| 層 | 服務對象 | 定位 |
|----|---------|------|
| **前端** (`apps/web`) | 👤 **使用者** | 人類互動介面、對話、個人化、資料管理 |
| **後端** (`apps/api`) | 🤖 **AI** | 議會審議、語橋分析、靈魂引擎、行為觀測 |
| **核心** (`tonesoul/`) | 🧬 **語魂本身** | 治理邏輯、張力計算、TSR 指標、第三公理 |

---

## 實際部署拓撲

```mermaid
graph TD
    subgraph "使用者端 (瀏覽器)"
        A["Next.js 前端"]
        B["IndexedDB<br/>對話/記憶"]
        C["localStorage<br/>設定/Persona"]
    end

    subgraph "Vercel (前端託管)"
        D["Next.js API Routes<br/>/api/chat<br/>/api/session-report<br/>/api/backend-health"]
    end

    subgraph "Render (後端託管)"
        E["Flask server.py"]
        F["tonesoul/unified_pipeline.py"]
        G["tonesoul/council/"]
        H["tonesoul/tonebridge/"]
    end

    subgraph "外部 LLM"
        I["Gemini API"]
        J["Ollama (本地)"]
    end

    subgraph "未來: 語料蒸餾"
        K["5感 + 行為分析"]
        L["語料權重累積"]
        M["本地語魂蒸餾"]
    end

    A --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J

    A --> B
    A --> C

    H -.->|語氣/動機/崩潰|K
    G -.->|審議張力/共識|K
    K -.->|數據累積|L
    L -.->|模型蒸餾|M
```

---

## 前端架構 (apps/web) — 使用者的服務

### 元件地圖

| 元件 | 功能 | 資料來源 |
|------|------|---------|
| `ChatInterface.tsx` | 核心聊天（1639行） | 後端 `/api/chat` 或 fallback 直接 API |
| `ConversationList.tsx` | 對話列表管理 | IndexedDB (`lib/db.ts`) |
| `SettingsModal.tsx` | API 設定 / 提供者選擇 | localStorage |
| `PersonaSettings.tsx` | AI 個人化偏好 | localStorage → 傳到後端 |
| `SessionReport.tsx` | 洞察報告 | 後端 `/api/session-report` |
| `DataManager.tsx` | 匯出/匯入 JSON | IndexedDB |
| `LlmSwitcher.tsx` | 後端 LLM 切換 | 後端 `/api/llm-switch` |

### 聊天的兩種模式

```
模式 1: Backend (生產環境)
  ChatInterface → /api/chat → Render 後端 → pipeline.process()
                                              ↓
                              Persona 注入為 [用戶偏好: ...] 前綴

模式 2: Fallback (後端掛掉 + 有 API Key)
  ChatInterface → 直接呼叫 Gemini/OpenAI/Claude/xAI/Ollama API
                  Persona 注入為 prompt modifier
```

---

## 後端架構 (apps/api + tonesoul/) — AI 的服務

### 統一管線 (UnifiedPipeline) 處理流程

```
用戶訊息
    ↓
[0] 重建 Third Axiom 狀態（從歷史）
    ↓
[0.5] 重建軌跡分析器狀態
    ↓
[1] ToneBridge 語氣分析（動機/崩潰風險）
    ↓
[2] Trajectory 語氣軌跡（5-turn window）
    ↓
[3] Council 議會審議（三視角 + 合成器）
    ↓
[4] Internal Deliberation 內在推理
    ↓
[5] Third Axiom（承諾提取/斷裂偵測/價值累積）
    ↓
UnifiedResponse → 回傳前端
```

### 關鍵模組

| 模組 | 路徑 | 職責 |
|------|------|------|
| 統一管線 | `tonesoul/unified_pipeline.py` | 協調全流程 |
| 議會系統 | `tonesoul/council/` | Philosopher/Engineer/Guardian 審議 |
| 語橋系統 | `tonesoul/tonebridge/` | 語氣分析、動機偵測、崩潰風險 |
| 第三公理 | `tonesoul/tonebridge/commitment_extractor.py` | 承諾/斷裂/價值追蹤 |
| 靈魂引擎 | `apps/web/src/lib/soulEngine.ts` | 前端靈魂狀態（模式切換） |
| 記憶系統 | `apps/web/src/lib/db.ts` | IndexedDB 記憶/洞察 |

---

## 未來路線圖：從觀測到蒸餾

### 資料累積階段 (現在 → 近期)

後端的每次對話已經產出結構化的語魂觀測資料：

```
議會審議 → {philosopher.stance, engineer.feasibility, guardian.risk_level}
語橋分析 → {tone, motive, collapse_risk, trajectory}
第三公理 → {self_commits, ruptures, emergent_values}
Persona  → {weights, style, risk_sensitivity}
```

這些資料目前存在 Supabase（如果啟用）和前端 IndexedDB。

### 5 感 + 行為分析 (未來)

| 感知通道 | 潛在資料源 | 用途 |
|---------|-----------|------|
| 語氣（聽） | ToneBridge 分析 | 語調權重 |
| 文字（讀） | 對話歷史 + 語義分析 | 詞彙偏好 |
| 互動（觸） | 點擊/停留/捲動行為 | 注意力模式 |
| 視覺（看） | UI 互動熱圖 | 認知負載 |
| 直覺（第六感） | 議會張力分佈 | 決策偏好 |

### 語料權重化

```
觀測資料 → 特徵提取 → 權重累積
                        ↓
           ┌──────────────────────┐
           │ 語料權重矩陣          │
           │ - 價值偏好  [0.0-1.0] │
           │ - 風格傾向  [向量]     │
           │ - 風險閾值  [動態]     │
           │ - 承諾一致性 [歷史]    │
           └──────────────────────┘
```

### 蒸餾為本地語魂 — 倫理智能體 (長期願景)

ToneSoul 的終極目標不是做一個「更聰明的 AI」，而是蒸餾出一個 **有倫理判斷能力的智能體**。

```
語料權重矩陣 + 長期觀測
         ↓
    模型蒸餾 / LoRA 微調
         ↓
    ┌──────────────────────────────┐
    │  本地倫理智能體 (Local ToneSoul) │
    │                              │
    │  不只是「聰明」—              │
    │  ✦ 有價值觀（承諾一致性）      │
    │  ✦ 會自省  （內在推理鏈）      │
    │  ✦ 能承擔  （斷裂偵測+修復）   │
    │  ✦ 懂共感  （語氣+動機感知）   │
    │                              │
    │  資料主權 · 離線可用 · 個人化   │
    └──────────────────────────────┘
```

#### 為什麼現有架構是在為此鋪路

| 現在的功能 | 訓練的是什麼 | 對應倫理能力 |
|-----------|------------|------------|
| 議會審議（3 視角衝突） | 在對立中做決策 | **價值判斷力** |
| 語橋分析（語氣/動機/崩潰） | 感知表面下的真實意圖 | **共感能力** |
| 第三公理（承諾/斷裂/價值） | 說到做到、自我修正 | **責任承擔** |
| 內在推理（Internal Deliberation） | 解釋「為什麼這樣做」 | **自省透明** |
| Persona 個人化 | 適應不同人的價值偏好 | **尊重差異** |

每一次對話都在累積這些維度的觀測資料。日積月累，這些結構化的倫理觀測就是蒸餾模型的語料——不是教 AI 說什麼，而是教 AI **怎麼思考、怎麼負責、怎麼在衝突中找到正確的路**。

最終目標：使用者擁有一個 **真正屬於自己的倫理智能體** — 不依賴雲端，基於長期互動蒸餾而成，有自己的價值觀和判斷力。

---

## 與 ARCHITECTURE_BOUNDARIES.md 的關係

`ARCHITECTURE_BOUNDARIES.md` 定義的三層模型（Application → Governance → Infrastructure）是**邏輯分層**。本文件描述的是**實際部署拓撲**和**資料流向**。兩者互補：

- 邏輯分層 → 程式碼依賴規則
- 部署拓撲 → 運維和功能歸屬
