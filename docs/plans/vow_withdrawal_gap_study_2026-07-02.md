# Vow 撤回語義補課 — G8 對照研究 + 治理決策記錄

> Status: 研究完成;實作等 owner 點頭(動 vow system = CLAUDE.md 治理綁定範圍)
> 方法:三路 workflow(G8 原始碼提取 / 現行系統提取 / gap 對抗分析),
> 全部宣稱帶 file:line 證據,現行側逐點對 live repo 驗證。
> 出處:docs/LINEAGE.md parked asset #2(G8 tonesoul-codex 的 WithdrawalConditions)。

## 一句話結論

**現行系統的「違諾」半邊比 G8 強一個量級(真後果、真記憶、真審計);
「退場」半邊卻退化為零**——今天一條 vow 唯一的離開方式是 `unregister()` 硬刪
(`vow_system.py:226-229`,無墓碑、無理由、無溯源,runtime 從未呼叫)。
G8 的核心洞見值得復活:**退出成本在創建時申報,退場要留痕、要有名字**。

## G8 有、今天沒有(判 REVIVE,全部 declarative-only)

| G8 欄位 | 語義 | 今天 | 判決 |
|---|---|---|---|
| `WITHDRAWN` 狀態 + 必填 `WithdrawalConditions` | vow 不能沒有退場條款就存在 | 無撤回概念 | REVIVE(用本倉自己的 revoke-with-provenance 模式,不用 G8 的裸 mutation) |
| `repair_owner` | 退場後誰負責修復/解釋(角色) | 只有 `needs_attention` 布林(有旗無人) | **REVIVE — 四者中價值最高**:一個欄位,回答「義務落在誰身上」 |
| `conditions` + `repair_actions` | 何時退場正當 + 欠什麼(升級清單到公開道歉) | 無 | REVIVE,shadow 期刻意不驗證(申報本身就是問責動作) |
| repair `deadline` | 修復 SLA | 無 | REVIVE 為 Optional 記錄欄;G8 自己也是 dormant——不長 scheduler |

## G8 有、今天不要(判 OBSOLETE)

- **FULFILLED/fulfilled_at + 關鍵字抽取到期日**:G8 的 vow 是從語句解析的承諾言語行為
  (我發誓→CRITICAL…),會「履行完畢」;現行 vow 是常設治理約束,永遠不會「履行完」。
- **VIOLATED/EXPIRED 狀態**:在 G8 就 unreachable(全 repo 無 writer;測試證明
  FULFILLED→WITHDRAWN 無守衛直接過)。現行的單調違諾帳(VowInventory 計數、違諾 2x
  懲罰、永不特赦)嚴格更強——**狀態可以被覆寫,計數器不能**。復活它是倒退。
- **簽章/見證人/五倉聯署儀式**(spec-only):capability 形狀的儀式,不復活。
  唯一致敬的原則:**不可回退承諾——只 annotate + supersede,永不改寫**。

## 今天有、G8 沒有(進步存證)

違諾有真後果(hard mode 真擋輸出、fail-closed)、有記憶(conviction 帳 + 衰退觸發
強制自省)、有審計綁定(違諾必上 Aegis 鏈 audit_required);G8 只有「偵測而無後果」,
且只 trace 創建。現行的 repair 修的是**輸出**,G8 的 repair 修的是**關係**——
不同概念,復活不重複。

## 【治理決策記錄】最小復活提案(等 owner 點頭再動)

**決策**:三個小改動,全部 shadow-first、不 gating:
1. `WithdrawalTerms` dataclass(conditions/repair_owner/repair_actions/repair_deadline=None)
   → `Vow.withdrawal_terms: Optional[...] = None`(向後相容,逐 vow 建構——記取 G8 的
   共享模板別名 bug;先種進 3 條 DEFAULT_VOWS)。
2. `VowRegistry.withdraw(vow_id, reason, actor)`:設 `active=False`(enforce 已跳過
   inactive,零執行路徑變更)+ 追加不可變撤回記錄(含 conditions_cited,**記錄不驗證**)
   + 永不刪除;`unregister()` 降級為測試/工具用。約 25 行。
3. Shadow 面:`VowInventory.record_withdrawal`(不動 conviction)+ CLI 顯示
   `[WITHDRAWN by <actor>: <reason>]`。

**為什麼**:退役一條常設約束是治理行為,今天零留痕;修復 = 純問責 metadata,零新能力。
**張力來源**:與「vow system 不輕動」的保守慣性有張力 → 解法是 additive-optional +
shadow-first + 本記錄先行。
**明確反目標**(每條擋一種 creep):不驗證條件、不建 deadline scheduler、不追蹤
action 完成度、**不綁 council 權重/latitude**(#228/#231 決議延續)、不因 conviction
衰退自動撤回。
**可逆性**:完全可逆(optional 欄位 + 新方法,無既有行為變更)。
**成功判準**(measure 期):撤回記錄存在、可查詢、有名字——G8 的洞見,去掉 G8 的虛構。
