# 【治理決策記錄】escalation.py 與 alert_escalation.py — 刻意保留雙套

> 2026-07-02。三路 workflow 測繪(兩模組全文精讀 + 全倉 consumer 掃描 + 對抗式 seam 判決),
> 判決 agent 對兩張地圖逐點重驗後裁定。

**決策**:不合併。兩модulю各自保留,各加一段互相指認的檔頭警告。

**為什麼**:這不是重複,是**共用詞彙的兩個機制**——可替代性測試雙向失敗:
- `escalation.py`:離線批次判斷(POAV 總分 + YSTM drift 檔 + kairos decision_mode →
  none/jump/quarantine + ErrorLedger 持久化);唯一函式呼叫者 `yss_pipeline` 是
  owner 保留的 unwired 基板(Responsibility Manifold 候選)。活路徑只「載入」它,從不執行。
- `alert_escalation.py`:每回合即時分級(DriftMonitor/JumpMonitor/CircuitBreaker 標量 →
  CLEAR/L1/L2/L3 瞬態severity);消費者是 unified_pipeline 與 llm.router。
- **詞彙相撞**:`jump` 一邊是輸出決策、一邊是輸入訊號;`lockdown` 一邊是輸入模式、
  一邊是後果;`drift` 指兩個無關指標。合併會製造歧義,不是消除。

**張力來源**:與「清理重複」的整理慣性衝突 → 用本記錄化解:名字相似≠概念相同。
**風險證據**:任何合併都要動 `yss_gates.py:11`——2026-06-13 差點被誤刪的活 POAV gate
的 import 縫,且兩條 live import 縫都是 try/except 靜默失敗(CI 不會紅,功能悄悄消失);
要切的縫(escalation_gate/dcs_gate)零直接測試。
**可逆性**:本決策零程式行為變更(僅文件+註解),完全可逆。
**再議條件**:Responsibility Manifold 真的接上 yss_pipeline 時,重新測繪。
