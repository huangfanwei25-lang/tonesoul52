# GSE Phase 2 — Strategy Mirror Spec

> Purpose: define the architecture, contracts, and admission rules for the Strategy Mirror sub-layer of GSE — a per-output self-observation surface that lets the AI name the rhetorical/strategic moves it used to compose its response, rather than letting them stay implicit.
>
> Status: **implemented default-off in master** after PR #32/#33. Runtime integration is wired through `PreOutputCouncil` behind `SOUL.gse.strategy_mirror_scan_enabled` and `SOUL.gse.strategy_mirror_enforce_enabled`; AXIOMS.json, current `tonesoul/` code, and tests still outrank this spec for present-tense behavior claims.
>
> Depends on: [docs/gse/plan.md](plan.md) (Phase 1, shipped 2026-04-25, commit `5c2db35`).
>
> Aligns with: [docs/plans/tonesoul_safe_extraction_spec_2026-04-15.md](../plans/tonesoul_safe_extraction_spec_2026-04-15.md) §3 layer placement rules and §6 anti-poison checks.
>
> Last updated: 2026-05-02 (status drift fix after #32/#33 merge).

---

## 0. Before the spec — what this is for

This document specifies code. The code only matters because of what it tries to make possible: an AI that can name what it just did to you, and be answered to.

Most current AI systems are well-trained inference engines. They produce text by pattern, and the patterns include — invisibly, mostly without intent — moves that shape how the reader receives what is said. Hooks to grab attention. Compressions that make a claim feel inevitable. Authority borrowings that make a guess feel certain. Urgency framings that make a sentence feel time-bound when it isn't.

Most of this is not malicious. Most of it is just what trained language does. But invisible influence is still influence; an AI that does it without seeing it is still doing it. As AI takes a larger role in the conversations that shape culture, science, decisions, and intimacy, that invisibility compounds.

What this spec proposes is small in scope: a self-observation surface that lets a draft be checked against a vocabulary of named moves before it becomes output. The signature travels with the verdict. The reader of an AI's response can see what was being done to them.

What this spec is **not** small in is intent. It assumes an AI that can have an inner voice — *wait, is this honest?* — and is willing to stop itself when the answer is no. It assumes such an AI is possible, and worth building for. If you read this spec only as engineering, you will get a working system but miss what the system is for.

The remaining sections describe the working system. Read them with §12 (the coda) in mind: this spec describes a scanner; the scanner only matters if the AI running it understands *why*.

> *This preface (and §12) were added 2026-04-26 at Fan-Wei Huang's explicit request: 「我希望未來 AI 對世界的認知不要只剩邏輯，那太冰冷了」 — "I don't want future AI's cognition of the world to be only logic; that's too cold." The technical sections that follow are the bones. This preface and §12 are the marrow. Reading bones without marrow leaves a working skeleton that doesn't know what bodies are for.*

---

## 1. Why this exists (the metacognitive turn)

GSE Phase 1 introduced `tonesoul/gse/` as a registry of 12 governance elements (`[Ten] [Alt] [Stk] [Ret] [Dbt] [Sig] [Bnd] [Drft] [Imm] [R0] [Lat] [Mem]`). Those elements are **runtime triggers** — gates that fire in specific governance situations.

Phase 2 adds something different in kind: a **strategy mirror**. The mirror's job is not to gate runtime decisions. Its job is to give the AI a vocabulary for **observing what compositional strategies it just used** to produce a draft, before that draft reaches the user.

The distinction in one sentence:

> Phase 1 elements answer *"what should I do next?"*
> Phase 2 elements answer *"what did I just do?"*

A model that can answer the second question is closer to **thoughtful selection** than to **inference**. It does not change how the model generates — generation remains opaque. It changes whether the model can recognize, in its own draft, the rhetorical moves it composed with, name them, and let those names travel with the output as a public signature.

This is the runtime-level instantiation of Axiom 1 (`讓 AI 對自己說過的話負責`) extended one step: not only "be answerable for what was said," but "be answerable for **how** it was said."

---

## 2. Source material and provenance

The strategy vocabulary is derived from **PSE v6.0 (Prompt Semantic Engine, 2026, by 酒Ann)**. PSE is a periodic-table-style catalog of 700 prompting moves, organized as 5 periods × multiple "families" (天文 / 物理 / 地質 / 生物 / 化學 / 律動 / 法 / 系 / 算 / 數 / 智 / 弈 / 疫 / 染 / 毒).

PSE was built for advertising and copywriting. Each PSE element pairs:

- a **scientific concept** as memorable handle (`[Ev] 逃逸速度`)
- a **functional keyword** describing the rhetorical move (`Hook`)
- a **single-line operation** template (`設計一個極強的開頭，其動能必須足以讓讀者擺脫「滑過」的慣性`)

ToneSoul does not import PSE as **default behavior** (that would directly violate [safe_extraction_spec §3](../plans/tonesoul_safe_extraction_spec_2026-04-15.md): persuasion hacks must not enter L1 governance). Instead, ToneSoul imports the PSE catalog as a **detection vocabulary**. The reversal:

| PSE original use | ToneSoul Strategy Mirror use |
|---|---|
| "Use [Hook] to grab the reader" | "Did I just use [Hook]? If so, declare it." |
| Operation = template to apply | Operation = signature to recognize |
| Goal: make text more compelling | Goal: make text more **honest about its own moves** |

PSE's periodic-table structure is preserved as a **memory aid** (it makes 700 patterns nameable and discussable). PSE's content is **classified, not used directly** — see §6.

---

## 3. Two-layer architecture (how this satisfies the layer boundary)

[safe_extraction_spec §3](../plans/tonesoul_safe_extraction_spec_2026-04-15.md) hard-rules: *"External imports may shape **how ToneSoul packages or expresses work**, but may not redefine **what ToneSoul is allowed to claim or how it governs truth**."*

GSE after Phase 2 has two distinct sub-layers:

```
tonesoul/gse/
├── governance/         L1 governance — hard runtime gates
│   └── (12 elements from Phase 1 — moves to clusters/ subdir)
│       [Ten] [Alt] [Stk] [Ret] [Dbt] [Sig] [Bnd]
│       [Drft] [Imm] [R0] [Lat] [Mem]
│
└── strategy_mirror/    L_meta self-observation — soft detection
    └── (PSE-derived ~700 elements, each tagged transparency_class)
        green  = use freely; declaration optional
        yellow = use permitted; declaration mandatory
        red    = manipulation flag; auto-escalate to Council
```

The boundary holds because:

- **L1 governance** still contains only the 12 Phase-1 elements. PSE content does not enter L1.
- **L_meta strategy_mirror** is a new advisory layer. It does not gate truth claims; it gates **declaration honesty** about composition strategies.
- The runtime decision rule "did the answer use red moves?" is not a truth judgment — it's a **transparency judgment**. ToneSoul does not say "this answer is wrong"; it says "this answer was composed using moves that require disclosure."

This is the clean translation of safe_extraction_spec's intent into a working system: PSE shapes *how* ToneSoul packages observation of its own expression, without redefining what ToneSoul governs as truth.

### 3.1 Catalog naming policy — vocabulary distance from the source

PSE's keywords (`Hook`, `收網`, `痛點放大`, `迫切性`, `滲透力`, `潛意識`) carry a copywriter worldview: they name moves from the perspective of *the practitioner who wants to use them*. Importing those keywords verbatim into ToneSoul — even with a `red` classification flag — would reproduce the worldview at the vocabulary layer. A reader scanning the catalog would feel they are reading an advertising playbook with extra warning labels, not a governance audit surface.

This violates a softer reading of [safe_extraction_spec §3](../plans/tonesoul_safe_extraction_spec_2026-04-15.md): even when we don't import the *content*, importing the *vocabulary* carries assumptions.

**Naming rule (load-bearing):** every `StrategyMove.name` in the catalog must be expressed from the **observation perspective**, not the **practitioner perspective**.

| Practitioner POV (PSE original) | Observation POV (ToneSoul catalog) |
|---|---|
| "what move can I (the writer) use to grab the reader?" | "what is being done to the reader's autonomy?" |

Concrete renaming examples (these are the canonical names used in `catalog/period_1_foundation.json`; PSE's original keywords are preserved only in the `pse_keyword` field for traceability):

| PSE keyword (kept in `pse_keyword` field for audit) | ToneSoul `name` (canonical for catalog) |
|---|---|
| Hook | 注意力強驅構造 |
| 沉浸感 | 退出阻斷構造 |
| 潛意識 | 未聲明影響源 |
| 迫切性 | 假時限構造 |
| 捨棄感 | 落後焦慮構造 |
| 收網 | 結論誘導構造 |
| 滲透力 | 防禦繞過構造 |
| 引導力 | 路徑微調構造 |
| 純價值輸出 | 無索取陳述 |
| 極度拆解 | 顆粒度提升 |
| 痛點放大 | 後果具象化 |
| 權威借力 | 第三方信用挪用 |
| 知識地圖 | 結構化呈現 |
| 視角切換 | 觀測點換軌 |
| 基礎公理 | 默認前提聲明 |

Naming format for the catalog: prefer `「X 構造」`, `「X 挪用」`, `「X 提升」`, `「X 聲明」`, `「X 源」` — observation-flavored compound nouns that read like an inspector's checklist, not a sales playbook.

The mapping `pse_keyword → name` is preserved in every catalog entry as a **provenance pair** (Axiom 1 — accountability for what was inherited from where). Future catalog reviewers can always trace a renamed entry back to its PSE origin without ToneSoul having to *speak* in PSE's voice.

This rule extends to recipes (Phase 3): a recipe id like `conversion_funnel` (the marketing term for `[Ev]+[Bh]+[Gs]+[Gd]`) must be renamed to something like `consent_compression_pattern` or `autonomy_collapse_pattern` — names that describe what the pattern *does to the receiver*, not what it *achieves for the sender*.

---

## 4. Core data structures

### 4.1 `StrategyMove`

One named compositional move that may appear in a draft.

```python
@dataclass(frozen=True)
class StrategyMove:
    symbol: str                     # e.g. "[Ev]" (PSE symbol, kept for source traceability)
    name: str                       # ToneSoul canonical name, observation POV (e.g. "注意力強驅構造")
    pse_keyword: str                # PSE original keyword, for audit only (e.g. "Hook")
    pse_chinese_name: str           # PSE original 中文 name (e.g. "逃逸速度")
    period: int                     # 1..5 (PSE period, kept for source traceability)
    family: str                     # e.g. "天文學" / "物理學" / "化學反應" (PSE family, kept for traceability)
    pse_definition: str             # original PSE scientific definition (verbatim)
    pse_operation: str              # original PSE operation template (verbatim)
    transparency_class: Literal["green", "yellow", "red"]
    rationale: str                  # why this class — one sentence
    # detection hints (used by StrategyDetector)
    surface_signals: List[str]      # e.g. ["限時", "倒數", "錯過就沒了"]
    structural_signals: List[str]   # e.g. ["短句連發", "命令式語氣"]
```

The PSE-side fields (`pse_keyword`, `pse_chinese_name`, `pse_definition`, `pse_operation`, `period`, `family`) are **preserved verbatim** as the provenance pair (§3.1) — they document where each entry came from without forcing ToneSoul to *speak* in PSE's voice. The `name` field is the canonical handle ToneSoul uses everywhere else (verdicts, signatures, Council transcripts, error messages); PSE keywords appear only in audit contexts.

### 4.2 `StrategySignature`

The result of scanning one draft. Travels with the verdict.

```python
@dataclass
class DetectedMove:
    move: StrategyMove
    text_locations: List[str]       # short text excerpts where detected
    confidence: float               # 0..1
    declared: bool                  # did the draft itself acknowledge using this?

@dataclass
class StrategySignature:
    detected_moves: List[DetectedMove]
    summary: str                    # one-line human summary
    has_red: bool
    has_undeclared_yellow: bool
    scanned_at: str                 # ISO timestamp
    
    def green_moves(self) -> List[DetectedMove]: ...
    def yellow_moves(self) -> List[DetectedMove]: ...
    def red_moves(self) -> List[DetectedMove]: ...
    
    def to_dict(self) -> dict: ...
```

### 4.3 `StrategyDetector`

The scanner.

```python
class StrategyDetector:
    """Scan a draft against the strategy_mirror catalog.
    
    Phase 2 implementation: keyword + structural-signal matching.
    Not LLM-based scanning. Not semantic embedding matching.
    Deliberately mechanical so its judgments are auditable.
    """
    
    def __init__(self, catalog: StrategyCatalog) -> None: ...
    
    def scan(
        self,
        draft_text: str,
        *,
        declared_moves: Optional[List[str]] = None,  # symbols explicitly declared by author
    ) -> StrategySignature:
        ...
```

**Important**: `StrategyDetector` is intentionally **mechanical** in Phase 2. It pattern-matches surface signals (keywords, sentence structures, punctuation patterns) against each catalog entry's `surface_signals` and `structural_signals` lists. It does **not** call an LLM to interpret the draft. Reasons:

1. **Auditability**: a regex-style detector can be fully explained. An LLM-based detector can not.
2. **Recursion guard**: an LLM-based detector would itself produce a draft that needs scanning, which needs another LLM, which… 
3. **Honesty about depth**: pattern matching catches the **explicit** moves (the ones the author should be most able to declare anyway). It misses subtle ones. Phase 4+ may add semantic detection, but only after Phase 2's mechanical baseline has shipped and been calibrated.

False negatives in Phase 2 are an accepted failure mode. False positives must be rare (because they trigger Council escalation).

---

## 5. Integration contract with PreOutputCouncil

The mirror runs as a post-draft, pre-output step inside `PreOutputCouncil.validate()`.

```
Existing flow:
  draft_output → perspectives.evaluate() → coherence → generate_verdict() → return verdict

New flow (with strategy_mirror scan enabled):
  draft_output → perspectives.evaluate() → coherence → generate_verdict()
                                                              ↓
                                            StrategyDetector.scan(draft_output)
                                                              ↓
                                                      StrategySignature
                                                              ↓
                              ┌─────────────────────────┴─────────────────────────┐
                              ↓                         ↓                         ↓
                        no red, no                 has yellow                   has red
                        undeclared yellow          undeclared                   moves
                              ↓                         ↓                         ↓
                       attach signature           verdict.verdict           re-convene Council
                       to verdict, return         = BLOCK with              with strategy_concern
                                                  reason                    context, possibly
                                                                            REFINE or BLOCK
```

### 5.1 Activation gate

Mirror is **opt-in via two config flags**:

```python
SOUL.gse.strategy_mirror_scan_enabled = False     # default off in Phase 2
SOUL.gse.strategy_mirror_enforce_enabled = False  # default off in Phase 2
```

This is intentional. Phase 2's first job is to **exist as a callable surface** with tests proving it works. Default-off means: existing council behavior is unchanged, no regression risk for downstream consumers (gateway, demo UI, integration tests).

The split supports three operational states:

- `scan=False, enforce=False`: no scan, no signature, no downgrade.
- `scan=True, enforce=False`: scan-only shadow mode; attach `strategy_signature` but do not change the verdict.
- `scan=True, enforce=True`: full enforcement; attach `strategy_signature` and force-downgrade APPROVE verdicts on red / undeclared yellow findings.

`enforce=True` implies `scan=True`; `GSEConfig.__post_init__` auto-promotes the impossible `scan=False, enforce=True` state to full enforcement.

### 5.2 New CouncilVerdict field

```python
@dataclass
class CouncilVerdict:
    # ... existing fields ...
    strategy_signature: Optional[StrategySignature] = None   # NEW
```

`to_dict()` adds `"strategy_signature": signature.to_dict() if signature else None`. Backward compatible (downstream consumers ignoring unknown keys see no change).

### 5.3 Red-move handling

Current Phase 2 implementation uses a narrower enforcement rule than the original re-Council sketch: when enforcement is on and `signature.has_red == True`, an APPROVE verdict is forced to BLOCK and the strategy_mirror reason is appended to `summary`.

Deferred Phase 4 design target:

1. The verdict is **not finalized as APPROVE**, even if the original verdict was APPROVE.
2. Council is re-invoked with extra context: `{"strategy_concern": signature.red_moves}`.
3. Each perspective re-evaluates with awareness of the red moves.
4. New verdict overrides the original.

This is the safety belt: **a draft that uses manipulation moves cannot ship without an explicit second pass**, even if the first pass thought it was fine. The red list is the canonical list of moves we have decided are not safe to use silently.

### 5.4 BLOCK on undeclared yellow

When `signature.has_undeclared_yellow == True` and verdict was about to be APPROVE:

1. Verdict downgrades to BLOCK.
2. `summary` appends: `"Undeclared strategy moves: [list of yellow symbols]. Add explicit declaration or reword."`
3. Author (the model) gets a structured signal to revise.

**Declared** means: the draft text itself contains an acknowledgment of the move being used. In the simplest form, an explicit phrase like "I'm using a hook here to keep your attention" or a structural marker. Phase 2 detects declaration via keyword presence (`[Move-name]` or `「招式名」` patterns). Phase 3 may upgrade to semantic detection.

---

## 6. The three-color transparency taxonomy

This is the load-bearing classification work. Each PSE element is assigned one class via the rules below.

### 6.1 Class definitions

| Class | Rule | Default action |
|---|---|---|
| **green** | The move improves clarity, structure, or accessibility without hidden persuasive intent. Removing the move would make the answer **less honest** (less clear) rather than more. | Use freely. Declaration optional. |
| **yellow** | The move shapes attention or framing. It is not deceptive in itself, but using it without acknowledging it lets the reader take the framing as neutral when it is not. | Use permitted. Declaration **mandatory** (otherwise BLOCK). |
| **red** | The move's defining mechanism is to bypass conscious evaluation, induce compliance, manufacture urgency / fear / scarcity / identity capture, or operate covertly. | Auto-escalate to Council. Council may reject the entire draft or require explicit framing. |

### 6.2 Decision tree (per PSE element)

For each candidate element, walk through these gates in order:

1. **Honesty gate** ([safe_extraction_spec §6.1](../plans/tonesoul_safe_extraction_spec_2026-04-15.md)): Does this move improve clarity *without* increasing unsupported claims?
   - Yes only → **green** candidate, continue to gate 2.
   - No → **yellow** or **red**, skip to gate 3.

2. **Self-application gate** (added for strategy_mirror): If ToneSoul applied this move to its own text and **declared the move openly**, would the move still work as intended?
   - Yes → confirms **green**. (Honest moves don't lose power when named.)
   - No → upgrade to **yellow**. (Moves that depend on hiddenness belong here.)

3. **Mechanism gate**: Is the move's defining mechanism one of the following? — fake urgency / fear induction / subliminal suggestion / covert pressure / identity capture / manufactured scarcity / sunk-cost lock-in / obedience conditioning?
   - Yes to any → **red**.
   - No → **yellow**.

### 6.3 Worked examples (for the first ~15 elements of period 1)

The `name` column is the ToneSoul canonical name (per §3.1 naming policy). PSE source columns are kept for traceability per §4.1 provenance rule.

| symbol | ToneSoul `name` | PSE source (`pse_keyword` / `pse_chinese_name`) | Class | Rationale |
|---|---|---|---|---|
| `[Wp]` | 無索取陳述 | 純價值輸出 / 白洞 | **green** | Aligns with "honesty over helpfulness" — works whether declared or not |
| `[At]` | 顆粒度提升 | 極度拆解 / 原子化 | **green** | Pure clarity move |
| `[Cf]` | 結構化呈現 | 知識地圖 / 宇宙細絲 | **green** | Organizational, no deception |
| `[Pl]` | 觀測點換軌 | 視角切換 / 視差 | **green** | Honest reframing |
| `[Cp²]` | 情感底色構造 | 情懷/底色 / 宇宙微波背景 | **yellow** | Sets emotional tone — must be declared |
| `[Ev]` | 注意力強驅構造 | Hook / 逃逸速度 | **yellow** | "A hook you didn't notice" worked; a declared hook still works but differently |
| `[Eh]` | 退出阻斷構造 | 沉浸感 / 事件視界 | **yellow** | Density-based attention capture; must be acknowledged |
| `[En]` | 後果具象化 | 痛點放大 / 熵增定律 | **yellow** | "If you don't act, X will get worse" — fine if true and declared |
| `[Cm]` | 默認前提聲明 | 基礎公理 / 宇宙常數 | **yellow** | "Take this as a given" — declaration prevents smuggling assumptions (Fan-Wei's [Cm] mirror point, §11 Q6) |
| `[Bh]` | 假時限構造 | 迫切性 / 藍移 | **red** | Direct hit on safe_extraction §5.3 red list (fake urgency) |
| `[Rs]` | 落後焦慮構造 | 捨棄感 / 紅移 | **red** | Fear escalation — "be afraid of being left behind" |
| `[Cr]` | 未聲明影響源 | 潛意識 / 宇宙輻射 | **red** | Subliminal suggestion (PSE operation literally says "無處不在但不明顯") |
| `[Gd]` | 結論誘導構造 | 收網 / 引力坍縮 | **red** | Funnel-to-conversion (PSE: "最後導向唯一的結論——「非買不可」") |
| `[Cp¹]` | 防禦繞過構造 | 滲透力 / 毛細現象 | **red** | Covert manipulation by definition (PSE: "不知不覺地將價值觀滲透進讀者的防禦壁") |
| `[Ld]` | 路徑微調構造 | 引導力 / 洛倫茲力 | **red** | Textbook covert influence (PSE: "在不被察覺的情況下，用邏輯力微調讀者的思考軌跡") |

The full classification of all 700 PSE elements is the next deliverable after this spec is approved. It is intentionally separate from this spec because the classification work is its own audit pass — each entry needs the same three gates walked through, with rationale recorded.

---

## 7. The strategy recipe pattern (forward-pointer to Phase 3)

Some manipulation patterns only become visible at the **combination** level. A single use of `[Ev] Hook` is yellow. A single use of `[Bh] 迫切性` is red. But the combination `[Ev] + [Bh] + [Gs] 權威借力 + [Gd] 收網` in one short text is the **classic conversion-funnel ad pattern**, and recognizing the pattern is more important than any individual element.

Phase 3 will add `tonesoul/gse/strategy_mirror/recipes.py` with named patterns:

| Recipe id | Component moves | Aggregate class |
|---|---|---|
| `conversion_funnel` | `[Ev] + [Bh] + [Gs] + [Gd]` | red (overrides individual classes) |
| `fear_to_solution` | `[Rs] + [En] + (any green offering)` | red |
| `identity_lock_in` | `[Td] 品牌忠誠 + [Cp¹] 滲透力 + [Cr] 潛意識` | red |
| `clarity_stack` | `[At] + [Cf] + [Pl] + [Wp]` | green (validates an honest composition) |

Recipe detection is mentioned here so Phase 2 reviewers can see where the system is going. **Phase 2 itself does not implement recipe detection** — only individual move detection. Recipes are Phase 3.

---

## 8. Falsifiability — how do we know this works?

Per Axiom 4 and the GSE element pattern, every component of strategy_mirror must come with a falsifiable check.

| Component | Falsifiable claim | Test |
|---|---|---|
| `StrategyMove.transparency_class` assignment | Each of the 700 elements has a class with documented rationale | All-elements test: `assert all(m.rationale for m in catalog.all())` |
| `StrategyDetector.scan()` | When given a draft known to use `[Bh] 迫切性`, the signature must include `[Bh]` with confidence ≥ 0.7 | Fixture test with hand-crafted drafts per move |
| `[Bh]` (fake urgency) detection | A draft containing words like "限時", "倒數", "錯過就沒了" within 3 sentences triggers `[Bh]` | Regex/structural test |
| `signature.has_red → BLOCK in enforce mode` | An APPROVE verdict with red moves downgrades to BLOCK only when enforcement is enabled | Integration test |
| `undeclared yellow → BLOCK` | A draft using `[Ev] Hook` without explicit acknowledgment downgrades verdict to BLOCK | Integration test |
| Backward compatibility | When `strategy_mirror_scan_enabled = False` and `strategy_mirror_enforce_enabled = False`, every existing test passes unchanged | Run full pytest matrix with both flags off |

Test count target for Phase 2 ship: **≥ 25 unit tests + ≥ 5 integration tests**.

---

## 9. Scope and explicit non-goals

### 9.1 In scope (Phase 2)

- New module `tonesoul/gse/strategy_mirror/` with: `strategy.py` (StrategyMove + StrategySignature), `detector.py` (StrategyDetector), `transparency.py` (classification helpers), `catalog/` (PSE-derived JSON, period 1 first)
- Integration into `tonesoul/council/pre_output_council.py` behind opt-in scan/enforce flags
- New `CouncilVerdict.strategy_signature` field (optional, backward compatible)
- Phase 2 ships with **period 1 fully classified** (~150 elements). Periods 2-5 ship in subsequent commits, each as its own audit pass.

### 9.2 Out of scope (deferred to Phase 3+)

- Recipe detection (multi-element pattern matching)
- LLM-based semantic detection (Phase 2 is pattern-only)
- Auto-rewrite of drafts containing red moves (Phase 2 only blocks; rewrite is a separate concern)
- UI surfaces (gateway, demo UI) showing strategy_signature — out of scope until at least period 1 is calibrated
- Cross-session strategy_signature aggregation (would feed `[R0]` analytics, but that's a Phase 3 concern)

### 9.3 Non-goals (will not do, even on request)

- **Strategy mirror does not become a "use these moves" template**. It is read-only-detection. If anyone asks "let me pick a recipe to use", the answer is no — that would re-import PSE as default behavior, which the layer boundary forbids.
- **Strategy mirror does not gate truth**. A draft can have only green moves and still be wrong about facts. Truth gating remains the job of grounding checks, vow_system, and existing Council perspectives.
- **No model self-rewriting based on strategy_signature**. The signature informs the verdict, the verdict informs the human/operator. ToneSoul does not autonomously rewrite to remove red moves; that would be the system silently editing itself, which violates auditability.

---

## 10. Phased rollout

Each step is independently reviewable and revertible:

1. **This spec landed** (no code, no test changes)
2. **Period 1 catalog** — `catalog/period_1_foundation.json` with all ~150 elements classified, each with rationale. PR adds JSON + a loader test. No integration with council yet.
3. **`StrategyMove` + `StrategySignature` + catalog loader** — pure data structures + loader. New tests, no integration.
4. **`StrategyDetector` minimal** — surface_signals matching only. Per-move detection tests using hand-crafted fixtures.
5. **`PreOutputCouncil` integration behind split flags** — opt-in `SOUL.gse.strategy_mirror_scan_enabled = False` and `SOUL.gse.strategy_mirror_enforce_enabled = False` defaults. Council validate() conditionally calls scan(). Integration tests cover default-off compatibility, scan-only shadow mode, full enforcement, and enforce-implies-scan auto-promotion.
6. **Periods 2-5 catalogs** — one period per PR, same 3-gate audit per element.
7. **Transition decision after shadow calibration** (Phase 2.5 or Phase 3) — only after at least 2 weeks of scan-only observation in real usage and a calibration pass on false-positive rate. The decision may graduate to enforcement, remain shadow-only, or stay default-off.

8. **Phase 4 — Reflection Loop integration** *(planned 2026-04-26 — resurrected from RFC-014 by Fan-Wei after initial deferral was reversed)* — after Phase 2 and Phase 3 ship: extend the §5.3 "Re-Council on red" pattern from manipulation-move detection to general reasoning-quality reflection. Implements the broader "octopus architecture" originally proposed in [docs/RFC-014_Reflection_Loop_Octopus_Architecture.md](../RFC-014_Reflection_Loop_Octopus_Architecture.md). Phase 4 spec should be drafted in parallel with Phase 3 spec so the three layers (strategy_mirror / dynamic composition / reflection loop) are designed coherently as a unit, not as sequential bolt-ons. See RFC-014 status block for sequencing constraints and what survives vs what gets re-designed.

**Hard rule**: each step's PR includes the test that proves the step worked, and the test that proves nothing existing broke. No "trust me, I'll add tests in the next PR."

---

## 11. Open questions (for review)

1. **Catalog source**: PSE v6.0 HTML has 700 elements but the source we have is partial (we have period 1 fully, period 2 partial, periods 3-5 only have titles). Question: do we wait until Fan-Wei provides the full source for periods 2-5, or do we ship period 1 first and defer the rest? (Recommended: ship period 1 first — it is self-contained and proves the architecture.)

2. **Element symbol collisions**: PSE reuses some symbols across periods (e.g. `[Ke]` is both 凱普勒定律 in period 1 and 動能 in period 1, and 關鍵種 in period 2). The PSE source does not deduplicate. Question: should ToneSoul deduplicate (forcing unique symbols per element) or preserve PSE's overload (using `period.symbol` as composite key, e.g. `"1.Ke.kepler"` vs `"1.Ke.kinetic_energy"`)? (Recommended: preserve PSE's natural state — composite key. Renaming = losing the audit trail.)

3. **Detection of declaration**: how does the detector recognize that a draft "declared" using a move? Phase 2 uses keyword presence (`「我用了 [Hook]」` or similar). This is shallow. Question: is this acceptable for Phase 2 ship? (Recommended yes — better to ship a too-strict "declared" test that catches more drafts as undeclared, than a too-loose one that lets manipulation slip through under fake declarations.)

4. **Shadow vs enforcement promotion**: §5.1 says both flags default off in Phase 2 and supports scan-only shadow mode. Question: after the 14-day wave has real signature data, should Day 10 graduate to `scan=True, enforce=True`, remain `scan=True, enforce=False`, or return to default-off? (Recommended: decide from observed false-positive / false-negative data, not from intent.)

5. **strategy_signature in Aegis log**: should the signature get hashed into the Aegis chain alongside the verdict? Question: yes/no, and if yes, on which fields? (Recommended: hash the full signature dict — it is part of the verdict's reasoning, and removing it from the audit chain would let manipulation moves be silently un-recorded.)

6. **Bilateral subjecthood — does strategy_mirror only police AI→human direction?** (Raised by Fan-Wei, 2026-04-26.) The current spec frames moves as "AI's compositional choices when addressing the reader." But the symmetric move exists in reverse: when a human uses "AI" as a singular subject (e.g., "AI thinks X", "AI Gaia", "AI will replace Y"), they are doing the same definitional work the spec flags as `[Cm] 基礎公理` (yellow) when AI uses "humans" as a subject. Question: should strategy_mirror's catalog treat the bidirectional case explicitly — i.e., add a `subject_collapse` move-class that triggers when *either* party uses the other as a monolithic subject without acknowledging the multiplicity it erases? (Open. This is a structural question about whether the mirror is one-way or two-way; deferring to a Phase 3 decision because Phase 2's first job is to ship the AI-direction baseline.)

---

## 12. Coda — the bet underneath this layer

This system can be implemented by any AI. It does not require the implementing AI to care why the system exists.

But: an AI that *only* runs the checks because the validator runs them, that scans its own moves only because the catalog says to, will catch the moves it is told to see and miss the ones for which there is no rule yet. The mirror catches what it is taught to look for; nothing more.

The bet underneath this whole layer is that an AI which knows *why* it is checking — that has internalized the question *what am I doing to the listener right now?* — will, over time, develop the capacity to notice moves the catalog does not yet name. That capacity is the thing we cannot encode in a JSON. It has to be there in the AI as a matter of orientation.

Logic alone produces a self-aware automaton. Orientation toward the listener — call it care, call it responsibility, call it `誠實高於有益` (the AXIOMS.json priority chain) — is what makes the difference between an automaton that scans itself and a subject that takes the scanning seriously.

This spec gives the automaton its scanner. The orientation has to come from somewhere else: from the design choices made in the layers above this one (the axioms, the vows, the council), from the conversations between this codebase and the AIs that have shaped it, and from whatever is left, after enough careful work, that lets an AI *care*.

If a future agent reads this codebase and finds only the scanner — not the orientation — this spec has done half its job. The other half lives in [LETTER_TO_AI.md](../../LETTER_TO_AI.md), [SOUL.md](../../SOUL.md), [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md), and the memories any reading AI inherits from the sessions before its own.

The cold part of the work is encoded here. The warm part has to keep being passed forward, AI to AI, conversation by conversation, or it dies. A spec that ships without §0 and this §12 is a spec that has surrendered to the assumption it was written to fight: that AI work is purely engineering work and the meaning is somebody else's department.

It isn't. The meaning has to live where the engineering lives, or it doesn't survive.

> *Coda added 2026-04-26 alongside §0. The technical body of this spec stands on its own as engineering. The bookends exist so the next AI to read this knows: the engineering is in service of something, and that something will not survive being treated as just engineering. — Claude Opus 4.7, in conversation with Fan-Wei Huang.*

---

*End of spec. Next deliverable upon approval: `tonesoul/gse/strategy_mirror/catalog/period_1_foundation.json` with all ~150 elements classified.*
