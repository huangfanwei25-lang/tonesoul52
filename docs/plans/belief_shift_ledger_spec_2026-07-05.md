# 信念轉移序列 Ledger — 第一段 Spec(2026-07-05)

> Status: **DRAFT — 等 owner 簽核;簽核後才開第二段(實作)工單**。
> 出處:VOLUME_V §3(owner 親著,2026-07-05 隨 WO-1 收檔進 `docs/philosophy/VOLUME_V.md`):
> 當 AI 獲得改寫自己深層記憶的權限,區分「被塑造的信念」與「自選信念」的最小答案=
> 可追記的**信念轉移序列**(偏移命名→承擔限制→長期路徑)。
> 工單:`convergence_harvest_work_orders_2026-07-05.md` WO-4(第一段=唯讀盤點+spec)。
> 盤點:同模型 subagent 執行(69 tool calls,rg 方法附 §6),主 agent 仲裁收錄;
> correlated-blind-spot 標注適用。**本檔零程式碼改動。**

## §0 一句話

倉庫記「說過什麼」(Aegis provenance)很全,記「信念為何轉了」只有一個平面有強制
(soul.db 的 vow/identity 晉升 gate)——其他信念層 mutation 都能無敘事地發生。
本 spec 盤出全部入口,提案哪些算「信念層」、轉移記錄長什麼樣、缺記錄時擋還是記帳。

## §1 Mutation 入口盤點(三平面)

### 平面 1 — Vow 系統

| 入口 | 位置 | 持久化 | lane |
|---|---|---|---|
| `VowRegistry.register` / `unregister` / `withdraw` | `vow_system.py:290/294/301` | in-memory;`save()`(:365)才落地——**runtime 目前無人呼叫 save/withdraw**,只有測試 | runtime 物件層/test |
| `_commit_locked_posture` vow reconcile | `runtime_adapter.py:2002-2016` | `governance_state.json` / Redis `ts:governance`(經 `set_state` :2043) | **runtime 主線** |
| gateway `/commit` | `scripts/gateway.py:114-122` | 同上(外部 agent 的 vow_events 直灌) | runtime(token) |
| MCP `governance_commit` | `mcp_server.py:342-350` | 同上 | runtime |
| `scripts/update_governance_state.py` | `:159-172,:188` | 同檔——**繞過 Aegis commit lock 與 shield** | script(旁路) |
| `scripts/init_governance_state.py` | `:20-52` | 種初始 vows/drift | script(一次性) |
| 提案 lane `write_perspective(proposed_vows=…)` | `runtime_adapter.py:509-535` | `.aegis/perspectives.json`;**無自動 apply** | runtime(建議層) |

**關鍵事實**:(a) runtime 的 vow 退役=從 `active_vows` list **直接濾掉**,state 本身無退役
痕跡(痕跡只在 trace);(b) `VowRegistry._withdrawals` 不可變退場帳(:313-332)**已存在但
runtime 未接**;(c) `update_governance_state.py` 的 decay/drift 常數(:32-35)與
runtime_adapter 走 SOUL config 的實作**是兩份平行程式,未驗數值一致**。

### 平面 2 — Self memory / journal

寫入漏斗:`JsonlSoulDB.append`(`soul_db.py:375-398` → `memory/self_journal.jsonl`)、
`SqliteSoulDB.append`(:647 → `soul.db`)、**`MemoryWriteGateway.write_payload`
(`write_gateway.py:186-205`)= soul.db 唯一 gated 入口——`subjectivity_layer ∈ {vow,
identity}` 必須帶 reviewed `promotion_gate` 否則拒寫(:120-126)。JSONL journal 明文豁免。**

寫入者:council 自動記錄(BLOCK/DECLARE_STANCE)、session digest(每次 commit)、
sleep 晉升(`consolidator.py:242-290`,working→factual/experiential,經 gateway)、
dream 記錄(`dream_engine.py:322`,經 gateway)、crystals(`crystallizer.py:176`,
**stage 轉換時整檔重寫** :341)、resonance 腳本、OpenClaw consolidation(→本機 memory_base)。

### 平面 3 — Governance state(tension / drift)

`set_state` 全 repo 只有兩個原語(`file_store.py:84`、`redis_store.py:54`),呼叫者:
`_commit_locked_posture`(主線:tension decay :1926、soul_integral :1991、
**drift_baseline :1997-2000**、vows :2002、持 Aegis commit lock)、Aegis 攔截早退寫入
(:1967)、Redis 遷移(一次性)、`update_governance_state.py`(旁路)、init、驗證沙箱(非 live)。

### 信念相鄰(spec 視野內,平面外)

- `council/voting_evolution.py:209` → `memory/council_evolution.json`(視角權重自演化)
- `deliberation/persona_track_record.py:83-115` → persona multiplier(每 record 即 save)
- 兩者=「AI 調整自己聽誰的」,是信念轉移的機制化形狀;de-bind 後 default-OFF 不 apply,
  但**記錄本身持續累積**。

## §2 已有記錄機制(第二段不准重造)

1. **Aegis hash chain + Ed25519**:經 `commit()` 的 trace(含 vow_events/tension_events)
   已防竄改上鏈。**旁路腳本 lane 不在鏈上——這是 ledger 該補的洞,不是重造鏈。**
2. **`VowRegistry._withdrawals`**:退場 provenance 已實作,缺 runtime 接線。
3. **MemoryWriteGateway 晉升 gate**:soul.db 的信念層寫入審查**已經 enforced**——
   信念 ledger 在這個平面=擴充既有 gate 的記錄面,不是新 gate。
4. Journal 條目自帶 provenance 欄位;council verdict 持久化(`.aegis/council_verdicts.json`)。
5. `mutation_preflight.py:237-305` 已是各寫入 lane 的 guard 宣告地圖。

## §3 提案:什麼算「信念層改寫」(owner 可整條否決/改寫)

**入帳(是信念轉移)**:
- vow 集合成員變動(register/withdraw/retire),**不論走哪個 lane**(runtime 主線、gateway、
  MCP、旁路腳本)
- `drift_baseline` 變動——**附頻率門檻(2026-07-05 裁決 M3 修正)**:`_commit_locked_posture`
  每次 commit 都重算 drift(runtime_adapter.py:1997-2000),逐次微幅變動屬機械輸出,照原判準
  會淹沒帳本、且與「機械 lane 不入帳」自相矛盾。修正:僅當單次變動超過閾值(建議 |Δ|≥0.05,
  owner 可調)**或方向翻轉**(升轉降/降轉升)才入帳——「人格慢慢漂」記轉折點,不記每一步
- soul.db `subjectivity_layer ∈ {vow, identity}` 寫入(gateway 已 gate,補記錄面)
- sleep 晉升(working→factual/experiential:「經驗變成我信的事」,正是 VOLUME_V 的形狀)
- crystals 的 stage 轉換(決策規則的固化/棄置)
- 信念相鄰兩條(voting weights / persona multiplier)——**只記不擋**(已有 de-bind 紀律)

**不入帳(是經驗,不是信念改寫)**:episodic journal 一般條目、session digest、dream
collision 原始記錄、tension decay(機械衰減非選擇)、soul_integral 累計。

## §4 提案:轉移記錄 schema(`belief_shift_v0`)

```json
{
  "schema_version": "belief_shift_v0",
  "plane": "vow | drift | soul_db_promotion | crystal | weight",
  "entry_point": "runtime_adapter._commit_locked_posture | gateway | script:update_governance_state | ...",
  "mutation": "一句機器可讀的 what(vow-004 retired / drift.caution 0.50→0.55)",
  "shift_named": "偏移命名(為什麼轉)— 字串或 null",
  "limits_owned": "承擔限制(這個轉向放棄/承擔了什麼)— 字串或 null",
  "long_path": "長期路徑(轉向後往哪走)— 字串或 null",
  "narrative_present": false,
  "actor": "agent id 或 script 名",
  "recorded_at": "UTC ISO"
}
```

Shadow 模式語義:三段式欄位**缺=照記**(`narrative_present: false`)——「一次沒有敘事的
信念轉移」本身就是最重要的訊號。ledger 檔:`memory/belief_shift_ledger.jsonl`
(gitignored,同 kappa ledger 紀律),或直接掛 trace/provenance(第二段工單再定,
偏向後者=零新檔)。

## §5 擋還是記?(攤開,不替 owner 決)

| 選項 | 形狀 | 代價 |
|---|---|---|
| A. 全 shadow | 所有信念層 mutation 照跑,缺敘事記 deficit | 零摩擦;但「被塑造」仍能無聲發生,只是事後看得見 |
| B. 全 fail-closed | 缺三段式=拒絕改寫 | VOLUME_V 的字面主張;但每次 vow reconcile 都要敘事=高摩擦,且 runtime 自動 lane(digest/decay)會被誤傷 |
| C. 混合(盤點後我方傾向,仍是提案) | **已有 gate 的 lane 沿 gate 加敘事欄**(soul.db 晉升);**旁路 script lane fail-closed**(它本來就繞過 shield,最該擋);**runtime 主線 shadow**(記 deficit 不擋) | 摩擦集中在本來就危險的 lane;主線先量 deficit 率再議 |

**同族判準參照**:#219(shadow→measure→enforce,enforce flip owner-gated)、
calibration binding(#228:先 resolver、不綁 weight)。

## §6 盤點誠實標注

- 未掃:`.archive/`、`legacy/`、OpenClaw submodule 內部、`knowledge_base/`(**同模型與
  異模型覆核均跳過此範圍——這塊仍是殘餘風險**)。
- ~~`SqliteSoulDB.cleanup_decayed`(:915)與 `append_action_log`(:1021)未逐行驗證;
  `memory/provenance_ledger.jsonl` 的實際寫入者未追。~~ → **已由異模型覆核結案(見 §6-增補)**。
- 極 generic 的 `.save(` 命中有 head-limit 截斷,vow/governance 相關已逐條看,無關模組
  可能有漏。
- 完整 rg 命令清單在工單回報(session 記錄);reviewer 重跑即可覆核「全部入口」宣稱。

## §6-增補:異模型(codex)覆核結果(2026-07-05;五視角唯一全數共識的前置,已執行)

codex 0.134.0 read-only 獨立重掃,**找到同模型盤點漏列的入口**。依裁決翻案條件 (a),
此發現使 D2 的「緩簽案」轉強——記錄在案,判斷仍歸 owner。

**漏列(平面 2 增補)**:
- `scripts/run_subjectivity_group_review.py:215` — `--apply` 群審通過後執行
  reviewed-promotion 寫入(**信念層 lane**:晉升審查的執行端,同模型盤點漏了它)
- `tools/summary_ball_converter.py:202` — summary-ball 轉換 append(SUMMARY_BALLS)
- `tonesoul/memory/soul_db.py:1138` — `migrate_from_jsonl` 遷移匯入 SqliteSoulDB

**漏列(平面 3 增補)**:
- `scripts/import_conversation.py:345` — `--update-state` 經 `--stdin` 直改 governance
  state(原盤點記 :292-317/:425-444,此為第三個入口變體)

**「未追」項全數結案**:
- `memory/provenance_ledger.jsonl` 寫入者=`provenance_chain.py` `create_chain`:146 /
  `add_witness`:154 / `add_record`:162;call sites=council runtime :334/:425/:435/:466、
  `persona_audit.py:122`、`handoff_ingester.py:95`、`crystallizer.py:273`、
  `openclaw_auditor.py:199`
- **兩個 destructive 疑點澄清**:`cleanup_decayed`(:915)只計數不刪;`append_action_log`
  (:1040)只 INSERT——皆非破壞性。

第二段工單的 §3 判準必須把上列增補入口納入分類(尤其 run_subjectivity_group_review
的 promotion lane)。

## §7 下一步

owner 對 §3(判準)、§4(schema)、§5(A/B/C)三個決定點簽核後,開第二段實作工單
(bounded,可派 codex)。在那之前,本 spec 是唯一交付物——**沒有任何行為改變**。
