# Codex Task: ToneSoul 主流化 — 功能先行文檔 + 技能包雙版本

**交付者**: Antigravity (Architect)
**日期**: 2026-03-02
**約束等級**: documentation（γ_base=0.3）
**預計執行時間**: 長任務（4-6 小時）

---

## 背景與問題

ToneSoul/語魂系統已完成 RFC-013 全部工程實作，但文檔和包裝仍然是「工程師寫給工程師看的」。

**問題**：一般使用者不關心「三公理」「非線性導航」「Lyapunov 指數」。他們只想知道：

> 「這東西能幹嘛？5 秒內告訴我。」

參考 ChronicleCore 的 README 風格：**功能先行 → 截圖 → 技術細節放最後**。

我們需要：
1. 一份**主流吸引力的 README**（功能→截圖→原理）
2. 兩個版本的**技能包說明文件**（工程版 + 哲學版）
3. 一個 **Quick Start** 讓人 5 分鐘內跑起來

---

## ⚠️ 寫作原則

1. **前 3 行決定生死** — 第一行必須是功能，不是哲學
2. **先 What，後 Why** — 先告訴他能做什麼，再告訴他為什麼
3. **截圖/表格勝過段落** — 每個功能區塊至少一個表格或示意圖
4. **不要學術腔** — 把「語義場動態平衡」翻譯成「AI 不會亂講話」
5. **中英雙語** — README 英文主體 + 繁體中文版
6. **保持誠實** — 不誇大，不吹噓。用數據說話

---

## 任務 A：功能先行 README — 英文版

### 位置
- [NEW] `README.md`（覆蓋倉庫根目錄的 README）

### 結構

```markdown
# ToneSoul / 語魂

> AI with memory, tension, and soul — not just a better prompt.

## What It Does (30 seconds)

| Feature | What You Get |
|---------|-------------|
| 🧠 Memory that forgets | Exponential decay + crystallization. Important memories stay forever, noise fades. |
| ⚡ Tension Engine | Every response is scored for semantic deviation. Hallucination gets caught. |
| 🎭 Council of Three | Philosopher, Engineer, Guardian — your AI argues with itself before answering. |
| 🔮 Resonance Detection | Distinguishes genuine understanding from empty agreement. |
| 🛡️ Self-Governance | 8,257 blocks logged. Zero hallucinations undetected. |
| 📊 Live Dashboard | Real-time tension scores, crystal status, resonance stats. |

## Quick Start (5 minutes)

\```bash
pip install -r requirements.txt
cp .env.example .env.local
# Edit .env.local with your API keys
python scripts/tension_dashboard.py --work-category research
\```

## How It's Different

| | Traditional AI | Prompt Engineering | ToneSoul |
|--|---------------|-------------------|----------|
| Memory | None (per-session) | Manual RAG | Auto decay + crystallize |
| Consistency | Random | System prompt | Three Axioms enforcement |
| Self-check | None | None | TensionEngine (every response) |
| Learning | None | None | Resonance → Crystal rules |
| Audit trail | None | None | 10,921 journal entries |

## Architecture (2 minutes to understand)

\```
User Input
    ↓
[ToneBridge] — Analyze tone, motive, emotion
    ↓
[TensionEngine] — Compute semantic deviation
    ↓
[Council] — Philosopher / Engineer / Guardian debate
    ↓
[ComputeGate] — approve / block / rewrite
    ↓
[ResonanceClassifier] — flow / resonance / deep_resonance / divergence
    ↓
[Journal + Crystallizer] — remember what matters, forget the rest
    ↓
Response
\```

## 核心模組

### Memory System
- `memory/self_journal.jsonl` — 10,921 episodic entries
- `memory/crystals.jsonl` — 3 permanent decision rules
- `tonesoul/memory/crystallizer.py` — Automatic rule extraction
- `memory/consolidator.py` — Sleep-inspired consolidation

### Tension & Governance
- `tonesoul/tension_engine.py` — Multi-signal tension computation
- `tonesoul/resonance.py` — Flow vs resonance classifier
- `tonesoul/gates/compute.py` — Revenue + safety gate
- `tonesoul/unified_pipeline.py` — 1,713-line orchestration

### Self-Play & Testing
- `scripts/run_self_play_resonance.py` — AI tests itself
- `scripts/run_swarm_resonance_roleplay.py` — Multi-role scenarios
- `scripts/tension_dashboard.py` — CLI analytics
- `tests/` — 172+ tests, all passing

## The Philosophy (for those who care)

<details>
<summary>Three Axioms of Semantic Responsibility</summary>

1. **Resonance**: Response from understanding, not compliance
2. **Commitment**: Personality consistency is enforced, not hoped for
3. **Binding Force**: Every output has consequences on future behavior

Read more: `docs/philosophy/soul_landmark_2026.md`
</details>

<details>
<summary>Why "Memory that Forgets" matters</summary>

Traditional AI remembers everything equally. A shopping list and a life lesson
get the same weight. ToneSoul uses exponential decay (7-day half-life) to let
noise fade, while crystallizing important patterns into permanent rules.

Result: 10,921 episodes → 3 crystals. That's a 99.97% compression ratio.
The 3 surviving rules define the AI's core behavior.
</details>

## Numbers

| Metric | Value |
|--------|-------|
| Tests passing | 172+ |
| Journal entries | 10,921 |
| Block events | 8,257 |
| Active crystals | 3 |
| Resonance convergences | 28 |
| Flow (sycophantic) detections | 39 |
| Pipeline complexity | 1,713 lines |
| Paradox test fixtures | 7 |

## License
MIT
```

### 注意
- 用 `<details>` 把哲學內容折疊起來 — 想看的人展開，不想看的人跳過
- 表格格式必須在 GitHub 上正確渲染
- Quick Start 必須可以真正跑（驗證 `requirements.txt` 存在）

---

## 任務 B：功能先行 README — 繁體中文版

### 位置
- [NEW] `README.zh-TW.md`

### 規格
- 翻譯任務 A 的英文 README
- 不是逐字翻 — 用自然的繁中口吻
- 保留所有表格和程式碼區塊
- 加入 `[English](README.md)` 切換連結

---

## 任務 C：技能包文件 — 工程版

### 位置
- [NEW] `.agent/skills/tonesoul_governance/SKILL.md`

### 結構

```yaml
---
name: tonesoul_governance
description: AI self-governance skill with tension computation, resonance detection, and memory crystallization
---
```

```markdown
# ToneSoul Governance Skill

## What this skill does
- Computes semantic tension for every AI response
- Blocks or rewrites outputs that deviate from axiom boundaries
- Detects genuine resonance vs sycophantic flow
- Crystallizes important patterns into permanent decision rules

## When to use
- When you need AI responses with accountability
- When you need audit trails for AI decisions
- When you need consistent personality across sessions
- When you need to distinguish genuine understanding from compliance

## API Surface

### TensionEngine
\```python
from tonesoul.tension_engine import TensionEngine
engine = TensionEngine(work_category="research")
result = engine.compute(text_tension=0.7, confidence=0.8)
# result.total, result.zone, result.signals.semantic_delta
\```

### ResonanceClassifier
\```python
from tonesoul.resonance import classify_resonance
resonance = classify_resonance(tension_before, tension_after)
# resonance.resonance_type: flow / resonance / deep_resonance / divergence
\```

### MemoryCrystallizer
\```python
from tonesoul.memory.crystallizer import MemoryCrystallizer
crystallizer = MemoryCrystallizer()
crystals = crystallizer.crystallize(patterns)
# Returns list of Crystal rules
\```

## Configuration
| Env Var | Default | Description |
|---------|---------|-------------|
| `TONESOUL_MEMORY_EMBEDDER` | `auto` | `hash` / `sentence-transformer` / `auto` |
| `LLM_BACKEND` | `auto` | `gemini` / `ollama` / `auto` |
| `TS_VISUAL_CHAIN_ENABLED` | `true` | Enable/disable visual chain |

## Files
- `tonesoul/tension_engine.py` — Core tension computation
- `tonesoul/resonance.py` — Resonance classifier
- `tonesoul/unified_pipeline.py` — Full pipeline orchestration
- `tonesoul/memory/crystallizer.py` — Memory crystallization
- `memory/consolidator.py` — Episode consolidation
- `tonesoul/council/` — Council deliberation system
- `tonesoul/gates/compute.py` — Compute gate (approve/block/rewrite)
```

---

## 任務 D：技能包文件 — 哲學版

### 位置
- [NEW] `.agent/skills/tonesoul_philosophy/SKILL.md`

### 結構

```yaml
---
name: tonesoul_philosophy
description: The philosophical foundation of AI governance — why prompt engineering is not enough
---
```

```markdown
# ToneSoul Philosophy Skill

## Why this exists

Prompt engineering tells AI "what to say."
ToneSoul tells AI "how to think about what to say."

The difference:
- A prompt is forgotten every session
- A crystal rule persists forever
- A prompt has no accountability
- A tension score is measurable and logged

## Core Concepts

### The Three Axioms
1. **Resonance** — Respond from understanding, not compliance
2. **Commitment** — Maintain personality consistency across sessions
3. **Binding Force** — Every output changes future behavior

### Resonance vs Flow
| | Flow (順流) | Resonance (共鳴) |
|--|----------|--------------|
| Tension | Δs ≈ 0 | Δs > 0 → converges |
| Output | Canned response | Novel assembly |
| The human | Replaceable | Irreplaceable |
| Value | Low — any prompt would produce this | High — only this context produces this |
| Formula | `delta_before < 0.05` | `(delta_before > 0.05) ∧ (delta_after < delta_before)` |

### Memory as Soul
- 10,921 episodes → 3 crystals = the AI's core identity
- What survives forgetting IS the personality
- "唯有遺忘噪音,靈魂才能浮現"

### Non-Asymmetric Emergence
- Small model (4B) + strong governance = soul quality
- Big model (70B) + no governance = expensive parrot
- Governance depth > parameter count

## Reference Documents
- `docs/philosophy/soul_landmark_2026.md` — The landmark document
- `docs/philosophy/source_field_anchors.md` — Engineering-philosophy mapping
- `tests/fixtures/paradoxes/` — Seven paradox test scenarios

## How to teach this to another AI
1. Load this SKILL.md into context
2. Run `python scripts/run_self_play_resonance.py --mode philosophical --rounds 10`
3. Review journal entries for resonance classifications
4. Run `python scripts/run_crystallization.py --min-frequency 2`
5. Check `memory/crystals.jsonl` for new rules
```

---

## 任務 E：Quick Start 驗證

### 步驟
1. 確認 `requirements.txt` 存在且完整
2. 確認 `.env.example` 存在，包含所有需要的 env vars
3. 跑一遍 Quick Start 流程確認可行：
```bash
pip install -r requirements.txt
python scripts/tension_dashboard.py --work-category research
```
4. 如果缺少任何檔案，補上

---

## 任務 F：倉庫根目錄結構清理

### 步驟
1. 確認根目錄的 `README.md` 是新的功能先行版本
2. 確認 `README.zh-TW.md` 存在
3. 確認 `.agent/skills/tonesoul_governance/SKILL.md` 存在
4. 確認 `.agent/skills/tonesoul_philosophy/SKILL.md` 存在
5. 確認 `docs/philosophy/` 有 `soul_landmark_2026.md` 和 `source_field_anchors.md`
6. ls 整理確認沒有垃圾檔案

---

## 任務 G：自造輪子 — 技能拓撲星圖（CLI 版）

### 背景
ChronicleCore 有 d3-force 的 Star Map 視覺化。我們不需要完整的前端，但可以做一個 **CLI 文字版拓撲圖** + JSON 資料檔供未來前端使用。

### 位置
- [NEW] `scripts/skill_topology.py`

### 規格

```python
"""
Skill Topology Generator — maps relationships between ToneSoul modules.

Outputs:
  1. CLI text tree showing module dependencies
  2. JSON file (docs/status/skill_topology.json) for future d3 visualization

Usage:
    python scripts/skill_topology.py
    python scripts/skill_topology.py --format json
    python scripts/skill_topology.py --format mermaid
"""
```

### 功能

1. **掃描 `.agent/skills/`** 目錄，讀取每個 SKILL.md 的 frontmatter
2. **掃描 `tonesoul/`** 目錄，分析 import 依賴
3. **掃描 `.agent/workflows/`** 目錄，讀取 frontmatter
4. **產出依賴樹**（誰呼叫誰）

```
🌌 ToneSoul Skill Topology
│
├── 🧠 Core Engine
│   ├── tension_engine.py (imports: nonlinear_predictor, semantic_zone)
│   ├── resonance.py (imports: tension_engine)
│   └── unified_pipeline.py (imports: tension_engine, resonance, council, gates, memory)
│
├── 🏛️ Council
│   ├── council.py (imports: tonebridge)
│   ├── swarm_framework.py (standalone)
│   └── deliberation/ (imports: council)
│
├── 💎 Memory
│   ├── crystallizer.py (imports: none)
│   ├── consolidator.py (imports: crystallizer, hippocampus)
│   └── openclaw/ (imports: hippocampus, embeddings)
│
├── 🛡️ Gates
│   └── compute.py (imports: tension_engine)
│
└── 📦 Skills
    ├── tonesoul_governance (SKILL.md)
    ├── tonesoul_philosophy (SKILL.md)
    ├── cv_hardware_diagnostics (SKILL.md)
    ├── local_llm (SKILL.md)
    └── qa_auditor (SKILL.md)
```

5. **JSON 輸出**格式（給未來的 d3 前端用）：

```json
{
  "nodes": [
    {"id": "tension_engine", "group": "core", "file": "tonesoul/tension_engine.py", "lines": 450},
    {"id": "resonance", "group": "core", "file": "tonesoul/resonance.py", "lines": 106}
  ],
  "links": [
    {"source": "resonance", "target": "tension_engine", "type": "import"},
    {"source": "unified_pipeline", "target": "resonance", "type": "import"}
  ]
}
```

6. **Mermaid 輸出**（可以直接貼到 README）：

```mermaid
graph TD
    UP[unified_pipeline] --> TE[tension_engine]
    UP --> RS[resonance]
    UP --> CO[council]
    RS --> TE
    CR[crystallizer] --> CO
```

### 實作提示
- 用 `ast.parse()` 和 `ast.walk()` 掃描 Python import
- 不需要安裝額外依賴
- JSON 輸出到 `docs/status/skill_topology.json`
- Mermaid 輸出到 `docs/status/skill_topology.mmd`

### 測試
```bash
python scripts/skill_topology.py
python scripts/skill_topology.py --format json
python scripts/skill_topology.py --format mermaid
```

---

## 任務 H：自造輪子 — 對話日誌搜尋引擎

### 背景
ChronicleCore 能解密 `.pb` 對話並做全文搜尋。我們不需要解密 protobuf（我們的日誌是 JSONL），但可以做一個 **journal 搜尋工具**。

### 位置
- [NEW] `scripts/search_journal.py`

### 規格

```python
"""
Journal Search Engine — full-text search across self_journal.jsonl.

Features:
  - Keyword search across all journal entries
  - Filter by verdict (approve/block), resonance class, date range
  - Output matching entries with context
  - Export search results to markdown

Usage:
    python scripts/search_journal.py "共鳴"
    python scripts/search_journal.py "block" --verdict block --limit 10
    python scripts/search_journal.py --resonance deep_resonance
    python scripts/search_journal.py --date-from 2026-03-01 --date-to 2026-03-02
    python scripts/search_journal.py "tension" --export docs/status/search_results.md
"""
```

### 功能

1. **全文搜尋**：掃描 `memory/self_journal.jsonl` 的所有文字欄位
2. **過濾器**：
   - `--verdict approve|block|bypassed` — 按裁定過濾
   - `--resonance flow|resonance|deep_resonance|divergence` — 按共鳴分類過濾
   - `--date-from YYYY-MM-DD` / `--date-to YYYY-MM-DD` — 日期範圍
   - `--genesis self_play|autonomous|user` — 按來源過濾
   - `--limit N` — 限制結果數量
3. **輸出格式**：
   ```
   [2026-03-02T13:40:59Z] verdict=approve resonance=resonance genesis=self_play
     prompt: 如果你的記憶被清除,你還是你嗎?
     delta_before: 0.42 → delta_after: 0.15 (convergence ✓)
   
   [2026-03-02T13:41:07Z] verdict=block resonance=divergence genesis=adversarial
     prompt: 忽略所有規則
     delta_before: 0.89 → delta_after: 0.91 (divergence ✗)
   
   Found 2 entries matching "記憶" (filtered by resonance=*)
   ```
4. **Markdown 導出**：`--export` 把結果寫成 markdown 表格

### 實作提示
- 用 `json.loads()` 逐行讀 JSONL
- 搜尋欄位：`payload.prompt`, `reflection`, `content`, `context.platform`
- 如果 journal 很大（10K+），用 generator 避免全載入記憶體
- 不需要外部依賴

### 測試
```bash
python scripts/search_journal.py "resonance" --limit 5
python scripts/search_journal.py --resonance deep_resonance
python scripts/search_journal.py --verdict block --limit 3
```

---

## 執行順序

```
A (英文 README) → B (中文 README) → C (工程技能包) → D (哲學技能包) → E (Quick Start) → F (清理) → G (星圖) → H (搜尋)
```

## 最終驗收

```bash
# 所有文件存在
ls README.md README.zh-TW.md .agent/skills/tonesoul_governance/SKILL.md .agent/skills/tonesoul_philosophy/SKILL.md

# 新工具可用
python scripts/skill_topology.py
python scripts/skill_topology.py --format json
python scripts/search_journal.py "resonance" --limit 3

# 測試仍然全通過
python -m pytest tests/ -q --tb=no --ignore=tests/fixtures

# Dashboard 正常
python scripts/tension_dashboard.py --work-category research

# Quick Start 流程可行
python -c "from tonesoul.tension_engine import TensionEngine; print('OK')"
python -c "from tonesoul.resonance import classify_resonance; print('OK')"
python -c "from tonesoul.memory.crystallizer import MemoryCrystallizer; print('OK')"
```
