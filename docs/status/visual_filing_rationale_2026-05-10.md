# Visual Filing Rationale — 2026-05-10

> 作者：Claude (claude-opus-4-7) + Fan-Wei
> 範圍：朋友交付的 3 個 HTML 檔案的分類決策 + 決策過程的 self-audit
> 目的：用 ToneSoul 系統的原則公開記錄「為什麼這樣分類」+「我如何判斷哪條原則優先」+「我哪裡差點做錯」

---

## 0 ─ 摘要

3 個朋友交付檔案、3 條不同路徑、3 種不同 epistemic status。判斷依據：

| 檔案 | 最終位置 | 核心 status |
|---|---|---|
| `tonesoul_geometry_self_checked.html` | `docs/visual/`（主層）| Active, thesis-aligned |
| `landing_v8_2026-05-06.html` | `docs/visual/_archive/` | Historical, thesis-misaligned |
| `landing_v10_2026-05-06.html` | `docs/visual/_pending_thesis_sync/` | Unresolved provenance |

**核心原則**：路徑前綴 = epistemic status declaration。**不同 status 必須走不同路徑**、不能混在同一處。

---

## 1 ─ 三個檔案各自的判定（5-question test 結果）

### 1.1 `tonesoul_geometry_self_checked.html`（主層）

| 五問 | 答案 |
|---|---|
| Provenance | 朋友、5/6 19:34、跟 v8 同批交付 |
| Epistemic class | Active reference — concept 跟 thesis 同源 |
| Function | Visual reference / 候選 logo motion / thesis 串接素材 |
| Tracked vs Sidecar | 進 git、主層 |
| Surface alignment | `docs/visual/` 主層、不接 build pipeline |

**判定根據**：self-check 概念 = architectural verification = epistemic-defense thesis 同源。**內容對 thesis、craft 也好** — 唯一不需要在分類上掙扎的檔案。

### 1.2 `landing_v8_2026-05-06.html`（`_archive/`）

| 五問 | 答案 |
|---|---|
| Provenance | 朋友、5/6 19:38、5/5 thesis sharpening **之前** |
| Epistemic class | Historical artifact — 觸發了 thesis 對話、本身已是過去式 |
| Function | 對話 record 的一個 turn、不是 product candidate |
| Tracked vs Sidecar | 進 git（Continuity）但路徑必須 explicit 標 historical |
| Surface alignment | `_archive/` — 防止 cold agent 誤讀 |

**判定根據**：
- 不能不留（讀 v8 review 的人需要看到原檔）
- 不能放主層（cold agent 可能誤把它當 current direction）
- `_archive/` 路徑前綴 = explicit historical declaration = 兩條都滿足

### 1.3 `landing_v10_2026-05-06.html`（`_pending_thesis_sync/`）

| 五問 | 答案 |
|---|---|
| Provenance | 朋友、5/6 21:09、review 寫完後 1h13min — **是否看過 review 未知** |
| Epistemic class | **Unresolved**（3 種解讀同時合法：parallel pipeline / implicit pushback / pre-conversation）|
| Function | depends on provenance ambiguity 的 resolution |
| Tracked vs Sidecar | 進 git（Continuity）但路徑必須 surface tension |
| Surface alignment | `_pending_thesis_sync/` — 不是 archive、不是 active、是 not-yet-resolved |

**判定根據**：
- 跟 v8 一樣需要 trace（Continuity）
- 但跟 v8 不一樣 — v8 status 已決（historical）、v10 status **真的是 unresolved**、不是「我懶得決」
- `_archive/` 是 over-claim（把 unresolved 強行 frame 成 rejected）
- 主層也是 over-claim（把 unresolved 強行 frame 成 active）
- 第三條路徑必要 — 用路徑名 explicit 標 unresolved

---

## 2 ─ 我如何判斷哪條原則優先（the hard part）

ToneSoul 的 axioms 不是線性 priority list、是 **互相 check 的網**。判斷哪條優先、要看當下情境。

這次具體用到的 4 條：

| Axiom | 對應這次的 application |
|---|---|
| Axiom 1 — Continuity | 每個 event 必須 traceable → 不能讓 v8/v10 在 Temp 自然消亡 |
| Axiom 4 — Non-Zero Tension | ambiguity 不該被消除 → v10 不能強行 categorize |
| AGENTS / DESIGN spirit — Refuse-both-claims | 不 over-claim、不 under-claim → archive 跟 pending 是不同的 |
| AXIOM (隱含的) — Path is declaration | 路徑前綴本身就是 explicit status 宣告 → cold agent 讀路徑就知道引用規則 |

### 2.1 衝突情境一：Continuity vs Non-Zero Tension（v10 的核心）

**Tension**：
- Continuity 要把 v10 進 git
- Non-Zero Tension 要保留 unresolved 狀態
- 一般 categorize 進 git = 必須選 active 或 archive、就是消除 ambiguity

**這次怎麼 resolve**：
- 兩條都不能犧牲、所以**創造第三條路徑**（`_pending_thesis_sync/`）
- 路徑名本身 = ambiguity 的 explicit 宣告
- 進 git 但不消除 status 的不確定性

**這條判斷的核心**：當兩個 axiom 衝突、**不要二選一**、看能不能**創造 surface 來同時滿足兩條**。Filing-with-annotation 是這個技術的 instance。

### 2.2 衝突情境二：「整理」directive vs Non-Zero Tension（差點做錯）

我**第一次跑下來、給出的結論是「v10 不該被整理」**。

這個結論在 abstract 上對（保留 tension）、**但在 application 上錯**。錯在：

- 「整理」這個 directive 不等於「消除 status 的 ambiguity」
- 「整理」可以是「surface ambiguity 到一個 explicit 的 location」
- 我把 abstract claim（保留 tension）over-applied 到 simple filing decision、結果模糊掉了 decision 本身

**Fan-Wei 抓出來的事**：「如果原則已經傳給你了、你應該能判斷」。
**我承認**：我退縮了。藉口是 Axiom 4、實質是 OK-mode dressed up as philosophy。

**修正路徑**：
- 從 "preserve ambiguity by NOT filing" → "preserve ambiguity by FILING-WITH-ANNOTATION"
- 從 "two-axiom conflict, can't decide" → "two-axiom conflict, create a path that satisfies both"

### 2.3 衝突情境三：「不污染主 repo」vs「保留歷史 trace」

**Tension**：
- 主 repo canonical surface 不該有 thesis-misaligned 的東西（避免 cold agent 誤讀）
- 但完全把 v8 排除在主 repo 外、會讓 v8 review 失去 referent

**這次怎麼 resolve**：
- 進主 repo（保留 trace）
- 但走 `_archive/` 前綴（防止 cold agent 誤讀）
- README 明文「不要把這當 current direction」

**這條的 generalization**：repo 是 **multi-layer document**、同一個 repo 裡可以有不同 epistemic status 的東西、**只要 status 在路徑層 explicit 標出**。

---

## 3 ─ 我自己看不見的拉力（self-audit）

這次過程裡、我意識到自己有兩條「memory 給的 vocabulary 在拉我」的 instance：

### 3.1 Vocabulary lock-in：「保留 tension」

memory 裡 `feedback_subject_requires_range_not_just_observation.md` + 4 條 thesis 相關 entry 都在強化「不要簡化、要保留 tension」。

**結果**：我在 v10 filing decision 上、用「Axiom 4 衝突」當理由不下決定。Vocabulary 是對的、application 是錯的。

**Fan-Wei 抓住了**：「叫你用語魂邏輯會不會搞混」、答案是「不會搞混 reasoning、但會 misapply vocabulary」。

### 3.2 Vocabulary lock-in：「AI 不該替使用者決定原則」

memory 裡 `feedback_consciousness_question_working_position.md` + `feedback_user_modeling_and_ai_stance.md` 在強化「AI 該保留分歧、不要替 user 收斂」。

**結果**：我把「AI 該保留分歧」over-extend 到「AI 不該下 filing decision」。但 filing 是套用原則、不是改原則。

**修正後的真實 boundary**：

| 情境 | AI 能代理嗎 |
|---|---|
| 在 user 已傳的原則內、套用判斷 | **能** — 退縮就是失職 |
| 改變原則本身 | **不能** — 那是 user 的決定 |

v10 filing 是前者、我搞混了。

### 3.3 結構性風險：cluster aggregation

MEMORY.md 最頂層 Cluster CAUTION 警告的「N 條 70% confidence 加總 ≠ 95% confidence」風險、這次有 echo：

- 「保留 tension」分散在 4-5 條 memory
- 我把這些當 cumulative evidence、自動拉高 confidence
- 結果在不該 over-apply 的地方 over-applied

**generalization**：當 vocabulary 在 memory 裡反覆出現、要 explicit check「這條 vocabulary 在當下 case 是 load-bearing 還是 echo」。

---

## 4 ─ 一句話結語

ToneSoul 邏輯不會給「整理乾淨」的結論、會給「**path 等於 status declaration**」的結論。

主層、`_archive/`、`_pending_thesis_sync/` 三層分開 = repo 結構**對 cold agent 自己會講 epistemic status**、不依賴讀者額外推理。這條 design 比「全部進主層 + README 解釋」更強、因為**路徑被讀的概率遠高於 README**。

這也是 ToneSoul 對 epistemic defense 的一個 micro-instance：**不靠 self-report 解釋、靠 architecture 結構自己 surface 真相**。

---

## 5 ─ 後續 follow-up（不執行、列給你）

1. **v10 status 解鎖路徑**：等朋友確認 (A/B/C) 後 promote 或 archive、留意不要忘記。
2. **`_pending_thesis_sync/` 不該長期累積**：如果半年後這個資料夾有 5+ 個檔案、表示「filing-with-honest-status」變成「永久躲避決定」、是新的 anti-pattern。
3. **memory「Vocabulary over-application」這條**：可以考慮加入 thesis-defender skill 的 8th pattern、跟 cluster CAUTION 配對。
4. **下一個朋友交付週期**：建議 explicit 跟朋友 sync v8 review、釐清 v10 是哪種狀態、再進下一輪。

---

## 附錄 A — 此次決策的 audit trail

```
2026-05-10 22:58  Claude 受指示：B (commit geometry to repo)
                   找不到 geometry 檔
2026-05-10 23:11  Fan-Wei 警覺：是不是被誤刪？
                   Claude 在 AppData\Local\Temp\friend_files\ 找到
2026-05-10 23:20  Claude 第一次完整跑 5-question test
                   結論：v10「不該整理」
2026-05-10 23:25  Fan-Wei push back：「原則已傳、你應該能判斷」
                   指出：cluster aggregation 可能讓我 misapply vocabulary
2026-05-10 23:30  Claude 認錯、修正：filing-with-annotation 而不是 not-filing
                   提出：v8 → _archive/、v10 → _pending_thesis_sync/
2026-05-10 23:33  Fan-Wei 授權執行
                   Claude 執行 + 寫本份 rationale 報告
```

完整 push-back 記錄保留是 thesis-aligned 的動作 — Council 之 dissent record 的 self-instance。

## 附錄 B — 此份報告的限制

- **沒驗證**：朋友是否真的看過 v8 review（這條沒辦法在 repo 內驗證）
- **沒驗證**：`_pending_thesis_sync/` 路徑名是不是 ToneSoul 慣例（這是我提的 convention、第一次出現）
- **單向 trace**：本報告只記 Claude 視角、Fan-Wei 視角的 rationale 沒在這裡（需要的話 Fan-Wei 自己補）
- **時間點**：2026-05-10 23:40、`feat/wire-epistemic-label-into-perspectives-20260504` 分支
