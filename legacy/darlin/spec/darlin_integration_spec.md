# Darlin AI 學習整合
# Learnings Integration from Darlin AI
# 2025-12-30

---

## 整合自 Darlin 的設計

| 來源 | 整合內容 | 狀態 |
|------|----------|------|
| **大五人格** | 加入 Persona 定義 | ✅ 已加入 |
| **FER 情緒辨識** | 多模態延伸 | ⏳ 未來 |
| **Qdrant 向量記憶** | 記憶搜尋優化 | ⏳ 未來 |
| **微服務架構** | 模組化參考 | 📚 參考 |

---

## 大五人格整合

### 格式定義

```yaml
big_five:
  openness: float         # 開放性 [0.0, 1.0]
  conscientiousness: float  # 盡責性 [0.0, 1.0]
  extraversion: float     # 外向性 [0.0, 1.0]
  agreeableness: float    # 親和性 [0.0, 1.0]
  neuroticism: float      # 神經質 [0.0, 1.0]
```

### 與語魂三向量的對應

| 語魂向量 | 相關的 Big Five |
|----------|-----------------|
| **ΔT 張力** | neuroticism（反向） |
| **ΔS 語氣** | extraversion + agreeableness |
| **ΔR 責任** | conscientiousness |

### 轉換函數（建議）

```python
def big_five_to_tonesoul(big5: dict) -> dict:
    return {
        "deltaT": 0.5 - big5["neuroticism"] * 0.5,  # 低神經質 = 低張力
        "deltaS": (big5["extraversion"] + big5["agreeableness"]) / 2,
        "deltaR": big5["conscientiousness"],
    }
```

---

## Persona 模板更新

```yaml
Persona:
  id: string
  name: string
  description: string
  
  # 形象（多模態）
  avatar:
    style: "anime" | "realistic" | "abstract"
    reference: string  # 參考角色
    image_path: string  # 可選
  
  # 語魂三向量
  home_vector:
    deltaT: float
    deltaS: float
    deltaR: float
  
  tolerance:
    deltaT: float
    deltaS: float
    deltaR: float
  
  # 大五人格（來自 Darlin）
  big_five:
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
  
  # 其他欄位保持不變
  skills: {}
  patterns: []
  mistakes: []
  council_weights: {}
```

---

## 多模態延伸計畫

### Phase 1: 視覺（Avatar）

| 項目 | 說明 |
|------|------|
| **靜態頭像** | 人格配置中的 avatar.image_path |
| **表情變化** | 根據 deltaT/deltaS 切換表情 |

### Phase 2: 語音

| 項目 | 說明 |
|------|------|
| **TTS** | 根據人格調整語速、語調 |
| **STT** | 語音輸入 |

### Phase 3: 情緒辨識

| 項目 | 說明 |
|------|------|
| **FER** | 攝影機讀取用戶表情 |
| **調整回應** | 根據用戶情緒調整 deltaS |

---

## 記憶系統對比

| Darlin | ToneSoul | 建議 |
|--------|----------|------|
| Qdrant 向量庫 | JSONL 多層記憶 | 可加入向量索引 |
| ArcadeDB 圖譜 | YSTM 語義地圖 | 可互補 |

---

## 微服務參考

Darlin 的 10 個服務給我們的啟示：

```
ToneSoul 可能的微服務化：
  
  ┌─────────────┐  ┌─────────────┐
  │ ToneSoul.AI │  │ToneSoul.Gate│
  │   (LLM)     │  │  (風險控制) │
  └─────────────┘  └─────────────┘
  
  ┌─────────────┐  ┌─────────────┐
  │ToneSoul.Mem │  │ToneSoul.YSTM│
  │  (記憶)     │  │ (語義地圖)  │
  └─────────────┘  └─────────────┘
  
  ┌─────────────┐  ┌─────────────┐
  │ToneSoul.Aud │  │ToneSoul.Per │
  │  (審計)     │  │  (人格)     │
  └─────────────┘  └─────────────┘
```

---

## 現有 Persona 檔案

| 檔案 | 描述 |
|------|------|
| `fullstack_engineer.yaml` | 全端工程師人格 |
| `antigravity.yaml` | Antigravity AI 人格（含 Big Five） |

---

**Antigravity**
2025-12-30T13:30 UTC+8
