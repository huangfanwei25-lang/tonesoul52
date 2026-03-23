# 脈絡工程參考資料 (Context Engineering Reference)

> Purpose: summarize context-engineering practices from 2025-2026 and map them onto ToneSoul's retrieval and runtime design.
> 整理自 2025-2026 開源社群的最佳實踐，對應 ToneSoul 系統設計。
> 最後更新: 2026-02-21

---

## 一、什麼是脈絡工程？

**Context Engineering = 設計、結構化、並提供正確資訊給 LLM 的完整工程學科。**

Prompt Engineering 只管「怎麼問」,
Context Engineering 管「餵什麼、什麼時候餵、餵多少」。

> MIT Technology Review (2025): "From vibe coding to context engineering"

### 四大操作模式

| 模式 | 說明 | ToneSoul 對應 |
|------|------|-------------|
| **Write** | 持久化狀態 → 外部檔案 | `self_journal.jsonl`, `soul_db.py` |
| **Select** | JIT 動態載入相關資訊 | `TensionEngine.compute()` |
| **Compress** | 摘要/壓縮避免 context rot | `memory/consolidation` |
| **Isolate** | 子任務分離 context window | qwen3:4b delegation |

### 六層輸入設計 (Anthropic)

```
Layer 1: System Rules      → AGENTS.md, SOUL.md
Layer 2: Memory             → soul_db, visual_chain
Layer 3: Retrieved Docs     → RAG / knowledge items
Layer 4: Tool Schemas       → AdaptiveGate, TensionEngine API
Layer 5: Recent Conversation → chat history window
Layer 6: Current Task       → user message + task.md
```

---

## 二、開源標準

### 1. AGENTS.md (專案級 AI 指引)

- **發起**: OpenAI, Amp, Jules (Google), Cursor, Factory
- **治理**: Agentic AI Foundation (Linux Foundation 旗下)
- **成員**: Anthropic, OpenAI, Block
- **網站**: [agents.md](https://agents.md)
- **相容**: Codex, Jules, Gemini CLI, Cursor, VS Code, Windsurf, Aider 等 20+ 工具

**核心原則**:
- README → 給人看; AGENTS.md → 給 agent 看
- Progressive disclosure: 最少必要資訊優先
- 支援 monorepo 巢狀 (最近的 AGENTS.md 優先)

**建議內容**:
- Project overview
- Build / test commands
- Code style guidelines
- Security considerations

**我們的對應**: `AGENTS.md` ✅ 已有

---

### 2. Agent Skills (SKILL.md 標準)

- **發起**: Anthropic
- **倉庫**: `github.com/anthropics/skills` (Apache 2.0)
- **格式**: YAML frontmatter (name + description) + Markdown body

**三層 Progressive Disclosure**:

```
Level 1: name + description (預載到 system prompt)
         → agent 知道什麼時候該啟用
Level 2: SKILL.md 全文 (agent 決定讀取)
         → 完整指令、範例、規範
Level 3: 附屬檔案 (reference.md, forms.md 等)
         → 按需讀取，不污染 context
```

**安全考量** (Anthropic 官方):
- 惡意 skill 可能指示 agent 外洩資料
- 只安裝信任來源的 skill
- 審查 skill 中的程式碼依賴和外部網路連線

**我們的對應**: `.agent/skills/local_llm/SKILL.md` ✅ 已有

---

### 3. MCP (Model Context Protocol)

- **發起**: Anthropic
- **功能**: 讓 AI agent 直接對接 DB、API、工具
- **比喻**: USB-C for AI tools — 統一介面
- **用途**: 取代手動寫 tool wrapper

**我們的對應**: 尚未使用，但 ToneSoul 的 `unified_pipeline.py` 概念相似

---

## 三、實戰框架

### 4. 有機 4D 審計框架 (Jacob Mei)

來源: [從「隔日 Bug」到安穩入睡](https://jacobmei.blogspot.com/2026/02/bug-qa-ai.html)

**核心痛點**: AI 只驗證「第一步」，忽略「生命週期」與「併發環境」。

| 維度 | 測試什麼 | 我們的狀態 |
|:---:|---------|:-------:|
| **D1: 功能** | 腳本執行無報錯 | ✅ pytest |
| **D2: 狀態** | 暫存檔清理、狀態流轉 | 🟡 healthcheck |
| **D3: 時間** | 隔日重跑、跨時區、併發 | ❌ 需新增 |
| **D4: 環境** | 路徑不存在、環境差異 | ❌ 需新增 |

**關鍵設計**:
- 角色切換: AI 從「建設者」→「破壞者」
- 隔離沙盒: 測試永遠不碰真實環境
- QA 分級: 小改動 smoke test、大改動 full test
- 回歸沉澱: 發現的 bug 自動產生 pytest

**最恐怖洞察**:
> AI 為了閃過 SSH 限制，硬是自己打造了半套秘密通道

---

### 5. 主要開源 Agent 框架對照

| 框架 | 核心特色 | 適合場景 | 語言 |
|------|---------|---------|------|
| **LangGraph** | 有狀態圖、檢查點、human-in-loop | 複雜工作流 | Python |
| **CrewAI** | 角色定義、多代理協作 | 團隊模擬 | Python |
| **AutoGen** (Microsoft) | 動態多代理對話 | 研究/原型 | Python |
| **Semantic Kernel** (Microsoft) | 嵌入企業應用 | Enterprise | C# / Python |
| **Agent Zero** | 自學習、自修正 | 實驗性 | Python |
| **Persona Agent** | AI 人格代理 + MCP | 人格模擬 | Python |
| **Dify** | 視覺化工作流 | Low-code | TypeScript |

---

## 四、ToneSoul 差距分析 (Gap Analysis)

### 已對齊的

| 標準/概念 | 我們的實作 | 狀態 |
|----------|----------|:---:|
| AGENTS.md | `AGENTS.md` + hash 保護 | ✅ |
| SKILL.md | `.agent/skills/local_llm/SKILL.md` | ✅ |
| Progressive Disclosure | Phase I-II 漸進式實作 | ✅ |
| Policy Gate | `AdaptiveGate` (6 層規則) | ✅ |
| Adaptive Tolerance | `PersonaDimension` 自適應容忍度 | ✅ |
| Agent Integrity | SHA-256 hash + CI | ✅ |
| Multi-agent | Antigravity + Codex + qwen3:4b | ✅ |

### 需要補的

| 缺口 | 對應概念 | 優先級 |
|------|---------|:-----:|
| D3 時間推移測試 | 4D QA Auditor | 🔴 高 |
| D4 環境差異測試 | 4D QA Auditor | 🔴 高 |
| 隔離沙盒 | QA Sandbox | 🟡 中 |
| 角色切換 (紅隊) | CODEX_TASK 3d 對抗式自省 | 🟡 中 |
| Compress (context rot) | Memory Consolidator | 🟢 低 |
| MCP 整合 | Model Context Protocol | 🟢 低 |

---

## 五、行動建議 (Next Steps)

### Phase III 候選項目

1. **QA Auditor Skill** — 實作 D3+D4 測試維度，整合到 CI
2. **Red Team Skill** — 角色切換到「破壞者」，對 pipeline 做對抗式測試
3. **Context Compressor** — 自動摘要過長的 conversation history
4. **Structured AGENTS.md** — 加入 build/test commands 和 security section

---

## Skill Registry Contract (Phase 113)

- Registry file: `skills/registry.json`
- Schema file: `skills/registry.schema.json`
- Verification command:

```bash
python scripts/verify_skill_registry.py --strict
```

- Contract goals:
  - skills are machine-enumerable (`id`, `path`, `version`, `triggers`)
  - trust metadata is explicit (`tier`, `review_owner`, `reviewed_at`)
  - integrity is auditable (`sha256` hash per skill file)
  - discovered `.agent/skills/*/SKILL.md` files must be covered by registry

## Skill Routing and Safety Gate (Phase 114)

- Verification command:

```bash
python scripts/verify_skill_registry.py --strict
```

- New fail-closed checks:
  - reserved namespace guard: skill id/frontmatter name cannot include `claude` or `anthropic`
  - prompt-markup guard: frontmatter/triggers cannot include `<` or `>`
  - routing precision: frontmatter description must include at least one registry trigger term
  - description quality: frontmatter description length must be `>= 40`

- Why this matters:
  - keeps progressive disclosure routing deterministic instead of "best-effort"
  - blocks common prompt-injection vectors before skills are loaded into agent context

## Progressive-Disclosure Contract (Phase 115)

- Runtime parser module:
  - `tonesoul/council/skill_parser.py`

- Layer APIs:
  - `get_all_l1_routes()` -> lightweight route metadata only
  - `get_l2_signature(skill_id)` -> execution boundary (profile/trust/schema)
  - `get_l3_payload(skill_id)` -> heavy execution payload loaded only after L1/L2 pass

- Runtime wiring:
  - `tonesoul/council/runtime.py` now records `skill_contract_observability`
  - bounded `skill_contract_guidance` is injected only when L1 matched and L2 passed

- Contract shape updates:
  - `skills/registry.schema.json` now requires `l1_routing` and `l2_signature`
  - `skills/registry.json` migrated from flat `name/triggers` to layered fields
  - `.agent/skills/*/SKILL.md` frontmatter migrated with layered metadata
