# Antigravity Session Context Handoff
> Last Updated: 2026-02-21T14:57+08:00 (Session #764efc41)

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

### Key File Locations
| Component | Path | Public? |
|-----------|------|---------|
| Main Pipeline | `tonesoul/unified_pipeline.py` | ✅ |
| ComputeGate | `tonesoul/gates/compute.py` | ✅ |
| TensionEngine | `tonesoul/tension_engine.py` | ✅ |
| Council Runtime | `tonesoul/council/` | ✅ |
| Adversarial Stub | `tonesoul/memory/adversarial.py` | ✅ (stub only) |
| Memory Consolidator | `tonesoul_evolution/consolidator/core.py` | 🔒 Private |
| Red/Blue Prompts | `tonesoul_evolution/adversarial/prompts.py` | 🔒 Private |
| Adversarial Loop | `tonesoul_evolution/adversarial/loop.py` | 🔒 Private |

### Design Decisions to Remember
1. **Dual-Track Strategy**: Public repo teaches *how* to reason; private repo holds *what* values to enforce. `.gitignore` blocks `tonesoul_evolution/` but some files were `-f` force-committed for version control.
2. **3 Axioms**: Resonance (listen), Commitment (keep promises), Future Binder (bind future actions). These anchor ALL private evolution logic.
3. **ComputeGate Routing**: Free users → local LLM or single cloud agent, never journal-eligible. Premium → full Council + journal write.
4. **Tension as Cost Signal**: Tension score directly maps to API cost routing thresholds.

### Known Technical Debt
- `loop.py` uses `sys.path.insert` hack instead of proper package install
- ComputeGate `PASS_LOCAL` returns hardcoded Chinese string; should integrate real Ollama call
- `BLOCK_RATE_LIMIT` path is defined but never triggered (no rate limiter yet)
- `unified_pipeline.py` has garbled CJK in some older comments from encoding issues

### What Codex Has Done (Background Agent)
- Phase 105-B: Decay Query Top-K Heap optimization (completed, benchmarked)
- `.github/workflows/pytest-ci.yml` CI pipeline
- WFGY Tension Math research (assigned, status unknown)

### Next Priorities (from GLOBAL_TRACKING_BOARD.md)
1. ~~Wire ComputeGate to real Ollama local model for `PASS_LOCAL` route~~ (✅ Completed)
2. Implement rate limiting for `BLOCK_RATE_LIMIT`
3. Connect Adversarial Loop output → Memory Consolidator input (end-to-end pipeline)
4. Council Weight Evolution (adaptive council voting weights)

## Self-Optimization Notes
- When editing `unified_pipeline.py`, use `view_file` with specific line ranges — the file is 1460+ lines
- Always mock `_get_gemini`, `_get_tonebridge`, `_get_council` in integration tests to avoid network hangs
- PowerShell `&&` operator fails silently — use `;` instead for chaining commands
- The `.venv\Scripts\pytest` path is required; global `pytest` is not installed
