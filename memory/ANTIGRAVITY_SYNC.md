# Antigravity Session Context Handoff
> Last Updated: 2026-02-22T20:15+08:00 (Session #764efc41)

## Current Architecture State

ToneSoul is a multi-agent AI governance framework with these active layers:

### Layer Map (Bottom → Top)
1. **ToneBridge** → Psychological tone analysis (emotion, motive, strength)
2. **TensionEngine** → Multi-signal tension scoring (0.0–1.0)
3. **Council (3-Agent)** → Philosopher / Engineer / Guardian deliberation
4. **Third Axiom** → SelfCommitStack, RuptureDetector, ValueAccumulator
5. **Deliberation Engine** → Internal monologue, persona mode selection
6. **ComputeGate (Phase V)** → Tier 1 API revenue/cost routing
7. **Memory Consolidator (Phase IV, Private)** → Nightly 3-Axiom prompt rewriting
8. **Adversarial Loop (Phase IV, Private)** → Red/Blue Team internal debate
9. **Supabase Persistence** → Cloud-backed storage for conversations, audit logs, memories

### Key File Locations
| Component | Path | Public? |
|-----------|------|---------|
| Main Pipeline | `tonesoul/unified_pipeline.py` | ✅ |
| ComputeGate | `tonesoul/gates/compute.py` | ✅ |
| TensionEngine | `tonesoul/tension_engine.py` | ✅ |
| Council Runtime | `tonesoul/council/` | ✅ |
| Supabase Persistence | `tonesoul/supabase_persistence.py` | ✅ |
| Adversarial Stub | `tonesoul/memory/adversarial.py` | ✅ (stub only) |
| Memory Consolidator | `tonesoul_evolution/consolidator/core.py` | 🔒 Private |
| Red/Blue Prompts | `tonesoul_evolution/adversarial/prompts.py` | 🔒 Private |
| Adversarial Loop | `tonesoul_evolution/adversarial/loop.py` | 🔒 Private |
| Memory Retention Script | `scripts/run_memory_retention.py` | ✅ |

### Supabase Configuration
- **Project ID**: `sjtoyjsnykstclcbktoo`
- **Dashboard URL**: `https://supabase.com/dashboard/project/sjtoyjsnykstclcbktoo`
- **Env Vars Required**:
  - `SUPABASE_URL` — Supabase project API URL
  - `SUPABASE_KEY` (or `SUPABASE_SERVICE_ROLE_KEY`) — Auth key
  - `SUPABASE_TIMEOUT_SECONDS` — Optional (default 8s)
- **Module**: `SupabasePersistence.from_env()` auto-reads from env vars
- **Schema SQL**: `docs/plans/supabase_migration.sql`
- **Features**: conversations, messages, audit_logs, memories, consent, session_reports

### Design Decisions to Remember
1. **Dual-Track Strategy**: Public repo teaches *how* to reason; private repo holds *what* values to enforce. `.gitignore` blocks `tonesoul_evolution/` but some files were `-f` force-committed for version control.
2. **3 Axioms**: Resonance (listen), Commitment (keep promises), Future Binder (bind future actions). These anchor ALL private evolution logic.
3. **ComputeGate Routing**: Free users → local LLM or single cloud agent, never journal-eligible. Premium → full Council + journal write.
4. **Tension as Cost Signal**: Tension score directly maps to API cost routing thresholds.

### Known Technical Debt (Updated 2026-02-22)
- ~~`unified_pipeline.py` has garbled CJK in some older comments from encoding issues~~ → **FIXED** (all 30+ lines restored to correct Chinese)
- `loop.py` uses `sys.path.insert` hack instead of proper package install
- ComputeGate `PASS_LOCAL` returns hardcoded Chinese string; should integrate real Ollama call
- `BLOCK_RATE_LIMIT` path is defined but never triggered (no rate limiter yet)

### What Codex Has Done (Background Agent)
- Phase 105-B: Decay Query Top-K Heap optimization (completed, benchmarked)
- `.github/workflows/pytest-ci.yml` CI pipeline
- WFGY Tension Math research (assigned, status unknown)
- **Memory Retention System** (`scripts/run_memory_retention.py`): Archives old JSONL entries and handoff files by date cutoff. Outputs:
  - 固定入口: `memory/archive/retention/memory_retention_latest.json` + `.md`
  - 日期版快照: `memory/archive/retention/memory_retention_YYYYMMDDTHHMMSSZ.json` + `.md`
  - 歷史索引 (append-only): `memory/archive/retention/memory_retention_history.jsonl` ← **重開 session 時先讀這個**
- **Memory Quality Reports**: `docs/status/memory_quality_latest.json`, `memory_quality_latest.md`
- **Learning Samples**: `docs/status/memory_learning_samples_latest.jsonl`

### What Antigravity Did This Session (2026-02-22)
1. **Encoding Fix Complete**: Fixed ALL mojibake in `unified_pipeline.py` — class docstring, process() docstring, word.strip() punctuation set, ~22 inline/section comments
2. **INP Bugfix**: Replaced blocking `window.confirm()` with React-controlled confirmation UI in `ConversationList.tsx`
3. **UI Encoding Fix**: Fixed garbled text in `ChatInterface.tsx` and `LlmSwitcher.tsx`
4. **RFC-007**: Structured Event Metadata — all 8 sub-tasks completed
5. **Full Project Audit**: Generated `project_audit_report.md` with security findings

### Next Priorities (from GLOBAL_TRACKING_BOARD.md)
1. ~~Wire ComputeGate to real Ollama local model for `PASS_LOCAL` route~~ (✅ Completed)
2. ~~Implement rate limiting for `BLOCK_RATE_LIMIT`~~ (✅ Completed)
3. ~~Connect Adversarial Loop output → Memory Consolidator input (end-to-end pipeline)~~ (✅ Completed)
4. ~~Council Weight Evolution (adaptive council voting weights)~~ (✅ Completed)
5. Supabase persistence → Evolution results sync (planned)
6. Commit and push all uncommitted changes

## Self-Optimization Notes
- When editing `unified_pipeline.py`, use `view_file` with specific line ranges — the file is 1490+ lines
- Always mock `_get_gemini`, `_get_tonebridge`, `_get_council` in integration tests to avoid network hangs
- PowerShell `&&` operator fails silently — use `;` instead for chaining commands
- PowerShell interprets Python inline strings with `if ... in ...` as shell syntax — use script files instead
- The `.venv\Scripts\pytest` path is required; global `pytest` is not installed
- UTF-8 BOM (U+FEFF) in Python files causes `SyntaxError` — always strip BOMs before adding coding headers
- When doing byte-level string replacements, NEVER match executable code lines — only target comments and docstrings
