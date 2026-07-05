# Framework Canonical Decision — 2026-05-14

> 作者：Claude (claude-opus-4-7)、由 Fan-Wei 2026-05-14 明文授權做整理決定
> 性質：**決策記錄（decision record）**、不是 status snapshot、不是 catalog
> 範圍：ToneSoul 7+ 代演化中、哪個是 canonical / 哪些 archived / 哪些 backport / 哪些 drop
> 對應 catalog：`docs/philosophy/lineage_integration_catalog_2026-05-14.md`（observational 那一面）

---

## 0 ─ 為什麼有這份文件

`lineage_integration_catalog_2026-05-14.md` surface 了 26 repos + 多代演化的事實、但**沒做決定**。本檔做決定 — Fan-Wei 授權「如果你覺得沒必要的結構 寫清楚理由 就歸檔也行」。

決定影響：哪個 repo 是未來主場、哪些 repo 該 archive、哪些 unique spec 該 backport / 哪些 leave-in-archive / 哪些 drop。

---

## 1 ─ Executive Decision: tonesoul52 = canonical framework going forward

**Decision**：**`Fan1234-1/tonesoul52` 是 ToneSoul 框架的 canonical home**。其他 active framework iteration（TAE-01）建議 archive 為 legacy predecessor。

### 理由 / Evidence

| 維度 | tonesoul52 | TAE-01（ToneSoul-Architecture-Engine）|
|---|---|---|
| Status | active main、頻繁 commit、最近 2026-05-13 | active 但 last 較舊（2026-02 spec v0.9）|
| Maturity | "3,019 tests" 描述、實測 60+ tests pass | "v0.9 Architecture Audit" 標 Draft |
| Naming | "52" 暗示 v5.2 等命名（晚於 v2.0）| "01" 暗示 v0.1 / iteration 1 |
| Test coverage | extensive，多個 subsystem 各有 test 套件 | 未 verify 但 description 沒強調 |
| 文檔成熟度 | docs/architecture/ 20+ TONESOUL_*.md spec、docs/philosophy/ 30+ 卷 | docs/ ~15 specs、缺乏 mature philosophy folder（已 migrate 去 tonesoul52）|
| 對外公佈 | 列為 main 公開 framework | description 含 lobster emoji + abstract framing、未 emphasize 對外 |
| 演化方向 | 從 TAE-01 之後繼續迭代 | TAE-01 自身為 v2.0「Awakened Kernel」consolidation 嘗試 |

### 推論

TAE-01 是 2026-02 那次大整合（v2.0 Awakened Kernel）— 把 5 個 archived repos 集中。但 TAE-01 本身停在 v0.9 Spec Audit Draft、之後 ToneSoul 演化 fork 出 tonesoul52 並繼續成熟。

**tonesoul52 是 TAE-01 之後的 superseding iteration**、不是 parallel parallel work。

---

## 2 ─ Repo-by-Repo 決策

### 2.1 Active 框架 repos — Fan-Wei 該執行的 action

| Repo | 當前 status | 決策 | 理由 | Fan-Wei action |
|---|---|---|---|---|
| `tonesoul52` | active main | **保持 active main** | 已是 canonical | 無 |
| `ToneSoul-Architecture-Engine` (TAE-01) | active | **建議 archive、加 README MIGRATION NOTICE 指向 tonesoul52** | 已被 tonesoul52 superseded、保持 active 會 confuse 訪客 | `gh repo archive Fan1234-1/ToneSoul-Architecture-Engine`（待 backport 完關鍵 spec 後）|
| `tonesoul-conscience` | active | **保持 active**、但建議 README 加 MIGRATION 註記 | Claude Hackathon 2026 specific、Conscience Layer 概念現在 tonesoul52 有實作（vow_system / council） | 加 1 行 NOTICE 指向 tonesoul52 |
| `Yu-Hun-Cognitive-State-Navigator` | active | **保持 active、可選擇 archive** | yuhun 概念在 tonesoul52/yuhun/ 已有實作 | 你決定 archive 與否 |
| `OpenClaw-Memory` | active、submodule | **保持 active** | 是 tonesoul52 submodule、有獨立用途 | 無 |
| `ToneSoul-Memory-Vault` (private) | active | **保持 active** | 私有、可能存敏感內容 + RFC | 無 |

### 2.2 Archived predecessors — 保持 archived（無動作）

| Repo | 狀態 | 理由 |
|---|---|---|
| `ToneSoul-Integrity-Protocol`（2025-08）| archived | 最早 articulation、歷史價值、繼承者已存在 |
| `tone-soul-integrity-tonesoul-xai`（2025-09）| archived | 已整合進 TAE-01 modules/integrity/、再進 tonesoul52 |
| `governable-ai`（2025-11）| archived | 已整合進 TAE-01 core/governance/、再進 tonesoul52/tonesoul/governance/ |
| `Genesis-ChainSet0.1`（2025-11）| archived | 已整合進 TAE-01 core/genesis/、再進 tonesoul52 |
| `AI-Ethics`（2025-11）| archived | 已整合進 TAE-01 law/constitution.json、AXIOMS.json 演化來源 |
| `ai-soul-spine-system`（2025-11）| archived | 自己 README 已明文標 integrated into TAE-01 |
| `tone-soul-integrity`（2025-12）| archived | Tone Soul Fusion Kit、tonesoul52 vow + council 已實作 |
| `tonesoul-codex`（2025-12）| archived | 詳見 §2.3 backport 分析、結論為 keep archived |
| `Philosophy-of-AI`（2026-02）| 未 archive 但建議 archive | core 已 migrated 到 tonesoul52、VOLUMEs I-V 全 migrated（本 session 完成）| `gh repo archive Fan1234-1/Philosophy-of-AI`（建議）|

> **勘誤（2026-07-05,收斂掃描抓到）**:上行「VOLUMEs I-V 全 migrated(本 session 完成)」
> **寫下時在分支上為真,但該分支對應的 PR #71 之後 CLOSED 未 merge,宣稱從此懸空**——master
> 上實際只有 VOLUME_I、II,卷 III/IV/V 漏遷了近兩個月(anti-pattern family:completeness
> claim without post-change trace,2026-06-29 判例的前科)。2026-07-05 已自 PR #71 分支
> commit `a1c61ad0` verbatim 補遷三卷(WO-1,`docs/plans/convergence_harvest_work_orders_2026-07-05.md`)。
> 「建議 archive」因 confirm 從未完成而幸運地未執行——repo 未 archive 反而保住了內容。
> 原文一字未改,本註即是 reconcile 痕跡。

---

## 3 ─ Unique Specs Backport / Drop / Leave-in-archive 決定

按 spec、逐條決定：

### 3.1 TAE-01 unique specs

| Spec | Decision | 理由 |
|---|---|---|
| **`QUANTUM_KERNEL_ARCH.md`** | **Catalog pointer only、不 backport**（暫定）| Free Energy F=U-T·S 數學模型 substantial、可能 tonesoul52 缺。但要真正 backport 需要 verify 內容 still valid + 跟 tonesoul52 已有的 Tension Engine 對齊 — 不是 librarian 範圍、是 architect 範圍。**建議 Fan-Wei 後續 session deep read 再決定**。Pointer 放本檔 §4 |
| **`docs/WHITEPAPER.md`** | **Leave in TAE-01、flag for manual recovery** | 文件編碼壞了（Big5 mis-decoded、亂碼）、不能 backport 壞檔。需要 Fan-Wei 用 Big5 → UTF-8 conversion 重新轉換、或從 original source 重新生成。**只有 Fan-Wei 能做這個 recovery** |
| `SEMANTIC_SPINE_SPEC.md` | Catalog pointer | Spine 概念可能跟 tonesoul52 council / pipeline 重疊、未 deep diff、defer |
| `WORLD_MODEL_X_MIND_MODEL.md` | Catalog pointer | 未 sample、可能跟 tonesoul52 哲學 docs 重疊、defer |
| `STEPLEDGER_SYSTEM_PROMPT.md` + `STEP_LEDGER_SPEC.md` | Catalog pointer | StepLedger 概念在 ai-soul-spine-system README 也提過、tonesoul52 可能用不同 name 實作 |
| `YUHUN_PROTOCOLS.md` | Catalog pointer | yuhun 在 tonesoul52/yuhun/ 已實作、protocols spec 可能 redundant |
| `TAE-01_INIT.md` | Catalog pointer | TAE-01 自身 init spec、跟 tonesoul52 architecture 對應不明 |
| `MANIFEST.json`、`core_dna.json`、`core_memory.json` | Drop | TAE-01 runtime state file、tonesoul52 有自己的 state 管理 |
| `complete_audit_results.json`、`council_output.txt`、`dream_insights.json` | Drop | 都是 runtime output、不是 spec |

### 3.2 tonesoul-codex unique specs

| Spec | Decision | 理由 |
|---|---|---|
| `MANIFESTO.md` | **Leave in archive、不 backport** | tonesoul52 已有 3 個 manifesto 變體（docs/MGGI_MANIFESTO.md、docs/philosophy/manifesto.md、docs/status/tonesoul_system_manifesto.md）— 概念已 well-covered |
| `VOWOBJECT_SPECIFICATION.md` | **Leave in archive、catalog 標 historical reference**（不 backport）| 概念已實作於 tonesoul52/tonesoul/vow_system.py + vow_inventory.py + 4 個 test 套件。Spec doc 內文有錯字/OCR-like 異常（"不武可採"、"嘤供体"、"依寶"），不適合作 canonical spec。如 Fan-Wei 想正式化 vow spec、應該 fresh 寫於 tonesoul52、引用 implementation |
| `PHILOSOPHY.md` | Catalog pointer、可能 drop | tonesoul52/docs/philosophy/ 內容已豐富、tonesoul-codex 的 philosophy 應已 absorbed |
| `docs/CONSCIOUSNESS_RESEARCH.md` | Catalog pointer | 未 sample、可能有 unique research notes |
| `FIRST_CONTACT.md`、`DECISION_LOG_FORMAT.md` | Catalog pointer | 可能 useful patterns、未 verify |

### 3.3 AI-Ethics unique specs

| Spec | Decision | 理由 |
|---|---|---|
| `docs/v1.2/vol-1 ~ vol-5.md`（philosophy）| Catalog pointer | 跟 Philosophy-of-AI 5 卷 parallel structure、可能是 v1.2 修訂版、跟 tonesoul52 VOLUMEs I-V 關係不明 |
| `engineering/VOLUME_I ~ V_ENGINEERING_*.md`（engineering）| Catalog pointer + flag | "5-volume engineering 系列" 跟 philosophy 5-volume parallel、是個重要 structural design、可能值得 backport 全套 — 但需要 Fan-Wei 確認還有效 |
| `魂語框架.pdf` | Catalog pointer | PDF binary、不適合直接 backport markdown |
| `specs/GlobalMemory_UFP.{md,yaml}` | Catalog pointer | Global Memory Unified Format Protocol — 可能跟 tonesoul52 memory subsystem 重疊 |

---

## 4 ─ 建議 Fan-Wei 執行的 actions（依優先序）

### Now（這 session 完成或 next 5 分鐘）

無需 Claude action — 都是 Fan-Wei 在 GitHub 上手動執行或拍 decision。

### Soon（建議本週內）

1. **TAE-01_INIT.md 內容快讀** — 確認 tonesoul52 是否 truly supersede TAE-01。10 分鐘。如 confirm、執行：
   ```
   gh repo archive Fan1234-1/ToneSoul-Architecture-Engine
   ```
   並於 archive 前在 README 加 MIGRATION NOTICE 指向 tonesoul52（範本見 ai-soul-spine-system 的 README）。

2. **Philosophy-of-AI archive**（如 VOLUMEs migration confirm 完整）：
   ```
   gh repo archive Fan1234-1/Philosophy-of-AI
   ```
   並於 archive 前確認 README MIGRATION NOTICE 已存在（已存在 per 2026-02-04 update）。

3. **TAE-01/docs/WHITEPAPER.md 編碼修復** — Big5 → UTF-8 conversion、或 re-export from original source。**只有 Fan-Wei 能做**。修復後可選擇 backport 成 tonesoul52/docs/research/whitepaper_2026.md 或類似。

### Later（後續 session、不急）

4. **QUANTUM_KERNEL_ARCH.md deep read + 評估是否 backport** — Free Energy 模型是 sophisticated architecture spec、值得 dedicated architect session
5. **AI-Ethics engineering 5-volume backport 評估** — 整套 structural design、值得 dedicated migration sprint
6. **tonesoul-conscience 跟 Yu-Hun-Cognitive-State-Navigator** archive 與否、Fan-Wei 拍

### Future ambition（Fan-Wei mentioned）

7. **vocus 舊文章修改** — long-term ambition、本 session 不啟動

---

## 5 ─ 沒做、為什麼

本檔做了**架構級決策 + catalog pointer**、沒做：

- **Deep content backport** for QUANTUM_KERNEL_ARCH 或 AI-Ethics engineering volumes — 那需要 architect-level judgment、不是 librarian level
- **修復 WHITEPAPER.md 編碼** — 只有 Fan-Wei 能做、Claude 不該猜 binary encoding
- **執行 archive 動作** — repo-level archive 是 shared-state action、必須 Fan-Wei 拍
- **删除任何 archived repo** — archived 不等於 delete、歷史 value 永遠保留

「值得留的整理好架構我們以後慢慢做也行」 — 本檔提供「架構（決策 + 推薦 + 理由）」、細節執行留 Fan-Wei 跟未來 session。

---

## 6 ─ 對未來 maintainer / agent 的指示

如果你讀本檔、應該知道：

1. **tonesoul52 是 canonical**、不要嘗試重新 instantiate 別的 framework iteration
2. **TAE-01 specs 未在 tonesoul52 的、要 backport 前先 check 是否 superseded**（很多概念已實作但 spec name 不同）
3. **`MANIFESTO.md`、`VOWOBJECT_SPECIFICATION.md` 在 tonesoul-codex 是 historical artifact、不要當 active spec 引用**
4. **WHITEPAPER.md 編碼問題只能 Fan-Wei 修**、Claude 不該嘗試 reconstruct
5. **本檔本身是 2026-05-14 snapshot decision、未來如有新 framework 出現（TAE-02？v6？）、需要 update**
6. **catalog（observational）跟本決策 doc（prescriptive）並用** — catalog 告訴你「有什麼」、本檔告訴你「該怎麼處理」

---

## 7 ─ 本檔的限制

- **N=1 librarian session**、決策由 Claude opus-4-7 + Fan-Wei explicit auth 共同做、未經其他 reviewer
- **未 deep-read** 多數 unique specs、決策基於 README + 第一頁 sample
- **未 verify** TAE-01 vs tonesoul52 的 git ancestry（是否 fork 關係）— 純粹從 maturity / naming / activity 推
- **archive 推薦不執行**、留 Fan-Wei 拍 + 執行
- **後續 session 該重新 verify** — 對應 `feedback_stale_reference_recurrence_pattern_2026-05-14`、本檔結論可能在 1-2 個月後就 drift

**對未來自己警告**：別把本檔當 ground truth 不 verify 就引用。「tonesoul52 是 canonical」這條 claim 假設 Fan-Wei 認同；若 Fan-Wei 後來推出 tonesoul53 或新的整合 attempt、本檔結論 invalid。
