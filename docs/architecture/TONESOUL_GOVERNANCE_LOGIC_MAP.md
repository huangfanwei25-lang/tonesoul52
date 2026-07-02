# ToneSoul Governance Logic Map — 治理邏輯地圖

> Purpose: 把散在 `unified_pipeline.py` / `council/` / `governance/` / `runtime_adapter.py` 裡的治理決策路徑,整理成一張**以實際執行順序為準**的邏輯地圖,供後續開發、審查、與外部稽核使用。
> Last Updated: 2026-07-02
> Status: document-backed (E4)。本文件是對程式碼的**描述**,不是程式碼本身;任何不一致以程式碼為準(`docs/POSITIONING.md` 原則)。逐項標注證據等級。
> Provenance: 2026-07-02 外部稽核(全測試 8053 passed / ruff clean / demo 可跑)過程中,由 AI 協作者逐檔追線整理;`file:line` 錨點在整理當日驗證存在。
> Claim boundary: 遵守 `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md` — 本文只描述可觀察的執行路徑(B 層)與已標注的機制限制(A 層),不做能力詮釋(C 層)。

---

## 0. 一句話的脊椎

整個治理系統回答一個問題:**答案為什麼變成答案**。
每一個 gate 的存在理由,都是在「模型草稿 → 對外輸出」之間留下一個可回溯的判斷點。以下按實際執行順序列出這些判斷點。

證據等級沿用 `docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md`:

- **E1 test-backed** — 有回歸測試釘住
- **E3 runtime-present** — 程式存在且會執行,測試深度較薄
- **E4 document-backed** — 文件描述意圖,runtime 未證明
- **E5 philosophical** — 設計命題

---

## 1. 決策路徑(`UnifiedPipeline.process()` 實際順序)

主入口:`tonesoul/unified_pipeline.py:1840`。以下階段編號對應原始碼中的 `# ==========` 區塊註解。

### 前段:路由與姿態

| # | 階段 | 模組 | 判斷 | 等級 |
|---|------|------|------|------|
| 1 | **ComputeGate 路由** | `gates/compute.py` | 依 user tier、訊息長度、初始張力、governance friction 決定路徑:`route_local_llm` / `route_single_cloud` / `route_full_council` / `block_rate_limit`,並產生 governance depth plan(light/standard/…) | E1 |
| 2 | **Drift 監測** | `drift_monitor.py`(Phase 544) | 結構層錨點;drift summary 附掛到 dispatch trace,不直接阻擋 | E3 |
| 3 | **Governance Reflex Arc(前段)** | `governance/reflex.py` | `ReflexEvaluator.evaluate(GovernanceSnapshot)` 產生 gate_modifier,調整後續 gate 的鬆緊 | E1 |
| 4 | **AlertEscalation L1/L2/L3** | `alert_escalation.py`(Phase 545) | 分級告警,L2/L3 觸發 graduated response | E3 |
| 5 | **內在審議** | (ToneSoul 2.0 區塊) | 生成前的內部立場預演 | E3 |

### 中段:承諾與脈絡

| # | 階段 | 模組 | 判斷 | 等級 |
|---|------|------|------|------|
| 6 | **承諾堆疊載入(Axiom 3)** | `constraint_stack.py` | 載入歷史 SelfCommit;偵測到與新輸入矛盾時注入早期警告 | E1 |
| 7 | **脈絡檢索** | GraphRAG / semantic trigger / `memory/hippocampus.py` | 高張力重現檢查 + 潛意識檢索,餵入增強 prompt | E3 |
| 8 | **LLM 生成** | `llm/`, `local_llm.py` | 產生草稿 — **草稿不是輸出**;後面全部 gate 都作用在這之後 | E1 |

### 後段:審議與輸出關卡(核心)

| # | 階段 | 模組 | 判斷 | 等級 |
|---|------|------|------|------|
| 9 | **Reflection Loop** | `reflection.py` | 最多 `MAX_REVISIONS=2` 次修訂;預算耗盡時**誠實承認不收斂**(fail-stop),不假裝收斂(Axiom 5 紀律) | E1 |
| 10 | **Council 審議** | `council/runtime.py:233 deliberate()` | 見 §2。可產生 `council_block` / `council_rewrite` | E1 |
| 11 | **LLM 呼叫預算 fail-stop**(Phase 852) | pipeline 內 | 驗證用 LLM 呼叫超出預算 → 停止,不無限自我修補 | E1 |
| 12 | **語場斷裂偵測(Axiom 3)** | pipeline 內 | 偵測回應與承諾堆疊的斷裂 | E3 |
| 13 | **SelfCommit 提取 + 記憶更新** | `constraint_stack.py`, `memory/` | 新承諾入堆疊;記憶單元更新 | E1 |
| 14 | **PersonaDimension 後處理** | `persona_dimension.py` | 可觸發 `persona_dimension_rewrite` | E3 |
| 15 | **Reflex Arc 最終 gate** | `_apply_reflex_final_gate`(定義於 `unified_pipeline.py:599`,呼叫於 `:3391`;機制由 `governance/reflex.py` 的 ReflexAction/ReflexEvaluator 提供) | `ReflexAction.BLOCK` 時**整段輸出被替換** — 這是 vow 零容忍與 council BLOCK 的最終執行點 | E1 |
| 16 | **De-escalation 套用(Axiom 7 reframed)** | `governance/de_escalation.py` | 即時張力 > `SOUL.tension.high_tension_threshold` 時,附加降溫框架(非破壞性、冪等);pipeline 測試釘住「高張力→有框架、低張力→無」 | E1 |
| 17 | **POAV gate** | `poav.py`, `unified_pipeline.py:625` | 高風險路徑 0.92 / 低風險 0.70(`soul_config.py:139-140`);不足 → `poav_block`。**已知限制:感測器是英文詞彙統計,非語義共識;非高風險路徑 record-only** | E1(gate)/ E3(感測深度) |
| 18 | **Consumer contract 檢查** | `consumer_contract.py`, `contract_observer.py` | 違約 → `contract_block` | E3 |
| 19 | **repair_stages 記錄** | pipeline 內 | 所有觸發過的修補階段(`council_block`, `poav_block`, `reflex_block`…)以序列形式進 trace — 這就是「答案為什麼變成答案」的直接證據 | E1 |

### 落地:不可變承諾

| # | 階段 | 模組 | 判斷 | 等級 |
|---|------|------|------|------|
| 20 | **Responsibility audit 蓋章(Axiom 2)** | `governance/responsibility_audit.py` | 每筆 committed trace 在進鏈**之前**蓋上 responsibility_audit 標記(峰值張力 severity vs threshold,Aegis veto / vow violation 提升) | E1 |
| 21 | **Aegis 雜湊鏈提交** | `runtime_adapter.py:1919 _commit_locked_posture` → `aegis_shield.py` | trace 進入不可變雜湊鏈(Isnād 譜系);**fail-closed**:aegis_shield 匯入失敗不會靜默降級(原始碼註解明言此事故教訓) | E1 |

---

## 2. Council 子系統邏輯

### 2.1 兩套審議系統並存(這不是 bug,但要知道)

| 系統 | 角色 | 位置 | 關係 |
|------|------|------|------|
| **Council(五視角)** | Guardian / Analyst / Critic / Advocate / Axiomatic | `council/perspectives/` | 主審議面,pipeline §1-10 呼叫 |
| **Deliberation(三視角)** | Muse(創想)/ Logos(理則)/ Aegis(守護) | `deliberation/perspectives.py` | 獨立模組,adaptive rounds / gravity 機制 |

歷史上曾有角色數量不一致的稽核發現;目前兩者是**明確分開的模組**,glossary(`docs/GLOSSARY.md` council 條目)把兩者都列入計算責任。引用時務必指明是哪一套。

### 2.2 投票 → 裁決的映射

```
每個 perspective 投票 (council/types.py):
  APPROVE | CONCERN | OBJECT | ABSTAIN
          ↓ 聚合 (council/verdict.py generate_verdict)
整體裁決 (VerdictType):
  APPROVE          — 放行
  REFINE           — 退回修訂 (→ council_rewrite)
  DECLARE_STANCE   — 分歧誠實外顯:同意誰、反對誰、分歧核心為何,把決定權交還使用者
  BLOCK            — 阻擋 (→ council_block → reflex final gate 執行替換)
```

術語紀律:glossary 說 council「沒有投票機制」,意指**沒有多數決裁決**(少數意見被保留;Guardian+Axiomatic 雙重 CONCERN 是**類別覆寫**——直接強制 REFINE、無視 coherence 分數,不是數值加權,見 `verdict.py:213-226`);但 perspective 層確實有 vote 這個詞(`voting_evolution.py`)。寫文件時建議用「投票≠多數決」表述,避免字面矛盾。

### 2.3 Council 內建的誠實機制

- **Escape valve**(`escape_valve.py`, `council/runtime.py:321`):偵測到系統性失效 → 直接改判 BLOCK 並在 transcript 標記 `honest_failure` — 寧可承認壞掉,不輸出假裝正常的結果。
- **Persona uniqueness audit**(`council/persona_audit.py`):檢查五視角是否退化成同一個聲音(呼應 Axiom 4 非零張力;`deliberation/gravity.py` 的 ECHO_CHAMBER 旗標是同一原則的另一實作)。
- **Grounding**:`UNGROUNDED_CONFIDENCE_CAP = 0.6`(`council/types.py:57`)— 無證據支撐的宣稱,信心值有硬上限。
- **五視角獨立性的邊界**:單模型配置下,五視角是同一 draft 上的 heuristic voters,**不是五個獨立心智**;獨立性只在 multi-model 配置下部分成立(README「What Currently Exists」已如實標注)。

---

## 3. 公理 → 執行點對照(佈線索引)

`AXIOMS.json` 的 enforcement 欄位是權威來源(0 fully enforced / 8 partial / 1 referenced, as of 2026-06-15);此表只做**佈線索引**,方便從公理跳到程式碼:

| 公理 | 執行點 | 已知窄化 |
|------|--------|----------|
| E0 選擇先於身份 | guardian/axiomatic OVERCLAIM_PHRASES(zh+en) | 片語比對,非語義 |
| 1 連續性 | `time_island.py`(opt-in ~13 call sites)+ Aegis chain | 無全域強制 |
| 2 責任閾值 | `governance/responsibility_audit.py` → 每筆 trace 蓋章 | 風險是峰值代理;閾值以下仍全部進鏈 |
| 3 治理 gate(POAV) | `unified_pipeline.py:625`,0.92/0.70 讀自 `soul_config` | 感測器是英文詞彙統計;縮寫仍有三種展開待定 |
| 4 非零張力 | `deliberation/gravity.py` ECHO_CHAMBER(<0.3)+ axiomatic CONCERN | 閾值硬編碼 |
| 5 鏡像遞迴 | `reflection.py` MAX_REVISIONS=2 + 誠實 fail-stop | accuracy 增益無法測量,**刻意**維持 referenced,不捏造指標 |
| 6 使用者主權 | vow 零容忍 → guardian OBJECT → reflex final gate 替換輸出 | harm detection 僅 3 個英文字面片語;改寫與非英文(含 zh-TW)穿透 |
| 7 語義場守恆(reframed) | `governance/de_escalation.py` + pipeline 附加降溫框架 | 附加框架,非重生成;僅 >threshold 觸發 |
| 8 記憶主權 | `memory/sovereignty_gate.py`(handoff TRANSFER 需同意 token;training EXPORT 預設去識別化) | 中央 write_payload 刻意不 gate;`inter_soul/sovereignty.py` field map 缺 Axiom 8 |

---

## 4. 驗證拓撲:誰在驗證驗證者

治理系統自己也被治理。目前的檢查層:

| 檢查器 | 驗證對象 | 產物 | 觸發 |
|--------|----------|------|------|
| `pytest`(8054 collected) | 機制層行為 | CI | 每次 PR |
| `ruff` | 程式碼衛生 | CI | 每次 PR |
| `scripts/verify_abc_firewall.py` | 入口文件的 claim 邊界(7 entrypoints、禁語掃描) | `docs/status/abc_firewall_latest.*` | 手動/CI |
| `scripts/verify_skill_registry.py` | `.agent/skills/` 與 `skills/registry.json` 的一致性 + 完整性雜湊 | healthcheck 子項 | healthcheck |
| `scripts/run_repo_healthcheck.py` | 上述全部 + attribution / friction / audit_7d | `docs/status/repo_healthcheck_latest.*` | 排程/手動 |
| 7D audit(`docs/7D_AUDIT_FRAMEWORK.md`) | 跨維度審計 | `audit_7d` 子項 | 排程 |

**已知結構性風險(2026-07-02 稽核確認的實例)**:status artifact 本身會過期。`abc_firewall_latest.md` 曾以 2026-03-22 的 ok=true 掩蓋 2026-07 的活迴歸(兩個 entrypoint 掉了 doctrine reference)。**教訓:status 檔的 `generated_at` 是該檔可信度的一部分;讀任何 `*_latest.*` 前先看日期,寫任何依賴 status 的結論前先重跑檢查器。** 結構性修復(status max-age 告警)追蹤中。

---

## 5. 已知邏輯張力(誠實清單)

按倉庫「公開 reject / 公開未解」的紀律,列出目前仍開放的邏輯張力:

1. **POAV 三種縮寫展開**(AXIOMS / `poav.py` / quickstart)— owner decision pending,每個外部審查者都會撞到。
2. **council「無投票機制」vs `voting_evolution.py`** — 術語層矛盾,語義層無矛盾(見 §2.2),建議統一措辭。
3. **`memory/` 路徑語義** — `MEMORY.md` 宣告該層屬私有,但 git 追蹤了合成 fixture 與一份真實 conversation ledger;內容無害,但與自宣告的隔離規則字面不符。
4. **status artifact 時效性** — 見 §4;是本地圖列出的最高優先結構性風險,因為它侵蝕的是「可審計」這個核心宣稱本身。
5. **Axiom 6 的語言覆蓋缺口** — harm detection 對 zh-TW 穿透,而這是專案的母語。已在 AXIOMS 自我標注,尚未修。

---

## 6. 閱讀順序建議

1. 本文件 §1(拿到執行順序的骨架)
2. `AXIOMS.json` 的 enforcement notes(拿到每條公理的真實邊界)
3. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`(拿到寫作紀律)
4. `examples/demo_declare_stance.py` 跑一次(親眼看 DECLARE_STANCE)
5. 需要細節時才進 `unified_pipeline.py` — 它 3,686 行,先有地圖再進去。
