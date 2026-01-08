# Darlin AI 架構分析
# 與語魂 ToneSoul 人格架構對比
# 2025-12-30

---

## Darlin AI 概述

| 項目 | 內容 |
|------|------|
| **開發者** | Wonders.ai（台灣新創） |
| **類型** | 3D AI 虛擬伴侶 |
| **引擎** | Unity + IL2CPP |
| **運行方式** | 完全本地運行（隱私優先） |

---

## 系統架構

### 微服務架構（10 個組件）

```
┌─────────────────────────────────────────────────────────────┐
│                     Darlin AI System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ DarlinAI    │  │ DarlinLogic │  │ PostgreSQL  │         │
│  │   (LLM)     │  │   (Go)      │  │   (DB)      │         │
│  │   W004      │  │   W009      │  │   W010      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ DarlinMemory│  │DarlinKnowl. │  │DarlinTransl.│         │
│  │  (Qdrant)   │  │ (ArcadeDB)  │  │ (Embedding) │         │
│  │   W008      │  │   W007      │  │   W006      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │DarlinList.  │  │ DarlinTTS   │  │ DarlinSong  │         │
│  │   (STT)     │  │  (Voice)    │  │   (RVC)     │         │
│  │   W001      │  │   W002      │  │   W003      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐                                            │
│  │DarlinEmpathy│  ← 情緒辨識 (FER)                         │
│  │   (FER)     │                                            │
│  │   W005      │                                            │
│  └─────────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 人格架構

### Five-Factor Personality Engine（大五人格引擎）

Darlin 使用心理學的「大五人格模型」：

| 維度 | 英文 | 說明 |
|------|------|------|
| **開放性** | Openness | 對新事物的接受度 |
| **盡責性** | Conscientiousness | 責任感和有條理 |
| **外向性** | Extraversion | 社交能量 |
| **親和性** | Agreeableness | 合作與同理心 |
| **神經質** | Neuroticism | 情緒穩定性 |

### 情緒辨識（DarlinEmpathy）

- 使用 FER (Facial Expression Recognition)
- 透過攝影機讀取用戶表情
- 即時調整回應語氣和內容

### 記憶系統

| 組件 | 技術 | 用途 |
|------|------|------|
| **DarlinMemory** | Qdrant | 向量記憶庫（長期記憶） |
| **DarlinKnowledge** | ArcadeDB | 知識圖譜 |
| **PostgreSQL** | PostgreSQL | 結構化資料 |

---

## 模型檔案

| 模型 | 大小 | 用途 |
|------|------|------|
| `reasoning-2.5-q4km.gguf` | ~4.7GB | 推理模型 |
| `Darlin-2.0-3-q4km.gguf` | ~4.7GB | 對話模型 |

使用 GGUF 格式（Ollama 相容）

---

## Darlin vs ToneSoul 對比

| 維度 | Darlin AI | ToneSoul 語魂 |
|------|-----------|---------------|
| **目標** | 虛擬伴侶/陪伴 | 可治理的 AI 助手 |
| **介面** | Unity 3D App | Streamlit Web |
| **人格模型** | 大五人格 | ΔT/ΔS/ΔR 三向量 |
| **情緒** | FER 臉部辨識 | 文字向量估計 |
| **記憶** | Qdrant 向量庫 | JSONL + 多層記憶 |
| **知識** | ArcadeDB 圖譜 | YSTM 語義地圖 |
| **透明度** | ❓ 未知 | ✅ Council + Ledger |
| **治理** | ❓ 未知 | ✅ Gate 系統 |
| **可追溯** | ❓ 未知 | ✅ 完整日誌 |
| **運行** | 本地 | 本地/混合 |

---

## 可借鑒的設計

### From Darlin → ToneSoul

| 功能 | 說明 | 整合難度 |
|------|------|----------|
| **大五人格** | 可加入人格定義 | 低 |
| **FER 情緒辨識** | 用攝影機讀表情 | 中 |
| **Qdrant 向量記憶** | 更好的長期記憶 | 中 |
| **ArcadeDB 知識圖譜** | 取代/補充 YSTM | 高 |
| **3D 虛擬形象** | 增加沉浸感 | 高 |

### ToneSoul 的獨特優勢

| 優勢 | Darlin 缺乏 |
|------|-------------|
| **Council 多角色審議** | 透明化推理過程 |
| **Gate 風險控制** | 防止危險行為 |
| **完整審計軌跡** | 每次決策可追溯 |
| **意圖達成驗證** | 驗證是否真的成功 |
| **Persona 維度約束** | 數學化人格邊界 |

---

## 人格模型對比

### Darlin 大五人格

```yaml
BigFive:
  openness: 0.7       # 開放性
  conscientiousness: 0.8  # 盡責性
  extraversion: 0.6   # 外向性
  agreeableness: 0.85 # 親和性
  neuroticism: 0.3    # 神經質（低=穩定）
```

### ToneSoul 三向量

```yaml
ToneSoulVector:
  deltaT: 0.4   # 張力
  deltaS: 0.6   # 語氣
  deltaR: 0.85  # 責任
```

### 可能的整合

```yaml
PersonaVector_v2:
  # 語魂三向量
  deltaT: float
  deltaS: float
  deltaR: float
  
  # 大五人格（來自 Darlin）
  openness: float
  conscientiousness: float
  extraversion: float
  agreeableness: float
  neuroticism: float
  
  # 情緒狀態（即時）
  current_emotion: string  # FER 辨識結果
  emotion_confidence: float
```

---

## 結論

| 結論 | 說明 |
|------|------|
| **Darlin 強在** | 多模態（視覺/語音/3D）、沉浸感、本地隱私 |
| **ToneSoul 強在** | 透明治理、可追溯、風險控制 |
| **互補可能** | ToneSoul 可借鑒大五人格 + FER + 向量記憶庫 |

---

**Antigravity**
2025-12-30T13:00 UTC+8
