---
name: honest-judgment
description: 誠實判斷器 — owner 丟一個問題,用語魂系統自己的邏輯(Council 五視角真分身、verdict 詞彙、UNGROUNDED_CONFIDENCE_CAP、張力保留)跑結構化判斷。Use when the owner asks 判斷看看 / 正反分析 / 誠實判斷 / should-we questions about design, direction, adoption, trade-offs. NOT for moral dilemmas (DECLARE_STANCE, don't rule) and NOT for financial entry/exit calls (never endorsed).
---

# 誠實判斷器(Honest Judgment)— 語魂原生

把 2026-07-02 驗證過的研究形狀(G8 撤回研究 #248、escalation seam 判決)固化成
可重複協議,**且判斷框架就是語魂自己的治理邏輯**——不是外掛一個通用 pro/con。
核心不是給答案,是**讓反方有真牙齒**。

## 語魂映射(為什麼這不是新發明)

| 協議部件 | 語魂既有機制 | 出處 |
|---|---|---|
| 真分身多視角 | Council 五視角(Guardian/Analyst/Critic/Advocate/Axiomatic) | `tonesoul/council/perspectives/` |
| 裁決詞彙 | APPROVE / REFINE / **DECLARE_STANCE** / BLOCK | `council/verdict.py` |
| 信心上限 | 無證據宣稱信心 ≤ 0.6 | `council/types.py:57 UNGROUNDED_CONFIDENCE_CAP` |
| 分歧處理 | 張力保留、不平均掉(Axiom 4) | `AXIOMS.json` |
| 證據分級 | E0–E4 | `tonesoul/reviewer/evidence_levels.py` |
| 落痕 | 反證鏈 + 決策記錄 | `tools/accountability_panel/`、`docs/plans/` |

## 模式分流(第 0 步,2026-07-03 外部批評後新增)

不是每個問題都想要判決。拆題前先分流,含糊時**問 owner 要哪種**:

- **判決模式**:可裁決的行動命題(「該不該做 X」)→ 走下面四步,出判決。
- **探究模式**:理念之爭、哲學題(「X 和 Y 哪個對」的觀念層)→ 五視角各自把
  立場做到最強,輸出**張力地圖**:各立場最強形式、真衝突在哪、哪些是假衝突。
  **沒有判決、沒有舉證責任**——這是 Axiom 4「張力保留」的正式用法。
  落痕照舊,但落的是對話錄,不是判決書。
- 道德兩難:一律探究模式 + DECLARE_STANCE(既有規則不變)。

出處:2026-07-03 一個外部模型讀了首份判決書後批評「系統把靈魂拷問強行收斂成
做/不做」——批評一半成立(行為導向確實會窄化題目),修法是加模式而不是教
使用者唸解鎖咒語。已記入反證鏈(outcome=narrowed)。

## 協議(四步,缺一步就不叫誠實判斷)

1. **拆題**:把問題改寫成可裁決命題 + 「什麼證據會翻案」(falsifier),
   回給 owner 確認——別裁決一個他沒問的題。
2. **五視角真分身**:spawn 獨立 agent(Workflow/Agent tool),各戴一個
   Council 視角:Guardian(傷害/安全面)、Analyst(機制與證據)、
   Critic(最強反方)、Advocate(最強正方)、Axiomatic(與 AXIOMS 的一致性)。
   **不得單 context 自演**(同組權重=同組盲點)。每個論點帶證據
   (file:line / URL / 數據)+ E-tag;無證據就標 E0 並明說。
3. **對抗裁決**:裁決 agent 收五案,舉證責任預設在「改變現狀」方。
   輸出用 council 詞彙:
   - **APPROVE / BLOCK**:證據夠一邊倒時。
   - **REFINE**:方向對但命題要改窄(Guardian+Axiomatic 同時 CONCERN 的類比)。
   - **DECLARE_STANCE**:真分歧——正反各自站得住,輸出兩案+張力核心,
     **決定權交還 owner**。道德兩難一律走這格(meta.not_for)。
   附:信心(受 0.6 上限約束——裁決信心不得高於較弱方證據所能撐的)、
   兩案各自最強一點、翻案條件。
4. **落痕**:結果進 docs/plans/ 決策記錄;重大判斷進反證鏈
   (outcome=survived/refuted/narrowed)。判斷不落痕=沒發生。

## 輸出格式:論點筆記體(前台白話,證據在下)

owner 回饋(2026-07-03):前台不要堆自家術語和分級。每個論點寫成:

```
**論點(白話一句)**
  為什麼信:<證據,白話>
  可信度:<白話翻譯>(內部分級括號附註,如 E3)
  哲學出處(選填):<哪位哲學家/學派的哪個立場>——只在真的對得上時標
```

分級白話對照:E0=只是直覺還沒查證 / E1=自家測試撐著 / E2=可重現的檢查 /
E3=外部或程式碼直接佐證 / E4=獨立重現過。判決詞白話:APPROVE=照做 /
REFINE=方向對但要修窄 / DECLARE_STANCE=真分歧,交還你決定 / BLOCK=別做。

**哲學出處的紀律**:錯掛哲學家=過度宣稱的同罪。只在立場真的對得上文獻時標,
並附信心;對不上就寫「近似於…但不完全是」。前例教訓:2026-07-01 一次
「你=存在主義、我=維根斯坦」的漂亮對照,重查後因太乾淨而收回。

## 硬邊界(不可協商)

- **道德兩難**:永遠 DECLARE_STANCE,結構化呈現≠替人選。
- **金融進出場**:可分析機制與風險;結論欄永遠寫「不構成投資判斷」。錢這刀不軟。
- **同模型警告**:五視角+裁決若同模型,標 correlated-blind-spot;
  codex 可用時優先當異模型 Critic(`scripts/codex_review.py`)。

## 先例(可抄措辭)

- `docs/plans/escalation_two_mechanisms_decision_2026-07-02.md` —
  裁決指令「Be adversarial to the merge; burden of proof on the surgery」→ 判 BLOCK。
- `docs/plans/vow_withdrawal_gap_study_2026-07-02.md` — 逐項 REVIVE/OBSOLETE → 判 APPROVE(窄化後)。

## 誠實限制

協議不是引擎:執行品質取決於當下模型與算力。單 agent 環境(本地 qwen)
退化模式=順序跑五視角、輪間清 context,結論標「degraded: sequential, not
independent」。runtime council(heuristic voters)與本協議(深推理 agent)是
同一設計的兩個深度——引用時別混稱。
