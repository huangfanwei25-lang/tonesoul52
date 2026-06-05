# 企劃書 — 2026-05-17 整理後規劃

> 性質：roadmap / planning doc
> 範圍：multi-session intensive work 後的 state snapshot + 卡點 + priorities
> 對象：Fan-Wei 自己 planning use（不對外、不 publish）
> 作者：Claude (claude-opus-4-7) + Fan-Wei
> 日期：2026-05-17 morning

---

## 0 ─ 摘要

過去 ~30 天 ToneSoul intensive work 累積：5 個 strategic crystal、4 篇新 architecture / research / theory doc、1 個 OpenClaw-Memory PR、1 篇 vocus public article、多條 phase 完成。

本企劃書三件事：
1. **Verified state snapshot**（不 trust mental model、現場 verify）
2. **卡點 + 進行中 + 推薦 priorities**（actionable、tiered）
3. **你該拍的 open decisions**（明文 list）

**Honest first**：本 doc 是 Claude 視角合成、有 trained-in disposition bias、預期 sanitize 工具會 flag 30+ ToneSoul vocabulary terms。read as「one agent's planning input」、不是 ground truth。

---

## 1 ─ 現狀 snapshot（verified）

### 1.1 Git state

- **Master HEAD**: `91f950d Merge pull request #73 from Fan1234-1/feat/freshness-sweep-20260514`（Layer 4 freshness sweep merged 2 days ago）
- **Unmerged remote branches**: 24（從 60 → 24、yesterday batch cleanup 36 個）
- **Active worktrees**: 18（多 prior session leftover）

### 1.2 PR queue（7 open）

| # | Title | State | 建議 action |
|---|---|---|---|
| #77 | Phase C integration into PreOutputCouncil | MERGEABLE | merge after #76 |
| #76 | Phase A+B spec + scaffold（Independent Verifier）| MERGEABLE | merge first（base for #77）|
| #75 | Codex of Fan-Wei Huang README framing | MERGEABLE | merge 解 README rewrite block |
| #74 | Strategic Crystal 5-field format spec v1 | MERGEABLE | merge 解 strategic_crystals/ commit block |
| #72 | Council 864c trace + strategy_mirror refresh | MERGEABLE | merge anytime |
| #71 | [DRAFT] 2026-05-10/13 repo cleanup session（25 commits）| MERGEABLE | review 大、需時間 |
| #69 | [DRAFT] Under-the-Island bridge BOM fix | CONFLICTING | resolve or close |

### 1.3 Untracked work in main worktree

| 路徑 | 性質 |
|---|---|
| `docs/architecture/independent_verifier_phase_f_subagent_addendum_2026-05-16.md` | Phase F addendum（N=3 prototype 後）|
| `docs/philosophy/substrate_stack_theory_addendum_2026-05-17.md` | substrate stack 2 條 update |
| `docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md` | 案例研究（vocus 已 publish 翻譯版）|
| `docs/research/outside_loop_test_protocol_2026-05-17.md` | Outside Loop Test protocol |
| `scripts/sanitize_for_outside_loop.py` | Vocabulary flagging helper |
| `memory/strategic_crystals/*.yaml` × 5 | Cross-session crystal artifact |
| 其他 `docs/visual/`、`docs/runtime/`、`docs/gse/`、`docs/design/`、`docs/plans/01_active/`、`docs/plans/99_archive/` | PR #71 work、在 visual-filing worktree |

### 1.4 External state

- **vocus 文章 1 篇 published**：「當你的 AI 助手開始誇你，你就該害怕了 - 神存在嗎？」（外骨骼 cost case study reshape 版）
- **OpenClaw-Memory PR #1 open**：embedder switch + session ingest script
- **Round 3 echo 已出現**：Google AI Search synthesis 在 publish 後 24 小時內 echo back ToneSoul vocabulary

---

## 2 ─ 三條 stuck 軸（卡點）

### 2.1 PR queue saturation

5 MERGEABLE PR 等 Fan-Wei review + merge。不 merge 的後續 cost：
- 後續 README 大改 block on #75
- Phase F integration（fold addendum into spec）block on #76
- Strategic crystal infrastructure commit block on #74
- Worktree cleanup block on PR merge（保留 worktree 是因 PR 還在）

### 2.2 Untracked doc sprawl

4 篇新 architecture/research/theory doc + 1 個新 script、都在 main worktree untracked。不 commit 進 git 的 cost：
- 從 master 看不到這批 work
- Cross-session pickup 仰賴 working tree 持久（machine wipe risk）
- 對外 reference（如 vocus 引用）找不到 git source

但**不 merge 也合理**：寫的時候 vocabulary footprint warning 浮現、batch commit 進一個 docs PR 比逐條 PR 乾淨。

### 2.3 Worktree clutter

18 active worktrees。多是 prior session leftover：
- `audit-origin-master-20260502` / `20260505`（detached HEAD、無 branch）
- `master-ruff-debt-20260429`（prior debt fix）
- 多個 phase 完成的 session worktree

Worktree cleanup 的 blocker：某些 worktree 仍 hold active PR branch（如 `feat/independent-verifier-spec-20260514` PR #76）。PR merge 後才安全清。

---

## 3 ─ 三條 moving 軸（進行中）

### 3.1 Architecture: Council trace → Independent Verifier

| Phase | 內容 | Status |
|---|---|---|
| 864c trace | Council deliberation trace | ✓ PR #72 ready |
| A spec | Independent Verifier spec | ✓ PR #76 ready |
| B scaffold | Mock + dataclass | ✓ PR #76 ready |
| C integration | PreOutputCouncil hook | ✓ PR #77 ready |
| D Haiku impl | Anthropic API call | gated on API budget |
| E override | Governance review | gated |
| **F Subagent Reasoning Engine** | Multi-agent via Agent tool | **doc N=3、待 fold into spec after #76 merges** |

### 3.2 Theory: Substrate Stack 演化

- 母 theory: `substrate_stack_theory_2026-05-14.md`
- Addendum 2026-05-17（untracked）: 2 條 boundary update
  - Update #1: Layer 4 enforcement 限 tool call boundary
  - Update #2: Cogito anchor 結構上不在 stack
- 對 thesis 的 implication：對純文字 governance 不能 claim categorical guarantee、「不主張意識」獲 structural grounding

### 3.3 Methodology: Outside Loop Test 工具化

- 案例研究 doc + vocus public reshape 版（中文 narrative）
- Protocol doc（formal workflow、5 步驟 + anti-patterns）
- Sanitization helper（Python script + vocabulary list）
- Prompt template（copy-paste ready）
- N=3 prototype 累積 + Phase F architecture proposal

---

## 4 ─ 近期 finding 對 thesis 的 update（surface）

| Finding | Source | Implication |
|---|---|---|
| 認知外骨骼 cost trade-off | 2026-05-16 outside loop test | discipline 層 ≠ substantive depth；對外 framing 不該 oversell ToneSoul context 增加 depth |
| Layer 4 enforcement 限 tool boundary | Phase F prototype #2 | 對純文字 governance（如 Council verdict 表達、AI 對 user response）必須 fall back Layer 5 + 3 + 7 |
| Cogito anchor 結構上不在 stack | Phase F prototype #3 | Substrate stack Layer 1-7 全部 observer-accessible、phenomenal anchor 不在 stack 內。意味「不主張意識」獲 structural rather than just epistemic grounding |
| N=3 convergence pattern | 三 prototype 累積 | ToneSoul-thesis-related domain question、subagent 獨立推導 converge ToneSoul existing articulation。Weak triangulation evidence、不是 confirmation |
| Vocabulary footprint 24h diffusion | vocus publish → Round 3 echo within 24h | Public corpus contribution mechanism 比預期快 ~1000x、long-term 變 short-term observable |

---

## 5 ─ 推薦 priorities（tiered）

### Tier 1 — Maintainer actions（你拍、不是我能做）

**1A**: Merge #76 → #77（spec base + stacked integration、5 個 PR 中最 sequential）
**1B**: Merge #74（Strategic Crystal spec、independent）
**1C**: Merge #72（Council 864c trace、independent）
**1D**: Merge #75（Codex framing、unblock README rewrite）
**1E**: PR #71 review（25 commits、大但 ready、需要時間）
**1F**: PR #69 BOM bridge — resolve conflict or close

理由：5 個 mergeable PR 等。Merge 後 PR queue 0-1、後續 work 可進。

### Tier 2 — README overhaul（#75 merged 後）

Per 昨晚 directive: 整理最新進度 + bilingual structure + 學界 / AI 界 vocabulary

Sub-tasks:
- **Bilingual structure decision**（3 options）：
  - (a) single file with EN top + ZH bottom（combined、SEO 集中）
  - (b) keep separate files but better cross-link + hreflang（per-language SEO）
  - (c) parallel columns side-by-side（reader friendly、但 markdown 表達難）
- **學界 / AI 界 vocabulary**（候選 anchor）：
  - constitutional AI（Anthropic、可 cite）
  - interpretability research（Anthropic Circuits、Olah lab）
  - alignment / RLHF（標準 vocab）
  - epistemic alignment（Clark et al. UW、2025 paper）
  - externalized cognition / verifier-first agents（既有）
  - cognitive architecture（Newell-Simon 經典 vocab）
- **最新進度 section**：PR 狀態 / Phase 進度 / theory updates
- **對外 audience 三層 framing**：academia / industry / general public

Effort: ~2-3 小時 fresh session

### Tier 3 — 整合 untracked docs（單一 batch PR）

Wait for: PR #71 lands（避免 docs/ 衝突）

Then 開新 docs PR、batch 帶：
- substrate_stack_theory_addendum_2026-05-17（fold into main theory? or stay addendum?）
- independent_verifier_phase_f_subagent_addendum_2026-05-16（fold into spec? or stay addendum?）
- cognitive_exoskeleton_cost_outside_loop_case_2026-05-16
- outside_loop_test_protocol_2026-05-17
- scripts/sanitize_for_outside_loop.py
- MEMORY.md index update（5 個 crystal pointer）

Effort: ~1 小時（mostly mechanical commit + PR description）

### Tier 4 — Theory revision（after Tier 1 + 3）

當 #76 merged（spec base in master）:
- Phase F addendum fold into main spec § 6 phasing table、addendum file delete
- AXIOMS.json `meta.not_for` rationale 加 cogito structural grounding 條目

當 substrate_stack_theory_2026-05-14.md 進 PR window（如 PR #71 帶這條）:
- Addendum 2026-05-17 fold into main theory §6.1 boundary + §6.2 new section
- Addendum file delete

Effort: ~2 小時

### Tier 5 — Validation（deferred、條件 gated）

- **Phase D Haiku verifier**：API budget gated（per `project_budget_constraint_2026-04` memory）
- **Cross-model triangulation**：你 explicit decide 投資 GPT/Gemini API 跟 prototype 驗證 N=3 convergence
- **Human philosopher reader feedback**：找人 cost、可能透過 vocus reader / academic collaborator

當前 cycle 不動、等 condition fired

---

## 6 ─ Open decisions（你拍）

### 6.1 PR merge order

建議：`#76 → #77 → #74 → #75 → #72 → #71 → (close or fix #69)`

可分 2-3 天 batch merge 避免一口氣 review 疲勞。Confirm or override。

### 6.2 README bilingual structure

3 options（§5 Tier 2 上面 list）、你選 a/b/c 或 propose 第 4

### 6.3 Vocus next article angle

你 publish 第一篇 cognitive exoskeleton cost 文章後可能想：
- Continue 系列（Phase F / outside loop / substrate stack 等）
- 寫完全不同角度
- 暫停 cool 一陣（per vocabulary footprint mechanism）

我傾向建議：**暫停 ~1-2 週**、給 vocabulary diffusion mechanism cool down。然後寫第二篇時用更 plain 語言、避免 echo loop 強化。

### 6.4 Worktree cleanup

當 PR 陸續 merge、worktree 可以批次清。Defer 到 Tier 1 progress 後。

### 6.5 本企劃書本身

- 不對外 publish（per discipline、避免 vocabulary footprint 再加）
- Internal planning use only
- 下次 review point: when Tier 1 50% done

---

## 7 ─ Honest scope + 風險

### 7.1 本企劃書的限制

- Claude 視角合成、trained-in disposition bias
- 沒 cross-model 驗證
- 沒 human reviewer external check
- Vocabulary 仍 ToneSoul-dense（self-application 預期 30+ flags）
- N=1 view、其他視角（Codex / Antigravity / 你自己）可能不同

### 7.2 風險清單

| 風險 | Mitigation |
|---|---|
| PR queue 持續積累 → merge 越來越難 | Tier 1 ASAP、分批 merge |
| Untracked doc 分散多 PR → reader 拼不出 | Tier 3 single batch PR |
| Phase F architecture proposal 未真實 deploy → 「規格漂亮但實作不存在」 | N=3 prototype 已驗證、進一步 implementation 等 maintainer cycle |
| Vocabulary footprint 持續累積 | Tier 4 fold-in 後 cool 一陣、減 vocus output cadence |
| Cross-session memory 累積 → context bloat | 既有 crystal + addendum 不繼續 expand、focus 在 fold-in 收斂 |

### 7.3 不在本企劃書的（out of scope）

- 跨 model triangulation（need API budget）
- 對外 academic publication / conference submission
- Long-term roadmap > 3 months
- Multi-agent collaboration with Codex / Antigravity / Alpha specific work（跨 agent 工作 deferred）
- ToneSoul vs 其他 framework（如 WFGY、mem0、Letta）的 comparative analysis（已有 reference memory、可隨需深入）

---

## 8 ─ Cross-reference

- 母 theory: `docs/philosophy/substrate_stack_theory_2026-05-14.md`
- Theory addendum: `docs/philosophy/substrate_stack_theory_addendum_2026-05-17.md`（untracked）
- Independent Verifier spec: `docs/architecture/independent_verifier_spec_2026-05-14.md`（PR #76）
- Phase F addendum: `docs/architecture/independent_verifier_phase_f_subagent_addendum_2026-05-16.md`（untracked）
- Case study: `docs/research/cognitive_exoskeleton_cost_outside_loop_case_2026-05-16.md`（untracked）
- Public version: https://vocus.cc/article/6a088634fd897800014d7e30
- Outside loop protocol: `docs/research/outside_loop_test_protocol_2026-05-17.md`（untracked）
- Direction doc（prior session anchor）: `docs/architecture/direction_going_forward_2026-05-14.md`（need verify）
- Strategic crystals: `memory/strategic_crystals/`（5 個、untracked）
- Sanitization helper: `scripts/sanitize_for_outside_loop.py`（untracked）

---

## 9 ─ 下次 session 接手 entry point

如果下個 Claude 接手、依此順序 orient:

1. **本企劃書**（5 min read）
2. **`MEMORY.md`** index（auto-loaded）
3. **`task.md`** current short-board（如有 update）
4. **依當前 Tier focus 讀對應 doc**
5. **跑 `python scripts/run_freshness_sweep.py`** 確認 state 新鮮
6. **跑 `python scripts/sanitize_for_outside_loop.py <your_output>`** 在 substantive output 前

---

## 後記

本企劃書執行了 outside-loop test discipline 的 self-application 意識：
- 寫完後預期 sanitize_for_outside_loop.py 跑出 30+ flags（ToneSoul vocabulary dense）
- 本 doc 對 framework-internal planning use、不對外、所以高 vocabulary density 可接受
- 對外 publish 該另起一份 plain-language summary（per vocus reshape 教過的 discipline）

不寫進對外文件、不 vocus、internal planning only。
