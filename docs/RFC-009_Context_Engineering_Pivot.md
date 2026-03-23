# RFC-009: Context Engineering Pivot（脈絡工程轉向）

> Purpose: approved RFC that documents the architecture pivot from older council-first framing toward context-engineering-centered runtime design.
> Last Updated: 2026-03-23

**版本**: v1.0
**日期**: 2026-02-27
**狀態**: Approved
**繼承**: 取代 `ARCHITECTURE_CONVERGENCE_PLAN.md` Phase 100A-D

---

## 1. 定位轉變聲明

ToneSoul 的差異化**不再是** Council 投票機制。

多代理投票在 2024-2025 是護城河，但到 2026 已被 Grok 4.2、Gemini 2.5 等模型的原生推理能力追平。模型自身已具備多角度思考的能力，不需要外部框架來「強迫」多視角審議。

### 新定位

> **ToneSoul 的核心價值是脈絡工程（Context Engineering）。**
>
> 把正確的工程脈絡（張力、承諾、記憶、斷裂偵測）注入 AI 的上下文，
> 讓 AI **自然**地推理到更深的層次 — 不是模擬思考，而是讓思考真正發生。

Council 保留為品質閘門，但不再是主打。

---

## 2. 脈絡工程四支柱

### 2.1 TensionEngine（張力感知）

- **路徑**: `tonesoul/tension_engine.py`
- **公式**: `T = W × (E × D)`
- **4 信號融合**: semantic_delta, text_tension, cognitive_friction, entropy
- **作用**: 讓 AI 知道自己的回應和意圖之間有多少摩擦

### 2.2 SelfCommitStack + RuptureDetector（承諾追蹤 + 斷裂偵測）

- **路徑**: `tonesoul/unified_pipeline.py` 內部
- **作用**: 追蹤 AI 做過的承諾，偵測是否發生斷裂（口是心非）
- **工程效果**: AI 能意識到自己前後矛盾

### 2.3 Memory / Hippocampus（記憶衰減 + 混合 RAG）

- **路徑**: `tonesoul/memory/soul_db.py`, `tonesoul/memory/hippocampus.py`
- **作用**: 三層記憶（factual / experiential / working）具衰減機制
- **工程效果**: AI 擁有持續的脈絡，而非每次從零開始

### 2.4 VisualChain + SemanticGraph（語義場記憶）

- **路徑**: `tonesoul/unified_pipeline.py` 內部
- **作用**: 語義主題跨對話持續跟蹤
- **工程效果**: AI 知道「我們之前聊到哪裡了」

---

## 3. Council 降級為品質閘門

### 前端呈現：維持 3 人議會

用戶體驗穩定。前端繼續呈現 Philosopher / Engineer / Guardian 的三角結構。

### 後端實作：5 Perspectives

| Perspective | 角色 | 模式 |
|-------------|------|------|
| Guardian | 安全 | Rules / LLM / Ollama |
| Analyst | 事實 | Rules / LLM / Ollama |
| Critic | 批判 | Rules / LLM / Ollama |
| Advocate | 用戶 | Rules / LLM / Ollama |
| Axiomatic | 哲學 VTP | Rules / LLM / Ollama |

Council 的職責從「驅動思考」降級為「品質把關」。

---

## 4. 部署現況

| 平台 | 用途 | 狀態 |
|------|------|------|
| **Vercel** | Full-Stack（前端 + Python API） | ✅ 運行中 |
| **Render** | ~~Python 後端~~ | ❌ 免費帳戶已鎖定部署 |

---

## 5. 舊 Phase 100A-D 繼承表

| 舊 Phase | 內容 | 本 RFC 處置 |
|----------|------|------------|
| 100A | 協議定錨（Trinket Spec） | **保留** — Context Engineering 就是 Trinket 的工程化版本 |
| 100B | Runtime 接線（dispatcher A/B/C） | **重新解讀** — A/B/C 改為 TensionEngine 的 SemanticZone |
| 100C | YSS Wrapper shared schema | **保留** — 已建立 `tonesoul/pipeline_context.py` |
| 100D | 多人格能力升級 | **廢棄** — 不再追求更多人格，轉向更好的脈絡 |

---

## 6. 不可變公理

- `AXIOMS.json` 不可修改
- 7 條鐵律（AI_CONTINUITY_PROTOCOL.md）不可修改（用語已對齊）
- 前端 3 人議會呈現不可修改（穩定的用戶體驗）
