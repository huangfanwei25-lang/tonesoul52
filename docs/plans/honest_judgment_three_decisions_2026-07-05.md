# 誠實判斷決策記錄 — 三個待決點(2026-07-05)

> 協議:`.claude/skills/honest-judgment`(判決模式);五視角真分身(Workflow,5 獨立
> agent)+ 獨立裁決 agent。**全程同模型(Fable 5)= correlated-blind-spot,且 PR/spec
> 作者亦同模型**——裁決據此對同模型互驗一律不給 E4、從嚴舉證。裁決書全文與五視角簡報
> 存 session 記錄;本檔=決策摘要+執行帳。
> **兩把鑰匙**:第一把=owner 要求「3個點 你用語魂系統分析後」;第二把=owner 對裁決結果
> 說「**用最後的建議去做**」(2026-07-05,原文)——本檔所載執行均以此為授權;D2 的
> DECLARE_STANCE 依協議不含可執行建議,筆仍在 owner(見 D2 節)。

## 裁決前:裁決 agent 的事實矛盾裁定(抓到作者的兩個過度宣稱)

- **M2**:作者宣稱「全部 shadow 起步」——**對 WO-5 不成立**(無 flag,無條件附掛
  BLOCK/DECLARE_STANCE 的 metadata;僅 fail-soft)。已勘正工單檔 + 本記錄。
- **M3**:belief-shift spec §3 的 drift_baseline 入帳與「機械 lane 不入帳」自相矛盾
  (drift 每次 commit 重算)。已修 spec(頻率門檻+方向翻轉判準)。
- **M4**:Aegis 根因獲**兩份互相獨立的 E4 重現**(Analyst 與 Critic 各自跑單檔測試,
  chain head hash 均被推移)——升為本輪最高置信事實。

## D1 — merge PR #300:**REFINE(可 merge,附四條 follow-up)**,信心 0.72

舉證責任:在 merge 方(改變現狀)。正方 ≥2 條 E3+(runtime 改動無路徑改 verdict、
27 新測試獨立重跑綠、CI live 16 pass);反方最強 E3(shadow 過度宣稱、regex 誤報面、
DECLARE_STANCE≠refusal 詞彙混淆)→ 依門檻規則不得 APPROVE,只能 REFINE。

**四條 follow-up 與執行**:
1. regex 誤報 caveat → ✅ `V0_CAVEAT` 寫進 principle_invocation 每筆記錄本體 + 開
   GitHub issue 追 pattern 修正;修正前兩記錄的統計不可引用。
2. DECLARE_STANCE≠refusal → ✅ schema 加 `event_class`(refusal / stance_declaration),
   消費端算拒絕率必須 key 這欄;測試釘住。
3. 工單收檔文字勘正 → ✅ 已在工單檔 EXECUTED header 明記 WO-5 無 flag。
4. 全套 8137 維持 E1 標注、merge 訊息不寫 verified → ✅ 遵守。

翻案條件(裁決原文):兩訊號例外能中斷 commit 或翻轉 verdict→BLOCK;乾淨環境全套
rerun 紅→BLOCK;誤報率量測 <5% 且無 dict-shape 消費者→撤 caveat 升 APPROVE;
codex 異模型審出共同盲點→全案重審。

## D2 — belief-shift spec 簽核:**DECLARE_STANCE(advisory:選擇權在人)**,信心 0.70

依協議規則 3,「什麼算信念層」觸 Axiom 8 記憶主權,AI 不裁。owner 的「用最後的建議
去做」**不適用本項**——裁決書明文不替 owner 選,故無「建議」可執行;能執行的只有:
- 五視角唯一全數共識的前置:**§6 盤點由異模型(codex)重跑覆核**——已嘗試執行(結果
  見執行帳)。
- M3 spec 缺陷修正(作者修自己的 DRAFT,不等於簽核)→ ✅ 已修。

**兩案最強點(裁決原文,供 owner 拍板)**:
- 簽核案:三個洞(vow 退役無痕/退場帳未接線/旁路腳本繞 Aegis)不簽也在漏;§5-C 把
  fail-closed 集中在本來就繞過 shield 的 lane=恢復公理一致而非新管制(E3)。
- 緩簽案:§4 三段式欄位無 authorship/review 欄,自動 lane 的「敘事」必為機器自填——
  VOLUME_V 要防的形狀反被 schema 洗白;零真實資料就簽=違反自家 #219 判例(E2-E3)。
- 張力核心:「帳本現在就該開」vs「會被機械寫入淹沒、敘事欄會表演的帳本比沒有更傷誠實」。

## D3 — Aegis chain-head 修法:**REFINE(必須修;形狀改窄)**,信心 0.80

舉證責任:**移轉到維持現狀方**(警報詞貶值=記錄在案的持續傷害 + 雙 E4 重現)——
不修不是選項。但 env 覆寫形狀被反方 E3 級更窄替代案擊中:**conftest monkeypatch
`_AEGIS_DIR`,生產面零改動**(倉庫已有同款前例 `_isolate_soul_db`)。裁決 REFINE:
優先 monkeypatch;env 若成唯一解,必附可見性條款(diagnose 回報實際錨點)。

執行:✅ 照 monkeypatch 形狀實作(conftest autouse fixture + regression test;
驗收=污染測試檔跑前後 repo chain head hash 不變)。詳見 D3 執行 commit。

## 執行帳(owner 授權「用最後的建議去做」之後)

- D1 follow-up 1-3 落碼落檔(本 commit);issue 開立;#300 照 REFINE merge。
- D3 monkeypatch 修法 + regression test(獨立 PR)。
- 判斷期間 Analyst/Critic 的兩次 E4 重現各污染鏈頭一次 → 修法落地後 re-anchor 收尾。
- D2:筆在 owner;codex 覆核嘗試結果與殘餘風險聲明另記。
- 反證鏈:本判斷的三個裁決各附翻案條件,outcome(survived/refuted/narrowed)待
  事實發生後回填。
