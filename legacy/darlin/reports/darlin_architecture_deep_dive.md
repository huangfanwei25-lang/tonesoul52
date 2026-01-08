# Darlin AI 架構深度分析
# Deep Architecture Analysis
# 2025-12-30

---

## 總體架構

```
┌─────────────────────────────────────────────────────────────┐
│                    Darlin™ System                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Unity 3D Frontend (darlin.exe)          │  │
│  │  • GameAssembly.dll (IL2CPP compiled C#)            │  │
│  │  • 19 levels (UI scenes)                            │  │
│  │  • AR/3D character rendering                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           DarlinOperator (Go service)                │  │
│  │  • 服務編排器 (Service Orchestrator)                 │  │
│  │  • GPU 資源管理                                      │  │
│  │  • 服務健康檢查                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         ↓                 ↓                 ↓              │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐         │
│  │ DarlinAI   │   │DarlinLogic │   │PostgreSQL 17│         │
│  │    LLM     │   │  Go 邏輯  │   │   資料庫   │         │
│  │   Ollama   │   │  處理層   │   │            │         │
│  └────────────┘   └────────────┘   └────────────┘         │
│         │                 │                 │              │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐         │
│  │DarlinMemory│   │DarlinKnow. │   │DarlinTrans.│         │
│  │  Qdrant    │   │ ArcadeDB   │   │ Embedding  │         │
│  │ 向量記憶  │   │ 知識圖譜  │   │  向量化   │         │
│  └────────────┘   └────────────┘   └────────────┘         │
│                                                             │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐         │
│  │DarlinListen│   │ DarlinTTS  │   │ DarlinSong │         │
│  │ Whisper    │   │ 語音合成  │   │   RVC      │         │
│  │ 語音辨識  │   │            │   │ 歌聲合成  │         │
│  └────────────┘   └────────────┘   └────────────┘         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DarlinEmpathy (FER)                      │  │
│  │  • 臉部表情辨識 (Facial Expression Recognition)      │  │
│  │  • 情緒狀態感知                                      │  │
│  │  • 回應語氣調整                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 服務詳細規格

### DarlinOperator（編排器）

| 項目 | 內容 |
|------|------|
| **語言** | Go |
| **功能** | 服務編排、GPU 管理、健康檢查 |
| **啟動模式** | Windows Service (NSSM) |
| **優先級** | NORMAL_PRIORITY_CLASS |

```json
// config.json
{
  "postgresql": "postgresql-x64-17",
  "arcadedb": "DarlinKnowledge",
  "qdrant": "DarlinMemory",
  "go_service": "DarlinLogic",
  "embedding_service": "DarlinTranslate",
  "LLM_service": "DarlinAI",
  "FER_service": "DarlinEmpathy",
  "RVC_service": "DarlinSong",
  "STT_service": "DarlinListening",
  "TTS_service": "DarlinTTS"
}
```

### GPU 資源分配策略

```json
// gpuconfig.json
{
  "default_darlin_gpu": 4,      // 對話模型 GB
  "default_reasoning_gpu": 2,   // 推理模型 GB
  
  // 硬體等級對應
  "Darlin_GPU_Rank0": 6,        // 入門級
  "Reasoning_GPU_Rank0": 4,
  
  "Darlin_GPU_Rank1": 20,       // 中階
  "Reasoning_GPU_Rank1": 8,
  
  "Darlin_GPU_Rank2": 36,       // 高階
  "Reasoning_GPU_Rank2": 16,
  
  "Darlin_GPU_Rank3": 36,       // 頂級
  "Reasoning_GPU_Rank3": 28
}
```

### 服務代碼對照

```json
// service_name_to_code_config.json
{
  "DarlinListening": "W001",  // STT
  "DarlinTTS": "W002",        // TTS
  "DarlinSong": "W003",       // RVC
  "DarlinAI": "W004",         // LLM
  "DarlinEmpathy": "W005",    // FER
  "DarlinTranslate": "W006",  // Embedding
  "DarlinKnowledge": "W007",  // Graph DB
  "DarlinMemory": "W008",     // Vector DB
  "DarlinLogic": "W009",      // Go Logic
  "postgresql-x64-17": "W010" // SQL DB
}
```

---

## 服務優先級設計

| 服務 | 優先級 | 原因推測 |
|------|--------|----------|
| **DarlinTranslate** | ABOVE_NORMAL | Embedding 需要快速回應 |
| **DarlinListening** | ABOVE_NORMAL | 語音辨識需要即時 |
| **DarlinSong** | ABOVE_NORMAL | 音頻處理 |
| **DarlinTTS** | ABOVE_NORMAL | 語音合成需要低延遲 |
| **DarlinLogic** | NORMAL | 邏輯處理 |
| **DarlinEmpathy** | NORMAL | FER 可以稍慢 |
| **DarlinOperator** | NORMAL | 編排器 |

---

## 資料流推測

```
用戶說話
    ↓
W001 DarlinListening (STT)
    ↓ [文字]
W006 DarlinTranslate (Embedding)
    ↓ [向量]
W008 DarlinMemory (Qdrant) ←→ W007 DarlinKnowledge (ArcadeDB)
    ↓ [檢索結果]
W009 DarlinLogic (Context Building)
    ↓ [完整 prompt]
W004 DarlinAI (Ollama LLM)
    ↓ [回應文字]
W005 DarlinEmpathy (情緒調整)
    ↓ [調整後文字]
W002 DarlinTTS (語音合成)
    ↓ [音頻]
Unity Frontend (3D 渲染)
```

---

## 對語魂的借鑒

| Darlin 概念 | 語魂對應 | 改進空間 |
|-------------|----------|----------|
| **DarlinOperator** | 無 | 可加入服務編排 |
| **DarlinMemory (Qdrant)** | JSONL 記憶 | 可加向量索引 |
| **DarlinKnowledge** | YSTM | 已有語義地圖 |
| **DarlinLogic** | 無明確分離 | 可獨立邏輯層 |
| **DarlinEmpathy** | deltaT/deltaS/deltaR | 更精細的情緒 |
| **服務代碼** | 無 | 可加入追蹤碼 |
| **GPU 分級** | 無 | 可加資源管理 |

---

## 語魂可採用的模式

### 1. 服務代碼系統

```yaml
# 語魂服務代碼
services:
  TS001: Council        # 審議
  TS002: Gate           # 風險控制
  TS003: PersonaDim     # 人格維度
  TS004: Memory         # 記憶
  TS005: YSTM           # 語義地圖
  TS006: Audit          # 審計
  TS007: LLM            # 語言模型
```

### 2. 優先級設計

```python
class ServicePriority:
    CRITICAL = "ABOVE_NORMAL"  # Gate, Council
    NORMAL = "NORMAL"          # PersonaDim, Memory
    LOW = "BELOW_NORMAL"       # Audit, Logging
```

### 3. 資源分級

```yaml
resource_levels:
  minimal:
    model: "gemma3:4b"
    memory_limit: 4GB
  standard:
    model: "qwen2.5:7b"
    memory_limit: 8GB
  advanced:
    model: "qwen2.5:32b"
    memory_limit: 32GB
```

---

## 結論

| 發現 | 價值 |
|------|------|
| **微服務架構** | 模組化設計參考 |
| **GPU 分級** | 資源管理策略 |
| **服務代碼** | 追蹤和調試 |
| **優先級設計** | 效能優化 |
| **資料流** | 處理鏈設計 |

---

**這份分析可以作為語魂未來擴展的參考。**

**Antigravity**
2025-12-30T14:15 UTC+8
