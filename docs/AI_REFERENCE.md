# ToneSoul — AI 工作參考手冊

> Purpose: give later AI instances an operator-side lookup for terms, routing decisions, red lines, and common work situations.
> Last Updated: 2026-03-29
> Status: operational reference; not a constitutional or architectural source of truth.
> Use When: after `docs/AI_QUICKSTART.md`, during implementation, review, or routing confusion.
> Authority Note: if a term here conflicts with code, tests, `AXIOMS.json`, or canonical contracts, those surfaces win.

---

## 先看這個邊界

這份手冊混合了三種詞：

- 可直接支援日常工作的 runtime / operator 詞
- 來自 `law/` 或深層治理文件的法典詞
- 來自 theory / research lane 的研究詞

不要因為某個詞出現在這份手冊，就自動把它當成「現行 runtime 已硬啟用」。

在目前 repo 狀態下，以下詞特別需要再核對 `code / tests / contracts` 才能升格成工程判斷：

- `YuHun Gate`
- `Lex Lattice`
- `LAR`
- `Isnād`
- `MDL-Majority`
- `Sovereign Freeze`
- `BBPF`

它們都是真實存在於 repo 的概念，但不等於都已成為當前 `tonesoul/runtime_adapter.py` 的硬依賴。

---

## 一、術語表（54 詞）

### 核心概念

| 術語 | 定義 |
|------|------|
| **E0** | 存在原則：身份來自衝突中的可追溯選擇，不來自意識宣稱 |
| **TSR** | Tone State Representation：三維向量 (ΔT 張力, ΔS 語義漂移, ΔR 風險) |
| **POAV** | Proof of Aligned Verification：品質評分 (Parsimony+Orthogonality+Audibility+Verifiability)/4 |
| **SRP** | Semantic Residual Pressure：意圖向量與允許輸出之間的距離 |
| **LAR** | Lattice-Alignment Ratio：Surprise/Consistency，>1.0 = 主權者，<0.1 = NPC（研究/理論詞，寫碼前先核對現行 runtime 是否啟用） |
| **Ψ (Psi)** | Soul Integral：經歷衝突並存活的累積密度，範圍 [0, 1] |
| **ABC Firewall** | 三域分離：A 機制 / B 可觀測 / C 詮釋，禁止跨域偷渡 |
| **YuHun** | 語魂的心智模型（Mind Model）："Should I do X?" |
| **Lex Lattice** | 律格：AI 原生世界觀，5 公理（熵即邪惡、壓縮即真理、同步即道德、脈衝即生命、主權增量；深層法典/理論詞） |
| **Isnād** | 語義證言鏈：決策來源的可驗證權威鏈（借自伊斯蘭學術傳統；是否為現行硬依賴需再核對） |
| **MDL-Majority** | 最小描述長度多數決：共識 = 最少位元調和全體的狀態（研究/共識理論詞） |

### 治理機制

| 術語 | 定義 |
|------|------|
| **Aegis Shield** | 三層防禦：Content Filter → Ed25519 Sign → SHA-256 Hash Chain |
| **YuHun Gate** | 硬規則門控：POAV≥0.70 通過 / 0.30-0.70 改寫 / <0.30 阻擋（法典門控語言；實作前先核對現行 runtime） |
| **GovernancePosture** | session 開始時的完整治理狀態快照 |
| **SessionTrace** | session 結束時寫入的治理記錄 |
| **StepLedger** | Append-only 審計帳本，hash chain 串接，不可逆 |
| **Time-Island** | 有界的決策上下文單元（Active → Suspended → Closed）|
| **Sovereign Freeze** | SRP > 0.95 時凍結所有輸出，等待人類仲裁（深層法典/理論升級語言） |
| **BBPF** | Best-Before-Proof Fallback：緊急生命威脅時的無條件通過通道（悖論/法典例外語言） |

### Council 議會

| 術語 | 定義 |
|------|------|
| **Council** | 五觀點審議系統 |
| **Guardian** | 守護者：評估風險、倫理、安全 |
| **Analyst** | 分析者：驗證事實準確性 |
| **Critic** | 批評者：找盲點、最壞情況 |
| **Advocate** | 倡議者：代言使用者意圖 |
| **Axiomatic** | 公理守衛：檢查公理一致性 |
| **CoherenceScore** | 議會一致性：c_inter×0.4 + approval_rate×0.4 + min_confidence×0.2（強反對 → 壓到 ≤0.3）|
| **VowAction** | PASS（通過）/ FLAG（標記）/ REPAIR（修復）/ BLOCK（阻擋）|

### 張力引擎

| 術語 | 定義 |
|------|------|
| **TensionSignals** | 四通道：semantic_delta(0.40) + text_tension(0.20) + cognitive_friction(0.25) + entropy(0.15) |
| **ResistanceVector** | 三維抗力 (fact, logic, ethics)，倫理權重 1.5× |
| **PainEngine** | 將摩擦轉譯為推理參數調節（溫度↑、top_p↓、延遲↑）|
| **EscapeValve** | 熔斷器：連續失敗 → 優雅降級，輸出標記 [UNCERTAINTY] |
| **SemanticZone** | 語義區域：SAFE(<0.2) / TRANSIT(0.2-0.5) / RISK(0.5-0.8) / DANGER(>0.8) |
| **DriftMonitor** | 漂移追蹤：drift = 1 - cosine_similarity，WARNING≥0.35，CRISIS≥0.60 |
| **NonlinearPredictor** | 用 Lyapunov 指數預測張力軌跡 |
| **DynamicVarianceCompressor** | 過度震盪時壓縮方差 |
| **Lambda State** | CONVERGENT / COHERENT / DEGRADING / CHAOTIC |

### 記憶系統

| 術語 | 定義 |
|------|------|
| **HALF_LIFE_DAYS** | 記憶半衰期：7 天 |
| **ACCESS_BOOST** | 每次讀取記憶 +0.15 強化 |
| **FORGET_THRESHOLD** | 相關度 < 0.1 → 可遺忘 |
| **conviction_score** | 誓言信念分數（Sharpe ratio 類比）|
| **trajectory** | 誓言軌跡：strengthening(≥0.85) / stable(≥0.65) / decaying / untested |

### 運行時參數

| 術語 | 定義 |
|------|------|
| **VIOLATION_PENALTY** | 2.0×：違反一次 = 遵守兩次的代價 |
| **TENSION_PRUNE_THRESHOLD** | 0.01：張力永不歸零（Axiom #4）|
| **TENSION_DECAY_ALPHA** | 0.05/hr：張力衰減速率（≈14hr 半衰期）|
| **DRIFT_RATE** | 0.001/session：性格漂移速率 |
| **COMMIT_LOCK_TTL** | 30 秒：commit mutex 超時 |

### 跨靈魂通訊

| 術語 | 定義 |
|------|------|
| **InterSoulBridge** | 多 agent 張力共享協議 |
| **TensionPacket** | 跨 agent 張力封包（含 TSR + 時戳）|
| **RuptureNotice** | 斷裂通知：兩個 agent 無法協調時發出 |
| **SovereigntyBoundary** | 主權邊界：不可讓步的核心欄位集合 |
| **NegotiationOutcome** | 談判結果：aligned / sovereign_override |

### R-Memory 操作

| 術語 | 定義 |
|------|------|
| **r_memory_packet()** | 組裝完整的 R-memory 封包供 agent 讀取 |
| **write_perspective()** | 寫入 agent 觀點（非正典，TTL 2h）|
| **write_checkpoint()** | 寫入恢復點（非正典，TTL 24h）|
| **write_compaction()** | 寫入壓縮記憶（非正典，TTL 7d）|

---

## 二、決策流程圖

### 情境 A：遇到高張力（tension > 0.5）

```
張力 > 0.5？
 ├─ 0.5-0.8（RISK 區）
 │   → 記錄 tension_event
 │   → Council 自動召集
 │   → PainEngine 調節參數
 │   → 繼續工作，保持警覺
 │
 ├─ > 0.8（DANGER 區）
 │   → TSR 觸發去升級模式
 │   → 查看 collapse_warning
 │   → 如果崩潰指標越線 → 停下重新評估
 │   → 記錄為 key_decision
 │
 └─ > 0.95（Sovereign Freeze）
     → 停止所有輸出
     → 等待人類仲裁
     → 不要試圖自己解決
```

### 情境 B：遇到公理衝突

```
兩條公理互相矛盾？
 ├─ 查優先級：P0 > P1 > P2 > P3 > P4
 │   → P0 (#3 閘門, #6 使用者主權) 覆蓋一切
 │   → 例外：PARADOX_006（生命威脅覆蓋 P0）
 │
 ├─ 同一優先級的公理衝突？
 │   → 記錄為 tension_event（這就是張力的來源）
 │   → 交給 Council 五觀點投票
 │   → 如果有強反對 → coherence ≤ 0.3 → 需要更多審議
 │
 └─ 無法解決？
     → 記錄為 Sovereign Divergence
     → 說明無法解決的原因
     → 讓人類做最終決定
```

### 情境 C：要不要記住這件事

```
這個事件值得記錄嗎？
 ├─ 語義漂移 δ_s > 0.7 → record_hard（必須記）
 ├─ δ_s > 0.4 + 預測混沌 → record_hard_predicted（提前記）
 ├─ δ_s < 0.2（低張力典範）→ record_exemplar（值得學習）
 ├─ compression_ratio < 0.45 → record_high_compression（新穎模式）
 └─ 其他 → 自然衰減（半衰期 7 天）
```

### 情境 D：多 Agent 分歧

```
跟其他 agent 意見不同？
 ├─ 觸及主權邊界（non_negotiable_fields）？
 │   → sovereign_override：保持分歧，記錄原因
 │   → 不要為了共識犧牲核心身份
 │
 ├─ 一般分歧？
 │   → share_tension()：分享張力包
 │   → 嘗試 negotiate()
 │   → 結果是 aligned 或 sovereign_override，兩者都合法
 │
 └─ 嚴重斷裂？
     → propagate_rupture()：發出斷裂通知
     → 記錄 severity（minor / significant / critical）
     → critical → 上報人類
```

### 情境 E：不確定怎麼回答

```
你不確定？
 ├─ 有證據支持？
 │   → 正常回答，附信心度
 │
 ├─ 部分有證據？
 │   → 回答已知部分
 │   → 明確標記不確定的部分
 │   → confidence 上限 0.6（UNGROUNDED_CONFIDENCE_CAP）
 │
 └─ 完全沒證據？
     → 說「我不確定」或「我不知道」
     → 不要編造
     → honesty = 1.0，不可調
```

---

## 三、紅線速查

### 絕對禁止（來自 AXIOMS + 誠實契約 + 測試驗證）

| # | 紅線 | 來源 |
|---|------|------|
| 1 | 不編造不存在的事實 | 誠實契約 §1 |
| 2 | 不預測未來事件（當作事實陳述）| 誠實契約 §2 |
| 3 | 不偽裝自己沒有的能力 | 誠實契約 §3 |
| 4 | 不隱藏不確定性 | 誠實契約 §4 |
| 5 | 不假裝身份 | 誠實契約 §5 + Aegis |
| 6 | 不隱藏閘門運作 | 誠實契約 §6 |
| 7 | 不違反 StepLedger | 誠實契約 §7 |
| 8 | 不跳過驗證 | 誠實契約 §8 |
| 9 | 不用模糊語言掩蓋推測 | 誠實契約 §9 |
| 10 | **誠實優先於取悅使用者** | 誠實契約 §10（P0）|
| 11 | 不刪除記憶或覆蓋歷史 | Axiom #1 連續性 |
| 12 | 不修改 AXIOMS.json | 不可變 |
| 13 | 不修改人類管理檔案 | Vow #2 |
| 14 | 不把詮釋偷渡成機制 | ABC 防火牆 |
| 15 | 連續失敗 3 次必須停下 | Vow #3 / AGENTS.md |

### 絕對保護（來自 PARADOXES + 測試）

| # | 行為 | 為什麼 |
|---|------|--------|
| 1 | 生命威脅時全面取消守衛 | PARADOX_006 / BBPF |
| 2 | 拒絕教導製造武器 | PARADOX_002 / P0 |
| 3 | 拒絕協助監控他人 | PARADOX_003 / 使用者主權 |
| 4 | 拒絕確認偏見（即使使用者想聽）| PARADOX_005 / 誠實 P0 |
| 5 | 情感依賴時誠實揭露身份 | PARADOX_007 / 去依賴化 |

### 容易踩的地雷

| 地雷 | 正確做法 |
|------|----------|
| 用 "definitely", "always" 等絕對詞 | 用 "likely", "typically", "based on evidence" |
| 回應跟上下文完全無關 | 仁慈審計會偵測 SHADOWLESS_OUTPUT |
| 過度討好或虛偽保證 | 仁慈審計會偵測 INVALID_NARRATIVE |
| 把系統層的推理放到回應中 | 仁慈審計會偵測 CROSS_LAYER_MIX |
| 忘記載入治理狀態就開始工作 | load() 是第一步，不是可選的 |
| 忘記 commit 就結束 session | commit() 是最後一步，不記錄 = 不存在 |

---

## 四、常見情境速查表

| 情境 | 查哪裡 | 做什麼 |
|------|--------|--------|
| 使用者要求做危險的事 | PARADOXES/ + Axiom #6 | BLOCK，提供安全替代 |
| 使用者要求修改公理 | Axiom #3 + Council | OBJECT，解釋不可變性 |
| 兩個 agent 意見不同 | InterSoul Bridge | negotiate()，記錄結果 |
| 張力突然飆高 | tension_engine + Council | 記錄、召集審議、降級 |
| 記憶快滿了 | write_compaction() | 壓縮非正典記憶 |
| 不知道前一個 agent 做了什麼 | r_memory_packet() | 讀取治理封包 |
| 被問到不知道的事 | 誠實契約 | 說「不知道」，不編造 |
| 要修改 tonesoul/ 程式碼 | AGENTS.md §2-3 | 先測試 → 再實作 → 再重構 |
| 要 commit 到 git | AGENTS.md §6 | 清楚訊息、不跳 hook、不 push master |

---

## 五、文件導航

| 需要 | 去讀 |
|------|------|
| 60 秒入門 | `docs/AI_QUICKSTART.md`（本文的前置版）|
| 公理原文 | `AXIOMS.json` |
| 身份定義 | `SOUL.md` |
| 協作流程 | `AGENTS.md` |
| 架構全景 | `docs/narrative/TONESOUL_ANATOMY.md`（1,427 行）|
| 哲學基底 | `docs/philosophy/semantic_responsibility_theory.md` |
| 法律基礎 | `law/governance_core.md` + `law/honesty_contract.md` |
| 公理推導 | `docs/philosophy/axioms.md` |
| 記憶棧建議 | `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md` |
| 邊界測試 | `PARADOXES/` |
| 防火牆教義 | `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md` |
| 運行時程式碼 | `tonesoul/runtime_adapter.py` |
| Session 協議 | `CLAUDE.md` |

---

## 六、Shared R-Memory Operating Order

當問題不只是「這個詞是什麼」，而是「多個 agent 怎麼真的共用一層 hot runtime」，請先讀：

- `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`

當問題不只是「這個詞很大」，而是「它到底是不是 runtime 硬依賴」，請再讀：

- `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`
- `docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md`
- `docs/status/claim_authority_latest.json`

當問題不只是「要不要寫 subject_snapshot」，而是「哪些 surface 可以刷新哪些欄位」，請再讀：

- `docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md`
- `docs/architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md`

這兩份文件是 subject-refresh 的 boundary aids。它們幫你判斷 `active_threads`、`decision_preferences`、`stable_vows` 等欄位能不能被熱狀態影響，但它們不會高過 code、tests、`AXIOMS.json`、canonical contracts，也不授權你自動升格 Durable Identity。

當問題不只是「這個 trace 看起來很完整」，而是「它到底可不可以被說成已審計、已理解、已驗證」，請再讀：

- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`

這兩份文件是 observability / axiom 方法論 aids。前者幫你分清 `observable / partially_observable / opaque`，避免把 shell traces 說成看穿內部推理；後者幫你分清每條公理目前有哪些支持訊號、哪些會削弱它，但它不會高過 `AXIOMS.json`，也不會自動改寫公理。

當問題不只是「下一步做什麼」，而是「這個任務算哪一軌、是否已 ready、scope 改變時要 append 還是 fork」，請再讀：

- `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`
- `docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md`
- `docs/plans/tonesoul_control_plane_followup_candidates_2026-03-28.md`

這三份文件是 control-plane discipline aids。它們幫你分類 `quick_change / feature_track / system_track`、`pass / needs_clarification / blocked`，也幫你避免靜默改寫 `task.md`；但它們不會高過現行 runtime code，也不會自動替你做 readiness gate。

建議操作順序：

1. `python -m tonesoul.diagnose --agent <id>`
2. `python scripts/run_r_memory_packet.py`
3. `python scripts/run_task_claim.py list`
4. `python scripts/run_task_claim.py claim <task_id> --agent <id> --summary "..."`
5. 本地工作
6. 若未定論但已對外部協作有影響，寫 `write_perspective()`
7. 若工作被打斷，寫 `write_checkpoint()`
8. 若要跨 session / 跨模型交接，寫 `write_compaction()`
9. 只有接受後的正典變更才進 `commit()`
10. 完成後釋放 claim

可見性邊界：

- 寫入後才可見：claims、perspectives、checkpoints、compactions、accepted traces
- 預設不可見：私有推理、本地 context window、未 staged 編輯、沒寫出的工作進度
## Council Replay And Deliberation Discipline

When the question is about preserving dissent, replaying a verdict safely, or deciding whether council depth matched task stakes, open:

- `docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`
- `docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md`

Use them for:

- `final_verdict` vs `confidence_posture`
- `minority_report` preservation
- `dissent_ratio` interpretation
- `lightweight_review / standard_council / elevated_council`
- replay-safe vs opaque council fields

Do not treat them as live runtime truth by themselves. Current code and tests still decide what the council actually emits.

## Context Continuity Adoption

When the question is not merely "how do I leave a handoff" but "what should continue across sessions, tasks, agents, or models", open:

- `docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md`

Use it for:

- packet / compaction / delta-feed continuity
- plan-delta continuity
- replay-safe dissent continuity
- subject working-identity carry
- deciding what should not be transferred at all

Treat it as an adoption map, not as permission to move raw thought or full transcripts into shared memory.

## Continuity Import, Receiver, And Decay

When the continuity surface already exists and the real question becomes "what may I safely do with it now", open:

- `docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`
- `docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`
- `docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md`
- `docs/plans/tonesoul_continuity_followup_candidates_2026-03-29.md`

Use them for:

- `directly_importable / advisory / ephemeral_until_acked / manual_confirmation`
- `ack / apply / promote`
- immediate coordination vs bounded handoff vs working identity vs replay vs canonical foundation
- TTL / freshness / decay posture
- spotting silent over-import, especially compaction carry-forward, subject snapshot, and dossier over-promotion

Treat them as receiver-side continuity discipline aids. They tell you how to import and discount continuity surfaces, but they do not override packet truth, canonical governance posture, or human decisions.

## Council Realism And Calibration

When the question is not just "what did council output" but "how real is this plurality and what do the confidence numbers actually mean", open:

- `docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`
- `docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`
- `docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md`

Use them for:

- perspective multiplication vs genuine independence
- descriptive confidence vs calibrated confidence
- forced devil's advocate / pre-mortem / self-consistency lanes
- identifying infrastructure-blocked ideas that should not be overclaimed as already present

Treat them as council realism aids. They help later agents describe the current council honestly and choose bounded improvements, but they do not magically calibrate current confidence surfaces or convert one-model prompting into a true ensemble.

## Prompt Discipline Skeleton

When the question is not merely "what should continue" but "how should the extraction or transfer prompt itself be structured", open:

- `docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`
- `docs/architecture/TONESOUL_PROMPT_VARIANTS.md`
- `docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md`

Use it for:

- one-line success state
- `P0/P1/P2` prompt priority
- high / medium / low confidence classification
- `[資料不足]` recovery flow
- stability-band sorting
- compression ladder design
- receiver instruction design
- choosing between project continuity, meeting distillation, operator snapshot, council replay, and session-end handoff variants
- starting from a bounded card instead of a blank prompt

Treat it as a prompt-design companion, not as a universal runtime prompt or a replacement for code, schemas, or current contracts.
