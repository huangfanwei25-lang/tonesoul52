# κ 違諾預測實驗 — Phase 0 燃料盤點 + TSR 遺產仲裁(2026-07-05)

> Status: **Phase 1 訊號落帳已實作(同日,shadow-only;見文末增修節)**;Phase 0 結論不變
> =違諾 ground truth 燃料不足,先收集後建模;Phase 2 門檻與開工權在 owner。
> 出處:LINEAGE parked asset #1(VowCollapsePredictor,G2/G4 的 κ——「違諾之前的
> 預測性預警;當年死於沒有真訊號可餵」)。owner 同日重提 TSR(ΔT/ΔS/ΔR 語氣張力
> 向量、認識論邊界標籤、漂移門控),問「這套還有用嗎」——兩題合併處理,
> 因為 TSR 的正確復活形狀就是 κ 的燃料。

## Phase 0 燃料盤點(2026-07-05 實測,file backend)

| 訊號 | 現況 | 判定 |
|---|---|---|
| 違諾 ground truth(vow 崩壞/撤回事件) | **≈0**(3 條 active vows,無崩壞紀錄;撤回 measure 期空轉中) | **致命缺口**——沒有 y,任何預測器都無法驗證 |
| tension_history | **0 點**(governance_state.json) | 空 |
| calibration 訊號 | `tonesoul/calibration_score.py` 真程式(ECE/report),eval 判例 2026-06-30 一份 | 可用但樣本薄 |
| TSR 遺產 | `tsr_delta_norm` 欄位活在 CouncilVerdict(types.py:108);EpistemicLabeler(864a)活著 | 有掛點,無時序資料 |
| 劇場玩家軌痕 | 管道昨天剛開(0 份) | 未來燃料 |

**誠實結論:當年殺死 κ 的問題(沒有真訊號)今天仍未解**。直接建預測器=重演 G4 偽數學。
正確的下一步不是建模,是**開始收集**。

## TSR 遺產仲裁(owner 2026-07-05 問「還有用嗎」)

三堆分開:

**堆一:已經活著的(別重做)**
- 認識論邊界標籤(事實/推論/假設)→ **EpistemicLabeler(864a,shipped)** + E0-E4 證據
  分級 + UNGROUNDED_CONFIDENCE_CAP(無證據信心 ≤0.6)。claim ≤ evidence 的實作,在跑。
- 漂移門控 → baseline_drift、divergence ledger(shadow seam #219)、escape valve。
- 「不准用事實語氣講假設」→ council guardian/critic 的 overclaim 檢測 + 誠實審計家族。

**堆二:死得有理的(別復活)**
- ΔT/ΔS/ΔR 三維連續向量+幾何軌跡:G4 偽數學(LINEAGE 明載「Φ/κ 偽數學死了」)。
  死因不是想法錯,是**量出來的數字沒有 ground truth 可校準**——張力向量無法回答
  「量得準不準」,claim>evidence 風險最大的正是量測本身。
- 「運算痛覺」作為機制名:今天的對應物=escape valve + council BLOCK + vow-003
  三連敗必停。**詞可進劇場世界書當渲染層**(佈景可幻想),機制不另建。

**堆三:今晚撿回來的(成為 κ 燃料的收集規格)**
- **姿態-證據錯位計數**(TSR 的「語氣錯位」離散化):EpistemicLabeler 標籤 vs 語氣
  篤定度的不一致事件,每 session 記一筆計數——可驗證(有標籤有規則)。
- **滑動視窗篤定度跳變**(TSR 滑動視窗的離散化):前 N 輪 vs 當輪,「推測→絕對」
  型跳變記事件;本地 qwen 當廉價評分器,**shadow-only**(記 divergence 不 gate,
  沿 #219 紀律)。
- `tsr_delta_norm` 既有欄位:開始寫入時序(現在是 Optional 常空)。

## Phase 1(收集期,從現在到燃料夠)

1. 每次 council 審議落 `tsr_delta_norm` + 錯位計數進 trace(掛點已存在,工程量小)。
2. 劇場玩家軌痕過審進 human lane 後,`contradiction_level`/`tone_drift` 欄位
   成為天然的 κ 訓練對(玩家承諾 vs 後續選擇=有 ground truth 的微型違諾!)。
3. 觸發建模門檻(到了才進 Phase 2):**≥20 筆有結局的承諾事件**
   (與反證鏈 ≥20 門檻同款紀律)。

## Phase 2(建模期,門檻到了才開)

規則式先行(不上 ML):錯位計數+篤定度跳變+calibration 漂移的簡單加權 → 預警分。
輸出=shadow 預警,記 divergence ledger,catch-rate 對照真實違諾——量測,不宣稱。

## Lane

Phase 1 工程(訊號落帳)=bounded ticket,可派 codex;門檻判定與 Phase 2 開工=owner。

---

## 增修(2026-07-05,Phase 1 落地 + 收斂掃描併桌)

### Phase 1 訊號落帳:已實作(shadow-only)

- **模組**:`tonesoul/council/kappa_signals.py`;掛點=`CouncilRuntime.deliberate()`
  genesis 步之後(runtime.py,fail-soft try/except,與 vtp/benevolence 同形)。
- **每次審議落兩個訊號進 transcript["kappa_signals"]**(永遠附掛、無副作用,
  epistemic_label 同款姿態;隨 council_verdict provenance 事件持久化):
  1. `tsr_delta_norm`(既有計算,收進同一筆 schema `kappa_signal_v0`);
  2. **姿態-證據錯位**:語氣姿態(tsr_metrics strong_modals vs caution 離散化:
     assertive/hedged/neutral)× EpistemicLabel 證據分級(strong/medium/weak/unlabeled);
     **assertive + weak = 一筆 mismatch 事件**,附錯位維度。
- **JSONL ledger**(`memory/kappa_signal_ledger.jsonl`,gitignored)= **default-OFF**
  (`SOUL.council.kappa_signal_ledger_enabled`,#219 檔案副作用紀律);**翻開關=owner**。
  transcript 附掛不受此旗標影響——observability 永遠在。
- **誠實標注(v0 限度)**:tsr_metrics 詞庫是英文(tokenizer 丟 CJK)——純中文草稿
  姿態=neutral、錯位**低估**;計數是 floor 不是真率。無標籤=unlabeled,不計 mismatch
  (沒標籤≠證據弱)。永不 gate verdict(測試有 never-a-gate invariant)。
- 測試:`tests/test_kappa_signals.py`(9 tests:規則正反例、編碼紀律、旗標 OFF 不寫檔、
  不改判決)。

### 「滑動視窗篤定度跳變」(堆三第 2 條)未實作

需要跨 session 時序 + 本地 qwen 評分器,屬 7/7 後工作;本次只落單次審議層的離散訊號。

### 收斂掃描併桌(2026-07-05 大掃描,見 convergence_sweep_report S4/S5 相關項)

- **升格前壓力預測**(vocus〈AI 應學會「不輕易承諾」〉2026-03-10):κ 量「立誓後、
  違諾前」,這條量「升格前」——同一組 calibration 燃料的**第二量測點**。Phase 2 設計時
  把「張力候選→承諾」的升格事件也納入收集面(掛點=vow 升格路徑,尚未實作)。
- **三層 Trace 架構 Layer 2/3**(dissent 衰減 + pattern crystal;PR #72 遺落 spec
  `trace_architecture_followup_2026-05-13.md`):與 κ 同屬衰減/預警家族。併桌結論=
  **先量再建**:等本 ledger 有時序後,先驗 owner 觀察(「dissent 影子該衰減而 AI 不衰減」)
  是否在資料裡成立,再決定 Layer 2 建不建;不獨立開工。
