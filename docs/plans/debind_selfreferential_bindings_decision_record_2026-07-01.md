# 【治理決策記錄】self-referential binding cleanup（2026-07-01）

> **決策物件**：兩條 **live** 的 council self-referential weight-binding 做 cleanup —
> `voting_evolution` → shadow/observe-only，`persona_track_record` → modify-not-remove。
> **狀態**：**RATIFIED**（PR #231 merged 2026-07-02；`docs/status/yu_handoff_final.md` 記「de-bind ratified」）。
> **實作進度（2026-07-03 回填）**：尚未動工——shadow/observe-only flag 與 post-normalize floor（codex 但書）的 code 均不存在（`pre_output_council.py:110-118` 仍無條件 `get_weights()`；`deliberation/types.py:168-174` 無 floor）。§0 的但書仍有效：實作 PR 前必須在 proposed flag 下實跑 `test_deliberation_gravity_pareto` + `test_council_evolution`。
> **界定（承重）**：這是 **de-bind / self-referential binding cleanup，不是刪除 council memory**。

---

## 0. 這份記錄怎麼來的（三方確認 + 誠實限制）

- **cross-model 三方確認**：(1) 我的 7-agent de-bind 評估 workflow（跑 live modules）；(2) codex
  獨立驗（57 tests、自跑 probe、file:line）；(3) 本次 prep workflow 對 **origin/master @ 7e17aa1**
  逐條 first-hand 驗。方向與機制三方一致。
- **誠實限制**：prep 的 test-impact 是 **source inspection，未實跑 suite** → ratify 前必須在 proposed
  flag 下實跑 `test_deliberation_gravity_pareto` + `test_council_evolution` 確認 green/red split
  （我自己的紀律：suite-green 必須引 post-change run，那個 run 目前不存在）。adversarial-critic
  agent 這次 structured-output 失敗，framing 由 codex + design residuals 覆蓋。

## 1. 決策（建議，待 ratify）

- **`voting_evolution` → shadow / observe-only（優先做）**：gate **只**在
  `pre_output_council.py:110-120` 的 `get_weights()→compute_coherence` handoff，default-off flag，
  off 時傳 `weights=None`（＝未加權，`compute_coherence` 本就把 None 當全 1.0）。
  `record_deliberation / evolve_weights / get_summary`（`runtime.py:479-511`）**照舊 in-memory 跑**，
  transcript + suppression flag 照舊產生。**~5 行 + 一個 flag。**
- **`persona_track_record` → modify-not-remove**：核心**不是調權重，是停止把 verdict-label 當跨
  session 的 success 分數直接綁 live weight**。3 個可組合選項（都保留 telemetry）：
  - **(A)** advisory / default-off flag on `gravity.py:229-244`（最小、最可逆、＝ shadow-equivalent）
  - **(B)** context-aware scoring 讓 **Aegis 的 block 不算 failure**（touches `persona_track_record.py`；
    會重新詮釋累積 stats → **最難乾淨可逆**）
  - **(C)** **post-normalize 最低 share floor**（修 codex 的「clamp 在 raw multiplier ≠ normalized
    share floor」bug；`types.py:161-174` 的 normalize 沒有 floor）
  - **建議 A（可 ratify 的第一刀）+ C（即使保持 on 也該修，見 §3）**，B 之後再談。
- **HYGIENE（必須同時，見 §5）**：`memory/council_evolution.json` 加進 `.gitignore`（本 PR 已含）。

## 2. 為什麼

- 兩條都是 **live，不是純觀測**：`voting_evolution` 讓同一組票可 approve↔declare_stance（codex
  probe）；`persona` 讓 20 次 Aegis block → aegis normalized share **0.253 < 0.30 baseline**（codex
  probe）。
- self-referential（獎勵「跟 council 自己的最終 verdict 一致」）= **echo-chamber / yes-machine 壓力**
  —— `voting_evolution` 自己 ship 的 `suppression_observability` flag 正是在警告這件事。
- `persona` 的 `block=0.0` 對 Aegis = 把**正確的安全阻擋當失敗** → **active anti-safety gradient**。

## 3. 張力來源

- **vs suppression detector（最承重）**：suppression flag 的 `weight<0.95` gate 需要 weights 真的動。
  所以 shadow **只能 gate consumer（`pre_output_council` 的 get_weights→coherence），絕不能連
  `runtime` 的 evolve_weights/record_deliberation/get_summary 一起關**——否則 weights 凍在 1.0、
  flag 永不 fire = **靜默殺掉「偵測 dissent 壓制」這個信號本身**。sweep 已驗證 **8 個下游 consumer**
  （receiver_posture / observer_window / diagnose / runtime_adapter / runtime_adapter_normalization /
  start_agent_session / dossier / R-Memory packet）**全部從 transcript 那條路讀 flag、不讀
  get_weights → 全部 shadow-safe**。
- **vs R-Memory packet schema 契約**：`evolution_suppression_flag` 是
  `spec/governance/r_memory_packet_v1.schema.json:1496` 的 **REQUIRED 欄位** → 必須保持存在（bool，
  `runtime_adapter.py:1900` 預設 False → OK）。**不可移除該欄位**，否則 packet validation hard-fail。
- **vs Axiom 4（非零張力）**：cleanup 方向是**保留/恢復 dissent**（shadow 移除 pro-approve 的
  conformity nudge；persona floor 保護 minority share）→ **與 Axiom 4 同向，不衝突**。
- **producer/consumer split**：`pre_output_council` 和 `runtime` 各自 lazily build 自己的
  `CouncilEvolution` instance（同一份 on-disk state）→ 哪個是「權威」weight source 本就 muddy；
  gate consumer 反而澄清這件事（owner 該知道這個 split 存在）。
- **這不是刪除**：history / weights / summary / telemetry 全保留。

## 4. 可逆性

**HIGH。** voting_evolution shadow = 一個 default-off flag，翻回即恢復，無 migration、無刪除。
persona (A)/(C) 也是 flag/floor，可逆；**(B) scoring 改動最不乾淨可逆**（重新詮釋累積 success_sum）
→ 建議 A/C 先行。gitignore fix 可逆，且 `council_evolution.json` 尚未 tracked，無需改寫歷史。

## 5. Sequencing / preconditions（ratify 前必須）

1. **gitignore fix 先/同時**：shadow gate **不會**停止 state 檔寫入（`runtime.py:504` 每 cycle 仍
   `evolve_weights()→_save_state()`——那是刻意的 telemetry），所以 state 檔**必須先被 ignore**，
   否則 `memory/council_evolution.json`（含 per-perspective vote/dissent/alignment + suppression
   narrative）會在下一次 `git add -A` **外洩進公共 repo**。**已驗證 NOT-ignored、且未追蹤的副本已在
   workspace materialize（不是假設）。**
2. **實跑測試**：在 proposed flag 下確認 green/red split（`test_deliberation_gravity_pareto` 的
   end-to-end「persona bias reaches final weight」測試會需要更新；`test_council_evolution` 全部應
   green，因為它們測 in-memory math 不測 pre_output_council handoff）。
3. **加測試**：一條「shadow off vs on 的 verdict 差異」end-to-end 測試 + 一條「vindicated Aegis block
   不被當 failure」測試（選 B/C 時）。
4. **實作是獨立 owner-gated PR**（這份只是決策記錄）；governance-adjacent → 落地後**再讓 codex 驗一次**
   （本 session 已證 single-model 改 governance code 會兩向出錯）。

## 6. 給 owner 的選擇

1. **採納**：voting_evolution shadow（default-off flag）+ persona **A**（default-off）+ **C**
   （post-normalize floor）+ gitignore fix。**（建議）**
2. **最小**：voting_evolution shadow + gitignore，persona 之後。
3. **只擋 leak**：先只做 gitignore hygiene，binding 之後再談。
4. 其他 / 擱置。

## 7. 誠實標註

- 事實三方驗過（對 origin/master@7e17aa1 first-hand）；但 **test-impact 未實跑 → ratify 前補**。
- **broad `memory/*.json` guard 的建議我查證後否決**：有 tracked `memory/*.json`（`crystal_index.json`
  / `session_pulse_latest.json` / `profiles/*.soul.json` / `schemas/*.schema.json`）→ 只加 **targeted**
  `memory/council_evolution.json`。**enumerate-don't-glob gap 仍是系統性風險**（每個新 governance-state
  writer 要自己一行）——這條留給後續系統性處理，別用會誤傷 tracked config 的 blanket glob。
- persona 的 raw-clamp-vs-share（codex）是**獨立於 de-bind 決策的真 correctness bug**：即使 binding
  保持 ON，選項 C 也該落——安全聲音(Aegis)在正確 block 上被評 0.0、再於 normalize 後掉到 baseline
  以下，是 active anti-safety gradient。

接 `docs/plans/consequence_structure_calibration_2026-06-30.md`、`calibration_binding_decision_record_2026-06-30.md`（#228 姊妹決策）。
