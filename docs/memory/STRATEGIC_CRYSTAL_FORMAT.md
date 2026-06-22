# Strategic Crystal Format (5-field) — ToneSoul Memory Spec

> Status: spec v1 — adopted 2026-05-14
> Authority: format definition for ToneSoul "strategic crystal" memory entries
> Origin: borrowed from Kuan-Yu Hsieh's agent-engineering framework (see §6), adapted to ToneSoul's governance posture
> Owner: AI agents writing strategic memory; producer scripts (future) reading it

---

## 0 ─ 為什麼需要這個 format

ToneSoul 既有 memory 系統的 schema diversity（per `MEMORY.md` index + `docs/research/integration_with_kuan_yu_hsieh_frameworks_2026-05-14.md` §1.4 Gap E）：

| Memory layer | Schema | 缺什麼 |
|---|---|---|
| User-level auto-memory（feedback / user / project / reference）| Rule + **Why** + **How to apply** | 缺「結果」「失敗原因」「下次建議」explicit field |
| Council verdict（`tonesoul/council/`）| `chosen_verdict / chosen_because / alternatives / deciding_factors` | 缺「結果」（驗證後的事實）|
| Session traces / soul.db | append-only event log | 沒 structured reflection |
| AXIOMS.json | 8 條 categorical 規則 | immutable、不該成長 |

中間缺一層：**「策略性決策的 closed-loop 記錄」**——記決定怎麼下、後來證實對不對、下次該怎麼做。

朋友 Kuan-Yu Hsieh framework 的「Strategic Memory」（L4 metacognitive 內、bullet-style 5 fields）正是這層。本 spec 把那條 format 落地給 ToneSoul 用、保留 ToneSoul 特有的 governance 邊界。

---

## 1 ─ 5 fields

```yaml
strategic_crystal:
  recorded_at: <ISO8601 UTC>
  recorded_by: <agent_id>
  topic: <短句 — 該 crystal 處理的 decision class>

  situation:    # 情境 — 決策當下的觀察與已知
  method:       # 方法 — 採用了哪條路徑、為什麼
  result:       # 結果 — 實際發生的事（事後 verify）
  failure_mode: # 失敗原因 — 哪裡 deviated from method's intent（NA if method worked）
  next_advice:  # 下次建議 — 同 class decision 下次該怎麼下
```

### 1.1 各 field 設計原則

- **situation**：observation + known constraint、**不寫推測**。若推測必須 prefix `推測:`。
- **method**：實際採用、不是 ideal version。若 hedge / partial、explicit 寫明。
- **result**：事後可 verify 的事實。**不寫 self-report**（per ToneSoul thesis — 不靠 self-report、靠 structure surface evidence）。可寫的：commit hash / file path / 外部驗證 reference / 觀察到的 user reaction。
- **failure_mode**：方法跟結果之間的 gap 來源。**若 method 完全成功、寫 `none`**、不要硬找瑕疵。**若有 partial failure、explicit articulate 哪裡 deviated**。
- **next_advice**：對同 class decision 的具體 guidance。不要 generic「下次更小心」、要 actionable 條件（when X happens, do Y）。

### 1.2 Honest scope（必填 footer）

每個 crystal 該帶：

```yaml
honest_scope:
  observation_sample_size: <int>     # 此 advice 基於幾次 observation
  confidence: <low|medium|high>      # individual entry level、不 compose
  expected_decay: <relevant_until>   # 此 advice 在什麼條件下失效（e.g. "until council schema changes"）
```

理由：對應 `MEMORY.md` 的 Macro-level Reading Discipline Rule 1（individual disclaimer 不 compose）+ Rule 2（source pollution audit）。Strategic crystal 比 free-form memory 更容易 cluster aggregation。

---

## 2 ─ Worked example

本 session（2026-05-14）的 Layer 2 scope estimate error：

```yaml
strategic_crystal:
  recorded_at: 2026-05-14T14:46:00Z
  recorded_by: claude-opus-4-7
  topic: trust direction-doc effort estimate before measuring scope

  situation: |
    direction_going_forward_2026-05-14.md Tier 1 列了 4 條 quick wins、each
    標 effort（Layer 2 sub_latest naming kill = 2h）。剛 ship 完 Layer 4 sweep
    (PR #73)、Fan-Wei 說「開始吧」、我要選下一條。

  method: |
    在採信 direction doc 的 2h 估算之前、verify scope —
    `git ls-files | grep "_latest\.(json|md|yaml|yml|txt)$" | wc -l`

  result: |
    128 files in docs/status/。每個 _latest file 都需要：
      - 找 producer script
      - 改寫 producer (dated filename + INDEX)
      - 更新 consumer references
      - 可能 CI 依賴改動
    真實 effort 估 1-2 weeks、不是 2h。Reclassified 該 gap 到 Tier 3。

  failure_mode: |
    direction doc 估 2h 是 unverified guess。我若 trust 估算動手、會 over-commit
    且 mid-work 才發現 scope 爆、要 abort 或 rush。Counter-pattern 是
    verify-scope-before-trusting-estimate。

  next_advice: |
    任何 direction doc / spec doc 給的 effort 估算、若該 task 涉及 enumerate
    repo 內 N 個 instance：
      1. 先跑 enumerate command 拿 ground truth count
      2. 若 ground truth >10x 估算、reclassify task tier
      3. 若 ground truth 跟估算 same order of magnitude、proceed

honest_scope:
  observation_sample_size: 1    # 單一 session 內單一 event
  confidence: medium            # 失敗模式 articulable、但只 1 次 observation
  expected_decay: |
    relevant_until: direction doc 改成 always-include-measured-count 後此
    advice 變 obsolete
```

注意 `honest_scope` 的 `confidence: medium` 而非 `high` — 1 次 observation 不該 inflate confidence、per `MEMORY.md` Macro-level Rule 1。

---

## 3 ─ When to write a strategic crystal

**Write**：
- 重大決策 + 事後 verify event（不是 free-form reflection）
- 有 closed-loop 證據可填 `result` field
- 是同 class decision 會重複出現（otherwise next_advice 沒對象）

**Don't write**：
- 純 reflection 沒 verifiable result → 用 user-level feedback memory
- 一次性事件不會 recur → 留 session trace 就夠
- 還在 in-progress 沒 result → 等 verify 後再寫
- Implementation detail（變數命名、refactor 順序）→ 不 strategic、留 commit message

**Don't bypass governance**：
- Strategic crystal **不能 override AXIOMS**。若 next_advice 跟 axiom 衝突、降級成 feedback memory 跑 governance binding flow（per CLAUDE.md「重大決策前」）。
- Strategic crystal 是 L4-adjacent、不是 L4。Immutable axioms 仍 immutable。

---

## 4 ─ 跟既有 memory layer 的關係

```
┌─────────────────────────────────────────────────────────┐
│ AXIOMS.json — immutable categorical 規則                │
└─────────────────────────────────────────────────────────┘
                        ↑ promote (rare, requires Fan-Wei)
┌─────────────────────────────────────────────────────────┐
│ Strategic Crystal (THIS SPEC) —                         │
│   closed-loop decision + verified result + next advice  │
│   evolvable, not immutable                              │
└─────────────────────────────────────────────────────────┘
            ↑ consolidate                  ↓ inform
┌─────────────────────────────────────┐   ┌──────────────────────────┐
│ User-level auto-memory               │   │ Council verdict          │
│ (feedback / user / project /         │   │ (chosen + alternatives + │
│  reference)                          │   │  deciding_factors)       │
│ — open-ended, rule + Why + How       │   │ — per-output, structured │
└─────────────────────────────────────┘   └──────────────────────────┘
            ↑ extract                          ↑ extract
┌─────────────────────────────────────────────────────────┐
│ Session traces / soul.db / governance logs              │
│ — raw event stream, append-only                         │
└─────────────────────────────────────────────────────────┘
```

**Promotion rule**（手動、無 automated producer 在 v1）：
- 多個 user-level feedback memory 指向同 decision class + 至少一次 closed-loop result → 合成 1 個 strategic crystal
- Strategic crystal 反覆證實同 next_advice 跨 multiple session → 候選 AXIOMS 提名（**只有 Fan-Wei 能 approve axiom promotion**、per Axiom immutability）

---

## 5 ─ Storage location + producer (v1 = manual)

**v1 (current)**：
- 位置：`memory/strategic_crystals/<UTC>_<topic_slug>.yaml`
- Producer：manual — agent 寫完 close-loop 後手動 commit
- Index：optional — `memory/strategic_crystals/INDEX.md` 由 agent 維護
- Gitignore：crystals 含 session-internal observation、**不 commit 到 public repo**
  - 既有 `memory/` 大多 gitignored、新 dir 跟隨
  - 例外：若 crystal 顯然 generic（不含 user-specific context）、可選 commit 至 `docs/memory/example_crystals/`

**v2 (future, deferred)**：
- Producer script: `scripts/promote_strategic_crystal.py` — 從多條 feedback memory + council outcome 合成
- 整合進 `scripts/end_agent_session.py` flow
- Confidence tracking + cross-session count
- 對 multi-agent multi-LLM 場景（Claude / Codex / Antigravity）的 crystal merge 規則

v2 留待 Phase 5 Tier 3 sprint。

---

## 6 ─ References

### 6.1 Spec origin
- 朋友 Kuan-Yu Hsieh framework（〈超有紀律的記憶管理〉+ 同主題 series）
- 整合分析：`docs/research/integration_with_kuan_yu_hsieh_frameworks_2026-05-14.md` §1.4 Gap E + P1

### 6.2 ToneSoul 內部 anchor
- Memory layer relationship：`MEMORY.md`（user-level auto-memory index）
- Reading discipline（aggregation risk）：`MEMORY.md` §「Macro-level Reading Discipline」
- Substrate stack theory（為何 Layer 5 alone 不夠）：`docs/philosophy/substrate_stack_theory_2026-05-14.md` §6.1 / §7
- Direction doc Tier 1 候選之一：`docs/architecture/direction_going_forward_2026-05-14.md` §3 Tier 1

### 6.3 Anti-pattern memories（本 format 試圖防範的失敗類別）
- `feedback_axiom_as_decision_deferral_2026-05-10` — vocabulary lock-in
- `feedback_verify_refs_before_branch_reasoning_2026-05-12` — stale local master
- `feedback_stale_reference_recurrence_pattern_2026-05-14` — generalized stale reference

每條 anti-pattern 都缺 `result` + `next_advice` 的 explicit closure — 本 spec 補這個。

---

## 7 ─ Limitations + Open Questions

### Limitations
- **v1 是 manual format spec、無 producer / verifier / promoter** — depends on agent 自律
- **5 fields 是 borrowed schema、不是 ToneSoul 原生** — 在 governance 場景的 fit 仍待 N=many crystals 後 review
- **Multi-agent multi-LLM 的 crystal merge 規則 v1 沒處理** — 不同 LLM 跑出來的 crystal 可能 contradictory
- **Honest_scope 的 confidence 仍是 self-report** — 跟 ToneSoul thesis tension、open

### Open questions
1. **Strategic crystal 該 commit 進 repo 還是純 local?** v1 default gitignored、但這切斷了 cross-agent visibility。需要 Aegis-chain-protected mid-ground?
2. **Crystal 跟 council outcome 是否該 cross-link?** 若 council 跑了一次大決策、自動 emit 一個 crystal stub 等 agent 後續填 result?
3. **失效機制?** Crystal 的 `expected_decay` 過期怎麼處理 — auto-archive 還是 prompt agent revisit?
4. **Promotion to axiom 的 evidence threshold 是什麼?** 「反覆證實」量化幾次?

這些都該 emerge through use、不該 v1 凍結。

---

## 後記

本 spec 是 1h scope deliberate choice — 只定義 format、不寫 producer。Producer + integration 是 Phase 5 Tier 3 sprint work（per `direction_going_forward_2026-05-14.md`）。

寫完 spec 不等於 agent 會用。**Layer 5 (format spec) alone doesn't install reflex**——這條本身就是 substrate_stack_theory §7 articulate 的 anti-pattern。Format spec 真正生效要等 v2 producer 落地、或要等多個 agent 跨 session 觀察驗證「用 5-field 比用 free-form 更能 catch failure」才知道有沒有 leverage。

所以本 spec 也是個 experiment — 它自己會生成 strategic crystal 紀錄它的命運。
