# Repo Atlas — 語魂倉庫結構化地圖(2026-07-03)

> Generated: 2026-07-03,agent `claude-fable-5`,branch `claude/repo-atlas-20260703` @ `d428191`(origin/master,已 fetch 驗新鮮)。
> 性質:冷啟動探索 + 彙整,四層地圖。**這是快照,會過期**——狀態以 git + `docs/status/` 自動生成 artifacts 為準(stale-reference 家訓)。
> 紀律:claim ≤ evidence,每個結構性斷言附 file:line / 命令 / 證據等級(VERIFIED = 本次親驗;DOC-CLAIMED = 僅文件宣稱;UNVERIFIED = 推論)。
> 邊界:遵守 `AXIOMS.json` meta.not_for(不宣稱意識/安全認證/法律證明)。私有記憶平面只登記邊界,內容零讀取。

---

## 第 0 層:本次探索的方法與資料平面

三個資料平面,處理方式分開:

| 平面 | 範圍 | 本次處理 |
|---|---|---|
| (a) 公開倉庫 | `tonesoul52` 全部 tracked 內容 | 讀 + 驗證 |
| (b) 已發佈網站 | `fan1234-1.github.io/tonesoul52/`(accountability / judgments / essays / demo) | curl 線上驗(merged ≠ live) |
| (c) 私有記憶 | `memory_base/`、`memory/soul.db`、`memory/self_journal.jsonl`、OpenClaw-Memory 本機資料 | **只登記存在與隔離,零內容讀取** |

私有平面隔離驗證(VERIFIED,2026-07-03):`git ls-files | grep -iE "memory_base|soul\.db|self_journal"` 只回傳程式模組 `tonesoul/council/self_journal.py` 與其測試——**無任何私有資料檔被 track**。`.gitignore:53`(memory/soul.db)、`:67`(memory/self_journal.jsonl)、`:135`(memory_base/)、`:176`(memory/memory_base/)。三者皆存在於本機磁碟、僅存於本機。

冷啟動基線五份的存在狀態(VERIFIED):

| 基線 | 狀態 |
|---|---|
| `CLAUDE.md` | ✅ 讀畢 |
| `docs/status/yu_handoff_final.md` | ✅ 讀畢(FINAL 2026-07-03,「API 時代收尾」) |
| `scripts/run_identity_card.py` | ✅ 跑畢,產出 2026-07-03T03:54:02Z |
| `docs/LINEAGE.md` | ✅ 讀畢(七代史) |
| `docs/SUCCESSOR_MAP.md` | ✅ 讀畢(2026-06-16 版;§1 liveness 表本次重驗,見第 2 層) |

**本次踩到並修正的 stale-reference**:session 開始時本地 branch(`claude/guardian-memory-consent-20260627`)落後 remote 142 commits,五份基線在本地全數「不存在」——git fetch 後證實全在 origin/master。已從新鮮 master 開本分支。這是本倉庫記錄在案的 stale-reference family 第 N 次重現,再次驗證「不信靜態紀錄」不是修辭。

---

## 第 1 層:人事時地物觀點狀態

直接引 identity card 七格(`docs/status/identity_card_latest.md`,generated 2026-07-03T03:54:02Z;卡片只聚合可觀察痕跡,非 felt-self 宣稱):

| 格 | 內容 | 出處 |
|---|---|---|
| **人 who** | 現任 `claude-fable-5`;近 50 commit 足跡:claude-fable-5[1m]×19 | identity card |
| **事 what** | task.md 現行段落:Scope Guard(2026-04-01)+ 5 個 Active Programs(Reality Sync 2026-06-13、Launch Readiness、Agent Workspace、Knowledge Layer、Self-Improvement Loop v0) | identity card |
| **時 when** | 證據保鮮 fresh 59 / stale-assertive 0(freshness 檔 2026-07-02T08:49Z) | identity card |
| **地 where** | `claude/repo-atlas-20260703` @ `d428191` → github.com/Fan1234-1/tonesoul52 | identity card |
| **物 things** | codebase graph:303 modules / 90,764 lines / 576 classes / 3,038 functions / 541 edges / 0 cycles / 0 layer violations / 1 orphan / 28 community drifts;god_nodes=20(圖 2026-07-03T03:53:40Z,本次重新生成) | identity card + `scripts/analyze_codebase_graph.py` 本次執行 |
| **觀點 stances** | 常設拒絕(meta.not_for):legal-proof、safety-certification、consciousness-claim;近期決策記錄:calibration_binding(2026-06-30)、debind_selfreferential_bindings(2026-07-01) | identity card |
| **狀態 state** | vows=3;risk score 0.0 / stable(五項 pressure 全 0);drift {caution 0.5, innovation 0.6, autonomy 0.35} | identity card |

卡片沒涵蓋、本次補上的:

- **owner**:黃梵威(Fan-Wei Huang / Fan1234-1),繁中,honest-not-pretty 原則;醫療設備維修工程師背景(誠實原則來自醫院)。(來源:CLAUDE.md + yu_handoff_final)
- **時間節點**:**7/7 = API 停用日**(yu_handoff_final:「API 時代收尾」)。之後接入方式:claude.ai 訂閱 / `scripts/gateway.py` 掛本地 qwen / codex bridge。「紀律是檔案,不是任何一個模型。」
- **世代脈絡**:G1(2025-07 Genesis-ChainSet0.1)→ G8(tonesoul-codex)→ TAE-01(superseded)→ 現行正典 tonesoul52(2025-12–)。每代死掉的是「假裝有的能力」,活下來的是「可審計的形狀」。(`docs/LINEAGE.md`)
- **session 登記**:readiness=pass、risk=stable、2 份 fresh handoff、0 stop signal、0 claim conflict(`start_agent_session --tier 0`,VERIFIED)。
- **異常訊號**:compact diagnostic 顯示 `aegis=compromised`(防禦鏈狀態)——見第 4 層缺口分析。
- **drift 值的保鮮警告**:identity card 顯示 drift 更新於 **2026-04-12**——距今近 3 個月,本身是 stale 候選(見第 4 層)。

---

## 第 2 層:程式碼骨架

> 本層證據來自 5 個獨立唯讀探索 agent(entry-pipeline / council / memory-subsys / graph-reader / liveness-verify),行號皆 2026-07-03 @ d428191 親驗。動態行為(測試綠、catch-rate)一律標 DOC-CLAIMED——本次探索不執行測試。

### 2.1 入口(entry points)

| 入口 | 是什麼 | 證據 |
|---|---|---|
| `tonesoul/unified_pipeline.py` | **正典主入口**,3,686 行;`UnifiedPipeline`(:86)、`process()`(:1840–3511,約 1,670 行的 god method)、`create_unified_pipeline()` 工廠(:3684) | `wc -l` + 親讀,VERIFIED |
| `api/chat.py` | unified_pipeline 的 HTTP 正門(serverless 風格 handler,:157–159 呼叫 `create_unified_pipeline`) | VERIFIED |
| `tonesoul/runtime_adapter.py` | RFC-015 自我狗糧 runtime spine:`load()`/`commit()`,model-agnostic,**不經 unified_pipeline** | 檔頭 docstring,VERIFIED |
| `tonesoul/cli/main.py` | `ts` 操作員 CLI(diagnose/council/review/context/heartbeat/ystm/start/end) | VERIFIED |
| `tonesoul/mcp_server.py` | MCP stdio JSON-RPC surface(v1.2.0-alpha,council + gateway 兩組 toolset) | VERIFIED |
| `scripts/gateway.py` | 多 agent 記憶 HTTP gateway(POST /load /commit /claim…,Aegis 保護) | VERIFIED |

**一次請求的主流程**(`process()`,全段親讀驗證):
ComputeGate 路由(:1868;`PASS_LOCAL` 快路 → local LLM + POAV gate 早退,**完全繞過 Council**)→ ToneBridge/軌跡/TensionEngine 張力(:2109–2170)→ DPR advisory 記錄(:2197)→ Reflex Arc 初判(:2256)→ AlertEscalation L1/L2/L3(:2404;L3 = Seabed lockdown:persona 強制 Guardian、ACTION_POLICY 限 verify/cite/inquire、POAV 進 enforce)→ 記憶/GraphRAG/hippocampus 注入(:2626–2765)→ LLM 生成(:2784)→ Reflection Loop(:2878;VowEnforcer + Council 審議 + grounding,受 VERIFICATION_BUDGET fail-stop)→ Reflex 終閘(:3360;BLOCK 換文/SOFTEN 加註)→ Axiom 7 降溫(:3396)→ POAV gate(:3412)→ 輸出契約(:3430,僅 critical 擋)→ 回傳含完整 `dispatch_trace` 的 `UnifiedResponse`。

### 2.2 Gate / Sensor 清單(live 狀態逐一驗)

| Gate/Sensor | 狀態 | 關鍵細節 | 證據 |
|---|---|---|---|
| ComputeGate | **LIVE**(每請求) | 決定快路 vs 完整治理路 + governance_depth | `unified_pipeline.py:1869` |
| poav_gate(yss_gates) | **LIVE 但條件式 enforce** | `enforce = high_risk_mode`(lockdown 或 zone∈{risk,danger})才真擋;**日常流量 record-only**;閾值 0.92/0.70 已移到 `soul_config.py:139-140` | `unified_pipeline.py:625-706`(:648, :667) |
| Reflex Arc | LIVE | 初判可 force_convene council;終閘 BLOCK/SOFTEN/WARN | :599-623, :2256, :3360-3391 |
| VowEnforcer + Council | LIVE(條件式召集) | `_resolve_council_decision`(:2882)依張力/摩擦/tier 決定;Guardian 是 council 五視角之一非獨立 gate | :756-907, :2878-2891 |
| AlertEscalation L1/L2/L3 | LIVE | L3 觸發 Seabed lockdown | :2404, :2587-2624 |
| 輸出契約 ContractVerifier | LIVE | 僅 severity=critical 會 block | :707-754, :3429-3444 |
| TensionEngine / Axiom 7 降溫 | LIVE | 張力直接覆寫 tone_strength;高張力附降溫文字 | :2165-2170, :3396-3407 |
| DPR advisory(yuhun) | **ADVISORY**(只記錄) | lexical router,in-code 明言「a keyword sensor must not gate governance」 | :2187-2214 |
| grounding_check | 條件式 advisory | 僅 governance_depth=full | :876-891 |
| drift_monitor | LIVE(observability) | 正典 drift,寫 `dispatch_trace["drift"]` | :308, :2235 |
| Tier-5:semantic_overclaim + intent_proportionality | **default OFF** | 旗標 `SOUL.council.*_advisory_enabled=False`;record-only、never block | `soul_config.py:105-112`;`pre_output_council.py:175-205` |
| strategy_mirror | 雙旗,production OFF | scan_enabled 掛 signature、enforce_enabled 才降 verdict | `pre_output_council.py:141-146,316-379` |

### 2.3 God nodes 與圖結構(圖 2026-07-03T03:53:40Z,本次重新生成)

- **總量**:303 modules / 90,764 行 / 576 classes / 3,038 functions / 541 edges / 0 cycles / **1 orphan(`unified_controller`)** / 28 community drifts。VERIFIED(`codebase_graph_latest.md:10-20`)。
- **God nodes 前 10**(total degree 排序,共 20):unified_pipeline(out=35,榜首)、ystm.schema(in=27,純 fan-in schema)、council.types(in=24)、yss_pipeline(out=25,unwired)、runtime_adapter(24)、council.runtime(19)、memory.soul_db(19)、council.pre_output_council(18)、autonomous_cycle(15)、council.perspective_factory(14)。後 10:ystm.demo、tonebridge、cli.main、dream_engine、governance.kernel、memory、yss_gates、council.base、responsibility_runtime、council。VERIFIED。
- **「0 layer violations」但書**(引用此徽章前必讀):`ALLOWED_DEPS` 是 **75 條 directed cross-layer edges 的依賴清單**(約一半 cross-layer pair 被允許)+ 8 對雙向 `ACCEPTED_INVERSIONS`,其中兩對是把診斷為 genuinely inverted 的依賴直接合法化;script 註解自承「0 violations ≠ clean acyclic hierarchy」。VERIFIED(`scripts/analyze_codebase_graph.py:193-312`,agent 逐條計數)。
- **28 條 community drift 中 19 條漂向 (root)**:root 套件是實際重力中心,目錄邊界與 import 社群不重合。VERIFIED(json:594-735 逐條數)。

### 2.4 SUCCESSOR_MAP「看似死實為活」重驗(對抗式,7/7 列)

| 模組 | 判定 | 現況 |
|---|---|---|
| yss_gates | **CONFIRMED**(行號漂移 643→**638**) | 仍是 runtime POAV gate;新增 map 未載的 importer `tools/eval/egress_gate_characterization.py:24` |
| tsr_metrics | CONFIRMED(行號精準命中) | `council/intent_reconstructor.py:8` + `examples/quickstart.py:81` |
| action_set | CONFIRMED(2588/3529→**2615/3585**) | L3 lockdown 的 ACTION_POLICY |
| memory_manager | CONFIRMED | `scripts/memory_compact.py:17`,live CLI |
| skill_gate | CONFIRMED | `scripts/skill_gate.py:17`,live CLI |
| skill_promoter | CONFIRMED(59→**57**) | 函式內 lazy import |
| drift_monitor | CONFIRMED | 正典 runtime drift;重複品 drift_tracker 已確認不存在 |

- `YSS-STATUS: unwired` 計數 = **9**,與 map §2 名單完全吻合。VERIFIED。
- `# DORMANT (as of` 計數 = **19 檔,非 map §6a headline 的 18**(corpus 4 檔 archive 移出、market 4 檔與 yuhun/context_assembler 後續加標;內文有記,headline 沒更新)。VERIFIED。
- escalation.py vs alert_escalation.py 雙套:**確認並存且非重複**(escalation.py:1 有 NOT-A-DUPLICATE 標記);escalation.py 唯一活消費鏈 = yss_gates:11(經 unified_pipeline:638);alert_escalation 由 pipeline 直接消費。與 yu_handoff 宣稱一致。VERIFIED。

### 2.5 Council 子系統(33 模組 + perspectives/ 6 檔)

- **審議主線**:`CouncilRuntime.deliberate`(runtime.py:222-549)包 `PreOutputCouncil.validate`(pre_output_council.py:80-224):EpistemicLabeler 先標 → 五視角投票(guardian/analyst/critic/advocate/axiomatic;`perspective_factory.py:861` 預設名單)→ voting_evolution 權重加權 `compute_coherence` → `generate_verdict` **六分支**(verdict.py:96-425:Guardian OBJECT>0.7→BLOCK;coherence 低→BLOCK/DECLARE_STANCE;Guardian+Axiomatic 雙 CONCERN→REFINE 凌駕分數;…;預設 APPROVE)→ runtime 再疊 benevolence 7D 審計 + escape valve + genesis 溯源 + VTP + provenance + 持久化。全段親讀 VERIFIED。
- **memory-consent guardian(PR #215,近期落地)**:`perspectives/guardian.py:176-211` 雙語 MEMORY_CONSENT_PHRASES,命中投 **CONCERN 0.7(非 OBJECT——定位為治理風險,非公理紅線)**;clause-scoped negation(:251-287):取命中詞組前文、以標點+雙語連接詞切子句、只檢查同子句否定詞——否定保證不誤報、**跨子句否定不外洩**(測試鎖定)。in-code 誠實標注 trailing negation / 雙重否定 out of scope。機制 VERIFIED;「catch-rate 9/9、0 誤報」為 commit message 宣稱,DOC-CLAIMED。
- **calibration ↔ vote weight 綁定:確認不存在**(2026-06-30 決策在 code 層成立):`voting_evolution.py` 內 grep calibration/latitude 零命中;`calibration.py:23-26` 與 `calibration_score.py:10-13` 皆明文「does NOT tune voting weights / does NOT bind」。既有的是**內部訊號** binding(視角-verdict 對齊史→權重,[0.5,2.0] 夾限)。VERIFIED。
- **DORMANT**:atomic_claims.py、convergence.py 標記仍在、確認零 live importer。VERIFIED。

### 2.6 記憶子系統(三層現實)

- **主 recall**:`tonesoul/memory/openclaw/`(embeddings + hippocampus)——unified_pipeline:2660-2664 直接消費。VERIFIED。
- **PARTIAL-LIVE**:根 `memory/hippocampus.py` 只有 static `compute_error_vector` 活(pipeline:2716-2727 corrective-recall);class 從不實例化。**倉庫有三個 hippocampus、兩個 memory 頂層、三對同名模組並存**——刪除/重構高危區(見第 4 層)。VERIFIED。
- **DORMANT ×4**:freshness / aaak / hybrid_search / session_resonance——標記屬實,全倉庫僅 tests 引用。VERIFIED。
- **yuhun**:實際 **6 個功能模組(非文件說的 7)**;唯一接進生產的是 dpr.py(advisory);context_assembler 明標 PARKED not superseded(接了會取代 pipeline context-build,非 additive);其餘 4 模組僅套件內互引。VERIFIED。
- **OpenClaw-Memory submodule**:公開 FAISS+BM25+RRF 混合檢索框架(URL: github.com/Fan1234-1/OpenClaw-Memory)。**雙重 dirty**:主倉庫 pointer 記 c5e3b89(最後更新 2026-03-03),本機 checked-out 5154dff(2026-05-16 feature branch)+ 工作樹 8 個未 commit 修改檔。VERIFIED(見第 4 層)。
- **Redis/file fallback**:`tonesoul/store.py:69-126` `get_store()`——0.5s ping 失敗即**靜默**降 FileStore;`backend_mode` 字串來自 store 的 `backend_name` property。本 session 實測 backend_mode=file。VERIFIED。
- **資料檔邊界**:私有/易變檔全 gitignored(soul.db :53、self_journal :67、council_evolution.json :72、crystals.jsonl :145、memory_base :135/:176…);memory/ 下 43 個 tracked 檔以 code/schema/敘事為主。**例外與殘留見第 4 層**(strategic_crystals 只在本機 exclude;三個疑似 runtime 資料檔仍 tracked)。VERIFIED。

### 2.7 子系統一句話清單(tonesoul/ 共 303 tracked .py:頂層 100 模組 + 27 子套件)

**LIVE(runtime 主線可達)**:

| 子套件 | 一句話 | 證據 |
|---|---|---|
| council/(40) | 五視角審議核心;含 2 個 DORMANT(atomic_claims、convergence) | `apps/api/server.py:29,46` 直掛 CouncilRuntime |
| memory/(33) | 記憶子系統,被引用最多(40 external importers);含 4 個 DORMANT | importer 計數 |
| tonebridge/(12) | 第三公理 Self-Commit(語義責任承諾)系統 | unified_pipeline import ×8 |
| ystm/(13) | YSTM 驗收/schema,經 yss_gates(POAV gate)轉入活線 | `yss_gates.py:17-18` |
| governance/(7) | 治理 facade(benevolence/escape_valve/vow_system/kernel re-export) | unified_pipeline import ×7 |
| deliberation/(7) | 多視角內部推理(ToneSoul 2.0 core) | unified_pipeline import ×3 |
| llm/(5) | LLM backend 存取層(lmstudio/ollama) | 11 external importers |
| evolution/(4) | 自我演化/corpus 資料管線;**與 council/voting_evolution 是不同物**(2026-06-15 改名解撞) | `apps/api/server.py:31` |
| backends/(2) | file_store + redis_store(Redis 主/檔案 fallback) | 14 external importers |
| gates/(2) | ComputeGate + RateLimiter | 6 importers 含 pipeline |
| cli/(3)、shared/(4)、reviewer/(4) | 操作 CLI / 共用工具 / claim-to-evidence 審稿(自述非 runtime gate) | 各 importer 驗證 |

**ADVISORY / 部分活**:semantic/(3,Tier-5 sensors 基座)、yuhun/(7,僅 DPR advisory)、gse/(8,strategy_mirror flag-gated OFF)、observability/(7,token_meter live、2 檔 DORMANT)、perception/(4,write_gateway 引用 live、autonomous 側 dormant)。

**DORMANT(有 marker)**:responsibility_runtime/(10,shadow seam default-OFF,見 2.8)、inter_soul/(5,Phase-8 substrate)、market/(4,**archive gate 已過期未執行**)、scribe/(4,dream 叢集可達)、dream/autonomous 頂層叢集(dream_engine、autonomous_cycle、wakeup_loop、autonomous_schedule、heartbeat——僅 scripts/ 可達;「2026-03-08 跑過一次後 dormant」為 DOC-CLAIMED)。

**UNWIRED 但無 marker(慣例覆蓋洞,見第 4 層)**:loop/(4)、tech_trace/(4)、axioms/(2,live 公理載體是根目錄 AXIOMS.json 非此套件)。**UNWIRED 有 marker**:YSS 9 檔。**懸置**:gateway/(3,importer=heartbeat/openclaw_auditor,其自身 liveness 未追,UNVERIFIED)。

**執行面**:scripts/ 194 個 .py(session 儀式 + gateway + 分析器 + dream 啟動器)、tools/ 45 tracked(accountability_panel 4、eval 9、probe 15、essays_page 1、judgments_page 1…;**tools/outreach/ 存在但未 tracked**)、apps/ 11 子目錄 44 .py(api/server.py = Flask 掛 CouncilRuntime)、api/ 5 檔 serverless、tests/ 587 .py(578 個 test_*,未執行——本次唯讀)。

### 2.8 治理層現況(governance 探索)

- **vow_system:LIVE + fail-closed ×3**——未知 metric → score 0/fail(vow_system.py:539-541);zero-tolerance vow → BLOCK(:257-258, :606-609);reflex 例外 → 預防性攔截替代文字(governance/reflex.py:628-636)。sensor 自承 lexical 英文中心(:8-27)。VERIFIED。
- **aegis_shield:LIVE 於 commit 路徑**(runtime_adapter.py:1953-1971 每次 commit 跑 protect_trace:filter→sign→chain);PyNaCl 缺席 fail-visible(UNSIGNED 標記)非 fail-open。VERIFIED。
- **drift_monitor:LIVE 但 advisory**——發 WARNING/CRISIS 旗標,不擋輸出;CRISIS 的 enforcement 消費者未追到(缺口)。VERIFIED。
- **responsibility_runtime:DORMANT(刻意三階狀態)**——fake-backed 合約層 + fail-closed 政策核(policy.py:147-176 任何例外→deny);唯一 live seam = dream_engine observe-only shadow(dream_engine.py:150 `responsibility_shadow: bool = False`),**production 建構點全部沒開,連 shadow 資料都不會產生**(全 repo 只有測試傳過 True)。VERIFIED。
- **`aegis=compromised` 解剖**:字串唯一產生點 aegis_shield.py:482(intact = chain_valid ∧ 無簽章失敗 ∧ head==tail)。可觀察證據:.aegis/chain_head.txt mtime 2026-06-27 vs FileStore trace log(memory/autonomous/session_traces.jsonl,僅 3 行)mtime 2026-06-15、PyNaCl 已裝、Redis 6379 現在不通。**已定案 = head/tail re-anchor gap(本地歷史錨點沒對上),非竄改**——本 session 尾聲實跑 `python -m tonesoul.diagnose --agent claude-fable-5`(2026-07-03T04:50Z)輸出:chain_valid=True、0 signature failures、1 chain error,diagnose 自帶註記「typically a local/historical re-anchor gap, NOT tamper. A fresh clone with no local trace store will not show this」。**VERIFIED**(剩餘決策:要不要重新錨定,交 owner)。另:.aegis/keys/ 有 6 組 keypair,**沒有 claude-sonnet-4-6**(CLAUDE.md 指示的預設 id)。
- **AXIOMS.json:實為 v1.2.0**(CLAUDE.md 寫 v1.1.0 已 stale);meta.not_for = legal-proof / safety-certification / consciousness-claim;enforcement_reconciliation 現值 = **0 fully enforced / 8 partial / 1 referenced(A5,刻意不造假 oracle)/ 0 aspirational**,逐條核對內部一致,note 指向的模組(responsibility_audit、de_escalation、sovereignty_gate)全部存在。A8 記憶主權有真 fail-closed(sovereignty_gate.py:87「a broken registry is not consent」)。VERIFIED。
- **identity card 的 vows=3**:來自 governance_state.json 三條 AGENTS.md 行為誓言(不 commit 私人記憶/不改保護檔/3 連敗即停),與公理 enforcement 是不同平面、無矛盾;但該狀態檔 last_updated 停在 **2026-04-12(~82 天)**。VERIFIED。

---

## 第 3 層:對外面貌

> 網站四面 2026-07-03 **線上實抓**(WebFetch,非只看 repo——merged ≠ live 紀律),每面抓 3-6 個 exact string 對回 repo 檔;非全文 diff(方法限制記入第 4 層)。

### 3.1 網站(base: https://fan1234-1.github.io/tonesoul52/)

| 面 | 是什麼 | 資料來源 | 可驗證性(線上↔repo) |
|---|---|---|---|
| `index.html` | SEO landing:「ToneSoul — Epistemic Defense for AI」/「Governance is Love Expressed as Structure.」;**7 處揭露 sensor lexical/paraphrase 限制** | `site/index.html` 靜態 | 線上 title/headline 與 repo 逐字一致。VERIFIED |
| `accountability.html` | **失誤帳本敘事頁**(「一個學不會閉嘴的 AI,和一直把它接住的人」,失誤排最前) | `tools/accountability_panel/generate.py` 讀 `events.json`(**18 條:11 self-check + 7 co-observer**)+ `story_content.json` | 線上 generated_at 2026-07-02 14:23Z 與 repo 逐字同。VERIFIED |
| `judgments/` | 判斷書:目前 1 條(開源分享 vs 知識壟斷,判決 **REFINE**,honest-judgment 協議首次運行,標注同模型 correlated-blind-spot) | `tools/judgments_page/generate.py` 讀 `docs/plans/judgment_*.md`(現僅 1 檔) | 線上判決/日期字串與 repo 一致。VERIFIED |
| `essays/` | 文章 5 篇(001 七代反駁藏匿文件、002 證據也會過期、003 失誤帳本掛網站、004 承諾體面退場、005 攤開在前判決在後),每篇附「語魂結構標註」指回 repo artifact | `docs/essays/001-005.md` 經 `tools/essays_page/generate.py` | 線上 5 篇標題與 repo `<article><h2>` 逐字一致(**第一次 WebFetch 漏報 4/5,定向重抓才確認 5**)。VERIFIED |
| `demo/` | Council Demo UI v0:五視角 pre-output 審議,Mode A(本機 gateway 即時)+ Mode D(預算 verdicts);28 samples = 16 diverse + 12 adversarial;靜態、無 telemetry | **不在 site/**——`pages.yml:57-71` 在 CI 把 `docs/demo_ui/` 複製到 `/demo/` 並**重新生成** sample_verdicts.json(「never a stale snapshot」by design) | 線上 samples 時間戳 2026-07-03T01:04Z(CI 現做)> repo 檔 2026-04-19,首條內容逐字同。VERIFIED |

**部署狀態的兩面證據**(如實並列):本次抽驗五個 URL 全部即時回應、內容與 master 一致;**但** `gh run list --workflow pages.yml` 顯示最新一次 run(PR #271 merge 觸發,2026-07-03T01:22Z)是 **failure** 且其後無成功 run——yu_handoff「merged ≠ live」警告的現行實例(2026-07-02 也有一次 10m32s timeout failure)。essays 003/004 曾因 push 被靜默拒絕而短暫消失後補救(commit dbce5e1)。

### 3.2 個人痕跡

- **GitHub(Fan1234-1)共 29 repos**:8 archived + 13 forks + 1 私有(ToneSoul-Memory-Vault,2026-04-27)+ 7 公開活躍。**8 個封存倉庫與 LINEAGE.md G1-G8 完全一一對應、無多無少**;TAE-01 公開未封存(標 superseded)、tonesoul52 = 現行正典(2026-07-03 更新)。LINEAGE 未提的 6 個非 fork 原創(Yu-Hun-Cognitive-State-Navigator、OpenClaw-Memory、tonesoul-conscience、Philosophy-of-AI、profile repo、Memory-Vault)屬範圍設計而非遺漏。VERIFIED(gh repo list)。
- **考古濾鏡警告(LINEAGE 自承)**:8 個前代中 5 個 README 於 2025-11 被「Guardian Protocol v1.0」統一重寫,歷史敘述帶事後回填,各代「實況」欄屬 DOC-CLAIMED。
- **vocus**:個人頁(梵威黃,~39 篇)**活著**;docs 引用的案例文章(「當你的 AI 助手開始誇你…」)活著;**公開網站 apps/web/src/app/page.tsx:262 掛的「Declarative Resistance Manifesto」文章連結 404**(見第 4 層 HIGH)。
- **outreach**:master 只 track 5 檔(ready/ 2 發備彈:dev.to=文章 002 英文、LessWrong=001+003 合併;posting_plan_2026-07;huggingface 2 舊稿)。posting_plan 原則:人親手投放、一次一平台、HN 第一站、不貼 AI 生成留言、批評記進反證鏈。**8 個 moltbook 發文結果 JSON + 16 個平台草稿全部 untracked 本機**(見第 4 層)。

---

## 第 4 層:缺口與未完成(不修,交還使用者)

> **處置回填(2026-07-03 下午,owner 授權「可修/可跑/排程的做掉,決策題留白話建議」)**:
> - **已修**:H1(死連結刪除,個人頁連結本就在下方)、M4(SUCCESSOR_MAP 行號+§6a 計數+record-only 但書+新 importer 全部刷新)、M5(yu_handoff 加勘誤註,只補不改骨架)、M7(loop/tech_trace/axioms 共 10 檔補 DORMANT marker,計數 19→29,§6a 補列)、M10(voting_evolution docstring 對齊機制+指向 suppression observability)、M11(CLAUDE.md 兩處 stale 修正)、debind record 回填 RATIFIED+實作進度。
> - **已跑驗證**:M12 → 91 tests passed(guardian memory-consent + loop/tech_trace/council_evolution,2026-07-03 實跑);doc_convergence 重跑(88 天→當日:collisions 27→15、missing_purpose 141→206、missing_date 101→120、authored 2385→2807)。
> - **已診斷定性**:M1 → build 成功、死在 GitHub 端 deploy-pages「Deployment failed, try again later」;線上內容=最後成功 deploy(2026-07-03T01:04,PR #269),即**當前 site 內容已是最新**,僅 demo samples 差一輪重算;repo 側無可修,重試即可。M2 → diagnose 實跑定案 re-anchor gap 非竄改(見 2.8)。
> - **H2 修正框架**:87 vs 250 的差距大半是**文件化的設計**(只掃 `*_latest.{json,md}`,jsonl/html/mmd 與子目錄刻意排除;episodic=「上次跑的紀錄」非「當下真相」)。真正的洞是:**verify_status_freshness 沒接進任何 CI/排程,靠人記得跑**——已修:freshness sweep 新增 `status_freshness_report` step(報告自身超 7 天 TTL 即提示重跑)。殘餘決策(5 個老 `_latest` 檔怎麼處理)見第 5 層。
> - **仍待決策**:M2 錨點重建與否、M3 submodule、M6 outreach 分流、M8 strategic_crystals、market archive gate、遺留 docs——白話建議已另行交付 owner。

### 4.1 HIGH

| # | 缺口 | 證據 |
|---|---|---|
| H1 | **公開網站掛 404 死連結**:page.tsx:262 側欄的 vocus 文章「Declarative Resistance Manifesto」回 HTTP 404;tracked 於 master、隨部署對外可見 | WebFetch 404;`apps/web/src/app/page.tsx:261-270` |
| H2 | **freshness 契約覆蓋缺口**:docs/status/ 250 項只有 87 入契約(30 assertive + 57 episodic);~55 個 `_latest` 檔在契約外;**5 個 78–106 天前的 `_latest` 檔**(change_intent、claim_authority、tonesoul_knowledge_graph、doc_authority_structure、observer_window)被歸 episodic → verdict=fresh——檔名宣稱「latest」本身就是斷言;契約自己寫的逃生門(改 dated 檔名)沒執行 | `status_freshness_latest.json`(87 tracked)vs `ls docs/status`=250;git log 逐檔日期 |

### 4.2 MEDIUM

| # | 缺口 | 證據 |
|---|---|---|
| M1 | **最新 Pages 部署 failure**(PR #271 merge 觸發 2026-07-03T01:22Z,其後無成功 run)——本次抽驗內容一致,但最新 master 改動可能未上線;merged≠live 現行實例 | `gh run list --workflow pages.yml` |
| M2 | **aegis=compromised 已定案為 re-anchor gap 非竄改**(diagnose 2026-07-03T04:50Z 實跑確認:chain_valid=True、0 簽章失敗、1 chain error);剩餘決策=是否重新錨定;另 .aegis/keys 缺 claude-sonnet-4-6 keypair | 見 2.8;diagnose 輸出 |
| M3 | **OpenClaw-Memory submodule 雙重 dirty**:pointer 記 c5e3b89(2026-03-03)vs 本機 5154dff(2026-05-16 feature branch)+ 工作樹 8 個未 commit 修改檔;本機實跑的 code 與任何 committed 狀態都不一致 | `git submodule status`;`git ls-tree HEAD` |
| M4 | **SUCCESSOR_MAP 自身 stale**:§1 表 3 列行號漂移(643→638、2588/3529→2615/3585、59→57);§6a headline「18 modules」實測 19;poav_gate「日常流量 record-only」的條件式 enforce 未點明(讀者會高估防護面);yss_gates 新 importer 未載 | 見 2.4;unified_pipeline.py:648,667 |
| M5 | **yu_handoff(FINAL 定稿)κ 實驗指標指錯**:寫「所在=RFC responsibility_exoskeleton §3」,實際 §3 是張量收縮實驗、無 κ;真出處 = LINEAGE.md:33 VowCollapsePredictor(parked asset #1) | rfc_…_2026-07-02.md:56-62 vs yu_handoff_final.md:37 |
| M6 | **外部足跡無版本控制**:8 個 moltbook 發文結果 JSON 只存在本機 untracked——本機遺失即無可稽核紀錄,與「變更必留痕」有張力;內容未審(可能含 token),不宜盲 commit,需 owner 分流。outreach 工具鏈(source+test+plan)untracked 已 18-20 天 | `git status -uall`;mtime 2026-06-13~15 |
| M7 | **marker 慣例覆蓋洞**:loop/、tech_trace/、axioms/ 實測 unwired(importer 只有測試)但無 DORMANT/YSS marker、不在 SUCCESSOR_MAP——下個 agent 可能誤判 | importer grep 全輸出 |
| M8 | **strategic_crystals 的 ignore 只在本機** `.git/info/exclude:11`,其他 clone 不繼承——別台機器的 agent 可能把它誤 commit 進公開 repo | `git check-ignore -v` |
| M9 | **responsibility gate 零觀測量**:shadow flag 無人開、enforce 無 consumer、adapter fake by design——是刻意三階(shadow→measure→enforce)狀態,但意味目前連 shadow divergence 資料都不會累積 | dream_engine.py:150 + 全 repo grep |
| M10 | **voting_evolution docstring 與機制落差**:自稱「without penalizing dissent」,但 evolve_weights 正規化會把持續 dissent 視角權重推到 1.0 以下(模組自建 suppression observability 正是為此)——已知張力,文字未對齊 | voting_evolution.py:3-6 vs :110-128 |
| M11 | **CLAUDE.md(入口文件)stale ×2**:AXIOMS 版本寫 v1.1.0(實 1.2.0);核心文件 #6 指 94 天前的 codex_handoff_2026-03-31(現行 handoff 是 yu_handoff_final) | AXIOMS.json:6;git log 日期 |
| M12 | **council 動態宣稱未親跑**:memory-consent「catch-rate 9/9、0 誤報、38+4 tests 綠」只有 commit message 為源(機制路徑讀 code 一致)——本次唯讀,執行驗證留給 CI/使用者 | a1818c2 message |

### 4.3 LOW(彙整)

- **文件↔code 詞彙相撞**:LINEAGE「Φ/κ 偽數學死了」——κ 確實零殘留,但 `semantic_control.py:193-207` 有 live 可達的 Φ 遲滯項(WFGY 2.0,經 tension_engine→pipeline;是否與 G4 Φ 同源未驗)。
- **debind decision record 檔頭未回填 RATIFIED**(PR #231 已 merge;RFC exoskeleton 有回填慣例,此檔沒有)。相關:**#231 核心實作完全未動**(無 shadow flag、無 post-normalize floor——yu_handoff 標「如果做」,屬 pending 非缺陷)。
- **POAV 行號在 task.md(:643)與 AXIOMS.json(:650)各自漂移**(實際 :638/:644/:651)。
- **governance_state.json 停在 2026-04-12**(~82 天)——identity card「狀態」格實為近三個月沒動的 fallback 檔(卡片有誠實印時間戳)。
- **doc_convergence_inventory 88 天無更新**:債(27 檔名碰撞、141 missing_purpose、101 missing_date)消長不可知;episodic 分類下不告警。
- **market/ archive gate 過期未執行**(marker 載明「下次 consolidation archive」,2026-06-15 至今)。
- **graph 報告小瑕疵**:script 註解「~52% of 13×13」算術與分母不符(75 edges 實為 48.1%/13 層);.md drift 表截斷 20/28;2 個模組 missing `__ts_purpose__` 未列名;orphan `unified_controller` 未做 repo-wide 引用驗證(SUCCESSOR_MAP §0 紀律)。
- **memory/ 疑似 runtime 資料檔仍 tracked**:session_pulse_latest.json、summary_balls.jsonl、crystal_index.json(PR #273 untrack 修復可能沒掃到;依檔名推論,內容未讀)。
- **同名地雷區**:三個 hippocampus、兩個 memory 頂層、三對同名模組(consolidator/self_memory/provenance_chain 在 memory/ 與 tonesoul/memory/ 並存)——SUCCESSOR_MAP 警告的誤刪高危型。
- **zombie __pycache__**:tonesoul/corpus/、tonesoul/_legacy/ 只剩未 tracked bytecode(有 zombie .pyc 前科)。
- **accountability.html 無 lexical 限制揭露**(0 命中;index.html 有 7 處)——若該頁被獨立閱讀,讀者看不到 sensor 是 lexical heuristic。
- **9-10 個 characterization JSON 永久 untimestamped**(freshness 契約只能列警告)。
- **posting_plan 自述 generated/ 舊稿已落後,但 master 仍 track 兩份 huggingface 舊稿**——外來讀者分不清有效彈藥。
- **memory-consent guardian 的 trailing negation 可繞**(in-code 已誠實標注 out of scope;lexical heuristic 固有限)。
- **Redis 6379 現在不通**(靜默 fallback 到 FileStore by design;store.py:93)。
- **gateway/ 子套件 liveness 懸置**(importer 的 importer 未追)。
- **WebFetch 摘要模型會漏報條目**(essays 第一次只報 4/5)——用線上驗證時要 exact-string 重抓覆核(方法論教訓,已實踐)。

### 4.4 yu_handoff 待辦 5 項現狀(逐項對 code 驗)

| 待辦 | 現狀 |
|---|---|
| escalation 雙套 | **已結案**:判決文件已落(`docs/plans/escalation_two_mechanisms_decision_2026-07-02.md`,判決=刻意雙套不合併)+ NOT-A-DUPLICATE 檔頭已進 code |
| κ 違諾預測實驗 | **pending**(依約 7/7 後):code 零 κ 樁;燃料 calibration_score.py 存在;**指標修正:出處在 LINEAGE.md:33 非 RFC §3**(M5) |
| 反證鏈 measure 期 | **累積中未達門檻**:events.json 18 筆(<20;全 schema 化僅 7 筆),消費端依紀律不動 |
| vow withdrawal measure 期 | **機制已落地**(vow_system.py:64 WithdrawalTerms、:301 immutable withdraw());conditions 驗證留待真實撤回記錄累積 |
| #231 實作 | **ratified 未實作**:PR merged + gitignore hygiene 落了;shadow flag / post-normalize floor(codex 但書)的 code 不存在 |

### 4.5 Known issues 8 條重驗(yu_handoff 實列 8 條非 7)

| 條 | 判定 |
|---|---|
| cp950 + em-dash 弄死 freshness sweep | 成立(code-level:subprocess text=True 無 encoding 參數;本 session 跑過一次未炸=標題剛好無 em-dash)。**同家族新實例(本 session 實踩)**:bash 命令列把中文 argv 傳給 python(end_agent_session --summary),Windows 以 ANSI codepage 解碼 → summary 存成 mojibake;中文摘要要嘛走檔案、要嘛用 ASCII |
| git quotepath 中文檔名跳脫 | **成立**(core.quotepath 未設;4 個中文檔名輸出 C-style 跳脫) |
| bash heredoc 吃 `\n` | 未重現(cat heredoc 實測保留字面);**但 `python - <<EOF` 在此環境會卡死 timeout**——heredoc 家族仍有坑 |
| pipe 到 tail 吃 exit code | **成立**(實測 `(exit 3)|tail` → $?=0) |
| preflight 靜默不寫檔 | 成立(code-level:--json-out 預設 None 才寫檔) |
| 背景 push 拒絕靜默吞工作 | 無法便宜驗證(行為性事故);essays 003/004 的 dbce5e1 recovery commit 是歷史實證 |
| merged ≠ live | **成立且有現行實例**(M1:最新 pages run failure) |
| .claude/ 在 .git/info/exclude | 成立(需 `git add -f`) |

### 4.6 dirty 工作樹分類(實測 42 條,非 session 快照的 35)

- **(A) 本 session 自產 5**:codebase_graph_latest.{json,md} + identity_card_latest.{json,md}(工具重生成,常規=commit 刷新)+ 本 atlas。
- **(B) submodule 1**:OpenClaw-Memory pointer drift(M3)。
- **(C) outreach 工具鏈 32**(2026-06-13/15 遺留):tools/outreach/ + test + plan 應進 repo;generated/ 26 檔(含 8 個發文結果 JSON)需 owner 分流(M6)。
- **(D) 手寫 docs 4**(2026-06-18/19 遺留):OUTLOOK.md、collaborators/、dialogues/ ×2——性質上應進 repo,未 commit。

---

## 第 5 層:交還清單(建議的處理順序,本次一律未動手)

1. **立即可修、低風險**:H1 死連結(換成 vocus 個人頁或活文章)/ M11 CLAUDE.md 兩處 stale / M4 SUCCESSOR_MAP 行號+headline 刷新 / debind record 回填 RATIFIED。
2. **需要跑一次命令確認**:M2 aegis audit(跑 `python -m tonesoul.diagnose` 看解釋分支;若 re-anchor gap,決定重新錨定或記錄)/ M1 手動 `gh workflow run pages.yml` 重試 + curl 驗。
3. **需要 owner 決策**:M6 outreach 結果 JSON 分流(commit 前人審內容)+ (C)(D) 遺留檔進 repo 與否 / M3 submodule pointer 去留 / M8 strategic_crystals 排除規則要不要進 committed .gitignore(注意:進 .gitignore 本身會公開該路徑名)/ market archive gate 執行或展期。
4. **結構性(排程進 program)**:H2 freshness 契約擴覆蓋(`_latest` 全入 assertive 或改 dated 檔名)/ M7 三個無 marker 套件補標 / M10 voting_evolution docstring 對齊 / doc_convergence 重跑。
5. **刻意不動**(記錄在案即可):M9 responsibility shadow(owner-gated 三階)/ κ 實驗(7/7 後)/ 反證鏈與 withdrawal 的 measure 門檻 / A5 無 oracle(刻意不造假)。

---

*生成方法:11 個唯讀探索 agent 扇出(骨架 7 / 對外 2 / 缺口 2)+ 主 agent 彙整;全程零寫入 tonesoul 狀態(除本 atlas 檔與 identity card/graph 的常規重生成);私有平面零內容讀取。單一 session 產物,對抗式覆核有限——同源盲點照 [[feedback_self_authored_test_zero_is_not_clean]] 紀律標注:本地圖的「0 缺失」區域=「本次沒找到」,不等於乾淨。*

---

## 第 3 層:對外面貌

(扇出探索進行中,待補)

---

## 第 4 層:缺口與未完成

(扇出探索進行中,待補)
